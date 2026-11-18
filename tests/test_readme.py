import re

import pytest

from germanized.apps import App
from germanized.readme import check, update

FRAPPE_TAG = "v16.60.2"
APPS = (
	App("https://github.com/frappe/erpnext", "v16.60.0"),
	App("https://github.com/alyf-de/erpnext_pdf-on-submit", "v16.3.1"),
	App("https://github.com/encircle360-oss/steuerbote", "v0.1.1"),
)
FRAPPE_ROW = "| [frappe](https://github.com/frappe/frappe) | v16.60.2 | Framework | MIT |"
ERPNEXT_ROW = "| [erpnext](https://github.com/frappe/erpnext) | v16.60.0 | ERP | GPL-3.0 |"
PDF_ROW = (
	"| [erpnext_pdf-on-submit](https://github.com/alyf-de/erpnext_pdf-on-submit) | v16.3.1 | PDF | GPL-3.0 |"
)
STEUERBOTE_ROW = (
	"| [steuerbote](https://github.com/encircle360-oss/steuerbote) | v0.1.1 | ELSTER | AGPL-3.0 |"
)


def readme(*rows: str, separator: str = "|---|---|---|---|") -> str:
	return "\n".join(
		[
			"# erpnext_germanized",
			"",
			"## Enthaltene Apps",
			"",
			"Die Versionen kommen aus `apps.json`.",
			"",
			"| App | Version | Zweck | Lizenz |",
			separator,
			*rows,
			"",
			"## Schnellstart",
			"",
		]
	)


VALID = readme(FRAPPE_ROW, ERPNEXT_ROW, PDF_ROW, STEUERBOTE_ROW)


def test_a_table_in_step_with_the_pins_has_no_problems():
	assert check(VALID, APPS, FRAPPE_TAG) == []


def test_one_dash_is_enough_for_a_separator_cell():
	assert (
		check(
			readme(FRAPPE_ROW, ERPNEXT_ROW, PDF_ROW, STEUERBOTE_ROW, separator="|-|-|-|-|"), APPS, FRAPPE_TAG
		)
		== []
	)


def test_the_table_may_be_aligned_and_padded():
	text = readme(
		"|  [frappe](https://github.com/frappe/frappe)  |  v16.60.2  | Framework |  MIT |",
		ERPNEXT_ROW,
		PDF_ROW,
		STEUERBOTE_ROW,
		separator="| :--- | :---: | --- | ---: |",
	)
	assert check(text, APPS, FRAPPE_TAG) == []


def test_an_escaped_pipe_stays_inside_its_cell():
	text = VALID.replace("| ERP |", "| ERP \\| CRM |")
	assert check(text, APPS, FRAPPE_TAG) == []


def test_the_readme_needs_the_section():
	assert check("# erpnext_germanized\n", APPS, FRAPPE_TAG) == [
		"README.md has no section '## Enthaltene Apps'"
	]


def test_the_section_appears_once():
	assert check(VALID + "\n## Enthaltene Apps\n", APPS, FRAPPE_TAG) == [
		"README.md has the section '## Enthaltene Apps' more than once"
	]


def test_the_table_belongs_to_the_section():
	text = "## Enthaltene Apps\n\nSiehe unten.\n\n## Andere Apps\n\n| App | Version | Zweck | Lizenz |\n"
	assert check(text, APPS, FRAPPE_TAG) == [
		"the section '## Enthaltene Apps' has no table with the columns App | Version | Zweck | Lizenz"
	]


def test_the_table_has_the_four_columns():
	text = VALID.replace("| App | Version | Zweck | Lizenz |", "| App | Version | Lizenz |")
	assert check(text, APPS, FRAPPE_TAG) == [
		"the section '## Enthaltene Apps' has no table with the columns App | Version | Zweck | Lizenz"
	]


def test_a_table_without_outer_pipes_does_not_count():
	text = VALID.replace("| App | Version | Zweck | Lizenz |", "App | Version | Zweck | Lizenz")
	assert check(text, APPS, FRAPPE_TAG)[0].startswith("the section '## Enthaltene Apps' has no table")


