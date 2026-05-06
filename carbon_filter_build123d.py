"""
Activated-carbon filter cassette — build123d, MJF-optimized.
Target: HP Multi Jet Fusion, PA12 (HP 3D HR PA 12 enabled by Evonik or
equivalent).

Design intent
-------------
Vertical-airflow cassette in its own frame (Z up while filling):
    Floor (Z=0): hex-perforated, fused to the trough body.
    Lid   (Z=size_z): hex-perforated, removable, hook-and-snap from above.
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
`floor` mm thick. Because its Y span (size_y + 2·flange_extra_y = 113 mm) is
wider than the shaft hard height (100 mm), it catches on the shaft front
frame at the top and bottom while passing cleanly through in X. The cassette
protrudes `floor` mm (= 2.2 mm) from the opening — enough for finger access,
well within the user-accepted 5 mm limit.

Lid retention: one simple hook rail on one X-side of the lid engages a shallow
receiving pocket in the opposite trough wall; two cantilever tabs on the
other X-side engage through-slots in the matching X-wall. The tabs have a
release ramp, so the lid can be lifted open from a single center notch without
separately pinching both snaps. The passive side is a modest form-fit, not a
deep hidden mechanism: enough to define the opening side, simple enough for
MJF and easy inspection.
Y-walls (against hard shaft top/bottom) stay completely
flush —
Moosgummi strips on top and bottom of the cassette body provide the axial seal.

Viewer:
    ./run setup
    Launch "OCP CAD Viewer" in VSCode, then:
        ./run cad
Save the file to live-reload the viewer. Exports STEP + STL alongside.
"""

# SPDX-License-Identifier: CERN-OHL-S-2.0 OR AGPL-3.0-or-later

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
VERSION = "1.1.6"
version_font = 5.0       # mm — fits the 10 mm Y-overhang comfortably
version_depth = 0.6      # mm — recessed engraving; MJF prints this crisp
                         # without weakening the 2.2 mm flange floor

# ---------------------------------------------------------------------------
# Parameters (mm) — MJF-tuned, cassette's own frame (Z up during filling)
# ---------------------------------------------------------------------------
# Outer envelope of cassette body
size_x = 65.0       # shaft width direction (foam contact both sides)
size_y = 95.0       # shaft vertical direction (hard walls top/bottom)
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
hex_margin_x = 2.8
hex_margin_y = 4.0

# Lid retention:
#   * one simple hook rail on the -X side (engages a shallow side pocket)
#   * two snap tabs on the +X side (engage through-slots in the +X wall)
# This revision is tuned for PA12 MJF and for geometric simplicity:
#   * passive side = one simple hook rail with a short sloped nose
#   * active side = one long cantilever with a simple asymmetric snap nose
# The passive side only needs to guide and hold the first opening moment;
# the active side supplies the real retention and the self-release behavior.
retainer_y_offset = 18.0
hook_rail_width = 34.0
hook_rail_drop = 3.0
hook_rail_depth = 2.1
hook_rail_capture = 1.1
hook_nose_outboard = 0.35
hook_rail_nose_height = 0.9
hook_tip_cham = 0.2
hook_slot_w = hook_rail_width + 0.6
hook_slot_depth = 1.35
hook_slot_lead_depth = 0.55
hook_slot_floor_clearance = 0.4
hook_slot_roof_clearance = 0.35

hook_width = 6.0
hook_arm = 1.0
hook_length = 10.2
hook_protr = 1.1
hook_lead = 1.5
hook_hold = 0.4
hook_release = 2.8
hook_root_fil = 0.5

# Opening aid on the snap side (+X): a shallow body notch exposes a small lid
# lip so the user can lift the lid with one finger. The lip stays within the
# cassette body envelope, so shaft insertion remains unaffected.
grip_lip_width = 16.0
grip_lip_extend = 1.2
grip_lip_cham = 0.4
grip_notch_width = 18.0
grip_notch_height = 5.0
grip_notch_plane_offset = 1.0
grip_notch_min_wall = 1.0
grip_notch_cut = wall + grip_notch_plane_offset - grip_notch_min_wall

# The earlier triangular passive-corner reliefs solved an insertion collision
# but left a visible diagonal witness line on production parts. The stronger
# two-depth receiver ledge now keeps hook-first assembly viable without that
# cosmetic corner cut.
passive_corner_relief_x = 0.0
passive_corner_relief_y = 0.0

