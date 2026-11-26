"""What a build contains, as Markdown for the job summary of the CI and for the release notes."""

from collections.abc import Mapping, Sequence

from germanized.apps import App, pin_note


def markdown(apps: Sequence[App], pins: Mapping[str, str], tags: Sequence[str]) -> str:
	"""The apps with links and versions, the pinned build arguments and the image tags of a build."""
	frappe = App(pins["FRAPPE_PATH"], pins["FRAPPE_BRANCH"])
	lines = ["### Apps", "", "| App | Version |", "| --- | --- |"]
	lines += [f"| [{app.name}]({app.url}) | `{app.tag}` |" for app in (frappe, *apps)]
	if notes := [note for app in apps if (note := pin_note(app))]:
		lines += ["", *(f"- {note}" for note in notes)]
	lines += ["", "### Build arguments", "", "| Argument | Value |", "| --- | --- |"]
	lines += [f"| `{name}` | `{value}` |" for name, value in pins.items()]
	lines += ["", "### Image tags", ""]
	lines += [f"- `{tag}`" for tag in tags] or ["None: this build is not pushed."]
	return "\n".join(lines) + "\n"
