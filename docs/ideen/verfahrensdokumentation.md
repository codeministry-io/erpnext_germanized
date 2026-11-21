# Verfahrensdokumentation aus ERPNext: Idee und Ausbauplan

Stand: 21.11.2026 · Status: Idee, nicht umgesetzt · Entschieden: eigene App, voller Umfang als Ziel in Stufen · Offen: Name und Lizenz (Abschnitte 6 und 7)

**Lesehilfe.** `[Sn]` verweist auf das Quellenverzeichnis in Abschnitt 8. „unbestätigt“: keine Primärquelle gefunden; solche Punkte kommen erst mit Beleg in Code oder Text. „[Einschätzung]“: eigene Schlussfolgerung. Rz. ist die Randziffer der GoBD. Die Nummern sind in der Fassung von 2019 [S1] und in den Ausgaben 2021 und 2025 des AO-Handbuchs [S5, S2] gleich; die Änderungsschreiben haben den Wortlaut geändert, nicht die Nummern, außer Rz. 124 (2024 aufgehoben) und Rz. 182–185 [S3, S4]. [S2] gibt den Stand vor der zweiten Änderung wieder, für Rz. 76, 118–133 und 166 gilt [S4]. Technische Angaben gelten für die Apps von erpnext_germanized v16.60.0-5: Frappe 16.60.2, ERPNext und HRMS 16.60.0, erpnext_germany 16.2.2, erpnext_datev 16.0.2, eu_einvoice 16.4.0, erpnext_pdf-on-submit 16.3.1, banking 16.6.4 und Steuerbote 0.3.0 [S33]. Feldnamen sind im Quelltext geprüft, wo nicht „unbestätigt“ steht; Vorgabewerte stehen in Klammern. `<app>` steht für den Python-Namen der App, solange der Name offen ist.

## Kurzfassung

- **Pflicht.** Zu den Büchern gehören die „zu ihrem Verständnis erforderlichen Arbeitsanweisungen und sonstigen Organisationsunterlagen“ (§ 147 Abs. 1 Nr. 1 AO) [S8]. Die GoBD verlangen je DV-System eine Verfahrensdokumentation in vier Teilen (Rz. 151–153), die über die ganze Aufbewahrungsfrist zeigt, was gelebt wurde, „insbesondere für die eingesetzten Versionen der Programme (Programmidentität)“ (Rz. 154) [S2].
- **Lücke.** Weder die Apps im Image noch der Frappe Cloud Marketplace noch eine Code-Suche auf GitHub zeigen einen Generator für ERPNext [S31, S42–S48, S50, S51]. Repository und Herstellerdokumentation beschreiben den ausgelieferten Stand, nicht die Einrichtung einer Installation [S29].
- **Idee.** Eine Frappe-App erzeugt je Unternehmen eine deutsche Verfahrensdokumentation aus Einstellungen, Protokollen und Versionsständen der Site und ergänzt sie um ein Formular für die organisatorischen Angaben. Was fehlt, steht als „Fehlt:“ im Text. Fassungen werden unveränderlich gespeichert, von der Geschäftsführung freigegeben, jährlich eingefroren und als „veraltet“ markiert, sobald sich eine dokumentierte Einstellung oder eine Version ändert.
- **Plattform.** Frappe 16 liefert die meisten Nachweise schon: SBOM, Patch Log, Version, Permission Log, Access Log [S35–S38]. Es fehlen ein im Container lesbarer Image-Stand, ein unveränderliches Hauptbuch als Vorgabe und eine lange Aufbewahrung der Protokolle; vier Einstellungs-DocTypes der Apps werden nicht protokolliert, der DATEV-CSV-Export hinterlässt keine Spur, MCP ist in der Vorgabe eingeschaltet [S36, S40, S42–S46].
- **Risiko.** Eine fehlende Verfahrensdokumentation wiegt allein selten schwer, gibt aber anderen Mängeln Gewicht (Rz. 155; BFH X R 3/22) [S2, S23]. Hauptrisiko eines Generators ist falsche Sicherheit: Text, der vollständig wirkt, während die Praxis abweicht. Gegenmittel: Lücken statt Platzhalter, Herkunft je Absatz, getestete Aussagen, keine Konformitätsaussagen.
- **Ziel und Plan.** Ziel ist der volle Umfang. Stufe 1, der Grundausbau, kostet grob 31 Entwicklertage, alle acht Stufen zusammen grob 61 (Abschnitt 5).
- **Verortung.** Eigene App in der Distribution, entschieden am 21.11.2026; die Fakten zu den Alternativen stehen in Abschnitt 6, Name und Lizenz folgen bei der Gründung des Repositorys.

## 1. Ausgangslage und Pflicht

### 1.1 Rechtsgrundlagen

| Punkt | Regel |
|---|---|
| Wer | Allein der Steuerpflichtige, auch wenn er Buchführung oder Rechenzentrum auslagert (Rz. 21) [S2]; die Verantwortung ist „persönlich und unausweichlich“ [S28]. Softwarehersteller trifft keine Pflicht nach der AO; ihre Dokumentation deckt den ausgelieferten Stand, Anpassungen brauchen eine Dokumentation des Unternehmens [S29]. Zertifikate binden niemanden (Rz. 179–181) [S2]. |
| Gesetz | § 147 Abs. 1 Nr. 1 AO: Bücher „sowie die zu ihrem Verständnis erforderlichen Arbeitsanweisungen und sonstigen Organisationsunterlagen“ [S8]; ebenso § 257 Abs. 1 Nr. 1 HGB [S15]. § 145 Abs. 1 AO: Überblick für einen sachverständigen Dritten [S6]. § 146 Abs. 3 Satz 3 AO: Die Bedeutung von Abkürzungen und Schlüsseln muss feststehen, nach Rz. 149 in der Verfahrensdokumentation [S7, S2]. |
| Verwaltung | GoBD, BMF-Schreiben vom 28.11.2019, IV A 4 - S 0316/19/10003 :001, BStBl I S. 1269 [S1]; geändert am 11.03.2024, IV D 2 - S 0316/21/10001 :002, BStBl I S. 374, ab 01.04.2024 [S3]; geändert am 14.07.2025, IV D 2 - S 0316/00128/005/088, ab diesem Tag (Rz. 185) [S4]. Keine der Änderungen berührt Rz. 151–155 [S3, S4]. |
| Rz. 151 | Eine strukturierte Verfahrensdokumentation je DV-System, „für einen sachverständigen Dritten in angemessener Zeit nachprüfbar“; der Umfang folgt der Komplexität. Dem Dritten fehlen „produktabhängige System- oder Programmierkenntnisse“ (Rz. 148) [S2]. |
| Rz. 152–153 | Rz. 152 beschreibt den „organisatorisch und technisch gewollten Prozess“ von der Entstehung bis zur Wiedergabe; Rz. 153 nennt die vier Teile „allgemeine Beschreibung, Anwenderdokumentation, technische Systemdokumentation und Betriebsdokumentation“ [S2]. |
| Rz. 154 | Dokumentiert ist, was über die Aufbewahrungsfrist gelebt wurde, „insbesondere für die eingesetzten Versionen der Programme (Programmidentität)“; Änderungen werden versioniert, die Historie bleibt nachvollziehbar [S2]. Änderungen „inhaltlich und zeitlich lückenlos“ (Rz. 150); anlassbezogene Prüfung des Systems gegen die Dokumentation im IKS (Rz. 101) [S2]. |
| Aufbewahrung | So lange wie die Unterlagen, die sie erklärt (Rz. 154) [S2]: zehn Jahre, länger, solange die Festsetzungsfrist läuft (§ 147 Abs. 3 Satz 1, 5 AO) [S8]; § 257 Abs. 4 HGB [S15]. Eine vom System erzeugte Verfahrensdokumentation wird im Ursprungsformat aufbewahrt (Rz. 133) [S2]. |
| Rz. 155 | Ein „formeller Mangel mit sachlichem Gewicht“ nur, wenn die Nachvollziehbarkeit leidet [S2]. |
| Änderung 2024 | Z3 heißt „Datenüberlassung“, auch über eine Plattform (§ 87a AO), anforderbar mit der Prüfungsanordnung, mobile Bearbeitung, Löschung nach Bestandskraft (Rz. 167–169); Zugriff auf die Prüfung beschränkt (Rz. 159); Kontoart und Kontotyp in den Journaldaten (Rz. 94); Rz. 124 aufgehoben; Anlage neu gefasst [S3]. Cloud ist seit 2019 erfasst (Rz. 20) [S1]. |
| Änderung 2025 | E-Rechnungen: Der strukturierte Teil genügt (Rz. 118, 119, 131); keine Bildkopie ausgehender Rechnungen, wenn sie reproduzierbar sind (Rz. 76); das Ergebnis von Z2 ist maschinell auswertbar zu liefern (Rz. 166) [S4]. |

### 1.2 Was die Verfahrensdokumentation beschreibt und ein ERP belegen kann

| Anforderung | Rz. | Inhalt [S2] |
|---|---|---|
| Unveränderbarkeit | 58–60, 107–112 | Änderungen „müssen … protokolliert werden“ (59); Festschreibung als Mittel, ein Dateisystem allein genügt nicht (110); Änderungen an Einstellungen protokollieren, Stammdaten historisieren, Historie unveränderbar (111) |
| Zeitpunkt der Festschreibung | 52, 85, 87, 109 | Kennzeichnung „zwingend“, außer bei Unveränderbarkeit ab Erfassung (85); Journal bis Ende des Folgemonats, wenn ein Vorsystem die Grundaufzeichnung hält (87), später nur mit vorheriger Grundaufzeichnung (52); bis Jahresende offene Stapel unzulässig (109) |
| Vollständigkeit, Richtigkeit | 36–44 | etwa Lückenanalyse der Belegnummern (40) |
| Zeitgerechtigkeit, Ordnung | 45–57 | unbare Vorgänge binnen zehn Tagen „unbedenklich“ (47); Kasse täglich (48) |
| Belegfunktion | 61–81 | Erfassung bis Ablage elektronischer Belege (66); automatische Buchungen: Regeln, berechtigte Änderungen, Nachweis der Anwendung (80); AfA (81) |
| Journal, Konten | 82–99 | Einstellungen mit Historie (89); Journalfelder (94); Zuordnungstabellen (97) |
| IKS | 100–102 | „Die Beschreibung des IKS ist Bestandteil der Verfahrensdokumentation“ (102) |
| Datensicherheit | 103–106 | Die Beschreibung der Datensicherung gehört in die Verfahrensdokumentation (106) |
| Aufbewahrung | 113–135, 142–144 | Ursprungsformat (131–133); Migration (142) |
| Bildliche Erfassung | 136–141 | „Das Verfahren muss dokumentiert werden“ (136) |
| Datenzugriff | 158–178 | Erstqualifizierung (161); Z1–Z3 (165–167) |

### 1.3 Warum ein Git-Repository nicht reicht

| Teil nach Rz. 153 | Repository deckt ab | Es fehlt |
|---|---|---|
| Allgemeine Beschreibung | nichts | Unternehmen, Organisation, Zuständigkeiten, eingesetzte Systeme |
| Anwenderdokumentation | allgemeine Moduldokumentation | die tatsächlichen Abläufe des Unternehmens (Rz. 152) |
| Technische Systemdokumentation | Code, Schema, ausgeliefertes Verhalten [S29] | Einstellungen dieser Installation und ihre Historie (Rz. 89, 111), Anpassungen [S29], welche Version wann lief (Rz. 154) |
| Betriebsdokumentation | nichts | Benutzer und Rollen (Rz. 100), Sicherung und Wiederherstellung (Rz. 103–106), Aufbewahrung, Ort der Daten (§ 146 Abs. 2–2b AO) [S7] |

Gründe [Einschätzung]: Der Leser muss keinen Code lesen (Rz. 148) [S2]. Commits halten Code fest, nicht Auslieferungen, und belegen deshalb keine Programmidentität (Rz. 154). Entfernte Historie lässt sich umschreiben: `--force` „can cause the remote repository to lose commits“ [S32]. Der Steuerpflichtige muss die Verfahrensdokumentation über die ganze Frist halten und auf Anforderung lesbar machen (Rz. 154, 156; § 147 Abs. 5 AO) [S2, S8], auf Deutsch oder auf Verlangen übersetzt (§ 87 Abs. 2, § 146 Abs. 3 Satz 2 AO) [S14, S7]. Ein Repository ist höchstens eine in Bezug genommene „mitgeltende Unterlage“ [S29].

### 1.4 Praxis der Außenprüfung

- **Anforderung.** Mit der Prüfungsanordnung können Unterlagen in angemessener Frist verlangt werden; Daten aus DV-Systemen sind maschinell auswertbar zu übermitteln (§ 197 Abs. 3 AO) [S11]. Z1 nur lesend vor Ort, kein Fernzugriff (Rz. 165); Z2 Auswertung durch den Steuerpflichtigen (Rz. 166, Fassung 2025); Z3 Überlassung samt Stammdaten und Verknüpfungen (Rz. 167) [S2, S4]. Keine vorgefilterten Berichte (Rz. 173); Strukturinformationen maschinell lesbar (Rz. 176); der Steuerpflichtige begrenzt den Zugriff auf die relevanten Daten (Rz. 172) [S2]. Typische Anforderungslisten des ersten Prüfungstags: unbestätigt.
- **Format.** Beschreibungsstandard (index.xml mit CSV) für IDEA; außerdem ASCII, xlsx, accdb, dBASE, SAP/AIS [S3, Anlage].
- **Analysen.** Zeitreihen-, Ziffern-, Struktur- und Verteilungsanalyse, Summarische Risikoprüfung, Stichproben [S20].
- **Sanktionen.** Mitwirkungsverzögerungsgeld 75 Euro je Tag, höchstens 150 Tage (§ 200a AO) [S12]; Verzögerungsgeld 2.500 bis 250.000 Euro bei verweigertem Datenzugriff (§ 146 Abs. 2c AO) [S7], nicht mehr für nicht vorgelegte Unterlagen, wenn die Steuer nach 2024 entstanden oder die Prüfung nach 2024 angeordnet ist (AEAO zu § 146 Nr. 5) [S18].
- **Schätzung.** Ordnungsmäßige Bücher sind Grundlage der Besteuerung (§ 158 Abs. 1 AO) [S9]; geschätzt wird bei fehlenden Büchern oder in den Fällen des § 158 Abs. 2 (§ 162 Abs. 2 Satz 2 AO) [S10]. Jeder Mangel wird gewichtet, eine Vollschätzung nur bei schweren Mängeln (BFH X R 3/22, Leitsätze 1–2) [S23]. Formell mangelhafte Bücher erlauben eine Hinzuschätzung ohne nachgewiesenen sachlichen Fehler (BFH X R 20/13, Leitsatz 3) [S21]; Mängel ohne Gewicht nicht (Rz. 155; X R 3/22, Leitsatz 1; X B 65/17, Leitsatz 3) [S2, S23, S22]. Fehlende Programmierprotokolle einer Kasse sind fehlende „sonstige Organisationsunterlagen“ und ein gewichtiger Mangel (X R 20/13) [S21]; sie dürfen elektronisch vorliegen, das Gericht muss den Mangel gewichten (X B 65/17) [S22]; X R 23-24/21 (2025) stellt Anforderungen an Methode und Begründung [S24]. In der Rechtsprechungsdatenbank des Bundes enthält keine BFH-Entscheidung das Wort „Verfahrensdokumentation“; die Rechtsprechung zur Dokumentation betrifft Kassensysteme [S25, S21–S24].
- **Kasse (Abgrenzung).** § 146a AO verlangt eine zertifizierte technische Sicherheitseinrichtung [S13]; § 1 KassenSichV erfasst Kassensysteme und nimmt „elektronische Buchhaltungsprogramme“ aus [S16]; der AEAO zu § 146a ist seit 26.10.2026 neu gefasst [S19]. Wird ERPNext POS für Barverkäufe genutzt, ist es ein Kassensystem: erkennen und hinweisen, nicht dokumentieren [Einschätzung].