# Internal anti-spread ties: permanent crossbars inside the trough envelope.
# FEM showed the free upper rim is the weak mode; these bars tie the two long
# X walls together near the top without adding anything outside the 65 mm fit.
# They sit below the passive hook rail and away from the two snap-arm lanes.
anti_bulge_tie_width_y = 2.2
anti_bulge_tie_height_z = 1.4
anti_bulge_tie_lid_gap = 4.0
anti_bulge_tie_y_offsets = (-36.0, 0.0, 36.0)

# DFM (Design-for-Manufacturability) radii applied after the main solid
# operations. See README "MJF-Optimierungen" for reasoning per edge.
cavity_floor_fil = 1.0   # inside fillet where cavity floor meets cavity walls
flange_step_fil = 1.0    # inside fillet where flange top meets body sidewall
lid_corner_fil = 1.0     # vertical corner fillet of the lid slab (handling)
lid_top_cham = 0.5       # chamfer on lid top outer edges (finish + no chipping)
lid_bot_cham = 0.2       # chamfer on lid bottom outer edges (rabbet lead-in).
                         # 0.3 mm conflicts via OCCT with the 0.5 mm snap-arm
                         # root fillet on the X-side (tab attach at X≈30.3 is
                         # 0.7 mm from the X-perim edge at 31.0); 0.2 mm clears.
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
slot_h = hook_hold + 0.4
retainer_y_offsets = (-retainer_y_offset, retainer_y_offset)

# No finger recess: the 10 mm Y-flange overhangs (top and bottom) already
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
catch_center_z = arm_tip_z + hook_lead + hook_hold / 2
hook_nose_bottom_z = arm_top_z - hook_rail_drop
hook_nose_top_z = hook_nose_bottom_z + hook_rail_nose_height
hook_slot_bottom_z = hook_nose_bottom_z - hook_slot_floor_clearance
hook_slot_roof_z = hook_nose_top_z + hook_slot_roof_clearance
hook_slot_full_h = hook_slot_roof_z - hook_slot_bottom_z
hook_slot_full_center_z = (hook_slot_roof_z + hook_slot_bottom_z) / 2
hook_slot_lead_h = arm_top_z - hook_slot_roof_z
hook_slot_lead_center_z = (arm_top_z + hook_slot_roof_z) / 2
hook_receiver_ledge_depth = hook_slot_depth - hook_slot_lead_depth
slot_z_min = catch_center_z - slot_h / 2
slot_z_max = catch_center_z + slot_h / 2
anti_bulge_tie_top_z = arm_top_z - anti_bulge_tie_lid_gap
anti_bulge_tie_z0 = anti_bulge_tie_top_z - anti_bulge_tie_height_z

