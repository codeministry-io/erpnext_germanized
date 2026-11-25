"""The table of the included apps in README.md, kept in step with apps.json and the Containerfile.

The table is the first one under the heading `## Enthaltene Apps` with the columns App, Version, Zweck and
Lizenz. It has one row for Frappe and then one row per app in the order of apps.json. The App cell links the
repository under its name, `[erpnext](https://github.com/frappe/erpnext)`, and the Version cell holds the
pinned tag, `v16.60.0`. Zweck and Lizenz are written by hand and never touched by the tools; the row of a fork
links its upstream repository there, so that the table names where the app comes from.
"""

import itertools
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from germanized.apps import ERPNEXT_URL, FRAPPE_URL, App, frappe_app

README = Path("README.md")
HEADING = "## Enthaltene Apps"
COLUMNS = ("App", "Version", "Zweck", "Lizenz")

_PIPE = re.compile(r"(?<!\\)\|")
_SEPARATOR_CELL = re.compile(r":?-+:?")
_LINK = re.compile(r"\[(?P<name>[^\]]*)\]\((?P<url>[^)\s]*)\)")
_FENCE = re.compile(r" {0,3}(?:```|~~~)")
_SECTION_END = re.compile(r"#{1,2}(?:[ \t]|$)")


@dataclass(frozen=True)
class _Row:
	"""A data row of the app table: its index in the lines, its text and the spans of its cells."""

	index: int
	text: str
	spans: tuple[tuple[int, int], ...]

	@property
	def cells(self) -> tuple[str, ...]:
		return tuple(self.text[start:end].strip() for start, end in self.spans)

	@property
	def where(self) -> str:
		return f"README.md line {self.index + 1}"


def _spans(line: str) -> tuple[tuple[int, int], ...] | None:
	"""The spans of the cells of a table line with outer pipes, or None for any other line."""
	pipes = [match.start() for match in _PIPE.finditer(line)]
	if len(pipes) < 2 or line[: pipes[0]].strip() or line[pipes[-1] + 1 :].strip():
		return None
	return tuple((start + 1, end) for start, end in itertools.pairwise(pipes))


def _cells(line: str) -> tuple[str, ...] | None:
	spans = _spans(line)
	return None if spans is None else _Row(0, line, spans).cells


def _section(lines: Sequence[str]) -> list[int]:
	"""Indexes of the lines under HEADING up to the next heading of level 1 or 2, outside code blocks."""
	starts = [index for index, line in enumerate(lines) if line.rstrip() == HEADING]
	if not starts:
		raise ValueError(f"README.md has no section {HEADING!r}")
	if len(starts) > 1:
		raise ValueError(f"README.md has the section {HEADING!r} more than once")
	indexes = []
	in_code = False
	for index in range(starts[0] + 1, len(lines)):
		if _FENCE.match(lines[index]):
			in_code = not in_code
		elif not in_code:
			if _SECTION_END.match(lines[index]):
				break
			indexes.append(index)
	return indexes


def _rows(lines: Sequence[str]) -> list[_Row]:
	"""The data rows of the app table: the table lines that follow its header and separator."""
	header = next((index for index in _section(lines) if _cells(lines[index]) == COLUMNS), None)
	if header is None:
		raise ValueError(f"the section {HEADING!r} has no table with the columns {' | '.join(COLUMNS)}")
	separator = _cells(lines[header + 1]) if header + 1 < len(lines) else None
	if (
		separator is None
		or len(separator) != len(COLUMNS)
		or not all(_SEPARATOR_CELL.fullmatch(cell) for cell in separator)
	):
		raise ValueError("the app table needs a separator line like |---|---|---|---| under its header")
	rows = []
	for index in range(header + 2, len(lines)):
		spans = _spans(lines[index])
		if spans is None:
			break
		rows.append(_Row(index, lines[index], spans))
	return rows


def _pinned(apps: Sequence[App], frappe_tag: str) -> list[App]:
	return [frappe_app(frappe_tag), *apps]


def check(readme_text: str, apps: Sequence[App], frappe_tag: str) -> list[str]:
	"""How the app table differs from the pins; an empty list means it is in step."""
	try:
		rows = _rows(readme_text.splitlines())
	except ValueError as error:
		return [str(error)]
	expected = _pinned(apps, frappe_tag)
	by_url = {app.url: app for app in expected}
	problems = []
	listed: list[str] = []
	complete = True
	for row in rows:
		cells = row.cells
		if len(cells) != len(COLUMNS):
			problems.append(f"{row.where}: {len(cells)} cells instead of {len(COLUMNS)}")
			complete = False
			continue
		link = _LINK.fullmatch(cells[0])
		if link is None:
			problems.append(
				f"{row.where}: the App cell must be a link like [erpnext]({ERPNEXT_URL}), not {cells[0]!r}"
			)
			complete = False
			continue
		app = by_url.get(link["url"])
		if app is None:
			problems.append(f"{row.where}: {link['url']} is neither Frappe nor an app of apps.json")
			complete = False
			continue
		if app.url in listed:
			problems.append(f"{row.where}: a second row for {app.name}")
			complete = False
			continue
		listed.append(app.url)
		if link["name"] != app.name:
			problems.append(f"{row.where}: the link text must be {app.name}, not {link['name']}")
		if cells[1] != app.tag:
			source = "the Containerfile" if app.url == FRAPPE_URL else "apps.json"
			problems.append(f"{row.where}: {app.name} has the version {cells[1]!r}, {source} pins {app.tag}")
		if app.upstream and not _links(row.text, app.upstream):
			problems.append(
				f"{row.where}: {app.name} is pinned to the fork {app.url}, "
				f"so its row must link the upstream repository {app.upstream}"
			)
	missing = [app for app in expected if app.url not in listed]
	problems += [f"README.md has no row for {app.name} ({app.url})" for app in missing]
	if complete and not missing and listed != [app.url for app in expected]:
		problems.append(
			"the rows of the app table must list frappe first and then the apps in the order of apps.json"
		)
	return problems


def _links(text: str, repository: str) -> bool:
	"""Whether a text links a repository or a page inside it, such as a pull request."""
	return any(
		link["url"] == repository or link["url"].startswith(repository + "/") for link in _LINK.finditer(text)
	)


def update(readme_text: str, apps: Sequence[App], frappe_tag: str) -> str:
	"""The README with the Version cell of every row of Frappe or an app set to its pin."""
	lines = readme_text.splitlines(keepends=True)
	texts = [line.rstrip("\r\n") for line in lines]
	versions = {app.url: app.tag for app in _pinned(apps, frappe_tag)}
	for row in _rows(texts):
		cells = row.cells
		link = _LINK.fullmatch(cells[0]) if len(cells) == len(COLUMNS) else None
		if link is None or link["url"] not in versions or cells[1] == versions[link["url"]]:
			continue
		start, end = row.spans[1]
		cell = row.text[start:end]
		if cell.strip():
			lead = len(cell) - len(cell.lstrip())
			trail = len(cell) - len(cell.rstrip())
			new_cell = cell[:lead] + versions[link["url"]] + cell[len(cell) - trail :]
		else:
			new_cell = f" {versions[link['url']]} "
		ending = lines[row.index][len(row.text) :]
		lines[row.index] = row.text[:start] + new_cell + row.text[end:] + ending
	return "".join(lines)
