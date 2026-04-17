# Logbuch

Chronologisches Protokoll der Design- und Toolchain-Entscheidungen.

## 2026-04-17

### MJF-Optimierung und FreeCAD-Abkehr

Entfernen der FreeCAD-Toolchain; weiter nur build123d + ocp-vscode als
Designer/Viewer-Kombination.

**Begründung**: Der Editier-Workflow in FreeCAD (Spreadsheet-Expressions +
Sketch-Klicks) war für dieses Projekt nie nötig; alle Parameter-Iterationen
liefen ohnehin über Script-Edits. Durch build123d entfallen topologische
Naming-Probleme und fragile MapMode-Heuristiken.

### MJF-Optimierungen am Design

Mehrere parametrische Änderungen am `carbon_filter_build123d.py`:

| Parameter | Vorher | Nachher | Grund |
|---|---|---|---|
| `wall` | 1.8 mm | 2.2 mm | Nach Rabbet-Schulter blieb nur 0.3 mm Wand — nicht druckbar |
| `floor` | 1.8 mm | 2.2 mm | Symmetrie zu `wall` |
| `fit_clear` | 0.15 mm | 0.30 mm | MJF-Standard (±0.3 mm Maßtoleranz) |
| `hex_margin_*` | 3.0 mm | 4.0 mm | Mehr Rahmenmaterial um Hex-Perforation |
| `outer_fillet` | 1.5 mm | 2.0 mm | Haptik und Oberfläche |
| `hook_root_fil` | — | 0.5 mm | Neu: Kerbspannungsreduktion am Armansatz |

**Rabbet-Geometrie**: Die bisherige Version cuttete den OUTER-Ring des
Wandabschlusses, was eine stehende 0.3 mm-Innenlippe hinterliess. Neue
Logik: das Rabbet WEITET die Kavität am oberen Ende (Rechteck grösser als
Kavitäts-Rechteck, cut `rabbet_depth` tief). Ergibt eine saubere Schulter
von `shelf_w` Breite, auf der der Deckel aufsitzt.

**Snap-Mechanik**: Grundsätzlich umgestellt auf den Ansatz „Durchbrüche in
Aussenwand + Lippen schnappen durch". Verworfene Alternativen:

- _Interner Catch an Cavity-Wand-Nut_: benötigt Horizontal-Nut, klassisches
  Powder-Trap-Problem beim MJF-Entpulvern
- _Lippe catcht auf Schulter_: bei gegebenen Wandstärken geometrisch nicht
  sauber darstellbar ohne Arm-Kollision mit Cavity-Wand
- _Friktionspassung ohne Hooks_: wäre am einfachsten, aber User hatte
  explizit Rastnasen spezifiziert

Die Durchbrüche-Variante ist MJF-ideal: keine geschlossenen Untermasse,
klares akustisches Feedback, Deckel reversibel öffenbar (alle vier Lippen
gleichzeitig eindrücken).

### Material PA11

Umstieg von PA12 auf PA11. Begründung im README dokumentiert (höhere
Bruchdehnung, bessere Dauerfestigkeit, niedrigere Feuchteaufnahme). Bei
dem Duty-Cycle (~10 Zyklen in 5 Jahren) kein technischer Zwang, aber
komfortabler Sicherheitsabstand.

### Repo-Struktur

CLAUDE.md, TODO.md, LOGBOOK.md angelegt für strukturierte Fortführung des
Projekts.

## 2026-04-18

### Schacht-Fit-Redesign

Geometrie an den tatsächlichen Lüftungsschacht angepasst. Schachtmaße (aus
Foto und Benutzerangaben verifiziert):

- Harte Innenbreite 70 mm, je ca. 5 mm Schaumstoff links/rechts
- Höhe 100 mm, harte Ober- und Unterwand
- Tiefe 100 mm
- Luftrichtung: hinten → vorne (durch 3 aktive Wohnungsabsaugungen
  gezogen, 3 Fenster × 2 Schächte = 6 parallele Pfade)

**Änderungen am Design**:

