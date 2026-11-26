import json
import re
from pathlib import Path

import pytest

from germanized.apps import (
	ERPNEXT_URL,
	FORKS,
	FRAPPE_URL,
	INDEPENDENTLY_VERSIONED,
	App,
	fork_base,
	frappe_app,
	is_branch,
	is_fork_tag,
	is_release_tag,
	load_apps,
	parse_tag,
	pin_note,
	validate,
)

ERPNEXT = App("https://github.com/frappe/erpnext", "v16.60.0")
HRMS = App("https://github.com/frappe/hrms", "v16.60.0")
STEUERBOTE = App("https://github.com/encircle360-oss/steuerbote", "v0.1.1")
BRIEFBOTE = App("https://github.com/encircle360-oss/briefbote", "v0.1.0")
GERMANY_URL = "https://github.com/alyf-de/erpnext_germany"
GERMANY_FORK = App("https://github.com/encircle360-oss/erpnext_germany", "v16.2.2-encircle360.4")


def write(path: Path, text: str) -> Path:
	path.write_text(text, encoding="utf-8")
	return path


def test_an_app_knows_its_repository_name_and_major_version():
	app = App("https://github.com/alyf-de/erpnext_pdf-on-submit", "v16.3.1")
	assert app.owner_repo == "alyf-de/erpnext_pdf-on-submit"
	assert app.name == "erpnext_pdf-on-submit"
	assert app.major == 16


def test_frappe_is_described_like_an_app():
	frappe = frappe_app("v16.60.2")
	assert frappe.url == FRAPPE_URL == "https://github.com/frappe/frappe"
	assert (frappe.name, frappe.major) == ("frappe", 16)


def test_release_tags_are_v_and_three_numbers():
	assert parse_tag("v16.60.2") == (16, 60, 2)
	assert parse_tag("v0.1.1") == (0, 1, 1)
	assert is_release_tag("v16.0.0")


@pytest.mark.parametrize(
	"tag", ["16.60.2", "v16.60", "v16.60.2-1", "version-16", "v16.60.2-beta.1", "v\u0661\u0666.0.0"]
)
def test_other_branches_are_no_release_tags(tag):
	assert not is_release_tag(tag)
	with pytest.raises(ValueError, match="is not a release tag like"):
		parse_tag(tag)


def test_release_tags_compare_by_number():
	assert parse_tag("v16.10.0") > parse_tag("v16.9.9")


def test_the_major_version_needs_a_release_tag():
	with pytest.raises(ValueError, match="'version-16' is not a release tag"):
		_ = App(ERPNEXT_URL, "version-16").major


def test_a_fork_tag_is_an_upstream_release_with_a_counter_of_the_fork():
	assert is_fork_tag("v16.2.2-encircle360.4")
	assert fork_base("v16.2.2-encircle360.4") == "v16.2.2"
	assert not is_release_tag("v16.2.2-encircle360.4")


@pytest.mark.parametrize(
	"tag",
	[
		"v16.2.2",
		"v16.2.2-encircle360",
		"v16.2.2-encircle360.0",
		"v16.2.2-encircle360.01",
		"v16.2.2-beta.1",
		"v16.2-encircle360.1",
		"16.2.2-encircle360.1",
		"main",
	],
)
def test_other_tags_are_no_fork_tags(tag):
	assert not is_fork_tag(tag)
	with pytest.raises(ValueError, match=re.escape("is not a fork tag like v16.2.2-encircle360.1")):
		fork_base(tag)


def test_a_fork_knows_its_upstream_and_the_major_version_of_its_base():
	assert FORKS[GERMANY_FORK.url] == GERMANY_URL
	assert GERMANY_FORK.upstream == GERMANY_URL
	assert GERMANY_FORK.name == "erpnext_germany"
	assert GERMANY_FORK.major == 16
	assert App(GERMANY_URL, "v16.2.2").upstream is None


