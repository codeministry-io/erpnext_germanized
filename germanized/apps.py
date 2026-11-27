"""The apps of the image as apps.json lists them, in frappe_docker's format, and the rules they follow."""

import json
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

APPS_JSON = Path("apps.json")
GITHUB = "https://github.com/"
FRAPPE_URL = "https://github.com/frappe/frappe"
ERPNEXT_URL = "https://github.com/frappe/erpnext"
# Apps with a version line of their own instead of Frappe's major version, such as Insights 3 on Frappe 16. Before
# its first release, such an app may be pinned to a branch; release-check refuses that and bump moves it to the
# first release.
INDEPENDENTLY_VERSIONED = frozenset(
	{
		"https://github.com/encircle360-oss/steuerbote",
		"https://github.com/encircle360-oss/briefbote",
		"https://github.com/frappe/insights",
	}
)
# Forks the image is built from until a release of their upstream repository contains their fixes, each with its
# upstream repository. A fork is pinned to a fork tag: the upstream release it builds on and a counter of the fork,
# such as v16.2.2-encircle360.4. bump never moves a fork; going back to upstream is a change of apps.json by hand.
FORKS = {"https://github.com/encircle360-oss/erpnext_germany": "https://github.com/alyf-de/erpnext_germany"}

_TAG = re.compile(r"v([0-9]+)\.([0-9]+)\.([0-9]+)")
_FORK_TAG = re.compile(r"(?P<base>v[0-9]+\.[0-9]+\.[0-9]+)-encircle360\.[1-9][0-9]*")
# A git branch name as bench clones it, without the forms git refuses, and none that looks like a tag.
_BRANCH = re.compile(r"(?!.*\.\.)(?!.*//)[A-Za-z0-9][A-Za-z0-9._/-]*(?<![./])")
_REPOSITORY_URL = re.compile(r"https://github\.com/[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?/[A-Za-z0-9._-]+")


def is_release_tag(tag: str) -> bool:
	"""Whether a branch is a release tag such as v16.60.0."""
	return _TAG.fullmatch(tag) is not None


def parse_tag(tag: str) -> tuple[int, int, int]:
	"""The version numbers of a release tag, so that tags compare by number."""
	match = _TAG.fullmatch(tag)
	if match is None:
		raise ValueError(f"{tag!r} is not a release tag like v16.60.0")
	major, minor, patch = (int(number) for number in match.groups())
	return major, minor, patch


def is_fork_tag(tag: str) -> bool:
	"""Whether a branch is a fork tag such as v16.2.2-encircle360.4."""
	return _FORK_TAG.fullmatch(tag) is not None


def fork_base(tag: str) -> str:
	"""The upstream release a fork tag builds on: v16.2.2 for v16.2.2-encircle360.4."""
	match = _FORK_TAG.fullmatch(tag)
	if match is None:
		raise ValueError(f"{tag!r} is not a fork tag like v16.2.2-encircle360.1")
	return match["base"]


def is_branch(name: str) -> bool:
	"""Whether a name is a branch and not a release or fork tag: the provisional pin of an app without a release."""
	return _BRANCH.fullmatch(name) is not None and not is_release_tag(name) and not is_fork_tag(name)


@dataclass(frozen=True)
class App:
	"""An app of apps.json: its GitHub repository and the release tag that frappe_docker calls branch."""

	url: str
	tag: str

	@property
	def owner_repo(self) -> str:
		"""The repository as owner/name, the way the GitHub API addresses it."""
		return self.url.removeprefix(GITHUB)

	@property
	def name(self) -> str:
		"""The repository name, which is not always the name of the Python module bench installs."""
		return self.owner_repo.rpartition("/")[2]

	@property
	def major(self) -> int:
		"""The major version of the pinned release tag, or of the upstream release a fork tag builds on."""
		return parse_tag(fork_base(self.tag) if is_fork_tag(self.tag) else self.tag)[0]

	@property
	def upstream(self) -> str | None:
		"""The upstream repository of a fork in FORKS, None for any other app."""
		return FORKS.get(self.url)


def pin_note(app: App) -> str | None:
	"""What a person has to know about a pin that is no plain release: a fork tag or a branch; None otherwise."""
	if is_fork_tag(app.tag) and app.upstream:
		upstream = app.upstream.removeprefix(GITHUB)
		return (
			f"{app.name}: {app.tag} of the fork {app.owner_repo}, based on {fork_base(app.tag)} of {upstream}"
		)
	if is_branch(app.tag):
		return f"{app.name}: the branch {app.tag}, not a release"
	return None


def frappe_app(tag: str) -> App:
	"""Frappe described like an app: the image builds it from FRAPPE_BRANCH, not from apps.json."""
	return App(FRAPPE_URL, tag)


def load_apps(path: Path = APPS_JSON) -> tuple[App, ...]:
	"""The apps of apps.json in their order, which is the order bench installs them in."""
	try:
		entries = json.loads(path.read_text(encoding="utf-8"))
	except json.JSONDecodeError as error:
		raise ValueError(f"{path} is not valid JSON: {error}") from error
	if not isinstance(entries, list):
		raise ValueError(f"{path} must hold a JSON array of apps")
	return tuple(_app(path, number, entry) for number, entry in enumerate(entries, start=1))


def _app(path: Path, number: int, entry: object) -> App:
	if not isinstance(entry, dict) or entry.keys() != {"url", "branch"}:
		raise ValueError(f"{path}: entry {number} must be an object with exactly the keys url and branch")
	url, branch = entry["url"], entry["branch"]
	if not isinstance(url, str) or not isinstance(branch, str):
		raise ValueError(f"{path}: entry {number}: url and branch must be strings")
	return App(url, branch)


def validate(apps: Sequence[App], frappe_tag: str) -> list[str]:
	"""The problems of an app list for the image built on frappe_tag; an empty list means it is valid."""
	if not apps:
		return ["apps.json lists no apps"]
	problems = []
	frappe_major = None
	if is_release_tag(frappe_tag):
		frappe_major = parse_tag(frappe_tag)[0]
	else:
		problems.append(f"FRAPPE_BRANCH {frappe_tag!r} is not a release tag like v16.60.0")
	if apps[0].url != ERPNEXT_URL:
		problems.append(f"the first app must be {ERPNEXT_URL}, not {apps[0].url}")
	seen = set()
	listed = {app.url.lower() for app in apps}
	for app in apps:
		if _REPOSITORY_URL.fullmatch(app.url) is None or app.url.endswith(".git"):
			problems.append(f"{app.url}: not a repository url like https://github.com/<owner>/<repo>")
		# GitHub treats owner and repository names case-insensitively.
		key = app.url.lower()
		if key in seen:
			problems.append(f"{app.url}: listed more than once")
		seen.add(key)
		if app.upstream and app.upstream.lower() in listed:
			problems.append(f"{app.url}: a fork of {app.upstream}, which apps.json lists as well")
		provisional = is_branch(app.tag) and app.url in INDEPENDENTLY_VERSIONED
		if is_fork_tag(app.tag) and not app.upstream:
			problems.append(f"{app.url}: {app.tag} is a fork tag, but the repository is no fork in FORKS")
		elif not (provisional or is_release_tag(app.tag) or is_fork_tag(app.tag)):
			problems.append(f"{app.url}: {app.tag!r} is not a release tag like v16.60.0")
		elif (
			frappe_major is not None and app.url not in INDEPENDENTLY_VERSIONED and app.major != frappe_major
		):
			problems.append(f"{app.url}: {app.tag} is not on major version {frappe_major} of Frappe")
	return problems
