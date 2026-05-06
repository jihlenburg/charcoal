# TODO

## Offen

- [ ] `trough.stl` (geheilt) erneut beim Bureau hochladen und DFM-Check
      verifizieren (erwartet: 0 non-manifold, 0 Randkanten,
      0 Selbstdurchdringungen)
- [ ] Viewer-/Druckmuster-Recheck `v1.1.5`: fluchten die zwei +X-Slots mit den
      Schnappern, und sitzt die einfache -X-Hakenleiste sauber in ihrer Tasche?
- [ ] Fingergriff: reicht der 10 mm Y-Flanschüberstand, um die Kassette
      gegen den Sog der Absaugung zu ziehen? Prüfung nach Druckmuster.
- [ ] Armwurzel-Fillet visuell prüfen — Kanten-Selektor ist bbox-gefiltert,
      sollte jetzt robust greifen
- [ ] Probe-Einbau im Schacht: Flansch fängt an Oberkante/Unterkante? X passt
      ohne Anstehen durch die 70 mm Hartöffnung? Kassette steht die
      erwarteten 2.2 mm aus dem Schacht?
- [ ] Moosgummistreifen auf Y-Flächen des Körpers auswählen (Materialstärke
      auf Spalt ~3.5 mm zwischen Körper und harter Schachtwand abstimmen)
- [ ] Öffnungsbedienung am Druckmuster prüfen: reicht die mittige
      Ein-Finger-Hebebewegung an der Zuglippe? Lösen beide Schnapper sauber
      über die Auslöserampe? 1.1-mm-Lippen und 1.2-mm-Zuglippe MJF-sauber
      gedruckt?
- [ ] Passive Seite am Druckmuster prüfen: bleibt der -X-Haken beim Öffnen
      definiert eingehakt und klappt der Deckel tatsächlich um diese Seite
      auf? Reicht die kleine Verschiebebewegung zum kompletten Aushängen?
- [ ] Hook-first-Montage am Druckmuster plausibilisieren: greifen die neuen
      passiven Eckfreistiche praktisch wie im Baugruppen-Checker, und lässt
      sich der Deckel tatsächlich erst einhängen und dann herunterkippen?
- [ ] Maßprüfung nach Druck: Deckel-Spiel 0.30 mm in Ordnung? Hex-Lochweite
      im Soll (MJF-Verzug)?
- [ ] Druckorientierung mit Bureau abstimmen (Snap-Arme parallel zu
      Schichten, Flansch möglichst plan)
- [ ] FE-Abschätzung am Druckmuster plausibilisieren: subjektiv ~8–11 N
      Gesamt-Hebekraft? Wiederholtes Öffnen ohne Whitening/Rissbildung?
- [ ] Lüfter-Specs (Modell, Volumenstrom, Statikdruck) erfassen, um
      `size_z` ggf. nachzujustieren
- [ ] DFM-Check am Druckmuster: wirken die gefilleteten Kanten (Flansch-Step
      1.0 mm, Kavitätsboden 1.0 mm, Rabbet 0.3 mm) visuell / haptisch wie
      gewünscht? Sind die 4 offenen Flansch-Eckenschelfs (OCCT-Limitation)
      wirklich nur kosmetisch?
- [ ] Deckel-DFM am Druckmuster: Eckenfillet 1.0 mm, Oberkanten-Chamfer 0.5 mm,
      Unterkanten-Chamfer 0.2 mm / Zuglippen-Chamfer 0.4 mm haptisch ok?
      Stören die lokal scharfen Restkanten (OCCT-Limitation) beim Einsetzen?
- [ ] Optional v1.1.5: Flansch-Eckenschelfs durch Redesign (Flansch mit
      eigenen Ecken-Fillets) auflösen — nur falls das Druckmuster tatsächlich
      stört
- [ ] Lesbarkeit der Versionsgravur am Druckmuster prüfen — Font-Size 5 mm,
      Tiefe 0.6 mm ausreichend bei MJF/PA12? Ggf. Tiefe auf 0.8 mm erhöhen

