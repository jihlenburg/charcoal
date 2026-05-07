#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""FEM regression check.

Compares each current FEM-solver output (output/FEM/<solver>_v*.json) against
a committed baseline (output/FEM/baseline/<solver>.json) on a curated set of
fields with per-field tolerances. Baselines use unversioned filenames so
version bumps do not orphan them; promote a new release with
`./run fem-diff --update-baseline`.

Tolerances are deliberately loose by default (±15 % relative for measured
floats) because PA12 modulus uncertainty is already ±15 % at the materials
level — tighter would false-alarm on benign numerical noise. Where physics
demands exactness (penetration counts, feasibility flags, integer point
counts), the field is checked with mode "exact".

Run:
    ./run fem-diff
    ./run fem-diff --update-baseline   # accept current as new baseline
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
FEM_DIR = ROOT / "output" / "FEM"
BASELINE_DIR = FEM_DIR / "baseline"


# Each solver: either {"fields": [(field, mode, tol), ...]} for a flat-dict
# JSON, or {"list_index_by": <key>, "entries": {<key_value>: [(field, mode,
# tol), ...]}} for a list-of-dicts JSON.
#
# Modes:
#   "rel"    abs(cur-base)/abs(base) <= tol
#   "abs"    abs(cur-base) <= tol
#   "exact"  cur == base   (tol ignored)
#
# Field paths use dot notation for nested dicts (e.g., "best_pose.dx_mm").
SOLVERS: dict[str, dict] = {
    "snap_fit": {
        "fields": [
            ("lift_open_force_total_nominal_n",       "rel", 0.15),
            ("lateral_force_per_tab_nominal_n",       "rel", 0.15),
            ("lateral_stiffness_nominal_n_per_mm",    "rel", 0.15),
            ("max_principal_strain",                  "rel", 0.15),
        ],
    },
    "hook_hold": {
        "fields": [
            ("force_at_pa12_proxy_low_n",             "rel", 0.15),
            ("force_at_pa12_proxy_high_n",            "rel", 0.15),
            ("vertical_stiffness_n_per_mm",           "rel", 0.15),
            ("effective_wall_capture_mm",             "abs", 0.05),
            ("pocket_outer_clearance_mm",             "abs", 0.05),
        ],
    },
    "trough_bulge": {
        "list_index_by": "variant",
        "entries": {
            "plain": [
                ("max_outer_bulge_mm",                "rel", 0.20),
                ("pressure_for_1_0mm_bulge_kpa",      "rel", 0.20),
            ],
            "current": [
                ("max_outer_bulge_mm",                "rel", 0.20),
                ("pressure_for_1_0mm_bulge_kpa",      "rel", 0.20),
            ],
        },
    },
    "lid_trough_assembly": {
        "fields": [
            ("best_pose.feasible",                    "exact", None),
            ("best_pose.angle_deg",                   "abs",   5.0),
            ("best_pose.dx_mm",                       "abs",   0.2),
            ("best_pose.dz_mm",                       "abs",   0.2),
            ("best_pose.max_penetration_mm",          "abs",   0.05),
            ("best_pose.penetrating_points",          "exact", None),
            ("vertical_entry_path.feasible",          "exact", None),
            ("vertical_entry_path.hard_penetrating_points", "exact", None),
            ("closing_path.hard_penetrating_points",  "exact", None),
        ],
    },
}


def get_path(d: Any, dotted: str) -> Any:
    for key in dotted.split("."):
        d = d[key]
    return d