### 1.5 Muster und Angebote

| Dokument | Herausgeber, Stand | Gliederung, Aussage |
|---|---|---|
| Muster-Verfahrensdokumentation zur Belegablage | AWV, V1.0 vom 19.10.2015, weiter aktuell [S26]; die bei der IHK abgelegte Kopie ist dieselbe V1.0 [S27] | 0 Hinweise · 1 Vorbemerkungen · 2 Zielsetzung und Überblick (Anwendungsbereich, Unternehmen, Rechtsgrundlagen, Unterlagen mit Belegfunktion, Einweisung, Abgrenzung) · 3 Organisation und Sicherheit (Hard- und Software, Zuständigkeiten, IKS, Datenschutz) · 4 Verfahren je Belegart (Papier, gescannt, originär digital; jeweils vom Posteingang bis zur Vernichtung) · 5 Mitgeltende Unterlagen · 6 Änderungshistorie · 7 Glossar. Word-Vorlage; Nutzung durch Verbände nur nach Vereinbarung [S26]. |
| Muster-Verfahrensdokumentation zum ersetzenden Scannen | BStBK und DStV, v2.1 vom 27.02.2026, Dateiname noch „v2.0-2019-11-29“ [S28]; die AWV nennt den alten Titel „…zur Digitalisierung und elektronischen Aufbewahrung von Belegen inkl. Vernichtung der Papierbelege“ [S26] | 0 Hinweise (Dritte, Cloud) · 1 Vorbemerkungen (Freigabe durch die Geschäftsleitung, Version, gültig ab) · 2 Zielsetzung und Überblick (Unternehmensportrait, Organisation, Einsatzorte, Rechtsgrundlagen, Dokumente, Einweisung, Abgrenzung) · 3 Organisation und Sicherheit (Hard- und Software, Zuständigkeiten, IKS, Datenschutz und Datensicherheit) · 4 zentrales Scannen · 5 mobiles Scannen · 6 Mitgeltende Unterlagen · 7 Änderungshistorie (Datum, Kapitel, Inhalt, geändert durch) · 8 Glossar · 9 Anlage |
| GoBD-Praxisleitfaden, Kapitel 5 | AWV, v2.2, 2023 [S29] | Hauptdokument mit mitgeltenden Unterlagen; Gültigkeitszeitraum je Version; Verfahrensdokumentation und IKS als Grundlage eines Steuerkontrollsystems (Art. 97 § 38 EGAO) [S17] |
| Muster-VD Kassenführung | DFKA, 08/2020 [S30] | nicht Gegenstand |

Am Markt gibt es drei Arten von Angeboten: Kanzlei-Software, die die Verfahrensdokumentation über einen Fragebogen erstellt, teils mit Vorbefüllung aus Unterlagen der Mandanten; Vorlagen mit Beratung durch die Steuerberatung, oft mit jährlicher Überprüfung; einzelne quelloffene Werkzeuge, die aus einem Fragebogen oder aus dem Stand eines Buchhaltungsprogramms ein Dokument erzeugen. Im Frappe-Umfeld gibt es keinen Generator; eine quelloffene App für den Z3-Export klammert die Verfahrensdokumentation ausdrücklich aus [S31, S50, S51]. Werbeaussagen wie „GoBD-zertifiziert“ sind verbreitet, obwohl Zertifikate die Finanzverwaltung nicht binden (Rz. 179–181) [S2].

### 1.6 Einschätzung

- Eine kleine GmbH braucht die Verfahrensdokumentation ohnehin. Fehlt sie, ist das Risiko allein gering (Rz. 155; Gewichtung nach X R 3/22) [S2, S23]; bei einer GmbH ohne Kasse gibt sie anderen Mängeln aber zusätzliches Gewicht [Einschätzung].
- Im ERP liegt der Wert in der Technik: Eine erzeugte Verfahrensdokumentation bleibt fast ohne Aufwand aktuell und belegt die Programmidentität mit Daten statt Behauptungen [Einschätzung]. Den Systemüberblick nach Rz. 160 („einen vollständigen Systemüberblick“ samt Beschreibung der Tabellen, Felder, Verknüpfungen und Auswertungen) erzeugt ein ERP besser als jede Vorlage [S2; Einschätzung].
- Hauptrisiko ist falsche Sicherheit: Text, der vollständig wirkt, während die Praxis abweicht, widerspricht Rz. 154 [S2]. Gegenmittel sind Lücken statt Platzhalter, die Herkunft je Absatz, Aussagen nur mit Test und keine Konformitätsaussagen.
- Ergebnis: bauen, in Stufen, mit dem Grundausbau zuerst [Einschätzung].

## 2. Zielbild

### 2.1 Grundsätze

1. **Ein Dokument je Unternehmen.** Steuerpflichtig ist das Unternehmen (Rz. 21) [S2]; Teile, die für die ganze Site gelten, stehen in jedem Dokument und sind so gekennzeichnet [Einschätzung].
2. **Deutsch, für Laien lesbar.** Das Dokument ist immer deutsch, unabhängig von der Sprache des Benutzers (§ 87 AO, § 146 Abs. 3 AO) [S14, S7]. Es richtet sich an einen Leser ohne Produktkenntnis (Rz. 148) [S2]: Namen der Oberfläche wie in der deutschen Übersetzung, der DocType beim ersten Vorkommen in Klammern.
3. **Aussagen nur mit Test.** Jeder erzeugte Satz über das Verhalten des Systems hat einen Test, der dieses Verhalten prüft [Einschätzung].
4. **Lücken statt Platzhalter.** Für organisatorische Angaben gibt es keinen Vorgabetext. „keine“ ist eine gültige Angabe, ein leeres Feld nicht.
5. **Eigener Text.** Die Gliederung folgt Rz. 153 und verweist auf die Muster aus 1.5; deren Wortlaut wird nicht übernommen, die AWV erlaubt eine Nutzung nur nach Vereinbarung [S26].
6. **Keine Konformitätsaussagen** (2.9).

### 2.2 Gliederung

a = aus Konfiguration und Protokollen ableitbar, b = Angabe des Unternehmens, c = beides. Stufen nach Abschnitt 5. „Formular“ heißt: In Stufe 1 ist das Kapitel ein Formularabschnitt mit „Fehlt:“, bis die genannte Stufe es erzeugt.

| Nr. | Teil (Rz. 153) | Kapitel | Rz., Norm | Kl. | Stufe 1 | Ausbau |
|---|---|---|---|---|---|---|
| 1 | Allgemeine Beschreibung | Zweck, Geltung, Version, Freigabe | 151, 154 | c | erzeugt und Formular | – |
| 2 | | Unternehmen: Firma, Rechtsform, Kontenrahmen, Besteuerung | § 145 Abs. 1 AO; 151 | c | erzeugt und Formular | – |
| 3 | | Organisation: Verantwortliche, Vertretung, Beratung, Dienstleister | 21 | b | Formular | – |
| 4 | | Systemlandschaft, Vor- und Nebensysteme, Schnittstellen | 20, 161 | c | erzeugt und Formular | Stufe 7 (§ 146a) |
| 5 | Anwenderdokumentation | Prozess je Belegart, Entstehung bis Wiedergabe | 152 | c | Formular | Stufe 3 |
| 6 | | Belegeingang, Papier, Scannen | 66, 136–141 | b | Formular | Stufe 8 |
| 7 | | Nummernkreise, Schlüssel, Abkürzungen | 149; § 146 Abs. 3 Satz 3 AO | a | erzeugt | – |
| 8 | Technische Systemdokumentation | Unveränderbarkeit, Festschreibung, Storno, Protokoll | 52, 58–60, 85, 87, 107–112 | a | erzeugt | – |
| 9 | | Automatische Buchungen | 80–81 | a | Formular | Stufe 4 |
| 10 | | Tabellen, Felder, Verknüpfungen | 160 | a | Formular | Stufe 2 |
| 11 | | Versionen mit Zeitraum, Anpassungen | 111, 154 | a | erzeugt | – |
| 12 | | Aufbewahrung, Formate, Z1–Z3 | 113–135, 158–178 | c | Formular und Exporte | Stufe 5 |
| 13 | | Migration, Systemwechsel | 142–144 | c | Formular | Stufe 5 |
| 14 | Betriebsdokumentation | Zugänge, Rollen, Funktionstrennung | 100–102 | c | erzeugt und Formular | Stufe 6 |
| 15 | | Kontrollen außerhalb des Systems | 100–102 | b | Formular | – |
| 16 | | Datensicherung, Wiederherstellungstest | 103–106 | c | erzeugt und Formular | – |
| 17 | | Ort der Daten, Betrieb, Updates | § 146 Abs. 2–2b AO | c | erzeugt und Formular | – |
| 18 | | Änderungshistorie der Verfahrensdokumentation | 150, 154 | a | erzeugt | Stufe 6 (Fassungsvergleich) |
| A–D | Anhang | Mitgeltende Unterlagen, Glossar, Fehlende Angaben und Hinweise, Rechtsquellen | 154 | c | erzeugt und Formular | – |

Rz. 160 verlangt, dass die Teile der Verfahrensdokumentation, die einen vollständigen Systemüberblick geben, auf Anforderung vorliegen [S2]; bis Stufe 2 nennt Kapitel 10 als Formularabschnitt, woher dieser Überblick kommt. Alle Kapitel späterer Stufen stehen von Anfang an in der Gliederung, damit nichts unbemerkt fehlt (Frage 7.13).

### 2.3 Lücken, Herkunft, Hinweise

- **Lücke.** „Fehlt: <Angabe> (<Grundlage>)“ steht dort, wo der Wert stünde, etwa „Fehlt: Rechtsform (§ 145 Abs. 1 AO)“. Als Lücke zählen ein Pflichtabschnitt ohne Text, ein fehlender Wert aus dem System (leere Zeitzone, unbekannter Image-Stand, fehlende Registernummer) und ein Fehler beim Erfassen.
- **Hinweisband.** Bei mindestens einer Lücke tragen jede PDF-Seite und der Anfang der Markdown-Datei „Unvollständig: n Angaben fehlen“; Anhang C listet alle. Ohne Lücke entfällt das Band, der Stempel sagt „Fehlende Angaben: 0“ und nie „vollständig“.
- **Herkunft je Absatz.** „Herkunft: abgeleitet aus Buchhaltungseinstellungen (Accounts Settings)“ oder „Herkunft: erklärt von <Name>, zuletzt geändert am <Datum>, geprüft am <Datum>“. Wer was wann geändert hat, kommt aus den Version-Datensätzen des Dokuments (`data.changed`, `data.added`, `data.row_changed`) [S38].
- **Hinweis.** Schwache Einstellungen stehen als „Hinweis:“ neben dem Wert, mit Tatsache und Wirkung und nie mit rechtlicher Wertung, etwa „Das unveränderliche Hauptbuch ist ausgeschaltet. Eine Stornierung kennzeichnet dann auch die ursprüngliche Buchung als storniert.“ Hinweise zählen nicht als Lücke; die Fälle stehen in 4.8.

### 2.4 Stempel

| Angabe | Quelle |
|---|---|
| Zeitpunkt in Europe/Berlin, unabhängig von `System Settings.time_zone` | Uhr des Servers in UTC, umgerechnet |
| Site, Unternehmen | `frappe.local.site`, `Company.company_name` |
| Versionen aller Apps und der Datenbank | `frappe.utils.change_log.get_versions()`, `select version()` [S35, S36] |
| Komponenten-Prüfsumme (SBOM) | SHA-256 über die sortierte Liste aus `frappe.utils.sbom.collector.collect()`: Apps, Python- und npm-Pakete mit Version und Lizenz [S35]. Nicht über eine SPDX-Datei, weil diese vermutlich Erzeugungszeit und Namespace trägt (unbestätigt). |
| Image-Stand | `ERPNEXT_GERMANIZED_VERSION` (Vorschlag in 4.1), sonst „manuell: …“ aus dem Formular, sonst Lücke |
| Version des Generators | `<app>.__version__` und Stand des Textkatalogs |
| SHA-256 der Markdown-Datei | im PDF und im Formular; die Markdown-Datei trägt den Stempel ohne ihre eigene Prüfsumme |
| Fehlende Angaben | Anzahl |
| Freigabe | „Entwurf, nicht freigegeben“ oder „Freigegeben von … am …, gültig ab …“, dazu „fachlich geprüft durch … am …“, wenn erfasst |

### 2.5 Freigabe und Gültigkeit

- **Zustände.** Entwurf, dann Freigegeben. Eine Fassung gilt erst mit Freigabe durch die Geschäftsführung, wie im Muster von BStBK und DStV [S28]. Ersetzt ist eine Fassung, sobald eine spätere freigegeben ist; ihre Gültigkeit endet am Tag vor deren „gültig ab“ und bleibt im Dokument sichtbar [S28, S29].
- **Wer.** Name der freigebenden Person aus der Geschäftsführung, Datum der Freigabe, „gültig ab“. Erfassen darf sie die Person selbst oder ein Accounts Manager in ihrem Auftrag; der erfassende Benutzer wird mitgespeichert (Frage 7.4).
- **Fachlich geprüft.** Ein freiwilliges Feld „fachlich geprüft durch … am …“, etwa für die Steuerberatung. Es belegt einen Ablauf, hat aber keine Rechtswirkung (Rz. 179–181) [S2].
- **Freigabe trotz Lücken.** Nur nach ausdrücklicher Bestätigung im Dialog („Die n fehlenden Angaben sind bekannt“); das Hinweisband bleibt.
- **Gültig ab.** Später als „gültig ab“ der vorigen freigegebenen Fassung. Es darf vor dem Freigabedatum liegen, weil eine Freigabe eine gelebte Praxis bestätigen kann; beide Daten stehen im Dokument.
- **Unveränderlich.** Die Freigabe ändert keine gespeicherte Fassung, sondern legt eine neue an, die auf dem Entwurf beruht (`based_on`) und denselben Inhalt hat (gleiche `body_sha256`). Gespeichert wird die Datei, nicht nur die Daten, weil neuerer Code anders darstellen würde (Rz. 133, 154) [S2].