## In Arbeit

_(leer)_

## Erledigt

- [x] Automatische Pip-/Venv-Umgebung ergänzt (2026-05-06):
      - `run` legt `.venv/` an und aktualisiert Abhängigkeiten aus
        `requirements.txt` nur bei Manifest-Änderung
      - Wrapper-Kommandos für CAD, lokale FEM, Baugruppenprüfung und
        Montagezeichnungen ergänzt
      - `pymeshfix` als optionale Heal-Abhängigkeit nach
        `requirements-heal.txt` ausgelagert

- [x] Aktive Schnapper moderat straffer gemacht (2026-05-06):
      - Version/Gravur auf `v1.1.3` angehoben
      - `hook_protr` 1.0 → 1.1 mm
      - lokale FEM: nominell ~10.3 N laterale Auslenkkraft pro Schnapper,
        ~10.4 N Gesamt-Hebekraft, FE-Band ~8.0–10.6 N
      - maximale Hauptdehnung ~3.4 %, weiterhin im PA12-`1/3`-Proxyband mit
        kleiner Reserve
      - Baugruppen-Checker bleibt kollisionsfrei; harte Restpenetration
        weiterhin 0 Punkte

- [x] Trogseitige Haken-Retentionslippe ergänzt (2026-05-06):
      - Version/Gravur auf `v1.1.5` angehoben
      - Haken-Tasche zweistufig: 1.35 mm tiefe Retentionstasche unten,
        0.55 mm tiefer Einführkanal oben
      - dadurch bleibt eine 0.80 mm tiefe Materiallippe in der Trogwand,
        unter der die Haken-Nase sichtbar trägt
      - äußerste Haken-Nase mit 0.2-mm-Fase entschärft
      - lokale Hook-FEM: PA12-`1/3`-Proxy-Haltekraft ~174–213 N
      - Baugruppen-Checker bleibt kollisionsfrei; harte Restpenetration
        weiterhin 0 Punkte

- [x] Passive Hakenleiste verstärkt und Haltekraft geprüft (2026-05-06):
      - Version/Gravur auf `v1.1.4` angehoben
      - realer Untergriff hinter der Trog-Innenwand 0.70 → 1.05 mm
      - Haken-Nase 0.35 mm über die Deckelkante nach außen gezogen
      - oberer Hakensteg 0.40 → 1.00 mm, Querschnitt 34 mm²
      - neuer Solver `fem/hook_hold_fem.py`
      - lokale Hook-FEM: PA12-`1/3`-Proxy-Haltekraft ~103–125 N
      - Baugruppen-Checker bleibt kollisionsfrei; harte Restpenetration
        weiterhin 0 Punkte

- [x] Breite nach Druckmuster-Fit auf 65 mm erhöht, Hook verstärkt und
      STEP-remesh-STLs ergänzt (2026-05-06):
      - `size_x` 62 → 65 mm, Flansch-Footprint jetzt 65 × 113 × 2.2 mm
      - Version/Gravur auf `v1.1.2` angehoben
      - passive Haken-Überdeckung 0.6 → 1.1 mm
      - passive Haken-Tasche auf 3.4 mm Höhe erweitert, damit der
        Hook-first-Checker mit der breiteren Baugruppe wieder kollisionsfrei
        bleibt
      - STL-Export auf STEP→Gmsh-Remesh plus `pymeshfix` umgestellt;
        `trough.stl` und `lid.stl` sind jetzt beide watertight mit 0
        gemeldeten Selbstdurchdringungen
      - STEP/STL und Montage-SVGs neu erzeugt

- [x] Release `v1.1.0` vorbereitet (2026-04-19):
      - asymmetrische Deckelverriegelung `1 einfache Hakenleiste + 2 Schnapper`
      - selbstlösende Schnapper mit oberer Auslöserampe
      - Zuglippe + Freistellung auf der Schnapper-Seite
      - Schnapperlänge 6.0 → 7.0 mm für geringere Öffnungskraft
      - Kraftabschätzung dokumentiert (~5.6–6.3 N lateral pro Schnapper,
        ~4.5 N Hebekraft gesamt)
      - `_heal_stl()` toleriert fehlendes `pymeshfix`