| Parameter | Vorher | Nachher | Grund |
|---|---|---|---|
| `size_x` | 65 | 62 | 1.5 mm Schaumstoff-Kompression pro Seite: dichtet und rutscht noch rein |
| `size_y` | 45 | 40 | Optimum aus Ergun-ΔP und AC-Kapazität bei aktiven Absaugungen |
| Snap-Durchbrüche | 4 (alle Seiten) | 2 (nur X) | Y-Flächen = Hex-Luftweg, Z-Flächen = an den harten Schachtwänden |
| Rastnasen am Deckel | 4 | 2 | Entsprechend |
| Fingermulde vorn | — | 25 × 6 × 1.2 mm | Herausziehen aus dem Schacht |

**Begründung Tiefe 40 mm**: Bei Kassettenquerschnitt ~48 cm² und 6
parallelen Pfaden pendelt sich die Strömung durch AC-Bett bei
Bad-/Küchenabsaugung (40–100 Pa statisch) auf ~0.5 m/s Face Velocity
ein. Ergun-ΔP bei 30 mm Bett (nach Wänden und Filtervlies) ≈ 75 Pa —
verträglich. Kohle-Masse ~78 g/Kassette → ~6 Monate Standzeit in
normaler Wohnluft. Verworfene Alternativen:

- 45 mm (Status quo): ~110 Pa ΔP, fängt an Absaugung zu drosseln
- 30 mm: ΔP ok, aber Standzeit unter 4 Monaten zu kurz für Komfort
- 55 mm: >150 Pa ΔP, nur bei überdimensionierten Absaugungen sinnvoll

**Begründung 2 statt 4 Rastnasen**: Einrastung auf Y-Flächen würde die
Hex-Perforation unterbrechen (Strömung und Optik), Einrastung auf
Z-Flächen würde an den harten Schachtwänden anschlagen und das Einsetzen
verhindern. Nur die X-Seiten stehen im Schaumstoff und erlauben
Durchbrüche ohne Schachtkonflikt. Zwei Rastnasen reichen für die
Haltekraft (Deckel ist statisch, nur Eigenmasse + Filtervlies-Druck).

**Fingermulde**: Der Schacht ist tief (100 mm) und die Kassettenoberkante
fluchtet bündig mit der Schachtkante. Ohne Griffmulde ist die Kassette
kaum herausnehmbar. 1.2 mm Tiefe bei 2.2 mm Wand → 1.0 mm Restwand
(>= MJF-Minimum).

### Grundlegende Umkonstruktion: vertikaler Luftstrom durch den Filter

Bei der Einbaubesprechung wurde klar, dass die bisherige Konstruktion
(horizontaler Luftstrom durch Hex-Gitter in den Y-Flächen, Deckel an der
Seite) den eigentlichen Zweck verfehlt: **die Luft muss durch das
Kohlebett, nicht daran vorbei**. Neue Konstruktion:

- Hex-Gitter auf **Boden und Deckel** (Z-Flächen)
- Z wird zur Luftstromachse — beim Einbau wird die Kassette um 90° gekippt,
  sodass Z horizontal zur Schachttiefe wird
- Neue Nennmasse: `size_z = 40 mm` (Luftweg), `size_y = 93 mm`
  (Schachthöhe), `size_x = 62 mm` (unverändert)
- Deckel schnappt von **oben** auf (Befüllung: Deckel ab → Vlies → Kohle →
  Vlies → Deckel drauf)

**Einbaulage umgedreht**: Deckel zeigt nach hinten (Aussenluft-Seite),
Boden mit Fingermulde nach vorne in die Wohnung. Gründe:

- Beim Ziehen an der Fingermulde kommt die gesamte Kassette mit, nie nur
  der Deckel. Umgekehrt würde der Zug ausser der Reibung auch direkt die
  Rastnasen belasten und die Kassette in sich auseinanderziehen können.
- Der Luftstrom (hinten → vorne) drückt den Deckel in den Rabbet-Sitz,
  nicht heraus.

**Einschub-Stopper als Bodenflansch**: Ein umlaufender Flansch am Boden
(Z = 0 … 2.2 mm) ist breiter als die harte Schachtöffnung und fängt an
der Schacht-Frontkante. Erste Version hatte den Flansch rundum 5 mm
vergrössert (72 × 103 mm) — das überschreitet jedoch die 70 mm
X-Hartöffnung und blockiert den Einschub. Korrigiert: Flansch nur in Y
verbreitert (62 × 103 × 2.2 mm), X bleibt auf Körperbreite. Die 3 mm
Y-Überstand oben und unten reichen zum Einfangen; in X geht der Flansch
sauber durch die 70-mm-Öffnung. Die Kassette steht 2.2 mm aus der
Schachtkante (User-Limit 5 mm).