@pytest.mark.parametrize("branch", ["main", "develop", "version-16", "feature/print-formats"])
def test_branch_names(branch):
	assert is_branch(branch)


@pytest.mark.parametrize(
	"branch", ["", "-main", "main branch", "main..x", "main/", "v1.0.0", "v16.2.2-encircle360.1"]
)
def test_tags_and_malformed_names_are_no_branches(branch):
	assert not is_branch(branch)


def test_load_apps_keeps_the_order_of_the_file(tmp_path):
	path = write(
		tmp_path / "apps.json",
		json.dumps([{"url": ERPNEXT.url, "branch": ERPNEXT.tag}, {"url": HRMS.url, "branch": HRMS.tag}]),
	)
	assert load_apps(path) == (ERPNEXT, HRMS)


def test_load_apps_reads_apps_json_in_the_working_directory(tmp_path, monkeypatch):
	write(tmp_path / "apps.json", json.dumps([{"url": ERPNEXT.url, "branch": ERPNEXT.tag}]))
	monkeypatch.chdir(tmp_path)
	assert load_apps() == (ERPNEXT,)


@pytest.mark.parametrize(
	("content", "message"),
	[
		("[", "apps.json is not valid JSON"),
		('{"url": "https://github.com/frappe/erpnext"}', "apps.json must hold a JSON array"),
		(
			'["https://github.com/frappe/erpnext"]',
			"entry 1 must be an object with exactly the keys url and branch",
		),
		('[{"url": "https://github.com/frappe/erpnext"}]', "entry 1 must be an object with exactly the keys"),
		(
			'[{"url": "u", "branch": "v1.0.0", "name": "n"}]',
			"entry 1 must be an object with exactly the keys",
		),
		('[{"url": 1, "branch": "v1.0.0"}]', "entry 1: url and branch must be strings"),
		(
			'[{"url": "u", "branch": "v1.0.0"}, {"url": "u", "branch": null}]',
			"entry 2: url and branch must be",
		),
	],
)
def test_load_apps_accepts_only_an_array_of_url_and_branch(tmp_path, content, message):
	with pytest.raises(ValueError, match=re.escape(message)):
		load_apps(write(tmp_path / "apps.json", content))


def test_a_valid_list_has_no_problems():
	assert validate((ERPNEXT, HRMS, STEUERBOTE), "v16.60.2") == []


def test_an_empty_list_is_a_problem():
	assert validate((), "v16.60.2") == ["apps.json lists no apps"]


def test_erpnext_comes_first():
	assert validate((HRMS, ERPNEXT), "v16.60.2") == [
		"the first app must be https://github.com/frappe/erpnext, not https://github.com/frappe/hrms"
	]


@pytest.mark.parametrize(
	"url",
	[
		"https://github.com/alyf-de/banking/",
		"https://github.com/alyf-de/banking.git",
		"http://github.com/alyf-de/banking",
		"https://gitlab.com/alyf-de/banking",
		"https://github.com/alyf-de",
		"https://github.com/alyf-de/banking/tree/main",
		"git@github.com:alyf-de/banking",
		"https://github.com/-alyf-de/banking",
		"https://github.com/alyf-de/bänking",
	],
)
def test_every_url_names_a_github_repository(url):
	assert validate((ERPNEXT, App(url, "v16.6.4")), "v16.60.2") == [
		f"{url}: not a repository url like https://github.com/<owner>/<repo>"
	]


def test_every_app_is_listed_once():
	duplicate = App("https://github.com/Frappe/HRMS", "v16.60.0")
	assert validate((ERPNEXT, HRMS, duplicate), "v16.60.2") == [
		"https://github.com/Frappe/HRMS: listed more than once"
	]


def test_every_branch_is_a_release_tag():
	assert validate((ERPNEXT, App(HRMS.url, "version-16")), "v16.60.2") == [
		"https://github.com/frappe/hrms: 'version-16' is not a release tag like v16.60.0"
	]


