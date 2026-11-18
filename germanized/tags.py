"""The image tags of a git ref and the scheme of the release tags.

A release is tagged v<erpnext>-<revision>: the ERPNext version the image ships and a counter for changes of
the recipe on that version, starting at 1. The image of a release gets the full tag and the moving tags
<erpnext>, <major> and latest; main gets main and main-<commit>; every other ref is built and not pushed.
"""

import re
from collections.abc import Sequence
from dataclasses import dataclass

from germanized.apps import ERPNEXT_URL, App

IMAGE = "ghcr.io/encircle360-oss/erpnext_germanized"
MAIN = "refs/heads/main"
TAG_PREFIX = "refs/tags/"

_RELEASE = re.compile(r"v(?P<erpnext>[0-9]+\.[0-9]+\.[0-9]+)-(?P<revision>[1-9][0-9]*)")
_SHA = re.compile(r"[0-9a-f]{7,40}")


@dataclass(frozen=True)
class Release:
	"""A release of the image: the ERPNext version it ships and the revision of the recipe."""

	erpnext: str
	revision: int


def parse_release(tag: str) -> Release:
	"""The release a tag such as v16.60.0-1 names."""
	match = _RELEASE.fullmatch(tag)
	if match is None:
		raise ValueError(f"{tag!r} is not a release tag like v16.60.0-1 (the revision starts at 1)")
	return Release(match["erpnext"], int(match["revision"]))


def image_tags(ref: str, sha: str, image: str = IMAGE) -> tuple[str, ...]:
	"""The tags to push for a git ref and its commit; none for refs that are only built."""
	if ref == MAIN:
		if _SHA.fullmatch(sha) is None:
			raise ValueError(f"{sha!r} is not a commit SHA")
		return (f"{image}:main", f"{image}:main-{sha[:7]}")
	if not ref.startswith(TAG_PREFIX):
		return ()
	try:
		release = parse_release(ref.removeprefix(TAG_PREFIX))
	except ValueError:
		return ()
	major = release.erpnext.partition(".")[0]
	return (
		f"{image}:{release.erpnext}-{release.revision}",
		f"{image}:{release.erpnext}",
		f"{image}:{major}",
		f"{image}:latest",
	)


def release_check(tag: str, apps: Sequence[App]) -> list[str]:
	"""The problems of a release tag: it must name the ERPNext version that apps.json pins."""
	try:
		release = parse_release(tag)
	except ValueError as error:
		return [str(error)]
	erpnext = next((app for app in apps if app.url == ERPNEXT_URL), None)
	if erpnext is None:
		return [f"apps.json has no app {ERPNEXT_URL}"]
	if release.erpnext != erpnext.tag.removeprefix("v"):
		return [f"the release {tag} names ERPNext {release.erpnext}, but apps.json pins {erpnext.tag}"]
	return []