**Moosgummi-Axialdichtung**: Y-Flächen der Kassette kontaktieren die
harten Schachtwände oben/unten. Dort werden Moosgummistreifen aufgeklebt
(user-applied, nicht gedruckt), um axiale Leckluft am Filterbett vorbei
zu verhindern. Die Y-Flächen werden deshalb glatt und durchbruchfrei
konstruiert — keine Hex, keine Snap-Schlitze.

**Armwurzel-Fillet — robuste Kantenauswahl**: Der vorherige
Kantenselektor (`filter_by_position` auf Z-Höhe) griff auch die
Lid-Perimeterkanten und warf damit gelegentlich ValueError. Neu: pro
Arm eine XY-Bounding-Box, und nur Kanten deren Mittelpunkt innerhalb
liegt werden gefilletet. Tolerant mit 0.05 mm Saum, Fallback-Meldung
falls gar keine Kanten matchen.

**Verworfene Alternativen**:

- _Hex in Y-Flächen, Deckel seitlich_: ursprünglicher Ansatz, gibt
  horizontalen Bypass-Strom statt Durchströmung
- _Deckel vorne (Apartment-Seite)_: Fingermulde würde Deckel lösen, nicht
  Kassette ziehen; Luftstrom würde Deckel herausdrücken
- _Flansch rundum 5 mm_: X-Überstand blockiert Einschub in 70-mm-Öffnung
- _Axiale Dichtung per Geometrie (Dichtlippen, Schürzen)_: MJF drucken
  diese Feinstrukturen unzuverlässig; Moosgummi ist zuverlässiger und
  tauschbar

### Fingermulde entfernt, Snap-Slot-Fix, Hex-Raster vergrössert

Nach erstem Viewer-Check (User-Feedback):

**Snap-Slot-Bug -X-Seite**: Die zweite Slot-Cut-Ebene hatte Offset
`-size_x/2 + 1.0` (bei x=-30, also _innerhalb_ der Aussenwand); richtig
ist `-size_x/2 - 1.0` (bei x=-32, _ausserhalb_ der Wand). Damit ging der
Cut nur durch die inneren ~1.2 mm der -X-Wand statt sauber durch, und die
Deckel-Rastnase hatte keinen Durchbruch zum Einrasten. Fix: Vorzeichen
korrigiert → beide Slots schneiden jetzt symmetrisch durch.

**Fingermulde (40 × 8 × 1.2 mm) entfernt**: Auf Niveau der Bodenaussenseite
war sie ergonomisch sinnlos — eine flache Vertiefung ohne Unterkante zum
Hinterhaken. Die 5 mm Y-Flansch-Überstände (oben und unten an der
Apartment-Seite) bieten den natürlichen Fingergriff: Daumen oben,
Zeigefinger unten, direkter Auszug. Keine extra Geometrie nötig, Boden
bleibt strukturell geschlossener.

**Hex-Raster 8 → 10 mm flats**: Offenfläche steigt von 44 % auf 48 % der
Kavitätsfläche. Der Gewinn ist moderat, weil die 4 mm Margin (MJF-Verzug)
den Rand dominiert — dennoch besser für freies Pulverrieseln und optisch
aufgeräumter. Screen-ΔP bei 0.5 m/s Face Velocity unter 1 Pa in beiden
Varianten, also nicht strömungslimitierend (Bett dominiert mit 50–80 Pa).
Stegbreite bleibt 1.2 mm — gut über MJF-Minimum 1.0 mm, konservativ.

**Flanschüberstand 5 → 10 mm**: Der bisherige 5-mm-Überstand reichte als
Stopper, bot aber wenig Fingerauflage (die Fingerkuppe braucht ~8 mm
Greiftiefe für sicheren Zug gegen den Unterdruck der Absaugung). Mit je
10 mm gibt es einen komfortablen Griffrand. Gesamt-Flansch jetzt
62 × 113 × 2.2 mm. Kollidiert nicht mit der Fensterrahmen-Umgebung.
