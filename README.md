# Aktivkohlefilter-Einsatz (Passivlüftung mit aktiven Absaugungen)

**Version: 1.1.0** (im Script als `VERSION`-Konstante; wird als Gravur auf
den +Y-Flanschüberstand aufgebracht und muss beim Bump synchron mitgeführt
werden: `carbon_filter_build123d.py` → README → git-Tag).

Parametrischer Filterkorb (Grundkörper + Deckel) für Wohnungslüftung durch
Aktivkohle, konstruktiv auf HP Multi Jet Fusion in **PA12** abgestimmt
(`HP 3D HR PA 12 enabled by Evonik` oder vergleichbar). PA11 bleibt weiterhin
eine gutmütige Alternative, ist aber nicht mehr die Konstruktionsannahme.

Script: [`carbon_filter_build123d.py`](./carbon_filter_build123d.py) (build123d).

## Konstruktionsprinzip

**Vertikaler Luftstrom durch den Filter.** Die Luft tritt durch das Hex-Gitter
auf einer Z-Seite (Deckel) ein, durchströmt das Aktivkohlebett und tritt durch
das Hex-Gitter auf der anderen Z-Seite (Boden) aus. Im Skript-Koordinatensystem
ist Z die Luftstromachse; beim Einbau wird die Kassette um 90° gekippt, sodass
Z horizontal zur Schachttiefe wird.

### Befüllung (Kassette stehend, Deckel oben)

1. Finger in die mittige Freistellung an der Schnapper-Seite setzen und den
   Deckel am kleinen Zugsteg nach oben anheben; die beiden Schnapper lösen
   dabei über ihre Auslöserampe selbsttätig aus, während die Hakenleiste auf
   der Gegenseite den Deckel in ihrer Tasche hält und die Öffnungsseite definiert
2. Filtervlies auf den Boden legen (3 mm, dichtet Hex gegen Granulatdurchfall)
3. Aktivkohlegranulat einfüllen (~29 mm Schüttung, ~78 g bei 450 kg/m³)
4. Zweites Filtervlies obenauf
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

Eine X-Fläche trägt die Snap-Durchbrüche, die gegenüberliegende eine
flache Haken-Tasche im oberen Wandbereich. Beide X-Flächen pressen sich
in den seitlichen Schaumstoff — auch hier entsteht eine Dichtung durch den
Schaum.

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
  Hakenleiste mit 1.5 mm Gesamttiefe, 0.6 mm Überdeckung und einer kurzen
  schrägen Nase. Sie greift in eine flache rechteckige Tasche in der
  Gegenseite und bleibt dabei gut entpulverbar und visuell klar.
- Passive Montagefreistiche: an den beiden `-X`-Deckelecken ist in der
  Draufsicht je ein kleiner Eckfreistich (`1.6 × 8.0 mm`) ausgespart. Diese
  Entlastung sitzt bewusst **außerhalb** der mittigen Hakenleiste und dient
  nur dazu, die Hook-first-Kippmontage kollisionsfrei zu machen.
- Rastnasen: 6 mm breit, 10.2 mm lang, 1.0 mm Armdicke, 1.0 mm
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

- **Nur Führungsleiste**:
  Sehr einfach und MJF-freundlich, aber keine passive Haltefunktion. Die
  Gegenseite positioniert nur, sie trägt keinen Aufwärtslastpfad.
- **Einfache Hakenleiste**:
  Beste Balance. Ein echter Formschluss auf einer Seite, aber nur als flache,
  gut entpulverbare Tasche mit kleiner Überdeckung.
- **Tiefes Haken-/Taschensystem**:
  Mechanisch eindeutig, aber unnötig komplex, toleranzempfindlicher und für
  diesen Anwendungsfall überzogen.

### Öffnungsbewegung und Kraftfluss

Geschlossener Zustand:

- Auf der Schnapper-Seite halten die beiden Rastlippen gegen die Oberkante der
  Slots.
- Auf der Gegenseite sitzt die einfache Hakenleiste mit etwa `0.6 mm`
  Überdeckung unter dem Taschen-Dach.
