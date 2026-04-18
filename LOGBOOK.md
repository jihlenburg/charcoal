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

### Repo-Init, v1.0.0-Tag, Output-Neuordnung

Repo mit `git init` auf `main` initialisiert. Alle Dateien (Script,
Dokumentation, STEP/STL-Exporte) in einen Root-Commit `c24868b` gelegt und
als `v1.0.0` getaggt. STEP-Artefakte liegen unter `output/STEP/`, STL unter
`output/STL/` (script-relative Pfade über `Path(__file__).resolve().parent`,
sodass Läufe aus beliebigem CWD in denselben Ordner exportieren).

**Begründung Unterordner**: Die Unterscheidung STEP (maschinenlesbarer CAD-
Austausch, z. B. mit Bureau) vs. STL (direkter Druckfluss) soll in der
Ordnerstruktur sichtbar sein, damit beim Versand klar ist, welche Datei für
welchen Zweck dient. Beim Tagging von v1.0.0 wurde die Ordnerneuordnung
destruktiv in den Root-Commit eingefaltet (statt neuer Commit), da das Tag
noch nicht publiziert war und der lineare Commit-Graph sauber bleiben sollte.

### DFM-Optimierung (Design for Manufacturability)

Systematischer Durchgang durch alle 90°-Kanten und -Übergänge am Körper und
Deckel, mit explizit gewählten Radien pro Feature. Ziel war es, die
Druckbarkeit und Langlebigkeit zu verbessern, ohne die funktional relevanten
Masse (Flansch-Stopper, Dichtflächen, Snap-Geometrie) zu verändern.

**Angewandte Rundungen und Fasen** (alle in `carbon_filter_build123d.py`
parametrisiert; Werte in Klammern):

| Feature | Op | Wert | Zweck |
|---|---|---|---|
| Körper-Senkrechtkanten | Fillet | 2.0 mm | bereits vorhanden |
| Flansch-Unterseite (4 Aussenkanten Z=0) | Chamfer | 0.8 mm | Handling, Griffgefühl, kein Absplittern |
| Flansch-Y-Step (2 gerade Kanten Z=floor) | Fillet | 1.0 mm | Kerbspannung Innenecke |
| Flansch-Eckenschelfs (4 Bögen Z=floor) | Chamfer-Fallback 0.5 | — | OCCT-Konflikt, akzeptiert |
| Kavitäts-Bodeninnenkanten (4 Kanten Z=floor) | Fillet | 1.0 mm | Kerbspannung + Entpulvern |
| Rabbet-Schulterkanten (Z=size_z−rabbet_depth) | Fillet | 0.3 mm | abrupten Step weichen |
| Snap-Armwurzel | Fillet | 0.5 mm | bereits vorhanden, beibehalten |

**Hook-Lip von 0.45 auf 0.50 mm angehoben**: `hook_protr` lag unter dem
MJF-Minimum für positive Features (0.5 mm) und wäre potenziell mit
abgerundeter Lippen-Spitze gedruckt worden → unsauberes Einrasten. Auf 0.50
mm angehoben: maximale Cantilever-Dehnung steigt von 3.12 % auf 3.33 %
(PA11-Fliessdehnung ~5 %), weiterhin komfortabel elastisch.

**Per-Kanten-Fallback für OCCT-Konflikte**: `fillet()` und `chamfer()` in
build123d/OCCT werfen eine Exception für den gesamten Batch, wenn **eine
einzige** der übergebenen Kanten den Radius nicht akzeptiert. Lösung: zwei
Hilfsfunktionen `try_fillet()` / `try_chamfer()`, die zuerst den Batch
versuchen und bei Fehler auf per-Kanten-Versuch fallen. Fehlschläge werden
mit Kanten-Label und Radius auf STDOUT protokolliert. Das rettet alle
Kanten, die OCCT problemlos verarbeiten kann, auch wenn einzelne Kanten
scheitern.

