# Sicherheit

## Unterstützte Versionen

Sicherheitskorrekturen gibt es für den Branch `main` und das jeweils neueste Release. Ältere Releases werden nicht neu gebaut; eine Korrektur kommt als neue Revision, siehe [Versionierung](docs/versionierung.md).

## Sicherheitslücke melden

Bitte **nicht** als öffentliches Issue. Sende eine Beschreibung an **oss@encircle360.com** oder nutze die private Meldefunktion von GitHub ([„Report a vulnerability“](https://github.com/encircle360-oss/erpnext_germanized/security/advisories/new) unter *Security*).

Hilfreich sind: betroffenes Image-Tag oder Digest, Schritte zum Nachstellen, mögliche Auswirkungen und, wenn vorhanden, ein Vorschlag zur Behebung. Keine echten Passwörter, Schlüssel, Tokens, Sicherungen oder Geschäftsdaten mitschicken.

Wir bestätigen den Eingang so schnell wie möglich, in der Regel innerhalb weniger Werktage, und stimmen die Veröffentlichung einer Korrektur mit dir ab.

## Lücken in der enthaltenen Software

Das Image enthält Software anderer Projekte: Frappe, ERPNext, HRMS, die Apps von ALYF, Insights, CRM, Steuerbote, Briefbote, die Python- und Node-Pakete der Apps und das Basis-Image `python:3.14-slim-trixie` mit seinen Debian-Paketen. Lücken darin bitte direkt beim jeweiligen Projekt melden:

- **Frappe, ERPNext und HRMS** über [frappe.io/security](https://frappe.io/security), wie es die Sicherheitsrichtlinien von Frappe und ERPNext vorsehen.
- **Insights** ebenfalls über [frappe.io/security](https://frappe.io/security), wie es seine [SECURITY.md](https://github.com/frappe/insights/blob/v3.51.0/SECURITY.md) vorsieht. **CRM** hat zum Tag v16.5.0 keine eigene Sicherheitsrichtlinie; Meldungen dazu gehen am besten ebenfalls über [frappe.io/security](https://frappe.io/security) an die Frappe Technologies Pvt. Ltd.
- **Apps von ALYF** über das jeweilige Repository unter [github.com/alyf-de](https://github.com/alyf-de). erpnext_germany und eu_einvoice nehmen Meldungen über die private Meldefunktion von GitHub an.
- **Steuerbote** wie in seiner [SECURITY.md](https://github.com/encircle360-oss/steuerbote/blob/main/SECURITY.md) beschrieben.
- **Briefbote** wie in seiner [SECURITY.md](https://github.com/encircle360-oss/briefbote/blob/main/SECURITY.md) beschrieben.
- **Debian-Pakete des Basis-Images** an das [Sicherheitsteam von Debian](https://www.debian.org/security/), **Python** an das [Python Security Response Team](https://www.python.org/dev/security/).

Ist eine Korrektur veröffentlicht, wird das Image neu gebaut und als neue Revision veröffentlicht. Neue Versionen der Apps findet der wöchentliche Workflow App versions, ein neues Basis-Image schlägt Dependabot vor. Korrekturen aus Debian kommen mit jedem neuen Build ins Image; wann einer fällig ist, zeigt der wöchentliche Scan des Images `latest` für beide Plattformen.

## Was das Repository zusichert

- **Keine Zugangsdaten im Image.** Die Passwörter für Datenbank und Administrator setzt der Betreiber beim Anlegen der Site. Das Beispiel für docker compose enthält nur Platzhalter `CHANGE_ME`, der Site-Test nur erfundene Passwörter für eine Wegwerf-Site.
- **Veröffentlichen nur aus diesem Repository.** Images entstehen nur aus `main` und aus Release-Tags von `encircle360-oss/erpnext_germanized`, mit dem `GITHUB_TOKEN` des Laufs. Pull Requests melden sich nicht an der Registry an.
- **Kein Image ohne Test.** Vor jeder Veröffentlichung installiert der Site-Test alle Apps auf einer frischen Site, und ein Schritt prüft, dass das veröffentlichte Image das getestete ist.
- **Gepinnt und geprüft.** GitHub Actions sind per Commit-SHA gepinnt, die Dateien aus frappe_docker und die Pakete von wkhtmltopdf per SHA-256, die Apps per Release-Tag. Dependabot, gitleaks, zizmor, hadolint und trivy laufen in der CI. Die Scans der Images auf Schwachstellen sind Berichte und halten kein Image an, siehe [Entwicklung](docs/entwicklung.md#ci).
- **Nachvollziehbar.** Zu jedem veröffentlichten Image gibt es eine SBOM und eine Herkunftsangabe von GitHub, die `gh attestation verify` prüft.
