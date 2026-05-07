# Aktivkohlefilter-Einsatz (Passivlüftung mit aktiven Absaugungen)

**Version: 1.1.6**. Der String steht im Script als `VERSION`-Konstante und
wird als Gravur auf den +Y-Flanschüberstand übernommen. Bei jedem Versionssprung
muss er gleichzeitig in `carbon_filter_build123d.py`, im README und am
git-Tag nachgezogen werden.

Parametrischer Filterkorb aus Grundkörper und Deckel für die Wohnungs­lüftung
mit Aktivkohle. Die Konstruktion ist für HP Multi Jet Fusion in **PA12**
ausgelegt (`HP 3D HR PA 12 enabled by Evonik` oder vergleichbar). PA11 ist
nach wie vor eine tolerantere Alternative, aber nicht mehr der Konstruktionsfall.

Quellcode: [`carbon_filter_build123d.py`](./carbon_filter_build123d.py) (build123d).

![Exploded render of the filter cassette](docs/assets/charcoal_filter_v1_1_6_render.png)

Das README-Render entsteht über `./run render-readme` (Blender/Cycles, mit
VTK-Fallback, falls Blender fehlt).

## Konstruktionsprinzip

**Vertikaler Luftstrom durch den Filter.** Die Luft tritt durch das Hex-Gitter
auf der einen Z-Seite (Deckel) ein, durchströmt das Aktivkohlebett und
verlässt die Kassette durch das Hex-Gitter auf der anderen Z-Seite (Boden).
Im Skript-Koordinatensystem ist Z die Luftstromachse — eingebaut steht die
Kassette um 90° gekippt, sodass Z horizontal zur Schachttiefe wird.

### Befüllung (Kassette stehend, Deckel oben)

1. Finger in die mittige Freistellung an der Schnapper-Seite setzen und den
   Deckel am kleinen Zugsteg nach oben anheben. Die beiden Schnapper lösen
   sich dabei über ihre Auslöserampe selbsttätig; auf der Gegenseite hält die
   Hakenleiste den Deckel in ihrer Tasche und gibt damit die Öffnungs­seite vor
2. Filtervlies auf den Boden legen (3 mm, dichtet Hex gegen Granulatdurchfall)
3. Aktivkohlegranulat einfüllen (~29 mm Schüttung, ~72 g bei 450 kg/m³)
4. Zweites Filtervlies obenauf; die internen Anti-Bauch-Bars liegen 4.0 mm
   unter der Deckelunterseite, sodass ein 3-mm-Vlies mit ca. 1 mm Reserve
   zwischen Bars und Deckel passt
5. Deckel erst mit der Hakenleiste in die Gegentasche einsetzen, dann die
   Schnapper-Seite herunterdrücken bis beide Nasen hörbar einrasten

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
  70 mm nicht überschritten werden darf. Flansch-Footprint: 65 × 115 mm vs.
  Schacht-Hartöffnung 70 × 100 mm — die je 10 mm-Überstände oben und unten
  fangen an der Schacht-Frontkante und geben gleichzeitig bequem Platz für
  Daumen/Zeigefinger. Die Kassette steht damit `floor = 2.2 mm` aus der
  Öffnung heraus — klar unter der 5-mm-Grenze.

### Abdichtung mit Moosgummi

Die Y-Flächen der Kassette — im Skript-Frame oben und unten — kontaktieren
im Schacht die **harten** oberen und unteren Schachtwände. Sie sind dafür
glatt und ohne Durchbrüche ausgeführt. Vor dem Einschub werden auf beide
Flächen **Moosgummistreifen** geklebt; beim Einschieben werden sie
zusammengepresst und dichten dadurch axial gegen Leckluft am Filterbett vorbei.

Auf der einen X-Fläche sitzen die Snap-Durchbrüche, gegenüber eine flache
Haken-Tasche im oberen Wandbereich. Beide X-Flächen drücken sich in den
seitlichen Schaumstoff und werden so durch den Schaum selbst abgedichtet.

## Geometrie

- Zwei Teile: Grundkörper (Trog mit integriertem Flansch + Boden) und Deckel
- Körper-Aussenmasse: **65 (X) × 95 (Y) × 40 (Z)** mm
- Bodenflansch: **65 × 115 × 2.2** mm (Z = 0 … 2.2) — nur in Y breiter als Körper
  (je 10 mm Überstand oben und unten als Stopper + Fingergriff)
- Wand 2.2 mm, Boden 2.2 mm, Deckel 2.5 mm
- Hex-Perforation identisch auf **Boden** und **Deckel** (Z-Flächen):
  10 mm flat-to-flat, 1.2 mm Stegbreite, 2.8 mm X-Randabstand und 4.0 mm
  Y-Randabstand → 36 Löcher pro Fläche, ~57 % Offenfläche
  (~31 cm² auf ~55 cm² Kavität)
- Rabbet-Sitz am oberen Rand, 1.0 mm Schulter, 2.5 mm tief
- Passungsspiel 0.30 mm pro Seite (MJF-Standard)
- Kein Fingerausschnitt am Boden — die 10 mm Y-Flansch-Überstände oben und
  unten dienen als Fingergriff (Daumen oben, Zeigefinger unten, ziehen)
- Aktivkohlebett-Tiefe: **29.3 mm** (= Z − Boden − Deckel − 2 × 3 mm Filtervlies)
- Drei interne Anti-Bauch-Bars verbinden die langen X-Wände bei
  `Y = -36, 0, +36 mm`. Je Bar: **2.2 mm** breit in Y, **1.4 mm** hoch in Z,
  quer über die Kavität. Lage: **Z = 32.1 … 33.5 mm**, damit zur
  Deckelunterseite bei `Z = 37.5 mm` ein **4.0 mm** Spalt für das obere
  3-mm-Filtervlies bleibt.

