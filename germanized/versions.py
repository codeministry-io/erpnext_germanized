"""Compare the pinned versions with the releases on GitHub and move the pins to the newest release.

Every pin stays on its major version: Frappe and the apps that follow it on Frappe's, the apps with a version line
of their own, such as Steuerbote, Briefbote and Insights, on theirs. Moving to a new major version is a decision for
a person, not for a weekly job. A fork stays on its fork tag and is compared with the releases of its upstream
repository; a branch, the pin of an app before its first release, moves to the newest release of any major version.
"""

import json
import os
import urllib.error
import urllib.request
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from germanized.apps import (
	GITHUB,
	App,
	fork_base,
	frappe_app,
	is_branch,
	is_fork_tag,
	is_release_tag,
	parse_tag,
)
from germanized.containerfile import set_arg_default

GITHUB_API = "https://api.github.com/"

type Fetch = Callable[[str], bytes]


def fetch_github(url: str) -> bytes:
	"""GET a GitHub API url; GITHUB_TOKEN is sent when it is set and raises the rate limit."""
	if not url.startswith(GITHUB_API):
		raise ValueError(f"fetch_github only fetches from {GITHUB_API}, not {url}")
	headers = {
		"Accept": "application/vnd.github+json",
		"X-GitHub-Api-Version": "2022-11-28",
		"User-Agent": "erpnext_germanized",
	}
	if token := os.environ.get("GITHUB_TOKEN"):
		headers["Authorization"] = f"Bearer {token}"
	# The prefix check above keeps every request on https://api.github.com.
	request = urllib.request.Request(url, headers=headers)  # noqa: S310
	try:
		with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
			return response.read()
	except urllib.error.URLError as error:
		raise OSError(f"GET {url} failed: {error}") from error


def latest_release(owner_repo: str, major: int | None, fetch: Fetch = fetch_github) -> str | None:
	"""The newest published release of a repository on one major version, or on any for None; None when there is none."""
	releases = json.loads(fetch(f"{GITHUB_API}repos/{owner_repo}/releases?per_page=30"))
	if not isinstance(releases, list):
		raise ValueError(f"unexpected answer from GitHub for {owner_repo}")
	tags = [
		release["tag_name"]
		for release in releases
		if not release["prerelease"]
		and not release["draft"]
		and is_release_tag(release["tag_name"])
		and major in (None, parse_tag(release["tag_name"])[0])
	]
	return max(tags, key=parse_tag, default=None)


@dataclass(frozen=True)
class Row:
	"""A pinned version next to the newest release on its major version, of the upstream repository for a fork."""

	name: str
	pinned: str
	latest: str | None
	upstream: str = ""

	@property
	def status(self) -> str:
		"""Whether the pin is behind the newest release."""
		if is_branch(self.pinned):
			return "branch, no release yet" if self.latest is None else "branch, a release is available"
		if self.upstream:
			base = fork_base(self.pinned)
			fork = f"fork of {self.upstream} {base}"
			if self.latest is None:
				return f"{fork}, upstream has no release on major version {parse_tag(base)[0]}"
			if parse_tag(self.latest) > parse_tag(base):
				return f"{fork}, upstream has a newer release"
			return f"{fork}, the newest upstream release"
		if self.latest is None:
			return f"no release on major version {parse_tag(self.pinned)[0]}"
		if parse_tag(self.latest) > parse_tag(self.pinned):
			return "update available"
		return "up to date"


def check(apps: Sequence[App], frappe_tag: str, fetch: Fetch = fetch_github) -> list[Row]:
	"""Frappe and every app with its pin and the newest release on the same major version."""
	return [_row(app, fetch) for app in (frappe_app(frappe_tag), *apps)]


def _row(app: App, fetch: Fetch) -> Row:
	if is_branch(app.tag):
		return Row(app.name, app.tag, latest_release(app.owner_repo, None, fetch))
	if is_fork_tag(app.tag) and app.upstream:
		upstream = app.upstream.removeprefix(GITHUB)
		return Row(app.name, app.tag, latest_release(upstream, app.major, fetch), upstream)
	return Row(app.name, app.tag, latest_release(app.owner_repo, app.major, fetch))


def table(rows: Sequence[Row]) -> str:
	"""The rows as a Markdown table, readable in a terminal and in a pull request."""
	lines = ["| App | Pinned | Latest | Status |", "| --- | --- | --- | --- |"]
	lines += [f"| {row.name} | {row.pinned} | {row.latest or 'none'} | {row.status} |" for row in rows]
	return "\n".join(lines) + "\n"


def bump(apps: Sequence[App], frappe_tag: str, fetch: Fetch = fetch_github) -> tuple[tuple[App, ...], str]:
	"""The apps and the Frappe tag, each moved to the newest release on its major version, never back.

	A fork stays on its tag. A branch moves to the newest release of any major version once there is one.
	"""
	return tuple(App(app.url, _newest(app, fetch)) for app in apps), _newest(frappe_app(frappe_tag), fetch)


def _newest(app: App, fetch: Fetch) -> str:
	if is_fork_tag(app.tag):
		return app.tag
	if is_branch(app.tag):
		return latest_release(app.owner_repo, None, fetch) or app.tag
	latest = latest_release(app.owner_repo, app.major, fetch)
	if latest is not None and parse_tag(latest) > parse_tag(app.tag):
		return latest
	return app.tag


def write_apps(path: Path, apps: Sequence[App]) -> None:
	"""Write apps.json in its format: frappe_docker's keys, an indentation of two spaces, a final newline."""
	entries = [{"url": app.url, "branch": app.tag} for app in apps]
	path.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")


def write_frappe_tag(containerfile_path: Path, tag: str) -> None:
	"""Set the default of ARG FRAPPE_BRANCH and leave the rest of the Containerfile as it is."""
	if not is_release_tag(tag):
		raise ValueError(f"{tag!r} is not a release tag like v16.60.0")
	text = containerfile_path.read_text(encoding="utf-8")
	containerfile_path.write_text(set_arg_default(text, "FRAPPE_BRANCH", tag), encoding="utf-8")