- Ein Aufwärtszug am Deckel wird daher nicht nur von den Schnappern, sondern
  als Moment zwischen Schnapper-Seite und Haken-Seite aufgenommen.

Beginn des Öffnens:

- Die Fingerkraft greift an der mittigen Zuglippe auf der Schnapper-Seite an.
- Dadurch entsteht ein Drehmoment um die passive Haken-Seite.
- Die oberen Auslöserampen der Schnapper laufen gegen die Slot-Kante und
  wandeln den vertikalen Hub in seitliche Arm-Auslenkung um.
- Die dabei entstehende Reaktionskraft geht vom Finger über den Deckel in die
  Schnapper, von dort in die Trogwand der Slot-Seite.

Nach dem Lösen der Schnapper:

- Die Schnapper sind weitgehend lastfrei.
- Die passive Haken-Seite übernimmt die Führung und den Rest des Öffnungsmoments.
- Der Deckel klappt um diese Seite hoch, statt auf beiden Seiten gleichzeitig
  lose zu werden.

Vollständiges Abnehmen:

- Nach dem Hochklappen wird der Deckel leicht zur Schnapper-Seite verschoben,
  damit der passive Haken aus seiner Tasche frei kommt.
- Erst dann wird er komplett nach oben abgehoben.

### Öffnungskraft / Werkzeugfreiheit

Für die Rastarme wird der Deckel als rechteckiger Cantilever abgeschätzt.
Die reine Armsteifigkeit liefert die laterale Federkraft; die tatsächliche
Fingerkraft beim Öffnen sinkt durch die obere Auslöserampe:

```
F = 3 · E · I · δ / L³
I = b · t³ / 12
```

mit `b = 6 mm`, `t = 1 mm`, `L = 10.2 mm`, `δ = hook_protr + fit_clear = 1.3 mm`
und einem HP-PA12-Elastizitätsmodul von grob `E ≈ 1.65 … 2.20 GPa`
(JF 5200/5600-Datenblattband).

Ergebnis:

- laterale Federkraft pro Schnapper: **ca. 3.0 … 4.0 N**
- geschätzte Finger-Hebekraft gesamt: **ca. 2.8 … 3.7 N**
  für beide Schnapper zusammen, mit 2.8-mm-Auslöserampe und einer groben
  Reibannahme `μ ≈ 0.2`
- Maximale Randfaserdehnung: **≈ 1.87 %**

Damit ist die Bedienung realistisch **ohne Werkzeug** und mit einer einzigen
Fingerbewegung. Die Schnapper müssen nicht separat gedrückt werden; beim
Anheben an der Zuglippe fahren sie über die Auslöserampe selbst nach innen.

HPs Snap-Fit-Handbook empfiehlt als grobe Daumenregel eine zulässige Dehnung
von weniger als `1/3` der Fliessdehnung. Mit HP-PA12 (`~9 … 11 %` Yield im
5600-Datenblatt) ergibt sich damit ein Zielbereich `< 3.0 … 3.7 %`; die
aktuellen `~1.87 %` liegen darunter. Für diesen Anwendungsfall
(wenige Öffnungszyklen pro Jahr) ist das für PA12 deutlich plausibler als die
vorige kurze 7-mm-Geometrie.

### Lokale FEM des Schnappers

Zusätzlich zur schnellen Balkenabschätzung gibt es jetzt eine lokale
3D-FE-Analyse in `fem/snap_fit_fem.py`.
Das Modell bildet **einen aktiven Schnapper** mit der aktuellen
`v1.1.0`-Nasenform ab, belastet die reale Rastfläche mit `1 N` in `+X` und
skaliert die Antwort dann auf die nötige Öffnungs-Auslenkung
`hook_protr + fit_clear = 1.30 mm`.

Wichtig:

- Das ist bewusst ein **lokales Submodell**, kein vollständiges Kontaktmodell
  von Deckel, Trog und Gegenhaken.