### Versionsgravur

Der `VERSION`-String aus dem Script wird als 0.6 mm tiefe Vertiefung
(Font-Size 5 mm) auf die **Apartment-seitige Fläche des +Y-Flansch­überstands**
graviert. Position: Z = 0 … 0.6 mm, vertikal zentriert auf der Mittellinie des
10 mm breiten Überstands. Die Stelle ist solid (keine Hex-Löcher, keine
Snap-Schlitze), in der Sichtlinie des Benutzers, und die 1.6 mm Restboden
unter der Gravur liegt komfortabel über dem MJF-Minimum von 1.0 mm.

Die Gravur-Ebene ist bewusst gespiegelt konstruiert (Plane mit `z_dir=-Z`
und `x_dir=-X`, sodass `y_dir=+Y` rechtshändig bleibt), damit der Text von
der Apartment-Seite aus korrekt lesbar ist — aus −Z-Blickrichtung wäre ein
Standard-Plane.XY-Sketch nämlich spiegelverkehrt dargestellt.

Beim Versionswechsel muss die `VERSION`-Konstante im Script-Header **und**
die Angabe oben im README synchron nachgezogen werden (plus git-Tag beim
Release).

### Deckel und Schnappverbindung

- Deckel 2.5 mm dick, Oberseite bündig mit der Trog-Oberkante
- Asymmetrische Verriegelung: **eine** passive Hakenleiste auf einer X-Seite,
  **zwei** Cantilever-Rastnasen auf der gegenüberliegenden X-Seite.
- Passive Hakenleiste: 34 mm lang, 3 mm Absenkung, als **einfache**
  Hakenleiste mit 2.1 mm Gesamttiefe, 1.0 mm starkem oberem Steg und einer
  0.35 mm über die Deckelkante nach außen gezogenen Nase. Die reale
  Überdeckung hinter der Trog-Innenwand steigt damit auf etwa **1.05 mm**.
  Sie greift in eine flache rechteckige Tasche in der Gegenseite. Die Tasche
  ist zweistufig: unten eine 1.35 mm tiefe Retentionstasche, oben nur ein
  0.55 mm tiefer Einführkanal. Dadurch bleibt über der unteren Tasche eine
  **0.80 mm** tiefe Material-Lippe, unter der die Haken-Nase sichtbar trägt.
  Außen bleiben etwa **0.30 mm** Taschenluft. Die äußerste Haken-Nase ist mit
  einer 0.2-mm-Fase entschärft.
- Keine passiven Eckfreistiche mehr: die `v1.1.0`-Reliefs haben auf den
  Druckteilen eine sichtbare Diagonalkante erzeugt. `v1.1.6` entfernt diese
  kosmetische Störkante wieder; die zweistufige Haken-Tasche bleibt im
  Baugruppen-Checker trotzdem kollisionsfrei.
- Rastnasen: 6 mm breit, 10.2 mm lang, 1.0 mm Armdicke, 1.1 mm
  Lippenüberstand, 1.5 mm Einführschräge, 0.4 mm Haltelänge, 2.8 mm
  Auslöserampe, 0.5 mm Armwurzel-Fillet.
- Auf der Schnapper-Seite sitzt mittig eine kleine Zuglippe; die Trogwand hat
  dort eine Freistellung, die bewusst noch 1.0 mm Restwand stehen lässt,
  sodass der Deckel nach dem Entriegeln gezielt angehoben werden kann.
- Vorteile:
  - Klare passive Halteseite statt bloßer Führung
  - Deutlich einfacher als ein tiefes verstecktes Haken-/Taschensystem
  - Toleranzfreundlicher als 4 aktive Schnapper
  - Reversibel mit **einer** Hebebewegung: Zuglippe anheben, Schnapper
    cammen selbsttätig frei, Deckel klappt an der Haken-Seite kontrolliert hoch

### Variantenvergleich

- **Nur Führungsleiste**: sehr einfach und für MJF gut druckbar, aber
  ohne passive Haltefunktion. Die Gegenseite positioniert nur, sie trägt
  keinen Aufwärtslastpfad.
- **Einfache Hakenleiste**: der beste Kompromiss. Ein echter Formschluss auf
  einer Seite, dabei aber nur eine flache, gut entpulverbare Tasche mit
  kleiner Überdeckung.
- **Tiefes Haken-/Taschensystem**: mechanisch eindeutig, aber unnötig komplex,
  toleranzempfindlicher und für diesen Anwendungsfall überdimensioniert.

### Öffnungsbewegung und Kraftfluss

Im geschlossenen Zustand greifen auf der Schnapper-Seite die beiden Rastlippen
über die Oberkante der Slots, und auf der Gegenseite sitzt die einfache
Hakenleiste mit etwa `1.1 mm` Überdeckung unter dem Taschendach. Ein
Aufwärtszug am Deckel verteilt sich deshalb nicht nur auf die Schnapper,
sondern wird als Moment zwischen Schnapper- und Hakenseite aufgenommen.

Das Öffnen beginnt an der mittigen Zuglippe auf der Schnapper-Seite. Die
Fingerkraft erzeugt dort ein Drehmoment um die passive Hakenseite, und die
oberen Auslöserampen der Schnapper laufen gegen die Slot-Kante. Aus dem
vertikalen Hub wird dadurch eine seitliche Arm-Auslenkung; die Reaktions­kraft
fließt vom Finger über den Deckel in die Schnapper und von dort in die
Trogwand der Slot-Seite.

