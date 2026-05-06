#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Local retention check for the passive v1.1.6 hook rail.

This model is intentionally focused:

- one centered passive hook rail only
- linear-elastic PA12, no nonlinear contact
- downward retention load on the lower hook nose, with the top stem clamped
- separate geometry metrics for real wall undercut and pocket clearance

The force result is a structural margin estimate for the hook rail. If the
reported force is high but the real capture is shallow, the practical problem
is geometric disengagement rather than PA12 strength.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

try:
    import gmsh
    import meshio
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
class HookGeometry:
    version: str = "1.1.6"
    size_x: float = 65.0
    wall: float = 2.2
    shelf_w: float = 1.0
    fit_clear: float = 0.30
    hook_rail_width: float = 34.0
    hook_rail_drop: float = 3.0
    hook_rail_depth: float = 2.1
    hook_rail_capture: float = 1.1
    hook_rail_nose_height: float = 0.9
    hook_slot_depth: float = 1.35
    hook_slot_lead_depth: float = 0.55
    hook_nose_outboard: float = 0.35
    hook_tip_cham: float = 0.2
    load_patch_x: float = 0.35
    mesh_size: float = 0.30

    @property
    def cavity_x(self) -> float:
        return self.size_x - 2.0 * self.wall

    @property
    def lid_x(self) -> float:
        return self.cavity_x + 2.0 * self.shelf_w - 2.0 * self.fit_clear

    @property
    def effective_wall_capture(self) -> float:
        return self.lid_x / 2.0 + self.hook_nose_outboard - self.cavity_x / 2.0

    @property
    def pocket_outer_clearance(self) -> float:
        return self.hook_slot_depth - self.effective_wall_capture

    @property
    def receiver_ledge_depth(self) -> float:
        return self.hook_slot_depth - self.hook_slot_lead_depth

    @property
    def minimum_shift_to_unhook(self) -> float:
        return self.effective_wall_capture

    @property
    def top_stem_throat(self) -> float:
        return self.hook_rail_depth - self.hook_rail_capture

    @property
    def top_stem_area(self) -> float:
        return self.top_stem_throat * self.hook_rail_width

    @property
    def nose_slope_angle_deg(self) -> float:
        run = self.hook_rail_capture + self.hook_nose_outboard
        return float(np.degrees(np.arctan2(self.hook_rail_nose_height, run)))


@dataclass(frozen=True)
class Pa12Material:
    modulus_nominal: float = 2150.0
    modulus_low: float = 1650.0
    modulus_high: float = 2200.0
    poisson: float = 0.40
    yield_strain_low: float = 0.09
    yield_strain_high: float = 0.11


@dataclass(frozen=True)
class HookResult:
    version: str
    hook_nose_outboard_mm: float
    effective_wall_capture_mm: float
    pocket_outer_clearance_mm: float
    receiver_ledge_depth_mm: float
    minimum_shift_to_unhook_mm: float
    top_stem_throat_mm: float
    top_stem_area_mm2: float
    nose_slope_angle_deg: float
    mesh_size_mm: float
    nodes: int
    tetrahedra: int
    clamp_nodes: int
    load_nodes: int
    load_face_mean_compliance_mm_per_n: float
    vertical_stiffness_n_per_mm: float
    max_principal_strain_per_n: float
    max_von_mises_strain_per_n: float
    force_at_pa12_proxy_low_n: float
    force_at_pa12_proxy_high_n: float
    force_at_yield_low_n: float
    force_at_yield_high_n: float
    assessment: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Local FEM/check for the passive hook rail."
    )
    parser.add_argument(
        "--hook-nose-outboard",
        type=float,
        default=HookGeometry.hook_nose_outboard,
        help=(
            "Outward protrusion past the lid edge in mm "
            "(default: current geometry, %(default)s)."
        ),
    )
    parser.add_argument(
        "--hook-rail-depth",
        type=float,
        default=HookGeometry.hook_rail_depth,
        help=(
            "Maximum inward rail depth in mm "
            "(default: current geometry, %(default)s)."
        ),
    )
    parser.add_argument(
        "--mesh-size",
        type=float,
        default=HookGeometry.mesh_size,
        help="Target tetra edge length in mm (default: %(default)s).",
    )
    parser.add_argument(
        "--vtk",
        type=Path,
        help="Optional .vtu output with the unit-load displacement field.",
    )
    parser.add_argument(
        "--json",
        type=Path,
        help="Optional JSON summary output path.",
    )
    return parser


