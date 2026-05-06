#!/usr/bin/env python3
"""Rigid assembly-contact model for lid vs. trough, version 1.1.6.

Scope:
- full lid mesh against full trough mesh
- rigid-body motion only
- contact/clearance evaluated with signed distances into trough material
- search for a plausible "hook first, then rotate down" assembly family

This is intentionally not a nonlinear deformable contact FE solve. The goal is
to answer the practical question: does the current geometry admit a plausible
tilted insertion/hooking motion without unexpected hard interference?
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import cast

import numpy as np
import trimesh
from trimesh.proximity import signed_distance


@dataclass(frozen=True)
class Geometry:
    version: str = "1.1.6"
    size_x: float = 65.0
    size_y: float = 95.0
    size_z: float = 40.0
    wall: float = 2.2
    lid_thk: float = 2.5
    hook_rail_capture: float = 1.1
    hook_rail_depth: float = 2.1
    hook_nose_outboard: float = 0.35
    hook_rail_drop: float = 3.0
    hook_rail_nose_height: float = 0.9
    hook_tip_cham: float = 0.2
    hook_slot_depth: float = 1.35
    hook_slot_lead_depth: float = 0.55
    hook_slot_floor_clearance: float = 0.4
    hook_slot_roof_clearance: float = 0.35
    hook_protr: float = 1.1
    passive_corner_relief_x: float = 0.0
    passive_corner_relief_y: float = 0.0
    retainer_y_offset: float = 18.0

    @property
    def cavity_x(self) -> float:
        return self.size_x - 2.0 * self.wall

    @property
    def cavity_y(self) -> float:
        return self.size_y - 2.0 * self.wall

    @property
    def lid_x(self) -> float:
        return self.cavity_x + 2.0 - 0.6

    @property
    def arm_top_z(self) -> float:
        return self.size_z - self.lid_thk

    @property
    def hook_pivot(self) -> np.ndarray:
        # Approximate passive contact line near the upper rear point of the
        # simple hook nose, used as the kinematic hinge for hook-first closing.
        return np.array(
            [
                -self.lid_x / 2.0 + self.hook_rail_capture,
                0.0,
                self.arm_top_z - self.hook_rail_drop + self.hook_rail_nose_height,
            ],
            dtype=float,
        )

    @property
    def hook_nose_bottom_z(self) -> float:
        return self.arm_top_z - self.hook_rail_drop

    @property
    def hook_nose_top_z(self) -> float:
        return self.hook_nose_bottom_z + self.hook_rail_nose_height

    @property
    def hook_slot_bottom_z(self) -> float:
        return self.hook_nose_bottom_z - self.hook_slot_floor_clearance

    @property
    def hook_slot_roof_z(self) -> float:
        return self.hook_nose_top_z + self.hook_slot_roof_clearance

    @property
    def hook_slot_full_h(self) -> float:
        return self.hook_slot_roof_z - self.hook_slot_bottom_z

    @property
    def hook_slot_full_center_z(self) -> float:
        return (self.hook_slot_roof_z + self.hook_slot_bottom_z) / 2.0

    @property
    def hook_slot_lead_h(self) -> float:
        return self.arm_top_z - self.hook_slot_roof_z

    @property
    def hook_slot_lead_center_z(self) -> float:
        return (self.arm_top_z + self.hook_slot_roof_z) / 2.0


@dataclass(frozen=True)
class PoseCheck:
    angle_deg: float
    dx_mm: float
    dz_mm: float
    max_penetration_mm: float
    penetrating_points: int
    plus_edge_lift_mm: float
    feasible: bool


@dataclass(frozen=True)
class PathCheck:
    start_angle_deg: float
    start_dx_mm: float
    start_dz_mm: float
    end_dz_mm: float
    max_penetration_mm: float
    penetrating_points: int
    hard_max_penetration_mm: float
    hard_penetrating_points: int
    snap_max_interference_mm: float
    feasible: bool


@dataclass(frozen=True)
class AssemblyResult:
    version: str
    critical_points: int
    penetration_tol_mm: float
    best_pose: PoseCheck
    closing_path: PathCheck
    vertical_entry_path: PathCheck
    tilt_insert_possible: bool
    summary: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rigid assembly-contact check for lid vs. trough."
    )
    parser.add_argument(
        "--lid",
        type=Path,
        default=Path("output/STL/lid.stl"),
        help="Path to lid STL.",
    )
    parser.add_argument(
        "--trough",
        type=Path,
        default=Path("output/STL/trough.stl"),
        help="Path to trough STL.",
    )
    parser.add_argument(
        "--json",
        type=Path,
        help="Optional JSON output path.",
    )
    parser.add_argument(
        "--penetration-tol",
        type=float,
        default=0.15,
        help="Allowed numerical contact tolerance in mm.",
    )
    return parser.parse_args()


def rotation_y(angle_deg: float) -> np.ndarray:
    theta = math.radians(angle_deg)
    c = math.cos(theta)
    s = math.sin(theta)
    return np.array(
        [
            [c, 0.0, s],
            [0.0, 1.0, 0.0],
            [-s, 0.0, c],
        ],
        dtype=float,
    )


def transformed_points(
    points: np.ndarray,
    pivot: np.ndarray,
    angle_deg: float,
    dx_mm: float,
    dz_mm: float,
) -> np.ndarray:
    rotated = (points - pivot) @ rotation_y(angle_deg).T + pivot
    rotated[:, 0] += dx_mm
    rotated[:, 2] += dz_mm
    return rotated


def transformed_mesh(
    mesh: trimesh.Trimesh,
    pivot: np.ndarray,
    angle_deg: float,
    dx_mm: float,
    dz_mm: float,
) -> trimesh.Trimesh:
    moved = mesh.copy()
    moved.apply_translation(-pivot)
    matrix = np.eye(4)
    matrix[:3, :3] = rotation_y(angle_deg)
    moved.apply_transform(matrix)
    moved.apply_translation(pivot + np.array([dx_mm, 0.0, dz_mm]))
    return moved


def select_critical_points(
    lid_mesh: trimesh.Trimesh,
    limit: int = 180,
) -> np.ndarray:
    verts = lid_mesh.vertices
    perimeter_or_feature = (
        (np.abs(verts[:, 0]) > 24.0)
        | (np.abs(verts[:, 1]) > 38.0)
        | (verts[:, 2] < 38.0)
        | (
            (verts[:, 0] > 26.5)
            & (np.abs(np.abs(verts[:, 1]) - 18.0) < 5.0)
        )
        | ((verts[:, 0] < -27.0) & (np.abs(verts[:, 1]) < 18.5))
    )
    points = verts[perimeter_or_feature]
    if len(points) > limit:
        indices = np.linspace(0, len(points) - 1, limit, dtype=int)
        points = points[indices]
    return points


def active_snap_mask(
    points: np.ndarray,
    geom: Geometry,
) -> np.ndarray:
    """Points belonging to the two active +X snap features.

    Those points are allowed to interfere during the final snap-down because
    the real design expects elastic deformation there.
    """
    near_snap_y = (
        (np.abs(points[:, 1] - geom.retainer_y_offset) < 5.0)
        | (np.abs(points[:, 1] + geom.retainer_y_offset) < 5.0)
    )
    return (
        (points[:, 0] > 26.5)
        & near_snap_y
        & (points[:, 2] < geom.arm_top_z + 0.2)
    )


def pose_penetration(
    trough_mesh: trimesh.Trimesh,
    points: np.ndarray,
    pivot: np.ndarray,
    angle_deg: float,
    dx_mm: float,
    dz_mm: float,
    penetration_tol_mm: float,
) -> PoseCheck:
    moved = transformed_points(points, pivot, angle_deg, dx_mm, dz_mm)
    distances = signed_distance(trough_mesh, moved)
    max_penetration = float(distances.max())
    penetrating = int(np.sum(distances > penetration_tol_mm))

    plus_side = moved[points[:, 0] > 20.0, 2].mean()
    minus_side = moved[points[:, 0] < -20.0, 2].mean()
    lift = float(plus_side - minus_side)

    return PoseCheck(
        angle_deg=angle_deg,
        dx_mm=dx_mm,
        dz_mm=dz_mm,
        max_penetration_mm=max_penetration,
        penetrating_points=penetrating,
        plus_edge_lift_mm=lift,
        feasible=penetrating == 0,
    )


def path_penetration(
    trough_mesh: trimesh.Trimesh,
    points: np.ndarray,
    pivot: np.ndarray,
    start_angle_deg: float,
    start_dx_mm: float,
    start_dz_mm: float,
    penetration_tol_mm: float,
    steps: int = 16,
    mode: str = "closing",
    end_dz_mm: float = 0.0,
    snap_mask: np.ndarray | None = None,
    allow_snap_interference: bool = False,
) -> PathCheck:
    worst_penetration = -1e9
    worst_points = 0
    worst_hard_penetration = -1e9
    worst_hard_points = 0
    worst_snap_interference = -1e9
    if snap_mask is None:
        snap_mask = np.zeros(len(points), dtype=bool)

    for step in range(steps + 1):
        t = step / steps
        if mode == "closing":
            angle = (1.0 - t) * start_angle_deg
            dx = (1.0 - t) * start_dx_mm
            dz = (1.0 - t) * start_dz_mm
        elif mode == "entry":
            angle = start_angle_deg
            dx = start_dx_mm
            dz = start_dz_mm + t * (end_dz_mm - start_dz_mm)
        else:  # pragma: no cover - guarded by caller
            raise ValueError(f"Unsupported mode: {mode}")

        moved = transformed_points(points, pivot, angle, dx, dz)
        distances = signed_distance(trough_mesh, moved)
        worst_penetration = max(worst_penetration, float(distances.max()))
        worst_points = max(
            worst_points,
            int(np.sum(distances > penetration_tol_mm)),
        )
        hard_distances = distances[~snap_mask]
        if len(hard_distances):
            worst_hard_penetration = max(
                worst_hard_penetration,
                float(hard_distances.max()),
            )
            worst_hard_points = max(
                worst_hard_points,
                int(np.sum(hard_distances > penetration_tol_mm)),
            )
        if np.any(snap_mask):
            worst_snap_interference = max(
                worst_snap_interference,
                float(distances[snap_mask].max()),
            )

    return PathCheck(
        start_angle_deg=start_angle_deg,
        start_dx_mm=start_dx_mm,
        start_dz_mm=start_dz_mm,
        end_dz_mm=end_dz_mm,
        max_penetration_mm=worst_penetration,
        penetrating_points=worst_points,
        hard_max_penetration_mm=worst_hard_penetration,
        hard_penetrating_points=worst_hard_points,
        snap_max_interference_mm=worst_snap_interference,
        feasible=(
            worst_hard_points == 0
            if allow_snap_interference
            else worst_points == 0
        ),
    )


def search_best_pose(
    trough_mesh: trimesh.Trimesh,
    points: np.ndarray,
    pivot: np.ndarray,
    penetration_tol_mm: float,
) -> PoseCheck:
    candidates: list[PoseCheck] = []
    for angle in (-30.0, -25.0, -20.0, -15.0, -10.0, -5.0):
        for dx in (-0.4, -0.2, 0.0, 0.2, 0.4):
            for dz in (0.0, 0.3, 0.6, 0.9, 1.2):
                candidates.append(
                    pose_penetration(
                        trough_mesh,
                        points,
                        pivot,
                        angle,
                        dx,
                        dz,
                        penetration_tol_mm,
                    )
                )

    candidates.sort(
        key=lambda item: (
            item.penetrating_points,
            round(item.max_penetration_mm, 5),
            abs(item.dx_mm) + 0.2 * abs(item.dz_mm),
            -abs(item.angle_deg),
        )
    )
    return candidates[0]


def analyze(
    lid_mesh: trimesh.Trimesh,
    trough_mesh: trimesh.Trimesh,
    geom: Geometry,
    penetration_tol_mm: float,
) -> AssemblyResult:
    critical = select_critical_points(lid_mesh)
    snap_points = active_snap_mask(critical, geom)
    best_pose = search_best_pose(
        trough_mesh,
        critical,
        geom.hook_pivot,
        penetration_tol_mm,
    )

    closing = path_penetration(
        trough_mesh,
        critical,
        geom.hook_pivot,
        best_pose.angle_deg,
        best_pose.dx_mm,
        best_pose.dz_mm,
        penetration_tol_mm,
        mode="closing",
        snap_mask=snap_points,
        allow_snap_interference=True,
    )

    vertical_entry = path_penetration(
        trough_mesh,
        critical,
        geom.hook_pivot,
        best_pose.angle_deg,
        best_pose.dx_mm,
        max(best_pose.dz_mm + 3.0, 4.0),
        penetration_tol_mm,
        mode="entry",
        end_dz_mm=best_pose.dz_mm,
    )

    tilt_insert_possible = best_pose.feasible and closing.feasible and vertical_entry.feasible
    if tilt_insert_possible:
        summary = (
            "A plausible hook-first assembly path was found: passive side hook "
            "engaged at a negative Y-rotation, then rotate down without "
            "unexpected hard interference."
        )
    else:
        summary = (
            "No fully collision-free tilted insertion path was found in the "
            "searched motion family. The current hook-first motion is likely "
            "very tolerance-sensitive or needs more assembly clearance."
        )

    return AssemblyResult(
        version=geom.version,
        critical_points=len(critical),
        penetration_tol_mm=penetration_tol_mm,
        best_pose=best_pose,
        closing_path=closing,
        vertical_entry_path=vertical_entry,
        tilt_insert_possible=tilt_insert_possible,
        summary=summary,
    )


def print_result(result: AssemblyResult) -> None:
    print("Lid / trough assembly contact")
    print(f"Version:                   {result.version}")
    print("Model scope:               full lid mesh vs full trough mesh")
    print(
        "Method:                    rigid-body signed-distance search around "
        "the passive hook line"
    )
    print(f"Critical sample points:    {result.critical_points}")
    print(
        "Penetration tolerance:     "
        f"{result.penetration_tol_mm:.2f} mm"
    )
    print("")
    print("Best hooked-open pose")
    print(
        f"  angle / dx / dz:         {result.best_pose.angle_deg:.1f} deg, "
        f"{result.best_pose.dx_mm:.2f} mm, {result.best_pose.dz_mm:.2f} mm"
    )
    print(
        "  +X edge lift:            "
        f"{result.best_pose.plus_edge_lift_mm:.2f} mm"
    )
    print(
        "  max penetration:         "
        f"{result.best_pose.max_penetration_mm:.3f} mm"
    )
    print(
        "  penetrating points:      "
        f"{result.best_pose.penetrating_points}"
    )
    print(f"  feasible:                {result.best_pose.feasible}")
    print("")
    print("Path checks")
    print(
        "  hooked-open -> closed:   "
        f"{result.closing_path.feasible} "
        f"(hard {result.closing_path.hard_max_penetration_mm:.3f} mm, "
        f"hard points {result.closing_path.hard_penetrating_points}, "
        f"snap {result.closing_path.snap_max_interference_mm:.3f} mm)"
    )
    print(
        "  vertical entry at tilt:  "
        f"{result.vertical_entry_path.feasible} "
        f"(hard {result.vertical_entry_path.hard_max_penetration_mm:.3f} mm, "
        f"hard points {result.vertical_entry_path.hard_penetrating_points})"
    )
    print("")
    print(f"Tilt insert possible:      {result.tilt_insert_possible}")
    print(f"Assessment:                {result.summary}")


def json_ready(result: AssemblyResult) -> dict[str, object]:
    def convert(value: object) -> object:
        if isinstance(value, np.integer):
            return int(value)
        if isinstance(value, np.floating):
            return float(value)
        if isinstance(value, dict):
            return {k: convert(v) for k, v in value.items()}
        if isinstance(value, list):
            return [convert(v) for v in value]
        return value

    return cast(dict[str, object], convert(asdict(result)))


def main() -> int:
    args = parse_args()
    print("Loading lid/trough meshes...", flush=True)
    lid_mesh = trimesh.load_mesh(args.lid, force="mesh")
    trough_mesh = trimesh.load_mesh(args.trough, force="mesh")
    geom = Geometry()
    print("Running signed-distance assembly contact search...", flush=True)
    result = analyze(
        lid_mesh=lid_mesh,
        trough_mesh=trough_mesh,
        geom=geom,
        penetration_tol_mm=args.penetration_tol,
    )
    print_result(result)

    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(json_ready(result), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