- [x] Lokale FEM für aktiven Schnapper ergänzt (2026-04-19):
      - neuer Solver `fem/snap_fit_fem.py`
      - Gmsh + scikit-fem Workflow
      - nominell ~9.5 N laterale Auslenkkraft pro Schnapper
      - nominell ~8.8 N Gesamt-Hebekraft, FE-Band ~6.7–9.0 N
      - maximale Hauptdehnung ~3.2 %

- [x] Vollbaugruppen-Kontaktmodell ergänzt (2026-04-19):
      - neuer Solver `fem/lid_trough_assembly.py`
      - voller Deckel gegen vollen Trog als starre STL-Baugruppe
      - Hook-first-Kinematik um passive Hakenlinie geprüft
      - passive `-X`-Eckfreistiche ergänzt und erneut geprüft
      - Hook-first-Kipp-/Einhakebahn im Suchraum jetzt geometrisch plausibel
      - harte Restkollision eliminiert; verbleibende Interferenz nur an den
        aktiven Schnappern als beabsichtigte elastische Einfederung

- [x] SVG-Montagezeichnungen ergänzt (2026-04-19):
      - neuer Generator `fem/assembly_sequence_svg.py`
      - Sequenzblatt für Einhängen → Herunterkippen → Einrasten
      - Detailblatt zur elastischen Schnapper-Einfederung

- [x] Dokumentation auf aktuellen `v1.1.0`-Stand synchronisiert (2026-04-19):
      - README beschreibt den aktualisierten Hook-first-Befund mit
        passiven Eckfreistichen als gültigen Stand
      - Beispielpfade für FEM-/Assembly-JSON und VTK dokumentiert
        inklusive Auto-Anlage der Zielverzeichnisse
      - SVG-Montagezeichnungen und Ausgabepfade dokumentiert
      - veraltete Kinematik-Blocker aus README/TODO bereinigt und nur noch als
        Zwischenstand im Logbuch eingeordnet

- [x] FreeCAD-Macro gelöscht, alle Referenzen entfernt (2026-04-17)
- [x] build123d-Script MJF-optimiert (2026-04-17):
      - Wände 1.8 → 2.2 mm
      - `fit_clear` 0.15 → 0.30 mm
      - Rabbet-Geometrie korrigiert (vorher 0.3 mm fragile Innenlippe)
      - Snap-Mechanik auf Durchbrüche in Aussenwand umgestellt
      - Armwurzel-Fillet 0.5 mm
      - Hex-Randabstand 3 → 4 mm
- [x] Material-Entscheidung PA11 (2026-04-17)
- [x] `hook_arm` auf 1.0 mm (2026-04-17)
- [x] CLAUDE.md, TODO.md, LOGBOOK.md angelegt (2026-04-17)
- [x] Schacht-Fit-Redesign (2026-04-18):
      - `size_x` 65 → 62 mm (1.5 mm Schaumstoff-Kompression pro Seite)
      - `size_y` 45 → 40 mm (ΔP-optimiert, ~30 mm Kohlebett, ~6 Mon.)
      - Snap-Durchbrüche nur an X-Seiten (Schaumstoff-Kontakt)
      - Fingermulde vorn oben (25 × 6 × 1.2 mm)
- [x] Grundlegende Umkonstruktion auf vertikalen Luftstrom (2026-04-18):
      - Hex jetzt auf Z-Flächen (Boden + Deckel), nicht mehr Y
      - Z (Luftstromachse) = 40 mm, Y (Schachthöhe) = 93 mm
      - Deckel ist abnehmbar und schnappt von oben auf
      - Einbaulage umgedreht: Deckel nach hinten, Boden nach vorne
      - Einschub-Stopper als Boden-Flansch, nur in Y verbreitert
        (62 × 103 × 2.2 mm), X bleibt ≤ 70 mm Hartöffnung
      - Moosgummi auf Y-Flächen für Axialabdichtung (user-applied)
      - Armwurzel-Fillet robust per bbox-Filter
