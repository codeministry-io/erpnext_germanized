# Mitwirken an erpnext_germanized

Issues und Pull Requests sind willkommen. erpnext_germanized ist ein fertiges Container-Image mit ERPNext und deutschen Apps, gebaut aus `apps.json` mit dem Rezept von frappe_docker. Diese Seite beschreibt, wie ein Beitrag abläuft und welche Regeln gelten. Die Regeln gelten für Menschen und für Coding-Agenten gleichermaßen, siehe [AGENTS.md](AGENTS.md).

## Fehler und Wünsche melden

Bitte ein [Issue über die Vorlagen](https://github.com/encircle360-oss/erpnext_germanized/issues/new/choose) anlegen. Vorher lohnt ein Blick in die [Roadmap](docs/roadmap.md) und die offenen Issues. Fragen und Austausch gehen in die [Discussions](https://github.com/encircle360-oss/erpnext_germanized/discussions) oder auf [Matrix](https://matrix.to/#/#oss:encircle360.com).

Hierher gehören Fehler im Image, im Rezept, im Beispiel, in den Werkzeugen und in der Dokumentation. Fehler in Frappe, ERPNext oder einer der Apps gehören zum jeweiligen Projekt, die Links stehen im [README](README.md#community-support).

**Keine Passwörter, Schlüssel, Tokens, Inhalte von `site_config.json`, Sicherungen oder echten Geschäftsdaten** in Issues, Logs, Screenshots oder Pull Requests. Firmen, Beträge und Belege dürfen erfunden sein, solange der Fehler nachvollziehbar bleibt. Sicherheitslücken bitte nicht öffentlich melden, sondern wie in [SECURITY.md](SECURITY.md) beschrieben.

## Ein Pull Request

1. **Fork und Branch.** Branches heißen nach dem Thema, etwa `beispiel-reverse-proxy`.
2. **Test zuerst.** Jede Änderung an den Werkzeugen unter `germanized/` beginnt mit einem Test, der ohne sie fehlschlägt. Kein Test wird abgeschwächt, übersprungen oder gelöscht, um grün zu werden. Die Werkzeuge haben 100 % Testabdeckung, und das bleibt so. Änderungen am Image prüft der Site-Test.
3. **Quelle nennen.** Jede neue Version und jede Aussage über eine App braucht eine Quelle: Release-Notes, README oder Dokumentation des Projekts, für Optionen von bench der Quelltext von Frappe. Die Quelle steht im Pull Request und, wo sie bleibt, in `docs/`.
4. **Ein Thema pro Pull Request**, Dokumentation und Changelog im selben Pull Request. Kleine Schritte sind leichter zu prüfen.
5. **Lokal prüfen:** `pre-commit run --all-files` und `pytest`. Wer `Containerfile`, `apps.json` oder `build.sh` ändert, baut zusätzlich mit `./build.sh` und lässt `./tests/site/run.sh erpnext_germanized:local` laufen, siehe [Entwicklung](docs/entwicklung.md).
6. **Pull Request stellen.** Die Vorlage fragt nach Änderung, Quelle und Checkliste. Die CI muss grün sein.
7. **Review.** Neue Apps, neue Hauptversionen und Änderungen am Rezept werden erst gemergt, wenn ein Maintainer sie geprüft hat. Rückfragen im Review sind normal und kein Urteil über den Beitrag.

## Regeln

- **Nur die aktuelle Hauptversion** von Frappe und ERPNext (derzeit 16). Keine Images für ältere Hauptversionen.
- **Alles gepinnt.** Apps auf Release-Tags in `apps.json`; Frappe, Python, Node.js und wkhtmltopdf über die Vorgaben im `Containerfile`; Images in Compose-Dateien per Tag; GitHub Actions per vollem Commit-SHA mit der Version als Kommentar; Entwicklungswerkzeuge exakt (`==`) in `requirements-dev.txt`.
- **Upstream zuerst.** Das Image ändert keine App. Ein Fehler in einer App wird beim Projekt gemeldet und kommt mit dessen nächstem Release ins Image.
- **Nah am Original.** Das `Containerfile` weicht nur so weit von frappe_docker ab wie nötig, und sein Kopf nennt jede Abweichung.
- **Werkzeuge nur mit der Standardbibliothek.** Was für die Entwicklung dazukommt, wird exakt gepinnt und im Pull Request begründet.
- **Englisch im Code**, auch in Kommentaren, Meldungen der Werkzeuge und Namen von Workflow-Schritten. Dokumentation, Issues und Pull Requests auf Deutsch, deutsche Fachbegriffe bleiben deutsch.
- **Kommentare erklären das Warum**, nie das Was und nie die Geschichte einer Änderung. Eine bessere Benennung schlägt einen Kommentar.
- **Stil:** ruff mit der Konfiguration in `pyproject.toml` (Tabs, 110 Zeichen, doppelte Anführungszeichen), shellcheck für die Shell-Skripte, hadolint für das `Containerfile`.
- **Keine echten Daten, keine Geheimnisse.** Passwörter in Tests sind erfunden, im Beispiel stehen nur Platzhalter `CHANGE_ME`. Die CI erreicht die Registry nur mit dem `GITHUB_TOKEN` des Laufs.

## Commits

Commit-Nachrichten sind englisch, ein Satz, klein geschrieben, im Imperativ, und vervollständigen den Satz „If applied, this commit will …“: `add the site test`, `pin the actions by digest`. Keine Ticket-Präfixe, keine Fußzeilen. Eine Nachricht beschreibt, was sich ändert und warum, wenn das Warum nicht offensichtlich ist.

## Umgangston

Wir gehen respektvoll miteinander um, nehmen Kritik an der Sache an und nicht persönlich, und gehen davon aus, dass alle ihr Bestes geben. Wer das nicht einhält, wird von den Maintainern angesprochen und notfalls ausgeschlossen.

## Lizenz der Beiträge

Mit deinem Beitrag stimmst du zu, dass er unter der [Apache License 2.0](LICENSE) veröffentlicht wird, und bestätigst, dass du das Recht hast, ihn unter dieser Lizenz beizusteuern. Ausgenommen ist das `Containerfile`: Es steht wie das Original von frappe_docker unter der MIT-Lizenz (`LICENSES/frappe_docker.MIT.txt`), und Beiträge dazu ebenso.
