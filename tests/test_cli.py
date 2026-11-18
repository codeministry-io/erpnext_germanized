import io
import json
import runpy
import sys
import urllib.request
from pathlib import Path

import pytest

from germanized.__main__ import main

APPS_JSON = (
	"[\n"
	'  {\n    "url": "https://github.com/frappe/erpnext",\n    "branch": "v16.60.0"\n  },\n'
	'  {\n    "url": "https://github.com/frappe/hrms",\n    "branch": "v16.59.0"\n  },\n'
	'  {\n    "url": "https://github.com/encircle360-oss/steuerbote",\n    "branch": "v0.1.1"\n  }\n'
	"]\n"
)
CONTAINERFILE = """\
ARG PYTHON_VERSION=3.14
ARG DEBIAN_BASE=trixie
FROM python:3.14-slim-trixie AS base
ARG WKHTMLTOPDF_VERSION=0.12.6.1-3
ARG WKHTMLTOPDF_DISTRO=bookworm
ARG INSTALL_CHROMIUM=true
ARG NODE_VERSION=24
FROM base AS builder
ARG FRAPPE_BRANCH=v16.60.2
ARG FRAPPE_PATH=https://github.com/frappe/frappe
"""
README = """\
# erpnext_germanized

## Enthaltene Apps

| App | Version | Zweck | Lizenz |
|---|---|---|---|
| [frappe](https://github.com/frappe/frappe) | v16.60.2 | Framework | MIT |
| [erpnext](https://github.com/frappe/erpnext) | v16.60.0 | ERP | GPL-3.0 |
| [hrms](https://github.com/frappe/hrms) | v16.59.0 | Personal | GPL-3.0 |
| [steuerbote](https://github.com/encircle360-oss/steuerbote) | v0.1.1 | ELSTER | AGPL-3.0 |

## Schnellstart
"""
SHA = "0123456789abcdef0123456789abcdef01234567"
IMAGE = "ghcr.io/encircle360-oss/erpnext_germanized"


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
	(tmp_path / "apps.json").write_text(APPS_JSON, encoding="utf-8")
	(tmp_path / "Containerfile").write_text(CONTAINERFILE, encoding="utf-8")
	(tmp_path / "README.md").write_text(README, encoding="utf-8")
	monkeypatch.chdir(tmp_path)
	return tmp_path


def release(tag: str) -> dict:
	return {"tag_name": tag, "prerelease": False, "draft": False}


class FakeReleases:
	"""Stands in for urllib.request.urlopen and answers the release lists of the GitHub API."""

	def __init__(self, releases: dict[str, list[dict]]):
		self.releases = releases

	def __call__(self, request: urllib.request.Request, timeout: float) -> io.BytesIO:
		owner_repo = request.full_url.removeprefix("https://api.github.com/repos/").removesuffix(
			"/releases?per_page=30"
		)
		return io.BytesIO(json.dumps(self.releases[owner_repo]).encode())


@pytest.fixture
def github(monkeypatch: pytest.MonkeyPatch) -> None:
	releases = {
		"frappe/frappe": [release("v16.61.0"), release("v16.60.2")],
		"frappe/erpnext": [release("v16.60.0")],
		"frappe/hrms": [release("v16.60.0"), release("v16.59.0")],
		"encircle360-oss/steuerbote": [],
	}
	monkeypatch.setattr(urllib.request, "urlopen", FakeReleases(releases))


def test_validate_accepts_valid_apps(repo, capsys):
	assert main(["validate"]) == 0
	assert capsys.readouterr().out == "apps.json is valid: 3 apps on Frappe v16.60.2\n"


def test_validate_lists_every_problem(repo, capsys):
	(repo / "apps.json").write_text(
		'[{"url": "https://github.com/frappe/hrms/", "branch": "version-16"}]', encoding="utf-8"
	)
	assert main(["validate"]) == 1
	assert capsys.readouterr().err == (
		"apps.json breaks the rules of the image:\n"
		"- the first app must be https://github.com/frappe/erpnext, not https://github.com/frappe/hrms/\n"
		"- https://github.com/frappe/hrms/: not a repository url like https://github.com/<owner>/<repo>\n"
		"- https://github.com/frappe/hrms/: 'version-16' is not a release tag like v16.60.0\n"
	)


def test_an_unreadable_file_is_an_error(repo, capsys):
	(repo / "apps.json").write_text("[", encoding="utf-8")
	assert main(["validate"]) == 1
	assert capsys.readouterr().err.startswith("error: apps.json is not valid JSON")
	(repo / "apps.json").write_text(APPS_JSON, encoding="utf-8")
	(repo / "Containerfile").unlink()
	assert main(["validate"]) == 1
	assert "No such file or directory: 'Containerfile'" in capsys.readouterr().err


