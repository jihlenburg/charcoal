#!/usr/bin/env python3
"""Local linear-elastic FEM for the v1.1.0 snap tab.

This is intentionally a focused Phase-1 model:

- one active snap tab only
- current v1.1.0 nose geometry
- 3D tetra mesh generated with Gmsh
- solved with scikit-fem as small-strain linear elasticity
- load applied on the real catch face, not at the absolute tip

The goal is not a full contact simulation of lid + trough. It is a fast,
reproducible local compliance and strain check for PA12 MJF.
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
        "  pip install gmsh meshio scikit-fem"
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
        "  pip install gmsh meshio scikit-fem"
    ) from exc


@dataclass(frozen=True)
class SnapGeometry:
    version: str = "1.1.0"
    hook_width: float = 6.0
    hook_arm: float = 1.0
    hook_length: float = 10.2
    hook_protr: float = 1.0
    hook_lead: float = 1.5
    hook_hold: float = 0.4
    hook_release: float = 2.8
    fit_clear: float = 0.30
    mesh_size: float = 0.25

    @property
    def opening_deflection(self) -> float:
        return self.hook_protr + self.fit_clear

    @property
    def catch_z_min(self) -> float:
        return -self.hook_length + self.hook_lead

    @property
    def catch_z_max(self) -> float:
        return -self.hook_length + self.hook_lead + self.hook_hold


@dataclass(frozen=True)
class Pa12Material:
    modulus_nominal: float = 2150.0
    modulus_low: float = 1650.0
    modulus_high: float = 2200.0
    poisson: float = 0.40
    yield_strain_low: float = 0.09
    yield_strain_high: float = 0.11
    release_mu: float = 0.20


@dataclass(frozen=True)
class FemResult:
    version: str
    mesh_size: float
    nodes: int
    tetrahedra: int
    clamp_nodes: int
    load_nodes: int
    load_face_mean_disp_mm_per_n: float
    lateral_stiffness_nominal_n_per_mm: float
    lateral_stiffness_low_n_per_mm: float
    lateral_stiffness_high_n_per_mm: float
    opening_deflection_mm: float
    lateral_force_per_tab_nominal_n: float
    lateral_force_per_tab_low_n: float
    lateral_force_per_tab_high_n: float
    lift_open_force_total_nominal_n: float
    lift_open_force_total_low_n: float
    lift_open_force_total_high_n: float
    max_principal_strain: float
    min_principal_strain: float
    max_von_mises_strain: float
    pa12_proxy_target_low: float
    pa12_proxy_target_high: float
    assessment_tool_free: str
    assessment_repeatable: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Local FEM for the v1.1.0 PA12 snap tab."
    )
    parser.add_argument(
        "--mesh-size",
        type=float,
        default=SnapGeometry.mesh_size,
        help="Target tetra edge length in mm (default: %(default)s).",
    )
    parser.add_argument(
        "--vtk",
        type=Path,
        help="Optional .vtu output with the deformed displacement field.",
    )
    parser.add_argument(
        "--json",
        type=Path,
        help="Optional JSON summary output path.",
    )
    return parser


def build_local_snap_mesh(geom: SnapGeometry, mesh_path: Path) -> None:
    """Build a simple local 3D snap model and write it as Gmsh .msh."""

    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.add("snap_fit_v110")
        occ = gmsh.model.occ

        points = [
            (-geom.hook_arm, 0.0),
            (-geom.hook_arm, -geom.hook_length),
            (0.0, -geom.hook_length),
            (geom.hook_protr, geom.catch_z_min),
            (geom.hook_protr, geom.catch_z_max),
            (0.0, -geom.hook_length + geom.hook_lead + geom.hook_hold
             + geom.hook_release),
            (0.0, 0.0),
        ]
        tags = [occ.addPoint(x, 0.0, z) for x, z in points]
        edges = [occ.addLine(a, b) for a, b in zip(tags, tags[1:])]
        edges.append(occ.addLine(tags[-1], tags[0]))
        loop = occ.addCurveLoop(edges)
        face = occ.addPlaneSurface([loop])
        occ.extrude([(2, face)], 0.0, geom.hook_width, 0.0)
        occ.synchronize()

        gmsh.option.setNumber(
            "Mesh.CharacteristicLengthMin", geom.mesh_size
        )
        gmsh.option.setNumber(
            "Mesh.CharacteristicLengthMax", geom.mesh_size
        )
        gmsh.model.mesh.generate(3)
        gmsh.write(str(mesh_path))
    finally:
        gmsh.finalize()


def identify_node_sets(
    mesh: MeshTet,
    geom: SnapGeometry,
) -> tuple[np.ndarray, np.ndarray]:
    """Return root-clamp nodes and load-face nodes."""

    xyz = mesh.p.T
    x = xyz[:, 0]
    z = xyz[:, 2]
    tol = max(1e-6, 0.35 * geom.mesh_size)

    clamp = np.flatnonzero(
        (np.abs(z) <= tol)
        & (x >= -geom.hook_arm - tol)
        & (x <= tol)
    )
    load = np.flatnonzero(
        (np.abs(x - geom.hook_protr) <= tol)
        & (z >= geom.catch_z_min - tol)
        & (z <= geom.catch_z_max + tol)
    )

    if len(clamp) == 0:
        raise RuntimeError("No clamp nodes found on the snap root plane.")
    if len(load) == 0:
        raise RuntimeError("No load nodes found on the catch face.")
    return clamp, load


def solve_unit_force(
    mesh: MeshTet,
    clamp_nodes: np.ndarray,
    load_nodes: np.ndarray,
    modulus: float,
    poisson: float,
) -> tuple[Basis, np.ndarray]:
    """Solve one load case with 1 N total lateral load in +X."""

    element = ElementVector(ElementTetP1())
    basis = Basis(mesh, element)
    lame_lambda, lame_mu = lame_parameters(modulus, poisson)
    stiffness = asm(linear_elasticity(lame_lambda, lame_mu), basis)

    rhs = np.zeros(stiffness.shape[0])
    rhs[basis.nodal_dofs[0, load_nodes]] = 1.0 / len(load_nodes)
    constrained = basis.get_dofs(nodes=clamp_nodes).all()
    solution = solve(*condense(stiffness, rhs, D=constrained))
    return basis, solution


def nodal_displacements(
    basis: Basis,
    solution: np.ndarray,
    nvertices: int,
) -> np.ndarray:
    """Convert scikit-fem's flattened solution into nvertices x 3."""

    disp = np.zeros((nvertices, 3))
    disp[:, 0] = solution[basis.nodal_dofs[0]]
    disp[:, 1] = solution[basis.nodal_dofs[1]]
    disp[:, 2] = solution[basis.nodal_dofs[2]]
    return disp