def test_apps_are_on_the_major_version_of_frappe():
	assert validate((ERPNEXT, App(HRMS.url, "v15.40.0")), "v16.60.2") == [
		"https://github.com/frappe/hrms: v15.40.0 is not on major version 16 of Frappe"
	]


def test_steuerbote_keeps_its_own_version_numbers():
	assert STEUERBOTE.url in INDEPENDENTLY_VERSIONED
	assert validate((ERPNEXT, STEUERBOTE), "v16.60.2") == []


def test_briefbote_keeps_its_own_version_numbers():
	assert BRIEFBOTE.url in INDEPENDENTLY_VERSIONED
	assert validate((ERPNEXT, BRIEFBOTE), "v16.60.2") == []


def test_an_app_with_its_own_version_numbers_may_be_pinned_to_a_branch_before_its_first_release():
	assert validate((ERPNEXT, App(BRIEFBOTE.url, "main")), "v16.60.2") == []


def test_an_app_with_its_own_version_numbers_needs_a_branch_name_or_a_release_tag():
	assert validate((ERPNEXT, App(BRIEFBOTE.url, "-main")), "v16.60.2") == [
		"https://github.com/encircle360-oss/briefbote: '-main' is not a release tag like v16.60.0"
	]


def test_a_fork_is_pinned_to_a_fork_tag_of_the_major_version_of_frappe():
	assert validate((ERPNEXT, GERMANY_FORK), "v16.60.2") == []
	assert validate((ERPNEXT, App(GERMANY_FORK.url, "v15.24.1-encircle360.1")), "v16.60.2") == [
		"https://github.com/encircle360-oss/erpnext_germany: v15.24.1-encircle360.1 is not on major version 16 of Frappe"
	]


def test_a_fork_may_also_be_pinned_to_a_release_tag():
	assert validate((ERPNEXT, App(GERMANY_FORK.url, "v16.2.2")), "v16.60.2") == []


def test_only_a_fork_in_forks_takes_a_fork_tag():
	assert validate((ERPNEXT, App(GERMANY_URL, "v16.2.2-encircle360.4")), "v16.60.2") == [
		"https://github.com/alyf-de/erpnext_germany: v16.2.2-encircle360.4 is a fork tag, "
		"but the repository is no fork in FORKS"
	]


def test_a_fork_and_its_upstream_are_the_same_app():
	assert validate((ERPNEXT, App(GERMANY_URL, "v16.2.2"), GERMANY_FORK), "v16.60.2") == [
		"https://github.com/encircle360-oss/erpnext_germany: a fork of https://github.com/alyf-de/erpnext_germany, "
		"which apps.json lists as well"
	]


def test_a_pin_note_describes_a_fork_and_a_branch():
	assert pin_note(GERMANY_FORK) == (
		"erpnext_germany: v16.2.2-encircle360.4 of the fork encircle360-oss/erpnext_germany, "
		"based on v16.2.2 of alyf-de/erpnext_germany"
	)
	assert pin_note(App(BRIEFBOTE.url, "main")) == "briefbote: the branch main, not a release"
	assert pin_note(BRIEFBOTE) is None
	assert pin_note(App(GERMANY_FORK.url, "v16.2.2")) is None


def test_frappe_is_pinned_to_a_release_tag():
	assert validate((ERPNEXT, HRMS), "version-16") == [
		"FRAPPE_BRANCH 'version-16' is not a release tag like v16.60.0"
	]


def test_all_problems_are_reported_together():
	problems = validate((HRMS, App("https://github.com/alyf-de/banking.git", "main")), "v16.60.2")
	assert problems == [
		"the first app must be https://github.com/frappe/erpnext, not https://github.com/frappe/hrms",
		"https://github.com/alyf-de/banking.git: not a repository url like https://github.com/<owner>/<repo>",
		"https://github.com/alyf-de/banking.git: 'main' is not a release tag like v16.60.0",
	]