Sobald die Schnapper ausgelöst haben, sind sie weitgehend lastfrei. Den Rest
des Öffnungsmoments übernimmt die passive Hakenseite: der Deckel klappt um
sie hoch, statt auf beiden Seiten gleichzeitig lose zu werden. Zum
vollständigen Abnehmen wird er nach dem Hochklappen leicht zur Schnapper-Seite
verschoben, sodass der passive Haken aus seiner Tasche frei kommt — erst dann
lässt er sich nach oben abheben.

### Öffnungskraft / Werkzeugfreiheit

Für die Rastarme wird der Deckel als rechteckiger Cantilever abgeschätzt.
Die reine Armsteifigkeit liefert die laterale Federkraft; die tatsächliche
Fingerkraft beim Öffnen sinkt durch die obere Auslöserampe:

```
F = 3 · E · I · δ / L³
I = b · t³ / 12
```

mit `b = 6 mm`, `t = 1 mm`, `L = 10.2 mm`, `δ = hook_protr + fit_clear = 1.4 mm`
und einem HP-PA12-Elastizitätsmodul von grob `E ≈ 1.65 … 2.20 GPa`
(JF 5200/5600-Datenblattband).

Ergebnis:

- laterale Federkraft pro Schnapper: **ca. 3.3 … 4.4 N**
- geschätzte Finger-Hebekraft gesamt: **ca. 3.3 … 4.4 N**
  für beide Schnapper zusammen, mit 2.8-mm-Auslöserampe und einer groben
  Reibannahme `μ ≈ 0.2`
- Maximale Randfaserdehnung: **≈ 2.02 %**

Damit ist die Bedienung realistisch **ohne Werkzeug** und mit einer einzigen
Fingerbewegung. Die Schnapper müssen nicht separat gedrückt werden; beim
Anheben an der Zuglippe fahren sie über die Auslöserampe selbst nach innen.

HPs Snap-Fit-Handbook gibt als grobe Faustregel eine zulässige Dehnung
unter `1/3` der Fließdehnung an. Mit HP-PA12 (`~9 … 11 %` Fließdehnung laut
5600-Datenblatt) liegt der Zielbereich damit bei `< 3.0 … 3.7 %`; die
aktuellen `~2.02 %` bleiben deutlich darunter. Bei nur wenigen Öffnungs­zyklen
pro Jahr ist das für PA12 weit plausibler als die ältere kurze 7-mm-Geometrie.

### Lokale FEM des Schnappers

Zur Balkenabschätzung kommt eine lokale 3D-FE-Analyse in
`fem/snap_fit_fem.py` dazu. Das Modell bildet **einen aktiven Schnapper** in
der aktuellen `v1.1.6`-Nasenform ab, belastet die reale Rastfläche mit
`1 N` in `+X` und skaliert die Antwort anschließend auf die nötige
Öffnungs-Auslenkung `hook_protr + fit_clear = 1.40 mm`.

Drei Vorbehalte zum Mitlesen:

- Es ist bewusst nur ein **lokales Submodell**, kein vollständiges
  Kontaktmodell aus Deckel, Trog und Gegenhaken.
- Die FE-Kraft fällt **konservativer** aus als die Balkenformel, weil die
  Last an der realen Rastfläche bei `z ≈ -8.5 mm` ansetzt, nicht am freien
  Armende.
- Der `0.5 mm`-Armradius an der Deckelwurzel ist in diesem ersten Modell
  noch nicht explizit vernetzt; die echte Spitzendehnung dürfte deshalb
  leicht niedriger liegen.

Aktueller Stand mit `mesh_size = 0.25 mm` und nominalem `E = 2150 MPa`:

- laterale Federsteifigkeit pro Schnapper: **~7.3 N/mm**
- nötige laterale Auslenkkraft pro Schnapper für `1.40 mm`: **~10.3 N**
- geschätzte Gesamt-Hebekraft zum Öffnen: **~8.0 … 10.6 N**
- maximale Hauptdehnung beim Öffnen: **~3.4 %**

Werkzeugloses Öffnen bleibt damit plausibel. Wiederholtes Öffnen liegt im
HP-`1/3`-Proxyband für PA12 (`< 3.0 … 3.7 %`), aber mit kleinerer Reserve,
als die reine Balkenformel vermuten lässt.

### Lokale FEM der passiven Hakenleiste

Für die passive Hakenleiste gibt es das Pendant-Modell `fem/hook_hold_fem.py`.
Es belastet den unteren Hakennasenbereich mit `1 N` nach unten, klemmt den
oberen Steg als Deckelanschluss ein und skaliert die lineare Elastizität bis
zum PA12-`1/3`-Proxyband hoch.

Aktueller Befund für `v1.1.6`:

- reale Überdeckung hinter der Trog-Innenwand: **1.05 mm**
- nötige bewusste `+X`-Verschiebung zum Aushängen: **~1.05 mm**
- äußere Taschenluft: **0.30 mm**
- Retentionslippe in der Trogwand: **0.80 mm** tiefer Materialüberhang
- oberer Hakensteg: **1.00 mm** stark, **34 mm²** Querschnitt
- vertikale lokale Steifigkeit der Hakenleiste: **~1027 N/mm**
- PA12-`1/3`-Proxy-Haltekraft strukturell: **~174 … 213 N**

Interpretation: Nicht die PA12-Festigkeit der Hakenleiste war der begrenzende
Faktor, sondern ihre Geometrie. `v1.1.3` hatte real nur etwa `0.70 mm`
Untergriff und einen mit `0.40 mm` zu dünnen oberen Hakensteg. Ab `v1.1.5`
ist der Untergriff vergrößert, der Haken selbst sauberer druckbar und in der
Trogwand sitzt eine sichtbare Retentionslippe.