- Die FE-Kraft ist **konservativer** als die Balkenformel, weil die Last an
  der realen Rastfläche bei `z ≈ -8.5 mm` angreift und nicht am absoluten
  Tip des Arms.
- Der echte `0.5 mm`-Armradius an der Deckelwurzel ist in diesem ersten
  FE-Modell noch nicht explizit ausmodelliert; die reale Spitzen-Dehnung
  sollte daher eher leicht tiefer liegen.

Aktueller Stand mit `mesh_size = 0.25 mm` und nominal `E = 2150 MPa`:

- laterale Federsteifigkeit pro Schnapper: **~7.3 N/mm**
- nötige laterale Auslenkkraft pro Schnapper für `1.30 mm`: **~9.5 N**
- geschätzte Gesamt-Hebekraft zum Öffnen: **~6.7 … 9.0 N**
- maximale Hauptdehnung beim Öffnen: **~3.2 %**

Damit bleibt werkzeugloses Öffnen weiterhin plausibel. Für wiederholtes
Öffnen liegt die erste FE-Abschätzung noch innerhalb des HP-`1/3`-Proxybands
für PA12 (`< 3.0 … 3.7 %`), aber mit kleinerer Reserve als die reine
Balkenformel suggeriert.

### Innenaufbau (Luftweg-Richtung: Deckel → Boden)

```
Hex-Deckel → 3 mm Filtervlies → Aktivkohlebett (~29 mm) → 3 mm Filtervlies → Hex-Boden
```

Das Bett sitzt zwischen zwei Vlieslagen, die gleichzeitig als
Partikel-Rückhalt und als Staubfilter wirken.

## Nutzung

```bash
pip install build123d ocp-vscode gmsh meshio scikit-fem trimesh rtree
```

1. VSCode öffnen, Command Palette → „OCP CAD Viewer: Open Viewer"
2. `python carbon_filter_build123d.py` ausführen
3. Viewer-Panel: Maus zum Drehen, Scroll zum Zoomen

Datei speichern triggert Live-Reload im Viewer. Beim Ausführen werden
automatisch die Exporte in `output/STEP/` (für STEP) und `output/STL/`
(für STL) geschrieben — je eine `trough.*` und `lid.*` Datei.

`EXPLODED = True` hebt den Deckel 30 mm über den Trog; für die
Zusammenbau-Ansicht auf `False` setzen.

### FEM ausführen

Die lokale Schnapper-Simulation läuft separat vom CAD-Export:

```bash
python fem/snap_fit_fem.py
python fem/snap_fit_fem.py --vtk output/FEM/snap_fit_v1_1_0.vtu
python fem/snap_fit_fem.py --json output/FEM/snap_fit_v1_1_0.json
```

`--vtk` und `--json` legen Zielverzeichnisse wie `output/FEM/` bei Bedarf
automatisch an.

Das `.vtu` lässt sich direkt in ParaView öffnen. Gespeichert werden:

- nodale Verschiebungen in mm
- maximale/minimale Hauptdehnung pro Tetraeder
- von-Mises-Dehnungsproxy pro Tetraeder

### Vollbaugruppen-Kontakt / Kippmontage

Für die Baugruppenprüfung gibt es zusätzlich
`fem/lid_trough_assembly.py`. Das Script lädt **den vollständigen Deckel**
und **den vollständigen Trog** als STL, legt eine plausible
Hook-first-Bewegungsfamilie um die passive Hakenlinie an und bewertet
den Deckel dann über Signed-Distance gegen das Trogmaterial.

Lauf:

```bash
python fem/lid_trough_assembly.py
python fem/lid_trough_assembly.py --json output/FEM/lid_trough_assembly_v1_1_0.json
```

Auch hier wird das Zielverzeichnis der JSON-Datei bei Bedarf automatisch
angelegt.

Aktueller Befund für `v1.1.0`:

- beste gefundene Hook-first-Kipplage im Suchraum: **`-15°`**, `dx = +0.40 mm`,
  `dz = +1.20 mm`