**Bekannte Limitation (akzeptiert): 4 Flansch-Eckenschelfs**: An den 4
Körperecken entsteht beim Union von Körper (mit 2 mm vertikalem
Eckenfillet) und Flansch (rechteckig, ohne eigenes Fillet) ein kleines
"Shelf" — eine bogenförmige Kante bei Z=floor zwischen der zylindrischen
Körperecken-Oberfläche und der ebenen Flansch-Oberseite. OCCT verweigert
hier sowohl Fillet als auch Chamfer bei jedem Radius (getestet:
0.3/0.5/1.0 mm), weil die Tangente zur angrenzenden Zylinderfläche nicht
konsistent aufgelöst werden kann. Die Stellen sind ~2×2 mm, kosmetisch,
nicht lasttragend, nicht Dichtfläche. MJF druckt sie sauber; das Shelf
bleibt als akzeptierter Kompromiss bestehen. Ein Redesign (z. B. Flansch
mit eigenen Ecken-Fillets ausstatten, damit Union-Topologie kompatibel
wird) wäre möglich, aber mit Risiko weiterer Topologie-Probleme und
geringem funktionalem Gewinn.

**Topologische Ordnung der Operationen**: Getestet wurden verschiedene
Reihenfolgen (Straights-first vs. Arcs-first für den Flansch-Y-Step).
Ergebnis: **Straights zuerst** (2/2 Kanten filetieren bei 1.0 mm
erfolgreich), Arcs danach (4/4 werden vom Fallback übersprungen). Umgekehrt
gelingen 2/4 Arcs, aber dann scheitern die Straights komplett — weil
die erfolgreiche Arc-Fillet-Operation die Nachbar-Topologie verändert.
Straights-first maximiert den sichtbaren Verbesserungsgewinn auf den
langen Y-Kanten, wo die Kerbspannungsreduktion am meisten bringt.

**Verworfene Alternativen**:

- _Alle konkaven Kanten mit einheitlichem 0.5-mm-Fillet_: zu klein für
  Flansch-Y-Step (1.0 mm ist spannungsoptimal), zu gross für Rabbet
  (eigentlich reichen 0.3 mm, grössere Fillets fressen Schulterbreite)
- _Chamfer statt Fillet für Flansch-Step_: funktioniert, aber konkave
  Innenkanten profitieren stärker von Rundung als Fase (stetige Tangente
  statt erneutem Kantenknick)
- _Rabbet komplett weglassen_: nein, der Rabbet sitzt die Deckeloberkante
  bündig und ist funktional unverzichtbar; der 0.3-mm-Fillet soll nur die
  Kanten weicher machen
- _Redesign für Flansch-Ecken-Kompatibilität_: wurde für v1.0.1
  zurückgestellt; das Shelf hat keinen bekannten Nachteil

### Versionsgravur auf dem Flansch (v1.0.1)

Neue `VERSION`-Konstante im Script-Header, als 0.6 mm tiefe Vertiefung
(Font-Size 5 mm, Arial) auf die Apartment-seitige Fläche des
+Y-Flansch­überstands graviert. Platziert bei Z = 0 … 0.6 mm, vertikal
mittig im 10-mm-Überstand.

**Spiegelungs-Fix**: Der erste Wurf nutzte `Plane.XY` als Sketch-Ebene —
der Text war in der +Z-Blickrichtung lesbar, aber bei der effektiven
Benutzerperspektive (-Z, Apartment-Seite) spiegelverkehrt (Beobachter-Rechts
kippt von +X auf -X beim Wechsel der Blickseite). Fix: Sketch auf einer
Ebene mit Normalen -Z und `x_dir = -X`, damit `y_dir = +Y` (rechtshändig)
bleibt und die Zeichen aus der Apartment-Richtung korrekt orientiert sind.
Extrude-Amount wird negativ gewählt, sodass der Cut wieder in +Z-Richtung
ins Material geht.

**Font-Size 5 mm** (zunächst 4 mm): nach Viewer-Probe auf 5 mm angehoben,
damit die Zeichen auch nach MJF-typischem Randverzug klar lesbar bleiben.
Paßt weiterhin in den 10-mm-Überstand.

**Begründung Platzierung**:

- **+Y-Flanschüberstand**: solid (keine Hex-Perforation, kein Snap-Schlitz),
  in der Sichtlinie des Benutzers (Apartment-Seite), gleichzeitig Griffrand
  → die Gravur ist beim Wechsel immer sicht- und fühlbar
- **Tiefe 0.6 mm**: MJF druckt diese Tiefe crisp. Restboden unter der
  Gravur = 2.2 mm − 0.6 mm = 1.6 mm, deutlich über MJF-Minimum 1.0 mm.
