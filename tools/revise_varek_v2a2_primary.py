#!/usr/bin/env python3
"""Create motion-chassis-v2c from the reviewed V2A.1/V2B-equivalent source."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import bpy


ROOT = Path("/home/aaron/animation/thulans-production")
SOURCE = ROOT / "blender/candidates/varek-chassis-v2a1-dense-static.blend"
SOURCE_SHA = "93139166968b936d045ed740cd748a8c040f5864114a322dd4205b740883a6d3"
OUTPUT = ROOT / "blender/candidates/motion-chassis-v2c.blend"
EVIDENCE = ROOT / "evidence/motion-chassis-v2c"
sys.path.insert(0, str(ROOT / "tools"))
import build_varek_chassis_v2a as base


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def resize(name, dimensions, location=None):
    obj = bpy.data.objects[name]
    obj.dimensions = dimensions
    if location is not None:
        obj.location = location
    base.apply_scale(obj)
    return obj


def make_beam(name, start, end, thickness, collection, material, importance="PRIMARY"):
    return base.beam(name, start, end, thickness, collection, material, importance)


def object_geometry_signature(obj):
    payload = {
        "matrix_world": [list(row) for row in obj.matrix_world],
        "vertices": [list(vertex.co) for vertex in obj.data.vertices],
        "polygons": [list(poly.vertices) for poly in obj.data.polygons],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def replace_central_hull():
    """One solid hull with three heavy, connected front planes."""
    obj = bpy.data.objects["Thoracic_Center"]
    material = obj.data.materials[0]
    vertices = [
        (-0.15, 0.00, -0.26), (-0.055, -0.06, -0.26),
        (0.055, -0.06, -0.26), (0.15, 0.00, -0.26),
        (-0.24, 0.02, 0.26), (-0.09, -0.08, 0.26),
        (0.09, -0.08, 0.26), (0.24, 0.02, 0.26),
        (-0.15, 0.14, -0.26), (0.15, 0.14, -0.26),
        (-0.24, 0.15, 0.26), (0.24, 0.15, 0.26),
    ]
    faces = [
        (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6),
        (8, 10, 11, 9), (0, 4, 10, 8), (3, 9, 11, 7),
        (4, 5, 6, 7, 11, 10), (0, 8, 9, 3, 2, 1),
    ]
    mesh = bpy.data.meshes.new("Thoracic_Center_V2C_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj.data = mesh
    obj.data.materials.append(material)
    obj.location = (0.0, 0.04, 1.49)
    return obj


def replace_toe_with_wedge(name, location, material):
    """Replace a boot-like toe block with a low industrial wedge."""
    width, depth, height = 0.19, 0.27, 0.11
    x, y, z = width / 2, depth / 2, height / 2
    vertices = [
        (-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
        (-x, -y, -0.35 * z), (x, -y, -0.35 * z),
        (x, y, z), (-x, y, z),
    ]
    faces = ((0, 1, 2, 3), (0, 4, 5, 1), (1, 5, 6, 2),
             (2, 6, 7, 3), (3, 7, 4, 0), (4, 7, 6, 5))
    obj = bpy.data.objects[name]
    mesh = bpy.data.meshes.new(name + "_V2C_Wedge_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj.data = mesh
    obj.data.materials.append(material)
    obj.location = location
    return obj


def main():
    if Path(bpy.data.filepath).resolve() != SOURCE.resolve():
        raise RuntimeError("V2C must open the frozen reviewed source")
    if digest(SOURCE) != SOURCE_SHA:
        raise RuntimeError("reviewed source hash mismatch")
    if OUTPUT.exists():
        raise RuntimeError("motion-chassis-v2c output collision")

    scene = bpy.context.scene
    yoke_before = {
        obj.name: object_geometry_signature(obj)
        for obj in scene.objects
        if obj.type == "MESH" and obj.name.startswith("Yoke_")
    }
    frame = bpy.data.collections["03_LOAD_FRAME"]
    ground = bpy.data.collections["05_GROUND_INTERFACE"]
    hands = bpy.data.collections["06_MANIPULATORS"]
    iron = bpy.data.materials["QA_Primary_Iron_Clay"]
    dark = bpy.data.materials["QA_Protected_Hull_Clay"]

    # 1. One connected, aggressively tapered hull with three front planes.
    replace_central_hull()
    resize("Thoracic_Wing_L", (0.15, 0.21, 0.47), (-0.25, 0.05, 1.50))
    resize("Thoracic_Wing_R", (0.15, 0.21, 0.47), (0.25, 0.05, 1.50))
    resize("Abdominal_Cage", (0.30, 0.22, 0.20), (0.0, 0.06, 1.19))

    # 2. Shoulder/thoracic rails overlap the hull edges. Yoke geometry is untouched.
    for side, sign in (("L", -1), ("R", 1)):
        rail = bpy.data.objects[f"Thoracic_Rail_{side}"]
        rail.location.x = sign * 0.31
        rail.location.y = -0.155

        # 3. Third, rear-offset load member per leg.
        make_beam(f"Rear_Hydraulic_Piston_Upper_{side}",
                  (sign * 0.27, 0.15, 0.97),
                  (sign * 0.34, 0.15, 0.68), 0.06, frame, dark)
        make_beam(f"Rear_Hydraulic_Piston_Lower_{side}",
                  (sign * 0.34, 0.15, 0.55),
                  (sign * 0.34, 0.15, 0.30), 0.055, frame, dark)

        # 4. Low wedge toes and a visible folded heel-anchor plate.
        resize(f"Foot_Base_{side}", (0.48, 0.58, 0.13), (sign * 0.35, 0.0, 0.065))
        resize(f"Heel_Drive_{side}", (0.39, 0.27, 0.20), (sign * 0.35, 0.265, 0.10))
        replace_toe_with_wedge(f"Toe_Pad_{side}_0", (sign * 0.35 - 0.105, -0.31, 0.055), dark)
        replace_toe_with_wedge(f"Toe_Pad_{side}_1", (sign * 0.35 + 0.105, -0.31, 0.055), dark)
        resize(f"Folded_Outrigger_Rear_{side}", (0.29, 0.055, 0.25),
               (sign * 0.35, 0.39, 0.16))
        bpy.data.objects[f"Folded_Outrigger_Rear_{side}"].name = f"Folded_Heel_Anchor_Plate_{side}"

        # 5. Exposed wrist rotation bearing and lower palm guard.
        resize(f"Wrist_Bearing_{side}", (0.22, 0.25, 0.22),
               (sign * 0.72, -0.02, 0.91))
        resize(f"Manipulator_Palm_{side}", (0.23, 0.25, 0.25),
               (sign * 0.72, -0.005, 0.79))
        base.prism(f"Palm_Lower_Guard_{side}",
                   (sign * 0.72, -0.045, 0.675),
                   0.12, 0.18, 0.23, 0.13, 0.18,
                   hands, iron, 0.018, "PRIMARY")

    # Resizing a normalized source mesh preserves its small origin offset. Reseat only
    # ground-interface objects that fell below the established floor plane.
    for obj in ground.objects:
        if obj.type != "MESH" or not obj.get("production_geometry"):
            continue
        ground_error = base.bounds(obj)[0].z
        if ground_error < 0.0:
            obj.location.z -= ground_error
    bpy.context.view_layer.update()

    production = [obj for obj in scene.objects if obj.type == "MESH" and obj.get("production_geometry")]
    yoke_after = {
        obj.name: object_geometry_signature(obj)
        for obj in scene.objects
        if obj.type == "MESH" and obj.name.startswith("Yoke_")
    }
    if yoke_after != yoke_before:
        raise RuntimeError("yoke geometry changed")
    low, high = base.union_bounds(production)
    height = high.z - low.z
    if abs(height - 2.4384) > 0.0005 or abs(low.z) > 0.00025:
        lowest = sorted((base.bounds(obj)[0].z, obj.name) for obj in production)[:5]
        raise RuntimeError(
            f"scale/contact gate failed: height={height}, ground={low.z}, lowest={lowest}"
        )
    if scene.render.engine != "BLENDER_WORKBENCH":
        raise RuntimeError("review render must remain Workbench")

    scene["iteration"] = "MOTION_CHASSIS_V2C_PRIMARY_FORM_FAST_LANE"
    scene["source_candidate_sha256"] = SOURCE_SHA
    scene["human_approval"] = "REQUIRED"
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    candidate_sha = digest(OUTPUT)

    EVIDENCE.mkdir(parents=True, exist_ok=False)
    pilot_objects = list(bpy.data.collections["01_PILOT_ENVELOPE"].objects)
    cutaway_objects = [obj for obj in scene.objects if obj.get("review_hide_cutaway")]
    renders = {}
    views = (("front-clay.png", "Cam_Front"),
             ("side-clay.png", "Cam_CharacterRight"))
    for filename, camera_name in views:
        cutaway = False
        for obj in pilot_objects:
            obj.hide_render = not cutaway
        for obj in cutaway_objects:
            obj.hide_render = cutaway
        scene.camera = scene.objects[camera_name]
        path = EVIDENCE / filename
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        renders[filename] = {
            "camera": camera_name,
            "sha256": digest(path),
            "candidate_sha256": candidate_sha,
        }
    for obj in pilot_objects + cutaway_objects:
        obj.hide_render = False
    if digest(OUTPUT) != candidate_sha or digest(SOURCE) != SOURCE_SHA:
        raise RuntimeError("frozen-byte gate failed")

    record = {
        "schema_version": "1.0",
        "claim_class": "OBSERVED",
        "gate": "MOTION_CHASSIS_V2C_PRIMARY_FORM_FAST_LANE",
        "overall": "PASS",
        "human_approval": "REQUIRED",
        "source_sha256": SOURCE_SHA,
        "candidate_sha256": candidate_sha,
        "height_m": height,
        "ground_min_z_m": low.z,
        "authorized_changes": [
            "aggressively tapered three-plane central hull",
            "inward overlapping thoracic rails",
            "third rear hydraulic leg member",
            "wedge toes and folded heel anchor plates",
            "wrist rotation cylinders and lower palm guards",
        ],
        "yoke_geometry_changed": False,
        "yoke_geometry_signatures": yoke_after,
        "renders": renders,
    }
    (EVIDENCE / "measurements.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"MOTION_CHASSIS_V2C_PASS={candidate_sha}")


if __name__ == "__main__":
    main()
