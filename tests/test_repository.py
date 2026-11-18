"""Checks of the files of this repository, so that a change to one of them cannot leave the others behind."""

from pathlib import Path

from germanized.apps import load_apps, validate
from germanized.containerfile import base_image, frappe_tag, pins
from germanized.versions import write_apps

ROOT = Path(__file__).resolve().parents[1]
APPS_JSON = ROOT / "apps.json"
CONTAINERFILE = ROOT / "Containerfile"


def test_apps_json_follows_the_rules_of_the_image():
	assert validate(load_apps(APPS_JSON), frappe_tag(CONTAINERFILE)) == []


def test_the_first_from_names_the_image_of_the_python_and_debian_pins():
	# Dependabot updates the literal FROM, the other stages and the labels read the ARGs.
	text = CONTAINERFILE.read_text(encoding="utf-8")
	pinned = pins(text)
	assert base_image(text) == f"python:{pinned['PYTHON_VERSION']}-slim-{pinned['DEBIAN_BASE']}"


def test_apps_json_has_the_format_that_bump_writes(tmp_path):
	rewritten = tmp_path / "apps.json"
	write_apps(rewritten, load_apps(APPS_JSON))
	assert rewritten.read_text(encoding="utf-8") == APPS_JSON.read_text(encoding="utf-8")