### 2.6 Jahresstand

Ein täglicher Auftrag friert für jedes Unternehmen jedes Geschäftsjahr ein, dessen Ende mindestens `freeze_after_days` Tage zurückliegt (Vorgabe 30) und das noch keinen Jahresstand hat: Anlass „Jahresstand“, Status Entwurf, Benachrichtigung an die verantwortliche Person mit der Bitte um Prüfung und Freigabe. 30 Tage, weil die Buchungen des letzten Monats bis Ende des Folgemonats im Journal stehen sollen (Rz. 87) [S2; Einschätzung]. Fassungen bleiben gespeichert, bis die Unterlagen ihres letzten Geschäftsjahres nicht mehr aufzubewahren sind [S8]; die App löscht nichts.

### 2.7 „Veraltet“

Seit der letzten Freigabe zählt als Änderung:

1. Version-Datensätze dokumentierter DocTypes mit `track_changes`, etwa Accounts Settings, System Settings, Print Settings, Company, Account, Steuervorlagen, Print Format, Letter Head, Bank Account und Email Account, dazu `ref_doctype` „Series“ (Zählerstände) und „DefaultValue“ (Reihenfolge der Apps) [S38, S40];
2. neue Zeilen im Permission Log [S37, S38];
3. neue Zeilen im Patch Log, also eine Migration mit Patches [S35];
4. andere App-Versionen in Installed Applications oder `get_versions()` als in der Freigabe [S35];
5. ein jüngeres `modified` an dokumentierten Einstellungen ohne `track_changes`: ERPNext Germany Settings, E Invoice Settings, DATEV Unternehmen Online Settings, Banking Settings [S42–S46];
6. geänderte Formularabschnitte des Dokuments.

Das Formular zeigt „Veraltet seit <Datum>“ mit den Gründen; die verantwortliche Person bekommt je neuem Grund eine Benachrichtigung. Grundlage sind die anlassbezogene Prüfung im IKS (Rz. 101) und die lückenlose Änderungshistorie (Rz. 150) [S2].

### 2.8 Mehrere Unternehmen

Ein Dokument je Company. Sammler für Unternehmensdaten filtern nach `company`: Company, Fiscal Year, Accounting Period, Period Closing Voucher, Steuervorlagen, Bank Account, DATEV Settings, VAT Return Settings, Nummernkreise nach Nutzung je Unternehmen. Software, Konfiguration der Site, Scheduler, Sicherungen, Benutzer und Rollen, Druckeinstellungen sowie MCP und Agenten gelten für die ganze Site; sie erscheinen in jedem Dokument mit dem Vermerk „gilt für die ganze Site“. User Permissions auf Company zeigen, wer auf welches Unternehmen beschränkt ist.

### 2.9 Haftungshinweis und verbotene Aussagen

Langfassung in Kapitel 1 und im README:

> Diese Verfahrensdokumentation ist aus den Einstellungen, Protokollen und Versionsständen dieser ERPNext-Installation erzeugt und um die Angaben des Unternehmens ergänzt. Abgeleitete Angaben zeigen, was das System bei der Erzeugung enthielt. Ob die beschriebenen Abläufe im Unternehmen so gelebt werden, kann die Software nicht feststellen. Das Dokument ist eine Arbeitshilfe, keine Rechts- oder Steuerberatung, und ersetzt weder die Prüfung durch die Steuerberatung noch eine Beurteilung durch die Finanzverwaltung. Für Inhalt und Freigabe ist das Unternehmen verantwortlich.

Kurzfassung in der Fußzeile jeder Seite: „Aus ERPNext erzeugt · Arbeitshilfe, keine Rechts- oder Steuerberatung · verantwortlich ist das Unternehmen“.

Nie, weder in Oberfläche, Dokument, README, Dokumentation noch Release-Text: „GoBD-konform“, „GoBD-compliant“, „GoBD-zertifiziert“, „GoBD-geprüft“, „revisionssicher“, „rechtssicher“, „prüfungssicher“, „finanzamtssicher“, „testiert“, „anerkannt“. Die GoBD erscheinen nur als Quelle einer Anforderung („Rz. 153 verlangt …“), nie als Eigenschaft der App oder des Dokuments. Ein Test sucht diese Wörter in Textkatalog, Vorlagen, Übersetzungen und Dokumentation; ausgenommen sind nur Stellen, die sie als unzulässig benennen, wie diese.

## 3. Datenmodell und Pipeline

### 3.1 `Procedure Documentation`

Label „Verfahrensdokumentation“; eine je Company (`autoname: field:company`), `track_changes` 1, damit jede Änderung der Angaben eine Version schreibt [S38]. Die Labels stehen im JSON englisch und kommen über `translations/de.csv` deutsch in die Oberfläche, wie bei Steuerbote [S53].

| Feld | Typ | Label | Bedeutung |
|---|---|---|---|
| `company` | Link Company, Pflicht, eindeutig | Unternehmen | |
| `responsible` | Link User, Pflicht | Verantwortlich | bekommt Hinweise und Jahresstände |
| `review_months` | Int (12) | Überprüfung alle … Monate | regelmäßige Durchsicht neben der anlassbezogenen (Rz. 101) |
| `annual_freeze` | Check (1) | Jahresstand automatisch | |
| `freeze_after_days` | Int (30) | Jahresstand nach … Tagen | |
| `image_version` | Data | Image- oder Installationsstand | gilt, wenn die Umgebungsvariable fehlt |
| `replacing_scanning` | Select („“, Nein, Ja) | Ersetzendes Scannen | Ja macht `belege.scannen` zur Pflicht |
| `data_location` | Select („“, Deutschland, Anderer EU-Mitgliedstaat, Drittstaat) | Ort der Daten | EU frei, Drittstaaten nur mit Bewilligung, die Schweiz in der Regel nicht (§ 146 Abs. 2a–2b AO; AEAO zu § 146 Nr. 4) [S7, S18] |
| `relocation_approval` | Data | Bewilligung nach § 146 Abs. 2b AO | Pflicht bei Drittstaat |
| `print_format` | Link Print Format | Druckformat | Vorgabe: das der App |
| `pdfa` | Check (0) | PDF/A erzeugen | |
| `sections` | Table `Procedure Documentation Section`, `cannot_add_rows`, `cannot_delete_rows` | Angaben des Unternehmens | Zeilen aus dem Textkatalog |
| `stale_since`, `stale_reasons` | Datetime, Small Text, nur lesen | Veraltet seit, Gründe | setzt der tägliche Auftrag mit `frappe.db.set_value(update_modified=False)`, damit keine Version entsteht |

`Procedure Documentation Section` (Tabelle): `key` (Data, nur lesen, etwa `organisation.vertretung`), `chapter` (Data, nur lesen), `title` (Data, nur lesen) „Angabe“, `prompt` (Small Text, nur lesen) „Frage“, `required` (Check, nur lesen) „Pflichtangabe“, `source` (Data, nur lesen) „Grundlage“, `content` (Markdown Editor) „Inhalt“, `reviewed_on` (Date) „Geprüft am“. Neue Schlüssel eines App-Updates ergänzt `after_migrate`; entfallene bleiben mit ihrem Text erhalten und erscheinen in Anhang A, bis jemand den Text leert.

Formularabschnitte, Pflicht, wo nicht „frei“ steht:

| Kap. | Schlüssel |
|---|---|
| 1 | `zweck.geltungsbereich` (frei) |
| 2 | `unternehmen.rechtsform`, `unternehmen.gegenstand`, `unternehmen.gewinnermittlung`, `unternehmen.besteuerung` (Pflicht nur ohne Steuerbote) |
| 3 | `organisation.geschaeftsfuehrung`, `organisation.buchhaltung`, `organisation.vertretung`, `organisation.steuerberatung`, `organisation.dienstleister` |
| 4 | `systeme.vor_nebensysteme` |
| 5 | `prozesse.belegarten` |
| 6 | `belege.eingang`, `belege.papier`, `belege.scannen` (bei ersetzendem Scannen) |
| 9 | `buchungen.automatisch` |
| 10 | `datenlexikon.verweis` (woher der Systemüberblick nach Rz. 160 auf Anforderung kommt) |
| 11 | `versionen.vorher` (Pflicht, wenn das erste Patch Log älter ist als die Installation der App) |
| 12 | `aufbewahrung.verfahren` |
| 13 | `migration.altsysteme` |
| 14 | `zugaenge.vergabe`, `zugaenge.funktionstrennung` |
| 15 | `kontrollen.abstimmungen`, `kontrollen.freigaben`, `kontrollen.ueberpruefung` |
| 16 | `sicherung.verfahren`, `sicherung.wiederherstellung` |
| 17 | `betrieb.hosting`, `betrieb.updates`, `betrieb.zugang` |
| Anhang A | `anhang.unterlagen` (frei) |
| jedes | `<kapitel>.ergaenzung` (frei) |

### 3.2 `Procedure Documentation Version`

Label „Fassung der Verfahrensdokumentation“, in der Liste „Fassungen“. Nur Einfügen, nach dem Muster von Steuerbotes `VAT ID Confirmation`: `in_create` 1, keine Rolle mit write, create oder delete, `validate()` wirft außer bei `is_new()`, `on_trash()` wirft immer, Einfügen nur serverseitig mit `ignore_permissions=True` nach eigener Rechteprüfung, Dateischutz über `doc_events["File"]` (`validate`, `on_trash`), weil `File.has_permission` dem Eigentümer einer Datei das Löschen erlaubt [S38, S48, S53]. `autoname: format:VD-{#####}`.

| Gruppe | Felder (Typ) |
|---|---|
| Zuordnung | `company` (Link Company) · `procedure_documentation` (Link) · `version_no` (Int, fortlaufend je Unternehmen) · `reason` (Select: Freigabe, Jahresstand, Änderung, Manuell) · `status` (Select: Entwurf, Freigegeben) · `fiscal_year` (Link Fiscal Year, beim Jahresstand) · `based_on` (Link, der freigegebene Entwurf) · `previous` (Link, vorige Fassung des Unternehmens) |
| Erzeugung | `generated_at` (Datetime) · `generated_by` (Link User) · `site` (Data) · `generator_version` (Data) · `app_versions` (JSON) · `components_sha256` (Data) · `image_version` (Data) · `image_version_source` (Select: Umgebung, Manuell, Unbekannt) · `print_format` (Data) · `print_format_sha256` (Data, über `html` und `css`) · `pdf_generator` (Data) |
| Inhalt | `markdown_text` (Long Text, verborgen; Quelle des Druckformats) · `markdown` (Attach, private Datei) · `pdf` (Attach, private Datei) · `report` (JSON: je Abschnitt Schlüssel, Kapitel, Status ok, fehlt oder Fehler, Herkunft, Sammler, SHA-256, Lücken, Hinweise, `volatile`; dazu die Komponentenliste) · `missing_count`, `error_count`, `finding_count` (Int) · `changed_sections` (Small Text) |
| Prüfsummen | `markdown_sha256` (Datei) · `body_sha256` (Inhalt ohne Stempel) · `pdf_sha256` · `report_sha256` (kanonisches JSON) · `previous_chain_sha256` · `chain_sha256` (alle Data) |
| Freigabe | `released_by` (Data, Person der Geschäftsführung) · `released_on` (Date) · `valid_from` (Date) · `reviewed_by` (Data, fachlich geprüft durch) · `reviewed_on` (Date) · `gaps_acknowledged` (Check) · `release_note` (Small Text) · `recorded_by` (Link User) |
| Berechnet | `valid_until` (Date, virtuell) · `superseded_by` (Link, virtuell) |

**Hash-Kette.** `chain_sha256` ist SHA-256 über `previous_chain_sha256` (beim ersten Glied 64 Nullen), `company`, `version_no`, `status`, `markdown_sha256`, `pdf_sha256`, `report_sha256` und die Freigabefelder, zeilenweise verbunden. `File.content_hash` ist ein MD5 zur Deduplizierung, deshalb eigene SHA-256 [S38]. Administrator kann Version-Datensätze löschen, System Manager Deleted Documents, ein Datenbankadministrator alles [S38]; die Kette macht das Löschen einer Fassung sichtbar. „Kette prüfen“ berechnet alle Glieder aus den gespeicherten Dateien neu und meldet die erste Lücke in `version_no` oder das erste falsche Glied.

**Einfrieren.** Unter einer Zeilensperre auf das Dokument des Unternehmens (`for_update`), damit Nummern und Kette linear bleiben: sammeln, Markdown erzeugen, Fassung mit Markdown, Bericht und deren Prüfsummen einfügen, PDF aus der gespeicherten Fassung drucken, Dateien anhängen und `pdf`, `pdf_sha256` und `chain_sha256` in derselben Transaktion mit `frappe.db.set_value(update_modified=False)` setzen, so wie Steuerbote `response_file` einer `VAT ID Confirmation` nachträgt [S53]. Danach verbietet `validate()` jede Änderung.

**Optional: `Software Version Log`.** Ein dritter, ebenfalls nur einfügender DocType hält die Programmidentität zwischen zwei Fassungen fest (Frage 7.14): `recorded_at` (Datetime), `trigger` (Select: Installation, Migration, Täglich), `app_versions` (JSON), `components_sha256`, `image_version`, `python_version`, `os_release`, `mariadb_version` (Data), `previous` (Link), `changes` (Small Text). Geschrieben von `after_install`, `after_migrate` und dem täglichen Auftrag, nur bei Änderung.

### 3.3 Pipeline

1. **Sammeln.** `collect(company, as_of)` ruft jeden Pfad aus `frappe.get_hooks("procedure_documentation_sections")` auf, die eingebauten Sammler eingeschlossen [S41, S48].
2. **Zusammenführen.** Formularabschnitte kommen über `key` dazu; ein Pflichtschlüssel ohne Text wird „Fehlt:“. Doppelte Schlüssel und unbekannte Kapitel werden Fehlerabschnitte.
3. **Darstellen.** Deterministisches Markdown, HTML mit `frappe.utils.md_to_html`, PDF mit `frappe.get_print` und dem Druckformat der Fassung; PDF/A optional [S39].
4. **Vorschau.** Dasselbe ohne Speichern, mit Leserecht.
5. **Einfrieren und Freigeben.** Für System Manager und Accounts Manager, als Hintergrundauftrag in der Queue `long` mit `job_id` je Unternehmen, damit zwei Klicks keine zwei Fassungen erzeugen.
6. **Vergleichen.** Der Bericht nennt die Abschnitte, deren SHA-256 sich gegenüber der vorigen Fassung geändert hat; Protokollstatistiken (`volatile`) zählen nicht.