@pytest.mark.parametrize(
	"separator", ["| App | Version | Zweck | Lizenz |", "|---|---|---|", "| --- | --- | --- | -x- |", ""]
)
def test_the_header_is_followed_by_a_separator_line(separator):
	assert check(readme(FRAPPE_ROW, separator=separator), APPS, FRAPPE_TAG) == [
		"the app table needs a separator line like |---|---|---|---| under its header"
	]


def test_the_header_may_not_end_the_readme():
	assert check("## Enthaltene Apps\n\n| App | Version | Zweck | Lizenz |\n", APPS, FRAPPE_TAG) == [
		"the app table needs a separator line like |---|---|---|---| under its header"
	]


def test_a_subsection_or_a_code_block_does_not_end_the_section():
	text = VALID.replace(
		"Die Versionen kommen aus `apps.json`.\n",
		"### Versionen\n\n```bash\n# apps.json\n## nur ein Kommentar\n```\n",
	)
	assert check(text, APPS, FRAPPE_TAG) == []


def test_a_table_inside_a_code_block_does_not_count():
	text = "## Enthaltene Apps\n\n```\n| App | Version | Zweck | Lizenz |\n|---|---|---|---|\n```\n"
	assert check(text, APPS, FRAPPE_TAG) == [
		"the section '## Enthaltene Apps' has no table with the columns App | Version | Zweck | Lizenz"
	]


def test_every_version_is_the_pinned_tag():
	text = VALID.replace("| v16.60.0 |", "| v16.59.0 |").replace("| v16.60.2 |", "| `v16.60.2` |")
	assert check(text, APPS, FRAPPE_TAG) == [
		"README.md line 9: frappe has the version '`v16.60.2`', the Containerfile pins v16.60.2",
		"README.md line 10: erpnext has the version 'v16.59.0', apps.json pins v16.60.0",
	]


def test_every_app_has_a_row():
	assert check(readme(FRAPPE_ROW, ERPNEXT_ROW, STEUERBOTE_ROW), APPS, FRAPPE_TAG) == [
		"README.md has no row for erpnext_pdf-on-submit (https://github.com/alyf-de/erpnext_pdf-on-submit)"
	]


def test_frappe_has_a_row():
	assert check(readme(ERPNEXT_ROW, PDF_ROW, STEUERBOTE_ROW), APPS, FRAPPE_TAG) == [
		"README.md has no row for frappe (https://github.com/frappe/frappe)"
	]


def test_there_are_no_other_rows():
	banking = "| [banking](https://github.com/alyf-de/banking) | v16.6.4 | Bank | GPL-3.0 |"
	assert check(readme(FRAPPE_ROW, ERPNEXT_ROW, PDF_ROW, STEUERBOTE_ROW, banking), APPS, FRAPPE_TAG) == [
		"README.md line 13: https://github.com/alyf-de/banking is neither Frappe nor an app of apps.json"
	]


def test_every_app_has_one_row_only():
	assert check(readme(FRAPPE_ROW, ERPNEXT_ROW, ERPNEXT_ROW, PDF_ROW, STEUERBOTE_ROW), APPS, FRAPPE_TAG) == [
		"README.md line 11: a second row for erpnext"
	]


def test_the_app_cell_links_the_repository_under_its_name():
	text = VALID.replace(
		"[erpnext](https://github.com/frappe/erpnext)", "[ERPNext](https://github.com/frappe/erpnext)"
	)
	assert check(text, APPS, FRAPPE_TAG) == ["README.md line 10: the link text must be erpnext, not ERPNext"]


def test_the_app_cell_is_a_link():
	text = VALID.replace("[erpnext](https://github.com/frappe/erpnext)", "erpnext")
	assert check(text, APPS, FRAPPE_TAG) == [
		"README.md line 10: the App cell must be a link like "
		"[erpnext](https://github.com/frappe/erpnext), not 'erpnext'",
		"README.md has no row for erpnext (https://github.com/frappe/erpnext)",
	]


