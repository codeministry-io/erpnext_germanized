import json
import re
from pathlib import Path

import pytest

from germanized.apps import (
	ERPNEXT_URL,
	FRAPPE_URL,
	INDEPENDENTLY_VERSIONED,
	App,
	frappe_app,
	is_release_tag,
	load_apps,
	parse_tag,
	validate,
)

ERPNEXT = App("https://github.com/frappe/erpnext", "v16.60.0")
HRMS = App("https://github.com/frappe/hrms", "v16.60.0")
STEUERBOTE = App("https://github.com/encircle360-oss/steuerbote", "v0.1.1")
INSIGHTS = App("https://github.com/frappe/insights", "v3.50.3")


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


def test_insights_keeps_its_own_version_numbers():
	assert INSIGHTS.url in INDEPENDENTLY_VERSIONED
	assert validate((ERPNEXT, INSIGHTS), "v16.60.2") == []


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
