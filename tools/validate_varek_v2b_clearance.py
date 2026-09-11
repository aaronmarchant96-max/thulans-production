#!/usr/bin/env python3
"""Render-only V2B clearance review and measure foot grounding."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy


ROOT = Path("/home/aaron/animation/thulans-production")
CANDIDATE = ROOT / "blender/candidates/varek-v2b7-anchor-grounded.blend"
CANDIDATE_SHA = "ccc8cd8fb3083f5c1298f3e2d046fb054752208597e7641c3051fe12d3cf6c40"
EVIDENCE = ROOT / "evidence/varek-v2b7-clearance-final"

POSES = {
    "neutral": {"frame": 1, "views": ("Cam_ThreeQuarter",)},
    "a-pose": {"frame": 20, "views": ("Cam_Front", "Cam_ThreeQuarter")},
    "asymmetric-stride": {"frame": 40, "views": ("Cam_ThreeQuarter", "Cam_CharacterRight")},
    "overhead-brace": {"frame": 60, "views": ("Cam_Front", "Cam_ThreeQuarter", "Cam_CharacterRight")},
    "anchor-state": {"frame": 80, "views": ("Cam_ThreeQuarter", "Cam_Front")},
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def world_bbox_z(obj) -> tuple[float, float]:
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        values = [(evaluated.matrix_world @ vertex.co).z for vertex in mesh.vertices]
        return min(values), max(values)
    finally:
        evaluated.to_mesh_clear()


def foot_grounding(scene, floor_top: float) -> dict:
    result = {}
    for side in ("L", "R"):
        bone = f"foot.{side}"
        objects = [
            obj for obj in scene.objects
            if obj.type == "MESH"
            and obj.get("production_geometry")
            and obj.get("rigid_driver_bone") == bone
            and not obj.name.startswith("Pilot_")
        ]
        minimum = min(world_bbox_z(obj)[0] for obj in objects)
        delta = minimum - floor_top
        if delta < -0.001:
            state = "PENETRATING"
        elif delta > 0.001:
            state = "FLOATING"
        else:
            state = "CONTACT"
        result[side] = {
            "assembly_min_z_m": round(minimum, 6),
            "floor_top_z_m": round(floor_top, 6),
            "clearance_m": round(delta, 6),
            "state": state,
        }
    return result


def main() -> None:
    if Path(bpy.data.filepath).resolve() != CANDIDATE.resolve():
        raise RuntimeError("validator must load the frozen V2B7 candidate")
    if digest(CANDIDATE) != CANDIDATE_SHA:
        raise RuntimeError("frozen V2B7 candidate hash mismatch")
    if EVIDENCE.exists():
        raise RuntimeError("V2B7 clearance evidence collision")
    EVIDENCE.mkdir(parents=True)

    scene = bpy.context.scene
    floor = scene.objects["QA_Floor"]
    floor_top = world_bbox_z(floor)[1]
    pilot = list(bpy.data.collections["01_PILOT_ENVELOPE"].objects)
    prior_hidden = {obj.name: obj.hide_render for obj in pilot}
    for obj in pilot:
        obj.hide_render = True

    records = {}
    for pose, contract in POSES.items():
        frame = contract["frame"]
        scene.frame_set(frame)
        pose_record = {
            "frame": frame,
            "arm_yoke": "PENDING_VISUAL_REVIEW",
            "pelvis_thigh": "PENDING_VISUAL_REVIEW",
            "knee_shin": "PENDING_VISUAL_REVIEW",
            "grounding": foot_grounding(scene, floor_top),
            "renders": {},
        }
        for camera_name in contract["views"]:
            camera = scene.objects[camera_name]
            scene.camera = camera
            slug = camera_name.removeprefix("Cam_").lower()
            output = EVIDENCE / f"f{frame:03d}-{pose}-{slug}.png"
            scene.render.filepath = str(output)
            bpy.ops.render.render(write_still=True)
            pose_record["renders"][output.name] = {
                "camera": camera_name,
                "sha256": digest(output),
                "candidate_sha256": CANDIDATE_SHA,
            }
        records[pose] = pose_record

    for obj in pilot:
        obj.hide_render = prior_hidden[obj.name]
    if digest(CANDIDATE) != CANDIDATE_SHA:
        raise RuntimeError("render-only validation mutated frozen candidate")

    evidence = {
        "schema_version": "1.0",
        "claim_class": "OBSERVED",
        "gate": "VAREK_V2B_CLEARANCE_AND_LOAD_POSES",
        "candidate_sha256": CANDIDATE_SHA,
        "candidate_unchanged_after_render": True,
        "contact_rule": "Touching or seating at a designed interface is permitted; impossible interpenetration, detached continuity, or lost required support fails.",
        "ground_contact_tolerance_m": 0.001,
        "human_motion_gate": "PENDING",
        "poses": records,
    }
    (EVIDENCE / "measurements.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(f"V2B5_CLEARANCE_EVIDENCE={EVIDENCE}")


if __name__ == "__main__":
    main()
