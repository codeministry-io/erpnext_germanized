# Apps

Diese Seite beschreibt jede App im Image: wozu sie da ist, woher sie kommt, unter welcher Lizenz sie steht, was sie für Deutschland mitbringt und wo sie eingerichtet wird. Grundlage sind README und Dokumentation der Projekte zum gepinnten Tag. Welche Version im Image steckt, steht in `apps.json` und in der Tabelle im [README](../README.md#enthaltene-apps). Weicht diese Seite von der Dokumentation eines Projekts ab, gilt die des Projekts.

Die Namen der Oberfläche stehen hier so, wie die deutsche Übersetzung sie zeigt, dahinter in Klammern der englische Name des DocTypes, wo das hilft.

## Frappe

- **Repository:** [frappe/frappe](https://github.com/frappe/frappe), Lizenz MIT
- **Dokumentation:** [docs.frappe.io/framework](https://docs.frappe.io/framework)

Frappe ist das Framework unter allen Apps: Python und MariaDB auf dem Server, eine eng verbundene Oberfläche im Browser. Es bringt die Oberfläche Desk, Rollen und Berechtigungen, eine REST-API für alle DocTypes, Berichte, Druckformate, E-Mail, Hintergrundjobs und den Scheduler mit. ERPNext ist die erste Anwendung, für die Frappe gebaut wurde.

Für Deutschland:

- **Übersetzung.** `frappe/locale/de.po`, gepflegt von der Community über Crowdin. Die Sprache gilt für die Site und lässt sich je Benutzer ändern.
- **Formate.** Mit dem Land Deutschland im Einrichtungsassistenten stellt Frappe Datum `dd.mm.yyyy`, Uhrzeit `HH:mm`, Zahlen `#.###,##`, Währung EUR und Zeitzone Europe/Berlin ein.

Einrichtung:

- **Systemeinstellungen** (System Settings): Sprache, Land, Zeitzone, Datums- und Zahlenformat und Währung. „Erster Wochentag“ steht auch nach dem Assistenten auf Sonntag. Als „Rundungsmethode“ steht vor dem Assistenten „Symmetrisches Runden (alt)“, der Assistent setzt „Symmetrisches Runden“, zur Wahl steht außerdem „Kaufmännisches Runden“. Welche Rundung zur Buchhaltung passt, klärt die Firma mit ihrer Steuerberatung.
- **Druckeinstellungen** (Print Settings): Vorgabe für den PDF-Generator, siehe [Architektur](architektur.md#was-im-image-steckt).

## ERPNext

- **Repository:** [frappe/erpnext](https://github.com/frappe/erpnext), Lizenz GPL-3.0
- **Dokumentation:** [docs.frappe.io/erpnext](https://docs.frappe.io/erpnext/)

ERPNext ist das ERP-System: Buchhaltung von der Buchung bis zu den Berichten, Auftragsabwicklung mit Verkauf, Einkauf und Lager, Fertigung, Anlagenverwaltung und Projekte mit Aufgaben und Zeiterfassung. ERPNext ist eine Marke der Frappe Technologies Pvt. Ltd., siehe deren [Logo and Trademark Policy](https://github.com/frappe/erpnext/blob/v16.60.0/TRADEMARK_POLICY.md).

Für Deutschland:

- **Kontenrahmen.** Für das Land Deutschland bietet der Einrichtungsassistent die Vorlagen „SKR03 mit Kontonummern“ und „SKR04 mit Kontonummern“ an (`erpnext/accounts/doctype/account/chart_of_accounts/verified/`), dazu die allgemeinen Vorlagen „Standard“ und „Standard with Numbers“.
- **Steuervorlagen.** Legt man eine Firma mit dem Land Deutschland an, erzeugt ERPNext aus `erpnext/setup/setup_wizard/data/country_wise_tax.json` passende Vorlagen: für den Verkauf etwa Inland, Lieferungen und sonstige Leistungen in die EU und in Drittländer, Bauleistungen nach § 13b UStG und den Nullsteuersatz nach § 12 Abs. 3 UStG, für den Einkauf Inland, EU, Drittland und § 13b UStG, dazu Artikelsteuervorlagen für 19 %, 7 % und 0 %.
- **Übersetzung.** `erpnext/locale/de.po`, ebenfalls über Crowdin.

Vorlagen sind ein Anfang, keine geprüfte Einrichtung. Kontenrahmen und Steuervorlagen gehören vor der ersten Buchung zur Steuerberatung.

Einrichtung: Firma, Kontenplan und Geschäftsjahr legt der Einrichtungsassistent an, alles Weitere regeln die Buchhaltungseinstellungen (Accounts Settings) und das Unternehmen (Company).

## HRMS

- **Repository:** [frappe/hrms](https://github.com/frappe/hrms) (Frappe HR), Lizenz GPL-3.0
- **Dokumentation:** [docs.frappe.io/hr](https://docs.frappe.io/hr/introduction)

HRMS ist die Personalverwaltung: Mitarbeiter von der Einstellung über Beförderungen und Versetzungen bis zum Austrittsgespräch, Urlaub und Anwesenheit, Spesen und Vorschüsse, Leistungsbeurteilung, Gehaltsstrukturen und Gehaltsabrechnung, dazu eine mobile App. Bis Version 13 gehörten diese Module zu ERPNext.

Für Deutschland bringt HRMS keinen eigenen Teil mit; `hrms/regional` enthält nur Indien und die Vereinigten Arabischen Emirate. Deutsche Felder am Mitarbeiter, die Liste der Krankenkassen und die Dienstreisen kommen aus [erpnext_germany](#erpnext_germany). Weil einige Funktionen von erpnext_germany HRMS voraussetzen, steht HRMS in `apps.json` davor.

## erpnext_germany

- **Repository:** [alyf-de/erpnext_germany](https://github.com/alyf-de/erpnext_germany) von der ALYF GmbH, Lizenz GPL-3.0
- **Name in bench:** `erpnext_germany`

Die App sammelt regionale Anpassungen für Deutschland:

- **Berichte** „Summen- und Saldenliste“ und „Zusammenfassende Meldung“. Die Zusammenfassende Meldung führt derzeit jede Rechnung als sonstige Leistung (S). Dreiecksgeschäfte (D) und innergemeinschaftliche Lieferungen (L) sind in der CSV-Datei von Hand zu ändern.
- **Registerinformation** mit Registerart, Registergericht und Registernummer an Unternehmen, Kunde und Lieferant.
- **Prüfung der USt-IdNr.** über den Dienst VIES der Europäischen Kommission, von Hand oder automatisch: Der Scheduler prüft nach und nach jeden aktiven Kunden und Lieferanten mit USt-IdNr., dessen letzte Prüfung (USt-IdNr Prüfung, VAT ID Check) mehr als drei Monate zurückliegt. Jede Prüfung läuft als Hintergrundjob in der Queue `long`; der Worker dafür braucht Zugang zu `ec.europa.eu`.
- **Lückenlose Nummern.** Von Angeboten, Aufträgen und Ausgangsrechnungen lässt sich je Nummernkreis und Firma nur der jeweils letzte Beleg löschen. Den Schalter dazu enthalten die ERPNext-Deutschland-Einstellungen (ERPNext Germany Settings), vorgegeben ist er an.
- **Geschützte Anhänge.** An Angeboten, Aufträgen, Lieferscheinen, Rechnungen, Zahlungen, Buchungssätzen, Anlagen und weiteren Belegen lassen sich Anhänge nur löschen, solange der Beleg ein Entwurf oder storniert ist.
- **Mitarbeiter:** zusätzliche Felder, etwa für Steuerangaben, eine Liste der Konfessionen und, mit HRMS, eine Liste der deutschen Krankenkassen.
- **Geschäftsbriefe** (Business Letter) aus einer Geschäftsbriefvorlage, zum Drucken oder als E-Mail an Kunden und Lieferanten.
- **Dienstreisen** (Business Trip) mit HRMS: Verpflegungsmehraufwand nach Dienstreise-Region und Kilometerpauschale für den privaten Pkw. Eine gebuchte Dienstreise legt eine Spesenabrechnung (Expense Claim) als Entwurf an. Die Regionen mit ihren Pauschalen kommen bei der Installation als Grundliste nach dem deutschen Steuerrecht dazu. Ein Update der App kann neue Pauschalen bringen: Der Patch `import_business_trip_regions` in `patches.txt` importiert die Liste bei `bench migrate` erneut, legt fehlende Regionen an und ergänzt neue Zeiträume, ohne vorhandene Beträge zu ändern. In den Dienstreise-Einstellungen stehen die Kilometerpauschale und je eine „Art der Auslagenabrechnung“ für Verpflegungsmehraufwand und Kilometerpauschale.
- **GDPdU-Export** für die Übergabe von Daten an das Finanzamt nach § 147 Abs. 6 AO und den GoBD: je DocType eine CSV-Datei, auf Wunsch mit den Anhängen, dazu `index.xml` und die DTD, als ZIP-Datei am Export. Welche DocTypes dazugehören, entscheidet die App nicht, das klärt die Firma mit ihrer Steuerberatung.

Die DTD `gdpdu-01-03-2019.dtd` gehört nicht zur App, sie ist von der CaseWare Germany GmbH und liegt unverändert bei. Mehr steht im [README von erpnext_germany](https://github.com/alyf-de/erpnext_germany/blob/v16.2.2/README.md).

## erpnext_datev

- **Repository:** [alyf-de/erpnext_datev](https://github.com/alyf-de/erpnext_datev) von der ALYF GmbH, Lizenz GPL-3.0
- **Name in bench:** `erpnext_datev`

Die App verbindet ERPNext mit DATEV auf zwei Wegen:

- **DATEV Unternehmen Online.** Beim Buchen einer Ausgangsrechnung, Eingangsrechnung oder Spesenabrechnung schickt die App den Beleg per E-Mail an DATEV Unternehmen Online, als PDF des Ausdrucks oder als die Anhänge des Belegs. Einrichtung in den DATEV Unternehmen Online-Einstellungen: Integration aktivieren, unter „Absender“ das E-Mail-Konto wählen, je Belegart die Zieladresse aus DATEV Unternehmen Online eintragen und „Anhänge anfügen“ oder „Druck anfügen“ wählen. Die Absenderadresse muss die des gewählten E-Mail-Kontos sein.
- **DATEV-CSV-Export.** Der Bericht „DATEV“ zeigt die Buchungen (GL Entry) im Format von DATEV und exportiert sie mit den Stammdaten als ZIP-Datei für die Steuerberatung. Einrichtung in den DATEV-Einstellungen: Mandantennummer, Beraternummer und „Temporäre Gegenkontonummer“, empfohlen ist 9090.

ERPNext kennt keine Automatikkonten von DATEV. Mit dem Gegenkonto 9090 ist die Automatik abgeschaltet. Wer ein anderes Gegenkonto nimmt, bucht in ERPNext nur auf Konten ohne Automatik, sonst stimmt der Abzug der Umsatzsteuer nicht. DATEV und DATEV Unternehmen Online sind Marken der DATEV eG, die App ist von ihr weder geprüft noch empfohlen. Mehr steht im [README von erpnext_datev](https://github.com/alyf-de/erpnext_datev/blob/v16.0.2/README.md).

## eu_einvoice

- **Repository:** [alyf-de/eu_einvoice](https://github.com/alyf-de/eu_einvoice) von der ALYF GmbH, Lizenz GPL-3.0-or-later
- **Name in bench:** `eu_einvoice`
- **Dokumentation:** [eu_einvoice/docs](https://github.com/alyf-de/eu_einvoice/tree/v16.4.0/eu_einvoice/docs/en/eu_einvoice) im Repository

Die App erstellt und liest E-Rechnungen im Format UN/CEFACT Cross Industry Invoice (CII) in den Profilen BASIC, EN 16931, EXTENDED und XRECHNUNG. Außer bei XRECHNUNG lässt sich die XML in ein PDF einbetten (ZUGFeRD, Factur-X). UBL-Rechnungen und ein Versand über Peppol gehören nicht dazu.

- **Ausgangsrechnung.** Das Feld „E-Rechnungs-Profil“ wählt das Profil. Je nach den E-Rechnungs-Einstellungen entsteht die E-Rechnung beim Speichern oder Buchen zur Probe und wird gegen die Schematron-Regeln des Profils geprüft. „E-Rechnung herunterladen“ unter „…“ liefert die XML. Das PDF aus der Druckvorschau enthält sie eingebettet, außer beim Profil XRECHNUNG.
- **Eingangsrechnung.** Ein E-Rechnungs-Import (E Invoice Import) liest eine XML-Datei oder ein ZUGFeRD-PDF, prüft es und übernimmt Lieferant, Positionen, Steuern und Zahlungsbedingungen. Rechnungen mit formalen Fehlern lassen sich trotzdem importieren.
- **PDF/A-3.** Vor dem Einbetten wandelt die App das PDF mit Ghostscript in PDF/A-3 um. Ghostscript ist im Image, siehe [Architektur](architektur.md#ghostscript).

Einrichtung:

- **Codelisten** im Format Genericode, etwa für Zahlungsarten (UNTDID 4461), Einheiten, Steuerkategorien (UNTDID 5305), Befreiungsgründe (VATEX) und elektronische Adressen (EAS). Die XML-Datei wird zuerst heruntergeladen und dann hochgeladen; danach ordnet man die Codes Zahlungsbedingungen, Einheiten, Steuervorlagen und Konten zu.
- **Käufer-Referenz** (Buyer Reference), in Deutschland die Leitweg-ID für öffentliche Auftraggeber, an Ausgangsrechnung, Auftrag oder Kunde.
- **Elektronische Adresse** mit ihrem Schema an Unternehmen, Kunde und Lieferant; ohne Eintrag nimmt die App E-Mail-Adressen.
- **Bankverbindung** über eine Zahlungsweise vom Typ Bank mit Konto und Bankkonto, in der Vorlage der Zahlungsbedingungen gewählt.
- **E-Rechnungs-Einstellungen:** ob beim Speichern und Buchen validiert wird und was bei einem Fehler geschieht.

Die App [Compendium](https://github.com/alyf-de/compendium), die die Dokumentation in Desk unter `/app/docs` anzeigt, ist nicht im Image. Die Dokumentation steht deshalb nur im Repository.

## erpnext_pdf-on-submit

- **Repository:** [alyf-de/erpnext_pdf-on-submit](https://github.com/alyf-de/erpnext_pdf-on-submit) von der ALYF GmbH, Lizenz GPL-3.0-or-later
- **Name in bench:** `pdf_on_submit`, nicht der Name des Repositories. Unter diesem Namen steht die App in `bench --site <site> list-apps` und in `--install-app`.

Die App erzeugt beim Buchen eines Belegs ein PDF und hängt es an den Beleg. Das geht für jeden DocType, der sich drucken und buchen lässt.

Einrichtung in den PDF-on-Submit-Einstellungen: In der Tabelle „Aktiviert für“ steht eine Zeile je DocType, auf Wunsch mit eigenem Druckformat, Briefkopf, Muster für den Dateinamen und Filtern, etwa für eigene PDFs von Gutschriften. „PDF im Hintergrund erstellen“ ist vorgegeben an: Das PDF entsteht dann in einem Hintergrundjob, also nur mit laufenden Workern. Das PDF entsteht in der Sprache aus dem Feld Sprache des Belegs; an Kunden und Lieferanten lässt sich dafür eine eigene Drucksprache (Print Language) wählen.

## banking

- **Repository:** [alyf-de/banking](https://github.com/alyf-de/banking) (ALYF Banking) von der ALYF GmbH, Lizenz GPL-3.0
- **Name in bench:** `banking`
- **Dokumentation:** [Banking Wiki](https://github.com/alyf-de/banking/wiki) und [banking/docs](https://github.com/alyf-de/banking/tree/v16.6.4/banking/docs/en/banking) im Repository

Die App holt Kontoauszüge als Banktransaktionen (Bank Transaction) in ERPNext und hilft, sie mit Belegen abzugleichen.

- **Abgleich** im Bankabgleich Beta (Bank Reconciliation Tool Beta): Banktransaktionen gegen Zahlungen und Buchungssätze oder gegen offene Ausgangs- und Eingangsrechnungen, für die der Abgleich die Zahlung selbst anlegt, mit HRMS auch gegen Spesenabrechnungen. Der Abgleich ist kostenlos und arbeitet auch mit Umsätzen aus anderen Quellen.
- **Import von Hand:** CAMT-Dateien (camt.052, camt.053) und MT940-Dateien, hochgeladen im Bankabgleich Beta.
- **EBICS:** Abruf der Umsätze direkt bei der Bank, für Banken in Deutschland, Österreich, Frankreich und der Schweiz. EBICS braucht ein kostenpflichtiges Abonnement bei ALYF ([banking.alyf.de](https://banking.alyf.de/banking-pricing)) und einen EBICS-Zugang der Bank. Für diesen Zugang empfiehlt die Dokumentation die Signaturklasse T: Damit ruft ERPNext Umsätze ab, kann aber keine Zahlungen auslösen.
- **SEPA-Zahlungsaufträge** (SEPA Payment Order) im Format pain.001 für Zahlungen an Lieferanten und Mitarbeiter, aus Eingangsrechnungen und mit HRMS aus Spesenabrechnungen. Einen gebuchten Auftrag lädt man unter „Aktionen“ mit „Als XML herunterladen“ herunter und dann selbst bei der Bank hoch. Das Senden per EBICS ist in banking v16.6.4 abgeschaltet, siehe [SEPA Payment Order](https://github.com/alyf-de/banking/blob/v16.6.4/banking/docs/en/banking/sepa-payment-order.md#send-via-ebics-currently-disabled).

Für EBICS nutzt die App die Python-Bibliothek fintech, die nicht unter einer Open-Source-Lizenz steht, siehe [README](../README.md#lizenz). ALYF erwirbt dafür eine Lizenz und erhält und speichert dazu Host-ID, Partner-ID und User-ID des EBICS-Zugangs. Löscht man den EBICS-Benutzer, widerruft ALYF die Lizenz und löscht die Angaben ([EBICS-Dokumentation](https://github.com/alyf-de/banking/blob/v16.6.4/banking/docs/en/banking/ebics-integration.md)). Kundennummer und API-Token des Abonnements gehören in die Bankeneinstellungen (Banking Settings).

## Steuerbote

- **Repository:** [encircle360-oss/steuerbote](https://github.com/encircle360-oss/steuerbote), Lizenz AGPL-3.0-or-later
- **Name in bench:** `steuerbote`
- **Dokumentation:** [docs](https://github.com/encircle360-oss/steuerbote/tree/v0.1.1/docs) im Repository

Steuerbote bringt Steuermeldungen aus ERPNext an ELSTER, zuerst die Umsatzsteuer-Voranmeldung, danach Dauerfristverlängerung, Zusammenfassende Meldung und die Jahresmeldungen. Die Voranmeldung rechnet es aus dem Hauptbuch und vergleicht Beleg für Beleg die gebuchte Steuer mit der Steuer, die sich aus der Bemessungsgrundlage ergibt. Die Vorgaben für SKR03 und SKR04 enthalten auch die Kontonummern der SKR-Vorlagen von ERPNext.

**Status: in Entwicklung, nicht einsatzfähig.** Ohne eigene Hersteller-ID läuft die Übermittlung an ELSTER nur als Simulation. Abgeben lässt sich eine Voranmeldung ohne Hersteller-ID als XML-Datei über Mein ELSTER, siehe [Abgabe über Mein ELSTER](https://github.com/encircle360-oss/steuerbote/blob/v0.1.1/docs/abgabe-mein-elster.md).

Im Image:

- **ERiC ist nicht dabei.** ERiC, die Bibliothek der Finanzverwaltung für die Übermittlung, darf nur als Teil des eigenen Produkts weitergegeben werden. Jeder Betreiber lädt ERiC für Linux x86_64 selbst aus dem ELSTER-Entwicklerbereich und richtet es in den ERiC-Einstellungen ein, siehe [ERiC](https://github.com/encircle360-oss/steuerbote/blob/v0.1.1/docs/eric.md).
- **Plattform.** ERiC braucht Linux x86_64 mit glibc ab 2.28 und mindestens 5 GiB freien Speicher. Das Image für `linux/amd64` ist auf Debian trixie gebaut, das glibc 2.41 mitbringt. Im Image für `linux/arm64` ist Steuerbote installiert, ERiC läuft dort aber nicht; was ERiC braucht, also Prüfen, Testsenden und Senden an ELSTER, geht nur mit `linux/amd64`. Wer ERiC nutzt, betreibt deshalb alle Dienste aus dem Image auf `linux/amd64`, in einem Kubernetes-Cluster mit Knoten beider Plattformen per `kubernetes.io/arch: amd64` im `nodeSelector` jedes Dienstes und Jobs des Charts. Die Abgabe als XML-Datei über Mein ELSTER braucht ERiC nicht und geht auf beiden Plattformen.
- **Ablage.** Die eingerichtete Laufzeit liegt außerhalb jeder Site in `sites/eric` der Bench, im Container also im Volume `sites`. Sie bleibt bei einem Wechsel des Images erhalten, `bench backup` sichert sie aber nicht. `steuerbote_eric_root` in `common_site_config.json` legt ein anderes Verzeichnis fest.
- **Worker.** Die Einrichtung von ERiC sowie Prüfen, Testsenden und Senden laufen als Hintergrundjobs in der Queue `long`, im Beispiel also im Dienst `queue-long`. Das Archiv von ERiC muss deshalb in diesem Container liegen; am einfachsten im Volume `sites`, das alle Dienste teilen.

Für Steuermeldungen gilt der [Haftungsausschluss von Steuerbote](https://github.com/encircle360-oss/steuerbote/blob/v0.1.1/README.md#haftungsausschluss).

## Zusammenspiel der Apps

- **HRMS und erpnext_germany:** Dienstreisen legen Spesenabrechnungen von HRMS an, die Krankenkassen hängen an HRMS. Deshalb kommt HRMS zuerst.
- **erpnext_datev und erpnext_pdf-on-submit:** Wer für dieselbe Belegart beide nutzt, wählt in den DATEV Unternehmen Online-Einstellungen „Anhänge anfügen“. PDF on Submit hängt das PDF an, und erpnext_datev schickt diesen Anhang.
- **banking und erpnext_germany:** erpnext_germany ergänzt die Eingangsrechnung um „Dienstreise“, „Dienstreise-Mitarbeiter“ und „An Mitarbeiter zahlen“. Das letzte Feld markiert eine Rechnung, die ein Mitarbeiter vorgestreckt hat, mit oder ohne Dienstreise. Sind „Dienstreise-Mitarbeiter“ und „An Mitarbeiter zahlen“ gesetzt, geht ein SEPA-Zahlungsauftrag dazu an den Mitarbeiter statt an den Lieferanten; banking zeigt dann statt „Lieferanten-Bankkonto“ das Feld „Mitarbeiter-Bankkonto“.
- **banking und HRMS:** Banktransaktionen lassen sich gegen offene Spesenabrechnungen abgleichen, und aus einer genehmigten Spesenabrechnung entsteht direkt ein SEPA-Zahlungsauftrag.
- **ERPNext und Steuerbote:** Die Vorgaben von Steuerbote für SKR03 und SKR04 kennen die Kontonummern der SKR-Vorlagen von ERPNext.

## Nicht im Image

- **ERiC** für Steuerbote, aus Lizenzgründen, siehe oben.
- **Compendium**, die Anzeige der Dokumentation von eu_einvoice und banking in Desk.
- **Weitere Apps.** Vorschläge für Apps, die deutsche Unternehmen brauchen, gehen als Issue an dieses Repository, siehe [Roadmap](roadmap.md).
