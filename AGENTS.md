# Hinweise für Coding-Agenten

Der Einsatz von Coding-Agenten ist in diesem Projekt ausdrücklich erlaubt, für Maintainer wie für Mitwirkende. Verantwortlich bleibt immer der Mensch, der den Pull Request stellt und die Änderung versteht. Diese Datei ist der Einstieg. Die Regeln stehen in [CONTRIBUTING.md](CONTRIBUTING.md) und [docs/entwicklung.md](docs/entwicklung.md) und gelten für Menschen und Agenten gleichermaßen.

## Was ein Agent wissen muss

- **Projekt:** ein Rezept für ein Container-Image, keine Frappe-App. Das Image enthält Frappe und ERPNext 16, HRMS, die Apps von ALYF, Steuerbote und Briefbote und entsteht aus `apps.json` mit dem `Containerfile` aus frappe_docker v4.2.0.
- **Struktur:** `apps.json` listet die Apps mit ihren Tags, `Containerfile` ist das Rezept, `build.sh` baut lokal. `germanized/` enthält die Werkzeuge (Python 3.14, nur Standardbibliothek, Tabs, `ruff`), `tests/` ihre Tests mit `pytest` und 100 % Abdeckung, `tests/site/` den Site-Test des Images. Die Workflows liegen unter `.github/workflows/`, die gemeinsamen Schritte der Image-Jobs (Build, Site-Test, Scan) als Composite-Action unter `.github/actions/build-and-test/`, die Dokumentation unter `docs/`.
- **Sprache:** Code, Kommentare, Meldungen, Namen von Workflow-Schritten und Commit-Nachrichten englisch. Dokumentation, Issues und Pull Requests deutsch.
- **Quellen:** Aussagen über eine App stammen aus ihrem README und ihrer Dokumentation zum gepinnten Tag, Optionen von bench aus dem Quelltext von Frappe 16. Was dort nicht steht, wird nicht aus dem Gedächtnis ergänzt, sondern nachgeschlagen und belegt.

## Leitplanken

1. **Test zuerst.** Erst ein Test, der fehlschlägt, dann die Änderung an den Werkzeugen. Kein Test wird abgeschwächt, übersprungen oder gelöscht, um grün zu werden. Änderungen am Image prüft der Site-Test.
2. **Keine Geheimnisse.** Keine Passwörter, Tokens, Schlüssel, Inhalte von `site_config.json` oder Sicherungen in Code, Tests, Logs, Issues oder Commits. Ein Agent fragt nie nach Zugangsdaten, liest sie nie aus und speichert sie nie. Beispiele enthalten nur Platzhalter `CHANGE_ME`, Tests nur erfundene Werte.
3. **Nichts Internes.** Das Repository ist öffentlich und allgemein. Keine internen Hostnamen, keine Kunden, nichts über die Infrastruktur von Maintainern oder Betreibern.
4. **Alles gepinnt.** Actions per Commit-SHA mit der Version als Kommentar, Apps per Release-Tag, Images per Tag, Entwicklungswerkzeuge exakt. Jeder Pin wird an seiner Quelle geprüft, etwa am Tag auf GitHub, nicht geraten.
5. **Ein Pull Request, ein Thema.** Dokumentation und Changelog im selben Pull Request. Kleine Schritte.
6. **Nichts Ungeprüftes nach `main`.** Die CI muss grün sein, und ein Maintainer prüft vor dem Merge. Neue Apps, neue Hauptversionen und Änderungen am Rezept brauchen dieses Review immer.
7. **Upstream zuerst.** Keine Patches an Apps im Image. Ein Fehler einer App wird beim Projekt gemeldet. Wiegt er im Betrieb schwer, darf das Image die App vorübergehend aus einem Fork in `FORKS` bauen, der genau die Korrektur trägt, die beim Projekt als Pull Request liegt, bis ein Release sie enthält.
8. **Keine neuen Abhängigkeiten ohne Grund.** Die Werkzeuge bleiben bei der Standardbibliothek. Was für die Entwicklung dazukommt, wird exakt gepinnt und begründet.
9. **Fremder Code nur mit Herkunft und Lizenz.** Übernommene Dateien nennen ihre Quelle und behalten ihre Lizenz unter `LICENSES/`.
10. **Prüfen, was sicher prüfbar ist:** `pre-commit run --all-files`, `pytest`, `python -m germanized validate`, `python -m germanized readme --check`, bei Änderungen am Image `./build.sh` und `./tests/site/run.sh erpnext_germanized:local`.

## Wiederkehrende Aufgaben

- **Versionen anheben:** `python -m germanized check-versions`, dann `bump --write` und `readme --write`, die Release-Notes jeder geänderten App lesen, den Changelog ergänzen. Den Pull Request des Workflows App versions prüft man genauso.
- **Neue App:** die Schritte in [Entwicklung](docs/entwicklung.md#eine-app-hinzufügen-oder-entfernen), mit Lizenz und Zweck aus dem README der App.
- **Neue Version von frappe_docker:** ihr `images/custom/Containerfile` Zeile für Zeile mit dem `Containerfile` vergleichen, Änderungen übernehmen, die Abweichungen im Kopf behalten, Adressen und SHA-256-Summen der geladenen Dateien anpassen, dann bauen und den Site-Test laufen lassen.
- **Neue Hauptversion:** eine geplante Umstellung. Das Rezept wird mit der dann aktuellen Version von frappe_docker abgeglichen, die Versionen von Python und Node.js werden geprüft, und jede App bekommt ein Tag auf der neuen Hauptversion, siehe [Versionierung](docs/versionierung.md#hauptversionen).
- **Release:** die Schritte in [Versionierung](docs/versionierung.md#release-prozess-für-maintainer).
