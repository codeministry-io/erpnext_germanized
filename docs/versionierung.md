# Versionierung

Diese Seite beschreibt, wie Releases von erpnext_germanized heißen, welche Image-Tags daraus entstehen, was eine Revision ändert und wie ein Release entsteht. Wie ein Update im Betrieb abläuft, steht in [Betrieb](betrieb.md#updates).

## Das Schema

Ein Release ist ein Git-Tag der Form `v<ERPNext-Version>-<Revision>`, etwa `v16.60.0-1`.

- **ERPNext-Version** ist das Tag von ERPNext in `apps.json` ohne das führende `v`. Das Release `v16.60.0-1` enthält also ERPNext v16.60.0. Frappe und die anderen Apps haben eigene Versionen, die Release-Notes nennen sie alle.
- **Revision** zählt die Releases zu einer ERPNext-Version, beginnend mit 1.

`python -m germanized release-check --ref refs/tags/<tag>` prüft beides, bevor die CI ein Release baut: Die ERPNext-Version des Tags muss das Tag von ERPNext in `apps.json` sein, und die Revision muss mindestens 1 sein.

## Image-Tags

`python -m germanized tags` leitet die Image-Tags aus Git-Ref, Commit und den vorhandenen Release-Tags ab:

| Ereignis | Image-Tags |
|---|---|
| Push auf `main` | `main`, `main-<sha7>` |
| Push des Git-Tags `v16.60.0-1` | `16.60.0-1`, dazu `16.60.0`, `16` und `latest`, soweit kein neueres Release sie trägt |
| Pull Request, Lauf von Hand oder anderer Branch | keine; das Image wird gebaut und getestet, aber nicht veröffentlicht |

`<sha7>` sind die ersten sieben Zeichen des Commits. Alle Tags gehören zu `ghcr.io/encircle360-oss/erpnext_germanized`. Veröffentlicht wird nur aus Pushes, auf `main` oder eines Release-Tags; ein Lauf von Hand baut und testet nur.

Bewegliche Tags gehen nur vorwärts. Neuer als ein Release ist eines mit höherer ERPNext-Version oder eine spätere Revision derselben Version. Ein Release bekommt `16.60.0`, `16` und `latest` nur, solange kein neueres Release das jeweilige Tag trägt: Eine spätere Revision einer älteren ERPNext-Version, etwa `v16.60.0-2` nach `v16.61.0-1`, bekommt ihr volles Tag und `16.60.0`, aber weder `16` noch `latest`. Die CI übergibt dafür die Release-Tags des Repositories mit `--existing "$(git tag -l 'v*')"`.

## Was die Tags bedeuten

| Tag | Bewegt sich | Zeigt auf |
|---|---|---|
| `16.60.0-1` | nein | genau dieses Release |
| `16.60.0` | mit jeder neuen Revision zu ERPNext 16.60.0 | die neueste Revision dieser ERPNext-Version |
| `16` | mit jedem neueren Release auf ERPNext 16 | das neueste Release der Hauptversion |
| `latest` | mit jedem neueren Release, auch beim Wechsel auf eine neue Hauptversion | das neueste Release |
| `main` | mit jedem Push auf `main` | den letzten Build von `main`, kein Release |
| `main-<sha7>` | nein | den Build eines Commits auf `main`, kein Release |

Auch eine neue Revision kann neue Versionen von Frappe und den Apps mitbringen und damit Patches für die Datenbank. Jedes bewegliche Tag kann deshalb beim nächsten Pull eine Version liefern, die `bench migrate` braucht. Ein Container, der ohne Migration auf einer neuen Version startet, arbeitet mit einer Datenbank im alten Stand.

`main` und `main-<sha7>` sind zum Ausprobieren gedacht, nicht für den Betrieb mit echten Daten.

## Was eine Revision ändert

Eine neue Revision entsteht, wenn sich bei gleicher ERPNext-Version etwas anderes im Image ändert:

- eine neue Version von Frappe, HRMS, einer App von ALYF, Insights, CRM, Steuerbote oder Briefbote,
- ein neues Basis-Image, etwa mit Sicherheitskorrekturen aus Debian, oder eine neue Version von Python, Node.js oder wkhtmltopdf,
- eine Änderung am Rezept, etwa ein zusätzliches Systempaket.

Mit einer neuen ERPNext-Version beginnt die Revision wieder bei 1: Auf `v16.60.0-2` folgt etwa `v16.61.0-1`.

## Wie Nutzer pinnen

Für den Betrieb gehört das volle Tag in die Konfiguration, in docker compose so:

```yaml
image: ghcr.io/encircle360-oss/erpnext_germanized:16.60.0-1
```

Im Helm-Chart von Frappe entsprechend `image.tag: "16.60.0-1"`. Noch strenger ist der Digest, der sich auch dann nicht ändert, wenn ein Tag neu vergeben würde:

```bash
docker buildx imagetools inspect ghcr.io/encircle360-oss/erpnext_germanized:16.60.0-1
```

Die Ausgabe nennt unter `Digest` den Wert für `ghcr.io/encircle360-oss/erpnext_germanized:16.60.0-1@sha256:<digest>`. Bei Releases nach 16.60.0-12 ist das der Digest des Index, der für beide Plattformen gilt; die Digests unter `Manifests` gelten je einer Plattform.

Woher ein veröffentlichtes Image kommt, prüft `gh attestation verify` gegen die Herkunftsangabe (Build Provenance), die die CI dazu ablegt. Bei Releases nach 16.60.0-12 nennt sie den Index und die Images beider Plattformen, die Prüfung geht also mit dem Tag wie mit dem Digest einer Plattform:

```bash
gh attestation verify oci://ghcr.io/encircle360-oss/erpnext_germanized:16.60.0-1 --repo encircle360-oss/erpnext_germanized
gh attestation verify oci://ghcr.io/encircle360-oss/erpnext_germanized@sha256:<digest> --repo encircle360-oss/erpnext_germanized
```

Ein Update ist dann ein bewusster Wechsel auf ein neues volles Tag, gefolgt von `bench migrate`.

## Hauptversionen

Es gibt Images nur für die aktuelle Hauptversion von Frappe und ERPNext, derzeit 16. Für Version 17 gehört dazu, das Rezept mit der dann aktuellen Version von frappe_docker abzugleichen, die Versionen von Python und Node.js zu prüfen und für jede App ein Tag auf Version 17 zu wählen. Das ist eine geplante Umstellung, kein gewöhnliches Update. Das Tag `16` bleibt danach auf dem letzten Release mit ERPNext 16 stehen, `latest` wechselt auf 17. Ältere Releases werden nicht neu gebaut.

## Release-Prozess für Maintainer

1. **Versionen anheben.** Der Workflow App versions (`versions.yml`) läuft jeden Montag um 06:00 UTC und lässt sich von Hand starten. Gibt es für Frappe oder eine App ein neueres Release auf ihrer Hauptversion, öffnet er einen Pull Request aus dem Branch `update/apps-<JJJJMMTT>`. Er setzt die Tags in `apps.json`, `FRAPPE_BRANCH` im `Containerfile` und die Spalte Version im README und nennt im Text die Tabelle von `check-versions`. Von Hand geht dasselbe so:

   ```bash
   python -m germanized check-versions    # pinned and newest release side by side
   python -m germanized bump --write      # moves apps.json and FRAPPE_BRANCH to the newest releases
   python -m germanized readme --write    # sets the Version cells of the README table
   ```

   `bump` hebt jede App nur innerhalb ihrer Hauptversion an, Steuerbote und Briefbote mit ihren eigenen Versionsnummern also innerhalb der Hauptversion 0 und Insights innerhalb der Hauptversion 3: Ein neueres Release `v0.x.y` oder `v3.x.y` schlägt der Workflow vor wie bei jeder anderen App, den Wechsel auf die nächste Hauptversion entscheidet ein Maintainer. CRM folgt wie die übrigen Apps der Hauptversion von Frappe und bleibt auf der Reihe v16, auch wenn GitHub ein Release der Reihe v15 als neuestes zeigt. `check-versions` und `bump` lesen dafür die Releases auf GitHub; Entwürfe und Vorabversionen zählen nicht. Eine App, die vor ihrem ersten Release auf einen Branch zeigt, setzt `bump` auf ihr neuestes Release; solange sie auf den Branch zeigt, lehnt `release-check` jedes Release ab. Einen Fork wie erpnext_germany lässt `bump` stehen und sagt das; `check-versions` zeigt daneben das neueste Release des Originals. Zurück zum Original geht es von Hand, sobald ein Release die Korrektur enthält: `url` und `branch` in `apps.json` und die Zeile im README.

2. **Prüfen.** Vor dem Merge die Release-Notes von ERPNext und jeder geänderten App lesen, besonders auf Patches der Datenbank und geänderte Abhängigkeiten. Die CI baut das Image und installiert alle Apps auf einer frischen Site. Die Checks eines Pull Requests, den der Workflow geöffnet hat, starten erst, wenn ein Maintainer sie mit „Approve workflows to run“ freigibt oder den Pull Request schließt und wieder öffnet.

3. **Changelog.** Die Einträge unter `## Unveröffentlicht` in [CHANGELOG.md](../CHANGELOG.md) kommen in einen neuen Abschnitt mit der Überschrift `## [16.60.0-1] - JJJJ-MM-TT`, also der Version ohne `v` und dem Datum des Releases. Der Workflow Release übernimmt den Abschnitt, dessen Überschrift mit der Version beginnt, in die Release-Notes.

4. **Taggen.** Nach dem Merge auf `main`:

   ```bash
   git switch main
   git pull
   git tag -a v16.60.0-1 -m "release v16.60.0-1"
   git push origin v16.60.0-1
   ```

5. **Veröffentlichen.** Der Push des Tags startet den Workflow Release (`release.yml`). Er prüft das Tag mit `release-check`, baut das Image, führt den Site-Test und den Scan auf Schwachstellen aus, veröffentlicht das volle Tag und die beweglichen Tags, die ihm zustehen (siehe [Image-Tags](#image-tags)), legt Herkunftsangabe und SBOM ab und erstellt das GitHub-Release mit der Zusammenfassung von `python -m germanized summary` und dem Abschnitt aus dem Changelog. Schlagen Prüfung, Build oder Site-Test fehl, wird nichts veröffentlicht.

Ein Release, das schon veröffentlicht ist, wird nicht neu getaggt. Eine Korrektur ist eine neue Revision.
