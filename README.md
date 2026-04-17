# Aktivkohlefilter-Einsatz (Passivlüftung mit aktiven Absaugungen)

Parametrischer Filterkorb (Grundkörper + Deckel) für Wohnungslüftung durch
Aktivkohle, ausgelegt für HP Multi Jet Fusion in **PA11** (BASF Ultrasint PA11
oder vergleichbar).

Script: [`carbon_filter_build123d.py`](./carbon_filter_build123d.py) (build123d).

## Konstruktionsprinzip

**Vertikaler Luftstrom durch den Filter.** Die Luft tritt durch das Hex-Gitter
auf einer Z-Seite (Deckel) ein, durchströmt das Aktivkohlebett und tritt durch
das Hex-Gitter auf der anderen Z-Seite (Boden) aus. Im Skript-Koordinatensystem
ist Z die Luftstromachse; beim Einbau wird die Kassette um 90° gekippt, sodass
Z horizontal zur Schachttiefe wird.

### Befüllung (Kassette stehend, Deckel oben)

1. Deckel abnehmen (beide Rastnasen gleichzeitig eindrücken)
2. Filtervlies auf den Boden legen (3 mm, dichtet Hex gegen Granulatdurchfall)
3. Aktivkohlegranulat einfüllen (~29 mm Schüttung, ~78 g bei 450 kg/m³)
4. Zweites Filtervlies obenauf
5. Deckel aufsetzen und eindrücken bis beide Nasen hörbar einrasten

## Einbaukontext

Der Schacht am Fensterrahmen hat 70 mm harte Innenbreite (mit je ca. 5 mm
Schaumstoff an beiden Seiten → 80 mm weich), 100 mm harte Höhe und 100 mm
Tiefe. Luftrichtung: hinten → vorne, angetrieben von drei aktiven
Wohnungs­absaugungen (3 Fenster × 2 Schächte = 6 parallele Zuluftpfade).

**Einbaulage (wichtig)**: Die Kassette wird mit dem **Deckel nach hinten**
eingeschoben, der **Boden zeigt nach vorne** in die Wohnung. Gründe:

- Der Y-Flanschüberstand (je 10 mm oben und unten) ist der Fingergriff.
  Beim Ziehen kommt immer die gesamte Kassette mit — nie nur der Deckel.
- Der Luftstrom drückt den Deckel in seinen Sitz, nicht heraus.
- Der Flansch am Boden fungiert als **Einschub-Stopper und Fingergriff**.
  Er ragt **nur in Y-Richtung** (vertikal im Schacht) über den Körper
  hinaus — in X bleibt er auf Körperbreite, weil die harte Schachtbreite
  70 mm nicht überschritten werden darf. Flansch-Footprint: 62 × 113 mm vs.
  Schacht-Hartöffnung 70 × 100 mm — die je 10 mm-Überstände oben und unten
  fangen an der Schacht-Frontkante und geben gleichzeitig bequem Platz für
  Daumen/Zeigefinger. Die Kassette steht damit `floor = 2.2 mm` aus der
  Öffnung heraus — klar unter der 5-mm-Grenze.

### Abdichtung mit Moosgummi

Die Y-Flächen der Kassette (im Skript-Frame oben/unten) kontaktieren im Schacht
die **harten** oberen und unteren Schachtwände. Dafür sind sie glatt und
durchbruchfrei ausgelegt. Vor dem Einschieben werden **Moosgummistreifen** auf
diese beiden Flächen geklebt; sie pressen sich beim Einschub an und dichten
axial gegen Leckluft vorbei am Filterbett.

Die X-Flächen (im Skript-Frame links/rechts) haben die Snap-Durchbrüche und
pressen sich in den seitlichen Schaumstoff — auch hier entsteht eine Dichtung
durch den Schaum.

## Geometrie

- Zwei Teile: Grundkörper (Trog mit integriertem Flansch + Boden) und Deckel
- Körper-Aussenmasse: **62 (X) × 93 (Y) × 40 (Z)** mm
- Bodenflansch: **62 × 113 × 2.2** mm (Z = 0 … 2.2) — nur in Y breiter als Körper
  (je 10 mm Überstand oben und unten als Stopper + Fingergriff)
