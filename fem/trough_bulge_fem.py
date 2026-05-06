#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Linear-elastic trough wall bulge check for charcoal packing pressure.

This is a focused design check, not a granular-material simulation:

- simplified trough shell with the current v1.1.6 wall/floor/rabbet geometry
- optional internal vertical ribs, segmented top belts, or permanent internal
  cross-ties between the two long X-side walls
- uniform lateral pressure on the inside of the long side walls
- PA12 small-strain linear elasticity solved with scikit-fem

The result should be read as "wall compliance per kPa of packing pressure".
Real pellet stuffing pressure is hand/process dependent, so the useful output
is the comparison between variants and the pressure required to reach a visible
bulge, not a single absolute pass/fail number.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

import meshio
import numpy as np

try:
    import gmsh
except ImportError as exc:  # pragma: no cover - dependency guard
    raise SystemExit(
        "Missing FEM dependency. Install with:\n"
        "  ./run setup"
    ) from exc

try:
    from skfem import (
        Basis,
        ElementTetP1,
        ElementVector,
        MeshTet,
        asm,
        condense,
        solve,
    )
    from skfem.models.elasticity import lame_parameters, linear_elasticity
except ImportError as exc:  # pragma: no cover - dependency guard
    raise SystemExit(
        "Missing FEM dependency. Install with:\n"
        "  ./run setup"
    ) from exc


@dataclass(frozen=True)
class TroughGeometry:
    version: str = "1.1.6"
    size_x: float = 65.0
    size_y: float = 95.0
    size_z: float = 40.0
    wall: float = 2.2
    floor: float = 2.2
    shelf_w: float = 1.0
    rabbet_depth: float = 2.5
    rib_count_per_side: int = 3
    rib_depth: float = 1.2
    rib_width: float = 2.0
    rib_z_clearance: float = 1.0
    belt_depth: float = 1.4
    belt_height: float = 4.8
    belt_top_clearance: float = 0.3
    belt_end_clearance: float = 1.0
    belt_feature_clearance_y: float = 3.0
    hook_rail_width: float = 34.0
    hook_width: float = 6.0
    retainer_y_offset: float = 18.0
    outer_belt_depth: float = 1.0
    outer_belt_height: float = 6.0
    outer_belt_top_clearance: float = 0.0
    lid_thk: float = 2.5
    hook_rail_drop: float = 3.0
    tie_width_y: float = 2.2
    tie_height_z: float = 1.4
    tie_lid_gap: float = 4.0
    tie_y_offsets: tuple[float, ...] = (-36.0, 0.0, 36.0)
    mesh_size: float = 1.45

    @property
    def cavity_x(self) -> float:
        return self.size_x - 2.0 * self.wall

    @property
    def cavity_y(self) -> float:
        return self.size_y - 2.0 * self.wall

    @property
    def rabbet_x(self) -> float:
        return self.cavity_x + 2.0 * self.shelf_w

    @property
    def rabbet_y(self) -> float:
        return self.cavity_y + 2.0 * self.shelf_w

    @property
    def rabbet_z(self) -> float:
        return self.size_z - self.rabbet_depth

    @property
    def lower_wall_height(self) -> float:
        return self.rabbet_z - self.floor

    @property
    def rib_z0(self) -> float:
        return self.floor + self.rib_z_clearance

    @property
    def rib_height(self) -> float:
        return self.rabbet_z - self.rib_z0

    @property
    def rib_y_offsets(self) -> tuple[float, ...]:
        if self.rib_count_per_side <= 0:
            return ()
        usable_y = self.cavity_y - 2.0 * self.rib_width
        if self.rib_count_per_side == 1:
            return (0.0,)
        step = usable_y / self.rib_count_per_side
        start = -usable_y / 2.0 + step / 2.0
        return tuple(start + step * idx for idx in range(self.rib_count_per_side))

    @property
    def belt_top_z(self) -> float:
        return self.rabbet_z - self.belt_top_clearance

    @property
    def belt_z0(self) -> float:
        return self.belt_top_z - self.belt_height

    @property
    def retainer_y_offsets(self) -> tuple[float, float]:
        return (-self.retainer_y_offset, self.retainer_y_offset)

    @property
    def belt_y_min(self) -> float:
        return -self.cavity_y / 2.0 + self.belt_end_clearance

    @property
    def belt_y_max(self) -> float:
        return self.cavity_y / 2.0 - self.belt_end_clearance

    @property
    def passive_belt_segments(self) -> tuple[tuple[float, float], ...]:
        gap = (
            -self.hook_rail_width / 2.0 - self.belt_feature_clearance_y,
            self.hook_rail_width / 2.0 + self.belt_feature_clearance_y,
        )
        return y_segments_with_gaps(self.belt_y_min, self.belt_y_max, [gap])

    @property
    def snap_belt_segments(self) -> tuple[tuple[float, float], ...]:
        half_gap = self.hook_width / 2.0 + self.belt_feature_clearance_y
        gaps = [
            (y - half_gap, y + half_gap)
            for y in self.retainer_y_offsets
        ]
        return y_segments_with_gaps(self.belt_y_min, self.belt_y_max, gaps)

    @property
    def outer_belt_top_z(self) -> float:
        return self.size_z - self.outer_belt_top_clearance

    @property
    def outer_belt_z0(self) -> float:
        return self.outer_belt_top_z - self.outer_belt_height

    @property
    def hook_nose_bottom_z(self) -> float:
        return self.size_z - self.lid_thk - self.hook_rail_drop

    @property
    def arm_top_z(self) -> float:
        return self.size_z - self.lid_thk

    @property
    def tie_top_z(self) -> float:
        return self.arm_top_z - self.tie_lid_gap

    @property
    def tie_z0(self) -> float:
        return self.tie_top_z - self.tie_height_z