def test_tags_prints_the_tags_of_main_separated_by_commas(repo, capsys):
	assert main(["tags", "--ref", "refs/heads/main", "--sha", SHA]) == 0
	assert capsys.readouterr().out == f"{IMAGE}:main,{IMAGE}:main-0123456\n"


def test_tags_prints_the_tags_of_a_release(repo, capsys):
	assert main(["tags", "--ref", "refs/tags/v16.60.0-2", "--sha", SHA]) == 0
	assert capsys.readouterr().out == f"{IMAGE}:16.60.0-2,{IMAGE}:16.60.0,{IMAGE}:16,{IMAGE}:latest\n"


def test_tags_prints_an_empty_line_for_refs_that_are_not_pushed(repo, capsys):
	assert main(["tags", "--ref", "refs/pull/7/merge", "--sha", SHA]) == 0
	assert capsys.readouterr().out == "\n"


def test_tags_refuses_a_malformed_sha(repo, capsys):
	assert main(["tags", "--ref", "refs/heads/main", "--sha", "HEAD"]) == 1
	assert capsys.readouterr().err == "error: 'HEAD' is not a commit SHA\n"


def test_release_check_accepts_a_release_of_the_pinned_erpnext(repo, capsys):
	assert main(["release-check", "--ref", "refs/tags/v16.60.0-1"]) == 0
	assert capsys.readouterr().out == "v16.60.0-1 is a release of ERPNext v16.60.0 as apps.json pins it\n"


def test_release_check_refuses_another_erpnext_version(repo, capsys):
	assert main(["release-check", "--ref", "refs/tags/v16.61.0-1"]) == 1
	assert capsys.readouterr().err == (
		"refs/tags/v16.61.0-1 cannot be released:\n"
		"- the release v16.61.0-1 names ERPNext 16.61.0, but apps.json pins v16.60.0\n"
	)


def test_release_check_needs_a_tag_ref(repo, capsys):
	assert main(["release-check", "--ref", "refs/heads/main"]) == 1
	assert capsys.readouterr().err == "error: refs/heads/main is not a tag ref like refs/tags/v16.60.0-1\n"


def test_summary_describes_the_build_with_its_tags(repo, capsys):
	assert main(["summary", "--tags", f"{IMAGE}:main,{IMAGE}:main-0123456"]) == 0
	out = capsys.readouterr().out
	assert out.startswith("### Apps\n\n| App | Version |\n| --- | --- |\n")
	assert "| [hrms](https://github.com/frappe/hrms) | `v16.59.0` |\n" in out
	assert "| `NODE_VERSION` | `24` |\n" in out
	assert out.endswith(f"### Image tags\n\n- `{IMAGE}:main`\n- `{IMAGE}:main-0123456`\n")


def test_summary_accepts_tags_on_separate_lines(repo, capsys):
	assert main(["summary", "--tags", f"{IMAGE}:main\n{IMAGE}:main-0123456\n"]) == 0
	assert capsys.readouterr().out.endswith(f"- `{IMAGE}:main`\n- `{IMAGE}:main-0123456`\n")


def test_summary_without_tags_says_that_nothing_is_pushed(repo, capsys):
	assert main(["summary"]) == 0
	assert capsys.readouterr().out.endswith("None: this build is not pushed.\n")


def test_check_versions_prints_the_table(repo, github, capsys):
	assert main(["check-versions"]) == 0
	assert capsys.readouterr().out == (
		"| App | Pinned | Latest | Status |\n"
		"| --- | --- | --- | --- |\n"
		"| frappe | v16.60.2 | v16.61.0 | update available |\n"
		"| erpnext | v16.60.0 | v16.60.0 | up to date |\n"
		"| hrms | v16.59.0 | v16.60.0 | update available |\n"
		"| steuerbote | v0.1.1 | none | no release on major version 0 |\n"
	)


def test_check_versions_needs_valid_apps(repo, github, capsys):
	(repo / "apps.json").write_text("[]", encoding="utf-8")
	assert main(["check-versions"]) == 1
	assert (
		capsys.readouterr().err == "error: apps.json breaks the rules of the image: apps.json lists no apps\n"
	)


def test_bump_without_write_only_shows_the_changes(repo, github, capsys):
	assert main(["bump"]) == 0
	assert capsys.readouterr().out == (
		"frappe: v16.60.2 -> v16.61.0\n"
		"hrms: v16.59.0 -> v16.60.0\n"
		"nothing written: pass --write to change apps.json and the Containerfile\n"
	)
	assert (repo / "apps.json").read_text(encoding="utf-8") == APPS_JSON
	assert (repo / "Containerfile").read_text(encoding="utf-8") == CONTAINERFILE