def build_hook_mesh(geom: HookGeometry, mesh_path: Path) -> None:
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.add("passive_hook_hold")
        occ = gmsh.model.occ

        points = [
            (geom.hook_rail_capture, 0.0),
            (geom.hook_rail_depth, 0.0),
            (geom.hook_rail_depth, -geom.hook_rail_drop),
            (
                -geom.hook_nose_outboard + geom.hook_tip_cham,
                -geom.hook_rail_drop,
            ),
            (
                -geom.hook_nose_outboard,
                -geom.hook_rail_drop + geom.hook_tip_cham,
            ),
            (
                geom.hook_rail_capture,
                -geom.hook_rail_drop + geom.hook_rail_nose_height,
            ),
        ]
        tags = [occ.addPoint(x, 0.0, z) for x, z in points]
        edges = [occ.addLine(a, b) for a, b in zip(tags, tags[1:])]
        edges.append(occ.addLine(tags[-1], tags[0]))
        loop = occ.addCurveLoop(edges)
        face = occ.addPlaneSurface([loop])
        occ.extrude([(2, face)], 0.0, geom.hook_rail_width, 0.0)
        occ.synchronize()

        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", geom.mesh_size)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", geom.mesh_size)
        gmsh.model.mesh.generate(3)
        gmsh.write(str(mesh_path))
    finally:
        gmsh.finalize()


def identify_node_sets(
    mesh: MeshTet,
    geom: HookGeometry,
) -> tuple[np.ndarray, np.ndarray]:
    xyz = mesh.p.T
    x = xyz[:, 0]
    z = xyz[:, 2]
    tol = max(1e-6, 0.45 * geom.mesh_size)

    clamp = np.flatnonzero(
        (np.abs(z) <= tol)
        & (x >= geom.hook_rail_capture - tol)
        & (x <= geom.hook_rail_depth + tol)
    )
    load = np.flatnonzero(
        (np.abs(z + geom.hook_rail_drop) <= tol)
        & (x <= -geom.hook_nose_outboard + geom.load_patch_x + tol)
    )

    if len(clamp) == 0:
        raise RuntimeError("No clamp nodes found on the hook top stem.")
    if len(load) == 0:
        raise RuntimeError("No load nodes found on the lower hook nose.")
    return clamp, load


def solve_unit_retention_load(
    mesh: MeshTet,
    clamp_nodes: np.ndarray,
    load_nodes: np.ndarray,
    material: Pa12Material,
) -> tuple[Basis, np.ndarray]:
    element = ElementVector(ElementTetP1())
    basis = Basis(mesh, element)
    lame_lambda, lame_mu = lame_parameters(
        material.modulus_nominal,
        material.poisson,
    )
    stiffness = asm(linear_elasticity(lame_lambda, lame_mu), basis)

    rhs = np.zeros(stiffness.shape[0])
    rhs[basis.nodal_dofs[2, load_nodes]] = -1.0 / len(load_nodes)
    constrained = basis.get_dofs(nodes=clamp_nodes).all()
    solution = solve(*condense(stiffness, rhs, D=constrained))
    return basis, solution


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
            "unit_displacement_mm": nodal_u,
            "u_x_mm_per_n": nodal_u[:, 0],
            "u_y_mm_per_n": nodal_u[:, 1],
            "u_z_mm_per_n": nodal_u[:, 2],
        },
        cell_data={
            "max_principal_strain_per_n": [max_principal],
            "min_principal_strain_per_n": [min_principal],
            "von_mises_strain_per_n": [von_mises],
        },
    )


def assess(geom: HookGeometry, force_proxy_low: float) -> str:
    notes: list[str] = []
    if geom.effective_wall_capture < 1.0:
        notes.append("geometric capture is shallow")
    else:
        notes.append("geometric capture is reasonable")
    if geom.pocket_outer_clearance < 0.25:
        notes.append("outer pocket clearance is tight")
    else:
        notes.append("outer pocket clearance is printable")
    if geom.receiver_ledge_depth < 0.6:
        notes.append("receiver ledge is shallow")
    else:
        notes.append("receiver ledge is deliberate")
    if force_proxy_low > 50.0:
        notes.append("PA12 hook strength is not the limiting factor")
    else:
        notes.append("PA12 hook strength may be limiting")
    return "; ".join(notes)