def element_strains(
    mesh: MeshTet,
    nodal_u: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return max principal, min principal, and von-Mises-like strain per tet."""

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


def assess_tool_free(total_lift_force_high: float) -> str:
    if total_lift_force_high <= 10.0:
        return "plausible"
    if total_lift_force_high <= 15.0:
        return "plausible, but not especially light"
    return "questionable without geometry changes"


def assess_repeatability(
    max_principal_strain: float,
    proxy_low: float,
    proxy_high: float,
) -> str:
    if max_principal_strain <= proxy_low:
        return "inside conservative HP proxy band"
    if max_principal_strain <= proxy_high:
        return "inside HP proxy band, but only with modest reserve"
    return "outside HP proxy band"


def analyze(
    geom: SnapGeometry,
    material: Pa12Material,
    vtk_path: Path | None,
) -> FemResult:
    with tempfile.TemporaryDirectory() as tmpdir:
        mesh_path = Path(tmpdir) / "snap_fit_v110.msh"
        build_local_snap_mesh(geom, mesh_path)
        mesh = MeshTet.load(str(mesh_path))

    clamp_nodes, load_nodes = identify_node_sets(mesh, geom)
    basis, solution = solve_unit_force(
        mesh,
        clamp_nodes,
        load_nodes,
        material.modulus_nominal,
        material.poisson,
    )

    unit_nodal_u = nodal_displacements(basis, solution, mesh.nvertices)
    load_face_disp = unit_nodal_u[load_nodes, 0].mean()
    if load_face_disp <= 0.0:
        raise RuntimeError("Unexpected non-positive load-face displacement.")

    stiffness_nominal = 1.0 / load_face_disp
    scale_to_opening = geom.opening_deflection / load_face_disp
    nodal_u_open = unit_nodal_u * scale_to_opening

    max_principal, min_principal, von_mises = element_strains(
        mesh,
        nodal_u_open,
    )

    stiffness_low = (
        stiffness_nominal
        * material.modulus_low
        / material.modulus_nominal
    )
    stiffness_high = (
        stiffness_nominal
        * material.modulus_high
        / material.modulus_nominal
    )

    lateral_force_nominal = stiffness_nominal * geom.opening_deflection
    lateral_force_low = stiffness_low * geom.opening_deflection
    lateral_force_high = stiffness_high * geom.opening_deflection

    release_ratio = geom.hook_protr / geom.hook_release
    lift_factor = (
        (release_ratio + material.release_mu)
        / (1.0 - material.release_mu * release_ratio)
    )
    total_lift_nominal = 2.0 * stiffness_nominal * geom.hook_protr * lift_factor
    total_lift_low = 2.0 * stiffness_low * geom.hook_protr * lift_factor
    total_lift_high = 2.0 * stiffness_high * geom.hook_protr * lift_factor

    proxy_low = material.yield_strain_low / 3.0
    proxy_high = material.yield_strain_high / 3.0

    if vtk_path is not None:
        write_vtk(
            vtk_path,
            mesh,
            nodal_u_open,
            max_principal,
            min_principal,
            von_mises,
        )

    return FemResult(
        version=geom.version,
        mesh_size=geom.mesh_size,
        nodes=mesh.nvertices,
        tetrahedra=mesh.nelements,
        clamp_nodes=len(clamp_nodes),
        load_nodes=len(load_nodes),
        load_face_mean_disp_mm_per_n=load_face_disp,
        lateral_stiffness_nominal_n_per_mm=stiffness_nominal,
        lateral_stiffness_low_n_per_mm=stiffness_low,
        lateral_stiffness_high_n_per_mm=stiffness_high,
        opening_deflection_mm=geom.opening_deflection,
        lateral_force_per_tab_nominal_n=lateral_force_nominal,
        lateral_force_per_tab_low_n=lateral_force_low,
        lateral_force_per_tab_high_n=lateral_force_high,
        lift_open_force_total_nominal_n=total_lift_nominal,
        lift_open_force_total_low_n=total_lift_low,
        lift_open_force_total_high_n=total_lift_high,
        max_principal_strain=float(max_principal.max()),
        min_principal_strain=float(min_principal.min()),
        max_von_mises_strain=float(von_mises.max()),
        pa12_proxy_target_low=proxy_low,
        pa12_proxy_target_high=proxy_high,
        assessment_tool_free=assess_tool_free(total_lift_high),
        assessment_repeatable=assess_repeatability(
            float(max_principal.max()),
            proxy_low,
            proxy_high,
        ),
    )


def print_report(result: FemResult) -> None:
    print("Local snap FEM")
    print(f"Version:                   {result.version}")
    print("Model scope:               1 active snap tab, linear elastic, no contact")
    print("Root assumption:           snap root clamped at the lid attach plane")
    print(f"Mesh size target:          {result.mesh_size:.2f} mm")
    print(f"Mesh nodes / tetrahedra:   {result.nodes} / {result.tetrahedra}")
    print(f"Clamp nodes / load nodes:  {result.clamp_nodes} / {result.load_nodes}")
    print(
        "Load-face mean compliance: "
        f"{result.load_face_mean_disp_mm_per_n:.4f} mm/N"
    )
    print(
        "Lateral stiffness per tab: "
        f"{result.lateral_stiffness_nominal_n_per_mm:.2f} N/mm "
        f"({result.lateral_stiffness_low_n_per_mm:.2f} … "
        f"{result.lateral_stiffness_high_n_per_mm:.2f} N/mm)"
    )
    print(
        "Opening deflection target: "
        f"{result.opening_deflection_mm:.2f} mm"
    )
    print(
        "Lateral force per tab:     "
        f"{result.lateral_force_per_tab_nominal_n:.2f} N "
        f"({result.lateral_force_per_tab_low_n:.2f} … "
        f"{result.lateral_force_per_tab_high_n:.2f} N)"
    )
    print(
        "Lift-open force total:     "
        f"{result.lift_open_force_total_nominal_n:.2f} N "
        f"({result.lift_open_force_total_low_n:.2f} … "
        f"{result.lift_open_force_total_high_n:.2f} N, 2 tabs)"
    )
    print(
        "Max principal strain:      "
        f"{result.max_principal_strain * 100:.2f} %"
    )
    print(
        "Max von-Mises strain:      "
        f"{result.max_von_mises_strain * 100:.2f} %"
    )
    print(
        "PA12 1/3-yield proxy:      "
        f"<{result.pa12_proxy_target_low * 100:.2f} … "
        f"{result.pa12_proxy_target_high * 100:.2f} %"
    )
    print(f"Tool-free opening:         {result.assessment_tool_free}")
    print(f"Repeated opening:          {result.assessment_repeatable}")
    print(
        "Note:                     This model resolves the real catch face and "
        "is therefore more conservative than the simple cantilever formula. "
        "The actual v1.1.0 arm-root fillet is not modeled explicitly here."
    )


def json_ready_dict(result: FemResult) -> dict[str, object]:
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
    geom = SnapGeometry(mesh_size=args.mesh_size)
    material = Pa12Material()

    result = analyze(geom, material, args.vtk)
    print_report(result)

    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(
                json_ready_dict(result),
                indent=2,
                sort_keys=True,
            ) + "\n",
            encoding="utf-8",
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
