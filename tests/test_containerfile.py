import pytest

from germanized.containerfile import (
	PIN_ARGS,
	arg_default,
	base_image,
	frappe_tag,
	pins,
	set_arg_default,
	split_digest,
)

DIGEST = "sha256:" + "0123456789abcdef" * 4

TEXT = """\
# syntax=docker/dockerfile:1

# ARG FRAPPE_BRANCH=v1.0.0 in a comment is no pin
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
ARG CACHE_BUST=""
FROM base AS backend
ARG PYTHON_VERSION
ARG VERSION=dev
"""


def test_arg_default_is_the_value_after_the_equals_sign():
	assert arg_default(TEXT, "FRAPPE_BRANCH") == "v16.60.2"
	assert arg_default(TEXT, "FRAPPE_PATH") == "https://github.com/frappe/frappe"


def test_an_arg_declared_again_without_a_value_keeps_its_default():
	assert arg_default(TEXT, "PYTHON_VERSION") == "3.14"


def test_quotes_around_a_default_are_no_part_of_it():
	assert arg_default(TEXT, "CACHE_BUST") == ""
	assert arg_default("ARG NODE_VERSION='24'\n", "NODE_VERSION") == "24"


def test_instructions_are_case_insensitive_and_may_be_indented():
	assert arg_default("  arg NODE_VERSION=24\n", "NODE_VERSION") == "24"


def test_the_name_must_match_completely():
	assert arg_default("ARG NODE_VERSION_MAJOR=1\nARG NODE_VERSION=24\n", "NODE_VERSION") == "24"


def test_an_arg_without_default_is_an_error():
	with pytest.raises(ValueError, match="the Containerfile has no default for ARG MISSING"):
		arg_default(TEXT, "MISSING")
	with pytest.raises(ValueError, match="no default for ARG NODE_VERSION"):
		arg_default("ARG NODE_VERSION\n", "NODE_VERSION")


def test_a_default_set_twice_is_an_error():
	with pytest.raises(ValueError, match="sets a default for ARG NODE_VERSION more than once"):
		arg_default("ARG NODE_VERSION=24\nARG NODE_VERSION=22\n", "NODE_VERSION")


def test_frappe_tag_reads_the_containerfile_of_the_working_directory(tmp_path, monkeypatch):
	(tmp_path / "Containerfile").write_text(TEXT, encoding="utf-8")
	monkeypatch.chdir(tmp_path)
	assert frappe_tag() == "v16.60.2"


def test_frappe_tag_reads_a_given_path(tmp_path):
	path = tmp_path / "Other"
	path.write_text("ARG FRAPPE_BRANCH=v16.1.0\n", encoding="utf-8")
	assert frappe_tag(path) == "v16.1.0"


def test_base_image_is_the_image_of_the_first_from():
	assert base_image(TEXT) == "python:3.14-slim-trixie"


def test_base_image_skips_flags_and_ignores_case():
	assert (
		base_image("FROM --platform=linux/amd64 python:3.14-slim-trixie AS base\n")
		== "python:3.14-slim-trixie"
	)
	assert base_image("  from debian:trixie\n") == "debian:trixie"


def test_base_image_keeps_the_digest_that_pins_it():
	text = f"FROM python:3.14-slim-trixie@{DIGEST} AS base\n"
	assert base_image(text) == f"python:3.14-slim-trixie@{DIGEST}"


def test_split_digest_separates_the_image_and_its_tag_from_the_digest():
	assert split_digest(f"python:3.14-slim-trixie@{DIGEST}") == ("python:3.14-slim-trixie", DIGEST)


def test_an_image_without_digest_has_none():
	assert split_digest("python:3.14-slim-trixie") == ("python:3.14-slim-trixie", None)


@pytest.mark.parametrize(
	"digest", ["", "sha256:", "sha256:0123abcd", "sha512:" + "0" * 128, "sha256:" + "A" * 64, "latest"]
)
def test_a_digest_is_sha256_with_64_hex_digits(digest):
	with pytest.raises(ValueError, match="is not a sha256 digest with 64 hex digits"):
		split_digest(f"python:3.14-slim-trixie@{digest}")


def test_base_image_needs_a_from_with_an_image():
	with pytest.raises(ValueError, match="the Containerfile has no FROM"):
		base_image("ARG NODE_VERSION=24\n\n")
	with pytest.raises(ValueError, match="the first FROM names no image"):
		base_image("FROM --platform=linux/amd64\n")


def test_pins_are_the_build_arguments_in_a_fixed_order():
	assert pins(TEXT) == {
		"FRAPPE_BRANCH": "v16.60.2",
		"FRAPPE_PATH": "https://github.com/frappe/frappe",
		"PYTHON_VERSION": "3.14",
		"DEBIAN_BASE": "trixie",
		"NODE_VERSION": "24",
		"WKHTMLTOPDF_VERSION": "0.12.6.1-3",
		"WKHTMLTOPDF_DISTRO": "bookworm",
		"INSTALL_CHROMIUM": "true",
	}
	assert tuple(pins(TEXT)) == PIN_ARGS


def test_set_arg_default_changes_nothing_but_that_default():
	changed = set_arg_default(TEXT, "FRAPPE_BRANCH", "v16.61.0")
	assert changed == TEXT.replace("ARG FRAPPE_BRANCH=v16.60.2", "ARG FRAPPE_BRANCH=v16.61.0")


def test_set_arg_default_keeps_quotes_and_indentation():
	assert set_arg_default("  ARG NODE_VERSION='24' \n", "NODE_VERSION", "26") == "  ARG NODE_VERSION='26' \n"


def test_set_arg_default_needs_exactly_one_default():
	with pytest.raises(ValueError, match="no default for ARG MISSING"):
		set_arg_default(TEXT, "MISSING", "1")
	with pytest.raises(ValueError, match="more than once"):
		set_arg_default("ARG NODE_VERSION=24\nARG NODE_VERSION=22\n", "NODE_VERSION", "26")