def analyze(
    geom: HookGeometry,
    material: Pa12Material,
    vtk_path: Path | None,
) -> HookResult:
    with tempfile.TemporaryDirectory() as tmpdir:
        mesh_path = Path(tmpdir) / "passive_hook_hold.msh"
        build_hook_mesh(geom, mesh_path)
        mesh = MeshTet.load(str(mesh_path))

    clamp_nodes, load_nodes = identify_node_sets(mesh, geom)
    basis, solution = solve_unit_retention_load(
        mesh,
        clamp_nodes,
        load_nodes,
        material,
    )
    unit_nodal_u = nodal_displacements(basis, solution, mesh.nvertices)
    mean_disp = float(abs(unit_nodal_u[load_nodes, 2].mean()))
    if mean_disp <= 0.0:
        raise RuntimeError("Unexpected non-positive hook compliance.")

    max_principal, min_principal, von_mises = element_strains(
        mesh,
        unit_nodal_u,
    )
    max_principal_per_n = float(max_principal.max())
    max_vm_per_n = float(von_mises.max())
    proxy_low = material.yield_strain_low / 3.0
    proxy_high = material.yield_strain_high / 3.0

    force_proxy_low = proxy_low / max_principal_per_n
    force_proxy_high = proxy_high / max_principal_per_n
    force_yield_low = material.yield_strain_low / max_principal_per_n
    force_yield_high = material.yield_strain_high / max_principal_per_n

    if vtk_path is not None:
        write_vtk(
            vtk_path,
            mesh,
            unit_nodal_u,
            max_principal,
            min_principal,
            von_mises,
        )

    return HookResult(
        version=geom.version,
        hook_nose_outboard_mm=geom.hook_nose_outboard,
        effective_wall_capture_mm=geom.effective_wall_capture,
        pocket_outer_clearance_mm=geom.pocket_outer_clearance,
        receiver_ledge_depth_mm=geom.receiver_ledge_depth,
        minimum_shift_to_unhook_mm=geom.minimum_shift_to_unhook,
        top_stem_throat_mm=geom.top_stem_throat,
        top_stem_area_mm2=geom.top_stem_area,
        nose_slope_angle_deg=geom.nose_slope_angle_deg,
        mesh_size_mm=geom.mesh_size,
        nodes=mesh.nvertices,
        tetrahedra=mesh.nelements,
        clamp_nodes=len(clamp_nodes),
        load_nodes=len(load_nodes),
        load_face_mean_compliance_mm_per_n=mean_disp,
        vertical_stiffness_n_per_mm=1.0 / mean_disp,
        max_principal_strain_per_n=max_principal_per_n,
        max_von_mises_strain_per_n=max_vm_per_n,
        force_at_pa12_proxy_low_n=force_proxy_low,
        force_at_pa12_proxy_high_n=force_proxy_high,
        force_at_yield_low_n=force_yield_low,
        force_at_yield_high_n=force_yield_high,
        assessment=assess(geom, force_proxy_low),
    )


def print_report(result: HookResult) -> None:
    print("Passive hook hold check")
    print(f"Version:                   {result.version}")
    print("Model scope:               centered passive hook rail, linear elastic")
    print("Root assumption:           top hook stem clamped by lid slab")
    print("Load assumption:           1 N downward retention load on lower nose patch")
    print(f"Hook outboard nose:        {result.hook_nose_outboard_mm:.2f} mm")
    print(
        "Effective wall capture:    "
        f"{result.effective_wall_capture_mm:.2f} mm"
    )
    print(
        "Pocket outer clearance:    "
        f"{result.pocket_outer_clearance_mm:.2f} mm"
    )
    print(
        "Receiver ledge depth:      "
        f"{result.receiver_ledge_depth_mm:.2f} mm"
    )
    print(
        "Minimum +X shift to unhook:"
        f" {result.minimum_shift_to_unhook_mm:.2f} mm"
    )
    print(f"Top stem throat:           {result.top_stem_throat_mm:.2f} mm")
    print(f"Top stem area:             {result.top_stem_area_mm2:.1f} mm²")
    print(f"Nose slope angle:          {result.nose_slope_angle_deg:.1f} deg")
    print(f"Mesh size target:          {result.mesh_size_mm:.2f} mm")
    print(f"Mesh nodes / tetrahedra:   {result.nodes} / {result.tetrahedra}")
    print(f"Clamp nodes / load nodes:  {result.clamp_nodes} / {result.load_nodes}")
    print(
        "Nose compliance:           "
        f"{result.load_face_mean_compliance_mm_per_n:.6f} mm/N"
    )
    print(
        "Vertical stiffness:        "
        f"{result.vertical_stiffness_n_per_mm:.0f} N/mm"
    )
    print(
        "PA12 1/3-yield force:      "
        f"{result.force_at_pa12_proxy_low_n:.0f} … "
        f"{result.force_at_pa12_proxy_high_n:.0f} N"
    )
    print(
        "PA12 yield-strain force:   "
        f"{result.force_at_yield_low_n:.0f} … "
        f"{result.force_at_yield_high_n:.0f} N"
    )
    print(f"Assessment:                {result.assessment}")


def json_ready(result: HookResult) -> dict[str, object]:
    out: dict[str, object] = {}
    for key, value in asdict(result).items():
        if isinstance(value, np.integer):
            out[key] = int(value)
        elif isinstance(value, np.floating):
            out[key] = float(value)
        else:
            out[key] = value
    return out


def main() -> int:
    args = build_parser().parse_args()
    geom = HookGeometry(
        hook_nose_outboard=args.hook_nose_outboard,
        hook_rail_depth=args.hook_rail_depth,
        mesh_size=args.mesh_size,
    )
    material = Pa12Material()
    result = analyze(geom, material, args.vtk)
    print_report(result)

    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(json_ready(result), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
