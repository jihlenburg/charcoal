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
    add,
    export_step,
    export_stl,
    extrude,
    fillet,
    make_face,
)
from ocp_vscode import set_port, show

set_port(3939)

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

# Snap: cantilever tab on lid + through-slot in trough X-wall
hook_width = 6.0
hook_arm = 1.0
hook_length = 6.0
hook_protr = 0.45
hook_engage = 0.8
hook_lead = 1.0
hook_root_fil = 0.5

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

    # Cavity (pocket from top down to floor top)
    with BuildSketch(Plane.XY.offset(size_z)) as _:
        Rectangle(cavity_x, cavity_y)
    extrude(amount=-(size_z - floor), mode=Mode.SUBTRACT)

    # Rabbet: widen cavity at top by shelf_w per side, depth = rabbet_depth
    with BuildSketch(Plane.XY.offset(size_z)) as _:
        Rectangle(rabbet_x, rabbet_y)
    extrude(amount=-rabbet_depth, mode=Mode.SUBTRACT)

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
export_stl(trough, str(stl_dir / "trough.stl"))
export_stl(lid, str(stl_dir / "lid.stl"))


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