### 3.4 Beitrags-Hook

Jede App kann Abschnitte beitragen. `frappe.get_hooks(key)` hängt die Listen aller installierten Apps in Installationsreihenfolge aneinander; ERPNext nutzt dasselbe Muster für `get_matching_queries`, das banking füttert [S41, S46].

```python
# hooks.py der beitragenden App
procedure_documentation_sections = ["meine_app.gobd.sections"]


# meine_app/gobd.py
from datetime import datetime


def sections(company: str, as_of: datetime) -> list[dict]:
	return [
		{
			"key": "meine_app.einstellungen",  # eindeutig, mit App-Präfix
			"chapter": "4",  # "1" bis "18" oder "A" bis "D"
			"title": "Einstellungen von Meine App",
			"rows": [["Einstellung", "Wert"], ["Versand", "ein"]],  # oder "markdown": "…"
			"missing": ["Fehlt: Empfänger der Belege"],
			"sources": ["GoBD Rz. 111"],
			"scope": "company",  # oder "site"
			"volatile": False,  # True für Protokollstatistik
		}
	]
```

- Eine Ausnahme wird ein Abschnitt mit Status „Fehler“ und ein Eintrag im Error Log (`frappe.log_error`), dessen Name im Abschnitt steht, die Fehlermeldung selbst nicht, weil sie Daten enthalten kann. Ebenso ein Ergebnis in falscher Form. Fehler zählen als Lücke.
- Adapter für fremde Apps lesen nur über DocType-Namen, wenn die App installiert ist (`frappe.get_installed_apps()`), und importieren nichts aus ihr [S42–S47]. Beiträge eigener Apps wie Steuerbote stehen in deren `hooks.py` und wirken nur, wenn diese App installiert ist.
- Beitragende maskieren selbst; die Hilfsfunktionen aus 3.6 gehören zur öffentlichen Schnittstelle.

### 3.5 Sammler je Kapitel

Feldnamen geprüft [S35–S48], außer wo „unbestätigt“ steht; „Erklärt“ verweist auf die Formularabschnitte aus 3.1.

| Kap. | Abgeleitet aus | Erklärt |
|---|---|---|
| 1 | Fassung (`version_no`, `status`, `reason`, Freigabe, `valid_from`, `valid_until`), `frappe.local.site`, `Company.company_name`; Lesehinweis (Rz. 148, 151) und Haftungshinweis aus dem Textkatalog | Geltungsbereich, Abgrenzung |
| 2 | Company: `company_name`, `abbr`, `tax_id`, `country`, `default_currency`, `chart_of_accounts`, `create_chart_of_accounts_based_on`, `existing_company`, `enable_perpetual_inventory` (1), `valuation_method`, `default_letter_head`, `round_off_account`, `default_*_account`; erpnext_germany: `register_type`, `register_number`, `register_court`; Fiscal Year: `year`, `year_start_date`, `year_end_date`, `disabled`, `is_short_year`, `companies`; Kontenplan: Herkunft aus `chart_of_accounts` („SKR03 mit Kontonummern“, „SKR04 mit Kontonummern“, leer bei Kopie aus `existing_company`), Abweichung als Vergleich der `account_number` mit `verified/de_kontenplan_SKR03.json` bzw. `…SKR04.json`, je abweichendem Konto `account_name`, `parent_account`, `root_type`, `account_type`, `tax_rate`, `disabled`, `account_category`; Steuerbote: VAT Return Settings `chart`, `taxation_type`, `tax_number`, `tax_office`, `ust_idnr` | Rechtsform, Gegenstand, Gewinnermittlung, Besteuerung |
| 3 | `responsible` | alle Angaben |
| 4 | Apps in Installationsreihenfolge (`frappe.get_installed_apps(_ensure_on_bench=True)`), Versionen (`get_versions()`: `title`, `description`, `version`), Komponenten (`collect()`: `Inventory.apps`, `.packages`, `.dependencies`); Plattform: `platform.python_version()`, `platform.freedesktop_os_release()`, MariaDB `select version()` und `show variables like 'log_bin'`, Redis `INFO SERVER` (`redis_version`, unbestätigt), PDF-Werkzeuge; Image-Stand; E-Mail: Email Account `email_account_name`, `email_id`, `enable_outgoing`, `default_outgoing`, `smtp_server`, `smtp_port`, `use_tls`, `enable_incoming`, `append_to`, dazu `System Settings.store_attached_pdf_document` (1); Druck: Print Settings `send_print_as_pdf` (1), `pdf_generator` (chrome), `allow_print_for_draft` (1), `add_draft_heading` (1), `allow_print_for_cancelled` (0); Bank Account `account_name`, `bank`, `iban`, `account`, `company`, `is_company_account`, `disabled`, `integration_id`, `last_integration_date`; Webhook `request_url`; Data Import (Anzahl je DocType); erpnext_datev: DATEV Settings `client_number`, `consultant`, `consultant_number`, `account_number_length`, `temporary_against_account_number`, DATEV Unternehmen Online Settings `enabled`, `sender`, `datev_voucher_config` (`voucher_type`, `print_format`, `recipient`, `attach_print`, `attach_files`); eu_einvoice: E Invoice Settings `validate_sales_invoice_on_save`, `validate_sales_invoice_on_submit`, `error_action_on_save`, `error_action_on_submit`, `auto_attach_xml`, E Invoice Import (`einvoice`, `supplier`, `profile`, `validation_errors`, `e_invoice_is_correct`); banking: Banking Settings `enabled`, `customer_id`, `admin_endpoint`, `enable_ebics`, EBICS User `bank`, `partner_id`, `user_id`, EBICS Request `order_type`, `status`, SEPA Payment Order `transmission_type`, `transmission_datetime`, Bank Reconciliation Rule (Anzahl); Steuerbote: ERiC Settings `simulation`, `hersteller_id`, `installed_version`, `archive_sha256` | Vor- und Nebensysteme mit Datenfluss |
| 5 | ab Stufe 3 (Abschnitt 5) | Prozesse je Belegart |
| 6 | Verweis auf Kap. 8 (geschützte Anhänge, PDF beim Buchen, E-Rechnungs-Originale) | Eingang, Papier, Scannen |
| 7 | Nummernkreise je DocType (`frappe.get_meta(dt).get_naming_series_options()`, etwa `ACC-SINV-.YYYY.-`, `ACC-PINV-.YYYY.-`, `ACC-JV-.YYYY.-`, `ACC-PAY-.YYYY.-`), Zähler (`tabSeries`: `name`, `current`), genutzte Kreise je Unternehmen (`group_by="naming_series"`), Zähleränderungen (Version mit `ref_doctype` „Series“), `default_amend_naming`, Document Naming Rule; erpnext_germany `prevent_gaps_in_transaction_naming` (1); `Company.abbr`; Sales und Purchase Taxes and Charges Template (`title`, `company`, `is_default`, `disabled`, `tax_category`, `taxes`), Item Tax Template (`taxes`: `tax_type`, `tax_rate`, `not_applicable`), Tax Rule (`tax_type`, `sales_tax_template`, `purchase_tax_template`, `tax_category`, `priority`, `from_date`, `to_date`); Mode of Payment (`mode_of_payment`, `type`, `enabled`, `accounts`: `company`, `default_account`); Payment Terms Template (`template_name`, `terms`) | Kürzel außerhalb des Systems (frei) |
| 8 | Accounts Settings: `enable_immutable_ledger` (0), `delete_linked_ledger_entries` (0), `book_tax_discount_loss`, `role_allowed_to_over_bill`, `allow_multi_currency_invoices_against_single_party_account`, `enable_common_party_accounting`, `unlink_payment_on_cancellation_of_invoice` (1), `check_supplier_invoice_uniqueness` (0), `add_taxes_from_item_tax_template` (1), `merge_similar_account_heads`, `round_row_wise_tax`, `repost_allowed_types`; Company `accounts_frozen_till_date`, `role_allowed_for_frozen_entries`; `Account.freeze_account`; Accounting Period (`start_date`, `end_date`, `company`, `closed_documents`: `document_type`, `closed`; `exempted_role`); Period Closing Voucher (`fiscal_year`, `period_start_date`, `period_end_date`, `closing_account_head`, `gle_processing_status`), Process Period Closing Voucher, Account Closing Balance; Repost Accounting Ledger (`company`, `vouchers`, `delete_cancelled_entries`, `status`), jeder Lauf; Ledger Health Monitor (`enable_health_monitor` (0), `debit_credit_mismatch`, `general_and_payment_ledger_mismatch`); Transaction Deletion Record (`company`, `status`, `doctypes`: `doctype_name`, `no_of_docs`); Deleted Document (`deleted_doctype`, `restored`; Anzahl je DocType und Jahr); `frappe.get_meta(dt).track_changes` je dokumentiertem DocType und Anzahl der Version-Datensätze je `ref_doctype`; Log Settings (`logs_to_clear`: `ref_doctype`, `days`); erpnext_germany: Property Setter `protect_attached_files` (22 DocTypes); pdf_on_submit: PDF on Submit Settings `create_pdf_in_background` (1), `enabled_for` (`document_type`, `print_format`, `letter_head`, `auto_name`, `filters`), Abdeckung als gebuchte Belege mit PDF; eu_einvoice: Purchase Invoice `e_invoice_import`, `supplier_invoice_file`, Sales Invoice `einvoice_profile`, `einvoice_is_correct` | frei |
| 9 | ab Stufe 4 | automatische Buchungen |
| 10 | ab Stufe 2 | Herkunft des Systemüberblicks |
| 11 | Zeiträume aus den Fassungen (`app_versions`, `components_sha256`, `image_version`) und, falls vorhanden, aus `Software Version Log`; Patch Log (`patch`, `skipped`, `creation`, nie `traceback`) als datierte Migrationen je App; Version mit `ref_doctype` „DefaultValue“; Änderungen dokumentierter Einstellungen seit der vorigen Fassung aus Version (`data.changed`: Feld, alt, neu, mit Datum und Benutzer; Rz. 111); Anpassungen mit Änderungsdatum: Custom Field, Property Setter, Client Script, Server Script (`server_script_enabled`), Workflow, Notification, Webhook, Report (`is_standard` „No“), Auto Repeat, Document Naming Rule; Druckformate: Standard je DocType (`frappe.get_meta(dt).default_print_format`, sonst „Standard“), Print Format (`doc_type`, `disabled`, `standard`, `pdf_generator`, SHA-256 über `html` und `css`), Letter Head (`is_default`) | frühere Versionsstände |
| 12 | erpnext_germany: GDPdU Export (`company`, `from_date`, `to_date`, `exported_doctypes`, `export_file`, `status`); Steuerbote: ELSTER Transmission (`document`, `operation`, `status`, `outcome`, `simulated`, `transferticket`, `eric_version`, Dateien `xml`, `protocol_pdf`, `response_xml`), VAT ID Confirmation (Anzahl, Antworten als private Dateien); mehr ab Stufe 5 | Aufbewahrung, Formate, Datenzugriff |
| 13 | ab Stufe 5 | Altsysteme, Übernahme |
| 14 | User mit `user_type` System User einzeln, Website-Benutzer gezählt: `enabled`, `user_type`, `roles` (Has Role `role`), `role_profile_name`, `role_profiles`, `module_profile`, `block_modules`, `creation`, `last_login`, `last_active`, `simultaneous_sessions`, `login_after`, `login_before`, `restrict_ip`, API-Zugang (`api_key` gesetzt); User Permission auf Company; Rechte je Rolle und DocType (`frappe.get_meta(dt).permissions`, Abweichung `permission_manager.get_permissions(doctype)` gegen `get_standard_permissions(doctype)`, Rechte `read` bis `delete`, `report`, `export`, `import`, `print`, `email`, `share`, `select`, `mask`, `if_owner`, `permlevel`); Permission Log (`changed_by`, `changed_at`, `changes`, `for_doctype`, `for_document`, `status`); System Settings `enable_password_policy` (1), `minimum_password_score` (2), `force_user_to_reset_password`, `allow_consecutive_login_attempts` (10), `allow_login_after_fail` (60), `enable_two_factor_auth` (0), `two_factor_method`, `bypass_2fa_for_retricted_ip_users`, `session_expiry` (170:00), `deny_multiple_sessions`, `disable_user_pass_login`, `login_with_email_link` (1), `log_api_requests` (0), `allow_error_traceback` (1), Role `two_factor_auth`; Activity Log (`operation` Login, Logout, Impersonate, `status`, `user`, `communication_date`) als Summen, Impersonate einzeln; Access Log (`export_from`, `user`, `timestamp`, `reference_document`, `file_type`, `report_name`, `method`, `filters`); MCP und Agenten: `System Settings.enable_mcp` (1), Flow Provider (`provider`, `enabled`, `base_url`), Flow Agent (`enabled`, `model`, `roles`), Flow Trigger (`enabled`, `agent`, `target_doctype`, `doc_event`, `run_as`, `last_fired_at`); hrms: HR Settings `expense_approver_mandatory_in_expense_claim`, `prevent_self_expense_approval`, Payroll Settings `email_salary_slip_to_employee`, `encrypt_salary_slips_in_emails`; Steuerbote: Deadline Reminder | Vergabe und Entzug, Funktionstrennung |
| 15 | – | Abstimmungen, Freigaben, Überprüfung |
| 16 | Dateien unter `get_backup_path()` (`private/backups`): Name `YYYYMMDD_HHMMSS-<site_slug>` mit `-database.sql.gz`, `-files`, `-private-files` oder `-site_config_backup.json`, `-enc` bei Verschlüsselung; daraus Zeitpunkt, Art, Größe, Änderungszeit und Anzahl der Sätze, ohne eine Datei zu öffnen; System Settings `backup_limit` (3), `encrypt_backup`; Site-Konfiguration `backup_encryption_key` (nur ob gesetzt), `backup` (Includes und Excludes als DocType-Namen), `backup_path`, `keep_backups_for_hours`; System Health Report `onsite_backups`, `backups_size`; Access Log der Sicherungs-Downloads | Verfahren, Ziel ohne Zugangsdaten, Wiederherstellungstest |
| 17 | Scheduler: `is_scheduler_disabled()` (`disable_scheduler`, `System Settings.enable_scheduler`), `is_scheduler_inactive()` (`maintenance_mode`, `pause_scheduler`), `get_scheduler_status()`, Scheduled Job Type (`method`, `frequency`, `stopped`, `last_execution`), Scheduled Job Log (`status`); `System Settings.time_zone`, `get_system_timezone()`; Site-Konfiguration aus `frappe.get_site_config()` und `frappe.get_common_site_config()` getrennt (4.2); System Health Report `database_version`, `binary_logging`, `failed_logins`, `failing_scheduled_jobs`, `top_errors` (nur Anzahl); Error Log (Anzahl) | Ort der Daten (`data_location`, `relocation_approval`), Updates, Server- und Datenbankzugang |
| 18 | alle Fassungen des Unternehmens (`version_no`, `generated_at`, `reason`, `status`, Freigabe, Gültigkeit, `missing_count`, `markdown_sha256`, `chain_sha256`, `changed_sections`); Änderungen der Formularabschnitte aus Version (`data.changed`, `data.added`, `data.row_changed`) mit Datum, Kapitel, Inhalt und Bearbeiter, wie die Änderungshistorie im Muster von BStBK und DStV [S28]; Ergebnis der Kettenprüfung | – |
| A–D | Glossar und Rechtsquellen aus dem Textkatalog; Anhang C aus Lücken und Hinweisen | Mitgeltende Unterlagen |