- eingehakte Kipplage: **kollisionsfrei** (`max penetration = -0.125 mm`)
- vertikale Einfädelbahn bei dieser Kipplage: **kollisionsfrei**
- Schließbahn in die Endlage: **ohne harte Kollision**;
  verbleibende Interferenz liegt nur an den aktiven Schnappern
  (`snap ~0.98 mm`) und ist dort die beabsichtigte elastische Einfederung
- harte Restpenetration außerhalb der Schnapper: **0 Punkte**

Interpretation:

- Die passive Hakenleiste funktioniert jetzt auch als **praktisch nutzbare
  Kipp-Einhakeachse**, weil die beiden passiven Deckelecken lokal entlastet
  wurden.
- Die Hook-first-Montage ist damit geometrisch plausibel:
  erst passive Seite einhängen, dann herunterrotieren, zuletzt die
  +X-Schnapperseite eindrücken.
- Kritisch bleibt nur noch die beabsichtigte Schnapper-Einfederung beim
  finalen Schließen, nicht mehr eine harte Baugruppen-Kollision.
- Frühere Checker-Läufe vor den passiven Eckfreistichen sind damit
  dokumentarisch überholt.

### Montagezeichnungen

Die Montagefolge wird zusätzlich als SVG ausgegeben:

```bash
python fem/assembly_sequence_svg.py
```

Das Script legt `output/assembly/` bei Bedarf automatisch an.

Erzeugte Dateien:

- `output/assembly/lid_trough_assembly_sequence_v1_1_0.svg`
- `output/assembly/lid_trough_snap_detail_v1_1_0.svg`

Das Sequenzblatt zeigt die Hook-first-Montage in drei Schritten, das
Detailblatt die elastische Einfederung der aktiven Rastnase beim finalen
Eindrücken.

### Mesh-Heal für STL-Export (pymeshfix)

Die OCCT-STL-Tessellation hinterlässt typischerweise ~0.02 % nicht-manifold
Kanten und Selbstdurchdringungen an Tangenten­nähten von Fillets/Chamfers —
Druck-Bureau-Slicer (Shapeways/Sculpteo/Protolabs) lehnen solche Meshes ab
oder heilen automatisch mit ungewissem Ergebnis. Der Export ruft deshalb
`_heal_stl()` nach dem `export_stl()` auf. Ist `pymeshfix` nicht installiert,
läuft der Export trotzdem durch und protokolliert nur, dass der Heal-Schritt
übersprungen wurde.

Verhalten:

- **trough.stl**: typischerweise 1 Randloop + ~300 Selbstdurchdringungen
  → nach Heal **0 / 0**, Volumen-Erhalt ≤ 0.5 %. Clean für Upload.
- **lid.stl**: typischerweise 0 Randloops + ~80 Selbstdurchdringungen.
  Hier schlägt die Heal-Kaskade fehl — die Durchdringungen sitzen
  topologisch fundamental (hex-perforierte Platte + Snap-Arm-Wurzel),
  pymeshfix's `strong_intersection_removal` kaskadiert in Komponenten­verlust
  (Volumen fällt von 7.25 auf 0.04 cm³). Der Volumen-Wächter (≤ 5 %
  Abnahme) bricht deshalb ab und behält das Original.

**Upload-Empfehlung** (Stand 2026-04-18, ein Bureau-Round):

- `trough.stl` (geheilt) → akzeptiert.
- `lid.stl` (ungeheilt, 83 Selbstdurchdringungen ~2.5 %) → ebenfalls
  akzeptiert; das Bureau-Auto-Heal kommt damit klar.
- `lid.step` bleibt als clean-by-construction-Option verfügbar, aber nicht
  nötig für den Upload.

Optional: `pip install pymeshfix`.

## MJF-Optimierungen

### Grundparameter

