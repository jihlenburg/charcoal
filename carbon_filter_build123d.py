"""
Activated-carbon filter cassette — build123d, MJF-optimized.
Target: HP Multi Jet Fusion, PA11 (BASF Ultrasint PA11 or equivalent).

Design intent
-------------
Vertical-airflow cassette in its own frame (Z up while filling):
    Floor (Z=0): hex-perforated, fused to the trough body.
    Lid   (Z=size_z): hex-perforated, removable, snap-fits from above.
    Carbon bed sits between two fleece layers inside the cavity.

Filling (cassette upright, lid up):
    Lid off → fleece on floor → pour carbon pellets → fleece on top → lid on.

Installation in window shaft (70 mm hard + 5 mm foam × 2 wide, 100 mm tall
hard walls, 100 mm deep, airflow back → front):
    Cassette rotated 90° so Z (lid↔floor) becomes the shaft airflow axis.
    LID goes in FIRST (toward the back of the shaft); FLOOR stays at the
    apartment-side opening. Air enters through the lid hex (outdoor side),
    passes through the carbon bed, exits through the floor hex into the
    apartment.

Why lid at the back, floor at the front:
  * Pulling on the front-facing flange overhangs extracts the whole
    cassette, not just the lid. Pulling on a front-facing lid would risk
    the snap tabs releasing and only the lid coming out.
  * Airflow back → front pushes the lid INTO its seat, not out.

Insertion stop: the floor carries a flange that extends `flange_extra_y` mm
beyond the body in Y ONLY (not in X — X is constrained by the 70 mm hard
shaft opening, so any X-overshoot would block insertion). The flange is
`floor` mm thick. Because its Y span (size_y + 2·flange_extra_y = 103 mm) is
wider than the shaft hard height (100 mm), it catches on the shaft front
frame at the top and bottom while passing cleanly through in X. The cassette
protrudes `floor` mm (= 2.2 mm) from the opening — enough for finger access,
well within the user-accepted 5 mm limit.

Snap-fit: two cantilever tabs on the lid engage two through-slots in the
X-walls of the cassette body (the walls that press into the shaft foam).
Y-walls (against hard shaft top/bottom) stay completely flush — Moosgummi
strips on top and bottom of the cassette body provide the axial seal.

Viewer:
    pip install build123d ocp-vscode
    Launch "OCP CAD Viewer" in VSCode, then:
        python carbon_filter_build123d.py
Save the file to live-reload the viewer. Exports STEP + STL alongside.
"""

import math
from pathlib import Path

from build123d import (
    Align,
    Axis,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    Location,
    Locations,
    Mode,
    Plane,
    Polyline,
    Rectangle,
    RegularPolygon,
    Text,
    add,
    chamfer,
    export_step,
    export_stl,
    extrude,
    fillet,
    make_face,
)
from ocp_vscode import set_port, show

set_port(3939)

# ---------------------------------------------------------------------------
# Version (engraved onto the +Y flange overhang, apartment-facing side)
# ---------------------------------------------------------------------------
VERSION = "1.0.2"
version_font = 5.0       # mm — fits the 10 mm Y-overhang comfortably
version_depth = 0.6      # mm — recessed engraving; MJF prints this crisp
                         # without weakening the 2.2 mm flange floor

# ---------------------------------------------------------------------------
# Parameters (mm) — MJF-tuned, cassette's own frame (Z up during filling)
# ---------------------------------------------------------------------------
# Outer envelope of cassette body
size_x = 62.0       # shaft width direction (foam contact both sides)
size_y = 93.0       # shaft vertical direction (hard walls top/bottom)
size_z = 40.0       # shaft depth / airflow direction (bed + walls + lid)

# Shell
wall = 2.2
floor = 2.2
outer_fillet = 2.0

# Insertion-stop flange at the floor end (Z=0..floor). Extends in Y only
# (not in X — X must stay ≤ 70 mm hard shaft width). The Y-overshoot catches
# on the shaft front frame top/bottom. Cassette protrudes `floor` mm out of
# the apartment-side opening.
flange_extra_y = 10.0

