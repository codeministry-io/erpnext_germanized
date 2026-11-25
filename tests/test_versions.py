import io
import json
import re
import urllib.error
import urllib.request

import pytest

from germanized.apps import App, load_apps
from germanized.versions import (
	Row,
	bump,
	check,
	fetch_github,
	latest_release,
	table,
	write_apps,
	write_frappe_tag,
)

ERPNEXT = App("https://github.com/frappe/erpnext", "v16.60.0")
HRMS = App("https://github.com/frappe/hrms", "v16.59.0")
STEUERBOTE = App("https://github.com/encircle360-oss/steuerbote", "v0.1.1")
BRIEFBOTE = App("https://github.com/encircle360-oss/briefbote", "main")
GERMANY_FORK = App("https://github.com/encircle360-oss/erpnext_germany", "v16.2.2-encircle360.4")
RELEASES_URL = "https://api.github.com/repos/frappe/frappe/releases?per_page=30"


def release(tag: str, prerelease: bool = False, draft: bool = False) -> dict:
	return {"tag_name": tag, "prerelease": prerelease, "draft": draft}


class FakeGitHub:
	"""Answers release list requests from a dict of repositories and records the urls."""

	def __init__(self, releases: dict[str, object]):
		self.releases = releases
		self.urls: list[str] = []

	def __call__(self, url: str) -> bytes:
		self.urls.append(url)
		owner_repo = url.removeprefix("https://api.github.com/repos/").removesuffix("/releases?per_page=30")
		return json.dumps(self.releases[owner_repo]).encode()


@pytest.fixture
def github() -> FakeGitHub:
	return FakeGitHub(
		{
			"frappe/frappe": [release("v16.61.0"), release("v15.90.0"), release("v16.60.2")],
			"frappe/erpnext": [release("v16.60.0")],
			"frappe/hrms": [
				release("v17.0.0-beta.1", prerelease=True),
				release("v16.61.0", draft=True),
				release("v16.60.0"),
				release("v16.59.0"),
			],
			"encircle360-oss/steuerbote": [],
			"encircle360-oss/briefbote": [release("v1.0.0-rc.1", prerelease=True), release("v0.1.0")],
			"alyf-de/erpnext_germany": [release("v16.2.2"), release("v15.24.1")],
		}
	)


def test_latest_release_asks_for_the_releases_of_the_repository(github):
	assert latest_release("frappe/frappe", 16, github) == "v16.61.0"
	assert github.urls == [RELEASES_URL]


def test_latest_release_stays_on_the_major_version(github):
	assert latest_release("frappe/frappe", 15, github) == "v15.90.0"
	assert latest_release("frappe/frappe", 17, github) is None


def test_latest_release_skips_prereleases_and_drafts(github):
	assert latest_release("frappe/hrms", 16, github) == "v16.60.0"


def test_latest_release_compares_by_number_not_by_order():
	github = FakeGitHub({"frappe/frappe": [release("v16.9.0"), release("v16.10.0"), release("v16.9.9")]})
	assert latest_release("frappe/frappe", 16, github) == "v16.10.0"


def test_latest_release_takes_only_release_tags_of_that_major():
	github = FakeGitHub(
		{"frappe/frappe": [release("v160.0.0"), release("v16.61.0-hotfix"), release("v16.60.2")]}
	)
	assert latest_release("frappe/frappe", 16, github) == "v16.60.2"


def test_latest_release_is_none_without_releases(github):
	assert latest_release("encircle360-oss/steuerbote", 0, github) is None


def test_latest_release_of_any_major_version():
	github = FakeGitHub({"o/r": [release("v0.9.0"), release("v1.2.0"), release("v1.10.0", draft=True)]})
	assert latest_release("o/r", None, github) == "v1.2.0"


def test_latest_release_expects_a_list_of_releases():
	github = FakeGitHub({"frappe/frappe": {"message": "Not Found"}})
	with pytest.raises(ValueError, match="unexpected answer from GitHub for frappe/frappe"):
		latest_release("frappe/frappe", 16, github)


class FakeUrlopen:
	"""Stands in for urllib.request.urlopen and records the requests."""

	def __init__(self, body: bytes = b"[]", error: Exception | None = None):
		self.body = body
		self.error = error
		self.requests: list[tuple[urllib.request.Request, float]] = []

	def __call__(self, request: urllib.request.Request, timeout: float) -> io.BytesIO:
		self.requests.append((request, timeout))
		if self.error is not None:
			raise self.error
		return io.BytesIO(self.body)


