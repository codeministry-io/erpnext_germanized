## Was ändert sich?

<!-- Ein Thema pro Pull Request. Was ändert sich für Betreiber, was intern? -->

## Quelle

<!-- Welche Quelle belegt die Änderung? Release-Notes, README oder Dokumentation einer App, Quelltext von Frappe, Dokumentation von frappe_docker. -->

## Checkliste

- [ ] Tests zuerst: Jede Änderung an den Werkzeugen hat einen Test, der ohne sie fehlschlägt. Kein Test wurde abgeschwächt.
- [ ] README, `docs/` und `CHANGELOG.md` passen zur Änderung.
- [ ] Neue Pins sind an ihrer Quelle geprüft: Apps per Release-Tag, Images per Tag, Actions per Commit-SHA mit Version als Kommentar.
- [ ] Keine Passwörter, Schlüssel, Tokens, Sicherungen oder echten Geschäftsdaten in Code, Tests, Beispielen oder Screenshots.
- [ ] `pre-commit run --all-files` und `pytest` laufen lokal durch.
- [ ] Bei Änderungen am Image: `./build.sh` und `./tests/site/run.sh erpnext_germanized:local` laufen durch, oder die CI zeigt es.
