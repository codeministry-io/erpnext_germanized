# Roadmap

erpnext_germanized soll ein Image sein, das deutsche Unternehmen ohne eigenen Build betreiben und mit einem Tag-Wechsel aktualisieren können. Diese Seite beschreibt Stand, nächste Schritte und Grundsätze, keine Termine.

## Stand

- **Rezept:** `Containerfile` aus frappe_docker v4.2.0 mit Ghostscript, gepinnten Vorgaben und OCI-Labels, `apps.json` mit Frappe v16.60.2, ERPNext, HRMS, den fünf Apps von ALYF und Steuerbote, siehe [Architektur](architektur.md).
- **Werkzeuge:** `python -m germanized` prüft `apps.json`, leitet die Image-Tags ab, prüft Release-Tags, hebt Versionen an und hält die Tabelle im README aktuell, mit 100 % Testabdeckung, siehe [Entwicklung](entwicklung.md#werkzeuge).
- **Site-Test:** `tests/site/run.sh` installiert alle Apps auf einer frischen Site und prüft Backend und nginx.
- **CI:** Tests, Linters, Security, Image, Release und App versions, siehe [Entwicklung](entwicklung.md#ci).
- **Beispiel** für docker compose und Hinweise für den Betrieb auf Kubernetes mit dem Helm-Chart von Frappe, siehe [Betrieb](betrieb.md).
- **Erstes Release:** `v16.60.0-1` als Image `ghcr.io/encircle360-oss/erpnext_germanized:16.60.0-1`, mit SBOM und Herkunftsangabe, siehe [Changelog](../CHANGELOG.md).

## Nächste Schritte

| Paket | Inhalt | Ergebnis |
|---|---|---|
| Rückmeldungen | Erfahrungen aus ersten Installationen sammeln: fehlende Apps, Einstellungen, die das Beispiel vorbelegen sollte, Fehler im Betrieb. | Issues und Discussions, die in die nächste Revision einfließen. |
| `linux/arm64` | Ein Image auch für Server mit ARM-Prozessoren. Das Rezept von frappe_docker enthält die Schritte für arm64 schon. Offen sind Dauer und Kosten des Builds, ein Site-Test auf arm64 und ob alle Apps dort laufen. ERiC für Steuerbote gibt es nur für Linux x86_64. | Ein Image für beide Plattformen unter denselben Tags. |
| Signierte Images | Images zusätzlich mit cosign signieren, falls Betreiber das brauchen, etwa für Richtlinien in ihrem Cluster, die Signaturen von cosign prüfen. | Eine Signatur, die sich mit `cosign verify` prüfen lässt. |
| Weitere Apps | Apps, die deutsche Unternehmen brauchen, auf Anfrage und nach Prüfung von Lizenz, Pflege und Hauptversion, siehe [Entwicklung](entwicklung.md#eine-app-hinzufügen-oder-entfernen). | Jede neue App mit Site-Test, Dokumentation und Eintrag im Changelog. |
| Demo-Site | Eine öffentliche Site mit Beispieldaten zum Ausprobieren, ohne eigene Installation. | Eine Site mit dem jeweils neuesten Release, regelmäßig zurückgesetzt. |
| Steuerbote | Die weiteren Meldungen von Steuerbote, sobald sie veröffentlicht sind: Dauerfristverlängerung, Zusammenfassende Meldung und die Jahresmeldungen, siehe die [Roadmap von Steuerbote](https://github.com/encircle360-oss/steuerbote/blob/main/docs/roadmap.md). | Jede neue Version von Steuerbote als neue Revision des Images. |

## Offene Punkte

- **Releases von Steuerbote.** `check-versions` und `bump` lesen Releases auf GitHub, Steuerbote veröffentlicht bisher nur Tags. Bis Steuerbote Releases anlegt, kommen seine neuen Versionen von Hand in `apps.json`.

## Grundsätze

- **Upstream zuerst.** Das Image ändert keine App. Fehler in Frappe, ERPNext oder einer App werden beim jeweiligen Projekt gemeldet und dort behoben; ins Image kommt die Korrektur mit dessen nächstem Release.
- **Alles gepinnt.** Apps auf Release-Tags, Frappe, Python, Node.js und wkhtmltopdf über die Vorgaben im `Containerfile`, Images per Tag, Actions per Commit-SHA. Was nicht gepinnt ist, steht mit Begründung im `Containerfile`.
- **Nur die aktuelle Hauptversion** von Frappe und ERPNext, derzeit 16. Ältere Hauptversionen werden nicht weitergebaut.
- **Erst testen, dann veröffentlichen.** Kein Image ohne grünen Site-Test, keine Änderung an den Werkzeugen ohne Test, der vorher fehlschlägt.
- **Nachvollziehbar.** Jedes Release nennt alle Versionen und bringt eine SBOM und eine Herkunftsangabe mit.
- **Nah an frappe_docker.** Das Rezept weicht nur dort vom Original ab, wo es nötig ist, und nennt jede Abweichung. So bleibt jede neue Version von frappe_docker Zeile für Zeile vergleichbar.
