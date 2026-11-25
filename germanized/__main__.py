"""The command line of the tools: `python -m germanized <command>`, run from the repository root.

Every command exits with 0 when it succeeds and with 1 and a message on stderr on any problem.
"""

import argparse
import re
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from germanized import readme, versions
from germanized.apps import APPS_JSON, GITHUB, App, frappe_app, is_fork_tag, load_apps, pin_note, validate
from germanized.containerfile import CONTAINERFILE, frappe_tag, pins
from germanized.node_modules import prune
from germanized.summary import markdown
from germanized.tags import TAG_PREFIX, image_tags, parse_release, release_check

type Command = Callable[[argparse.Namespace], int]


def _words(text: str) -> list[str]:
	# Lists come separated by commas, as build-push-action takes tags, or by lines, as git prints tags.
	return [word for word in re.split(r"[\s,]+", text) if word]


def _report(headline: str, problems: Sequence[str]) -> int:
	print(headline, file=sys.stderr)
	for problem in problems:
		print(f"- {problem}", file=sys.stderr)
	return 1


def _notes(apps: Sequence[App]) -> None:
	for app in apps:
		if note := pin_note(app):
			print(f"note: {note}")


def _valid_pins() -> tuple[tuple[App, ...], str]:
	apps, tag = load_apps(), frappe_tag()
	if problems := validate(apps, tag):
		raise ValueError("apps.json breaks the rules of the image: " + "; ".join(problems))
	return apps, tag


def _validate(args: argparse.Namespace) -> int:
	apps, tag = load_apps(), frappe_tag()
	if problems := validate(apps, tag):
		return _report("apps.json breaks the rules of the image:", problems)
	print(f"apps.json is valid: {len(apps)} apps on Frappe {tag}")
	_notes(apps)
	return 0


def _tags(args: argparse.Namespace) -> int:
	print(",".join(image_tags(args.ref, args.sha, _words(args.existing))))
	return 0


def _release_check(args: argparse.Namespace) -> int:
	if not args.ref.startswith(TAG_PREFIX):
		raise ValueError(f"{args.ref} is not a tag ref like refs/tags/v16.60.0-1")
	tag = args.ref.removeprefix(TAG_PREFIX)
	apps = load_apps()
	if problems := release_check(tag, apps):
		return _report(f"{args.ref} cannot be released:", problems)
	print(f"{tag} is a release of ERPNext v{parse_release(tag).erpnext} as apps.json pins it")
	_notes(apps)
	return 0


def _summary(args: argparse.Namespace) -> int:
	print(markdown(load_apps(), pins(CONTAINERFILE.read_text(encoding="utf-8")), _words(args.tags)), end="")
	return 0


def _check_versions(args: argparse.Namespace) -> int:
	apps, tag = _valid_pins()
	print(versions.table(versions.check(apps, tag)), end="")
	return 0


def _bump(args: argparse.Namespace) -> int:
	apps, tag = _valid_pins()
	new_apps, new_tag = versions.bump(apps, tag)
	before, after = (frappe_app(tag), *apps), (frappe_app(new_tag), *new_apps)
	changes = [(old, new) for old, new in zip(before, after, strict=True) if old.tag != new.tag]
	for app in apps:
		if is_fork_tag(app.tag) and app.upstream:
			print(
				f"{app.name}: {app.tag} stays, bump never moves a fork; "
				f"check-versions compares it with {app.upstream.removeprefix(GITHUB)}"
			)
	if not changes:
		print("every pin is on the newest release of its major version")
		return 0
	for old, new in changes:
		print(f"{old.name}: {old.tag} -> {new.tag}")
	if not args.write:
		print("nothing written: pass --write to change apps.json and the Containerfile")
		return 0
	written = []
	if new_apps != apps:
		versions.write_apps(APPS_JSON, new_apps)
		written.append("apps.json")
	if new_tag != tag:
		versions.write_frappe_tag(CONTAINERFILE, new_tag)
		written.append("the Containerfile")
	print("wrote " + " and ".join(written))
	return 0


def _readme(args: argparse.Namespace) -> int:
	apps, tag = load_apps(), frappe_tag()
	text = readme.README.read_text(encoding="utf-8")
	if args.write:
		updated = readme.update(text, apps, tag)
		if updated == text:
			print("README.md: the versions of the app table are up to date")
		else:
			readme.README.write_text(updated, encoding="utf-8")
			print("README.md: updated the versions of the app table")
		return 0
	if problems := readme.check(text, apps, tag):
		return _report("README.md is not in step with the pins:", problems)
	print(f"README.md lists frappe and the {len(apps)} apps with their pinned versions")
	return 0


def _prune_node_modules(args: argparse.Namespace) -> int:
	for line in prune(args.bench):
		print(line)
	return 0


def _parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		prog="python -m germanized",
		description="Tools for the erpnext_germanized image recipe, run from the repository root.",
	)
	commands = parser.add_subparsers(dest="command", metavar="command", required=True)

	def command(name: str, run: Command, purpose: str) -> argparse.ArgumentParser:
		subparser = commands.add_parser(name, help=purpose, description=purpose)
		subparser.set_defaults(run=run)
		return subparser

	command("validate", _validate, "check apps.json against the rules of the image")
	tags = command("tags", _tags, "print the image tags of a git ref, separated by commas")
	tags.add_argument(
		"--ref", required=True, help="the git ref, such as refs/heads/main or refs/tags/v16.60.0-1"
	)
	tags.add_argument("--sha", required=True, help="the commit of the ref")
	tags.add_argument(
		"--existing",
		default="",
		help="the release tags of the repository as git tag -l 'v*' lists them, separated by whitespace or commas",
	)
	release = command("release-check", _release_check, "check that a release tag names the pinned ERPNext")
	release.add_argument("--ref", required=True, help="the tag ref, such as refs/tags/v16.60.0-1")
	summary = command("summary", _summary, "print the apps, pins and tags of a build as Markdown")
	summary.add_argument("--tags", default="", help="the image tags, separated by commas or whitespace")
	command("check-versions", _check_versions, "compare the pins with the newest releases on GitHub")
	bump = command("bump", _bump, "move every pin to the newest release on its major version")
	bump.add_argument("--write", action="store_true", help="write apps.json and the Containerfile")
	readme_command = command("readme", _readme, "check or update the app table of README.md")
	mode = readme_command.add_mutually_exclusive_group(required=True)
	mode.add_argument("--check", action="store_true", help="fail when the table differs from the pins")
	mode.add_argument("--write", action="store_true", help="set the Version cells to the pins")
	prune_command = command(
		"prune-node-modules",
		_prune_node_modules,
		"remove the Node.js packages of a bench that nothing loads after the build (runs in the image build)",
	)
	prune_command.add_argument(
		"bench", type=Path, help="the bench directory, such as /home/frappe/frappe-bench"
	)
	return parser


def main(argv: Sequence[str] | None = None) -> int:
	"""Run one command and return its exit code."""
	try:
		args = _parser().parse_args(argv)
	except SystemExit as exit_request:
		# argparse exits with 2 on usage errors; the tools exit with 1 on every problem.
		return 0 if exit_request.code == 0 else 1
	try:
		return args.run(args)
	except (OSError, ValueError) as error:
		print(f"error: {error}", file=sys.stderr)
		return 1


if __name__ == "__main__":
	sys.exit(main())