- Wand 2.2 mm, Boden 2.2 mm, Deckel 2.5 mm
- Hex-Perforation identisch auf **Boden** und **Deckel** (Z-Flächen):
  10 mm flat-to-flat, 1.2 mm Stegbreite, 4 mm Randabstand → 28 Löcher pro
  Fläche, ~48 % Offenfläche (24 cm² auf 51 cm² Kavität)
- Rabbet-Sitz am oberen Rand, 1.0 mm Schulter, 2.5 mm tief
- Passungsspiel 0.30 mm pro Seite (MJF-Standard)
- Kein Fingerausschnitt am Boden — die 10 mm Y-Flansch-Überstände oben und
  unten dienen als Fingergriff (Daumen oben, Zeigefinger unten, ziehen)
- Aktivkohlebett-Tiefe: **29.3 mm** (= Z − Boden − Deckel − 2 × 3 mm Filtervlies)

### Deckel und Schnappverbindung

- Deckel 2.5 mm dick, Oberseite bündig mit der Trog-Oberkante
- **Zwei** Cantilever-Rastnasen auf den X-Kanten (links/rechts, gegen den
  Schacht-Schaumstoff). Y-Flächen (Moosgummi) und Z-Flächen (Hex, Luftweg)
  bleiben frei von Vorsprüngen und Durchbrüchen.
- Maße pro Rastnase: 6 mm breit, 6 mm lang, 1.0 mm Armdicke, 0.45 mm
  Lippenüberstand, 0.8 mm Einrasthöhe, 1 mm Einführschräge, 0.5 mm
  Armwurzel-Fillet
- Rechteckige Durchbrüche in den X-Aussenwänden — die Lippen schnappen
  sichtbar nach aussen durch (in den Schaumstoff). Vorteile:
  - Eindeutiges „Click"-Feedback beim Schliessen
  - Keine geschlossenen Untermasse, kein Powder-Trap beim MJF-Druck
  - Reversibel: beide Lippen gleichzeitig eindrücken, Deckel abheben

### Innenaufbau (Luftweg-Richtung: Deckel → Boden)

```
Hex-Deckel → 3 mm Filtervlies → Aktivkohlebett (~29 mm) → 3 mm Filtervlies → Hex-Boden
```

Das Bett sitzt zwischen zwei Vlieslagen, die gleichzeitig als
Partikel-Rückhalt und als Staubfilter wirken.

## Nutzung

```bash
pip install build123d ocp-vscode
```

1. VSCode öffnen, Command Palette → „OCP CAD Viewer: Open Viewer"
2. `python carbon_filter_build123d.py` ausführen
3. Viewer-Panel: Maus zum Drehen, Scroll zum Zoomen

Datei speichern triggert Live-Reload im Viewer. Beim Ausführen werden
automatisch die Exporte in `output/STEP/` (für STEP) und `output/STL/`
(für STL) geschrieben — je eine `trough.*` und `lid.*` Datei.

`EXPLODED = True` hebt den Deckel 30 mm über den Trog; für die
Zusammenbau-Ansicht auf `False` setzen.

## MJF-Optimierungen

| Bereich | Wert | Grund |
|---|---|---|
| Wandstärke | 2.2 mm | Nach Rabbet-Schulter 1.2 mm Restwand → oberhalb MJF-Minimum (1.0 mm) |
| Bodenstärke | 2.2 mm | Gleichwertige Struktursteifigkeit, gleichzeitig Flansch-Dicke |
| Passungsspiel `fit_clear` | 0.30 mm | MJF-typischer Toleranzbereich ±0.3 mm |
| Hex-Raster | 10 mm flats, 1.2 mm Web, 4 mm Margin | Grösseres Raster = weniger Stegen/Fläche, besseres Entpulvern, Stege trotzdem deutlich über MJF-Minimum |
| Eckenfillet Körper | 2.0 mm | Bessere Oberfläche; Flansch-Y-Kanten bleiben scharf (Stopperfunktion) |
| Armwurzel-Fillet | 0.5 mm | Kerbspannungsreduktion → Dauerfestigkeit des Snap-Arms |
| Snap-Mechanik | 2 Durchbrüche an X-Seiten | Keine Powder-Traps, klares Click-Feedback, reversibel |
| Entpulvern | Hex oben + unten durchgehend | Pulver rieselt frei durch die Kassette |

