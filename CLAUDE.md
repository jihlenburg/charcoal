# Claude-Arbeitsanweisungen für dieses Repository

## Workflow

1. **Planen**: Vor jeder Änderung einen kurzen Plan formulieren (welche
   Dateien, welche Schritte, in welcher Reihenfolge).
2. **Ausführen**: Plan umsetzen, dabei Tool-Aufrufe möglichst parallelisieren,
   wenn sie unabhängig sind.
3. **Validieren**: Nach der Umsetzung prüfen — Syntax-Check für Scripts,
   Konsistenz der Masse zwischen Script und README, sichtbare Diffs durchgehen.

Kein Schritt dieser Trias darf übersprungen werden.

## Dokumentationspflichten

### `README.md`

Muss bei jeder inhaltlichen Änderung des Designs oder Workflows synchron
gehalten werden. Insbesondere:

- Geometrische Parameter, die im Script geändert werden, müssen in den
  entsprechenden Tabellen/Abschnitten des README aktualisiert werden.
- Neue Dateien im Repo werden im Abschnitt „Dateien" gelistet.
- Gelöschte Features/Dateien dürfen keine verwaisten Verweise hinterlassen.
- Materialwahl und Drucker-Targets werden bei Änderung überall (Script-Header,
  README, ggf. Kommentare) konsistent nachgezogen.

### `TODO.md`

Offene Aufgaben werden als Checkliste gepflegt. Struktur:

- `## Offen` — noch nicht begonnene Aufgaben
- `## In Arbeit` — aktuell laufende Aufgaben
- `## Erledigt` — abgeschlossene Aufgaben (mit Datum)

Aufgaben werden hinzugefügt, sobald sie identifiziert sind, und von
`Offen` → `In Arbeit` → `Erledigt` verschoben, während sie durchlaufen werden.
Erledigte Einträge bleiben als Referenz erhalten, nicht löschen.

### `LOGBOOK.md`

Chronologisches Protokoll der inhaltlichen Entscheidungen und Änderungen.
Für jede substanzielle Änderung ein Eintrag mit:

- Datum (ISO, `YYYY-MM-DD`)
- Kurze Beschreibung der Änderung
- Begründung (warum diese Entscheidung getroffen wurde)
- Falls relevant: verworfene Alternativen

Keine reinen Formatierungs-/Tippfehlerkorrekturen ins Logbook — nur Designs-,
Material-, Workflow- oder Toolchain-Entscheidungen.

## Repo-Konventionen

- **CAD-Toolchain**: build123d + ocp-vscode. FreeCAD wird hier nicht genutzt;
  keine FreeCAD-Scripts oder -Referenzen hinzufügen.
- **Druckerziel**: HP Multi Jet Fusion, PA11. Bei Materialwechsel überall
  nachziehen (Script, README, ggf. CLAUDE.md).
- **Sprache**: README und Logbuch auf Deutsch, Script-Kommentare auf Englisch
  (damit das Script auch in internationalen Kontexten lesbar bleibt).
- **Keine automatischen Git-Commits** — erst auf explizite Aufforderung
  committen oder pushen.

## Tool-Nutzung

- `rg` / `ripgrep` statt `grep`.
- Dateisuche über `Glob`, keine `find`-Aufrufe.
- Dedizierte Tools (`Read`, `Edit`, `Write`) bevorzugen vor `Bash cat`/`sed`/
  `echo >`.
