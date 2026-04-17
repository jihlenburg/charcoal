# TODO

## Offen

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
      eindrückbar?
- [ ] Fingermulde griffig genug, um die Kassette gegen den Einzug der aktiven
      Absaugung aus dem Schacht zu ziehen?
- [ ] Maßprüfung nach Druck: Deckel-Spiel 0.30 mm in Ordnung? Hex-Lochweite
      im Soll (MJF-Verzug)?
- [ ] Druckorientierung mit Bureau abstimmen (Snap-Arme parallel zu
      Schichten, Flansch möglichst plan)
- [ ] Lüfter-Specs (Modell, Volumenstrom, Statikdruck) erfassen, um
      `size_z` ggf. nachzujustieren

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
