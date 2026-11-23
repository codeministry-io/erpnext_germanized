# Fork codeministry/erpnext_germanized

Dieser Fork baut das Image von [encircle360-oss/erpnext_germanized](https://github.com/encircle360-oss/erpnext_germanized)
für `linux/arm64`, solange upstream das nicht selbst so veröffentlicht. Die Datei kennt upstream nicht; sie kollidiert
deshalb bei keinem Abgleich.

## Warum es den Fork gibt

- **arm64:** Upstream baut das Image nur für `linux/amd64`. Der Fork baut dasselbe Rezept nativ auf einem
  arm64-Runner (`.github/workflows/fork-image.yml`).
- **Scanbar:** Das Image erscheint als einzelnes Manifest ohne Index und ohne Provenance-Attestation. Ein
  Schwachstellen-Scanner prüft so genau das Artefakt, das läuft, und nicht eine amd64-Variante daneben.
- **Schlanker:** Nach dem Build entfernt `python -m germanized prune-node-modules` die Node.js-Pakete, die zur
  Laufzeit niemand lädt (Pull Request #4 im Fork).

Beide Änderungen sollen als Pull Requests an upstream gehen; arm64 liegt dort als
[#25](https://github.com/encircle360-oss/erpnext_germanized/pull/25).

## Wie der Fork upstream folgt

Der Default-Branch ist `fork-test-image`. `main` bleibt ein unveränderter Spiegel von upstream.

| Workflow | Wann | Was |
|---|---|---|
| `upstream-sync.yml` | montags und auf Knopfdruck | merged das neueste upstream-Tag auf `sync/upstream` und hält genau einen Pull Request nach `fork-test-image` offen; ein neueres Tag zieht ihn nach |
| `fork-image.yml` | nach jedem Merge und montags | baut, führt den Site-Test aus und veröffentlicht nur danach `ghcr.io/codeministry/erpnext_germanized:<version>-cm<n>` |

- **Version und Revision:** `<version>` ist das upstream-Tag aus `fork/upstream-tag` ohne `v`, etwa `16.60.0-8`.
  `n` zählt die Builds dieser Version: 1 nach dem Abgleich, jede Woche eins mehr für den Neubau desselben Stands.
- **Spur im Repository:** Zu jedem veröffentlichten Image gehört ein annotierter Git-Tag `cm/<version>-cm<n>`, dessen
  Nachricht den Lauf nennt. Ein Build, dessen Site-Test scheitert, veröffentlicht weder Image noch Git-Tag.
- **Konflikte:** `CHANGELOG.md` und `README.md` übernimmt der Abgleich immer in der Fassung von upstream. Jede andere
  Datei mit Konflikt lässt den Lauf scheitern und öffnet ein Issue mit Tag und Dateiliste; gepusht wird dann nichts.
  Gelöst wird von Hand, mit dem Tag aus dem Issue:

  ```bash
  git fetch upstream --tags
  git switch -C sync/upstream origin/fork-test-image
  git merge --no-ff <tag>                       # Konflikte lösen
  git checkout <tag> -- CHANGELOG.md README.md
  echo <tag> > fork/upstream-tag
  git commit -am "merge upstream <tag>"
  git push --force origin sync/upstream         # danach den Pull Request nach fork-test-image öffnen
  ```

  Solange dieser Pull Request offen ist und dasselbe Tag trägt, lässt der nächste Lauf ihn stehen.
- **Abgeschaltet:** Die Workflows von upstream mit Zeitplan (`versions.yml`, `security.yml`) laufen im Fork nicht.

## Wann der Fork entfallen kann

Wenn upstream in einem Release beides übernommen hat und das Image passend veröffentlicht:

1. `.github/workflows/build.yml` baut `linux/arm64`.
2. Das `Containerfile` kürzt `node_modules` nach dem Build.
3. `ghcr.io/encircle360-oss/erpnext_germanized:<version>` liefert `linux/arm64` als einzelnes Manifest ohne Index.

Der Job „Check whether the fork can go“ in `upstream-sync.yml` prüft diese drei Punkte bei jedem Lauf und schreibt das
Ergebnis in seine Zusammenfassung, je Punkt „erfüllt“ oder „offen“.

## Rückweg auf das upstream-Image

1. Das Image im Betrieb auf `ghcr.io/encircle360-oss/erpnext_germanized:<version>` umstellen.
2. `upstream-sync.yml` und `fork-image.yml` abschalten (`gh workflow disable`).
3. Den Fork archivieren. Die veröffentlichten Images bleiben in der Registry stehen.