def test_fetch_github_sends_the_api_headers_and_the_token(monkeypatch):
	urlopen = FakeUrlopen(b'[{"tag_name": "v16.60.2"}]')
	monkeypatch.setattr(urllib.request, "urlopen", urlopen)
	monkeypatch.setenv("GITHUB_TOKEN", "fake-token")
	assert fetch_github(RELEASES_URL) == b'[{"tag_name": "v16.60.2"}]'
	[(request, timeout)] = urlopen.requests
	assert request.full_url == RELEASES_URL
	assert request.get_header("Accept") == "application/vnd.github+json"
	assert request.get_header("X-github-api-version") == "2022-11-28"
	assert request.get_header("User-agent") == "erpnext_germanized"
	assert request.get_header("Authorization") == "Bearer fake-token"
	assert timeout == 30


def test_fetch_github_works_without_a_token(monkeypatch):
	urlopen = FakeUrlopen()
	monkeypatch.setattr(urllib.request, "urlopen", urlopen)
	monkeypatch.delenv("GITHUB_TOKEN", raising=False)
	assert fetch_github(RELEASES_URL) == b"[]"
	[(request, _)] = urlopen.requests
	assert not request.has_header("Authorization")


def test_fetch_github_ignores_an_empty_token(monkeypatch):
	urlopen = FakeUrlopen()
	monkeypatch.setattr(urllib.request, "urlopen", urlopen)
	monkeypatch.setenv("GITHUB_TOKEN", "")
	fetch_github(RELEASES_URL)
	[(request, _)] = urlopen.requests
	assert not request.has_header("Authorization")


def test_fetch_github_names_the_url_that_failed(monkeypatch):
	error = urllib.error.HTTPError(RELEASES_URL, 403, "rate limit exceeded", hdrs=None, fp=None)
	monkeypatch.setattr(urllib.request, "urlopen", FakeUrlopen(error=error))
	with pytest.raises(
		OSError, match=re.escape(f"GET {RELEASES_URL} failed: HTTP Error 403: rate limit exceeded")
	):
		fetch_github(RELEASES_URL)


def test_fetch_github_reports_unreachable_hosts(monkeypatch):
	monkeypatch.setattr(
		urllib.request, "urlopen", FakeUrlopen(error=urllib.error.URLError("no route to host"))
	)
	with pytest.raises(OSError, match="failed: <urlopen error no route to host>"):
		fetch_github(RELEASES_URL)


def test_fetch_github_reaches_only_the_github_api(monkeypatch):
	urlopen = FakeUrlopen()
	monkeypatch.setattr(urllib.request, "urlopen", urlopen)
	with pytest.raises(ValueError, match=r"only fetches from https://api\.github\.com/"):
		fetch_github("file:///etc/passwd")
	with pytest.raises(ValueError, match="only fetches from"):
		fetch_github("https://api.github.com.example.org/repos")
	assert urlopen.requests == []


def test_check_compares_frappe_and_every_app_with_its_newest_release(github):
	assert check((ERPNEXT, HRMS, STEUERBOTE), "v16.60.2", github) == [
		Row("frappe", "v16.60.2", "v16.61.0"),
		Row("erpnext", "v16.60.0", "v16.60.0"),
		Row("hrms", "v16.59.0", "v16.60.0"),
		Row("steuerbote", "v0.1.1", None),
	]


def test_check_compares_a_fork_with_the_releases_of_its_upstream(github):
	assert check((ERPNEXT, GERMANY_FORK), "v16.60.2", github)[2] == Row(
		"erpnext_germany", "v16.2.2-encircle360.4", "v16.2.2", "alyf-de/erpnext_germany"
	)
	assert (
		"https://api.github.com/repos/encircle360-oss/erpnext_germany/releases?per_page=30" not in github.urls
	)


def test_check_compares_a_branch_with_the_releases_of_every_major_version(github):
	assert check((ERPNEXT, BRIEFBOTE), "v16.60.2", github)[2] == Row("briefbote", "main", "v0.1.0")


def test_a_row_of_a_fork_says_whether_upstream_has_a_newer_release():
	fork = "alyf-de/erpnext_germany"
	assert Row("erpnext_germany", "v16.2.2-encircle360.4", "v16.2.2", fork).status == (
		"fork of alyf-de/erpnext_germany v16.2.2, the newest upstream release"
	)
	assert Row("erpnext_germany", "v16.2.2-encircle360.4", "v16.3.0", fork).status == (
		"fork of alyf-de/erpnext_germany v16.2.2, upstream has a newer release"
	)
	assert Row("erpnext_germany", "v16.2.2-encircle360.4", None, fork).status == (
		"fork of alyf-de/erpnext_germany v16.2.2, upstream has no release on major version 16"
	)