### 3.6 Maskierung

| Regel | Felder |
|---|---|
| Wert nie lesen oder ausgeben | jedes Feld vom Typ Password, besonders `password` und `api_secret` (Email Account, User), `keyring` und `passphrase` (EBICS User), `statement_password` (Bank Account), `webhook_secret` (Webhook), `api_token` und `fintech_license_key` (Banking Settings), `proxy_password` (ERiC Settings); `encryption_key` und `backup_encryption_key` der Site-Konfiguration; der Inhalt von `-site_config_backup.json`; `Deleted Document.data`; Texte aus Error Log und `Patch Log.traceback`; IP-Adressen (`last_ip`, `ip_address`) |
| Nur „gesetzt“ oder „nicht gesetzt“ | `api_key`, `encryption_key`, `backup_encryption_key`, `restrict_ip`, Banking `customer_id`, EBICS `partner_id` und `user_id`, `Bank Account.integration_id` |
| Gekürzt | IBAN auf die letzten vier Zeichen: `Bank Account.iban`, eu_einvoice `payee_iban` [S44]; der Empfänger von DATEV Unternehmen Online (`recipient`) als erster Buchstabe und Domain, weil die Adresse Uploads in den DATEV-Bestand des Mandanten annimmt (unbestätigt) [S43] |
| Ausgeben | Steuernummer (steht ohnehin auf Rechnungen), USt-IdNr., Mandanten- und Beraternummer als Kennungen [S43, S48] |

Durchgesetzt wird das dreifach: mit Hilfsfunktionen im Kern; mit einem Kanarientest, der bekannte Geheimwerte in die Testsite schreibt und sie in Markdown, PDF-Text und Bericht sucht; mit einem Quelltexttest, der Aufrufe von `get_decrypted_password`, `get_password` und `get_encryption_key` sowie das Öffnen von Dateien unter `private/backups` verbietet. `get_encryption_key()` legt einen fehlenden Schlüssel sogar an [S36].

### 3.7 Darstellung und Ablage

- **Markdown.** Gleiche Daten ergeben dieselben Bytes: Zeilen nach festen Schlüsseln sortiert, keine Uhrzeit außer im Stempel, UTF-8 in NFC, LF, Datenwerte maskiert (`|`, `*`, `#`, `<`, `>`, `&`). Text aus dem Formular: Überschriften unter die Ebene des Abschnitts verschoben, rohes HTML maskiert. Dateiname `verfahrensdokumentation-<abbr>-fassung-<n>.md`.
- **HTML.** `frappe.utils.md_to_html()` mit markdown2 2.5.5 (Tabellen, Inhaltsverzeichnis, Code-Blöcke) [S39]. Ob es rohes HTML entschärft, ist unbestätigt, deshalb maskiert die App vorher. Das Druckformat ruft eine Funktion der App über den Hook `jinja` auf.
- **PDF.** `frappe.get_print(doctype, name, print_format, as_pdf=True, pdf_generator=None)` nimmt das Argument, dann `pdf_generator` des Druckformats, dann `Print Settings.pdf_generator` (chrome), dann wkhtmltopdf; im Image stehen wkhtmltopdf, chrome, PlutoPrint, Typst und WeasyPrint bereit. `frappe.utils.pdf.get_pdf()` nutzt immer wkhtmltopdf und scheidet aus [S39]. Hinweisband und Haftungshinweis als Kopf- und Fußzeile des Druckformats; ob chrome sie auf jeder Seite setzt, ist unbestätigt.
- **PDF/A.** Mit Ghostscript im Image möglich [S39]; eu_einvoice braucht dafür das Profil `srgb.icc`, das der Site-Test von erpnext_germanized prüft [S54]. Optional je Dokument (`pdfa`).
- **Dateien.** Private Datei über `frappe.get_doc({"doctype": "File", "file_name": …, "attached_to_doctype": …, "attached_to_name": …, "is_private": 1, "content": …}).insert()`, wie Frappes SBOM und Steuerbote [S38, S48].

### 3.8 Rechte

| | System Manager | Accounts Manager | Accounts User | Auditor |
|---|---|---|---|---|
| Procedure Documentation | lesen, schreiben, anlegen, drucken, exportieren | wie System Manager | lesen, drucken | lesen, drucken |
| Procedure Documentation Version | lesen, drucken, exportieren, Bericht | wie System Manager | lesen, drucken | lesen, drucken, exportieren |
| Vorschau, Kette prüfen | ja | ja | ja | ja |
| Einfrieren, Freigeben | ja | ja | nein | nein |

Niemand legt Fassungen an, ändert oder löscht sie; niemand löscht ein Dokument mit Fassungen. Leiste, Seitenleiste und Arbeitsbereich sehen dieselben vier Rollen.

### 3.9 Hooks, Aufträge, Oberfläche

| Baustein | Inhalt |
|---|---|
| `procedure_documentation_sections` | die eingebauten Sammler, über denselben Hook wie fremde Beiträge |
| `doc_events["File"]` | `validate` und `on_trash` werfen für gespeicherte Dateien einer Fassung |
| `company_data_to_be_ignored` | `Procedure Documentation`, `Procedure Documentation Version`; sonst löscht „Delete Company Transactions“ sie mit `frappe.db.delete` an `on_trash` vorbei [S53] |
| `scheduler_events["daily"]` | „veraltet“ prüfen und benachrichtigen, fällige Jahresstände einfrieren, Softwarestand vergleichen |
| `after_install`, `after_migrate` | Softwarestand festhalten, neue Formularabschnitte ergänzen; werfen nie, Fehler gehen ins Error Log, damit keine Migration scheitert |
| Whitelist | `preview(company)`, `download_markdown(company)`, `freeze(company)`, `release(company, version, released_by, released_on, valid_from, reviewed_by, reviewed_on, gaps_acknowledged, release_note)`, `verify_chain(company)`, `check_staleness(company)` |
| Oberfläche | Dock `<app>/dock/<app>/<app>.json` mit `mount_on: erpnext` und dem Eintrag „Verfahrensdoku“; Seitenleiste mit „Übersicht“, „Dokumentationen“, „Fassungen“, „Softwarestände“ (je höchstens 20 Zeichen); Arbeitsbereich „Verfahrensdokumentation“; `add_to_apps_screen` mit `has_permission`; Symbol über `app_include_icons` [S48, S53] |
| Fixtures | Property Setter für das Standard-Druckformat der Fassung, nach Modul gefiltert; Frappe lehnt `default_print_format` in einem Standard-DocType ab [S53] |
| Übersetzung | `translations/de.csv` für die Oberfläche; der Text des Dokuments kommt aus dem deutschen Textkatalog und hängt nicht an der Übersetzung |

### 3.10 Tests

- **Kern ohne Bench** (`pytest`, 100 % Zweigabdeckung, `fail_under = 100`): Golden-Dateien Byte für Byte, Prüfsummen gegen bekannte Werte, Kette (intakt, Lücke, verändert, vertauscht), Lückenzählung und Mehrzahl, Maskierung, Gültigkeitszeiträume, fällige Jahresstände (Rumpfjahr, Schaltjahr), Regeln für „veraltet“, verbotene Wörter, jede Katalogangabe mit Quelle, jede Gliederungszeile mit Klasse und Stufe, jeder Formularabschnitt mit Frage.
- **Frappe** (`IntegrationTestCase` aus `frappe.tests`, `bench run-tests --app <app>`, wie Steuerbote [S48]): Sammler gegen ein Testunternehmen mit gesetzten Einstellungen; Kanarientest; Beiträge über gepatchtes `frappe.get_hooks` (gültig, Ausnahme, falsche Form, doppelter Schlüssel); Golden-Kapitel 2, 7 und 8 mit festem Stempel; Unveränderlichkeit (Ändern, Löschen, Dateien ändern und löschen, auch als Eigentümer und als System Manager, Anlegen über REST); Kettenprüfung nach `frappe.db.delete`; Rechte je Rolle; Freigabe (ohne Bestätigung bei Lücken, „gültig ab“ zu früh, Gültigkeit der ersetzten Fassung); „veraltet“ (Accounts Settings, Patch Log, App-Version); Jahresstand (einmal, nicht doppelt, Benachrichtigung); zwei Unternehmen; „Delete Company Transactions“; Übersetzungen; Arbeitsbereich und Leiste.
- **Browser** wie Steuerbote (Playwright mit Chromium gegen die Testsite, Daten über `bench execute …seed.run`) [S53]: Vorschau, Freigabedialog mit Bestätigung der Lücken, Fassung herunterladen.
- **CI** wie Steuerbote: pre-commit, Kern ohne Bench, Frappe-Site mit ERPNext version-16 und gepinntem `frappe-bench`, semgrep mit den Frappe-Regeln an fester Revision, Security mit gitleaks, zizmor, pip-audit und CodeQL [S53]. Dazu ein Job mit den Pins von erpnext_germanized, damit die Adapter gegen die ausgelieferten Versionen laufen: Frappe-Tag aus der Zeile `ARG FRAPPE_BRANCH=` im `Containerfile`, die Apps mit `jq -r '.[] | "\(.url) \(.branch)"'` aus `apps.json`, die App selbst aus dem Checkout [S33, S54]. Ziel unter 30 Minuten, sonst nächtlich und bei Änderungen an Adaptern.
- **PDF.** Steuerbotes CI installiert keinen PDF-Generator und prüft Drucke als HTML [S48]; der PDF-Test gehört als neuer Schritt in `tests/site/run.sh` von erpnext_germanized (`bench --site … execute <app>.smoke.pdf`, nur mit `allow_tests`) [S33].

### 3.11 Code-Aufbau und Regeln

Reiner Kern `<app>/core` ohne Frappe-Import: Abschnittsmodell, Gliederung, Zusammenführung, Markdown, Stempel, Lücken, Hash-Kette, Maskierung, Gültigkeit, Jahresstand, „veraltet“, Hinweisregeln und der deutsche Textkatalog, in dem jede Angabe ihre Rechtsquelle trägt. Frappe-Schicht: `<app>/collectors`, das Modul `verfahrensdokumentation` mit den DocTypes, `hooks.py`. Regeln wie bei Steuerbote: Dokumentation, Oberfläche, Issues und Pull Requests deutsch, Code und Commits englisch; Test zuerst; Quelle im Code; Geld als `Decimal`; keine echten Daten in Tests; ruff mit Tabs und 110 Zeichen, pre-commit, Dependabot, exakt gepinnte Entwicklungswerkzeuge [S53].

## 4. Was Frappe und die Apps heute liefern und wo Lücken sind

Die Feldlisten stehen in 3.5; hier geht es um Verhalten, Vorgaben und Lücken.

### 4.1 Software und Programmidentität

| Nachweis | Verhalten | Lücke |
|---|---|---|
| Apps, Reihenfolge | globaler Default `installed_apps`; Umsortieren schreibt eine Version (`ref_doctype` „DefaultValue“) | – |
| Versionen | `get_versions()` liefert `version` aus `frappe.get_attr(app + ".__version__")`; das Single Installed Applications (`app_name`, `app_version`, `git_branch`) wird bei Installation und Migration neu geschrieben | `branch` kommt aus Git und bleibt im Image leer |
| Komponenten, Lizenzen | Frappe 16 baut aus `collect()` ein SPDX-2.3-SBOM und die Seite `/attribution`; `generate_sbom()` (System Manager) hängt eine private SPDX-Datei an Installed Applications | interne API: kapseln, sonst `__version__` |
| Upgrade-Historie | Patch Log mit datierten Zeilen je Migration | eine Migration ohne neue Patches hinterlässt keine Zeile [Einschätzung] |
| Plattform | Python 3.14.10, Debian trixie; MariaDB-Version und Binärlog wie im System Health Report; plutoprint 0.22.0, typst 0.15.2, weasyprint 70.0, chromium-headless-shell, wkhtmltopdf, Ghostscript | Redis-Schlüssel `redis_version` im Quelltext nicht gelesen (unbestätigt) |
| Image-Stand | nur das OCI-Label `org.opencontainers.image.version` | im Container nicht lesbar: `.git` wird beim Bau entfernt (Installed Applications zeigt „UNVERSIONED“), `sites/apps.json` liegt auf dem Volume `sites` [S33–S35]. Vorschlag: `ENV ERPNEXT_GERMANIZED_VERSION=${VERSION}` neben die Labels, die schon hinter dem letzten `RUN` stehen, damit eine neue Version keine Schicht neu baut [S54] |
| Scheduler | `is_scheduler_disabled()`, `is_scheduler_inactive()`, `get_scheduler_status()` | `is_schduler_process_running()` (sic) prüft eine Sperre unter `<bench>/config`, die kein anderer Container sieht; deshalb `Scheduled Job Type.last_execution`. `scheduler_status` des System Health Report zeigt aus einem Web-Pod vermutlich „Process Not Found“ (unbestätigt) |
| Zeitzone | `System Settings.time_zone`, `get_system_timezone()` | leer fällt auf „Asia/Kolkata“ zurück |

Quellen: [S35, S36].

### 4.2 Konfiguration der Site

`frappe.get_site_config()` und `frappe.get_common_site_config()` getrennt lesen, um die Herkunft zu nennen; nur Schlüssel einer Positivliste ausgeben [S35, S36].