- [x] Nach erstem Viewer-Check (2026-04-18):
      - Snap-Slot -X: Offset-Vorzeichen korrigiert, schneidet jetzt sauber
        durch beide X-Wände
      - Fingermulde entfernt (ergonomisch sinnlos); Fingergriff übernimmt
        der Y-Flanschüberstand
      - Hex-Raster 8 → 10 mm flats (48 % Offenfläche, Web 1.2 mm, Margin
        4 mm unverändert)
      - Flanschüberstand Y 5 → 10 mm (besserer Fingergriff, Flansch
        62 × 113 × 2.2 mm)
- [x] git init, Root-Commit, Tag `v1.0.0` (2026-04-18)
- [x] Output-Reorganisation `output/STEP/` + `output/STL/`, destruktiv in
      v1.0.0 eingefaltet (2026-04-18)
- [x] Versionsgravur v1.0.1 auf +Y-Flanschüberstand (2026-04-18):
      Font-Size 5 mm, 0.6 mm tief, Arial, Position auf Z=0-Fläche des
      Flansches; `VERSION`-Konstante im Script-Header. Gravur-Ebene
      gespiegelt (x_dir=-X, z_dir=-Z, y_dir=+Y) damit der Text aus der
      Apartment-Sichtrichtung (-Z) korrekt lesbar ist.
- [x] STL-Mesh-Heal (2026-04-18):
      - `pymeshfix` als Dependency; Post-Export-Schritt `_heal_stl`
      - Trough: 1 Randloop + 296 Selbstdurchdringungen → **0 / 0** (clean)
      - Lid: abort — Heal würde Volumen von 7.25 → 0.04 cm³ zerstören
        (Selbstdurchdringungen sind bei hex-perforierter Platte
        topologisch fundamental, nicht reparierbar ohne Komponentenverlust)
      - Volumen-Wächter (≤ 5 % Abnahme) behält bei Fehler das Original
      - Bureau-Test (2026-04-18): `lid.stl` ungeheilt akzeptiert, Auto-Heal
        kommt mit den 83 Selbstdurchdringungen klar
- [x] Deckel-DFM (2026-04-18):
      - `lid_corner_fil` 1.0 mm (4 vertikale Ecken, Handling)
      - `lid_top_cham` 0.5 mm (4 Oberkanten, Absplitterschutz)
      - `lid_bot_cham` 0.2 mm (Rabbet-Einführschräge) — 2/4 Kanten (Y-Seiten)
        angenommen; 2 X-Seiten-Kanten OCCT-verweigert wegen Nähe zur
        Armwurzel­fillet, bleiben scharf (nicht handgriffrelevant)
      - Reihenfolge: Chamfers vor Eckenfillet (Topologie-Konsistenz)
- [x] DFM-Optimierung (2026-04-18):
      - `try_fillet` / `try_chamfer` mit Per-Kanten-Fallback bei
        OCCT-Konflikten
      - Flansch-Unterseite 4 Chamfer 0.8 mm (Handling)
      - Flansch-Y-Step 2 gerade Kanten Fillet 1.0 mm (Kerbspannung)
      - Flansch-Eckenschelfs 4 Bögen: Fillet und Chamfer verweigert von
        OCCT (Tangentenkonflikt mit 2-mm-Körperecken­fillet) — akzeptiert
        als kosmetische Limitation
      - Kavitäts-Bodeninnenkanten 4 Fillet 1.0 mm (Kerbspannung + Entpulvern)
      - Rabbet-Schulterkanten Fillet 0.3 mm (weicher Step, Schulter bleibt
        mindestens 0.7 mm breit)
      - `hook_protr` 0.45 → 0.50 mm (MJF-min. positives Feature;
        Armdehnung 3.12 % → 3.33 %, weiterhin <5 % Fliessgrenze)
