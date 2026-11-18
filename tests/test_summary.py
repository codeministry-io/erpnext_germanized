from germanized.apps import App
from germanized.summary import markdown

PINS = {
	"FRAPPE_BRANCH": "v16.60.2",
	"FRAPPE_PATH": "https://github.com/frappe/frappe",
	"PYTHON_VERSION": "3.14",
	"DEBIAN_BASE": "trixie",
	"NODE_VERSION": "24",
	"WKHTMLTOPDF_VERSION": "0.12.6.1-3",
	"WKHTMLTOPDF_DISTRO": "bookworm",
	"INSTALL_CHROMIUM": "true",
}
APPS = (
	App("https://github.com/frappe/erpnext", "v16.60.0"),
	App("https://github.com/encircle360-oss/steuerbote", "v0.1.1"),
)
TAGS = (
	"ghcr.io/encircle360-oss/erpnext_germanized:main",
	"ghcr.io/encircle360-oss/erpnext_germanized:main-0123456",
)


def test_the_summary_lists_the_apps_the_build_arguments_and_the_tags():
	assert markdown(APPS, PINS, TAGS) == (
		"### Apps\n"
		"\n"
		"| App | Version |\n"
		"| --- | --- |\n"
		"| [frappe](https://github.com/frappe/frappe) | `v16.60.2` |\n"
		"| [erpnext](https://github.com/frappe/erpnext) | `v16.60.0` |\n"
		"| [steuerbote](https://github.com/encircle360-oss/steuerbote) | `v0.1.1` |\n"
		"\n"
		"### Build arguments\n"
		"\n"
		"| Argument | Value |\n"
		"| --- | --- |\n"
		"| `FRAPPE_BRANCH` | `v16.60.2` |\n"
		"| `FRAPPE_PATH` | `https://github.com/frappe/frappe` |\n"
		"| `PYTHON_VERSION` | `3.14` |\n"
		"| `DEBIAN_BASE` | `trixie` |\n"
		"| `NODE_VERSION` | `24` |\n"
		"| `WKHTMLTOPDF_VERSION` | `0.12.6.1-3` |\n"
		"| `WKHTMLTOPDF_DISTRO` | `bookworm` |\n"
		"| `INSTALL_CHROMIUM` | `true` |\n"
		"\n"
		"### Image tags\n"
		"\n"
		"- `ghcr.io/encircle360-oss/erpnext_germanized:main`\n"
		"- `ghcr.io/encircle360-oss/erpnext_germanized:main-0123456`\n"
	)


def test_frappe_is_linked_to_the_repository_the_image_is_built_from():
	pins = PINS | {"FRAPPE_PATH": "https://github.com/example/frappe"}
	assert "| [frappe](https://github.com/example/frappe) | `v16.60.2` |\n" in markdown(APPS, pins, TAGS)


def test_a_build_without_tags_is_not_pushed():
	assert markdown(APPS, PINS, ()).endswith("### Image tags\n\nNone: this build is not pushed.\n")