| Schlüssel | Gelesen von | Ausgabe |
|---|---|---|
| `encryption_key` | `get_encryption_key()` legt einen an, wenn er fehlt | nur ob vorhanden, über `"encryption_key" in frappe.local.conf`; den Getter nie aufrufen |
| `backup_encryption_key`, `backup` (Includes, Excludes), `backup_path`, `keep_backups_for_hours` | `utils/backups.py` | ob vorhanden; DocType-Namen der Includes und Excludes |
| `developer_mode`, `allow_tests`, `maintenance_mode`, `pause_scheduler`, `disable_scheduler`, `mute_emails`, `ignore_csrf`, `allow_cors`, `deny_multiple_sessions` | `__init__.py`, `app.py`, `auth.py`, `utils/scheduler.py` | ein oder aus |
| `server_script_enabled` | `is_safe_exec_enabled()`, nur aus common_site_config | ein oder aus |

### 4.3 Buchhaltung

- **Nicht mehr in v16:** `enable_audit_trail`, `acc_frozen_upto` und `frozen_accounts_modifier` (heute `Company.accounts_frozen_till_date` und `role_allowed_for_frozen_entries`), ein Bericht „Audit Trail“ in ERPNext, `attach_print_as_pdf` sowie die Sicherungs-DocTypes für Dropbox, S3 und Google Drive, die in die App `offsite_backups` gewandert sind; sie ist nicht im Image [S36, S37, S40].
- **Audit Trail** ist in Frappe ein Single (`doctype_name`, `document`, `start_date`, `end_date`), das bis zu fünf Änderungsstände eines Dokuments vergleicht: ein Werkzeug, nichts zu sammeln [S37, S38]. Änderungen belegen die Version-Datensätze, das Permission Log und die Protokolle aus 4.4.
- **Festschreibung** ist in ERPNext das Buchen (Submit) plus unveränderliches Hauptbuch, geschlossene Accounting Periods, `accounts_frozen_till_date` und Period Closing Voucher; eine neue Site hat nur das Buchen [S40, S41].
- **Unveränderliches Hauptbuch** (`enable_immutable_ledger`, Vorgabe 0): Eingeschaltet bucht ein Storno die Gegenbuchung zum Stornodatum, die Originale bleiben, stornierte Belege lassen sich nicht löschen; ausgeschaltet bekommen beide `is_cancelled` 1 [S40, S41].
- **Repost Accounting Ledger** baut das Hauptbuch gebuchter Belege nach dem letzten Period Closing Voucher neu auf; jeder Lauf gehört in die Dokumentation [S40, S41].
- **Nummernkreise:** Zähleränderungen schreiben eine Version (`ref_doctype` „Series“); das Löschen des jüngsten Belegs setzt den Zähler zurück (`revert_series_if_last`) [S38]. Mit erpnext_germany (`prevent_gaps_in_transaction_naming`, Vorgabe 1) lässt sich je Kreis und Unternehmen nur der jüngste Beleg vom Typ Quotation, Sales Order oder Sales Invoice löschen [S42].
- **Löschungen:** Jeder Transaction Deletion Record ist ein Warnsignal; der Hook `company_data_to_be_ignored` nimmt DocTypes aus [S40, S41]. Deleted Document nur zählen, `data` nie ausgeben [S38].
- **Protokollierung** (`track_changes`): an bei Sales und Purchase Invoice, Journal Entry, Payment Entry, Bank Transaction, Bank Account, Account, Company, Customer, Supplier, Item, Steuervorlagen, Print Format, Letter Head und den meisten Settings; aus bei GL Entry, Payment Ledger Entry, Cost Center, Mode of Payment, Tax Rule, Expense Claim, Salary Slip und Payroll Entry. Customize Form kann das ändern, deshalb zur Laufzeit lesen. Die Versionen der Settings sind ihre Änderungshistorie [S38, S40, S47].
- **Kontenplan:** Steuerbotes `VAT Return Settings.chart` nennt den Kontenrahmen ein zweites Mal [S48].
- **Druck:** Belege nehmen `Company.default_letter_head`; PDF on Submit und DATEV setzen je DocType eigene Druckformate [S40, S43, S45].

Vorgaberechte auf Ebene 0 [S40]:

| DocType | Accounts User | Accounts Manager |
|---|---|---|
| Sales Invoice | alles außer stornieren, löschen | alles |
| Purchase Invoice | alles außer löschen | alles |
| Journal Entry, Payment Entry | alles | alles |
| GL Entry | lesen, exportieren | lesen, exportieren |
| Account | lesen, schreiben, anlegen, löschen | ebenso |

Auditor liest Purchase Invoice, Journal Entry, GL Entry und Account.

### 4.4 Zugriff und Sicherheit

- **Rechte:** Custom DocPerm ersetzt DocPerm je DocType [S38].
- **Permission Log** protokolliert Änderungen an User, Role Profile, Module Profile, User Permission, Custom DocPerm, Custom Role, Custom Field, Property Setter, Report, Page und DocType; es wird nicht automatisch geleert und bei Installation und Migration nicht geschrieben [S37, S38].
- **Anmeldung:** Vorgaben in 3.5, Kap. 14; ein Feld `password_policy` gibt es nicht [S37]. Weitere System Settings: `encrypt_backup`, `enable_scheduler`, `enable_onboarding`, `rounding_method`, `enable_telemetry` (1) [S37].
- **Protokolle und Fristen:** Activity Log (Login, Logout, Impersonate) 90 Tage; Access Log für Listen-Exporte, Data Export, Drucke, PDFs und Downloads privater Dateien und Sicherungen, nicht automatisch geleert; Error Log 14 Tage; Scheduled Job Log 7 Tage und nicht für Aufträge vom Typ All und Cron ohne `create_log`. Die Fristen kommen aus dem Hook `default_log_clearing_doctypes` und sind in Log Settings änderbar [S36–S38].
- **Anpassungen:** Custom Field, Property Setter, Client Script, Server Script, Workflow, Notification, Webhook (nie `webhook_secret`), Report, Auto Repeat, Document Naming Rule und Data Import werden alle protokolliert [S37].
- **MCP und Agenten:** Frappe 16 öffnet zwei Wege, nach denen eine Prüfung fragen wird: MCP (`frappe/mcp`, `enable_mcp`, Vorgabe 1) und Flow Agents, die Flow Trigger bei Dokumentereignissen auslösen [S36–S38].
- **Fehlt im Image:** Energy Points (App `eps`) [S37].
- **Grenzen der Unveränderlichkeit:** Ein buchbarer Beleg sperrt seine Felder ab docstatus 1, Stornieren und Berichtigen bleiben möglich, `protect_attached_files` hält nur bis zum Storno [S38, S42].

### 4.5 Datensicherung

Frappe 16 plant keine Sicherung; der stündliche Auftrag `delete_downloadable_backups` behält `backup_limit` Sätze. Ohne eine Datei zu öffnen, belegt die Site Name, Größe und Änderungszeit unter `get_backup_path()`; `-site_config_backup.json` enthält Geheimnisse. `fetch_latest_backups()` (System Manager) liefert den neuesten Satz der letzten 30 Tage. Sicherungen über einen Helm-Job (`jobs.backup`), restic oder Kopien außer Haus sieht die Site nicht: Formularabschnitt [S33, S36].

### 4.6 Apps im Image

| App | Belegt | Eigenheiten |
|---|---|---|
| erpnext_germany 16.2.2 | geschützte Anhänge, Datenträgerüberlassungen (GDPdU Export), VIES-Abfragen (VAT ID Check: `party`, `party_vat_id`, `status`, `is_valid`, `request_id`) | keine eigene Festschreibung |
| erpnext_datev 16.0.2 | Export an die Steuerberatung; DATEV Unternehmen Online sendet beim Buchen als Communication | der CSV-Export hinterlässt auf der Site keine Spur, `download_datev_csv` schreibt kein Access Log |
| eu_einvoice 16.4.0 | eingehende E-Rechnungen mit Original, ausgehende E-Rechnungen | XML wird nur bei XRECHNUNG automatisch angehängt; Fehler stehen nur im Error Log (14 Tage) |
| erpnext_pdf-on-submit 16.3.1 | Belegkopie beim Buchen für eingerichtete DocTypes (`doc_events "*"`), private Datei unter Home/<DocType>; Sales Invoices mit eingebettetem ZUGFeRD-XML | nach der Installation leer |
| banking 16.6.4 | Abruf über den Dienst alle 4 Stunden von 6 bis 22 Uhr, EBICS stündlich werktags von 7 bis 18 Uhr; eindeutige `transaction_id`, Abgleichsregeln, Zahlungsaufträge | Kennungen nur als „gesetzt“ |
| hrms 16.60.0 | Freigabekontrollen bei Spesen | Expense Claim, Salary Slip und Payroll Entry ohne Protokoll; der Hook `audit_trail_doctypes` hat hier keinen Abnehmer |
| Steuerbote 0.3.0 | ELSTER-Abgaben und ihr Archiv, Nachweise zu USt-IdNrn., Fristen | `ELSTER Transmission` ist nur einfügend; in 0.3.0 hindert den Eigentümer einer angehängten Datei nichts, sie zu löschen, ab 0.4.0 schützt `record_files.py` die Dateien wie bei `VAT ID Confirmation` [S48, S53] |

Ohne Protokoll: ERPNext Germany Settings, E Invoice Settings, DATEV Unternehmen Online Settings, Banking Settings. Quellen: [S42–S48].

### 4.7 Bausteine für die App

- **Beiträge:** `frappe.get_hooks(key)` hängt Listen aller Apps in Installationsreihenfolge aneinander und führt Dicts je Schlüssel zusammen. Muster in ERPNext: `for method_name in frappe.get_hooks("get_matching_queries"): frappe.get_attr(method_name)(…)`, gefüttert von banking; außerdem `company_data_to_be_ignored` (gefüttert von Steuerbote und HRMS) und `standard_queries` [S41, S46, S48].
- **Steuerbote** nutzt `company_data_to_be_ignored`, `doc_events["File"]`, einen täglichen Auftrag, nach Modul gefilterte `fixtures` und `add_to_apps_screen` [S48].
- **Menü:** Frappe 16 liest `Dock` aus `<app>/dock/<name>/<name>.json` und `Sidebar` aus App oder Modul; Steuerbotes Dock hängt „Steuern“ in die Leiste von ERPNext und öffnet eine Seitenleiste mit dem Arbeitsbereich [S48].
- **Änderungen an Formularen:** `track_changes` 1 schreibt je Speichern eine Version, deren `data` `changed`, `added`, `removed` und `row_changed` hält [S38]. Den Feldtyp „Markdown Editor“ gibt es [S39].

### 4.8 Lücken und Umgang

| Lücke | Wirkung | Umgang in der App |
|---|---|---|
| Image-Stand im Container nicht lesbar | Programmidentität nur über App-Versionen | Umgebungsvariable vorschlagen, bis dahin Formularfeld, sonst Lücke |
| Unveränderliches Hauptbuch aus (0) | ein Storno kennzeichnet auch das Original | Wert ausgeben, Hinweis mit Wirkung |
| Error Log 14, Activity Log 90, Scheduled Job Log 7 Tage | Nachweise verfallen | Fristen ausgeben; deutlicher Hinweis, wenn Version, Permission Log, Access Log oder Deleted Document in Log Settings stehen |
| Keine geplante Sicherung, drei Sätze | die Sicherung liegt außerhalb der Site | Formularabschnitt Pflicht, Liste der Sätze |
| Accounts User darf Konten löschen | Funktionstrennung | Hinweis in Kap. 14 |
| Kein Schalter und kein Bericht „Audit Trail“ in v16 | Änderungen nur über Version, Permission Log und Access Log belegt | diese ausgeben |
| Settings ohne Protokoll (vier aus 4.6) und DocTypes ohne `track_changes` (4.3) | Änderungen ohne Historie | Hinweis; „veraltet“ über `modified` |
| DATEV-CSV-Export ohne Spur | Weitergabe an die Steuerberatung nicht belegt | Formularabschnitt in Kap. 4, Hinweis |
| MCP an, Flow Trigger | Zugriff und Änderungen ohne Oberfläche | in Kap. 14 listen |
| Auf einer neuen Site Festschreibung nur durch Buchen | keine Periodensperre | tatsächliche Mittel in Kap. 8 ausgeben |
| Leere Zeitzone | Zeiten in Asia/Kolkata | Lücke |
| Scheduler-Status aus dem Web-Pod unzuverlässig | falscher Befund | `last_execution` |
| `developer_mode`, `allow_tests` oder `ignore_csrf` an | Produktivsite im Testzustand | Hinweis |
| E-Rechnungsfehler nur im Error Log | nach 14 Tagen weg | Hinweis |
| Löschen durch Administrator oder in der Datenbank | Lücke in der Historie | Hash-Kette |
| ELSTER-Übermittlung ohne Dateischutz (bis 0.3.0) | Archiv löschbar | in Steuerbote 0.4.0 behoben (`record_files.py`) |

## 5. Ausbaustufen

Ziel ist der volle Umfang. Aufwand grob in Entwicklertagen, ohne die fachliche Durchsicht durch die Steuerberatung.

| Stufe | Inhalt | Kapitel | Tage |
|---|---|---|---|
| 1 | Grundausbau: Gliederung aller Kapitel; Kapitel 1, 2, 4, 7, 8, 11, 14, 16, 17 und 18 erzeugt, die übrigen als Formular; Lücken, Stempel, Fassungen, Freigabe, Jahresstand, „veraltet“, PDF und Markdown | alle | 31 |
| 2 | Datenlexikon nach Rz. 160: aus `frappe.get_meta()` je buchhaltungsrelevantem DocType die Felder (Label, Typ, Optionen), Verknüpfungen (Link, Dynamic Link, Table), Custom Field und Property Setter, dazu die Berichte; als Anhang und maschinenlesbar | 10 | 5 |
| 3 | Prozesskapitel je Modul (Verkauf, Einkauf, Bank, Spesen, Lohn, Anlagen): genutzte Belegarten mit Anzahl je Geschäftsjahr, Nummernkreis, Workflow, Druckformat, PDF beim Buchen, E-Rechnung, Versand an DATEV, Ablage | 5 | 8 |
| 4 | Automatische Buchungen nach Rz. 80: Regeln, berechtigte Änderungen, Nachweis der Anwendung für Auto Repeat, Abschreibungen, Abgrenzungen, Fremdwährungsbewertung, Bankabgleichsregeln, Server Scripts und Flow Trigger auf Buchungs-DocTypes; Felder unbestätigt | 9 | 5 |
| 5 | Z3-Beschreibung und Migration: GDPdU Export mit exportierten DocTypes und Format, Z1 über Leserollen, Aufbewahrung der Dateien, Eröffnungsbuchungen, Data Import; Format des Exports von erpnext_germany unbestätigt | 12, 13 | 4 |
| 6 | Funktionstrennung: Regeln für unverträgliche Rechte eines Benutzers (etwa Lieferanten anlegen und Zahlungen buchen, Bankkonten pflegen und zahlen), Bericht mit Begründung; Fassungsvergleich als Text | 14, 18 | 4 |
| 7 | § 146a-Erkennung: POS Profile, POS Invoice, Barzahlungsarten; nur Hinweis | 4 | 1 |
| 8 | Scan-Kapitel nach Rz. 136–141, nur bei erklärtem ersetzendem Scannen: zentrales und mobiles Scannen, Geräte, Kontrollen, Vernichtung; Gliederung mit Verweis auf das Muster von BStBK und DStV | 6 | 3 |
| | **Summe** | | **61** |