def test_a_row_of_a_branch_says_whether_a_release_exists():
	assert Row("briefbote", "main", "v0.1.0").status == "branch, a release is available"
	assert Row("briefbote", "main", None).status == "branch, no release yet"


def test_a_row_says_whether_an_update_is_available():
	assert Row("hrms", "v16.59.0", "v16.60.0").status == "update available"
	assert Row("erpnext", "v16.60.0", "v16.60.0").status == "up to date"
	assert Row("erpnext", "v16.61.0", "v16.60.0").status == "up to date"
	assert Row("steuerbote", "v0.1.1", None).status == "no release on major version 0"


def test_table_is_markdown():
	rows = [Row("frappe", "v16.60.2", "v16.61.0"), Row("steuerbote", "v0.1.1", None)]
	assert table(rows) == (
		"| App | Pinned | Latest | Status |\n"
		"| --- | --- | --- | --- |\n"
		"| frappe | v16.60.2 | v16.61.0 | update available |\n"
		"| steuerbote | v0.1.1 | none | no release on major version 0 |\n"
	)


def test_bump_moves_every_pin_to_the_newest_release_of_its_major_version(github):
	apps, frappe = bump((ERPNEXT, HRMS, STEUERBOTE), "v16.60.2", github)
	assert apps == (ERPNEXT, App(HRMS.url, "v16.60.0"), STEUERBOTE)
	assert frappe == "v16.61.0"


def test_bump_keeps_frappe_on_its_major_version(github):
	_, frappe = bump((ERPNEXT,), "v15.80.0", github)
	assert frappe == "v15.90.0"


def test_bump_never_moves_a_pin_back(github):
	newer = App(ERPNEXT.url, "v16.62.0")
	assert bump((newer,), "v16.62.0", github) == ((newer,), "v16.62.0")


def test_bump_never_moves_a_fork(github):
	github.releases["alyf-de/erpnext_germany"] = [release("v16.3.0")]
	apps, _ = bump((ERPNEXT, GERMANY_FORK), "v16.60.2", github)
	assert apps == (ERPNEXT, GERMANY_FORK)


def test_bump_moves_a_branch_to_the_newest_release(github):
	apps, _ = bump((ERPNEXT, BRIEFBOTE), "v16.60.2", github)
	assert apps == (ERPNEXT, App(BRIEFBOTE.url, "v0.1.0"))


def test_bump_keeps_a_branch_without_a_release(github):
	github.releases["encircle360-oss/briefbote"] = []
	apps, _ = bump((ERPNEXT, BRIEFBOTE), "v16.60.2", github)
	assert apps == (ERPNEXT, BRIEFBOTE)


def test_write_apps_keeps_the_format_of_apps_json(tmp_path):
	path = tmp_path / "apps.json"
	write_apps(path, (ERPNEXT, STEUERBOTE))
	assert path.read_text(encoding="utf-8") == (
		"[\n"
		"  {\n"
		'    "url": "https://github.com/frappe/erpnext",\n'
		'    "branch": "v16.60.0"\n'
		"  },\n"
		"  {\n"
		'    "url": "https://github.com/encircle360-oss/steuerbote",\n'
		'    "branch": "v0.1.1"\n'
		"  }\n"
		"]\n"
	)
	assert load_apps(path) == (ERPNEXT, STEUERBOTE)


CONTAINERFILE = """\
FROM base AS builder
ARG FRAPPE_BRANCH=v16.60.2
ARG FRAPPE_PATH=https://github.com/frappe/frappe
"""


def test_write_frappe_tag_changes_only_the_default_of_frappe_branch(tmp_path):
	path = tmp_path / "Containerfile"
	path.write_text(CONTAINERFILE, encoding="utf-8")
	write_frappe_tag(path, "v16.61.0")
	assert path.read_text(encoding="utf-8") == CONTAINERFILE.replace("v16.60.2", "v16.61.0")


def test_write_frappe_tag_writes_release_tags_only(tmp_path):
	path = tmp_path / "Containerfile"
	path.write_text(CONTAINERFILE, encoding="utf-8")
	with pytest.raises(ValueError, match="'version-16' is not a release tag"):
		write_frappe_tag(path, "version-16")
	assert path.read_text(encoding="utf-8") == CONTAINERFILE
