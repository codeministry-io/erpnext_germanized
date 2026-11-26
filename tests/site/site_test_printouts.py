"""Printouts of the image as its users get them, for tests/site/run.sh:

	cd sites && ../env/bin/python -m site_test_printouts <site> <url>

with this directory on PYTHONPATH, run in a container of the image on the network of the site test, after the seeds
of the bundled apps have written their documents: `steuerbote.tests.e2e.seed.run` and
`briefbote.tests.print_documents.run` with its siblings for sales, dunning, payment and purchase. `<url>` is the site as its users reach it, such as http://test.localhost.

- **Download.** One document of ERPNext's own print format of the Sales Invoice, one of each print format of Briefbote
  and one of each print format of Steuerbote are downloaded through nginx as a logged-in user, with wkhtmltopdf and
  with Chromium, the way the print view of the desk downloads them (`frappe.utils.print_format.download_pdf`, which
  runs the hooks of the apps, such as the e-invoice of eu_einvoice). Each answer must be a PDF. Briefbote and
  Steuerbote print the same pages with both generators, so a document of theirs must have as many pages with
  Chromium as with wkhtmltopdf.
- **Briefbote.** Each print format of Briefbote prints the first German document of Briefbote's proof directly with
  both generators, the way its proof does. Each PDF must hold the name of its document and set its text only in
  fonts that are embedded in the PDF: Inter wherever the settings of the company ask for the embedded font.
- **Draft mark.** Where Briefbote's proof has a draft, its invoice prints as a draft with both generators and goes
  through the conversion to PDF/A-3 with Ghostscript that eu_einvoice applies to every PDF of a Sales Invoice it
  embeds its XML in. The converted PDF must still say "ENTWURF" and paint the mark across the page, on every page
  with Chromium and on the first with wkhtmltopdf, measured with the band, grey and share of Briefbote's proof on the
  page rendered by Ghostscript.
- **Closing texts.** The invoices of Briefbote's proof whose end falls near the end of a page (from v0.2.1 on) print
  directly with both generators under the settings of their case on as many pages each.
- **Glyph advances.** In the PDFs of Chromium, the distance from each digit to the next digit must equal the advance
  width that the font gives the first digit at the printed size, as the PDF records it, within ADVANCE_TOLERANCE.
  Digits have no kerning, so any larger difference means the glyphs were moved, for example to whole pixels by font
  hinting, which spaces the letters of a printout unevenly.

Every check runs, and the test fails at the end when one of them failed.
"""

import http.cookiejar
import importlib
import io
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from collections.abc import Iterator
from dataclasses import dataclass

import frappe
from frappe.translate import print_language
from pypdf import PdfReader
from pypdf.generic import ArrayObject, DictionaryObject