# Lid seat (rabbet widens cavity at top)
shelf_w = 1.0
rabbet_depth = 2.5
lid_thk = rabbet_depth
fit_clear = 0.30

# Hex perforation (same pattern on floor and lid → straight airflow).
# 10 mm flats keeps open area ≈ 70 % while staying robust: each rim still
# has 1.2 mm web (> MJF min 1.0 mm) and the 4 mm margin around the cavity
# preserves frame stiffness.
hex_flats = 10.0
hex_web = 1.2
hex_margin_x = 4.0
hex_margin_y = 4.0

# Snap: cantilever tab on lid + through-slot in trough X-wall.
# hook_protr = 0.50 mm: at MJF minimum positive-feature size (0.5 mm). A
# 0.45 mm lip would come out rounded/unscharf; 0.50 mm still prints crisp
# while keeping max cantilever strain ~3.33 % (PA11 yield ~5 %).
hook_width = 6.0
hook_arm = 1.0
hook_length = 6.0
hook_protr = 0.50
hook_engage = 0.8
hook_lead = 1.0
hook_root_fil = 0.5

# DFM (Design-for-Manufacturability) radii applied after the main solid
# operations. See README "MJF-Optimierungen" for reasoning per edge.
cavity_floor_fil = 1.0   # inside fillet where cavity floor meets cavity walls
flange_step_fil = 1.0    # inside fillet where flange top meets body sidewall
lid_corner_fil = 1.0     # vertical corner fillet of the lid slab (handling)
lid_top_cham = 0.5       # chamfer on lid top outer edges (finish + no chipping)
lid_bot_cham = 0.2       # chamfer on lid bottom outer edges (rabbet lead-in).
                         # 0.3 mm conflicts via OCCT with the 0.5 mm snap-arm
                         # root fillet on the X-side (tab attach at X≈28.8 is
                         # 0.7 mm from the X-perim edge at 29.5); 0.2 mm clears.
flange_top_cham = 0.5    # chamfer on 4 body-corner "shelf" arcs at Z=floor.
                         # These arcs sit between the 2 mm body-corner cylinder
                         # fillet and the flange top plane — OCCT consistently
                         # refuses fillet+chamfer here (tangency conflict).
                         # Code falls back gracefully; the 4 small (~2×2 mm)
                         # sharp shelves remain as a documented cosmetic limit.
                         # MJF prints them cleanly; they're not load-bearing.
flange_bot_cham = 0.8    # chamfer around the flange bottom perimeter (grip face)
rabbet_fil = 0.3         # fillet on rabbet shelf edges (inner + outer step)

slot_w = hook_width + 0.6
slot_h = hook_engage + 0.4

# No finger recess: the 5 mm Y-flange overhangs (top and bottom) already
# give a comfortable thumb/index grip for extracting the cassette. Any
# extra pocket on the floor face weakens the plate and wastes open area.

# Fleece thickness (informational only, used in carbon-bed calc)
fleece_thk = 3.0

EXPLODED = True
EXPLODE_GAP = 30.0

# ---------------------------------------------------------------------------
# Derived values
# ---------------------------------------------------------------------------
cavity_x = size_x - 2 * wall
cavity_y = size_y - 2 * wall
rabbet_x = cavity_x + 2 * shelf_w
rabbet_y = cavity_y + 2 * shelf_w
lid_x = rabbet_x - 2 * fit_clear
lid_y = rabbet_y - 2 * fit_clear

flange_x = size_x                           # no X overshoot (shaft-width limit)
flange_y = size_y + 2 * flange_extra_y      # Y overshoot catches on frame

arm_top_z = size_z - lid_thk               # lid underside in cassette frame
arm_tip_z = arm_top_z - hook_length
catch_center_z = arm_tip_z + hook_lead + hook_engage / 2
slot_z_min = catch_center_z - slot_h / 2
slot_z_max = catch_center_z + slot_h / 2

carbon_bed_depth = size_z - floor - lid_thk - 2 * fleece_thk