def test_every_row_has_four_cells():
	text = VALID.replace("| ERP | GPL-3.0 |", "| ERP |")
	assert check(text, APPS, FRAPPE_TAG) == [
		"README.md line 10: 3 cells instead of 4",
		"README.md has no row for erpnext (https://github.com/frappe/erpnext)",
	]


def test_the_rows_follow_frappe_and_the_order_of_apps_json():
	text = readme(FRAPPE_ROW, PDF_ROW, ERPNEXT_ROW, STEUERBOTE_ROW.replace("v0.1.1", "v0.1.0"))
	assert check(text, APPS, FRAPPE_TAG) == [
		"README.md line 12: steuerbote has the version 'v0.1.0', apps.json pins v0.1.1",
		"the rows of the app table must list frappe first and then the apps in the order of apps.json",
	]


def test_the_table_may_end_the_readme():
	text = "\n".join(
		["## Enthaltene Apps", "| App | Version | Zweck | Lizenz |", "|---|---|---|---|", FRAPPE_ROW]
	)
	assert check(text, (), FRAPPE_TAG) == []


def test_the_table_ends_at_the_first_line_that_is_no_table_row():
	text = readme(FRAPPE_ROW, ERPNEXT_ROW, PDF_ROW, STEUERBOTE_ROW).replace(
		STEUERBOTE_ROW + "\n",
		STEUERBOTE_ROW + "\nText.\n| [banking](https://github.com/alyf-de/banking) | x | y | z |\n",
	)
	assert check(text, APPS, FRAPPE_TAG) == []


NEW_APPS = (
	App("https://github.com/frappe/erpnext", "v16.61.0"),
	App("https://github.com/alyf-de/erpnext_pdf-on-submit", "v16.3.1"),
	App("https://github.com/encircle360-oss/steuerbote", "v0.2.0"),
)


def test_update_rewrites_the_version_cells_and_nothing_else():
	updated = update(VALID, NEW_APPS, "v16.61.1")
	assert updated == (
		VALID.replace(FRAPPE_ROW, FRAPPE_ROW.replace("v16.60.2", "v16.61.1"))
		.replace(ERPNEXT_ROW, ERPNEXT_ROW.replace("v16.60.0", "v16.61.0"))
		.replace(STEUERBOTE_ROW, STEUERBOTE_ROW.replace("v0.1.1", "v0.2.0"))
	)
	assert check(updated, NEW_APPS, "v16.61.1") == []


def test_update_keeps_the_padding_of_a_cell():
	text = readme("| [frappe](https://github.com/frappe/frappe) |  v16.60.2   | Framework | MIT |")
	assert "|  v16.61.1   |" in update(text, APPS, "v16.61.1")


def test_update_fills_an_empty_version_cell():
	text = readme("| [frappe](https://github.com/frappe/frappe) |   | Framework | MIT |")
	assert "| [frappe](https://github.com/frappe/frappe) | v16.60.2 | Framework | MIT |" in update(
		text, APPS, FRAPPE_TAG
	)


def test_update_leaves_rows_alone_that_it_cannot_place():
	rows = (
		"| [banking](https://github.com/alyf-de/banking) | v16.6.3 | Bank | GPL-3.0 |",
		"| erpnext | v16.59.0 | ERP | GPL-3.0 |",
		"| [erpnext](https://github.com/frappe/erpnext) | v16.59.0 |",
	)
	text = readme(*rows)
	assert update(text, APPS, FRAPPE_TAG) == text


def test_update_keeps_the_line_endings():
	text = VALID.replace("\n", "\r\n")
	updated = update(text, NEW_APPS, FRAPPE_TAG)
	assert updated == text.replace("| v16.60.0 |", "| v16.61.0 |").replace("| v0.1.1 |", "| v0.2.0 |")


def test_update_needs_the_table():
	with pytest.raises(ValueError, match=re.escape("README.md has no section '## Enthaltene Apps'")):
		update("# erpnext_germanized\n", APPS, FRAPPE_TAG)
