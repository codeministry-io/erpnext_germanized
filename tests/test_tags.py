import pytest

from germanized.apps import App
from germanized.tags import IMAGE, Release, image_tags, parse_release, release_check

SHA = "0123456789abcdef0123456789abcdef01234567"
APPS = (
	App("https://github.com/frappe/erpnext", "v16.60.0"),
	App("https://github.com/frappe/hrms", "v16.60.0"),
)


def test_the_image_lives_in_the_github_container_registry():
	assert IMAGE == "ghcr.io/encircle360-oss/erpnext_germanized"


def test_main_gets_a_moving_tag_and_one_per_commit():
	assert image_tags("refs/heads/main", SHA) == (
		"ghcr.io/encircle360-oss/erpnext_germanized:main",
		"ghcr.io/encircle360-oss/erpnext_germanized:main-0123456",
	)


def test_a_release_gets_its_full_version_and_the_moving_tags():
	assert image_tags("refs/tags/v16.60.0-1", SHA) == (
		"ghcr.io/encircle360-oss/erpnext_germanized:16.60.0-1",
		"ghcr.io/encircle360-oss/erpnext_germanized:16.60.0",
		"ghcr.io/encircle360-oss/erpnext_germanized:16",
		"ghcr.io/encircle360-oss/erpnext_germanized:latest",
	)


def test_the_tags_can_name_another_image():
	assert image_tags("refs/heads/main", SHA, image="ghcr.io/example/erpnext") == (
		"ghcr.io/example/erpnext:main",
		"ghcr.io/example/erpnext:main-0123456",
	)


@pytest.mark.parametrize(
	"ref",
	[
		"refs/heads/feature/build-and-tools",
		"refs/heads/mainline",
		"refs/pull/12/merge",
		"refs/tags/v16.60.0",
		"refs/tags/latest",
		"main",
	],
)
def test_other_refs_are_built_but_never_pushed(ref):
	assert image_tags(ref, SHA) == ()


@pytest.mark.parametrize("sha", ["", "012345", "0123456789ABCDEF0123456789ABCDEF01234567", "zzzzzzz"])
def test_main_needs_a_commit_sha(sha):
	with pytest.raises(ValueError, match="is not a commit SHA"):
		image_tags("refs/heads/main", sha)


def test_a_release_tag_is_the_erpnext_version_and_a_revision():
	assert parse_release("v16.60.0-1") == Release(erpnext="16.60.0", revision=1)
	assert parse_release("v16.60.0-12") == Release(erpnext="16.60.0", revision=12)


@pytest.mark.parametrize(
	"tag",
	[
		"v16.60.0",
		"16.60.0-1",
		"v16.60-1",
		"v16.60.0-0",
		"v16.60.0-01",
		"v16.60.0-1-rc1",
		"refs/tags/v16.60.0-1",
	],
)
def test_other_tags_are_no_releases(tag):
	with pytest.raises(
		ValueError, match=r"is not a release tag like v16\.60\.0-1 \(the revision starts at 1\)"
	):
		parse_release(tag)


def test_a_release_names_the_erpnext_version_of_apps_json():
	assert release_check("v16.60.0-1", APPS) == []
	assert release_check("v16.60.0-3", APPS) == []


def test_a_release_of_another_erpnext_version_is_refused():
	assert release_check("v16.59.0-1", APPS) == [
		"the release v16.59.0-1 names ERPNext 16.59.0, but apps.json pins v16.60.0"
	]


def test_a_malformed_release_tag_is_refused():
	assert release_check("v16.60.0-0", APPS) == [
		"'v16.60.0-0' is not a release tag like v16.60.0-1 (the revision starts at 1)"
	]


def test_a_release_needs_erpnext_in_apps_json():
	assert release_check("v16.60.0-1", APPS[1:]) == ["apps.json has no app https://github.com/frappe/erpnext"]
