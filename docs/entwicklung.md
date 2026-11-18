# Entwicklung

Diese Seite beschreibt Aufbau, Einrichtung, Werkzeuge, Tests, Stil und CI. Wie ein Beitrag abläuft, steht in [CONTRIBUTING.md](../CONTRIBUTING.md), wie das Image aufgebaut ist, in [Architektur](architektur.md).

## Aufbau des Repositories

```text
erpnext_germanized/            Repository
├── apps.json                  Apps und ihre Release-Tags im Format von frappe_docker, Reihenfolge = Installation
├── Containerfile              Rezept des Images, aus frappe_docker v4.2.0 übernommen und angepasst
├── build.sh                   lokaler Build mit denselben Eingaben wie in der CI
├── germanized/                Werkzeuge in Python, nur Standardbibliothek, python -m germanized
│   ├── apps.py                apps.json lesen und gegen die Regeln des Images prüfen
│   ├── containerfile.py       Pins aus den Vorgaben der ARGs und das erste FROM des Containerfile lesen
│   ├── tags.py                Image-Tags aus Git-Ref und Commit, Prüfung der Release-Tags
│   ├── versions.py            neueste Releases auf GitHub nachsehen, Pins anheben und schreiben
│   ├── readme.py              Tabelle „Enthaltene Apps“ im README prüfen und ihre Versionen setzen
│   ├── summary.py             Zusammenfassung eines Builds für Workflow-Läufe und Release-Notes
│   └── __main__.py            Kommandozeile
├── tests/                     pytest-Tests der Werkzeuge
│   └── site/                  Site-Test des Images: compose.yaml und run.sh
├── examples/compose.yaml      Beispiel für docker compose
├── docs/                      Dokumentation
├── LICENSES/                  Lizenztext von frappe_docker (MIT) für das Containerfile
├── .github/workflows/         CI: Tests, Linters, Security, Image, Release, App versions
├── .github/dependabot.yml     wöchentliche Updates für GitHub Actions, Basis-Image, Compose-Dateien und pip
├── .github/ISSUE_TEMPLATE/    Vorlagen für Fehler und Wünsche, Verweise auf Discussions, Matrix und SECURITY.md
├── .github/PULL_REQUEST_TEMPLATE.md
│                              Vorlage für Pull Requests
├── .pre-commit-config.yaml    Hooks für pre-commit
├── pyproject.toml             Paketdaten der Werkzeuge, Einstellungen für ruff, pytest und coverage
└── requirements-dev.txt       Entwicklungswerkzeuge, exakt gepinnt
```

Die Werkzeuge unter `germanized/` kommen nicht ins Image. Sie prüfen das Rezept, leiten die Tags ab und heben Versionen an.

## Einrichtung

Du brauchst Python 3.14, für Build und Site-Test zusätzlich Docker mit Buildx und dem Compose-Plugin sowie `jq` und `timeout`.

```bash
git clone https://github.com/<dein-konto>/erpnext_germanized.git
cd erpnext_germanized
python3.14 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install
```

`requirements-dev.txt` bringt coverage, pre-commit, pytest, pytest-cov, ruff und zizmor in festen Versionen, dieselben wie bei Steuerbote. Zur Laufzeit brauchen die Werkzeuge nur die Standardbibliothek. `pre-commit install` richtet die Hooks aus `.pre-commit-config.yaml` ein.

## Werkzeuge

Alle Befehle laufen im Wurzelverzeichnis des Repositories und lesen `apps.json`, `Containerfile` und `README.md` von dort. Bei jedem Problem enden sie mit dem Exit-Code 1 und einer Meldung.

