"""The image tags of a git ref and the scheme of the release tags.

A release is tagged v<erpnext>-<revision>: the ERPNext version the image ships and a counter for changes of
the recipe on that version, starting at 1. The image of a release gets the full tag and the moving tags
<erpnext>, <major> and latest, each only when no newer release holds it; main gets main and main-<commit>;
every other ref is built and not pushed.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
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

	@property
	def version(self) -> tuple[int, ...]:
		"""The ERPNext version as numbers, so that versions compare by number and not as text."""
		return tuple(int(number) for number in self.erpnext.split("."))

	def is_newer_than(self, other: Release) -> bool:
		"""Whether this release comes after another: a newer ERPNext version, or a later revision of it."""
		return (self.version, self.revision) > (other.version, other.revision)


def parse_release(tag: str) -> Release:
	"""The release a tag such as v16.60.0-1 names."""
	match = _RELEASE.fullmatch(tag)
	if match is None:
		raise ValueError(f"{tag!r} is not a release tag like v16.60.0-1 (the revision starts at 1)")
	return Release(match["erpnext"], int(match["revision"]))


def releases(tags: Iterable[str]) -> tuple[Release, ...]:
	"""The releases among git tags, in their order; tags of another form are no releases."""
	return tuple(parse_release(tag) for tag in tags if _RELEASE.fullmatch(tag))


def image_tags(ref: str, sha: str, existing: Iterable[str] = (), image: str = IMAGE) -> tuple[str, ...]:
	"""The tags to push for a git ref and its commit; none for refs that are only built.

	`existing` are the release tags of the repository. A moving tag goes to a release only when no newer
	release holds it, so a late revision of an older version cannot take a moving tag back.
	"""
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
	newer = [other for other in releases(existing) if other.is_newer_than(release)]
	names = [f"{release.erpnext}-{release.revision}"]
	if not any(other.version == release.version for other in newer):
		names.append(release.erpnext)
	if not any(other.version[0] == release.version[0] for other in newer):
		names.append(release.erpnext.partition(".")[0])
	if not newer:
		names.append("latest")
	return tuple(f"{image}:{name}" for name in names)


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
