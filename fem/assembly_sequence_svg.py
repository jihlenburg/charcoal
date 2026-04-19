#!/usr/bin/env python3
"""Generate simple SVG assembly drawings for lid/trough insertion.

Outputs:
- output/assembly/lid_trough_assembly_sequence_v1_1_0.svg
- output/assembly/lid_trough_snap_detail_v1_1_0.svg
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import trimesh

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fem.lid_trough_assembly import Geometry, analyze


def mm_to_svg(points, origin_x, origin_y, scale):
    out = []
    for x, z in points:
        sx = origin_x + scale * x
        sy = origin_y - scale * z
        out.append(f"{sx:.1f},{sy:.1f}")
    return " ".join(out)


def transform_xz(points, pivot_x, pivot_z, angle_deg, dx_mm, dz_mm):
    theta = math.radians(angle_deg)
    c = math.cos(theta)
    s = math.sin(theta)
    out = []
    for x, z in points:
        xr = x - pivot_x
        zr = z - pivot_z
        xt = c * xr + s * zr + pivot_x + dx_mm
        zt = -s * xr + c * zr + pivot_z + dz_mm
        out.append((xt, zt))
    return out


def trough_shapes(geom: Geometry):
    outer = [(-31.0, 0.0), (31.0, 0.0), (31.0, 40.0), (-31.0, 40.0)]
    cavity_main = [(-28.8, 2.2), (28.8, 2.2), (28.8, 37.5), (-28.8, 37.5)]
    cavity_rabbet = [(-29.8, 37.5), (29.8, 37.5), (29.8, 40.0), (-29.8, 40.0)]
    hook_pocket = [(-29.65, 34.3), (-28.8, 34.3), (-28.8, 35.6), (-29.65, 35.6)]
    snap_slot = [(28.8, 28.6), (31.0, 28.6), (31.0, 29.4), (28.8, 29.4)]
    return outer, cavity_main, cavity_rabbet, hook_pocket, snap_slot


def lid_outline(geom: Geometry):
    slab = [(-29.5, 37.5), (29.5, 37.5), (29.5, 40.0), (-29.5, 40.0)]
    passive_relief_lo = [(-29.5, 37.5), (-27.9, 37.5), (-29.5, 39.1)]
    passive_relief_hi = [(-29.5, 40.0), (-27.9, 40.0), (-29.5, 38.4)]
    hook = [
        (-28.9, 37.5),
        (-28.0, 37.5),
        (-28.0, 34.5),
        (-29.5, 34.5),
        (-28.9, 35.4),
    ]
    snap = [
        (27.8, 37.5),
        (28.8, 37.5),
        (28.8, 27.3),
        (29.8, 28.8),
        (29.8, 29.2),
        (28.8, 32.0),
        (28.8, 37.5),
    ]
    return slab, passive_relief_lo, passive_relief_hi, hook, snap


def svg_header(width, height):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">\n'
        "  <defs>\n"
        '    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">\n'
        '      <path d="M0,0 L10,5 L0,10 z" fill="#111827"/>\n'
        "    </marker>\n"
        "  </defs>\n"
    )


def draw_trough(panel_x, panel_y, scale, geom: Geometry):
    outer, cavity_main, cavity_rabbet, hook_pocket, snap_slot = trough_shapes(geom)
    items = []
    items.append(
        f'  <polygon points="{mm_to_svg(outer, panel_x, panel_y, scale)}" '
        'fill="#d1d5db" stroke="#4b5563" stroke-width="2"/>\n'
    )
    for void in (cavity_main, cavity_rabbet, hook_pocket, snap_slot):
        items.append(
            f'  <polygon points="{mm_to_svg(void, panel_x, panel_y, scale)}" '
            'fill="#ffffff" stroke="#9ca3af" stroke-width="1.5"/>\n'
        )
    return "".join(items)


def draw_lid(panel_x, panel_y, scale, geom: Geometry, angle_deg, dx_mm, dz_mm, opacity="0.92"):
    slab, relief_lo, relief_hi, hook, snap = lid_outline(geom)
    pivot_x = geom.hook_pivot[0]
    pivot_z = geom.hook_pivot[2]
    items = []
    for poly, fill in (
        (transform_xz(slab, pivot_x, pivot_z, angle_deg, dx_mm, dz_mm), "#60a5fa"),
        (transform_xz(hook, pivot_x, pivot_z, angle_deg, dx_mm, dz_mm), "#3b82f6"),
        (transform_xz(snap, pivot_x, pivot_z, angle_deg, dx_mm, dz_mm), "#2563eb"),
    ):
        items.append(
            f'  <polygon points="{mm_to_svg(poly, panel_x, panel_y, scale)}" '
            f'fill="{fill}" fill-opacity="{opacity}" stroke="#1d4ed8" stroke-width="2"/>\n'
        )
    # show passive corner reliefs as white cut triangles on the slab
    for poly in (
        transform_xz(relief_lo, pivot_x, pivot_z, angle_deg, dx_mm, dz_mm),
        transform_xz(relief_hi, pivot_x, pivot_z, angle_deg, dx_mm, dz_mm),
    ):
        items.append(
            f'  <polygon points="{mm_to_svg(poly, panel_x, panel_y, scale)}" '
            'fill="#ffffff" stroke="#bfdbfe" stroke-width="1.2"/>\n'
        )
    return "".join(items)


def generate_sequence_svg(out_path: Path, geom: Geometry, angle_deg: float, dx_mm: float, dz_mm: float, snap_mm: float):
    width = 1140
    height = 420
    scale = 4.6
    panel_y = 315
    panel_xs = [165, 540, 915]
    svg = [svg_header(width, height)]
    svg.append('  <rect x="0" y="0" width="1140" height="420" fill="#ffffff"/>\n')
    svg.append('  <text x="28" y="36" font-family="Arial, Helvetica, sans-serif" font-size="26" fill="#111827">Deckelmontage v1.1.0</text>\n')
    svg.append('  <text x="28" y="62" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="#374151">Passive -X-Hakenleiste zuerst einhängen, dann nach unten rotieren, zuletzt +X-Schnapperseite drücken.</text>\n')

    for x in (20, 395, 770):
        svg.append(f'  <rect x="{x}" y="80" width="350" height="300" rx="14" fill="#f8fafc" stroke="#cbd5e1"/>\n')

    # Step 1
    svg.append('  <text x="38" y="108" font-family="Arial, Helvetica, sans-serif" font-size="18" font-weight="700" fill="#111827">1. Passive Seite zuerst einfädeln</text>\n')
    svg.append(draw_trough(panel_xs[0], panel_y, scale, geom))
    svg.append(draw_lid(panel_xs[0], panel_y, scale, geom, angle_deg, dx_mm, dz_mm + 3.0))
    svg.append('  <line x1="128" y1="140" x2="185" y2="185" stroke="#111827" stroke-width="2.5" marker-end="url(#arrow)"/>\n')
    svg.append('  <text x="44" y="158" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="#374151">-X-Hakenleiste in die Tasche führen.</text>\n')
    svg.append('  <text x="44" y="176" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="#374151">Neue Eckfreistiche halten die passiven Ecken frei.</text>\n')

    # Step 2
    svg.append('  <text x="414" y="108" font-family="Arial, Helvetica, sans-serif" font-size="18" font-weight="700" fill="#111827">2. Um die Hakenlinie nach unten rotieren</text>\n')
    svg.append(draw_trough(panel_xs[1], panel_y, scale, geom))
    svg.append(draw_lid(panel_xs[1], panel_y, scale, geom, angle_deg, dx_mm, dz_mm))
    svg.append('  <path d="M465,153 C520,118 590,118 638,165" fill="none" stroke="#111827" stroke-width="2.5" marker-end="url(#arrow)"/>\n')
    svg.append(f'  <text x="418" y="158" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="#374151">Gefundene Hook-first-Lage: {angle_deg:.0f}°, +X-Kante ~13.9 mm höher.</text>\n')
    svg.append('  <text x="418" y="176" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="#374151">Diese Lage ist jetzt ohne harte Kollision erreichbar.</text>\n')

    # Step 3
    svg.append('  <text x="789" y="108" font-family="Arial, Helvetica, sans-serif" font-size="18" font-weight="700" fill="#111827">3. Schnapperseite nach unten drücken</text>\n')
    svg.append(draw_trough(panel_xs[2], panel_y, scale, geom))
    svg.append(draw_lid(panel_xs[2], panel_y, scale, geom, 0.0, 0.0, 0.0))
    svg.append('  <line x1="1030" y1="124" x2="1030" y2="170" stroke="#111827" stroke-width="2.5" marker-end="url(#arrow)"/>\n')
    svg.append('  <text x="792" y="158" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="#374151">Auf der +X-Seite nach unten drücken.</text>\n')
    svg.append(f'  <text x="792" y="176" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="#374151">Beide Schnapper federn beim Schließen elastisch ~{snap_mm:.1f} mm ein.</text>\n')
    svg.append('  <text x="792" y="194" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="#374151">Danach rasten sie hörbar in die Slots ein.</text>\n')

    svg.append("</svg>\n")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(svg), encoding="utf-8")


def generate_snap_detail_svg(out_path: Path, geom: Geometry, snap_mm: float):
    width = 640
    height = 300
    scale = 7.5
    origin_x = 180
    origin_y = 292
    svg = [svg_header(width, height)]
    svg.append('  <rect x="0" y="0" width="640" height="300" fill="#ffffff"/>\n')
    svg.append('  <text x="24" y="34" font-family="Arial, Helvetica, sans-serif" font-size="24" fill="#111827">Detail: aktive Schnapperseite</text>\n')
    svg.append('  <text x="24" y="58" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="#374151">Schnittprinzip im X-Z: starre Trogwand, elastische Rastnase am Deckel.</text>\n')

    # Right wall with slot
    wall = [(28.8, 20.0), (31.0, 20.0), (31.0, 37.5), (28.8, 37.5)]
    slot = [(28.8, 28.6), (31.0, 28.6), (31.0, 29.4), (28.8, 29.4)]
    svg.append(f'  <polygon points="{mm_to_svg(wall, origin_x, origin_y, scale)}" fill="#d1d5db" stroke="#4b5563" stroke-width="2"/>\n')
    svg.append(f'  <polygon points="{mm_to_svg(slot, origin_x, origin_y, scale)}" fill="#ffffff" stroke="#9ca3af" stroke-width="1.5"/>\n')

    # Open-position tab and closed-position tab
    open_tab = [(27.8, 37.5), (28.8, 37.5), (28.8, 27.3), (29.8, 28.8), (29.8, 29.2), (28.8, 32.0), (28.8, 37.5)]
    closed_tab = [(x - snap_mm, z) for x, z in open_tab]
    svg.append(f'  <polygon points="{mm_to_svg(open_tab, origin_x, origin_y, scale)}" fill="#93c5fd" fill-opacity="0.35" stroke="#2563eb" stroke-width="2" stroke-dasharray="6 4"/>\n')
    svg.append(f'  <polygon points="{mm_to_svg(closed_tab, origin_x, origin_y, scale)}" fill="#60a5fa" fill-opacity="0.90" stroke="#1d4ed8" stroke-width="2"/>\n')

    svg.append('  <line x1="347" y1="136" x2="305" y2="136" stroke="#111827" stroke-width="2.5" marker-end="url(#arrow)"/>\n')
    svg.append(f'  <text x="362" y="141" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="#374151">Elastische X-Auslenkung ~{snap_mm:.1f} mm</text>\n')
    svg.append('  <text x="24" y="96" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="#374151">Hellblau gestrichelt: freie Rastnase vor Kontakt</text>\n')
    svg.append('  <text x="24" y="116" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="#374151">Blau: eingefederte Rastnase während des Eindrückens</text>\n')
    svg.append('  <text x="24" y="136" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="#374151">Nach der Slotkante springt die Nase wieder nach außen.</text>\n')
    svg.append("</svg>\n")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(svg), encoding="utf-8")


def main() -> int:
    root = ROOT
    lid_path = root / "output" / "STL" / "lid.stl"
    trough_path = root / "output" / "STL" / "trough.stl"
    lid_mesh = trimesh.load_mesh(lid_path, force="mesh")
    trough_mesh = trimesh.load_mesh(trough_path, force="mesh")
    geom = Geometry()
    result = analyze(lid_mesh, trough_mesh, geom, penetration_tol_mm=0.15)

    out_dir = root / "output" / "assembly"
    generate_sequence_svg(
        out_dir / "lid_trough_assembly_sequence_v1_1_0.svg",
        geom=geom,
        angle_deg=result.best_pose.angle_deg,
        dx_mm=result.best_pose.dx_mm,
        dz_mm=result.best_pose.dz_mm,
        snap_mm=max(0.0, result.closing_path.snap_max_interference_mm),
    )
    generate_snap_detail_svg(
        out_dir / "lid_trough_snap_detail_v1_1_0.svg",
        geom=geom,
        snap_mm=max(0.0, result.closing_path.snap_max_interference_mm),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
