#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Verify README.md is in sync with carbon_filter_build123d.py constants.

The CAD script is the source of truth for VERSION and geometry. The README
quotes those values in prose, tables, image filenames and FEM-output paths.
Without this checker the sync is a manual rule in CLAUDE.md — easy to miss
in a hot fix and the cost of a desync is a physically wrong part.

The checker AST-parses module-level assignments from the script, then for
each registered parameter searches README.md for one or more required
regex patterns built from the current value. A miss is a hard failure.

Run:
    ./run check
"""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "carbon_filter_build123d.py"
README = ROOT / "README.md"


def parse_constants(path: Path) -> dict[str, object]:
    """Return {name: value} for module-level Name = literal assignments.

    Also resolves single-name aliases like `lid_thk = rabbet_depth` against
    already-parsed constants, in source order — sufficient for the script's
    parameter block.
    """
    tree = ast.parse(path.read_text())
    out: dict[str, object] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        tgt = node.targets[0]
        if not isinstance(tgt, ast.Name):
            continue
        try:
            out[tgt.id] = ast.literal_eval(node.value)
            continue
        except ValueError:
            pass
        if isinstance(node.value, ast.Name) and node.value.id in out:
            out[tgt.id] = out[node.value.id]
    return out


def fmt_num(v: object) -> str:
    """Render a number as it appears in the German README prose."""
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    if isinstance(v, float):
        return f"{v:g}"
    return str(v)


def lit(template: str) -> Callable[[object], str]:
    """Pattern builder. Substitutions:

      <V>     regex-escaped formatted value. For float values an optional
              ".0" suffix (integer-valued floats) or a trailing "0" digit
              (one-decimal floats) is permitted, so the README may quote
              `2.2`, `2.20`, `1.0`, or `1` interchangeably with the script.
      space   matches any whitespace run including soft-wrap newlines, so
              line-wrapped German prose like `1.1 mm\\n  Lippenüberstand`
              is matched by the natural template `<V> mm Lippenüberstand`.
    """
    def build(value: object) -> str:
        v_str = re.escape(fmt_num(value))
        if isinstance(value, float):
            if value.is_integer():
                v_str = v_str + r"(?:\.0)?"
            elif "." in fmt_num(value):
                v_str = v_str + r"0?"
        pat = template.replace("<V>", v_str)
        pat = re.sub(r" ", r"\\s+", pat)
        return pat
    return build


def version_underscored(value: object) -> str:
    """Version "1.1.6" → "1_1_6" for embedded filenames."""
    assert isinstance(value, str)
    return re.escape(value.replace(".", "_"))


@dataclass
class Check:
    name: str                            # parameter name in the script
    build_pattern: Callable[[object], str]
    description: str                     # human label for output


CHECKS: list[Check] = [
    # ---- VERSION ----------------------------------------------------------
    Check("VERSION", lit(r"\*\*Version: <V>\*\*"), "README version header"),
    Check(
        "VERSION",
        lambda v: rf"v{version_underscored(v)}_render",
        "rendered hero-image filename",
    ),
    Check(
        "VERSION",
        lambda v: rf"v{version_underscored(v)}\.svg",
        "assembly SVG filename",
    ),
    Check(
        "VERSION",
        lambda v: rf"v{version_underscored(v)}\.json",
        "FEM JSON filename",
    ),

    # ---- Outer envelope ---------------------------------------------------
    Check("size_x", lit(r"<V> \(X\)"), "body X dimension"),
    Check("size_y", lit(r"<V> \(Y\)"), "body Y dimension"),
    Check("size_z", lit(r"<V> \(Z\)"), "body Z dimension"),
    Check("flange_extra_y", lit(r"je <V> mm Überstand"), "flange Y overhang"),

    # ---- Shell ------------------------------------------------------------
    Check("wall", lit(r"Wand <V> mm"), "wall thickness"),
    Check("floor", lit(r"Boden <V> mm"), "floor thickness"),
    Check("lid_thk", lit(r"Deckel <V> mm"), "lid thickness"),
    Check("fit_clear", lit(r"<V> mm pro Seite"), "fit clearance"),

    # ---- Hex perforation --------------------------------------------------
    Check("hex_flats", lit(r"<V> mm flat-to-flat"), "hex flats"),
    Check("hex_web", lit(r"<V> mm Stegbreite"), "hex web"),
    Check("hex_margin_x", lit(r"<V> mm X-Randabstand"), "hex X margin"),
    Check("hex_margin_y", lit(r"<V> mm Y-Randabstand"), "hex Y margin"),

    # ---- Anti-bulge bars --------------------------------------------------
    Check(
        "anti_bulge_tie_width_y",
        lit(r"\*\*<V> mm\*\* breit in Y"),
        "bar Y-width",
    ),
    Check(
        "anti_bulge_tie_height_z",
        lit(r"\*\*<V> mm\*\* hoch in Z"),
        "bar Z-height",
    ),

    # ---- Snap (active side) ----------------------------------------------
    Check("hook_arm", lit(r"<V> mm Armdicke"), "snap arm thickness"),
    Check("hook_length", lit(r"<V> mm lang"), "snap arm length"),
    Check("hook_protr", lit(r"<V> mm Lippenüberstand"), "snap nose protrusion"),
    Check("hook_lead", lit(r"<V> mm Einführschräge"), "snap insertion ramp"),
    Check("hook_hold", lit(r"<V> mm Haltelänge"), "snap hold length"),
    Check("hook_release", lit(r"<V> mm Auslöserampe"), "snap release ramp"),
    Check("hook_root_fil", lit(r"<V> mm Armwurzel-Fillet"), "snap root fillet"),
    Check("hook_width", lit(r"<V> mm breit"), "snap arm width"),

    # ---- Hook rail (passive side) ----------------------------------------
    Check("hook_rail_width", lit(r"<V> mm lang"), "hook rail length"),
    Check("hook_rail_drop", lit(r"<V> mm Absenkung"), "hook rail drop"),
    Check("hook_rail_depth", lit(r"<V> mm Gesamttiefe"), "hook rail depth"),
    Check(
        "hook_nose_outboard",
        lit(r"<V> mm über die Deckelkante"),
        "hook nose outboard",
    ),
    Check(
        "hook_slot_depth",
        lit(r"<V> mm tiefe Retentionstasche"),
        "hook receiver retention depth",
    ),
    Check(
        "hook_slot_lead_depth",
        lit(r"<V> mm tiefer Einführkanal"),
        "hook receiver lead-in depth",
    ),

    # ---- Engraving --------------------------------------------------------
    Check("version_font", lit(r"Font-Size <V> mm"), "version font size"),
    Check("version_depth", lit(r"<V> mm tiefe Vertiefung"), "version engraving depth"),
]


def render_offsets(offsets: tuple) -> str:
    """(-36.0, 0.0, 36.0) → '-36, 0, +36'."""
    parts = []
    for o in offsets:
        if isinstance(o, float) and o.is_integer():
            o = int(o)
        if o == 0:
            parts.append("0")
        elif o > 0:
            parts.append(f"+{o}")
        else:
            parts.append(str(o))
    return ", ".join(parts)


def custom_checks(params: dict[str, object], readme: str) -> list[tuple[str, str, bool]]:
    """Checks that don't fit the (param, single-pattern) shape."""
    out = []

    offsets = params.get("anti_bulge_tie_y_offsets")
    if isinstance(offsets, tuple):
        rendered = render_offsets(offsets)
        pattern = rf"Y = {re.escape(rendered)} mm"
        out.append((
            f"anti_bulge_tie_y_offsets = {offsets}",
            pattern,
            re.search(pattern, readme) is not None,
        ))

    return out


