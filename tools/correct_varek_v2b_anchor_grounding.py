#!/usr/bin/env python3
"""Create a pose-only V2B7 derivative with frame-80 Anchor State grounding."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path("/home/aaron/animation/thulans-production")
sys.path.insert(0, str(ROOT / "tools"))
from correct_varek_v2b_stride_grounding import digest, foot_min_z, mesh_signature


SOURCE = ROOT / "blender/candidates/varek-v2b6-stride-grounded.blend"
SOURCE_SHA = "cd7426ede743371d0fd9e14e264177858eb1f6a8bf42ef7189560162fb9e2cc0"
OUTPUT = ROOT / "blender/candidates/varek-v2b7-anchor-grounded.blend"
EVIDENCE = ROOT / "evidence/varek-v2b7-anchor-grounded"
FRAME = 80
TOLERANCE_M = 0.001


def main() -> None:
    if Path(bpy.data.filepath).resolve() != SOURCE.resolve() or digest(SOURCE) != SOURCE_SHA:
        raise RuntimeError("V2B6 source identity mismatch")
    if OUTPUT.exists() or EVIDENCE.exists():
        raise RuntimeError("V2B7 output collision")

    scene = bpy.context.scene
    rig = scene.objects["Varek_Original_Rig"]
    floor = scene.objects["QA_Floor"]
    floor_z = max((floor.matrix_world @ Vector(corner)).z for corner in floor.bound_box)
    geometry_before = mesh_signature(scene)

    scene.frame_set(FRAME)
    before = {side: foot_min_z(scene, side) - floor_z for side in ("L", "R")}
    correction = -min(before.values())
    if correction <= 0.0:
        raise RuntimeError("Anchor State feet are not below the floor; correction contract is stale")

    root = rig.pose.bones["root"]
    root.location.y += correction
    root.keyframe_insert("location", frame=FRAME)
    scene.frame_set(FRAME - 1)
    scene.frame_set(FRAME)
    bpy.context.view_layer.update()
    after = {side: foot_min_z(scene, side) - floor_z for side in ("L", "R")}
    if any(abs(value) > TOLERANCE_M for value in after.values()):
        raise RuntimeError(f"Anchor State grounding failed: {after}")
    if mesh_signature(scene) != geometry_before:
        raise RuntimeError("pose-only correction changed mesh geometry")

    scene["milestone"] = "V2B_ANCHOR_GROUNDING_CORRECTION"
    scene["human_motion_approval"] = "REQUIRED"
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    candidate_sha = digest(OUTPUT)

    EVIDENCE.mkdir(parents=True)
    pilot = list(bpy.data.collections["01_PILOT_ENVELOPE"].objects)
    prior_hidden = {obj.name: obj.hide_render for obj in pilot}
    for obj in pilot:
        obj.hide_render = True
    renders = {}
    for camera_name in ("Cam_ThreeQuarter", "Cam_Front"):
        scene.camera = scene.objects[camera_name]
        slug = camera_name.removeprefix("Cam_").lower()
        path = EVIDENCE / f"f080-anchor-state-{slug}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        renders[path.name] = {
            "camera": camera_name,
            "sha256": digest(path),
            "candidate_sha256": candidate_sha,
        }
    for obj in pilot:
        obj.hide_render = prior_hidden[obj.name]
    if digest(OUTPUT) != candidate_sha or digest(SOURCE) != SOURCE_SHA:
        raise RuntimeError("frozen-byte gate failed")

    record = {
        "schema_version": "1.0",
        "claim_class": "OBSERVED",
        "gate": "VAREK_V2B_ANCHOR_GROUNDING",
        "machine_result": "PASS",
        "human_motion_gate": "PENDING",
        "source_sha256": SOURCE_SHA,
        "candidate_sha256": candidate_sha,
        "frame": FRAME,
        "floor_world_z_m": round(floor_z, 6),
        "root_world_vertical_correction_m": round(correction, 6),
        "root_translation_channel": "pose_bone.location.y (root local Y == world Z)",
        "foot_clearance_before_m": {side: round(value, 6) for side, value in before.items()},
        "foot_clearance_after_m": {side: round(value, 6) for side, value in after.items()},
        "both_anchor_feet_contact_pass": all(abs(value) <= TOLERANCE_M for value in after.values()),
        "mesh_geometry_unchanged": mesh_signature(scene) == geometry_before,
        "renders": renders,
    }
    (EVIDENCE / "measurements.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"VAREK_V2B7_ANCHOR_PASS={candidate_sha}")


if __name__ == "__main__":
    main()
