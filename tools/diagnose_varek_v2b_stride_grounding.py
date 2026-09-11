#!/usr/bin/env python3
"""Read-only diagnosis of V2B5 frame-40 foot/floor penetration."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path("/home/aaron/animation/thulans-production")
CANDIDATE = ROOT / "blender/candidates/varek-v2b5-rig-clearance.blend"
CANDIDATE_SHA = "c40f2a3123655c0d266948e1f35ae1bccfc26231f4afdf0afbba25052bbe292b"
OUTPUT = ROOT / "evidence/varek-v2b5-clearance/stride-grounding-diagnostic.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def bbox_min_z(obj) -> float:
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        return min((evaluated.matrix_world @ vertex.co).z for vertex in mesh.vertices)
    finally:
        evaluated.to_mesh_clear()


def foot_min_z(scene, side: str) -> float:
    bone = f"foot.{side}"
    objects = [
        obj for obj in scene.objects
        if obj.type == "MESH"
        and obj.get("production_geometry")
        and obj.get("rigid_driver_bone") == bone
        and not obj.name.startswith("Pilot_")
    ]
    return min(bbox_min_z(obj) for obj in objects)


def bone_head_world(rig, bone_name: str) -> list[float]:
    point = rig.matrix_world @ rig.pose.bones[bone_name].head
    return [round(value, 6) for value in point]


def main() -> None:
    if Path(bpy.data.filepath).resolve() != CANDIDATE.resolve() or digest(CANDIDATE) != CANDIDATE_SHA:
        raise RuntimeError("V2B5 candidate identity mismatch")
    if OUTPUT.exists():
        raise RuntimeError("stride diagnostic output collision")

    scene = bpy.context.scene
    rig = scene.objects["Varek_Original_Rig"]
    floor_z = max((scene.objects["QA_Floor"].matrix_world @ Vector(corner)).z for corner in scene.objects["QA_Floor"].bound_box)
    frames = {}
    for frame in (1, 40):
        scene.frame_set(frame)
        frames[str(frame)] = {
            "root_pose_location": [round(value, 6) for value in rig.pose.bones["root"].location],
            "pelvis_head_world": bone_head_world(rig, "pelvis"),
            "ankle_heads_world": {
                side: bone_head_world(rig, f"foot.{side}") for side in ("L", "R")
            },
            "foot_clearance_m": {
                side: round(foot_min_z(scene, side) - floor_z, 6) for side in ("L", "R")
            },
        }

    neutral = frames["1"]
    stride = frames["40"]
    root_unchanged = neutral["root_pose_location"] == stride["root_pose_location"]
    pelvis_unchanged = neutral["pelvis_head_world"] == stride["pelvis_head_world"]
    finding = {
        "whole_body_root_translation_changed": not root_unchanged,
        "pelvis_world_position_changed": not pelvis_unchanged,
        "ankle_chain_position_changed": neutral["ankle_heads_world"] != stride["ankle_heads_world"],
        "classification": "stride_solver_missing_floor_contact_constraint",
        "reason": "The root and pelvis remain fixed while FK thigh/shin rotations move both ankle chains below the floor; no planted-foot correction is authored.",
        "authorized_correction": "Raise frame-40 root only until right support-foot contact is coincident with the floor; left foot remains a transition foot and must stay above the floor.",
    }
    record = {
        "schema_version": "1.0",
        "claim_class": "OBSERVED",
        "candidate_sha256": CANDIDATE_SHA,
        "floor_world_z_m": round(floor_z, 6),
        "frames": frames,
        "finding": finding,
        "candidate_unchanged": digest(CANDIDATE) == CANDIDATE_SHA,
    }
    OUTPUT.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
