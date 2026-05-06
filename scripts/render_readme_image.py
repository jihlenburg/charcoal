#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Render the README product image from the generated STL artifacts.

The normal Python entrypoint prefers Blender/Cycles when Blender is available.
On machines without Blender it falls back to VTK, which is already enough for a
clean documentation render.
"""

from __future__ import annotations

import argparse
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TROUGH = ROOT / "output/STL/trough.stl"
DEFAULT_LID = ROOT / "output/STL/lid.stl"
DEFAULT_OUTPUT = ROOT / "docs/assets/charcoal_filter_v1_1_6_render.png"
LID_EXPLODE_Z_MM = 26.0


def is_blender_python() -> bool:
    try:
        import bpy  # noqa: F401
    except Exception:
        return False
    return True


def resolve_path(path: str | Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else ROOT / path


def find_blender() -> str | None:
    candidates: list[Path | str] = []
    if os.environ.get("BLENDER"):
        candidates.append(os.environ["BLENDER"])
    which = shutil.which("blender")
    if which:
        candidates.append(which)
    candidates.append("/Applications/Blender.app/Contents/MacOS/Blender")
    candidates.extend(Path("/Applications").glob("Blender*.app/Contents/MacOS/Blender"))

    for candidate in candidates:
        candidate_path = Path(candidate)
        if candidate_path.exists() and os.access(candidate_path, os.X_OK):
            return str(candidate_path)
    return None


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--backend",
        choices=("auto", "blender", "vtk"),
        default="auto",
        help="Rendering backend. auto prefers Blender/Cycles and falls back to VTK.",
    )
    parser.add_argument("--trough", default=str(DEFAULT_TROUGH))
    parser.add_argument("--lid", default=str(DEFAULT_LID))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    return parser.parse_args(argv)


def blender_args() -> list[str]:
    if "--" not in sys.argv:
        return []
    return sys.argv[sys.argv.index("--") + 1 :]


def run_blender_subprocess(args: argparse.Namespace, blender: str) -> int:
    cmd = [
        blender,
        "--background",
        "--python",
        str(Path(__file__).resolve()),
        "--",
        "--backend",
        "blender",
        "--trough",
        str(resolve_path(args.trough)),
        "--lid",
        str(resolve_path(args.lid)),
        "--output",
        str(resolve_path(args.output)),
    ]
    return subprocess.run(cmd, check=False).returncode


def trim_transparent_png(path: Path, padding_px: int = 36, top_padding_px: int = 18) -> None:
    try:
        from PIL import Image
    except Exception:
        return

    image = Image.open(path).convert("RGBA")
    bbox = image.getchannel("A").getbbox()
    if bbox is None:
        return

    left = max(0, bbox[0] - padding_px)
    upper = max(0, bbox[1] - top_padding_px)
    right = min(image.width, bbox[2] + padding_px)
    lower = min(image.height, bbox[3] + padding_px)
    image.crop((left, upper, right, lower)).save(path)


def set_color_management(scene: object) -> None:
    view_settings = scene.view_settings
    for attr, value in (
        ("view_transform", "AgX"),
        ("look", "Medium High Contrast"),
        ("exposure", -0.15),
        ("gamma", 1.0),
    ):
        try:
            setattr(view_settings, attr, value)
        except Exception:
            pass


def render_with_blender(args: argparse.Namespace) -> None:
    import bpy
    from mathutils import Vector

    trough_path = resolve_path(args.trough)
    lid_path = resolve_path(args.lid)
    output = resolve_path(args.output)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 6
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1100
    scene.render.film_transparent = True
    set_color_management(scene)

    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.color = (1.0, 1.0, 1.0)
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if background is not None:
        background.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        background.inputs["Strength"].default_value = 0.25

    def import_stl(path: Path, name: str) -> object:
        before = set(bpy.data.objects)
        try:
            bpy.ops.wm.stl_import(filepath=str(path))
        except Exception:
            bpy.ops.import_mesh.stl(filepath=str(path))
        created = [obj for obj in bpy.data.objects if obj not in before]
        obj = created[0] if created else bpy.context.object
        obj.name = name
        return obj

    def pa12_material(name: str, color: tuple[float, float, float, float]) -> object:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf is not None:
            bsdf.inputs["Base Color"].default_value = color
            bsdf.inputs["Roughness"].default_value = 0.86
            if "Metallic" in bsdf.inputs:
                bsdf.inputs["Metallic"].default_value = 0.0
            if "Specular IOR Level" in bsdf.inputs:
                bsdf.inputs["Specular IOR Level"].default_value = 0.35

            noise = nodes.new("ShaderNodeTexNoise")
            noise.inputs["Scale"].default_value = 95.0
            noise.inputs["Detail"].default_value = 12.0
            noise.inputs["Roughness"].default_value = 0.62

            bump = nodes.new("ShaderNodeBump")
            bump.inputs["Strength"].default_value = 0.035
            bump.inputs["Distance"].default_value = 0.08

            links.new(noise.outputs["Fac"], bump.inputs["Height"])
            links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        return mat

    mat_trough = pa12_material("HP MJF PA12 natural grey trough", (0.50, 0.51, 0.50, 1.0))
    mat_lid = pa12_material("blue dyed PA12 lid", (0.04, 0.34, 0.86, 1.0))

    trough = import_stl(trough_path, "Trough")
    lid = import_stl(lid_path, "Lid")
    trough.data.materials.append(mat_trough)
    lid.data.materials.append(mat_lid)
    lid.location.z += LID_EXPLODE_Z_MM

    for obj in (trough, lid):
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        try:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
        except Exception:
            bpy.ops.object.shade_flat()
        try:
            normals = obj.modifiers.new("weighted CAD normals", "WEIGHTED_NORMAL")
            normals.keep_sharp = True
            normals.weight = 50
        except Exception:
            pass
        obj.select_set(False)

    bpy.context.view_layer.update()
    points = []
    for obj in (trough, lid):
        points.extend([obj.matrix_world @ Vector(corner) for corner in obj.bound_box])
    mins = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maxs = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    center = (mins + maxs) * 0.5

    bpy.ops.object.light_add(type="AREA", location=(-70, -85, 130))
    key = bpy.context.object
    key.name = "large softbox"
    key.data.energy = 130000
    key.data.size = 120

    bpy.ops.object.light_add(type="AREA", location=(85, 65, 95))
    fill = bpy.context.object
    fill.name = "small fill"
    fill.data.energy = 6000
    fill.data.size = 80

    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(42), 0, math.radians(-35)))
    sun = bpy.context.object
    sun.name = "soft direction sun"
    sun.data.energy = 0.3

    bpy.ops.object.camera_add(location=(190, -252, 172))
    camera = bpy.context.object
    camera.name = "README camera"
    target = center
    direction = target - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "PERSP"
    camera.data.lens = 56
    camera.data.sensor_width = 36
    camera.data.clip_end = 10000
    scene.camera = camera

    output.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(output)
    bpy.ops.render.render(write_still=True)
    print(f"Rendered {output} with Blender/Cycles")


def render_with_vtk(args: argparse.Namespace) -> None:
    import vtk

    trough_path = resolve_path(args.trough)
    lid_path = resolve_path(args.lid)
    output = resolve_path(args.output)

    def read_actor(path: Path, color: tuple[float, float, float], translate_z: float = 0.0) -> object:
        reader = vtk.vtkSTLReader()
        reader.SetFileName(str(path))

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*color)
        actor.GetProperty().SetRoughness(0.65)
        actor.GetProperty().SetInterpolationToPhong()
        if translate_z:
            transform = vtk.vtkTransform()
            transform.Translate(0, 0, translate_z)
            actor.SetUserTransform(transform)
        return actor

    pa12_grey = (0.50, 0.51, 0.50)
    pa12_blue = (0.04, 0.34, 0.86)
    trough = read_actor(trough_path, pa12_grey)
    lid = read_actor(lid_path, pa12_blue, LID_EXPLODE_Z_MM)

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(1.0, 1.0, 1.0)
    renderer.SetBackgroundAlpha(0.0)
    renderer.AddActor(trough)
    renderer.AddActor(lid)
    renderer.UseShadowsOn()

    key = vtk.vtkLight()
    key.SetLightTypeToSceneLight()
    key.SetPosition(-70, -85, 130)
    key.SetFocalPoint(0, 0, 35)
    key.SetIntensity(1.25)
    renderer.AddLight(key)

    fill = vtk.vtkLight()
    fill.SetLightTypeToSceneLight()
    fill.SetPosition(85, 65, 95)
    fill.SetFocalPoint(0, 0, 35)
    fill.SetIntensity(0.45)
    renderer.AddLight(fill)

    camera = renderer.GetActiveCamera()
    camera.SetPosition(190, -252, 172)
    camera.SetFocalPoint(0, 0, 34)
    camera.SetViewUp(0, 0, 1)
    camera.SetParallelProjection(False)
    camera.SetViewAngle(36)
    renderer.SetActiveCamera(camera)

    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(True)
    window.SetAlphaBitPlanes(True)
    window.SetMultiSamples(8)
    window.SetSize(1600, 1100)
    window.AddRenderer(renderer)
    window.Render()

    image = vtk.vtkWindowToImageFilter()
    image.SetInput(window)
    image.SetScale(1)
    image.SetInputBufferTypeToRGBA()
    image.ReadFrontBufferOff()
    image.Update()

    output.parent.mkdir(parents=True, exist_ok=True)
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(output))
    writer.SetInputConnection(image.GetOutputPort())
    writer.Write()
    print(f"Rendered {output} with VTK")


def main() -> int:
    args = parse_args(blender_args() if is_blender_python() else sys.argv[1:])

    if is_blender_python():
        render_with_blender(args)
        return 0

    if args.backend in ("auto", "blender"):
        blender = find_blender()
        if blender:
            code = run_blender_subprocess(args, blender)
            if code == 0:
                trim_transparent_png(resolve_path(args.output))
            return code
        if args.backend == "blender":
            print("Blender was requested but no Blender executable was found.", file=sys.stderr)
            return 2

    render_with_vtk(args)
    trim_transparent_png(resolve_path(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
