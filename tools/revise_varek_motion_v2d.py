#!/usr/bin/env python3
"""Final bounded silhouette refinement: limbs and ground interface only."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import bpy


ROOT = Path("/home/aaron/animation/thulans-production")
SOURCE = ROOT / "blender/candidates/motion-chassis-v2c.blend"
SOURCE_SHA = "b74d2177b71316816ca95531bddfa5127444a950fb487bf2a5f378cf5b71ec92"
OUTPUT = ROOT / "blender/candidates/motion-chassis-v2d.blend"
EVIDENCE = ROOT / "evidence/motion-chassis-v2d"
sys.path.insert(0, str(ROOT / "tools"))
import build_varek_chassis_v2a as base


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def signature(obj):
    payload = {
        "matrix_world": [list(row) for row in obj.matrix_world],
        "vertices": [list(vertex.co) for vertex in obj.data.vertices],
        "polygons": [list(poly.vertices) for poly in obj.data.polygons],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def resize(name, dimensions, location=None):
    obj = bpy.data.objects[name]
    obj.dimensions = dimensions
    if location is not None:
        obj.location = location
    base.apply_scale(obj)
    return obj


def main():
    if Path(bpy.data.filepath).resolve() != SOURCE.resolve():
        raise RuntimeError("V2D must open motion-chassis-v2c.blend")
    if digest(SOURCE) != SOURCE_SHA:
        raise RuntimeError("V2C source hash mismatch")
    if OUTPUT.exists() or EVIDENCE.exists():
        raise RuntimeError("V2D output collision")

    scene = bpy.context.scene
    frame = bpy.data.collections["03_LOAD_FRAME"]
    ground = bpy.data.collections["05_GROUND_INTERFACE"]
    hands = bpy.data.collections["06_MANIPULATORS"]
    iron = bpy.data.materials["QA_Primary_Iron_Clay"]
    dark = bpy.data.materials["QA_Protected_Hull_Clay"]

    frozen_names = sorted(
        obj.name for obj in scene.objects
        if obj.type == "MESH" and (
            obj.name.startswith("Yoke_")
            or obj.name.startswith("Thoracic_")
            or obj.name.startswith("Operator_")
            or obj.name == "Abdominal_Cage"
        )
    )
    frozen_before = {name: signature(scene.objects[name]) for name in frozen_names}

    for side, sign in (("L", -1), ("R", 1)):
        # A visible triangular load route from pelvis to knee to ankle.
        base.beam(
            f"Pelvis_Knee_Diagonal_{side}",
            (sign * 0.22, -0.145, 1.02),
            (sign * 0.41, -0.145, 0.66),
            0.067, frame, iron, "PRIMARY",
        )
        base.beam(
            f"Knee_Ankle_Return_{side}",
            (sign * 0.41, -0.145, 0.57),
            (sign * 0.29, -0.145, 0.29),
            0.061, frame, dark, "PRIMARY",
        )

        # Forearm brace and deeper palm carriage; digits become short jaws.
        base.beam(
            f"Forearm_LoadBrace_{side}",
            (sign * 0.63, -0.13, 1.26),
            (sign * 0.78, -0.13, 0.94),
            0.062, frame, iron, "PRIMARY",
        )
        resize(f"Wrist_Bearing_{side}", (0.24, 0.27, 0.23),
               (sign * 0.72, -0.025, 0.91))
        resize(f"Manipulator_Palm_{side}", (0.27, 0.28, 0.27),
               (sign * 0.72, -0.005, 0.79))
        resize(f"Palm_Lower_Guard_{side}", (0.21, 0.24, 0.15),
               (sign * 0.72, -0.05, 0.68))
        for digit, xoff in enumerate((-0.075, -0.025, 0.025, 0.075)):
            resize(f"Manipulator_Digit_{side}_{digit}", (0.043, 0.043, 0.13),
                   (sign * 0.72 + xoff, -0.05, 0.59))
            resize(f"Manipulator_Tip_{side}_{digit}", (0.052, 0.052, 0.065),
                   (sign * 0.72 + xoff, -0.065, 0.515))

        # Front-visible ground clamps widen the sole beyond boot language.
        resize(f"Folded_Outrigger_Outer_{side}", (0.20, 0.25, 0.20),
               (sign * 0.63, 0.035, 0.105))
        outer = bpy.data.objects[f"Folded_Outrigger_Outer_{side}"]
        outer.name = f"Front_Visible_Anchor_Clamp_{side}"
        base.box(
            f"Sole_Lateral_Spreader_{side}",
            (sign * 0.53, -0.04, 0.075),
            (0.25, 0.42, 0.095), ground, iron,
            edge=0.018, importance="PRIMARY",
        )

    # Re-seat only ground-interface shapes after dimension edits.
    bpy.context.view_layer.update()
    for obj in ground.objects:
        if obj.type != "MESH" or not obj.get("production_geometry"):
            continue
        low_z = base.bounds(obj)[0].z
        if low_z < 0.0:
            obj.location.z -= low_z
    bpy.context.view_layer.update()

    frozen_after = {name: signature(scene.objects[name]) for name in frozen_names}
    if frozen_after != frozen_before:
        raise RuntimeError("frozen torso or yoke changed")

    production = [obj for obj in scene.objects if obj.type == "MESH" and obj.get("production_geometry")]
    low, high = base.union_bounds(production)
    height = high.z - low.z
    if abs(height - 2.4384) > 0.0005 or abs(low.z) > 0.00025:
        raise RuntimeError(f"scale/contact gate failed: height={height}, ground={low.z}")
    if scene.render.engine != "BLENDER_WORKBENCH":
        raise RuntimeError("review render must remain Workbench")

    scene["iteration"] = "MOTION_CHASSIS_V2D_FINAL_SILHOUETTE_REFINEMENT"
    scene["source_candidate_sha256"] = SOURCE_SHA
    scene["human_approval"] = "REQUIRED"
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    candidate_sha = digest(OUTPUT)

    EVIDENCE.mkdir(parents=True)
    pilot_objects = list(bpy.data.collections["01_PILOT_ENVELOPE"].objects)
    renders = {}
    for filename, camera_name in (
        ("front-clay.png", "Cam_Front"),
        ("three-quarter-clay.png", "Cam_ThreeQuarter"),
    ):
        for obj in pilot_objects:
            obj.hide_render = True
        scene.camera = scene.objects[camera_name]
        path = EVIDENCE / filename
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        renders[filename] = {
            "camera": camera_name,
            "sha256": digest(path),
            "candidate_sha256": candidate_sha,
        }
    for obj in pilot_objects:
        obj.hide_render = False
    if digest(OUTPUT) != candidate_sha or digest(SOURCE) != SOURCE_SHA:
        raise RuntimeError("frozen-byte gate failed")

    record = {
        "schema_version": "1.0",
        "claim_class": "OBSERVED",
        "gate": "MOTION_CHASSIS_V2D_FINAL_SILHOUETTE_REFINEMENT",
        "overall": "PASS",
        "human_approval": "REQUIRED",
        "source_sha256": SOURCE_SHA,
        "candidate_sha256": candidate_sha,
        "height_m": height,
        "ground_min_z_m": low.z,
        "frozen_torso_and_yoke": True,
        "authorized_changes": [
            "triangular leg linkage structure",
            "forearm and manipulator structure",
            "front-visible ground-interface foot structure",
        ],
        "renders": renders,
    }
    (EVIDENCE / "measurements.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"MOTION_CHASSIS_V2D_PASS={candidate_sha}")


if __name__ == "__main__":
    main()