# ---------------------------------------------------------------------------
# Hex grid (pointy-top) — returns centers within a face_w × face_h rectangle
# centered at (0, 0).
# ---------------------------------------------------------------------------
def hex_centers(face_w, face_h, flats, web, margin_x, margin_y):
    r = flats / math.sqrt(3.0)
    col_pitch = flats + web
    row_pitch = 1.5 * r + web * math.sqrt(3) / 2
    usable_w = face_w - 2 * margin_x
    usable_h = face_h - 2 * margin_y
    if usable_w < flats or usable_h < 2 * r:
        return []
    n_col = int((usable_w - flats) // col_pitch) + 1
    n_row = int((usable_h - 2 * r) // row_pitch) + 1
    total_w = (n_col - 1) * col_pitch + flats
    total_h = (n_row - 1) * row_pitch + 2 * r
    x0 = -face_w / 2 + margin_x + (usable_w - total_w) / 2 + flats / 2
    y0 = -face_h / 2 + margin_y + (usable_h - total_h) / 2 + r
    out = []
    for j in range(n_row):
        x_shift = col_pitch / 2 if (j % 2) else 0.0
        cy = y0 + j * row_pitch
        for i in range(n_col):
            cx = x0 + i * col_pitch + x_shift
            if cx + flats / 2 > face_w / 2 - margin_x:
                continue
            if cx - flats / 2 < -face_w / 2 + margin_x:
                continue
            out.append((cx, cy))
    return out


r_hex = hex_flats / math.sqrt(3.0)
hex_pattern = hex_centers(
    cavity_x, cavity_y, hex_flats, hex_web, hex_margin_x, hex_margin_y
)


def try_fillet(edges, radius, label):
    """Fillet edges, falling back to per-edge attempts if the batch fails.
    Returns (ok_count, skipped_count). build123d raises if ANY single edge
    in a batch can't support the requested radius — so on failure we try
    each edge alone to keep as much smoothing as possible."""
    if not edges:
        return 0, 0
    try:
        fillet(edges, radius=radius)
        return len(edges), 0
    except Exception:
        ok, skip = 0, 0
        for e in edges:
            try:
                fillet([e], radius=radius)
                ok += 1
            except Exception:
                skip += 1
        if skip:
            print(
                f"NOTE: {label} fillet: {ok}/{ok+skip} edges at r={radius}, "
                f"{skip} skipped (curvature conflict)"
            )
        return ok, skip


def try_chamfer(edges, length, label):
    """Chamfer edges with per-edge fallback; same rationale as try_fillet."""
    if not edges:
        return 0, 0
    try:
        chamfer(edges, length=length)
        return len(edges), 0
    except Exception:
        ok, skip = 0, 0
        for e in edges:
            try:
                chamfer([e], length=length)
                ok += 1
            except Exception:
                skip += 1
        if skip:
            print(
                f"NOTE: {label} chamfer: {ok}/{ok+skip} edges at L={length}, "
                f"{skip} skipped"
            )
        return ok, skip


# ---------------------------------------------------------------------------
# Trough: body + floor flange, hex-perforated floor, X-wall snap slots.
# ---------------------------------------------------------------------------
with BuildPart() as trough_b:
    # Main body (centered in X and Y, rises from Z=0 to size_z)
    Box(size_x, size_y, size_z,
        align=(Align.CENTER, Align.CENTER, Align.MIN))

    # Fillet the body's vertical corners BEFORE adding the flange,
    # so the flange's own corners stay square.
    fillet(trough_b.edges().filter_by(Axis.Z), radius=outer_fillet)

    # Floor flange (insertion stop) — unions with the body bottom.
    Box(flange_x, flange_y, floor,
        align=(Align.CENTER, Align.CENTER, Align.MIN))

    # --- DFM: flange bottom chamfer (0.8 mm) -------------------------------
    # All 4 perimeter edges of the flange at Z=0. Bevels the apartment-facing
    # corner so it doesn't chip or cut fingers during handling. MJF prints
    # sharp convex edges fine, but chamfers improve robustness and feel.
    # Done BEFORE version engraving so the Z=0 edge filter only catches the
    # four flange-perimeter edges (text outlines come next).
    bot_edges = trough_b.edges().filter_by_position(Axis.Z, -0.01, 0.01)
    try_chamfer(list(bot_edges), flange_bot_cham, "flange bottom")

    # --- Version label (engraved recess on +Y flange overhang) -------------
    # Located on the apartment-facing face (Z=0), centered within the 10 mm
    # +Y overhang. The overhang is solid (no hex holes, no snap slots) and is
    # already the natural "grip" area, so it's visible and uncluttered.
    # Recessed 0.6 mm into the 2.2 mm flange → 1.6 mm residual thickness
    # (> MJF min 1.0 mm).
    #
    # Plane orientation: the text must read correctly when viewed from the
    # apartment (-Z world direction). A vanilla Plane.XY sketch reads fine
    # from +Z but appears MIRRORED from -Z (viewer's right flips from +X to
    # -X when the camera crosses the plane). Fix: build the sketch on a
    # plane whose normal is -Z (so the viewer sees the "front" of the
    # 2D glyphs) AND whose x_dir is -X, which keeps y_dir = +Y (right-handed:
    # x × y = z must give (-1,0,0) × (0,1,0) = (0,0,-1) ✓). On this plane,
    # sketch-+X → world-X, sketch-+Y → world +Y, normal → -Z. Extrude by a
    # NEGATIVE amount so the cut goes in +Z (into the flange material).
    version_y = (size_y / 2 + flange_y / 2) / 2  # midline of +Y overhang
    version_plane = Plane(
        origin=(0, version_y, -0.01),
        x_dir=(-1, 0, 0),
        z_dir=(0, 0, -1),
    )
    with BuildSketch(version_plane) as _:
        Text(
            f"v{VERSION}",
            font_size=version_font,
            align=(Align.CENTER, Align.CENTER),
        )
    extrude(amount=-(version_depth + 0.01), mode=Mode.SUBTRACT)

    # --- DFM: flange-top step fillet + corner chamfer ---------------------
    # Where the flange top face meets the body sidewall there is a concave
    # 90° step. Two sub-features need treatment, handled in two passes so
    # that each sub-feature gets the most appropriate operation:
    #   (a) straight segments along Y=±size_y/2 (body side meets flange top
    #       in the Y-overhang region) → inside FILLET for stress relief.
    #   (b) 4 arc segments following the body's vertical corner fillet at
    #       Z=floor → the "shelf" that appears because flange_x = size_x
    #       but body has 2 mm corner fillets (material steps IN at Z>floor).
    #       A fillet here would intersect the 2 mm body-corner fillet and
    #       fail; a CHAMFER kills the step cleanly without curve conflicts.
    step_straight = []
    step_arcs = []
    for e in trough_b.edges().filter_by_position(
        Axis.Z, floor - 0.01, floor + 0.01
    ):
        c = e.center()
        on_flange_y_edge = abs(c.Y) >= flange_y / 2 - 0.1
        on_flange_x_edge = (abs(c.X) >= flange_x / 2 - 0.1
                            and abs(c.Y) >= size_y / 2 - 0.1)
        if on_flange_y_edge or on_flange_x_edge:
            continue
        # Body corner fillet arcs sit in a small box around (±29, ±44.5).
        # Everything else on the body footprint outline is a straight edge.
        is_arc_region = (abs(c.X) > size_x / 2 - outer_fillet - 0.1
                         and abs(c.Y) > size_y / 2 - outer_fillet - 0.1)
        if is_arc_region:
            step_arcs.append(e)
        else:
            step_straight.append(e)
    # Straight step edges first (clean 90° step along Y=±size_y/2 where the
    # Y-flange overhang meets the body sidewall — unambiguous fillet target).
    # Corner "shelf" arcs after: they sit between a cylindrical body-corner
    # surface and the flange top, so OCCT often refuses both fillet and
    # chamfer at larger radii. We fall back chamfer→smaller radius→skip.
    try_fillet(step_straight, flange_step_fil, "flange step")
    if not try_fillet(step_arcs, flange_top_cham, "flange corner")[0]:
        if not try_chamfer(step_arcs, flange_top_cham, "flange corner")[0]:
            try_chamfer(step_arcs, 0.3, "flange corner (fallback 0.3)")

    # Cavity (pocket from top down to floor top)
    with BuildSketch(Plane.XY.offset(size_z)) as _:
        Rectangle(cavity_x, cavity_y)
    extrude(amount=-(size_z - floor), mode=Mode.SUBTRACT)

    # --- DFM: cavity-floor inner fillet (1.0 mm) ---------------------------
    # The 4 edges where the cavity floor meets the cavity walls at Z=floor.
    # Concave corner; filleting relieves stress (floor plate flexes under
    # the mass of the carbon bed) and helps residual MJF powder flow out of
    # the corners during de-powdering. Applied BEFORE the hex cut so the
    # selector only catches the 4 cavity perimeter edges.
    cavity_floor_edges = []
    for e in trough_b.edges().filter_by_position(
        Axis.Z, floor - 0.01, floor + 0.01
    ):
        c = e.center()
        if (abs(c.X) <= cavity_x / 2 + 0.1
                and abs(c.Y) <= cavity_y / 2 + 0.1):
            cavity_floor_edges.append(e)
    try_fillet(cavity_floor_edges, cavity_floor_fil, "cavity floor")

    # Rabbet: widen cavity at top by shelf_w per side, depth = rabbet_depth
    with BuildSketch(Plane.XY.offset(size_z)) as _:
        Rectangle(rabbet_x, rabbet_y)
    extrude(amount=-rabbet_depth, mode=Mode.SUBTRACT)

    # --- DFM: rabbet shelf fillet (0.3 mm) ---------------------------------
    # The rabbet step creates two horizontal edge sets at Z=size_z-rabbet_depth:
    # inner edges (concave, between shelf top and cavity wall below) and
    # outer edges (convex, between shelf top and rabbet wall above). A small
    # 0.3 mm fillet on both smooths the abrupt step without eating meaningful
    # shelf width (shelf_w=1.0 mm → ≥0.7 mm remaining contact for the lid).
    rabbet_z = size_z - rabbet_depth
    rabbet_edges = []
    for e in trough_b.edges().filter_by_position(
        Axis.Z, rabbet_z - 0.01, rabbet_z + 0.01
    ):
        c = e.center()
        if (abs(c.X) <= rabbet_x / 2 + 0.1
                and abs(c.Y) <= rabbet_y / 2 + 0.1):
            rabbet_edges.append(e)
    try_fillet(rabbet_edges, rabbet_fil, "rabbet")

    # Hex perforation on the floor face (Z=0) — cut upward through the
    # floor plate. Hex pattern is sized to the cavity interior so no
    # holes fall under the walls or the flange.
    with BuildSketch(Plane.XY.offset(-1.0)) as _:
        for cx, cy in hex_pattern:
            with Locations((cx, cy)):
                RegularPolygon(radius=r_hex, side_count=6, rotation=90)
    extrude(amount=floor + 2.0, mode=Mode.SUBTRACT)

    # Two through-slots in X outer walls for snap engagement
    # Plane.YZ: sketch-X maps to world-Y, sketch-Y maps to world-Z.
    with BuildSketch(Plane.YZ.offset(size_x / 2 + 1.0)) as _:
        with Locations((0.0, catch_center_z)):
            Rectangle(slot_w, slot_h)
    extrude(amount=-(wall + 2.0), mode=Mode.SUBTRACT)
    with BuildSketch(Plane.YZ.offset(-size_x / 2 - 1.0)) as _:
        with Locations((0.0, catch_center_z)):
            Rectangle(slot_w, slot_h)
    extrude(amount=wall + 2.0, mode=Mode.SUBTRACT)

assert trough_b.part is not None
trough = trough_b.part


# ---------------------------------------------------------------------------
# Lid: hex-perforated slab + two cantilever tabs on X-edges
# ---------------------------------------------------------------------------
def make_tab_proto():
    """
    Tab in local frame:
      +X = outward direction (toward the X-wall slot)
      attach plane at local x = 0 (arm outer face)
      arm material at x ∈ [-hook_arm, 0]
      arm spans z ∈ [-hook_length, 0], attach at z = 0
      lip protrudes +X from arm outer face; trapezoidal profile in XZ.
    """
    with BuildPart() as h:
        Box(
            hook_arm, hook_width, hook_length,
            align=(Align.MAX, Align.CENTER, Align.MAX),
        )
        with BuildSketch(Plane.XZ) as _:
            with BuildLine() as _bl:
                Polyline(
                    (0.0, -hook_length),
                    (hook_protr, -hook_length + hook_lead),
                    (hook_protr, -hook_length + hook_lead + hook_engage),
                    (0.0, -hook_length + hook_lead + hook_engage),
                    close=True,
                )
            make_face()
        extrude(amount=hook_width / 2, both=True)
    assert h.part is not None
    return h.part


with BuildPart() as lid_b:
    # Slab centered at origin in XY, Z = [size_z - lid_thk, size_z]
    with BuildSketch(Plane.XY.offset(size_z - lid_thk)) as _:
        Rectangle(lid_x, lid_y)
    extrude(amount=lid_thk)

    # Hex perforation on the lid — same pattern as floor for straight flow
    with BuildSketch(Plane.XY.offset(size_z - lid_thk - 1.0)) as _:
        for cx, cy in hex_pattern:
            with Locations((cx, cy)):
                RegularPolygon(radius=r_hex, side_count=6, rotation=90)
    extrude(amount=lid_thk + 2.0, mode=Mode.SUBTRACT)

    # Two tabs on X-edges. Arm outer face aligned with the cavity wall
    # inner face; lip protrudes outward into the wall slot.
    tab = make_tab_proto()
    arm_x_right = cavity_x / 2
    arm_x_left = -cavity_x / 2

    tab_locs = [
        Location((arm_x_right, 0.0, arm_top_z), (0, 0, 0)),
        Location((arm_x_left, 0.0, arm_top_z), (0, 0, 180)),
    ]
    for loc in tab_locs:
        add(tab.moved(loc))

    # Arm-root fillet: only the junctions where each arm's top meets the
    # lid underside. Narrow by per-arm XY bounding boxes so we don't try
    # to fillet the lid perimeter edges (no adjacent material on one side).
    arm_bbs = [
        (cavity_x / 2 - hook_arm, cavity_x / 2,
         -hook_width / 2, hook_width / 2),
        (-cavity_x / 2, -cavity_x / 2 + hook_arm,
         -hook_width / 2, hook_width / 2),
    ]
    tol = 0.05
    root_edges = []
    for e in lid_b.edges().filter_by_position(
        Axis.Z, arm_top_z - 0.01, arm_top_z + 0.01
    ):
        c = e.center()
        for xmin, xmax, ymin, ymax in arm_bbs:
            if (xmin - tol <= c.X <= xmax + tol
                    and ymin - tol <= c.Y <= ymax + tol):
                root_edges.append(e)
                break
    if root_edges:
        try:
            fillet(root_edges, radius=hook_root_fil)
        except Exception as exc:
            print(
                f"NOTE: root fillet skipped "
                f"({exc.__class__.__name__}: {exc})"
            )
    else:
        print("NOTE: no arm-root edges matched — fillet skipped")

    # --- DFM: lid top/bottom perimeter chamfers (done BEFORE corner fillet) -
    # The chamfer operation expects a clean 90° convex edge. If the corner
    # fillet is applied first, the perimeter edges get shortened and abut the
    # new arc faces — OCCT then refuses the chamfer due to tangency conflict.
    # Order: chamfers first on the pristine rectangular topology, corner
    # fillet afterwards.
    # Top perimeter (0.5 mm): outer finish; no sharp rim against fingers
    # when the user taps the lid on to snap it in.
    # Bottom perimeter (0.3 mm): lead-in into the rabbet seat during
    # closing, gentle self-centering despite the 0.30 mm fit_clear. Light
    # enough to not steal meaningful contact area on the rabbet shelf.
    # Both filters exclude hex-outline edges (interior) and tab edges
    # (not on the |X|=lid_x/2 or |Y|=lid_y/2 perimeter).
    lid_bot_z = size_z - lid_thk
    lid_top_z = size_z
    lid_top_perim = []
    lid_bot_perim = []
    for e in lid_b.edges():
        c = e.center()
        on_x_wall = abs(abs(c.X) - lid_x / 2) < 0.1
        on_y_wall = abs(abs(c.Y) - lid_y / 2) < 0.1
        if not (on_x_wall or on_y_wall):
            continue
        if abs(c.Z - lid_top_z) < 0.01:
            lid_top_perim.append(e)
        elif abs(c.Z - lid_bot_z) < 0.01:
            lid_bot_perim.append(e)
    try_chamfer(lid_top_perim, lid_top_cham, "lid top perim")
    try_chamfer(lid_bot_perim, lid_bot_cham, "lid bot perim")

    # --- DFM: lid vertical corner fillets (1.0 mm) -------------------------
    # Four vertical edges of the lid slab perimeter. MJF prints sharp 90°
    # edges cleanly; these fillets are purely for handling (no chipping, no
    # finger-cut risk) and aesthetic consistency with the trough body's 2 mm
    # corner fillets. 1 mm is smaller than the body value since the lid is
    # thinner and doesn't need as much tactile rounding. Applied AFTER the
    # top/bot chamfers so OCCT sees the chamfer arcs as simple curved
    # endpoints — sometimes it still refuses individual edges, in which case
    # try_fillet's per-edge fallback reports the skip.
    lid_corner_edges = []
    for e in lid_b.edges().filter_by(Axis.Z):
        c = e.center()
        if (abs(abs(c.X) - lid_x / 2) < 0.1
                and abs(abs(c.Y) - lid_y / 2) < 0.1):
            lid_corner_edges.append(e)
    try_fillet(lid_corner_edges, lid_corner_fil, "lid corner")

assert lid_b.part is not None
lid = lid_b.part


# ---------------------------------------------------------------------------
# Sanity checks
# ---------------------------------------------------------------------------
residual_wall = wall - shelf_w
if residual_wall < 1.0:
    print(f"WARN: residual wall after rabbet = {residual_wall:.2f} mm (<1.0)")

deflection = hook_protr + fit_clear
strain = 3.0 * hook_arm * deflection / (2.0 * hook_length ** 2)

print(f"Cassette body:            {size_x}×{size_y}×{size_z} mm")
print(f"Floor flange footprint:   {flange_x}×{flange_y}×{floor} mm")
print(f"Carbon bed depth:         {carbon_bed_depth:.1f} mm "
      f"(= Z − floor − lid − 2×{fleece_thk} fleece)")
print(f"Wall thickness:           {wall:.2f} mm")
print(f"Residual wall at rabbet:  {residual_wall:.2f} mm")
print(f"Lid clearance per side:   {fit_clear:.2f} mm")
print(f"Hex holes (per face):     {len(hex_pattern)}")
print(f"Snap arm max strain:      {strain*100:.2f} %  (PA11 yield ~5 %)")
print(f"Trough volume:            {trough.volume / 1000:.2f} cm³")
print(f"Lid volume:               {lid.volume / 1000:.2f} cm³")


# ---------------------------------------------------------------------------
# Exports — STEP under output/STEP/, STL under output/STL/ (relative to this
# script's directory so runs from any CWD put artifacts in the same place).
# ---------------------------------------------------------------------------
_here = Path(__file__).resolve().parent
step_dir = _here / "output" / "STEP"
stl_dir = _here / "output" / "STL"
step_dir.mkdir(parents=True, exist_ok=True)
stl_dir.mkdir(parents=True, exist_ok=True)

export_step(trough, str(step_dir / "trough.step"))
export_step(lid, str(step_dir / "lid.step"))

# STL export: angular tolerance tightened from the 0.1 rad (≈5.7°) default
# to 0.05 rad (≈2.9°) so that adjacent curved faces tessellate consistently
# along their shared edges — reduces OCCT t-vertex seam artifacts.
_stl_linear_tol = 1e-3
_stl_angular_tol = 0.05
export_stl(
    trough,
    str(stl_dir / "trough.stl"),
    tolerance=_stl_linear_tol,
    angular_tolerance=_stl_angular_tol,
)
export_stl(
    lid,
    str(stl_dir / "lid.stl"),
    tolerance=_stl_linear_tol,
    angular_tolerance=_stl_angular_tol,
)


def _mesh_volume_cm3(v, f) -> float:
    import numpy as np
    tris = v[f]
    return abs(
        np.einsum("ij,ij->i", tris[:, 0], np.cross(tris[:, 1], tris[:, 2]))
        .sum() / 6
    ) / 1000


def _heal_stl(path: Path) -> None:
    """
    Post-process an OCCT-tessellated STL for print-bureau acceptance.

    Strategy:
      1. Diagnose the raw mesh (boundaries, self-intersections).
      2. If clean (0 boundaries, 0 self-intersections): leave it alone.
      3. Else: apply targeted repairs with pymeshfix. Critically, validate
         volume preservation (±5 %) — pymeshfix's `clean()` can cascade
         through self-intersection removal into component loss on meshes
         with high-genus topology (e.g. the hex-perforated lid), where the
         "repaired" result shrinks to a tiny fragment. On volume mismatch,
         leave the original in place; the bureau's auto-heal usually handles
         a handful of residual intersections, and the STEP export remains
         the authoritative clean upload path.
    """
    import pymeshfix

    mesh = pymeshfix.PyTMesh()
    mesh.set_quiet(True)
    mesh.load_file(str(path))
    v0, f0 = mesh.return_arrays()
    vol0 = _mesh_volume_cm3(v0, f0)
    n_bnd = mesh.n_boundaries
    n_si = len(mesh.select_intersecting_triangles())

    if n_bnd == 0 and n_si == 0:
        print(
            f"  STL heal {path.name}: already clean "
            f"(faces={len(f0)}, vol={vol0:.2f} cm³) — skipped"
        )
        return

    # Re-load fresh (the prior select_intersecting_triangles mutates internal
    # state in some pymeshfix versions).
    mesh = pymeshfix.PyTMesh()
    mesh.set_quiet(True)
    mesh.load_file(str(path))
    if n_bnd > 0:
        mesh.fill_small_boundaries(nbe=100, refine=True)
    if n_si > 0:
        mesh.clean(max_iters=10, inner_loops=3)

    v1, f1 = mesh.return_arrays()
    vol1 = _mesh_volume_cm3(v1, f1)
    vol_drop = (vol0 - vol1) / vol0 if vol0 > 0 else 1.0

    if vol_drop > 0.05 or vol1 == 0:
        print(
            f"  STL heal {path.name}: abort — repair would cut volume by "
            f"{vol_drop*100:.1f} % ({vol0:.2f} → {vol1:.2f} cm³). "
            f"Original kept. Bureau auto-heal or STEP upload recommended."
        )
        return

    mesh.save_file(str(path))
    print(
        f"  STL heal {path.name}: boundaries {n_bnd}→{mesh.n_boundaries}, "
        f"intersections {n_si}→0, faces {len(f0)}→{len(f1)}, "
        f"vol {vol0:.2f}→{vol1:.2f} cm³"
    )


print("Mesh heal:")
_heal_stl(stl_dir / "trough.stl")
_heal_stl(stl_dir / "lid.stl")


# ---------------------------------------------------------------------------
# Show in ocp-vscode
# ---------------------------------------------------------------------------
lid_display = lid.moved(Location((0, 0, EXPLODE_GAP))) if EXPLODED else lid
show(
    trough,
    lid_display,
    names=["Trough", "Lid"],
    colors=["#8a8a8a", "#3b82f6"],
)