## Tiefenauslegung (`size_z` — Luftstromrichtung)

Kompromiss zwischen Kohlekapazität und Druckverlust durch die aktiven
Absaugungen. Nutzbarer Bettquerschnitt `cavity_x × cavity_y ≈ 57.6 × 88.6 ≈
51 cm²`, 6 parallele Pfade.

Druckverlust im AC-Granulatbett (Ergun, 3-mm-Pellets, ε ≈ 0.4):

| Face velocity | ΔP/mm Bett |
|---|---|
| 0.5 m/s | ~2.5 Pa |
| 1.0 m/s | ~8 Pa |
| 1.5 m/s | ~17 Pa |

Bei 40 mm `size_z` ergibt sich ein Kohlebett von 29.3 mm, Kapazität ~78 g pro
Kassette bei Schüttdichte ~450 kg/m³ → ~470 g gesamt über 6 Kassetten.
Erwartete Standzeit in normaler Wohnluft: ~6 Monate. ΔP bei realistischem
Arbeitspunkt (~0.5 m/s) ca. 50–80 Pa — verträglich mit
Bad-/Küchenabsaugungen (typisch 40–100 Pa statisch).

Tieferes Bett (45–55 mm) ist optional machbar, falls stärkere Absaugungen
vorhanden sind und längere Wechselintervalle gewünscht.

### Snap-Belastungs-Check

Beim Einrasten biegt sich der Arm um `hook_protr + fit_clear = 0.75 mm`.
Maximale Randfaserdehnung in einem Cantilever:

```
ε = 3 · t · δ / (2 · L²) = 3 · 1.0 · 0.75 / (2 · 6²) ≈ 3.1 %
```

PA11-Fliessdehnung ≈ 5 %, Bruchdehnung ≈ 45 %. 3.1 % liegt komfortabel im
elastischen Bereich. Das Script gibt den Wert beim Lauf auf STDOUT aus.

## Warum PA11 für diesen Einsatz

Lastprofil: ca. 10 Öffnungs-/Schliesszyklen in 5 Jahren, Innenraumluft,
Kontakt mit Aktivkohle.

- Höhere Bruchdehnung (~45 % vs. ~20 % PA12) → Snap-Arm verzeiht
  Überbeanspruchung; kein Bruch beim ersten Klick
- Bessere Dauerbiegefestigkeit und geringeres Creep → Rastnase behält über
  Jahre die Rückstellkraft
- Niedrigere Wasseraufnahme (~0.3 % vs. ~0.5 %) → stabilere Passung; das
  0.30 mm `fit_clear` bleibt über die Lebensdauer zuverlässig
- Biobasiert (Rizinusöl)
- Kosten: ~20–40 % über PA12, bei Einzelstücken vernachlässigbar

**Bureau-Bezug**: PA11 ist bei Craftcloud, Sculpteo, Materialise und Protolabs
im Standardkatalog. Bei Shapeways ggf. als Spezialmaterial anfragen oder PA12
als Fallback.

**Druckorientierung** (falls angebbar): Snap-Arm-Biegerichtung parallel zu
den Pulverschichten legen, nicht senkrecht. MJF ist nahezu isotrop, aber
der Effekt ist in Grenzfällen messbar.

**Entpulverung**: Die Hex-Raster auf Boden und Deckel sind durchgehend, das
Gehäuse hat keine geschlossenen Taschen. Pulver rieselt frei durch die Kassette
und durch die Snap-Schlitze.

## Parameter im Script

Alle Masse stehen als benannte Variablen am Dateianfang und sind über
Kommentare erklärt. Änderung → Datei speichern → ocp-vscode-Viewer reloadet;
Script re-exportiert STEP/STL.

## Dateien

- `carbon_filter_build123d.py` — build123d-Script mit ocp-vscode-Viewer
- `README.md` — dieses Dokument
- `CLAUDE.md` — Arbeitsanweisungen für Claude in diesem Repo
- `TODO.md` — offene Aufgaben
- `LOGBOOK.md` — Änderungs- und Entscheidungsprotokoll