@dataclass(frozen=True)
class Pa12Material:
    modulus_nominal: float = 2150.0
    poisson: float = 0.40
    yield_strain_low: float = 0.09
    yield_strain_high: float = 0.11


@dataclass(frozen=True)
class BulgeResult:
    version: str
    variant: str
    support_case: str
    pressure_kpa: float
    mesh_size_mm: float
    nodes: int
    tetrahedra: int
    constrained_dofs: int
    loaded_triangles: int
    loaded_area_per_side_mm2: float
    lateral_force_per_side_n: float
    max_outer_bulge_mm: float
    mid_outer_bulge_mm: float
    max_outer_bulge_mm_per_kpa: float
    pressure_for_0_5mm_bulge_kpa: float
    pressure_for_1_0mm_bulge_kpa: float
    max_principal_strain: float
    p95_principal_strain: float
    max_von_mises_strain: float
    pa12_proxy_target_low: float
    pa12_proxy_target_high: float
    assessment: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Linear-elastic FEM check for trough side-wall bulging."
    )
    parser.add_argument(
        "--pressure-kpa",
        type=float,
        default=5.0,
        help=(
            "Uniform side pressure from packed pellets in kPa "
            "(default: %(default)s)."
        ),
    )
    parser.add_argument(
        "--mesh-size",
        type=float,
        default=TroughGeometry.mesh_size,
        help="Target tetra edge length in mm (default: %(default)s).",
    )
    parser.add_argument(
        "--variant",
        choices=(
            "plain",
            "current",
            "ribs",
            "belt",
            "outer-belt",
            "both",
            "all",
        ),
        default="all",
        help="Geometry variant to solve (default: %(default)s).",
    )
    parser.add_argument(
        "--support",
        choices=("open", "lid", "both"),
        default="both",
        help=(
            "open = lid off during filling, floor table-supported in Z only; "
            "lid = same plus X spread constrained at the top rabbet as a "
            "seated-lid proxy (default: %(default)s)."
        ),
    )
    parser.add_argument(
        "--rib-count",
        type=int,
        default=TroughGeometry.rib_count_per_side,
        help="Number of ribs per long wall for the ribs variant.",
    )
    parser.add_argument(
        "--rib-depth",
        type=float,
        default=TroughGeometry.rib_depth,
        help="Rib protrusion into the cavity in mm.",
    )
    parser.add_argument(
        "--rib-width",
        type=float,
        default=TroughGeometry.rib_width,
        help="Rib width along Y in mm.",
    )
    parser.add_argument(
        "--belt-depth",
        type=float,
        default=TroughGeometry.belt_depth,
        help="Anti-spread belt protrusion into the cavity in mm.",
    )
    parser.add_argument(
        "--belt-height",
        type=float,
        default=TroughGeometry.belt_height,
        help="Anti-spread belt height in mm.",
    )
    parser.add_argument(
        "--outer-belt-depth",
        type=float,
        default=TroughGeometry.outer_belt_depth,
        help="External top bead protrusion beyond each X wall in mm.",
    )
    parser.add_argument(
        "--outer-belt-height",
        type=float,
        default=TroughGeometry.outer_belt_height,
        help="External top bead height in mm.",
    )
    parser.add_argument(
        "--json",
        type=Path,
        help="Optional JSON summary output path.",
    )
    parser.add_argument(
        "--vtk-dir",
        type=Path,
        help="Optional directory for .vtu displacement/strain fields.",
    )
    parser.add_argument(
        "--plot-dir",
        type=Path,
        help="Optional directory for PNG/SVG outer-wall bulge heatmaps.",
    )
    return parser