Kapitel 17 erzeugt in Stufe 1 die Betriebsangaben der Site (Scheduler, Konfiguration, Zeitzone), die die Sammler ohnehin lesen; Ort der Daten, Updates und Zugänge bleiben Formular. Die Stufen 2 bis 8 hängen nur von Stufe 1 ab und lassen sich in beliebiger Reihenfolge oder parallel liefern.

**Stufe 1 im Einzelnen**

| Paket | Inhalt | Tage |
|---|---|---|
| 1 | Gerüst: App, DocTypes, Rechte, Dateischutz, `company_data_to_be_ignored`, Dock, Seitenleiste, Arbeitsbereich, Übersetzung, CI | 3 |
| 2 | Beitrags-Hook, Registry, Lücken, Fehlerisolierung, Abschnittsmodell, Gliederung mit allen Schlüsseln | 2 |
| 3 | Sammler der Site: Software, Konfiguration, Scheduler, Zugriff, Protokolle, Sicherungen, MCP und Agenten | 4 |
| 4 | Sammler der Buchhaltung: Unternehmen, Abweichung des Kontenplans, Perioden, Nummernkreise, Löschungen, Protokollierung, Druck, E-Mail, Bank | 4 |
| 5 | Adapter für die fünf Apps von ALYF und HRMS; Beitrag von Steuerbote; CI-Job mit den Pins von erpnext_germanized | 4 |
| 6 | Darstellung: Markdown, Druckformat, PDF, PDF/A als Option | 3 |
| 7 | Einfrieren, Freigabe, Hash-Kette, Jahresstand, „veraltet“ (ein Tag mehr mit `Software Version Log`) | 3 |
| 8 | Textkatalog: Kapiteltexte, Formularfragen, Hinweise, Glossar, Haftungshinweis, jede Angabe mit Quelle | 4 |
| 9 | Site-Tests, Browser-Tests, Dokumentation, Changelog, Einbindung in erpnext_germanized | 4 |
| | **Summe** | **31** |

Die Pakete 3, 4, 5 und 8 laufen nach 1 und 2 parallel; 6 und 7 brauchen den Kern aus 2; 9 kommt zuletzt.

**Abnahme von Stufe 1** auf einer Testsite mit dem Image von erpnext_germanized:

1. Installation und `bench migrate` ohne Fehler; „Verfahrensdoku“ erscheint auf der Leiste für die vier Rollen aus 3.8 und für keine andere.
2. Für jedes Unternehmen lässt sich das Dokument anlegen; die Vorschau zeigt alle Kapitel auf Deutsch, das Hinweisband und die Herkunft je Absatz.
3. Stichproben stimmen mit der Site überein: Accounts Settings, Nummernkreise, Benutzer und Rollen, Sicherungsdateien, App-Versionen, Image-Stand.
4. Kein Geheimnis im Ergebnis: keine Passwörter, Schlüssel, Webhook-Secrets, vollständigen IBANs oder Empfängeradressen.
5. Einfrieren ergibt Markdown und PDF; `sha256sum` der heruntergeladenen Markdown-Datei gleicht `markdown_sha256`.
6. Freigabe mit Lücken nur nach Bestätigung; eine zweite Freigabe beendet die Gültigkeit der ersten am Vortag.
7. Ändern und Löschen von Fassung und Dateien scheitern auch für System Manager; „Kette prüfen“ meldet die Kette als intakt.
8. Nach einer geänderten Druckeinstellung zeigt das Dokument „veraltet“ mit Grund.
9. Mit installiertem Steuerbote erscheinen dessen Abschnitte.
10. README und Dokumentation enthalten keines der Wörter aus 2.9; die CI ist grün, der Kern hat 100 % Abdeckung; der PDF-Schritt im Site-Test von erpnext_germanized läuft durch.

## 6. Verortung

Entscheidung der Maintainer vom 21.11.2026: Variante A, eigene App. Die Fakten zu allen drei Varianten bleiben hier stehen.