### Innenaufbau (Luftweg-Richtung: Deckel → Boden)

```
Hex-Deckel → 3 mm Filtervlies → Anti-Bauch-Bars / Aktivkohlebett (~29 mm) → 3 mm Filtervlies → Hex-Boden
```

Das Bett sitzt zwischen zwei Vlieslagen; sie halten die Pellets zurück und
fangen gleichzeitig Staub ab. Die Anti-Bauch-Bars liegen unter dem oberen
Vlies und halten die langen Seitenwände beim Befüllen davon ab, sich nach
außen zu biegen.

## Nutzung

Die Python-Umgebung wird über `./run` automatisch als lokale `.venv/`
angelegt und aus `requirements.txt` aktualisiert, sobald sich die
Abhängigkeiten ändern. Der Wrapper wählt automatisch eine kompatible
Python-Version im Bereich 3.9–3.12, weil die CAD/OCP-Native-Wheels nicht für
jede neueste Python-Version verfügbar sind:

```bash
./run setup
```

1. VSCode öffnen, Command Palette → „OCP CAD Viewer: Open Viewer"
2. `./run cad` ausführen
3. Viewer-Panel: Maus zum Drehen, Scroll zum Zoomen

Datei speichern triggert Live-Reload im Viewer. Beim Ausführen werden
automatisch die Exporte in `output/STEP/` (für STEP) und `output/STL/`
(für STL) geschrieben — je eine `trough.*` und `lid.*` Datei.

`EXPLODED = True` hebt den Deckel 30 mm über den Trog; für die
Zusammenbau-Ansicht auf `False` setzen.

Für manuelle Python-/Pip-Kommandos innerhalb derselben Umgebung:

```bash
./run python --version
./run pip list
./run shell
```

### Konsistenz-Check Script ↔ README

Die geometrischen Konstanten (Außenmaße, Wandstärken, Hex-Raster,
Anti-Bauch-Bars, Snap- und Hook-Maße) und der `VERSION`-String stehen doppelt
im Repo: einmal als Variablen im Script, einmal als Prosa- und Tabellenwerte
in diesem README. Damit beide nicht auseinanderlaufen, gleicht sie ein
Sync-Checker laufend ab:

```bash
./run check
```

Der Checker parst `carbon_filter_build123d.py` per AST, formatiert jeden
registrierten Wert so, wie er im README erscheinen würde (mit
Trailing-Zero-Toleranz, also `1.0` ↔ `1`), und sucht ihn als regulären
Ausdruck im README — auch über Soft-Wrap-Zeilenumbrüche hinweg. Vor jeder
Geometrie- oder Versions­änderung sollte der Lauf grün durchgehen.

### DFM-Strict-Modus

