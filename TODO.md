# TODO

## Offen

- [ ] `trough.stl` (geheilt) erneut beim Bureau hochladen und DFM-Check
      verifizieren (erwartet: 0 non-manifold, 0 Randkanten,
      0 Selbstdurchdringungen)
- [ ] Viewer-Recheck nach Fix: sind **beide** Slots jetzt komplett durch die
      X-Wände geschnitten und die Rastnasen fluchten mit ihren Slots?
- [ ] Fingergriff: reicht der 10 mm Y-Flanschüberstand, um die Kassette
      gegen den Sog der Absaugung zu ziehen? Prüfung nach Druckmuster.
- [ ] Armwurzel-Fillet visuell prüfen — Kanten-Selektor ist bbox-gefiltert,
      sollte jetzt robust greifen
- [ ] Probe-Einbau im Schacht: Flansch fängt an Oberkante/Unterkante? X passt
      ohne Anstehen durch die 70 mm Hartöffnung? Kassette steht die
      erwarteten 2.2 mm aus dem Schacht?
- [ ] Moosgummistreifen auf Y-Flächen des Körpers auswählen (Materialstärke
      auf Spalt ~3.5 mm zwischen Körper und harter Schachtwand abstimmen)
- [ ] Rastnasen hörbar einrastend? Beide Lippen gleichzeitig zum Öffnen
      eindrückbar? Prüfen, ob die 0.50-mm-Lippe MJF-sauber gedruckt wurde
- [ ] Maßprüfung nach Druck: Deckel-Spiel 0.30 mm in Ordnung? Hex-Lochweite
      im Soll (MJF-Verzug)?
- [ ] Druckorientierung mit Bureau abstimmen (Snap-Arme parallel zu
      Schichten, Flansch möglichst plan)
- [ ] Lüfter-Specs (Modell, Volumenstrom, Statikdruck) erfassen, um
      `size_z` ggf. nachzujustieren
- [ ] DFM-Check am Druckmuster: wirken die gefilleteten Kanten (Flansch-Step
      1.0 mm, Kavitätsboden 1.0 mm, Rabbet 0.3 mm) visuell / haptisch wie
      gewünscht? Sind die 4 offenen Flansch-Eckenschelfs (OCCT-Limitation)
      wirklich nur kosmetisch?
- [ ] Deckel-DFM am Druckmuster: Eckenfillet 1.0 mm, Oberkanten-Chamfer 0.5 mm,
      Unterkanten-Chamfer 0.2 mm (2/4 Y-Seiten) haptisch ok? Stören die 2
      scharfen X-Seiten-Unterkanten (OCCT-Limitation) beim Einsetzen?
- [ ] Optional v1.0.2: Flansch-Eckenschelfs durch Redesign (Flansch mit
      eigenen Ecken-Fillets) auflösen — nur falls das Druckmuster tatsächlich
      stört
- [ ] Lesbarkeit der Versionsgravur am Druckmuster prüfen — Font-Size 5 mm,
      Tiefe 0.6 mm ausreichend bei MJF/PA11? Ggf. Tiefe auf 0.8 mm erhöhen

## In Arbeit

_(leer)_

## Erledigt

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