def main() -> int:
    if not SCRIPT.exists():
        print(f"FATAL: {SCRIPT} not found", file=sys.stderr)
        return 2
    if not README.exists():
        print(f"FATAL: {README} not found", file=sys.stderr)
        return 2

    params = parse_constants(SCRIPT)
    readme = README.read_text()

    failures: list[str] = []
    passes = 0

    print(f"Checking {SCRIPT.name} ↔ {README.name}\n")

    for check in CHECKS:
        if check.name not in params:
            failures.append(f"  ✗ {check.name}: not found as a top-level constant in {SCRIPT.name}")
            continue
        value = params[check.name]
        pattern = check.build_pattern(value)
        if re.search(pattern, readme):
            print(f"  ✓ {check.name} = {fmt_num(value)}  ({check.description})")
            passes += 1
        else:
            failures.append(
                f"  ✗ {check.name} = {fmt_num(value)}  ({check.description})\n"
                f"      pattern: {pattern}"
            )

    for label, pattern, ok in custom_checks(params, readme):
        if ok:
            print(f"  ✓ {label}")
            passes += 1
        else:
            failures.append(f"  ✗ {label}\n      pattern: {pattern}")

    print()
    if failures:
        print(f"FAIL: {len(failures)} sync issue(s) ({passes} OK):\n")
        for f in failures:
            print(f)
        print("\nFix: update README.md to match the script value, or update the")
        print("script if the README is the intended ground truth.")
        return 1

    print(f"OK: {passes} parameters in sync.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
