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
# Apps with a version line of their own instead of Frappe's major version.
INDEPENDENTLY_VERSIONED = frozenset(
	{"https://github.com/encircle360-oss/steuerbote", "https://github.com/frappe/insights"}
)

_TAG = re.compile(r"v([0-9]+)\.([0-9]+)\.([0-9]+)")
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
		"""The major version of the pinned release tag."""
		return parse_tag(self.tag)[0]


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
	for app in apps:
		if _REPOSITORY_URL.fullmatch(app.url) is None or app.url.endswith(".git"):
			problems.append(f"{app.url}: not a repository url like https://github.com/<owner>/<repo>")
		# GitHub treats owner and repository names case-insensitively.
		key = app.url.lower()
		if key in seen:
			problems.append(f"{app.url}: listed more than once")
		seen.add(key)
		if not is_release_tag(app.tag):
			problems.append(f"{app.url}: {app.tag!r} is not a release tag like v16.60.0")
		elif (
			frappe_major is not None and app.url not in INDEPENDENTLY_VERSIONED and app.major != frappe_major
		):
			problems.append(f"{app.url}: {app.tag} is not on major version {frappe_major} of Frappe")
	return problems