`try_fillet` und `try_chamfer` werden im Build an genau den Stellen mit
`strict=True` aufgerufen, die in der DFM-Tabelle den Status ✓ („vollständig
akzeptiert") tragen. Verliert eine dieser Stellen Kanten an OCCT, bricht
`./run cad` mit einer FATAL-Meldung ab: die README-Garantie wäre dann
verletzt und der Druck nicht mehr vertrauenswürdig. Stellen, die in der
Tabelle ohnehin als OCCT-Grenzfall geführt werden (die `flange corner`-Schelfs
und die `lid bot perim`-Innenkanten), bleiben best-effort und tauchen
einfach als „skipped" in der Zusammenfassung auf. Am Ende der Build-Phase
schreibt das Script eine kompakte Übersicht aller DFM-Operationen ins Log.

### FEM ausführen

Die lokale Schnapper-Simulation läuft separat vom CAD-Export:

```bash
./run fem-snap
./run fem-snap --vtk output/FEM/snap_fit_v1_1_6.vtu
./run fem-snap --json output/FEM/snap_fit_v1_1_6.json
./run fem-hook
./run fem-hook --json output/FEM/hook_hold_v1_1_6.json
./run fem-bulge
./run fem-bulge --json output/FEM/trough_bulge_v1_1_6.json \
  --vtk-dir output/FEM/vtk --plot-dir output/FEM/plots
```

#### FEM-Baseline-Vergleich

Jeder Solver schreibt eine JSON-Datei mit den wichtigsten Skalaren:
Steifigkeiten, Haltekräfte, Maximaldehnungen, Penetrationen. Diese Werte
werden gegen eine eingecheckte Baseline unter `output/FEM/baseline/` geprüft,
damit eine Geometrie- oder Solver-Änderung das Antwortverhalten nicht
unbemerkt verschiebt:

```bash
./run fem-diff                    # nur Vergleich, kein Schreiben
./run fem-diff --update-baseline  # aktuelle Ergebnisse als neue Referenz übernehmen
```

Die Default-Toleranz liegt bewusst lose bei ±15 % relativ. Die
PA12-Modul-Unsicherheit beträgt schon auf Materialebene ±15 %; engere
Schranken würden nur Fehlalarme produzieren. Felder, die physikalisch exakt
sein müssen (Penetrations-Punkte, Feasibility-Flags), werden dagegen hart
verglichen. Eine bewusst akzeptierte Designänderung wird mit
`--update-baseline` als neue Referenz übernommen. Die Baseline-Dateien
heißen absichtlich versionsfrei (`snap_fit.json` statt `snap_fit_v1_1_6.json`),
damit sie ein Versionssprung nicht verwaisen lässt.

`--vtk` und `--json` legen Zielverzeichnisse wie `output/FEM/` bei Bedarf
automatisch an.

Das `.vtu` lässt sich direkt in ParaView öffnen. Gespeichert werden:

- nodale Verschiebungen in mm
- maximale/minimale Hauptdehnung pro Tetraeder
- von-Mises-Dehnungsproxy pro Tetraeder

### Trogwand-Bauchung beim Befüllen

Für die beobachtete Bauchung der langen Trogwände gibt es
`fem/trough_bulge_fem.py`. Das Script bildet den Trog als vereinfachtes
lineares PA12-Solidmodell ab, belastet die Innenflächen der langen X-Wände
mit gleichförmigem seitlichem Granulatdruck und vergleicht den früheren
Plain-Trog gegen den aktuellen Trog mit internen Anti-Bauch-Bars.

Aktueller Befund für `v1.1.6` bei `5 kPa` Seitenlast:

- Plain-Trog ohne Bars: **0.083 mm** maximale Ausbuchtung
- aktueller Trog mit 3 internen Bars: **0.023 mm** maximale Ausbuchtung
- Druck für 1.0 mm Ausbuchtung: **60.5 kPa → 217.8 kPa**
- maximale Hauptdehnung bleibt bei beiden Varianten deutlich unter dem
  konservativen PA12-`1/3`-Proxy

Die erzeugten Heatmaps liegen unter `output/FEM/plots/`, die optionalen
ParaView-Felder unter `output/FEM/vtk/`.

### Vollbaugruppen-Kontakt / Kippmontage

Für die Baugruppenprüfung gibt es zusätzlich
`fem/lid_trough_assembly.py`. Das Script lädt **den vollständigen Deckel**
und **den vollständigen Trog** als STL, legt eine plausible
Hook-first-Bewegungsfamilie um die passive Hakenlinie an und bewertet
den Deckel dann über Signed-Distance gegen das Trogmaterial.

Lauf:

```bash
./run fem-assembly
./run fem-assembly --json output/FEM/lid_trough_assembly_v1_1_6.json
```

Auch hier wird das Zielverzeichnis der JSON-Datei bei Bedarf automatisch
angelegt.

Aktueller Befund für `v1.1.6`:

- beste gefundene Hook-first-Kipplage im Suchraum: **`-10°`**, `dx = +0.40 mm`,
  `dz = +1.20 mm`
- eingehakte Kipplage: **kollisionsfrei** (`max penetration = -0.163 mm`)
- vertikale Einfädelbahn bei dieser Kipplage: **kollisionsfrei**
- Schließbahn in die Endlage: **ohne harte Kollision**;
  verbleibende Interferenz liegt nur an den aktiven Schnappern
  (`snap ~0.94 mm`) und ist dort die beabsichtigte elastische Einfederung
- harte Restpenetration außerhalb der Schnapper: **0 Punkte**

Interpretation:

- Die passive Hakenleiste funktioniert jetzt auch als **praktisch nutzbare
  Kipp-Einhakeachse**, weil die flache Haken-Tasche bis an die
  Rabbet-Unterseite als Einführkanal geöffnet ist.
- Die Hook-first-Montage ist damit geometrisch plausibel:
  erst passive Seite einhängen, dann herunterrotieren, zuletzt die
  +X-Schnapperseite eindrücken.
- Kritisch bleibt nur noch die beabsichtigte Schnapper-Einfederung beim
  finalen Schließen, nicht mehr eine harte Baugruppen-Kollision.
- Die entfernten passiven Eckfreistiche und die neuen internen Anti-Bauch-Bars
  erzeugen im geprüften Suchraum keine harte Baugruppen-Kollision.

### Montagezeichnungen

Die Montagefolge wird zusätzlich als SVG ausgegeben:

```bash
./run drawings
```

Das Script legt `output/assembly/` bei Bedarf automatisch an.

Erzeugte Dateien:

- `output/assembly/lid_trough_assembly_sequence_v1_1_6.svg`
- `output/assembly/lid_trough_snap_detail_v1_1_6.svg`

Das Sequenzblatt zeigt die Hook-first-Montage in drei Schritten, das
Detailblatt die elastische Einfederung der aktiven Rastnase beim finalen
Eindrücken.

### Mesh-Heal für STL-Export (pymeshfix)

Die OCCT-STL-Tessellation hinterlässt an Tangenten­nähten von
Fillets/Chamfers teilweise offene Randloops und Selbstdurchdringungen.
Der Export schreibt deshalb zuerst weiterhin STEP und eine direkte OCCT-STL,
remesht die STEP-Dateien dann mit Gmsh zurück zu STL und lässt anschließend
`pymeshfix` als finalen Topologie-Heal laufen. Ist `pymeshfix` nicht
installiert, bleibt der Gmsh-remeshte STL-Stand erhalten; nur der finale
Selbstdurchdringungs-Clean wird übersprungen.

Verhalten:

- **trough.stl**: STEP→Gmsh ergibt eine wasserdichte STL; `pymeshfix` reduziert
  danach 13 Selbstdurchdringungen auf 0, bei praktisch unverändertem Volumen
  (`34.88 → 34.89 cm³`).
- **lid.stl**: STEP→Gmsh mit gröberem Lid-Remesh (`0.4 … 1.0 mm`) ergibt
  eine wasserdichte, winding-konsistente STL; `pymeshfix` überspringt den
  finalen Clean, weil bereits 0 Randloops und 0 Selbstdurchdringungen
  gefunden werden (`6.76 cm³`).

**Upload-Empfehlung** (Stand `v1.1.6`):

- `trough.stl` und `lid.stl` sind die aktuellen STL-Upload-Kandidaten
  (0 Randloops, 0 gemeldete Selbstdurchdringungen).
- `trough.step` und `lid.step` bleiben als BRep-Fallbacks verfügbar.

Optional: `./run --with-heal setup` installiert zusätzlich
`requirements-heal.txt` (`pymeshfix`). Danach nutzt `./run cad` den
finalen Heal-Schritt automatisch; ohne diese optionale Abhängigkeit läuft der
Export weiterhin durch und protokolliert nur den übersprungenen
`pymeshfix`-Clean.

## MJF-Optimierungen

### Grundparameter

| Bereich | Wert | Grund |
|---|---|---|
| Wandstärke | 2.2 mm | Nach Rabbet-Schulter 1.2 mm Restwand → oberhalb MJF-Minimum (1.0 mm) |
| Bodenstärke | 2.2 mm | Gleichwertige Struktursteifigkeit, gleichzeitig Flansch-Dicke |
| Passungsspiel `fit_clear` | 0.30 mm | MJF-typischer Toleranzbereich ±0.3 mm |
| Hex-Raster | 10 mm flats, 1.2 mm Web, 2.8 mm X-Margin, 4.0 mm Y-Margin | Grösseres Raster = weniger Stegen/Fläche, besseres Entpulvern, Stege trotzdem deutlich über MJF-Minimum |
| Anti-Bauch-Bars | 3 interne Querbars, 2.2 × 1.4 mm, 4.0 mm unter Deckelunterseite | Hält die langen X-Wände beim Befüllen gegen Ausbeulen zusammen, bleibt komplett innerhalb des 65-mm-Aussenmasses und lässt Platz für 3-mm-Obervlies |
| Eckenfillet Körper | 2.0 mm | Bessere Oberfläche; Flansch-Y-Kanten bleiben scharf (Stopperfunktion) |
| Armwurzel-Fillet | 0.5 mm | Kerbspannungsreduktion → Dauerfestigkeit des Snap-Arms |
| Snap-Mechanik | 1 einfache Hakenleiste + 2 selbstlösende Schnapper | echte passive Halte-Seite, aber einfach und MJF-freundlich, nur zwei elastische Stellen, einhändig entriegelbar |
| Entpulvern | Hex oben + unten durchgehend | Pulver rieselt frei durch die Kassette |

### DFM im Detail: 90°-Kanten-Rundungen und -Fasen

MJF-PA12 prüft keine scharfen Kanten in der Druckbarkeit — der Prozess druckt
Kanten so scharf wie das Laserscanfeld. Rundungen und Fasen werden eingesetzt,
um **(a)** Spannungskonzentrationen an konkaven Innenkanten zu reduzieren,
**(b)** Anfassbarkeit/Taktilität zu verbessern, **(c)** das Entpulvern zu
erleichtern und **(d)** Risiken beim Handling (Absplittern, scharfe Kanten)
zu vermeiden.

| Kante / Feature | Operation | Radius | Begründung | Status |
|---|---|---|---|---|
| Körper-Senkrechtkanten (4 vertikale X/Y-Ecken) | Fillet | 2.0 mm | Haupt-Oberflächenqualität, Hand-Kontaktkanten | ✓ |
| Flansch-Unterseite (4 Aussenkanten bei Z=0) | Chamfer | 0.8 mm | Fingergriff-Seite, verhindert Absplittern beim Einschub, keine scharfe Kante gegen Finger | ✓ |
| Flansch-Y-Step (2 gerade Kanten bei Z=floor, Y=±size_y/2) | Fillet | 1.0 mm | Konkaver 90°-Innenwinkel zwischen Körper-Seitenwand und Flansch-Oberseite — klassische Kerbspannungsstelle beim Einschieben | ✓ |
| Flansch-Eckenschelfs (4 Bogenkanten bei Z=floor, Körperecke ∩ Flansch-Oberseite) | Chamfer-Fallback | — | Sitzen zwischen der zylindrischen 2-mm-Körperecken­fillet und der ebenen Flansch-Oberseite → OCCT verweigert Fillet UND Chamfer (Tangentenkonflikt). Kosmetisch, ~2×2 mm, nicht lasttragend, MJF druckt sie sauber | Offen (akzeptiert) |
| Kavitäts-Bodeninnenkanten (4 Kanten bei Z=floor zwischen Bodenplatte und Kavitätswänden) | Fillet | 1.0 mm | Konkave Innenecken — Kerbspannung bei Flexion der Bodenplatte durch Kohlebett-Masse. Ausserdem: Pulver sammelt sich in scharfen 90°-Ecken, Verrundung hilft beim Entpulvern | ✓ |
| Rabbet-Schulterkanten (konkav/konvex bei Z=size_z−rabbet_depth) | Fillet | 0.3 mm | Kleine Rundung reduziert den abrupten Absatz ohne die Auflageflächen (shelf_w=1.0 mm) nennenswert zu verkleinern (verbleibend ≥0.7 mm Kontakt für Deckel) | ✓ |
| Snap-Armwurzel (Übergang Arm → Deckelunterseite) | Fillet | 0.5 mm | Klassische Cantilever-Kerbe — ohne Radius wäre das die erste Rissstelle bei Wiederholbelastung. 0.5 mm bringt Spannungskonzentrationsfaktor von ~3 auf <1.5 | ✓ |
| Deckel-Vertikalecken (4 Kanten entlang Z) | Fillet | 1.0 mm | Handling, konsistent mit Körperecken­fillet (2.0 mm wäre am kleineren Deckel-Footprint zu dominant) | ✓ |
| Deckel-Oberkante (4 Aussenkanten bei Z=size_z) | Chamfer | 0.5 mm | Sichtseite von oben, verhindert Absplittern und scharfe Kante unter dem Fingerdruck zum Öffnen | ✓ |
| Deckel-Unterkante (äussere Kanten bei Z=size_z−lid_thk inkl. Zuglippe) | Chamfer | 0.2 mm / 0.4 mm | Rabbet-Einführschräge für den Einbau; die kleine Zuglippe bekommt separat 0.4 mm. OCCT akzeptiert wegen der +X-Snapwurzel und der passiven Hakenleiste nicht alle Kanten, aktuell **1/5** gefundene Unterkanten mit 0.2 mm. Rest bleibt lokal scharf — MJF druckt sauber | Teilweise (akzeptiert) |

### Per-Kanten-Fallback für OCCT-Grenzfälle

Die Fillet/Chamfer-Operationen im Script nutzen eine `try_fillet` /
`try_chamfer`-Hilfsfunktion mit zweistufigem Fallback:

1. **Batch-Versuch**: alle selektierten Kanten auf einmal runden/fasen —
   schnell und konsistent, wenn die Geometrie es erlaubt.
2. **Per-Kanten-Versuch** bei Fehler: jede Kante einzeln; Fehler einzelner
   Kanten werden auf STDOUT protokolliert und übersprungen.

Grund: build123d/OCCT wirft eine Exception für den **gesamten** Batch, sobald
**eine einzige** Kante den gewünschten Radius nicht akzeptiert (typischer­weise
wegen Tangentenkonflikten mit anderen Radien/Zylinderflächen). Der Fallback
rettet die übrigen Kanten und gibt Diagnose aus, statt die komplette
DFM-Verbesserung zu verlieren.

### Konvex vs. konkav — Warum unterschiedliche Werte

- **Konvex/Aussen-Kanten** (Flansch-Unterseite, Körperecken): Chamfer 0.5–0.8
  mm oder Fillet 2.0 mm. Hauptzweck: Handling, Oberflächenqualität, keine
  scharfen Kanten gegen Finger oder angrenzende Flächen.
- **Konkav/Innen-Kanten** (Flansch-Step, Kavitäts-Boden, Armwurzel): Fillet
  0.3–1.0 mm. Hauptzweck: Kerbspannungsreduktion. Ein konkaver 90°-Winkel
  hat theoretisch einen unendlichen Spannungskonzentrationsfaktor; selbst
  kleine Rundungen (~10 % der Wandstärke) bringen ihn auf <2.

### Kein Powder-Trap

Alle Ausfräsungen (Kavität, Rabbet, Hex, Snap-Schlitze, flache Haken-Tasche,
Zuglippen-Freistellung) sind zur Aussenwelt bzw. nach oben geöffnet. Die
Anti-Bauch-Bars sind einfache offene Querstege, keine geschlossenen Taschen.
Die Hex-Bohrungen im Boden und Deckel sind deckungsgleich, sodass Pulver
während des Entpulverns frei hindurchfallen kann. Keine der Fillet- oder
Chamfer-Operationen schafft geschlossene Taschen.

### Druckorientierung (Empfehlung fürs Bureau)

- **Snap-Arme parallel zu den Pulverschichten** legen (Biegerichtung
  parallel zur Schichtebene). MJF ist nahezu isotrop (Z-Richtung ~5–10 %
  schwächer), aber beim 1-mm-Arm mit zyklischer Biegebelastung zählt jedes
  Prozent.
- **Flansch möglichst plan** (Z-Ebene parallel zur Baureise) → gleichmässige
  Flächenqualität auf den Dichtflächen.
- Wenn beides nicht gleichzeitig möglich ist: Priorität auf den Snap-Armen.

## Tiefenauslegung (`size_z` — Luftstromrichtung)

Kompromiss zwischen Kohlekapazität und Druckverlust durch die aktiven
Absaugungen. Nutzbarer Bettquerschnitt `cavity_x × cavity_y ≈ 60.6 × 90.6 ≈
55 cm²`, 6 parallele Pfade.

Druckverlust im AC-Granulatbett (Ergun, 3-mm-Pellets, ε ≈ 0.4):

| Face velocity | ΔP/mm Bett |
|---|---|
| 0.5 m/s | ~2.5 Pa |
| 1.0 m/s | ~8 Pa |
| 1.5 m/s | ~17 Pa |

Bei 40 mm `size_z` ergibt sich ein Kohlebett von 29.3 mm, Kapazität ~72 g pro
Kassette bei Schüttdichte ~450 kg/m³ → ~425 g gesamt über 6 Kassetten.
Erwartete Standzeit in normaler Wohnluft: ~6 Monate. ΔP bei realistischem
Arbeitspunkt (~0.5 m/s) ca. 50–80 Pa — verträglich mit
Bad-/Küchenabsaugungen (typisch 40–100 Pa statisch).

Tieferes Bett (45–55 mm) ist optional machbar, falls stärkere Absaugungen
vorhanden sind und längere Wechselintervalle gewünscht.

### Snap-Belastungs-Check

Beim Entriegeln biegt sich der Arm um `hook_protr + fit_clear = 1.40 mm`.
Maximale Randfaserdehnung in einem Cantilever:

```
ε = 3 · t · δ / (2 · L²) = 3 · 1.0 · 1.40 / (2 · 10.2²) ≈ 2.02 %
```

HP-PA12 Yield liegt laut aktuellem Datenblatt bei grob `9 … 11 %`. Das
HP-Handbook empfiehlt für Snap-Fits als Näherung `< 1/3` davon, also
`< 3.0 … 3.7 %`. `2.02 %` liegt darunter. Das Script gibt den Wert beim Lauf
zusammen mit Kraftabschätzung und PA12-Band auf STDOUT aus.

Die lokale FE-Analyse liefert konservativer **~3.4 % maximale Hauptdehnung**.
Das bleibt ebenfalls noch im HP-Proxyband, liegt aber mit bewusst kleiner
Reserve in Richtung Oberkante. Genau deshalb ist die FE hier wertvoller als
die reine Cantilever-Formel: sie setzt die Last an der realen Rastfläche und
nicht am freien Armende an.

## Materialwahl PA12 vs. PA11

Lastprofil: rund 10 Öffnungs-/Schliesszyklen in fünf Jahren, reine
Innenraumluft, ständiger Kontakt mit Aktivkohle.

**PA12 ist die aktuelle Zielgeometrie.** Längere Schnapparme, grössere
Rastüberdeckung und eine kräftigere passive Hakenleiste sind genau so
gewählt, dass das Bauteil sich auch in HP-PA12 wiederholt und werkzeugfrei
bedienen lässt. Dazu kommt das praktische Argument: PA12 ist beim
Druckdienstleister Standard, günstig und für dieses Lastprofil ausreichend,
solange die Geometrie nicht zur älteren kurzen 7-mm-Snap-Version
zurückkehrt.

**PA11 ist die robustere Snap-Fit-Wahl** und lohnt sich, sobald ein
Dienstleister es ohne Aufpreis druckt oder die Kassette deutlich öfter
geöffnet werden soll. Damit hat sich die Rolle umgedreht: PA11 ist heute
die ruhige Reserve, nicht mehr der Default.

**Druckorientierung** (falls angebbar): Snap-Arm-Biegerichtung parallel zu
den Pulverschichten legen, nicht senkrecht. MJF ist nahezu isotrop, aber
der Effekt ist in Grenzfällen messbar.

**Entpulverung**: Die Hex-Raster auf Boden und Deckel sind durchgehend, das
Gehäuse hat keine geschlossenen Taschen. Pulver rieselt frei durch die Kassette
und durch die Snap-Schlitze.

## Lizenz

Das Projekt nutzt bewusst zwei verschiedene Lizenzen — je nachdem, ob ein
Artefakt eher als Hardware-Design oder eher als Software einzuordnen ist:

- **Hardware-Design, CAD-/STEP-/STL-/SVG-Ausgaben, FEM-Ausgaben und
  Designdokumentation**: CERN Open Hardware Licence Version 2 — Strongly
  Reciprocal (`CERN-OHL-S-2.0`)
- **Software-Scripte und Tooling**: GNU Affero General Public License v3.0
  or later (`AGPL-3.0-or-later`)

`carbon_filter_build123d.py` ist beides gleichzeitig: parametrische CAD-Quelle
des physischen Produkts und ausführbares Python-Script. Sie steht deshalb als
Hardware-Design-Quelle unter `CERN-OHL-S-2.0` und, soweit sie als Software
behandelt wird, zusätzlich unter `AGPL-3.0-or-later`.

Der kurze Projekt-Lizenzhinweis liegt in `LICENSE`; die vollständigen
Lizenztexte stehen unter `LICENSES/CERN-OHL-S-2.0.txt` und
`LICENSES/AGPL-3.0-or-later.txt`.

## Parameter im Script

Alle Masse stehen als benannte Variablen am Dateianfang und sind über
Kommentare erklärt. Änderung → Datei speichern → ocp-vscode-Viewer reloadet;
Script re-exportiert STEP/STL.

## Dateien

- `run` — legt `.venv/` automatisch an, installiert Pip-Abhängigkeiten und
  startet CAD-/FEM-/Zeichnungs-Kommandos
- `LICENSE` — kurzer Projekt-Lizenzhinweis mit Scope-Aufteilung
- `LICENSES/` — vollständige Lizenztexte für CERN-OHL-S-2.0 und AGPL-3.0-or-later
- `requirements.txt` — Kernabhängigkeiten für CAD, Viewer, FEM und
  Baugruppenprüfung
- `requirements-heal.txt` — optionale STL-Heal-Abhängigkeit `pymeshfix`
- `carbon_filter_build123d.py` — build123d-Script mit ocp-vscode-Viewer
- `fem/snap_fit_fem.py` — lokale 3D-FEM für den aktiven Schnapper
- `fem/hook_hold_fem.py` — lokale 3D-FEM und Geometriecheck für die passive
  Hakenleiste
- `fem/trough_bulge_fem.py` — lineare FEM für Trogwand-Ausbeulung beim
  Befüllen und Heatmap-/VTK-Ausgabe
- `fem/lid_trough_assembly.py` — Vollbaugruppen-Kontakt und Kippmontage-Check
- `fem/assembly_sequence_svg.py` — erzeugt SVG-Montagezeichnungen
- `scripts/check_readme_sync.py` — `./run check`: prüft Geometrie- und
  Versions-Konstanten zwischen Script und README
- `scripts/fem_baseline_diff.py` — `./run fem-diff`: vergleicht die FEM-JSONs
  gegen `output/FEM/baseline/` mit `--update-baseline` zum Promoten
- `scripts/render_readme_image.py` — Blender/VTK-Rendering des Hero-Bilds
- `output/FEM/baseline/` — eingecheckte FEM-Referenzergebnisse für `fem-diff`
- `README.md` — dieses Dokument
- `CLAUDE.md` — Arbeitsanweisungen für Claude in diesem Repo
- `TODO.md` — offene Aufgaben
- `LOGBOOK.md` — Änderungs- und Entscheidungsprotokoll