ENGINES = ("wkhtmltopdf", "chrome")
# The modules of Briefbote's proof with the cases of its print formats: invoices, then sales, dunning, payment and
# purchase, which Briefbote has from v0.2.0 on.
BRIEFBOTE_PROOFS = (
	"print_proof",
	"print_proof_sales",
	"print_proof_dunning",
	"print_proof_payment",
	"print_proof_purchase",
)
# The apps whose print formats promise the same pages with both generators.
SAME_PAGES = frozenset({"briefbote", "steuerbote"})
EMBEDDED_FONT = "Inter"
FONT_FILES = ("/FontFile", "/FontFile2", "/FontFile3")
# Unhinted layout leaves rounding noise of about 0.05 %; hinting to whole pixels moves glyphs by several per cent.
ADVANCE_TOLERANCE = 0.005
# Chromium writes every glyph as `<dx> 0 Td <glyph> Tj`, after `/<font> <size> Tf`.
_TEXT = re.compile(
	rb"/(?P<font>[^\s/]+)\s+(?P<size>[\d.]+)\s+Tf|(?P<dx>-?[\d.]+)\s+-?[\d.]+\s+Td|<(?P<glyph>[0-9A-Fa-f]+)>\s*Tj"
)
_CHARS = re.compile(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>")
_RANGES = re.compile(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>")


@dataclass(frozen=True)
class Sample:
	"""A document to print: the app whose print format it is, the document and the print format."""

	app: str
	doctype: str
	name: str
	print_format: str


def main(site: str, url: str) -> None:
	"""Run every check on a site; exit with 1 after all of them when one failed."""
	frappe.init(site=site, sites_path=".")
	try:
		frappe.connect()
		lines, failures = run(site, url)
	finally:
		frappe.destroy()
	sys.stdout.write("\n".join(lines) + "\n")
	if failures:
		sys.stdout.write("\nfailed:\n" + "\n".join(f"- {failure}" for failure in failures) + "\n")
		raise SystemExit(1)


def run(site: str, url: str) -> tuple[list[str], list[str]]:
	lines: list[str] = []
	failures: list[str] = []
	opener = login(site, url)
	for sample in samples():
		pages: dict[str, int] = {}
		for engine in ENGINES:
			label = f"download {sample.app}: {sample.print_format}, {sample.name}, {engine}"
			try:
				pdf = download(opener, site, url, sample, engine)
				if not pdf.startswith(b"%PDF-"):
					raise AssertionError(f"no PDF but {pdf[:80]!r}")
				pages[engine] = len(PdfReader(io.BytesIO(pdf)).pages)
				lines.append(f"{label}: {pages[engine]} pages")
			except Exception as error:
				failures.append(f"{label}: {error}")
		if sample.app in SAME_PAGES and len(pages) == len(ENGINES) and len(set(pages.values())) > 1:
			counts = ", ".join(f"{engine} {count}" for engine, count in pages.items())
			failures.append(
				f"download {sample.app}: {sample.print_format}, {sample.name}: different page counts ({counts})"
			)
	if "briefbote" in frappe.get_installed_apps():
		for label, check in briefbote_checks():
			try:
				lines.append(f"{label}: {check()}")
			except Exception as error:
				failures.append(f"{label}: {error}")
	return lines, failures


def samples() -> list[Sample]:
	"""The documents to download: ERPNext's Sales Invoice in its default format and each format of the bundled apps."""
	installed = frappe.get_installed_apps()
	found = []
	invoice = frappe.get_all(
		"Sales Invoice", filters={"docstatus": 1}, order_by="creation", limit=1, pluck="name"
	) or frappe.get_all("Sales Invoice", order_by="creation", limit=1, pluck="name")
	if not invoice:
		raise AssertionError("the site has no Sales Invoice to print")
	# The default of the DocType itself: Briefbote's seed makes its Rechnung the default through a Property Setter.
	standard = frappe.db.get_value("DocType", "Sales Invoice", "default_print_format") or "Standard"
	found.append(Sample("erpnext", "Sales Invoice", invoice[0], standard))
	if "briefbote" in installed:
		found += [
			Sample("briefbote", case.doctype, case.name, case.print_format) for case in briefbote_cases()
		]
	if "steuerbote" in installed:
		from steuerbote.tests.print_proof import FORMATS, sample

		found += [
			Sample("steuerbote", doctype, sample(doctype), name) for doctype, (name, _) in FORMATS.items()
		]
	return found


def login(site: str, url: str) -> urllib.request.OpenerDirector:
	"""An opener with the session of Administrator, whose password the bench service of the test has."""
	opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
	body = urllib.parse.urlencode({"usr": "Administrator", "pwd": os.environ["ADMIN_PASSWORD"]}).encode()
	request = urllib.request.Request(f"{url}/api/method/login", data=body, headers={"Host": site})  # noqa: S310 - the site under test
	with opener.open(request, timeout=60):
		pass
	return opener


def download(
	opener: urllib.request.OpenerDirector, site: str, url: str, sample: Sample, engine: str
) -> bytes:
	query = urllib.parse.urlencode(
		{
			"doctype": sample.doctype,
			"name": sample.name,
			"format": sample.print_format,
			"no_letterhead": 0,
			"pdf_generator": engine,
		}
	)
	request = urllib.request.Request(  # noqa: S310
		f"{url}/api/method/frappe.utils.print_format.download_pdf?{query}", headers={"Host": site}
	)
	try:
		with opener.open(request, timeout=300) as response:
			return response.read()
	except urllib.error.HTTPError as error:
		raise AssertionError(f"HTTP {error.code}: {error.read()[-300:]!r}") from None


def briefbote_cases() -> list:
	"""The first German document of Briefbote's proof for each of its print formats."""
	formats = frappe.get_all("Print Format", filters={"module": "Briefbote", "disabled": 0}, pluck="name")
	if not formats:
		raise AssertionError("the site has no print format of the module Briefbote")
	cases = []
	for print_format in sorted(formats):
		case = next(
			(
				case
				for case in briefbote_proof_cases()
				if case.print_format == print_format and case.language == "de" and plain(case)
			),
			None,
		)
		if case is None:
			raise AssertionError(
				f"the proof of Briefbote has no German document for the print format {print_format}"
			)
		cases.append(case)
	return cases


def briefbote_checks() -> Iterator[tuple[str, object]]:
	"""Each format of Briefbote printed directly with both generators, and, with Chromium, a printout in the font of
	the system as well, for the glyph advances."""
	from briefbote.briefbote import printing
	from briefbote.layout import theme
	from briefbote.tests.print_proof import render

	system_font = next(
		(
			case
			for case in briefbote_proof_cases()
			if case.language == "de" and plain(case) and not theme.embeds(company_font(case, printing))
		),
		None,
	)
	for case in [*briefbote_cases(), *([system_font] if system_font else [])]:
		for engine in ENGINES:

			def check(case=case, engine=engine) -> str:
				doc = frappe.get_doc(case.doctype, case.name)
				inter = theme.embeds(printing.settings(doc.company).get("font"))
				with print_language(case.language):
					pdf = render(doc, case.print_format, engine, own_paper=True)
				line = fonts_and_name(pdf, doc.name, inter)
				if engine == "chrome":
					line += ", " + advances(pdf)
				return line

			yield f"briefbote: {case.print_format}, {case.name}, {engine}", check
	for case in closing_cases():
		yield (
			f"briefbote: {case.print_format}, {case.name}, end near the end of a page, both generators",
			lambda case=case: same_pages_directly(case, render),
		)
	draft = next(
		(
			case
			for case in briefbote_proof_cases()
			if getattr(case, "docstatus", None) == 0 and case.language == "de"
		),
		None,
	)
	if draft:
		for engine in ENGINES:
			yield (
				f"briefbote: {draft.print_format}, {draft.name} as draft, {engine}, PDF/A",
				lambda engine=engine: draft_mark(draft, engine, render),
			)


def briefbote_proof_cases() -> list:
	"""The cases of every module of Briefbote's proof that the installed version has, in their order."""
	cases = []
	for module in BRIEFBOTE_PROOFS:
		try:
			cases += importlib.import_module(f"briefbote.tests.{module}").CASES
		except ModuleNotFoundError:
			continue
	return cases


def closing_cases() -> list:
	"""The invoices of Briefbote's proof whose end falls near the end of a page, from v0.2.1 on: the closing texts
	stay with the totals, and both generators break alike."""
	from briefbote.tests import print_documents as documents

	if not hasattr(documents, "CLOSING_FAMILY"):
		return []
	names = {documents.closing_name(count) for count in documents.CLOSING_FAMILY}
	return [
		case
		for case in briefbote_proof_cases()
		if case.name in names and case.language == "de" and getattr(case, "docstatus", None) is None
	]


def same_pages_directly(case, render) -> str:
	"""A case printed directly with both generators, under the settings of the case, on as many pages each."""
	from briefbote.tests.print_proof import settings_of

	doc = frappe.get_doc(case.doctype, case.name)
	pages = {}
	with print_language(case.language), settings_of(doc.company, getattr(case, "settings", None) or {}):
		for engine in ENGINES:
			pdf = render(doc, case.print_format, engine, own_paper=True)
			if not pdf.startswith(b"%PDF-"):
				raise AssertionError(f"{engine} gave no PDF")
			pages[engine] = len(PdfReader(io.BytesIO(pdf)).pages)
	counts = ", ".join(f"{engine} {count}" for engine, count in pages.items())
	if len(set(pages.values())) > 1:
		raise AssertionError(f"different page counts ({counts})")
	return f"pages {counts}"


def plain(case) -> bool:
	"""A case of Briefbote's proof that prints its document as stored, under the stored settings."""
	return (
		getattr(case, "docstatus", None) is None
		and not getattr(case, "settings", None)
		and not getattr(case, "variant", "")
		and not getattr(case, "incomplete", False)
	)


def draft_mark(case, engine: str, render) -> str:
	"""The mark of a draft survives the image's conversion to PDF/A-3 and is painted across its pages."""
	from briefbote.proof import raster
	from briefbote.tests.print_proof import MARK_BAND, MARK_GREY, MARK_SHARE
	from eu_einvoice.european_e_invoice.einvoice import _convert_pdf_to_pdfa
	from frappe.model.docstatus import DocStatus

	frappe.db.set_single_value("Print Settings", "allow_print_for_draft", 1)
	doc = frappe.get_doc(case.doctype, case.name)
	doc.docstatus = DocStatus(0)
	with print_language(case.language):
		pdf = _convert_pdf_to_pdfa(render(doc, case.print_format, engine, own_paper=True))
	reader = PdfReader(io.BytesIO(pdf))
	if b"pdfaid:part" not in pdf:
		raise AssertionError("the conversion gave no PDF/A")
	marked = range(len(reader.pages)) if engine == "chrome" else range(1)
	problems = []
	for index in marked:
		if "ENTWURF" not in reader.pages[index].extract_text():
			problems.append(f"page {index + 1} lacks the word ENTWURF")
		image = raster.read_pgm(page_image(pdf, index + 1), 50)
		share = raster.share(image, MARK_BAND, *MARK_GREY)
		if share < MARK_SHARE:
			problems.append(f"page {index + 1}: the mark across the page is not painted ({share:.1%} grey)")
	if problems:
		raise AssertionError("; ".join(problems))
	return f"{len(reader.pages)} pages as PDF/A, the mark on {len(marked)} of them"


def page_image(pdf: bytes, number: int) -> bytes:
	"""One page of a PDF as a greyscale PGM at 50 dpi, rendered by the Ghostscript of the image."""
	gs = shutil.which("gs") or "gs"
	return subprocess.run(  # noqa: S603 - the Ghostscript of the image on a PDF this test printed
		[
			gs,
			"-q",
			"-sstdout=%stderr",
			"-dBATCH",
			"-dNOPAUSE",
			"-dSAFER",
			"-sDEVICE=pgmraw",
			"-r50",
			"-dTextAlphaBits=4",
			"-dGraphicsAlphaBits=4",
			f"-dFirstPage={number}",
			f"-dLastPage={number}",
			"-sOutputFile=-",
			"-",
		],
		input=pdf,
		capture_output=True,
		check=True,
		timeout=120,
	).stdout


def company_font(case, printing) -> str | None:
	return printing.settings(frappe.db.get_value(case.doctype, case.name, "company")).get("font")


def fonts_and_name(pdf: bytes, name: str, inter: bool) -> str:
	"""Pages and fonts of a printout; raises when it lacks its document or a font is missing or foreign."""
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
	whether the PDF embeds it; a Type 3 font carries its glyphs in the PDF itself."""
	resources = resources.get_object() if resources is not None else None
	if not isinstance(resources, DictionaryObject) or depth > 8:
		return
	for font in (resources.get("/Font") or DictionaryObject()).get_object().values():
		font = font.get_object()
		if font.get("/Subtype") == "/Type3":
			descriptor = font.get("/FontDescriptor")
			family = descriptor.get_object().get("/FontFamily") if descriptor is not None else None
			fonts[f"{family or 'Type3'} (Type 3)"] = True
			continue
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


def advances(pdf: bytes) -> str:
	"""The largest relative difference between the distance from a digit to the next and the advance width of the
	first digit at its size; raises above ADVANCE_TOLERANCE or when the printout has no digits to measure."""
	worst, pairs = 0.0, 0
	for page in PdfReader(io.BytesIO(pdf)).pages:
		fonts = {
			name.lstrip("/"): font_metrics(ref.get_object())
			for name, ref in page["/Resources"]["/Font"].items()
			if "/ToUnicode" in ref.get_object()
		}
		font = size = previous = None
		for match in _TEXT.finditer(page.get_contents().get_data()):
			if match["font"]:
				font, size, previous = match["font"].decode(), float(match["size"]), None
			elif match["dx"] is not None:
				previous = (*previous[:2], float(match["dx"])) if previous else None
			elif font in fonts:
				widths, characters = fonts[font]
				glyph = int(match["glyph"], 16)
				if (
					previous
					and len(previous) == 3
					and previous[1] in widths
					and characters.get(previous[1], "").isdigit()
					and characters.get(glyph, "").isdigit()
				):
					expected = widths[previous[1]] * size / 1000
					worst = max(worst, abs(previous[2] - expected) / expected)
					pairs += 1
				previous = (font, glyph)
			else:
				previous = None
	if not pairs:
		raise AssertionError("the printout of Chromium has no digits to measure the glyph advances")
	if worst > ADVANCE_TOLERANCE:
		raise AssertionError(
			f"glyph advances differ from the widths of the font by up to {worst:.2%} "
			f"(tolerance {ADVANCE_TOLERANCE:.1%}, {pairs} pairs of digits)"
		)
	return f"glyph advances within {worst:.3%} of the font widths ({pairs} pairs of digits)"


def font_metrics(font: DictionaryObject) -> tuple[dict[int, float], dict[int, str]]:
	"""The advance widths of a font in thousandths of its size and the characters of its glyphs, by glyph code."""
	widths: dict[int, float] = {}
	if font.get("/Subtype") == "/Type0":
		w = font["/DescendantFonts"].get_object()[0].get_object().get("/W", ArrayObject())
		index = 0
		while index < len(w):
			first = int(w[index])
			if isinstance(w[index + 1].get_object(), ArrayObject):
				widths |= {first + k: float(v) for k, v in enumerate(w[index + 1].get_object())}
				index += 2
			else:
				widths |= dict.fromkeys(range(first, int(w[index + 1]) + 1), float(w[index + 2]))
				index += 3
	elif "/Widths" in font:
		scale = float(font["/FontMatrix"][0]) * 1000 if "/FontMatrix" in font else 1.0
		first = int(font.get("/FirstChar", 0))
		widths = {first + k: float(v) * scale for k, v in enumerate(font["/Widths"].get_object())}
	cmap = font["/ToUnicode"].get_object().get_data().decode("latin-1")
	characters: dict[int, str] = {}
	for block in re.findall(r"beginbfchar(.*?)endbfchar", cmap, re.S):
		characters |= {int(code, 16): chr(int(text[:4], 16)) for code, text in _CHARS.findall(block)}
	for block in re.findall(r"beginbfrange(.*?)endbfrange", cmap, re.S):
		for first, last, text in _RANGES.findall(block):
			start = int(text[:4], 16)
			characters |= {
				code: chr(start + code - int(first, 16)) for code in range(int(first, 16), int(last, 16) + 1)
			}
	return widths, characters


if __name__ == "__main__":
	main(sys.argv[1], sys.argv[2])