| Bereich | Wert | Grund |
|---|---|---|
| Wandstärke | 2.2 mm | Nach Rabbet-Schulter 1.2 mm Restwand → oberhalb MJF-Minimum (1.0 mm) |
| Bodenstärke | 2.2 mm | Gleichwertige Struktursteifigkeit, gleichzeitig Flansch-Dicke |
| Passungsspiel `fit_clear` | 0.30 mm | MJF-typischer Toleranzbereich ±0.3 mm |
| Hex-Raster | 10 mm flats, 1.2 mm Web, 4 mm Margin | Grösseres Raster = weniger Stegen/Fläche, besseres Entpulvern, Stege trotzdem deutlich über MJF-Minimum |
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
| Deckel-Unterkante (äussere Kanten bei Z=size_z−lid_thk inkl. Zuglippe) | Chamfer | 0.2 mm / 0.4 mm | Rabbet-Einführschräge für den Einbau; die kleine Zuglippe bekommt separat 0.4 mm. OCCT akzeptiert wegen der +X-Snapwurzel und der passiven Hakenleiste nicht alle Kanten, aktuell **2/6** Grundkanten mit 0.2 mm. Rest bleibt lokal scharf — MJF druckt sauber | Teilweise (akzeptiert) |

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
Hex-Bohrungen im Boden und Deckel sind deckungsgleich, sodass Pulver während
des Entpulverns frei hindurchfallen kann. Keine der Fillet- oder
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

Beim Entriegeln biegt sich der Arm um `hook_protr + fit_clear = 1.30 mm`.
Maximale Randfaserdehnung in einem Cantilever:

```
ε = 3 · t · δ / (2 · L²) = 3 · 1.0 · 1.30 / (2 · 10.2²) ≈ 1.87 %
```

HP-PA12 Yield liegt laut aktuellem Datenblatt bei grob `9 … 11 %`. Das
HP-Handbook empfiehlt für Snap-Fits als Näherung `< 1/3` davon, also
`< 3.0 … 3.7 %`. `1.87 %` liegt darunter. Das Script gibt den Wert beim Lauf
zusammen mit Kraftabschätzung und PA12-Band auf STDOUT aus.

Die lokale FE-Analyse liefert konservativer **~3.2 % maximale Hauptdehnung**.
Das bleibt ebenfalls noch im HP-Proxyband, liegt aber erkennbar naher an der
Unterkante `3.0 %`. Genau deshalb ist die FE hier wertvoller als die reine
Cantilever-Formel: sie setzt die Last an der realen Rastfläche und nicht am
freien Armende an.

## Materialwahl PA12 vs. PA11

Lastprofil: ca. 10 Öffnungs-/Schliesszyklen in 5 Jahren, Innenraumluft,
Kontakt mit Aktivkohle.

- **PA12 ist jetzt die Zielgeometrie**: längere Schnapparme, grössere
  Rastüberdeckung und eine kräftigere passive Hakenleiste sind explizit so
  gewählt, dass HP-PA12 damit plausibel wiederholt und werkzeugfrei bedienbar
  bleibt.
- **PA11 bleibt die robustere Snap-Fit-Wahl**, falls ein Dienstleister es
  ohne Mehrpreis anbietet oder wenn deutlich häufigere Öffnungszyklen erwartet
  werden.
- **PA12 bleibt attraktiver im Standard-Bureau-Workflow**: verbreitet, günstig
  und für dieses Lastprofil ausreichend, solange die Geometrie nicht wieder auf
  die ältere, kürzere 7-mm-Snap-Version zurückfällt.

**Bureau-Bezug**: Für die aktuelle Version ist PA12 der Default. PA11 ist ein
optional noch gutmütigerer Fallback, nicht mehr umgekehrt.

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
- `fem/snap_fit_fem.py` — lokale 3D-FEM für den aktiven Schnapper
- `fem/lid_trough_assembly.py` — Vollbaugruppen-Kontakt und Kippmontage-Check
- `fem/assembly_sequence_svg.py` — erzeugt SVG-Montagezeichnungen
- `README.md` — dieses Dokument
- `CLAUDE.md` — Arbeitsanweisungen für Claude in diesem Repo
- `TODO.md` — offene Aufgaben
- `LOGBOOK.md` — Änderungs- und Entscheidungsprotokoll
