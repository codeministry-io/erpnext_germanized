"""Checks of the files of this repository, so that a change to one of them cannot leave the others behind."""

import re
from pathlib import Path

import pytest

from germanized.apps import load_apps, validate
from germanized.containerfile import base_image, frappe_tag, pins, split_digest
from germanized.versions import write_apps

ROOT = Path(__file__).resolve().parents[1]
APPS_JSON = ROOT / "apps.json"
CONTAINERFILE = ROOT / "Containerfile"
PRE_COMMIT_CONFIG = ROOT / ".pre-commit-config.yaml"
REQUIREMENTS_DEV = ROOT / "requirements-dev.txt"


def hook_revisions() -> dict[str, str]:
	"""The rev of each hook repository in .pre-commit-config.yaml, where rev follows repo directly."""
	text = PRE_COMMIT_CONFIG.read_text(encoding="utf-8")
	return dict(re.findall(r"^\s*- repo: *(\S+) *\n\s*rev: *['\"]?([^'\"\s]+)['\"]? *$", text, re.MULTILINE))


def development_pins() -> dict[str, str]:
	"""The exact versions of requirements-dev.txt by package."""
	text = REQUIREMENTS_DEV.read_text(encoding="utf-8")
	return dict(re.findall(r"^([A-Za-z0-9._-]+)==(\S+)$", text, re.MULTILINE))


def test_apps_json_follows_the_rules_of_the_image():
	assert validate(load_apps(APPS_JSON), frappe_tag(CONTAINERFILE)) == []


def test_the_first_from_names_the_image_of_the_python_and_debian_pins():
	# Dependabot updates the literal FROM, the other stages and the labels read the ARGs.
	text = CONTAINERFILE.read_text(encoding="utf-8")
	pinned = pins(text)
	image, _ = split_digest(base_image(text))
	assert image == f"python:{pinned['PYTHON_VERSION']}-slim-{pinned['DEBIAN_BASE']}"


def test_the_first_from_pins_the_base_image_by_digest():
	# The tag moves with every patch release of Python and every rebuild on Debian, but without a digest in
	# the FROM, Dependabot has nothing to propose.
	_, digest = split_digest(base_image(CONTAINERFILE.read_text(encoding="utf-8")))
	assert digest is not None


@pytest.mark.parametrize(
	("hook", "tool"),
	[
		("https://github.com/astral-sh/ruff-pre-commit", "ruff"),
		("https://github.com/zizmorcore/zizmor-pre-commit", "zizmor"),
	],
)
def test_the_hooks_run_the_versions_that_requirements_dev_pins(hook, tool):
	# The CI runs ruff and zizmor from requirements-dev.txt, pre-commit from the hooks. Dependabot updates the
	# two files as separate ecosystems, so a version that moves in only one of them fails here.
	assert hook_revisions()[hook] == f"v{development_pins()[tool]}"


def test_apps_json_has_the_format_that_bump_writes(tmp_path):
	rewritten = tmp_path / "apps.json"
	write_apps(rewritten, load_apps(APPS_JSON))
	assert rewritten.read_text(encoding="utf-8") == APPS_JSON.read_text(encoding="utf-8")


def image_labels() -> dict[str, str]:
	"""The labels of the LABEL instruction of the Containerfile, by key without the prefix of the OCI annotations."""
	text = CONTAINERFILE.read_text(encoding="utf-8")
	(instruction,) = re.findall(r"^LABEL ((?:.*\\\n)*.*)$", text, re.MULTILINE)
	return {
		key.removeprefix("org.opencontainers.image."): value
		for key, value in re.findall(r'(\S+)="([^"]*)"', instruction)
	}


def test_the_labels_name_the_image_its_maker_and_where_to_read_about_it():
	repository = "https://github.com/encircle360-oss/erpnext_germanized"
	labels = image_labels()
	assert {
		key: labels.get(key) for key in ("title", "vendor", "authors", "url", "source", "documentation")
	} == {
		"title": "erpnext_germanized",
		"vendor": "encircle360 GmbH",
		"authors": "encircle360 GmbH and contributors <oss@encircle360.com>",
		"url": repository,
		"source": repository,
		"documentation": f"{repository}#readme",
	}
	assert labels["description"].startswith("ERPNext 16 for German companies")
