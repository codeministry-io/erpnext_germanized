"""The print formats of Briefbote with the PDF generators of the image, for tests/site/run.sh:

	cd sites && ../env/bin/python -m site_test_briefbote <site>

with this directory on PYTHONPATH, after `bench --site <site> execute briefbote.tests.print_documents.run` has written
the documents of Briefbote's own proof of its printouts. Every print format of the module Briefbote prints the first
German document of that proof with wkhtmltopdf and with Chromium, on blank paper, the way the proof does it. Each PDF
must hold the name of its document and set its text only in fonts that are embedded in the PDF: Inter wherever the
settings of the company ask for the embedded font, so that a printout looks the same on every server.
"""

import io
import sys

import frappe
from briefbote.briefbote import printing
from briefbote.layout import theme
from briefbote.tests.print_proof import CASES, render
from frappe.translate import print_language
from pypdf import PdfReader
from pypdf.generic import DictionaryObject

ENGINES = ("wkhtmltopdf", "chrome")
EMBEDDED_FONT = "Inter"
FONT_FILES = ("/FontFile", "/FontFile2", "/FontFile3")


def main(site: str) -> None:
	"""Print the formats on a site and write one line per printout. bench execute refuses a module of no installed
	app, so the test connects to the site itself, from the sites directory as bench does."""
	frappe.init(site=site, sites_path=".")
	try:
		frappe.connect()
		lines = print_formats()
	finally:
		frappe.destroy()
	sys.stdout.write("\n".join(lines) + "\n")


def print_formats() -> list[str]:
	"""One line per print format and generator; raises on the first printout that fails."""
	formats = frappe.get_all("Print Format", filters={"module": "Briefbote", "disabled": 0}, pluck="name")
	if not formats:
		raise AssertionError("the site has no print format of the module Briefbote")
	lines = []
	for print_format in sorted(formats):
		case = next(
			(case for case in CASES if case.print_format == print_format and case.language == "de"), None
		)
		if case is None:
			raise AssertionError(
				f"the proof of Briefbote has no German document for the print format {print_format}"
			)
		doc = frappe.get_doc(case.doctype, case.name)
		inter = theme.embeds(printing.settings(doc.company).get("font"))
		for engine in ENGINES:
			with print_language(case.language):
				pdf = render(doc, print_format, engine, own_paper=True)
			lines.append(f"{print_format}, {doc.name}, {engine}: {check(pdf, doc.name, inter)}")
	return lines


def check(pdf: bytes, name: str, inter: bool) -> str:
	"""What a printout holds, as one line; raises when it lacks its document or a font is missing or foreign."""
	if not pdf.startswith(b"%PDF-"):
		raise AssertionError(f"the printout of {name} is no PDF")
	reader = PdfReader(io.BytesIO(pdf))
	text = " ".join(page.extract_text() for page in reader.pages)
	if name not in text:
		raise AssertionError(f"the printout of {name} does not name its document")
	fonts: dict[str, bool] = {}
	for page in reader.pages:
		collect_fonts(page.get("/Resources"), fonts)
	if not fonts:
		raise AssertionError(f"the printout of {name} has no font")
	if missing := sorted(font for font, embedded in fonts.items() if not embedded):
		raise AssertionError(f"the printout of {name} does not embed the fonts {', '.join(missing)}")
	if inter and (foreign := sorted(font for font in fonts if not font.startswith(EMBEDDED_FONT))):
		raise AssertionError(
			f"the printout of {name} sets text in {', '.join(foreign)} instead of {EMBEDDED_FONT}"
		)
	return f"{len(reader.pages)} pages, fonts {', '.join(sorted(fonts))}"


def collect_fonts(resources, fonts: dict[str, bool], depth: int = 0) -> None:
	"""The fonts of a resource dictionary and of the forms it draws, by name without the subset prefix, each with
	whether the PDF embeds it."""
	resources = resources.get_object() if resources is not None else None
	if not isinstance(resources, DictionaryObject) or depth > 8:
		return
	for font in (resources.get("/Font") or DictionaryObject()).get_object().values():
		font = font.get_object()
		name = str(font.get("/BaseFont", font.get("/Subtype", "unnamed"))).lstrip("/").split("+")[-1]
		descriptor = font.get("/FontDescriptor")
		if font.get("/Subtype") == "/Type0":
			descriptor = font["/DescendantFonts"].get_object()[0].get_object().get("/FontDescriptor")
		descriptor = descriptor.get_object() if descriptor is not None else DictionaryObject()
		fonts[name] = fonts.get(name, True) and any(key in descriptor for key in FONT_FILES)
	for xobject in (resources.get("/XObject") or DictionaryObject()).get_object().values():
		xobject = xobject.get_object()
		if xobject.get("/Subtype") == "/Form":
			collect_fonts(xobject.get("/Resources"), fonts, depth + 1)


if __name__ == "__main__":
	main(sys.argv[1])