def test_bump_write_moves_the_pins(repo, github, capsys):
	assert main(["bump", "--write"]) == 0
	assert capsys.readouterr().out.endswith("wrote apps.json and the Containerfile\n")
	assert (repo / "apps.json").read_text(encoding="utf-8") == APPS_JSON.replace("v16.59.0", "v16.60.0")
	assert (repo / "Containerfile").read_text(encoding="utf-8") == CONTAINERFILE.replace(
		"FRAPPE_BRANCH=v16.60.2", "FRAPPE_BRANCH=v16.61.0"
	)


def test_bump_write_touches_only_the_files_that_change(repo, monkeypatch, capsys):
	releases = {"frappe/frappe": [release("v16.60.2")], "frappe/hrms": [release("v16.60.0")]}
	releases |= {"frappe/erpnext": [], "encircle360-oss/steuerbote": []}
	monkeypatch.setattr(urllib.request, "urlopen", FakeReleases(releases))
	assert main(["bump", "--write"]) == 0
	assert capsys.readouterr().out == "hrms: v16.59.0 -> v16.60.0\nwrote apps.json\n"
	assert (repo / "Containerfile").read_text(encoding="utf-8") == CONTAINERFILE

	(repo / "apps.json").write_text(APPS_JSON, encoding="utf-8")
	releases |= {"frappe/frappe": [release("v16.61.0")], "frappe/hrms": []}
	monkeypatch.setattr(urllib.request, "urlopen", FakeReleases(releases))
	assert main(["bump", "--write"]) == 0
	assert capsys.readouterr().out == "frappe: v16.60.2 -> v16.61.0\nwrote the Containerfile\n"
	assert (repo / "apps.json").read_text(encoding="utf-8") == APPS_JSON


def test_bump_says_when_every_pin_is_current(repo, monkeypatch, capsys):
	releases = {
		"frappe/frappe": [],
		"frappe/erpnext": [],
		"frappe/hrms": [],
		"encircle360-oss/steuerbote": [],
	}
	monkeypatch.setattr(urllib.request, "urlopen", FakeReleases(releases))
	assert main(["bump", "--write"]) == 0
	assert capsys.readouterr().out == "every pin is on the newest release of its major version\n"


def test_readme_check_accepts_a_table_in_step(repo, capsys):
	assert main(["readme", "--check"]) == 0
	assert capsys.readouterr().out == "README.md lists frappe and the 3 apps with their pinned versions\n"


def test_readme_check_lists_the_differences(repo, capsys):
	(repo / "README.md").write_text(README.replace("| v16.59.0 |", "| v16.58.0 |"), encoding="utf-8")
	assert main(["readme", "--check"]) == 1
	assert capsys.readouterr().err == (
		"README.md is not in step with the pins:\n"
		"- README.md line 9: hrms has the version 'v16.58.0', apps.json pins v16.59.0\n"
	)


def test_readme_write_updates_the_versions(repo, capsys):
	(repo / "README.md").write_text(README.replace("| v16.59.0 |", "| v16.58.0 |"), encoding="utf-8")
	assert main(["readme", "--write"]) == 0
	assert capsys.readouterr().out == "README.md: updated the versions of the app table\n"
	assert (repo / "README.md").read_text(encoding="utf-8") == README
	assert main(["readme", "--write"]) == 0
	assert capsys.readouterr().out == "README.md: the versions of the app table are up to date\n"


def test_readme_needs_check_or_write(repo, capsys):
	assert main(["readme"]) == 1
	assert "one of the arguments --check --write is required" in capsys.readouterr().err
	assert main(["readme", "--check", "--write"]) == 1
	assert "not allowed with argument" in capsys.readouterr().err


def test_a_command_is_required(repo, capsys):
	assert main([]) == 1
	err = capsys.readouterr().err
	assert err.startswith("usage: python -m germanized")
	assert "the following arguments are required: command" in err


def test_usage_errors_exit_with_one(repo, capsys):
	assert main(["tags", "--ref", "refs/heads/main"]) == 1
	assert "the following arguments are required: --sha" in capsys.readouterr().err


def test_the_package_runs_as_a_module(repo, monkeypatch, capsys):
	monkeypatch.setattr(sys, "argv", ["python -m germanized", "validate"])
	# The tests import germanized.__main__ already; runpy has to execute it afresh.
	monkeypatch.delitem(sys.modules, "germanized.__main__")
	with pytest.raises(SystemExit) as exit_info:
		runpy.run_module("germanized", run_name="__main__")
	assert exit_info.value.code == 0
	assert capsys.readouterr().out.startswith("apps.json is valid")