def find_current(solver_name: str) -> Path | None:
    """Find the most recent versioned output for this solver."""
    candidates = sorted(FEM_DIR.glob(f"{solver_name}_v*.json"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def compare(base: Any, cur: Any, mode: str, tol: Any) -> tuple[bool, str]:
    if mode == "exact":
        ok = base == cur
        return ok, f"baseline={base!r}, current={cur!r}"
    base_f = float(base)
    cur_f = float(cur)
    if mode == "rel":
        if base_f == 0.0:
            ok = cur_f == 0.0
            return ok, f"baseline=0, current={cur_f:.4g}"
        delta_rel = (cur_f - base_f) / abs(base_f)
        ok = abs(delta_rel) <= tol
        return ok, (f"baseline={base_f:.4g}, current={cur_f:.4g}, "
                    f"Δrel={delta_rel:+.2%} (tol ±{tol:.0%})")
    if mode == "abs":
        delta = cur_f - base_f
        ok = abs(delta) <= tol
        return ok, (f"baseline={base_f:.4g}, current={cur_f:.4g}, "
                    f"Δabs={delta:+.4g} (tol ±{tol:g})")
    raise ValueError(f"unknown mode {mode!r}")


def diff_solver(solver_name: str, spec: dict, current_path: Path,
                baseline_path: Path) -> list[tuple[str, str, bool]]:
    cur = json.loads(current_path.read_text())
    base = json.loads(baseline_path.read_text())
    results: list[tuple[str, str, bool]] = []

    if "list_index_by" in spec:
        key_field = spec["list_index_by"]
        cur_by = {e[key_field]: e for e in cur}
        base_by = {e[key_field]: e for e in base}
        for entry_key, fields in spec["entries"].items():
            if entry_key not in cur_by:
                results.append((f"{solver_name}[{entry_key}]",
                                f"entry missing in current run", False))
                continue
            if entry_key not in base_by:
                results.append((f"{solver_name}[{entry_key}]",
                                f"entry missing in baseline", False))
                continue
            for field, mode, tol in fields:
                label = f"{solver_name}[{entry_key}].{field}"
                try:
                    cv = get_path(cur_by[entry_key], field)
                    bv = get_path(base_by[entry_key], field)
                except KeyError as e:
                    results.append((label, f"missing key {e}", False))
                    continue
                ok, msg = compare(bv, cv, mode, tol)
                results.append((label, msg, ok))
        return results

    for field, mode, tol in spec["fields"]:
        label = f"{solver_name}.{field}"
        try:
            cv = get_path(cur, field)
            bv = get_path(base, field)
        except KeyError as e:
            results.append((label, f"missing key {e}", False))
            continue
        ok, msg = compare(bv, cv, mode, tol)
        results.append((label, msg, ok))
    return results


def update_baseline() -> int:
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    promoted: list[str] = []
    missing: list[str] = []
    for solver in SOLVERS:
        cur = find_current(solver)
        if cur is None:
            missing.append(solver)
            continue
        dst = BASELINE_DIR / f"{solver}.json"
        shutil.copy2(cur, dst)
        promoted.append(f"{cur.name} → baseline/{dst.name}")
    if promoted:
        print("Promoted to baseline:")
        for line in promoted:
            print(f"  {line}")
    if missing:
        print("\nNo current output for:")
        for s in missing:
            print(f"  {s}  (run the corresponding ./run fem-* command first)")
    return 0 if promoted and not missing else (1 if missing else 0)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--update-baseline", action="store_true",
        help=("Copy current versioned outputs into output/FEM/baseline/ as "
              "the new reference. Use after deliberately accepting a result "
              "change (geometry edit, solver tuning, mesh refinement)."),
    )
    args = ap.parse_args()

    if args.update_baseline:
        return update_baseline()

    if not BASELINE_DIR.exists():
        print(f"FATAL: no baseline directory at {BASELINE_DIR.relative_to(ROOT)}",
              file=sys.stderr)
        print("Bootstrap: ./run fem-diff --update-baseline", file=sys.stderr)
        return 2

    print(f"FEM baseline diff (baseline: {BASELINE_DIR.relative_to(ROOT)})\n")
    all_results: list[tuple[str, str, bool]] = []
    for solver, spec in SOLVERS.items():
        cur = find_current(solver)
        baseline = BASELINE_DIR / f"{solver}.json"
        if cur is None:
            all_results.append((solver, "no current run output found", False))
            continue
        if not baseline.exists():
            all_results.append((solver, f"no baseline at {baseline.name}", False))
            continue
        all_results.extend(diff_solver(solver, spec, cur, baseline))

    failures = [r for r in all_results if not r[2]]
    passes = [r for r in all_results if r[2]]

    for label, msg, ok in all_results:
        marker = "✓" if ok else "✗"
        print(f"  {marker} {label}\n      {msg}")

    print()
    if failures:
        print(f"FAIL: {len(failures)} field(s) outside threshold "
              f"({len(passes)} OK)")
        print("\nIf the change is intentional, accept it with:")
        print("    ./run fem-diff --update-baseline")
        return 1
    print(f"OK: {len(passes)} fields within threshold.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