| Befehl | Was er tut |
|---|---|
| `python -m germanized validate` | prüft `apps.json` gegen die Regeln unten |
| `python -m germanized tags --ref REF --sha SHA` | gibt die Image-Tags eines Git-Refs aus, durch Kommas getrennt, siehe [Versionierung](versionierung.md#image-tags) |
| `python -m germanized release-check --ref REF` | prüft ein Release-Tag wie `refs/tags/v16.60.0-1` gegen das Tag von ERPNext in `apps.json` |
| `python -m germanized summary [--tags a,b]` | gibt Pins, Apps und Tags eines Builds als Markdown aus, für die Zusammenfassung eines Workflow-Laufs und die Release-Notes |
| `python -m germanized check-versions` | stellt jedem Pin das neueste Release auf seiner Hauptversion gegenüber |
| `python -m germanized bump [--write]` | zeigt, welche Pins sich anheben lassen; mit `--write` schreibt es `apps.json` und `FRAPPE_BRANCH` im `Containerfile` |
| `python -m germanized readme --check` | prüft die Tabelle „Enthaltene Apps“ im README gegen die Pins |
| `python -m germanized readme --write` | setzt die Spalte Version dieser Tabelle auf die Pins |

`check-versions` und `bump` fragen die API von GitHub ab. Ohne Token lässt GitHub nur 60 Anfragen in der Stunde zu; ist die Umgebungsvariable `GITHUB_TOKEN` gesetzt, schicken die Werkzeuge das Token mit.

Regeln für `apps.json`, die `validate` prüft:

- ein JSON-Array aus Einträgen mit genau den Schlüsseln `url` und `branch`, nicht leer,
- `url` hat die Form `https://github.com/<owner>/<repo>`, ohne `/` am Ende und ohne `.git`,
- keine App doppelt,
- `branch` ist ein Release-Tag der Form `vX.Y.Z`,
- der erste Eintrag ist `https://github.com/frappe/erpnext`,
- jede App hat dieselbe Hauptversion wie Frappe, außer den Apps in `INDEPENDENTLY_VERSIONED` in `germanized/apps.py`, bisher nur Steuerbote.

Die Tabelle im README hat die Spalten `| App | Version | Zweck | Lizenz |`, zuerst eine Zeile für `[frappe](https://github.com/frappe/frappe)`, dann eine Zeile je App in der Reihenfolge von `apps.json`. In der Spalte App steht ein Link mit dem Namen des Repositories, in der Spalte Version das Tag. `readme --write` ändert nur die Spalte Version; Zweck und Lizenz werden von Hand gepflegt.

## Tests

```bash
pytest
```

`pytest` führt die Tests unter `tests/` aus und misst dabei die Abdeckung von `germanized`, Zeilen und Zweige. Unter 100 % schlägt der Lauf fehl (`--cov-fail-under=100` in `pyproject.toml`). Die Tests brauchen kein Netz: Wo ein Werkzeug GitHub fragt, bekommt es im Test eine Funktion, die feste Antworten liefert. Weitere Tests prüfen das Repository selbst, etwa dass `apps.json` gültig ist und dass das erste `FROM` des `Containerfile` zu `PYTHON_VERSION` und `DEBIAN_BASE` passt.

## Testgetrieben arbeiten

1. **Rot:** Schreib zuerst einen Test, der ohne die Änderung fehlschlägt, und sieh ihn fehlschlagen.
2. **Grün:** Schreib die kleinste Änderung, die ihn bestehen lässt.
3. **Aufräumen:** Verbessere Namen und Struktur, während alle Tests grün bleiben.

Kein bestehender Test wird abgeschwächt, übersprungen oder gelöscht, um grün zu werden. Die Werkzeuge behalten 100 % Abdeckung. Testnamen beschreiben die Regel, die sie prüfen.

## Stil

- **ruff** mit der Konfiguration in `pyproject.toml`, wie bei Steuerbote: Einrückung mit Tabs, Zeilen bis 110 Zeichen, doppelte Anführungszeichen, Python 3.14 als Ziel. Regelgruppen F, E, W, I, UP, B, RUF, S, SIM, C4 und T20; ausgenommen sind E101 und W191 wegen der Tabs und E501, weil die Zeilenlänge der Formatierer setzt. In Tests ist `assert` erlaubt.
- **Nur die Standardbibliothek** zur Laufzeit, mit `pathlib`, `dataclasses` und Typangaben. Docstrings an öffentlichen Funktionen.
- **Shell:** `set -euo pipefail`, frei von Befunden von shellcheck.
- **Containerfile:** frei von Befunden von hadolint. Wo das Original von frappe_docker eine Regel verletzt, steht die Ausnahme mit Begründung direkt an der Anweisung, damit sich das Rezept weiter Zeile für Zeile mit dem Original vergleichen lässt.
- **Englisch im Code**, auch in Kommentaren, Meldungen der Werkzeuge und Namen der Workflow-Schritte. Dokumentation, Issues und Pull Requests auf Deutsch.
- **Kommentare erklären das Warum**, nie das Was und nie die Geschichte einer Änderung.
- **pre-commit** führt ruff (`ruff check --fix` und `ruff format`), shellcheck und zizmor aus und prüft JSON und YAML, Leerzeichen am Zeilenende (außer in Markdown), den Zeilenumbruch am Dateiende und große Dateien. Die Lizenztexte bleiben unverändert.

## Lokaler Build und Site-Test

```bash
./build.sh                                   # builds erpnext_germanized:local for linux/amd64
./tests/site/run.sh erpnext_germanized:local
```

`build.sh` prüft zuerst `apps.json` mit `python3 -m germanized validate` und baut dann mit `docker buildx build`: `apps.json` als Secret `apps_json`, `CACHE_BUST` aus der SHA-256-Summe von `apps.json` und `VERSION` aus `git describe --tags --always --dirty`. Optionen: `--tag TAG` für einen anderen Namen, `--push` schiebt das Image in die Registry von `TAG`, statt es lokal zu laden, `--no-cache` baut jede Schicht neu, `--platform` wählt eine andere Plattform als `linux/amd64`.

`tests/site/run.sh IMAGE` prüft ein Image so, wie die CI es vor jeder Veröffentlichung tut:

1. Die Apps im Image entsprechen `apps.json`, jede aus dem gepinnten Tag gebaut.
2. Ghostscript ist da, mit dem Profil `srgb.icc` für eu_einvoice.
3. MariaDB 11.8 und Redis starten aus `tests/site/compose.yaml`.
4. In einem Container des Images legt `bench new-site` die Site `test.localhost` mit allen Apps an, und `bench --site test.localhost list-apps` nennt jede davon.
5. gunicorn, der Standardbefehl des Images, beantwortet `/api/method/ping` mit `pong` und liefert die Anmeldeseite als HTML.
6. nginx vor dem Backend beantwortet den Ping ebenfalls und liefert die Assets aus.

Zum Schluss entfernt das Skript alle Container und Volumes. Nach 20 Minuten bricht es ab. Die Passwörter der Testsite stehen nur in `tests/site/compose.yaml` und gelten nur für diese Wegwerf-Site.

## CI

Ein Pull Request wird erst gemergt, wenn alle Jobs grün sind. Jeder Workflow liest den Inhalt des Repositories nur (`contents: read`); Rechte zum Schreiben bekommen einzelne Jobs, die sie brauchen. Alle Actions sind über den vollen Commit-SHA gepinnt, mit der Version als Kommentar.

| Workflow | Wann | Was er tut |
|---|---|---|
| Tests (`tests.yml`) | Pull Requests, Pushes auf `main`, von Hand | `ruff check`, `ruff format --check`, `pytest` mit 100 % Abdeckung, `python -m germanized validate` und `python -m germanized readme --check` |
| Linters (`linters.yml`) | Pull Requests, Pushes auf `main`, von Hand | pre-commit auf allen Dateien, darin shellcheck für `build.sh` und `tests/site/run.sh`; hadolint auf dem `Containerfile`; zizmor auf den Workflows und den Konfigurationen von Dependabot und pre-commit |
| Security (`security.yml`) | Pull Requests, Pushes auf `main`, montags 04:17 UTC, von Hand | gitleaks über die ganze Git-Historie, trivy über die Konfiguration im Repository, etwa `Containerfile` und Compose-Dateien; wöchentlich und von Hand zusätzlich trivy über das veröffentlichte Image `latest` |
| Image (`build.yml`) | Pull Requests und Pushes auf `main`, die `Containerfile`, `apps.json`, `build.sh`, `tests/site/`, `LICENSES/` oder den Workflow selbst ändern; von Hand; als Teil von Release | baut das Image, führt den Site-Test aus und scannt das Image mit trivy; auf `main` veröffentlicht es danach die Tags `main` und `main-<sha7>` mit Herkunftsangabe und SBOM |
| Release (`release.yml`) | Push eines Tags `v*` | `release-check`, dann Image wie oben mit den Tags des Releases, danach das GitHub-Release mit Release-Notes und SBOM |
| App versions (`versions.yml`) | montags 06:00 UTC, von Hand | hebt die Pins mit `bump --write` an und öffnet bei Änderungen einen Pull Request, siehe [Versionierung](versionierung.md#release-prozess-für-maintainer) |

**Was einen Pull Request anhält und was nur berichtet.** Tests, Linters, gitleaks, der Scan der Konfiguration und im Workflow Image Build und Site-Test halten einen Pull Request an, wenn sie fehlschlagen. Die Scans der Images auf Schwachstellen, im Workflow Image vor jeder Veröffentlichung und wöchentlich für `latest`, sind Berichte: Ihre Befunde kommen aus Debian und den Apps und verschwinden mit einem neuen Build oder einem Update, deshalb halten sie kein Image an. Ihre Befunde landen in Code Scanning; bei Pull Requests aus Forks, die nichts hochladen dürfen, stehen sie im Log des Laufs.

**Veröffentlichen.** Nur Pushes auf `main` und Release-Tags in `encircle360-oss/erpnext_germanized` veröffentlichen ein Image, mit dem `GITHUB_TOKEN` des Laufs. Pull Requests und Forks bauen und testen nur. Der Workflow Image baut zuerst ein lokales Image, testet es und schiebt danach dasselbe Image aus dem Cache in die Registry; ein Schritt prüft, dass die veröffentlichten Schichten die getesteten sind. Der Cache des Builds liegt als `ghcr.io/encircle360-oss/erpnext_germanized:buildcache` in der Registry. Herkunftsangabe und Code Scanning nutzt die CI nur in einem öffentlichen Repository; das prüft der Workflow bei jedem Lauf.

**Dependabot** schlägt jede Woche Updates vor (`.github/dependabot.yml`): für die GitHub Actions, für das Basis-Image im ersten `FROM` des `Containerfile`, für die Images in `tests/site/compose.yaml` und `examples/compose.yaml` und für die pip-Pakete aus `requirements-dev.txt`. Schlägt Dependabot ein Basis-Image mit anderer Python-Version oder anderem Debian vor, gehören `PYTHON_VERSION` und `DEBIAN_BASE` von Hand dazu; bis beide passen, schlagen die Tests fehl.

## Pins und wo sie stehen

| Was | Wo |
|---|---|
| Apps | `apps.json`, Release-Tags |
| Frappe | `FRAPPE_BRANCH` im `Containerfile` |
| Basis-Image, Python, Debian | erstes `FROM` des `Containerfile`, dazu `PYTHON_VERSION` und `DEBIAN_BASE` |
| Node.js, wkhtmltopdf | `NODE_VERSION`, `WKHTMLTOPDF_VERSION` und `WKHTMLTOPDF_DISTRO` im `Containerfile` |
| Dateien aus frappe_docker | Adressen mit `v4.2.0` und SHA-256-Summen im `Containerfile` |
| MariaDB, Redis | `tests/site/compose.yaml` und `examples/compose.yaml`, per Tag |
| GitHub Actions | in den Workflows, per Commit-SHA mit Version als Kommentar |
| Entwicklungswerkzeuge | `requirements-dev.txt` (`==`), Hooks in `.pre-commit-config.yaml` über `rev`, gitleaks mit Version und SHA-256 in `security.yml` |

Eine Version, die an mehreren Stellen steht, etwa ruff in `requirements-dev.txt` und `.pre-commit-config.yaml`, wird an allen Stellen gleichzeitig angehoben.

## Eine App hinzufügen oder entfernen

Hinzufügen:

1. **Prüfen**, ob die App passt: Releases als Tags `vX.Y.Z`, dieselbe Hauptversion wie Frappe, eine Lizenz, die eine Weitergabe im Image erlaubt, gepflegt und für ERPNext 16 freigegeben (`[tool.bench.frappe-dependencies]` in ihrer `pyproject.toml`).
2. **Test zuerst**, falls sich eine Regel ändert, etwa für eine App mit eigener Versionierung, die in `INDEPENDENTLY_VERSIONED` kommt.
3. **`apps.json`:** einen Eintrag mit `url` und `branch` an der Stelle, an der die App installiert werden soll, also nach den Apps, die sie voraussetzt, und vor Steuerbote.
4. **README:** eine Zeile in der Tabelle „Enthaltene Apps“ an derselben Stelle, mit Zweck aus dem README der App und ihrer Lizenz. `python -m germanized readme --check` muss grün sein.
5. **Beispiel und Dokumentation:** `--install-app` in `create-site` von [examples/compose.yaml](../examples/compose.yaml) und die Liste im Helm-Beispiel in [Betrieb](betrieb.md#auf-kubernetes) ergänzen, jeweils mit dem Namen, unter dem bench die App kennt (der Name aus ihrer `pyproject.toml`). Dazu ein Abschnitt in [Apps](apps.md) und ein Eintrag im [Changelog](../CHANGELOG.md).
6. **Lokal prüfen:** `python -m germanized validate`, `./build.sh` und `./tests/site/run.sh erpnext_germanized:local`.

Entfernen geht in umgekehrter Reihenfolge und ist für bestehende Sites ein Bruch: Eine Site, auf der die App installiert ist, lässt sich mit einem Image ohne die App nicht mehr migrieren. Der Changelog sagt deshalb, was Betreiber vorher tun, nämlich die App mit `bench --site <site> uninstall-app <app>` entfernen, solange das alte Image läuft. Das löscht die Daten der App, also vorher sichern.

## Commits

- Commit-Nachrichten sind englisch, ein Satz, klein geschrieben, im Imperativ, und vervollständigen den Satz „If applied, this commit will …“, etwa `add the site test` oder `pin the actions by digest`.
- Keine Ticket-Präfixe, keine Fußzeilen (Trailer).
- Branches heißen nach dem Thema. Auf `main` wird nicht direkt committet.
- Ein Thema pro Pull Request, die Dokumentation im selben Pull Request.
