# Fork codeministry/erpnext_germanized

Dieser Fork baut das Image von [encircle360-oss/erpnext_germanized](https://github.com/encircle360-oss/erpnext_germanized)
mit zusätzlichen Apps, die upstream (noch) nicht enthält. Die Datei kennt upstream nicht; sie kollidiert deshalb bei
keinem Abgleich.

> **Geschichte.** Vom 2026-11-23 bis zum 2026-11-24 brachte der Fork arm64 und die Kürzung von `node_modules`; beides hat
> upstream übernommen (#33, #39), und der Fork war ab dem 2026-11-24 archiviert. Seit dem 2026-11-25 läuft er wieder,
> diesmal für **Frappe Insights** (codeministry/cm-k8s-cluster, Spec 018), bis ein upstream-Release Insights enthält.

## Warum es den Fork gibt

- **Zusätzliche Apps:** `fork/extra-apps.json` listet, was der Fork zu upstreams `apps.json` hinzufügt, heute
  `frappe/insights`. `fork-image.yml` hängt die Liste erst im Runner an, nachdem upstreams `apps.json` die eigene
  Prüfung bestanden hat. Die eingecheckte `apps.json` bleibt damit die von upstream, und der Abgleich kollidiert dort
  nie. Die Insights-Version zieht niemand automatisch nach; gehoben wird sie in `fork/extra-apps.json` von Hand.
- **Scanbar:** Das Image erscheint als einzelnes arm64-Manifest ohne Index und ohne Provenance-Attestation. Ein
  Schwachstellen-Scanner prüft so genau das Artefakt, das läuft.

## Wie der Fork upstream folgt

Der Default-Branch ist `fork`. `main` bleibt ein unveränderter Spiegel von upstream.

| Workflow | Wann | Was |
|---|---|---|
| `upstream-sync.yml` | täglich 05:23 UTC und auf Knopfdruck | merged das neueste upstream-Tag **direkt** nach `fork`, ohne Pull Request, und startet `fork-image.yml` |
| `fork-image.yml` | nach jedem Abgleich, bei jedem Push auf `fork` und montags | baut mit den zusätzlichen Apps, führt den Site-Test aus und veröffentlicht nur danach `ghcr.io/codeministry/erpnext_germanized:<version>-cm<n>` |

- **Version und Revision:** `<version>` ist das upstream-Tag aus `fork/upstream-tag` ohne `v`, etwa `16.61.0-6`.
  `n` zählt die Builds dieser Version: 1 nach dem Abgleich, jede Woche eins mehr für den Neubau desselben Stands.
  Der Betrieb (cm-k8s-cluster) folgt diesen Tags per Renovate.
- **Spur im Repository:** Zu jedem veröffentlichten Image gehört ein annotierter Git-Tag `cm/<version>-cm<n>`, dessen
  Nachricht den Lauf nennt. Ein Build, dessen Site-Test scheitert, veröffentlicht weder Image noch Git-Tag.
- **Konflikte:** `CHANGELOG.md` und `README.md` übernimmt der Abgleich immer in der Fassung von upstream. Jede andere
  Datei mit Konflikt lässt den Lauf scheitern und öffnet ein Issue mit Tag und Dateiliste; gepusht wird dann nichts.
  Gelöst wird von Hand, mit dem Tag aus dem Issue:

  ```bash
  git fetch upstream --tags
  git switch fork && git pull
  git merge --no-ff <tag>                       # Konflikte lösen
  git checkout <tag> -- CHANGELOG.md README.md
  echo <tag> > fork/upstream-tag
  git commit -am "merge upstream <tag>"
  git push origin fork
  gh workflow run fork-image.yml --ref fork
  ```

- **Nur über den Sync-Workflow:** Den Knopf „Sync fork“ auf GitHub nicht benutzen. Er merged `main` von upstream,
  ohne `fork/upstream-tag` nachzuziehen, und das Image trüge dann eine Version, die sein Code nicht ist.
  `fork-image.yml` bricht deshalb ab, wenn das oberste Release in `CHANGELOG.md` nicht dem Tag in
  `fork/upstream-tag` entspricht.
- **Abgeschaltet:** Die Workflows von upstream mit Zeitplan (`versions.yml`, `security.yml`) laufen im Fork nicht.
- **Branch `insights-probe`:** die Testimages `-insights-probe.<n>` vom 2026-11-25 und die Vorlage für den späteren
  Upstream-PR mit Insights. Der Betrieb nutzt ihn nicht mehr.

## Wann der Fork entfallen kann

Wenn das neueste upstream-Release jede App aus `fork/extra-apps.json` in seiner `apps.json` führt. Der Job „Check
whether the fork can go“ in `upstream-sync.yml` prüft das bei jedem Lauf und schreibt je App „erfüllt“ oder „offen“
in seine Zusammenfassung.

## Rückweg auf das upstream-Image

1. Das Image im Betrieb auf `ghcr.io/encircle360-oss/erpnext_germanized:<version>` umstellen (arm64-Plattform-Digest).
2. `upstream-sync.yml` und `fork-image.yml` abschalten (`gh workflow disable`).
3. Den Fork archivieren. Die veröffentlichten Images bleiben in der Registry stehen.
