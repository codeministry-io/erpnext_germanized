"""The pins of the Containerfile: the defaults of its ARG instructions and the image of its first FROM."""

import re
from pathlib import Path

CONTAINERFILE = Path("Containerfile")
# The build arguments whose defaults decide what goes into the image.
PIN_ARGS = (
	"FRAPPE_BRANCH",
	"FRAPPE_PATH",
	"PYTHON_VERSION",
	"DEBIAN_BASE",
	"NODE_VERSION",
	"WKHTMLTOPDF_VERSION",
	"WKHTMLTOPDF_DISTRO",
	"INSTALL_CHROMIUM",
)


def _default(text: str, name: str) -> re.Match[str]:
	# Instructions are case-insensitive, build argument names are not.
	pattern = re.compile(
		rf"^[ \t]*(?i:ARG)[ \t]+{re.escape(name)}=(?P<quote>[\"']?)(?P<value>[^\s\"']*)(?P=quote)[ \t]*$",
		re.MULTILINE,
	)
	matches = list(pattern.finditer(text))
	if not matches:
		raise ValueError(f"the Containerfile has no default for ARG {name}")
	if len(matches) > 1:
		raise ValueError(f"the Containerfile sets a default for ARG {name} more than once")
	return matches[0]


def arg_default(text: str, name: str) -> str:
	"""The default of `ARG <name>=<value>`, which the Containerfile must set exactly once."""
	return _default(text, name)["value"]


def set_arg_default(text: str, name: str, value: str) -> str:
	"""The Containerfile text with the default of one ARG replaced and everything else unchanged."""
	match = _default(text, name)
	return text[: match.start("value")] + value + text[match.end("value") :]


def frappe_tag(path: Path = CONTAINERFILE) -> str:
	"""The Frappe release the image is built from: the default of ARG FRAPPE_BRANCH."""
	return arg_default(path.read_text(encoding="utf-8"), "FRAPPE_BRANCH")


def base_image(text: str) -> str:
	"""The image of the first FROM, without its flags and stage name."""
	for line in text.splitlines():
		words = line.split()
		if words and words[0].upper() == "FROM":
			images = [word for word in words[1:] if not word.startswith("--")]
			if not images:
				raise ValueError("the first FROM names no image")
			return images[0]
	raise ValueError("the Containerfile has no FROM")


def pins(text: str) -> dict[str, str]:
	"""The defaults of the build arguments in PIN_ARGS, in that order."""
	return {name: arg_default(text, name) for name in PIN_ARGS}