def y_segments_with_gaps(
    y_min: float,
    y_max: float,
    gaps: list[tuple[float, float]],
) -> tuple[tuple[float, float], ...]:
    clipped: list[tuple[float, float]] = []
    for gap_min, gap_max in gaps:
        lo = max(y_min, gap_min)
        hi = min(y_max, gap_max)
        if hi > lo:
            clipped.append((lo, hi))
    clipped.sort()

    merged: list[list[float]] = []
    for lo, hi in clipped:
        if not merged or lo > merged[-1][1]:
            merged.append([lo, hi])
        else:
            merged[-1][1] = max(merged[-1][1], hi)

    segments: list[tuple[float, float]] = []
    cursor = y_min
    for lo, hi in merged:
        if lo > cursor:
            segments.append((cursor, lo))
        cursor = max(cursor, hi)
    if cursor < y_max:
        segments.append((cursor, y_max))
    return tuple(segments)


def add_box(
    occ: object,
    x0: float,
    y0: float,
    z0: float,
    dx: float,
    dy: float,
    dz: float,
) -> tuple[int, int]:
    tag = occ.addBox(x0, y0, z0, dx, dy, dz)
    return (3, tag)


def build_trough_mesh(
    geom: TroughGeometry,
    variant: str,
    mesh_path: Path,
) -> None:
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.option.setNumber("Mesh.ElementOrder", 1)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", geom.mesh_size)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", geom.mesh_size)
        gmsh.option.setNumber("Mesh.SaveAll", 1)
        gmsh.model.add(f"trough_bulge_{variant}")
        occ = gmsh.model.occ

        volumes: list[tuple[int, int]] = []

        # Floor plate, full body footprint. The production flange is omitted
        # because it is outside the loaded cavity and barely affects side bulge.
        volumes.append(
            add_box(
                occ,
                -geom.size_x / 2.0,
                -geom.size_y / 2.0,
                0.0,
                geom.size_x,
                geom.size_y,
                geom.floor,
            )
        )

        # Lower side walls up to the rabbet shelf.
        volumes.extend(
            [
                add_box(
                    occ,
                    geom.cavity_x / 2.0,
                    -geom.size_y / 2.0,
                    geom.floor,
                    geom.wall,
                    geom.size_y,
                    geom.lower_wall_height,
                ),
                add_box(
                    occ,
                    -geom.size_x / 2.0,
                    -geom.size_y / 2.0,
                    geom.floor,
                    geom.wall,
                    geom.size_y,
                    geom.lower_wall_height,
                ),
                add_box(
                    occ,
                    -geom.cavity_x / 2.0,
                    geom.cavity_y / 2.0,
                    geom.floor,
                    geom.cavity_x,
                    geom.wall,
                    geom.lower_wall_height,
                ),
                add_box(
                    occ,
                    -geom.cavity_x / 2.0,
                    -geom.size_y / 2.0,
                    geom.floor,
                    geom.cavity_x,
                    geom.wall,
                    geom.lower_wall_height,
                ),
            ]
        )

        # Upper rabbet band: top opening is widened by shelf_w, leaving a
        # thinner wall band at the lid seat.
        upper_h = geom.size_z - geom.rabbet_z
        upper_wall = geom.wall - geom.shelf_w
        volumes.extend(
            [
                add_box(
                    occ,
                    geom.rabbet_x / 2.0,
                    -geom.size_y / 2.0,
                    geom.rabbet_z,
                    upper_wall,
                    geom.size_y,
                    upper_h,
                ),
                add_box(
                    occ,
                    -geom.size_x / 2.0,
                    -geom.size_y / 2.0,
                    geom.rabbet_z,
                    upper_wall,
                    geom.size_y,
                    upper_h,
                ),
                add_box(
                    occ,
                    -geom.rabbet_x / 2.0,
                    geom.rabbet_y / 2.0,
                    geom.rabbet_z,
                    geom.rabbet_x,
                    upper_wall,
                    upper_h,
                ),
                add_box(
                    occ,
                    -geom.rabbet_x / 2.0,
                    -geom.size_y / 2.0,
                    geom.rabbet_z,
                    geom.rabbet_x,
                    upper_wall,
                    upper_h,
                ),
            ]
        )

        if variant == "ribs":
            for y in geom.rib_y_offsets:
                volumes.extend(
                    [
                        add_box(
                            occ,
                            geom.cavity_x / 2.0 - geom.rib_depth,
                            y - geom.rib_width / 2.0,
                            geom.rib_z0,
                            geom.rib_depth,
                            geom.rib_width,
                            geom.rib_height,
                        ),
                        add_box(
                            occ,
                            -geom.cavity_x / 2.0,
                            y - geom.rib_width / 2.0,
                            geom.rib_z0,
                            geom.rib_depth,
                            geom.rib_width,
                            geom.rib_height,
                        ),
                    ]
                )

        if variant == "belt":
            for side, segments in (
                (-1.0, geom.passive_belt_segments),
                (1.0, geom.snap_belt_segments),
            ):
                x0 = (
                    side * geom.cavity_x / 2.0 - geom.belt_depth
                    if side > 0.0
                    else -geom.cavity_x / 2.0
                )
                for y0, y1 in segments:
                    volumes.append(
                        add_box(
                            occ,
                            x0,
                            y0,
                            geom.belt_z0,
                            geom.belt_depth,
                            y1 - y0,
                            geom.belt_height,
                        )
                    )

        if variant == "outer-belt":
            volumes.extend(
                [
                    add_box(
                        occ,
                        geom.size_x / 2.0,
                        -geom.size_y / 2.0,
                        geom.outer_belt_z0,
                        geom.outer_belt_depth,
                        geom.size_y,
                        geom.outer_belt_height,
                    ),
                    add_box(
                        occ,
                        -geom.size_x / 2.0 - geom.outer_belt_depth,
                        -geom.size_y / 2.0,
                        geom.outer_belt_z0,
                        geom.outer_belt_depth,
                        geom.size_y,
                        geom.outer_belt_height,
                    ),
                ]
            )

        if variant == "current":
            for y in geom.tie_y_offsets:
                volumes.append(
                    add_box(
                        occ,
                        -geom.cavity_x / 2.0,
                        y - geom.tie_width_y / 2.0,
                        geom.tie_z0,
                        geom.cavity_x,
                        geom.tie_width_y,
                        geom.tie_height_z,
                    )
                )

        fused, _ = occ.fuse([volumes[0]], volumes[1:])
        occ.synchronize()
        if not fused:
            raise RuntimeError("Gmsh failed to fuse the trough FEM volumes.")

        gmsh.model.mesh.generate(3)
        gmsh.write(str(mesh_path))
    finally:
        gmsh.finalize()