- **Font-Size 5 mm**: passt in den 10 mm Überstand und bleibt auch nach
  MJF-Randverzug klar lesbar (4 mm waren am Rand des Lesbaren).

**Topologie-Überlegung**: Die Gravur erzeugt viele neue Kanten bei Z ≈ 0
(Textkonturen). Deshalb wird die Gravur NACH dem `flange_bot_cham`-Chamfer
ausgeführt — so fasst der Z-Positions-Filter des Chamfers nur die 4
Flansch-Perimeter-Kanten und nicht die Textkonturen (OCCT würde Chamfer auf
Text-Kanten verweigern und den gesamten Batch abbrechen lassen, oder das
Ergebnis würde visuell unsauber).

**Maintenance-Pflicht**: `VERSION` steht zentral im Script-Header. Beim
Bump muss sie synchron im README mitgeführt werden (oberhalb der
Funktionsbeschreibung) und beim Release als git-Tag `vX.Y.Z` gesetzt
werden. Die Drei-Punkt-Regel ist in CLAUDE.md verankert.

**Verworfene Alternativen**:

- _Gravur auf der Deckel-Oberfläche_: wäre zwischen den Hex-Löchern gezwängt
  und beim Einbau verdeckt (Deckel zeigt nach hinten in den Schacht)
- _Erhabener Text statt vertieft_: würde gegen die Dichtflächen der
  Schachtkante drücken und lokal den Flansch-Sitz stören
- _Gravur auf den X-Wänden (Schaumstoffseite)_: unsichtbar nach Einbau
- _Gravur auf den Y-Wänden_: kollidiert mit Moosgummi-Dichtung
- _Gravur mittig auf der Flansch-Bodenfläche_: mittig sind die
  Hex-Perforationen, Text-Kontur würde Hex-Ränder schneiden

### Deckel-DFM: 90°-Kanten gesoftened