carbon_bed_depth = size_z - floor - lid_thk - 2 * fleece_thk
effective_hook_capture = lid_x / 2 + hook_nose_outboard - cavity_x / 2
hook_pocket_outer_clearance = hook_slot_depth - effective_hook_capture


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
# Trough: body + floor flange, hex-perforated floor, hook pocket, snap wall.
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

    # Permanent internal anti-spread ties. Each bar is fused into both long
    # X walls, so wall spread puts the bar in tension instead of relying on
    # contact/friction. They are low enough to clear the passive hook rail.
    for y in anti_bulge_tie_y_offsets:
        with Locations((0.0, y, anti_bulge_tie_z0)):
            Box(
                cavity_x,
                anti_bulge_tie_width_y,
                anti_bulge_tie_height_z,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

    # Hex perforation on the floor face (Z=0) — cut upward through the
    # floor plate. Hex pattern is sized to the cavity interior so no
    # holes fall under the walls or the flange.
    with BuildSketch(Plane.XY.offset(-1.0)) as _:
        for cx, cy in hex_pattern:
            with Locations((cx, cy)):
                RegularPolygon(radius=r_hex, side_count=6, rotation=90)
    extrude(amount=floor + 2.0, mode=Mode.SUBTRACT)

    # Passive hook receiver in the -X cavity wall. The lower cut is the real
    # retaining pocket; the shallower upper cut is only a lead-in channel.
    # Keeping the upper cut shallow leaves a material ledge above the lower
    # pocket, so the hook nose has something visible and deliberate to bear
    # under instead of relying on a nearly open vertical slot.
    with BuildSketch(Plane.YZ.offset(-cavity_x / 2)) as _:
        with Locations((0.0, hook_slot_full_center_z)):
            Rectangle(hook_slot_w, hook_slot_full_h)
    extrude(amount=-hook_slot_depth, mode=Mode.SUBTRACT)
    with BuildSketch(Plane.YZ.offset(-cavity_x / 2)) as _:
        with Locations((0.0, hook_slot_lead_center_z)):
            Rectangle(hook_slot_w, hook_slot_lead_h)
    extrude(amount=-hook_slot_lead_depth, mode=Mode.SUBTRACT)

    # Release notch on the +X snap side: removes only the local outer-wall
    # material above the rabbet so the lid lip is reachable by fingertip.
    with BuildSketch(Plane.YZ.offset(size_x / 2 + grip_notch_plane_offset)) as _:
        with Locations((0.0, size_z - grip_notch_height / 2)):
            Rectangle(grip_notch_width, grip_notch_height)
    extrude(amount=-grip_notch_cut, mode=Mode.SUBTRACT)

    # Two through-slots in the +X outer wall for snap engagement.
    # Plane.YZ: sketch-X maps to world-Y, sketch-Y maps to world-Z.
    with BuildSketch(Plane.YZ.offset(size_x / 2 + 1.0)) as _:
        for y in retainer_y_offsets:
            with Locations((y, catch_center_z)):
                Rectangle(slot_w, slot_h)
    extrude(amount=-(wall + 2.0), mode=Mode.SUBTRACT)

assert trough_b.part is not None
trough = trough_b.part


# ---------------------------------------------------------------------------
# Lid: hex-perforated slab + -X hook rail + +X snap tabs + pull lip
# ---------------------------------------------------------------------------
def make_hook_rail_proto():
    """Simple passive hook rail in local frame.

    Local x = inward from the lid edge, local z = downward into the trough.
    The upper stem is intentionally inset, while the lower nose reaches the lid
    edge with one simple sloped hook. This gives a modest passive capture
    without the visually busier stepped foot used before.
    """
    with BuildPart() as a:
        with BuildSketch(Plane.XZ) as _:
            with BuildLine() as _bl:
                Polyline(
                    (hook_rail_capture, 0.0),
                    (hook_rail_depth, 0.0),
                    (hook_rail_depth, -hook_rail_drop),
                    (-hook_nose_outboard + hook_tip_cham, -hook_rail_drop),
                    (-hook_nose_outboard, -hook_rail_drop + hook_tip_cham),
                    (hook_rail_capture, -hook_rail_drop + hook_rail_nose_height),
                    close=True,
                )
            make_face()
        extrude(amount=hook_rail_width / 2, both=True)
    assert a.part is not None
    return a.part


def make_tab_proto():
    """
    Tab in local frame:
      +X = outward direction (toward the X-wall slot)
      attach plane at local x = 0 (arm outer face)
      arm material at x ∈ [-hook_arm, 0]
      arm spans z ∈ [-hook_length, 0], attach at z = 0
      lip protrudes +X from arm outer face; a simple asymmetric nose with
      lower closing ramp, very short hold flat, and a long release ramp for
      one-finger lift-off.
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
                    (hook_protr, -hook_length + hook_lead + hook_hold),
                    (0.0, -hook_length + hook_lead + hook_hold + hook_release),
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

    # Small pull lip on the +X snap side. It sits inside the body envelope
    # and is only exposed where the trough's release notch clears the wall.
    with BuildSketch(Plane.XY.offset(size_z - lid_thk)) as _:
        with Locations((lid_x / 2 + grip_lip_extend / 2, 0.0)):
            Rectangle(grip_lip_extend, grip_lip_width)
    extrude(amount=lid_thk)

    if passive_corner_relief_x > 0.0 and passive_corner_relief_y > 0.0:
        # Optional plan-view corner reliefs on the passive hook side.
        with BuildSketch(Plane.XY.offset(size_z - lid_thk)) as _:
            with BuildLine() as _bl:
                Polyline(
                    (-lid_x / 2, -lid_y / 2),
                    (-lid_x / 2 + passive_corner_relief_x, -lid_y / 2),
                    (-lid_x / 2, -lid_y / 2 + passive_corner_relief_y),
                    close=True,
                )
                Polyline(
                    (-lid_x / 2, lid_y / 2),
                    (-lid_x / 2 + passive_corner_relief_x, lid_y / 2),
                    (-lid_x / 2, lid_y / 2 - passive_corner_relief_y),
                    close=True,
                )
            make_face()
        extrude(amount=lid_thk, mode=Mode.SUBTRACT)

    # Hex perforation on the lid — same pattern as floor for straight flow
    with BuildSketch(Plane.XY.offset(size_z - lid_thk - 1.0)) as _:
        for cx, cy in hex_pattern:
            with Locations((cx, cy)):
                RegularPolygon(radius=r_hex, side_count=6, rotation=90)
    extrude(amount=lid_thk + 2.0, mode=Mode.SUBTRACT)

    # Passive hook rail on -X plus two snap tabs on +X. The +X arm outer face
    # aligns with the cavity wall inner face; the lip protrudes outward into
    # the +X wall slot.
    hook_rail = make_hook_rail_proto()
    tab = make_tab_proto()
    add(hook_rail.moved(Location((-lid_x / 2, 0.0, arm_top_z), (0, 0, 0))))

    tab_locs = [
        Location((cavity_x / 2, y, arm_top_z), (0, 0, 0))
        for y in retainer_y_offsets
    ]
    for loc in tab_locs:
        add(tab.moved(loc))

    # Arm-root fillet: only the junctions where each arm's top meets the
    # lid underside. Narrow by per-arm XY bounding boxes so we don't try
    # to fillet the lid perimeter edges (no adjacent material on one side).
    arm_bbs = [
        (cavity_x / 2 - hook_arm, cavity_x / 2,
         y - hook_width / 2, y + hook_width / 2)
        for y in retainer_y_offsets
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

    # Dedicated chamfer on the pull lip so the fingertip contact edge isn't
    # a sharp 90° ridge. Kept smaller than the general lid perimeter chamfer
    # because the lip only extends 1.2 mm in X.
    grip_lip_top = []
    grip_lip_bot = []
    for e in lid_b.edges():
        c = e.center()
        on_grip_face = (abs(c.X - (lid_x / 2 + grip_lip_extend)) < 0.1
                        and abs(c.Y) <= grip_lip_width / 2 + 0.1)
        if not on_grip_face:
            continue
        if abs(c.Z - lid_top_z) < 0.01:
            grip_lip_top.append(e)
        elif abs(c.Z - lid_bot_z) < 0.01:
            grip_lip_bot.append(e)
    try_chamfer(grip_lip_top, grip_lip_cham, "grip lip top")
    try_chamfer(grip_lip_bot, grip_lip_cham, "grip lip bot")

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
# HP 3D HR PA12 enabled by Evonik datasheet ranges:
#   * JF 5200: tensile modulus ≈ 1650…2200 MPa
#   * JF 5600: tensile modulus ≈ 2000…2300 MPa, elongation at yield ≈ 9…11 %
# Use a conservative PA12 nominal value for the center estimate and print the
# broader force band as an informational range.
snap_modulus = 2150.0
snap_modulus_lo = 1650.0
snap_modulus_hi = 2200.0
pa12_yield_lo = 0.09
pa12_yield_hi = 0.11
arm_inertia = hook_width * hook_arm ** 3 / 12.0
snap_spring_k = 3.0 * snap_modulus * arm_inertia / (hook_length ** 3)
snap_spring_k_lo = 3.0 * snap_modulus_lo * arm_inertia / (hook_length ** 3)
snap_spring_k_hi = 3.0 * snap_modulus_hi * arm_inertia / (hook_length ** 3)
snap_force = snap_spring_k * deflection
snap_force_lo = snap_spring_k_lo * deflection
snap_force_hi = snap_spring_k_hi * deflection
release_run_ratio = hook_protr / hook_release
release_mu = 0.20
lift_factor = ((release_run_ratio + release_mu)
               / (1.0 - release_mu * release_run_ratio))
lift_force = snap_spring_k * hook_protr * lift_factor
lift_force_lo = snap_spring_k_lo * hook_protr * lift_factor
lift_force_hi = snap_spring_k_hi * hook_protr * lift_factor
hook_capture = effective_hook_capture
allowable_strain_lo = pa12_yield_lo / 3.0
allowable_strain_hi = pa12_yield_hi / 3.0

print(f"Cassette body:            {size_x}×{size_y}×{size_z} mm")
print(f"Floor flange footprint:   {flange_x}×{flange_y}×{floor} mm")
print(f"Carbon bed depth:         {carbon_bed_depth:.1f} mm "
      f"(= Z − floor − lid − 2×{fleece_thk} fleece)")
print(f"Wall thickness:           {wall:.2f} mm")
print(f"Residual wall at rabbet:  {residual_wall:.2f} mm")
print(f"Anti-spread ties:         {len(anti_bulge_tie_y_offsets)} bars, "
      f"{anti_bulge_tie_width_y:.1f}×{anti_bulge_tie_height_z:.1f} mm "
      f"at Z={anti_bulge_tie_z0:.1f}…{anti_bulge_tie_top_z:.1f}")
print(f"Tie-to-lid fleece gap:    {arm_top_z - anti_bulge_tie_top_z:.1f} mm "
      f"(for {fleece_thk:.1f} mm top fleece)")
print(f"Lid clearance per side:   {fit_clear:.2f} mm")
print(f"Hex holes (per face):     {len(hex_pattern)}")
print(f"Snap arm max strain:      {strain*100:.2f} %")
print(f"PA12 strain proxy target: <{allowable_strain_lo*100:.2f} … "
      f"{allowable_strain_hi*100:.2f} % "
      f"(= 1/3 of 9 … 11 % yield)")
print(f"Hook capture at passive side: ~{hook_capture:.2f} mm")
print(f"Hook pocket outer clearance:  ~{hook_pocket_outer_clearance:.2f} mm")
print(f"Hook receiver ledge depth:    ~{hook_receiver_ledge_depth:.2f} mm")
print(f"Snap force per tab:       ~{snap_force:.2f} N lateral "
      f"({snap_force_lo:.2f} … {snap_force_hi:.2f} N over PA12 modulus range)")
print(f"Lift-open force total:    ~{2*lift_force:.2f} N "
      f"({2*lift_force_lo:.2f} … {2*lift_force_hi:.2f} N, "
      f"2 tabs incl. mu={release_mu:.2f})")
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

# STL export: use a 1° angular tolerance per HP's general MJF tessellation
# recommendation and a fine linear tolerance so curved faces share vertices
# more consistently. STEP remains the authoritative upload format.
_stl_linear_tol = 1e-3
_stl_angular_tol = math.radians(1.0)
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


def _remesh_stl_from_step(
    step_path: Path,
    stl_path: Path,
    ref_volume_cm3: float,
    mesh_size_min: float = 0.2,
    mesh_size_max: float = 0.8,
) -> None:
    """Re-mesh a STEP BRep with Gmsh and replace the STL if validation passes.

    OCCT's direct STL tessellation can leave tiny open seams at tangent
    transitions. Gmsh meshes the STEP topology as a joined
    surface model, which gives pymeshfix a much cleaner starting point.
    """
    try:
        import gmsh
        import trimesh
    except ModuleNotFoundError as exc:
        print(f"  STEP remesh {stl_path.name}: skipped ({exc.name} not installed)")
        return

    import shutil
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        candidate = Path(tmp) / stl_path.name
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.open(str(step_path))
            gmsh.option.setNumber("Mesh.MeshSizeMin", mesh_size_min)
            gmsh.option.setNumber("Mesh.MeshSizeMax", mesh_size_max)
            gmsh.option.setNumber("Mesh.StlOneSolidPerSurface", 0)
            gmsh.model.mesh.generate(2)
            gmsh.write(str(candidate))
        finally:
            gmsh.finalize()

        mesh = trimesh.load_mesh(candidate, force="mesh")
        vol = abs(mesh.volume) / 1000
        vol_delta = abs(vol - ref_volume_cm3) / ref_volume_cm3
        if not mesh.is_watertight or not mesh.is_winding_consistent or vol_delta > 0.03:
            print(
                f"  STEP remesh {stl_path.name}: rejected "
                f"(watertight={mesh.is_watertight}, "
                f"winding={mesh.is_winding_consistent}, "
                f"vol {vol:.2f} vs {ref_volume_cm3:.2f} cm³)"
            )
            return

        shutil.copyfile(candidate, stl_path)
        print(
            f"  STEP remesh {stl_path.name}: accepted "
            f"(faces={len(mesh.faces)}, vol={vol:.2f} cm³)"
        )


def _heal_stl(path: Path) -> None:
    """
    Post-process an STL for print-bureau acceptance.

    Strategy:
      1. Diagnose the raw mesh (boundaries, self-intersections).
      2. If clean (0 boundaries, 0 self-intersections): leave it alone.
      3. Else: apply targeted repairs with pymeshfix. Critically, validate
         volume preservation (±5 %) — pymeshfix's `clean()` can cascade
         through self-intersection removal into component loss on meshes
         with high-genus topology (e.g. the hex-perforated lid), where the
         "repaired" result shrinks to a tiny fragment. On volume mismatch
         keep the prior STL and use the STEP export as fallback.
    """
    try:
        import pymeshfix
    except ModuleNotFoundError:
        print(
            f"  STL heal {path.name}: skipped "
            f"(optional dependency 'pymeshfix' not installed)"
        )
        return

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


print("STEP remesh:")
_remesh_stl_from_step(
    step_dir / "trough.step",
    stl_dir / "trough.stl",
    trough.volume / 1000,
)
_remesh_stl_from_step(
    step_dir / "lid.step",
    stl_dir / "lid.stl",
    lid.volume / 1000,
    mesh_size_min=0.4,
    mesh_size_max=1.0,
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