def mesh_from_msh(mesh_path: Path) -> tuple[MeshTet, np.ndarray]:
    gmsh_mesh = meshio.read(str(mesh_path))
    tetra_blocks = [
        block.data for block in gmsh_mesh.cells if block.type == "tetra"
    ]
    triangle_blocks = [
        block.data for block in gmsh_mesh.cells if block.type == "triangle"
    ]
    if not tetra_blocks:
        raise RuntimeError("No tetrahedra found in generated trough mesh.")
    if not triangle_blocks:
        raise RuntimeError("No boundary triangles found in generated trough mesh.")

    points = np.asarray(gmsh_mesh.points, dtype=float)
    tetra = np.vstack(tetra_blocks)
    triangles = np.vstack(triangle_blocks)
    return MeshTet(points.T, tetra.T), triangles


def triangle_areas_and_normals(
    points: np.ndarray,
    triangles: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    p0 = points[triangles[:, 0]]
    p1 = points[triangles[:, 1]]
    p2 = points[triangles[:, 2]]
    cross = np.cross(p1 - p0, p2 - p0)
    norm = np.linalg.norm(cross, axis=1)
    areas = 0.5 * norm
    normals = np.zeros_like(cross)
    ok = norm > 0.0
    normals[ok] = cross[ok] / norm[ok, None]
    centroids = (p0 + p1 + p2) / 3.0
    return areas, normals, centroids


def loaded_side_triangles(
    mesh: MeshTet,
    triangles: np.ndarray,
    geom: TroughGeometry,
) -> tuple[np.ndarray, np.ndarray, float]:
    points = mesh.p.T
    areas, normals, centroids = triangle_areas_and_normals(points, triangles)

    x = centroids[:, 0]
    y = centroids[:, 1]
    z = centroids[:, 2]
    nx = normals[:, 0]

    interior_y = np.abs(y) <= geom.rabbet_y / 2.0 + geom.mesh_size
    loaded_z = (z >= geom.floor - geom.mesh_size) & (
        z <= geom.size_z + geom.mesh_size
    )
    x_facing = np.abs(nx) >= 0.65

    # Exclude exterior faces at X=+/-size_x/2. Keep the lower cavity wall,
    # upper rabbet wall, and rib front faces.
    right_inner = (
        (x > 0.0)
        & (x < geom.size_x / 2.0 - 0.2)
        & interior_y
        & loaded_z
        & x_facing
    )
    left_inner = (
        (x < 0.0)
        & (x > -geom.size_x / 2.0 + 0.2)
        & interior_y
        & loaded_z
        & x_facing
    )

    side_sign = np.zeros(len(triangles), dtype=float)
    side_sign[right_inner] = 1.0
    side_sign[left_inner] = -1.0
    loaded = np.flatnonzero(side_sign != 0.0)
    if len(loaded) == 0:
        raise RuntimeError("No loaded side-wall triangles found.")

    area_per_side = max(
        float(areas[right_inner].sum()),
        float(areas[left_inner].sum()),
    )
    return loaded, side_sign, area_per_side


def pressure_rhs(
    basis: Basis,
    mesh: MeshTet,
    triangles: np.ndarray,
    loaded: np.ndarray,
    side_sign: np.ndarray,
    pressure_kpa: float,
) -> tuple[np.ndarray, float]:
    rhs = np.zeros(basis.N)
    points = mesh.p.T
    areas, _, _ = triangle_areas_and_normals(points, triangles)
    pressure_n_per_mm2 = pressure_kpa * 1e-3

    for tri_idx in loaded:
        tri = triangles[tri_idx]
        force_x = side_sign[tri_idx] * pressure_n_per_mm2 * areas[tri_idx]
        rhs[basis.nodal_dofs[0, tri]] += force_x / 3.0

    return rhs, float(pressure_n_per_mm2)


def constrained_dofs(
    basis: Basis,
    mesh: MeshTet,
    geom: TroughGeometry,
    support_case: str,
) -> np.ndarray:
    xyz = mesh.p.T
    x = xyz[:, 0]
    y = xyz[:, 1]
    z = xyz[:, 2]
    tol = max(1e-6, geom.mesh_size * 0.55)

    bottom = np.flatnonzero(z <= tol)
    constrained = [basis.nodal_dofs[2, bottom]]

    # The filling case is a trough resting on a table, not glued down:
    # support the floor vertically, then add minimal in-plane anchors to remove
    # rigid-body X/Y translation and rotation about Z without suppressing wall
    # spread at the floor perimeter.
    bottom_xyz = xyz[bottom]
    anchor0 = bottom[np.argmin(np.linalg.norm(bottom_xyz, axis=1))]
    anchor1_target = np.array([geom.size_x / 2.0, 0.0, 0.0])
    anchor1 = bottom[np.argmin(np.linalg.norm(bottom_xyz - anchor1_target, axis=1))]
    constrained.append(basis.nodal_dofs[0, np.array([anchor0])])
    constrained.append(basis.nodal_dofs[1, np.array([anchor0, anchor1])])

    if support_case == "lid":
        top_side = np.flatnonzero(
            (z >= geom.size_z - tol)
            & (np.abs(y) <= geom.rabbet_y / 2.0 + tol)
            & (np.abs(x) >= geom.rabbet_x / 2.0 - tol)
        )
        constrained.append(basis.nodal_dofs[0, top_side])

    return np.unique(np.concatenate(constrained))


def nodal_displacements(
    basis: Basis,
    solution: np.ndarray,
    nvertices: int,
) -> np.ndarray:
    disp = np.zeros((nvertices, 3))
    disp[:, 0] = solution[basis.nodal_dofs[0]]
    disp[:, 1] = solution[basis.nodal_dofs[1]]
    disp[:, 2] = solution[basis.nodal_dofs[2]]
    return disp


def element_strains(
    mesh: MeshTet,
    nodal_u: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    xyz = mesh.p.T
    tetra = mesh.t.T
    max_principal = np.zeros(len(tetra))
    min_principal = np.zeros(len(tetra))
    von_mises = np.zeros(len(tetra))

    for idx, elem in enumerate(tetra):
        coords = xyz[elem]
        matrix = np.ones((4, 4))
        matrix[:, 1:] = coords
        inverse = np.linalg.inv(matrix)
        grad_shape = inverse[1:, :].T
        ue = nodal_u[elem]
        grad_u = ue.T @ grad_shape
        strain = 0.5 * (grad_u + grad_u.T)
        principal = np.linalg.eigvalsh(strain)
        dev = strain - np.trace(strain) / 3.0 * np.eye(3)

        max_principal[idx] = principal[-1]
        min_principal[idx] = principal[0]
        von_mises[idx] = np.sqrt(2.0 / 3.0 * np.sum(dev * dev))

    return max_principal, min_principal, von_mises


def wall_bulge_metrics(
    mesh: MeshTet,
    nodal_u: np.ndarray,
    geom: TroughGeometry,
) -> tuple[float, float]:
    xyz = mesh.p.T
    x = xyz[:, 0]
    y = xyz[:, 1]
    z = xyz[:, 2]
    tol = max(0.35, geom.mesh_size * 0.8)

    outer_wall = (
        (np.abs(np.abs(x) - geom.size_x / 2.0) <= tol)
        & (np.abs(y) <= geom.cavity_y / 2.0)
        & (z >= geom.floor - tol)
        & (z <= geom.size_z + tol)
    )
    if not np.any(outer_wall):
        raise RuntimeError("No outer long-wall nodes found for bulge metrics.")

    outward = np.where(x >= 0.0, nodal_u[:, 0], -nodal_u[:, 0])
    max_outer = float(outward[outer_wall].max())

    mid_z = (geom.floor + geom.rabbet_z) / 2.0
    mid_band = outer_wall & (np.abs(y) <= tol) & (np.abs(z - mid_z) <= tol)
    if not np.any(mid_band):
        mid_band = outer_wall & (np.abs(y) <= 2.0 * tol)
    mid_outer = float(outward[mid_band].max())
    return max_outer, mid_outer


def assess(
    max_bulge: float,
    strain: float,
    material: Pa12Material,
) -> str:
    proxy_low = material.yield_strain_low / 3.0
    if max_bulge >= 1.0:
        bulge_note = "visible bulge likely at this pressure"
    elif max_bulge >= 0.5:
        bulge_note = "small but visible bulge possible at this pressure"
    else:
        bulge_note = "bulge is likely subtle at this pressure"

    if strain <= proxy_low:
        strain_note = "strain stays inside conservative PA12 proxy"
    else:
        strain_note = "strain exceeds conservative PA12 proxy"
    return f"{bulge_note}; {strain_note}"


def write_vtk(
    vtk_path: Path,
    mesh: MeshTet,
    nodal_u: np.ndarray,
    max_principal: np.ndarray,
    min_principal: np.ndarray,
    von_mises: np.ndarray,
) -> None:
    vtk_path.parent.mkdir(parents=True, exist_ok=True)
    meshio.write_points_cells(
        str(vtk_path),
        points=mesh.p.T,
        cells=[("tetra", mesh.t.T)],
        point_data={
            "displacement_mm": nodal_u,
            "u_x_mm": nodal_u[:, 0],
            "u_y_mm": nodal_u[:, 1],
            "u_z_mm": nodal_u[:, 2],
        },
        cell_data={
            "max_principal_strain": [max_principal],
            "min_principal_strain": [min_principal],
            "von_mises_strain": [von_mises],
        },
    )


def write_outer_wall_plot(
    plot_dir: Path,
    mesh: MeshTet,
    triangles: np.ndarray,
    nodal_u: np.ndarray,
    geom: TroughGeometry,
    result: BulgeResult,
) -> None:
    try:
        import matplotlib.pyplot as plt
        import matplotlib.tri as mtri
    except ImportError as exc:  # pragma: no cover - optional visualization
        raise RuntimeError(
            "matplotlib is required for --plot-dir visualizations"
        ) from exc

    points = mesh.p.T
    x = points[:, 0]
    y = points[:, 1]
    z = points[:, 2]
    tol = max(0.35, geom.mesh_size * 0.8)

    right_outer = (
        (np.abs(x - geom.size_x / 2.0) <= tol)
        & (np.abs(y) <= geom.cavity_y / 2.0 + tol)
        & (z >= geom.floor - tol)
        & (z <= geom.size_z + tol)
    )
    tri_mask = np.all(right_outer[triangles], axis=1)
    wall_triangles = triangles[tri_mask]
    if len(wall_triangles) == 0:
        raise RuntimeError("No right outer-wall triangles found for plot.")

    unique_nodes, inverse = np.unique(wall_triangles.reshape(-1), return_inverse=True)
    remapped = inverse.reshape((-1, 3))
    wall_y = y[unique_nodes]
    wall_z = z[unique_nodes]
    wall_bulge = nodal_u[unique_nodes, 0]
    triangulation = mtri.Triangulation(wall_y, wall_z, remapped)

    plot_dir.mkdir(parents=True, exist_ok=True)
    stem = f"trough_bulge_{result.variant}_{result.support_case}"

    fig, ax = plt.subplots(figsize=(8.0, 3.8), constrained_layout=True)
    color = ax.tripcolor(
        triangulation,
        wall_bulge,
        shading="gouraud",
        cmap="viridis",
    )
    contour = ax.tricontour(
        triangulation,
        wall_bulge,
        levels=6,
        colors="black",
        linewidths=0.35,
        alpha=0.45,
    )
    ax.clabel(contour, inline=True, fontsize=7, fmt="%.2f")
    cbar = fig.colorbar(color, ax=ax)
    cbar.set_label("outward displacement on +X wall [mm]")
    ax.set_title(
        f"{result.variant} / {result.support_case}: "
        f"{result.pressure_kpa:.1f} kPa side pressure"
    )
    ax.set_xlabel("Y across long wall [mm]")
    ax.set_ylabel("Z floor-to-lid [mm]")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-geom.cavity_y / 2.0, geom.cavity_y / 2.0)
    ax.set_ylim(geom.floor, geom.size_z)
    ax.text(
        0.02,
        0.98,
        (
            f"max {result.max_outer_bulge_mm:.3f} mm\n"
            f"mid {result.mid_outer_bulge_mm:.3f} mm\n"
            f"1 mm at {result.pressure_for_1_0mm_bulge_kpa:.1f} kPa"
        ),
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=8,
        bbox={
            "boxstyle": "round,pad=0.25",
            "facecolor": "white",
            "edgecolor": "0.75",
            "alpha": 0.85,
        },
    )
    fig.savefig(plot_dir / f"{stem}.png", dpi=180)
    fig.savefig(plot_dir / f"{stem}.svg")
    plt.close(fig)


def solve_case(
    mesh: MeshTet,
    triangles: np.ndarray,
    geom: TroughGeometry,
    material: Pa12Material,
    variant: str,
    support_case: str,
    pressure_kpa: float,
    vtk_dir: Path | None,
    plot_dir: Path | None,
) -> BulgeResult:
    element = ElementVector(ElementTetP1())
    basis = Basis(mesh, element)
    lame_lambda, lame_mu = lame_parameters(
        material.modulus_nominal,
        material.poisson,
    )
    stiffness = asm(linear_elasticity(lame_lambda, lame_mu), basis)

    loaded, side_sign, area_per_side = loaded_side_triangles(
        mesh,
        triangles,
        geom,
    )
    rhs, pressure_n_per_mm2 = pressure_rhs(
        basis,
        mesh,
        triangles,
        loaded,
        side_sign,
        pressure_kpa,
    )
    constrained = constrained_dofs(basis, mesh, geom, support_case)
    solution = solve(*condense(stiffness, rhs, D=constrained))
    nodal_u = nodal_displacements(basis, solution, mesh.nvertices)
    max_outer, mid_outer = wall_bulge_metrics(mesh, nodal_u, geom)
    max_principal, min_principal, von_mises = element_strains(mesh, nodal_u)

    positive_principal = max_principal[max_principal > 0.0]
    p95_principal = (
        float(np.quantile(positive_principal, 0.95))
        if len(positive_principal)
        else 0.0
    )
    disp_per_kpa = max_outer / pressure_kpa if pressure_kpa > 0.0 else 0.0
    proxy_low = material.yield_strain_low / 3.0
    proxy_high = material.yield_strain_high / 3.0

    result = BulgeResult(
        version=geom.version,
        variant=variant,
        support_case=support_case,
        pressure_kpa=pressure_kpa,
        mesh_size_mm=geom.mesh_size,
        nodes=mesh.nvertices,
        tetrahedra=mesh.nelements,
        constrained_dofs=len(constrained),
        loaded_triangles=len(loaded),
        loaded_area_per_side_mm2=area_per_side,
        lateral_force_per_side_n=pressure_n_per_mm2 * area_per_side,
        max_outer_bulge_mm=max_outer,
        mid_outer_bulge_mm=mid_outer,
        max_outer_bulge_mm_per_kpa=disp_per_kpa,
        pressure_for_0_5mm_bulge_kpa=0.5 / disp_per_kpa
        if disp_per_kpa > 0.0
        else float("inf"),
        pressure_for_1_0mm_bulge_kpa=1.0 / disp_per_kpa
        if disp_per_kpa > 0.0
        else float("inf"),
        max_principal_strain=float(max_principal.max()),
        p95_principal_strain=p95_principal,
        max_von_mises_strain=float(von_mises.max()),
        pa12_proxy_target_low=proxy_low,
        pa12_proxy_target_high=proxy_high,
        assessment=assess(max_outer, float(max_principal.max()), material),
    )

    if vtk_dir is not None:
        write_vtk(
            vtk_dir / f"trough_bulge_{variant}_{support_case}.vtu",
            mesh,
            nodal_u,
            max_principal,
            min_principal,
            von_mises,
        )
    if plot_dir is not None:
        write_outer_wall_plot(
            plot_dir,
            mesh,
            triangles,
            nodal_u,
            geom,
            result,
        )

    return result


def solve_variant(
    geom: TroughGeometry,
    material: Pa12Material,
    variant: str,
    support_cases: list[str],
    pressure_kpa: float,
    vtk_dir: Path | None,
    plot_dir: Path | None,
) -> list[BulgeResult]:
    with tempfile.TemporaryDirectory() as tmpdir:
        mesh_path = Path(tmpdir) / f"trough_bulge_{variant}.msh"
        build_trough_mesh(geom, variant, mesh_path)
        mesh, triangles = mesh_from_msh(mesh_path)

    return [
        solve_case(
            mesh,
            triangles,
            geom,
            material,
            variant,
            support_case,
            pressure_kpa,
            vtk_dir,
            plot_dir,
        )
        for support_case in support_cases
    ]


def print_report(results: list[BulgeResult], geom: TroughGeometry) -> None:
    print("Trough wall bulge FEM")
    print(f"Version:                   {geom.version}")
    print("Model scope:               simplified solid trough shell, linear elastic")
    print("Load assumption:           uniform side pressure on both long walls")
    print("Material:                  PA12, E=2150 MPa, nu=0.40")
    print(
        "Body / cavity:             "
        f"{geom.size_x:.1f}×{geom.size_y:.1f}×{geom.size_z:.1f} mm / "
        f"{geom.cavity_x:.1f}×{geom.cavity_y:.1f} mm"
    )
    print(
        "Rib candidate:             "
        f"{geom.rib_count_per_side} per side, "
        f"{geom.rib_width:.1f} mm wide × {geom.rib_depth:.1f} mm deep"
    )
    print(
        "Belt candidate:            "
        f"{len(geom.passive_belt_segments) + len(geom.snap_belt_segments)} "
        f"segments, {geom.belt_height:.1f} mm tall × "
        f"{geom.belt_depth:.1f} mm deep"
    )
    print(
        "Outer bead candidate:      "
        f"{geom.outer_belt_height:.1f} mm tall × "
        f"{geom.outer_belt_depth:.1f} mm protrusion each X side"
    )
    print(
        "Current tie bars:          "
        f"{len(geom.tie_y_offsets)} bars, "
        f"{geom.tie_width_y:.1f} mm wide × {geom.tie_height_z:.1f} mm tall, "
        f"{geom.tie_lid_gap:.1f} mm below lid underside"
    )
    print()
    for result in results:
        print(f"{result.variant} / {result.support_case}")
        print(
            "  Mesh nodes / tetrahedra: "
            f"{result.nodes} / {result.tetrahedra}"
        )
        print(
            "  Pressure / side force:   "
            f"{result.pressure_kpa:.1f} kPa / "
            f"{result.lateral_force_per_side_n:.1f} N per long wall"
        )
        print(
            "  Max outer bulge:         "
            f"{result.max_outer_bulge_mm:.3f} mm "
            f"({result.max_outer_bulge_mm_per_kpa:.3f} mm/kPa)"
        )
        print(
            "  Mid-wall outer bulge:    "
            f"{result.mid_outer_bulge_mm:.3f} mm"
        )
        print(
            "  Pressure for 0.5/1.0 mm: "
            f"{result.pressure_for_0_5mm_bulge_kpa:.1f} / "
            f"{result.pressure_for_1_0mm_bulge_kpa:.1f} kPa"
        )
        print(
            "  Max principal strain:    "
            f"{result.max_principal_strain * 100:.2f} % "
            f"(p95 {result.p95_principal_strain * 100:.2f} %)"
        )
        print(
            "  Max von-Mises strain:    "
            f"{result.max_von_mises_strain * 100:.2f} %"
        )
        print(f"  Assessment:              {result.assessment}")
    print()
    print(
        "Note: pellet pressure is not solved from first principles here; scale the "
        "mm/kPa number linearly for different hand-packing loads."
    )


def json_ready(results: list[BulgeResult]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for result in results:
        item: dict[str, object] = {}
        for key, value in asdict(result).items():
            if isinstance(value, np.integer):
                item[key] = int(value)
            elif isinstance(value, np.floating):
                item[key] = float(value)
            else:
                item[key] = value
        out.append(item)
    return out


def main() -> int:
    args = build_parser().parse_args()
    geom = TroughGeometry(
        mesh_size=args.mesh_size,
        rib_count_per_side=args.rib_count,
        rib_depth=args.rib_depth,
        rib_width=args.rib_width,
        belt_depth=args.belt_depth,
        belt_height=args.belt_height,
        outer_belt_depth=args.outer_belt_depth,
        outer_belt_height=args.outer_belt_height,
    )
    material = Pa12Material()

    if args.variant == "all":
        variants = ["plain", "current", "ribs", "belt", "outer-belt"]
    elif args.variant == "both":
        variants = ["plain", "current"]
    else:
        variants = [args.variant]
    support_cases = ["open", "lid"] if args.support == "both" else [args.support]

    results: list[BulgeResult] = []
    for variant in variants:
        results.extend(
            solve_variant(
                geom,
                material,
                variant,
                support_cases,
                args.pressure_kpa,
                args.vtk_dir,
                args.plot_dir,
            )
        )

    print_report(results, geom)

    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(json_ready(results), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