Rückfrage des Users („Sind die 90° Kanten des Deckels so ok?") → Analyse
und konsistente Behandlung analog zum Trog:

- **`lid_corner_fil = 1.0 mm`** (4 vertikale Deckel-Senkrechtkanten):
  Handling und visuelle Konsistenz zum Körperecken­fillet. 2.0 mm wie am
  Körper wäre am kleineren Deckel-Footprint zu dominant.
- **`lid_top_cham = 0.5 mm`** (4 Oberkanten bei Z=size_z): Sichtseite von
  oben, Absplitter­schutz, keine scharfe Kante unter dem Finger­druck beim
  Öffnen.
- **`lid_bot_cham = 0.2 mm`** (4 Unterkanten bei Z=size_z−lid_thk):
  Rabbet-Einführschräge. Nur 2/4 Kanten akzeptiert (beide Y-Seiten).
  Die 2 X-Seiten-Kanten verweigert OCCT konsistent auf 0.3/0.2/0.15 mm,
  weil die 0.5-mm-Armwurzelfillet am Tab-Anschluss (X≈28.8) nur 0.7 mm
  vom X-Perimeter (X=29.5) entfernt liegt — Tangentenkonflikt. Die 2
  X-Kanten bleiben scharf; das ist kein Druckproblem, MJF zeichnet sie
  sauber ab und sie zeigen zur Rabbet-Schulter hin, nicht zur Hand.

**Operations-Reihenfolge**: Chamfers **vor** Eckenfillet. Wird der
Eckenfillet zuerst ausgeführt, ändert sich die Perimeter-Topologie (die
4 Eckenkanten sind nun Bögen statt kurze gerade Stücke), und die
nachfolgenden Chamfer-Selektionen lehnt OCCT ab. Die umgekehrte
Reihenfolge (erst Chamfer auf die pristinen 4 Perimeter-Kanten, dann
Fillet auf die 4 Eckenkanten) funktioniert konfliktfrei.

**Klarstellung zur MJF-Druckbarkeit**: Das MJF-Laserscanfeld erzeugt
keine prozessbedingten Schwierigkeiten mit 90°-Kanten. Die Softening-
Operationen dienen hier ausschliesslich Haptik/Handling/Optik, nicht
der Druckbarkeit.

### STL-Mesh-Heal für Bureau-Upload (pymeshfix)

Nach Upload von `trough.stl` beim MJF-Bureau zeigte deren DFM-Analyse
1 nicht-manifold Kante, 71 Abschlusskanten und 117 Selbstdurchdringungen
(jeweils <0.02 % der Gesamt-Primitive, aber Slicer lehnen ab). Ursache:
OCCT's Standard-Tessellation setzt an den Tangentennähten von Fillets
und Chamfers T-Vertices, die je nach Nachbar­face nicht exakt koinzident
sind.

**Lösung**: Post-Processing-Schritt `_heal_stl()` nach dem STL-Export,
implementiert mit `pymeshfix` (Attene-Algorithmus, purpose-built für
topologische Mesh-Reparatur).

**Trough**: heilt robust von 1 Randloop + 296 Selbstdurchdringungen auf
0 / 0, Volumenerhaltung 33.53 → 33.60 cm³ (0.2 % Differenz durch fill_holes).

**Lid**: heilt NICHT. 83 Selbstdurchdringungen sitzen topologisch
fundamental (hex-perforierte Platte mit 28 Durchbrüchen + Snap-Arm-Wurzel­
fillet bei 0.5 mm). `strong_intersection_removal` entfernt die
konfliktierenden Dreiecke und kaskadiert über `fill_holes` in eine inverse
Geometrie-Rekonstruktion — das Endergebnis schrumpft von 7.25 auf 0.04 cm³
(99.4 % Volumen­verlust). Der Volumen-Wächter (≤ 5 % Abnahme) im
`_heal_stl` bricht deshalb ab und behält das Original-STL.

**Tessellations-Scan**: Angular-Tolerance von 0.02 bis 0.3 rad getestet —
Selbstdurchdringungen bleiben (31–204 Stück), saubere Tessellation nicht
erreichbar. Das ist kein Bug im Script, sondern eine OCCT-Limitation
bei hochgenus-Topologien.

**Upload-Strategie** (bestätigt 2026-04-18):
- `trough.stl` (geheilt) für MJF-Bureau — DFM clean.
- `lid.stl` (ungeheilt, 83 Selbstdurchdringungen ~2.5 %) — vom Bureau
  akzeptiert, Auto-Heal kommt damit klar. Kein Handlungsbedarf.
- `lid.step` bleibt als alternative BRep-Quelle verfügbar (clean by
  construction), wird aber für den aktuellen Bureau-Workflow nicht benötigt.

**Verworfene Alternativen**:
- _`pymeshfix.clean_from_file`_: verwirft "kleine Komponenten" per
  Default; für hex-perforierte Platten fatal
- _trimesh-only heal_: erreicht beim Trough nur watertight=False mit
  145 broken faces — trimesh's `fill_holes` schließt keine Loops mit
  T-Vertex-Artefakten zuverlässig
- _Voxelisierung + Marching Cubes_: rundet scharfe Kanten, nicht mit
  0.30-mm-Fit-Toleranz vereinbar
- _manifold3d Self-Union_: Engine nicht in der `ocp`-Env installiert;
  pymeshfix ist leichter

### Release v1.0.2

Sammelrelease der seit v1.0.0 kumulierten Änderungen:

1. **Versionsgravur** (ursprünglich als v1.0.1 geplant) auf dem
   +Y-Flanschüberstand, 5 mm Font, 0.6 mm tief, mit Spiegelungs-Fix über
   Plane(x_dir=-X, z_dir=-Z).
2. **DFM-Optimierung** am Trog (Flansch-Fasen/Fillets, Kavitäts-Boden,
   Rabbet-Schulter, Per-Kanten-Fallback für OCCT-Grenzfälle).
3. **Deckel-DFM**: Eckenfillet 1.0 mm, Oberkanten-Chamfer 0.5 mm,
   Unterkanten-Chamfer 0.2 mm (2/4, X-Seiten OCCT-verweigert).
4. **STL-Mesh-Heal** mit `pymeshfix` nach Bureau-DFM-Feedback. Trough
   heilt auf 0 Randloops / 0 Selbstdurchdringungen; Lid bleibt original
   (Bureau-Auto-Heal akzeptiert die 83 Restdurchdringungen).

Versionssprung von v1.0.0 direkt auf v1.0.2 (die v1.0.1-Gravur-Arbeit
wurde nie getaggt; der Bump geht in einem Commit auf).