| | A) eigene App | B) Modul in Steuerbote | C) Beitrag zu erpnext_germany |
|---|---|---|---|
| Name | `erpnext_gobd` oder `verfahrensbote`: frei auf PyPI und GitHub, kein Konflikt unter den 1.079 DocType-Namen im Image [S52] | – | – |
| Abhängigkeiten | `required_apps` erpnext; Apps von ALYF nur über DocType-Namen, wenn installiert, ohne Import | Steuerbote („ELSTER tax filings“) läse fachfremde Apps | ALYF liest die eigenen Apps; braucht deren Zustimmung |
| Releases | eigene Tags, in erpnext_germanized unter `INDEPENDENTLY_VERSIONED`; jedes Release eine Revision über den Workflow App versions [S33, S54] | mit Steuerbotes Releases | im Takt von ALYF: v16-Tags am 20.01., 30.01., 29.07., 17.09., 23.10. und 24.10.2026 [S49] |
| CI | eigener Bench-Job mit allen Apps an ihren Pins; PDF im Site-Test von erpnext_germanized | Steuerbotes CI installiert nur ERPNext: Adapter ungetestet | ALYFs CI installiert ERPNext und die App: dieselbe Lücke |
| Hooks anderer | Adapter in der App, später ein Hook-Angebot an ALYF | wie A | ALYF könnte aus datev, einvoice und banking beitragen |
| Auffindbarkeit | eigener Dock-Eintrag und Kachel | unter „Steuern“ | am breitesten: Frappe Cloud, 98 Sterne [S49] |
| Lizenz, Prozess | AGPL-3.0-or-later wie Steuerbote oder GPL-3.0, um C offen zu halten | AGPL-3.0-or-later, deutsche Dokumentation, 100 % Kernabdeckung | GPL-3.0, englisch, semantic-release, keine CONTRIBUTING-Datei; externe Pull Requests nach 2 Tagen (#139, #122) bis 3 Monaten (#103, #120, #121) gemergt, #142 und #143 offen seit 03.11.2026 [S49] |
| Aufwand Stufe 1 | 31 Tage | etwa 2 Tage weniger | mehr Review-Runden und Wartezeit auf Releases |

**Einbindung in erpnext_germanized** (A und B): ein Eintrag in `apps.json`; die URL in `INDEPENDENTLY_VERSIONED` (`germanized/apps.py`) samt Test, weil die App nicht der Hauptversion von Frappe folgt; eine Zeile in der Tabelle „Enthaltene Apps“ im README, die `python -m germanized readme --check` prüft; ein Abschnitt in `docs/apps.md`; ein Eintrag unter „Unveröffentlicht“ im CHANGELOG; die Umgebungsvariable aus 4.1; der PDF-Schritt in `tests/site/run.sh`. Das Lizenz-Label des Images enthält AGPL-3.0-or-later schon [S33, S54].

**Repository** (A): wie Steuerbote und erpnext_germanized deutsche Dokumentation mit README, CONTRIBUTING und SECURITY, Vorlagen für Issues und Pull Requests, Discussions, Dependabot für Actions und pip, SHA-gepinnte Actions, Workflows Tests, Linters und Security [S53, S54]. Einen Verhaltenskodex hat bisher keines der beiden Repositories.

**Steuerbote** trägt in jedem Fall selbst bei: Einstellungen (Kap. 2), ERiC-Einstellungen (Kap. 4), Übermittlungen, Archiv und Nachweise zu USt-IdNrn. (Kap. 12), Fristenerinnerungen (Kap. 14); den Dateischutz der `ELSTER Transmission` bringt Steuerbote 0.4.0 mit (4.6).

## 7. Offene Fragen mit Vorschlag

| Nr. | Frage | Vorschlag |
|---|---|---|
| 7.1 | Voller Umfang oder nur Grundausbau? | voller Umfang als Ziel, Lieferung in Stufen, Stufe 1 zuerst |
| 7.2 | Ein Dokument je Unternehmen oder je Site? | je Unternehmen, Teil der Site wiederholt |
| 7.3 | Gilt eine Fassung erst mit Freigabe? | ja, durch die Geschäftsführung; „fachlich geprüft“ freiwillig |
| 7.4 | Wer erfasst die Freigabe? | die Person selbst oder ein Accounts Manager in ihrem Auftrag; Name und Datum der Person aus der Geschäftsführung Pflicht, erfassender Benutzer gespeichert |
| 7.5 | Freigabe mit offenen Lücken? | ja, nach Bestätigung; das Hinweisband bleibt |
| 7.6 | Formate? | PDF und Markdown; PDF/A als Option, wenn der Test in Stufe 1 gelingt |
| 7.7 | Ablage freigegebener Fassungen? | unveränderliche Datei je Fassung, dazu der Jahresstand |
| 7.8 | Wortlaut der Muster übernehmen? | nein; eigener Text, die Gliederung verweist auf die Muster; die AWV erlaubt Nutzung nur nach Vereinbarung [S26] |
| 7.9 | Scan-Kapitel? | nur bei erklärtem ersetzendem Scannen (Stufe 8) |
| 7.10 | Datenlexikon nach Rz. 160 schon im Grundausbau? | nein, Stufe 2 |
| 7.11 | § 146a erkennen? | nur hinweisen (Stufe 7) |
| 7.12 | Haftungshinweis? | Wortlaut aus 2.9; nie „GoBD-konform“ |
| 7.13 | Kapitel späterer Stufen schon in Stufe 1 zeigen? | ja, als Formularabschnitte mit „Fehlt:“, damit die Gliederung nach Rz. 153 von Anfang an steht |
| 7.14 | Softwarestände zwischen zwei Fassungen lückenlos festhalten? | ja, mit dem kleinen DocType `Software Version Log` (etwa ein Tag); ohne ihn bleiben nur Patch Logs, die Migrationen ohne Patches nicht zeigen |
| 7.15 | Wann friert der Jahresstand ein? | 30 Tage nach Ende des Geschäftsjahres, einstellbar |
| 7.16 | Personenbezogene Daten in einem zehn Jahre aufbewahrten Dokument? | Name, Kennung, Rollen, Anlage- und letztes Anmeldedatum, Sperre; keine IP-Adressen, Anmeldungen nur als Summen; mit dem Datenschutz abstimmen |
| 7.17 | Image-Stand im Container? | `ENV ERPNEXT_GERMANIZED_VERSION=${VERSION}` in erpnext_germanized |
| 7.18 | Dateischutz der ELSTER-Übermittlung? | erledigt mit Steuerbote 0.4.0 |
| 7.19 | Wer prüft die Texte fachlich? | eine Steuerberaterin oder ein Steuerberater vor dem ersten Release |
| 7.20 | Name und Lizenz der App? | Entscheidung der Maintainer bei der Gründung des Repositorys; Verortung als eigene App ist entschieden (Abschnitt 6) |

## 8. Quellen

Alle abgerufen oder gelesen am 21.11.2026. Die Website des BMF antwortete; das PDF von 2019 war dort unter zwei bekannten Adressmustern nicht zu finden (404), deshalb ist [S1] die Kopie des unterzeichneten Schreibens bei der IHK München. Die Quelltexte [S35]–[S47] wurden im Image [S34] gelesen und entsprechen den genannten Tags.

**Recht und Verwaltung**

- [S1] BMF, GoBD, 28.11.2019, IV A 4 - S 0316/19/10003 :001 (Kopie): https://www.ihk-muenchen.de/ihk/documents/Recht-Steuern/Steuerrecht/2019-11-28-GoBD.pdf
- [S2] GoBD i. d. F. vom 11.03.2024, Amtliches AO-Handbuch 2025, Anhang 33 (BMF): https://ao.bundesfinanzministerium.de/ao/2025/Anhaenge/BMF-Schreiben-und-gleichlautende-Laendererlasse/Anhang-33/inhalt.html
- [S3] BMF, erste Änderung, 11.03.2024, IV D 2 - S 0316/21/10001 :002, mit Anlage: https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Weitere_Steuerthemen/Abgabenordnung/AO-Anwendungserlass/2024-03-11-aenderung-gobd.pdf?__blob=publicationFile&v=4
- [S4] BMF, zweite Änderung, 14.07.2025, IV D 2 - S 0316/00128/005/088: https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Weitere_Steuerthemen/Abgabenordnung/2025-07-14-GoBD-2-aenderung.pdf?__blob=publicationFile&v=4
- [S5] GoBD 2019, Amtliches AO-Handbuch 2021, Anhang 64 (Abgleich der Nummern): https://ao.bundesfinanzministerium.de/ao/2021/Anhaenge/BMF-Schreiben-und-gleichlautende-Laendererlasse/Anhang-64/anhang-64.html
- [S6] § 145 AO: https://www.gesetze-im-internet.de/ao_1977/__145.html
- [S7] § 146 AO: https://www.gesetze-im-internet.de/ao_1977/__146.html
- [S8] § 147 AO: https://www.gesetze-im-internet.de/ao_1977/__147.html
- [S9] § 158 AO: https://www.gesetze-im-internet.de/ao_1977/__158.html
- [S10] § 162 AO: https://www.gesetze-im-internet.de/ao_1977/__162.html
- [S11] § 197 AO: https://www.gesetze-im-internet.de/ao_1977/__197.html
- [S12] § 200a AO: https://www.gesetze-im-internet.de/ao_1977/__200a.html
- [S13] § 146a AO: https://www.gesetze-im-internet.de/ao_1977/__146a.html
- [S14] § 87 AO: https://www.gesetze-im-internet.de/ao_1977/__87.html
- [S15] § 257 HGB: https://www.gesetze-im-internet.de/hgb/__257.html
- [S16] § 1 KassenSichV: https://www.gesetze-im-internet.de/kassensichv/__1.html
- [S17] Art. 97 § 38 EGAO: https://www.gesetze-im-internet.de/aoeg_1977/art_97__38.html
- [S18] BMF, AEAO zu § 146 (Verlagerung, Verzögerungsgeld), 10.11.2026, IV D 2 - S 0316/00139/004/077: https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Weitere_Steuerthemen/Abgabenordnung/AO-Anwendungserlass/2026-11-10-aenderung-aeao-zu-paragraf-146.pdf?__blob=publicationFile&v=4
- [S19] BMF, Neufassung des AEAO zu § 146a, 26.10.2026: https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Weitere_Steuerthemen/Abgabenordnung/AO-Anwendungserlass/2026-10-26-neufassung-aeao-zu-paragraf-146a.pdf?__blob=publicationFile&v=4
- [S20] BMF, Automationsgestützte quantitative Prüfungsmethoden, 05.09.2023, IV D 3 - S 1445/20/10007 :006: https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Weitere_Steuerthemen/Betriebspruefung/2023-09-05-automationsgestuetzte-quantitative-pruefungsmethoden-steuerl-Aussenpruefung.pdf?__blob=publicationFile&v=3
- [S21] BFH, 25.03.2015, X R 20/13, BStBl II 2015, 743: https://testphase.rechtsinformationen.bund.de/v1/rechtsprechung/STRE201510182
- [S22] BFH, 23.02.2018, X B 65/17: https://testphase.rechtsinformationen.bund.de/v1/rechtsprechung/STRE201850053
- [S23] BFH, 28.11.2023, X R 3/22: https://testphase.rechtsinformationen.bund.de/v1/rechtsprechung/STRE202410062
- [S24] BFH, 29.07.2025, X R 23-24/21: https://testphase.rechtsinformationen.bund.de/v1/rechtsprechung/STRE202520320
- [S25] Rechtsprechungs-API des Bundes, Volltextsuche „Verfahrensdokumentation“ (ein Treffer, BGH 2 BGs 408/20; kein BFH): https://testphase.rechtsinformationen.bund.de/v1/rechtsprechung?searchTerm=Verfahrensdokumentation

**Muster**

- [S26] AWV, Muster-Verfahrensdokumentation zur Belegablage, V1.0, 19.10.2015 (Seite mit PDF und Word-Vorlage): https://www.awv-net.de/publikationen-produkte/publikationen/detailseite/musterverfahrensdokumentation-zur-belegablage
- [S27] Dasselbe Muster, bei der IHK abgelegte Kopie: https://www.ihk.de/blueprint/servlet/resource/blob/2787208/1a00bfaedfdbbb481eadd33c75e5444d/muster-verfahrensdokumentation-zur-belegablage-data.pdf
- [S28] BStBK und DStV, Muster-Verfahrensdokumentation zum ersetzenden Scannen, v2.1, 27.02.2026: https://www.bstbk.de/downloads/bstbk/steuerrecht-und-rechnungslegung/fachinfos/BStBK_Muster-VerfD-ersetzendes-Scannen_v2.0-2019-11-29.pdf
- [S29] AWV, GoBD – Ein Praxisleitfaden für Unternehmen, v2.2, 2023, Kapitel 5, und die GoBD-Seite der AWV: https://www.awv-net.de/publikationen-produkte/publikationen/detailseite/gobd-ein-praxisleitfaden-fuer-unternehmen-version-22 ; https://www.awv-net.de/publikationen-produkte/gobd-und-verfahrendokumentation
- [S30] DFKA, Muster-VD Kasse: https://dfka.net/unsere-themen/muster-vd-kasse/

**Werkzeuge und Umfeld**

- [S31] GitHub-Codesuche „Verfahrensdokumentation org:alyf-de“ (0 Treffer) und „Verfahrensdokumentation frappe“ (3 Treffer, kein Generator): https://github.com/search?type=code&q=Verfahrensdokumentation+frappe
- [S32] Dokumentation von git-push, Option `--force`: https://git-scm.com/docs/git-push

**Frappe, ERPNext und Apps**

- [S33] erpnext_germanized, Tag v16.60.0-5 (Commit 8041997): `apps.json`; `Containerfile` (`FRAPPE_BRANCH` v16.60.2, `VOLUME`, `LABEL`); `germanized/apps.py:14`; `docs/versionierung.md`, `docs/betrieb.md` (Sicherungen, `jobs.backup`), `docs/apps.md`, `docs/entwicklung.md`; `tests/site/run.sh`: https://github.com/encircle360-oss/erpnext_germanized/tree/v16.60.0-5
- [S34] Image von erpnext_germanized, lokal gebaut am 18.11.2026 (Label-Version 740203c), Apps wie in `apps.json`, Steuerbote darin 0.1.1, deshalb Steuerbote nach [S48]: `docker image inspect` (Labels, Umgebung), `sites/apps.json`, `env/lib/python3.14/site-packages/*.dist-info`, `/usr/local/bin/entrypoint.sh`, `pip list`, `/usr/bin/chromium-headless-shell`, `/usr/local/bin/wkhtmltopdf`; Quelltexte unter `/home/frappe/frappe-bench/apps/`, gelesen mit `docker run --rm`.
- [S35] Frappe v16.60.2, `frappe/`: `__init__.py` (930, 968–1035), `utils/change_log.py` (105–181), `utils/__init__.py:803`, `core/doctype/installed_applications/installed_applications.py` (29–150), `migrate.py:207`, `utils/sbom/__init__.py`, `utils/sbom/collector.py`, `www/attribution.py`, `core/doctype/patch_log/patch_log.json`: https://github.com/frappe/frappe/tree/v16.60.2/frappe
- [S36] Frappe v16.60.2, `frappe/`: `desk/doctype/system_health_report/`, `utils/scheduler.py` (56–265), `utils/data.py:389`, `utils/password.py:240`, `utils/safe_exec.py` (48–92), `utils/backups.py` (31, 211–216, 546–567, 686), `desk/page/backups/backups.py`, `hooks.py` (132, 222–262, 300–345, 601–620), `patches/v16_0/add_module_deprecation_warning.py`, `core/doctype/log_settings/log_settings.py`, `core/doctype/scheduled_job_type/scheduled_job_type.py` (55–185), `mcp/__init__.py:11`
- [S37] Frappe v16.60.2, DocType-JSON: core (system_settings, user, has_role, access_log, activity_log, error_log, scheduled_job_log, scheduled_job_type, permission_log, audit_trail, version, deleted_document, log_settings, logs_to_clear, api_request_log, file, custom_docperm, docperm, role, role_profile, module_profile, user_permission, user_type, server_script, security_settings, document_naming_settings, data_import, data_import_log, report, docfield); custom_field, property_setter, client_script; print_settings, print_format, letter_head; email_account, notification, webhook, connected_app, auto_repeat, workflow; flow_provider, flow_agent, flow_trigger, flow_settings
- [S38] Frappe v16.60.2, `frappe/`: `permissions.py` (513–605), `model/meta.py` (398, 637–650), `core/page/permission_manager/permission_manager.py` (80, 186, 192), `core/doctype/permission_log/permission_log.py` und `get_permission_log_options` in den Controllern aus 4.4; `model/delete_doc.py` (215–257), `model/naming.py` (408–478), `core/doctype/document_naming_settings/document_naming_settings.py` (41–104, 210–236); `core/doctype/activity_log/activity_log.py:72`, `utils/response.py` (275–305), `desk/reportview.py:533`; `core/doctype/file/file.py` (645–666, 1088–1125), `core/doctype/file/utils.py:213`; `core/doctype/audit_trail/audit_trail.py`, `custom/doctype/customize_form/customize_form.py` (737–748), `model/sync.py` (25–59)
- [S39] Frappe v16.60.2, `frappe/`: `utils/pdf.py` (110–220, 472), `utils/print_utils.py` (33–130), `www/printview.py` (84, 185), `utils/data.py` (2600–2634), `utils/__init__.py:738`
- [S40] ERPNext v16.60.0, DocType-JSON: Company; Accounts Settings, Account, GL Entry, Payment Ledger Entry, Cost Center; Fiscal Year mit Unternehmenstabelle, Accounting Period, Closed Document, Period Closing Voucher, Process Period Closing Voucher, Account Closing Balance; Repost Accounting Ledger, Repost Allowed Types, Ledger Health Monitor; Sales und Purchase Invoice, Journal Entry, Payment Entry; Bank Account, Bank Transaction, Bank Statement Import Log, Mode of Payment mit Kontentabelle, Payment Terms Template; Tax Rule, Tax Category, Sales und Purchase Taxes and Charges Template, Item Tax Template mit Details; Transaction Deletion Record mit drei Tabellen; `accounts/doctype/account/chart_of_accounts/verified/` mit `de_kontenplan_SKR03.json` und `de_kontenplan_SKR04.json`; Verzeichnis `accounts/report/`: https://github.com/frappe/erpnext/tree/v16.60.0/erpnext
- [S41] ERPNext v16.60.0, `erpnext/`: `accounts/utils.py` (2232–2250, 2826), `accounts/general_ledger.py` (156, 458–470, 730–860), `controllers/accounts_controller.py` (498–500, 603–630), `setup/doctype/company/company.py` (438–455, 635–644), `setup/doctype/transaction_deletion_record/transaction_deletion_record.py:1225`, `accounts/doctype/bank_reconciliation_tool/bank_reconciliation_tool.py:1461`, `accounts/doctype/accounting_period/accounting_period.py` (109–145), `accounts/doctype/repost_accounting_ledger/repost_accounting_ledger.py` (48–80, 320–335), `hooks.py:758`
- [S42] erpnext_germany v16.2.2, Commit 9df6007: `hooks.py`, `custom/sales.py`, `property_setters.py`, `custom_fields.py`; DocTypes ERPNext Germany Settings, GDPdU Export, GDPdU DocType, VAT ID Check; README, Abschnitte Features, GDPdU Export, Contributing und License: https://github.com/alyf-de/erpnext_germany/tree/v16.2.2
- [S43] erpnext_datev v16.0.2, Commit 2757764: `hooks.py`, DocTypes DATEV Settings, DATEV Unternehmen Online Settings (`.py` 40–80), DATEV Voucher Config, `report/datev/datev.py:542`: https://github.com/alyf-de/erpnext_datev/tree/v16.0.2
- [S44] eu_einvoice v16.4.0, Commit a001d94: `hooks.py`, `custom_fields.py`, DocTypes E Invoice Settings und E Invoice Import, `european_e_invoice/einvoice.py` (795–850, 980–992): https://github.com/alyf-de/eu_einvoice/tree/v16.4.0
- [S45] erpnext_pdf-on-submit v16.3.1, Commit 297acc4: `hooks.py`, `attach_pdf.py`, DocTypes PDF on Submit Settings und Enabled DocType, `patches/settings_checkbox_to_list.py`: https://github.com/alyf-de/erpnext_pdf-on-submit/tree/v16.3.1
- [S46] banking v16.6.4, Commit 436506b: `hooks.py` (113–175, 247–262), DocTypes Banking Settings, EBICS User, EBICS Request, SEPA Payment Order, Bank Reconciliation Rule: https://github.com/alyf-de/banking/tree/v16.6.4
- [S47] hrms v16.60.0, Commit 34fbb8a: `hooks.py` (299, 396), DocTypes HR Settings, Payroll Settings, Expense Claim, Salary Slip, Payroll Entry: https://github.com/frappe/hrms/tree/v16.60.0
- [S48] Steuerbote, Tag v0.3.0: `hooks.py`, `permissions.py`, `dock/steuerbote/steuerbote.json`, `steuerbote/sidebar/steuerbote/steuerbote.json`, `steuerbote/workspace/steuern/steuern.json`; DocTypes VAT ID Confirmation (`.py` 75–130), ELSTER Transmission (`.py` 70–90), ERiC Settings, VAT Return Settings, VAT Return, Recapitulative Statement, VAT Return Extension, Deadline Reminder; `tests/test_workspace.py`, `print_format/umsatzsteuer_voranmeldung/test_umsatzsteuer_voranmeldung.py`, `.github/workflows/tests.yml`: https://github.com/encircle360-oss/steuerbote/tree/v0.3.0
- [S49] GitHub-API zu erpnext_germany: Metadaten (GPL-3.0, Standardbranch version-16-hotfix, 98 Sterne); offene Pull Requests (#50, #142, #143) und die letzten 40 gemergten; Releases; Workflows zu v16.2.2; keine CONTRIBUTING-Datei, `alyf-de/.github` antwortet mit 404: https://github.com/alyf-de/erpnext_germany
- [S50] GitHub-Suche, Repositories „verfahrensdokumentation“ (3, keines für Frappe), „gobd frappe“ und „gobd erpnext“ (nur eine App für den Z3-Export, deren README die Verfahrensdokumentation ausklammert), „gobd“ in Python (keines für Frappe); Code „Verfahrensdokumentation“ in Python und „GoBD“ in `hooks.py`: https://github.com/search?type=repositories&q=gobd+erpnext
- [S51] Frappe Cloud Marketplace, über einen zusammenfassenden Abruf gelesen; Vollständigkeit unbestätigt: https://cloud.frappe.io/marketplace
- [S52] PyPI-JSON-API, Antwort 404 (Name frei) für erpnext-gobd, erpnext_gobd, gobd, frappe-gobd, verfahrensdoku, verfahrensdokumentation, gobd-doku und verfahrensbote: https://pypi.org/pypi/erpnext_gobd/json und entsprechend; GitHub-Namenssuche nach erpnext_gobd, frappe_gobd und verfahrensbote; Abgleich mit den 1.079 DocType-Namen im Image [S34]
- [S53] Steuerbote, Branch main, gelesen am 21.11.2026: `steuerbote/hooks.py` (`doc_events["File"]`, `company_data_to_be_ignored`, `scheduler_events`, `fixtures`, `add_to_apps_screen`); `steuerbote/steuerbote/doctype/vat_id_confirmation/vat_id_confirmation.py` und `.json` (`in_create`, Rechte, `keep_answer`, `store`); `steuerbote/steuerbote/doctype/elster_transmission/elster_transmission.py` (`validate`, `on_trash`, `records_a_filing`); `steuerbote/translations/de.csv`; `pyproject.toml`, `.pre-commit-config.yaml`, `requirements-dev.txt`; `.github/` (`dependabot.yml`, `ISSUE_TEMPLATE/`, `PULL_REQUEST_TEMPLATE.md`, `workflows/tests.yml` mit Browser-Tests, `linters.yml`, `security.yml`); `CONTRIBUTING.md`, `SECURITY.md`; `docs/architektur.md`, Abschnitte „Platz im Desk“ und „Standard-Druckformate“: https://github.com/encircle360-oss/steuerbote
- [S54] erpnext_germanized, Branch main, gelesen am 21.11.2026: `Containerfile` (Zeilen 229–239, `ARG VERSION=dev` und die Labels hinter dem letzten `RUN`); `germanized/apps.py` (`INDEPENDENTLY_VERSIONED`, `validate`); `tests/test_apps.py:160`; `tests/site/run.sh` (Pins aus `sites/apps.json`, Prüfung von Ghostscript und `srgb.icc`); `README.md`, Tabelle „Enthaltene Apps“; `CHANGELOG.md`; `docs/versionierung.md`: https://github.com/encircle360-oss/erpnext_germanized
