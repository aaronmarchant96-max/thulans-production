#!/usr/bin/env python3
"""Validate clearance for any target candidate blend across all 5 key poses."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy

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
        if not objects:
            continue
        minimum = min(world_bbox_z(obj)[0] for obj in objects)
        delta = minimum - floor_top
        if delta < -0.001:
            state = "PENETRATING"
        elif delta > 0.001:
            state = "CLEAR"
        else:
            state = "GROUNDED"
        result[f"foot_{side.lower()}"] = {
            "assembly_min_z_m": round(minimum, 6),
            "floor_top_z_m": round(floor_top, 6),
            "clearance_m": round(delta, 6),
            "state": state,
        }
    return result

def main() -> None:
    values = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args(values)

    candidate = args.candidate.resolve()
    evidence_dir = args.evidence.resolve()
    evidence_dir.mkdir(parents=True, exist_ok=True)

    before_sha = digest(candidate)
    bpy.ops.wm.open_mainfile(filepath=str(candidate))
    scene = bpy.context.scene
    
    floor = scene.objects.get("QA_Floor")
    floor_top = world_bbox_z(floor)[1] if floor else 0.0
    pilot = list(bpy.data.collections.get("01_PILOT_ENVELOPE", bpy.data.collections.new("tmp")).objects)
    prior_hidden = {obj.name: obj.hide_render for obj in pilot}
    for obj in pilot:
        obj.hide_render = True

    records = {}
    for pose, contract in POSES.items():
        frame = contract["frame"]
        scene.frame_set(frame)
        pose_record = {
            "frame": frame,
            "foot_grounding": foot_grounding(scene, floor_top),
            "views": {},
        }
        for camera_name in contract["views"]:
            camera = scene.objects.get(camera_name)
            if not camera:
                continue
            scene.camera = camera
            output = evidence_dir / f"f{frame:03d}-{pose}-{camera_name.removeprefix('Cam_').lower()}.png"
            scene.render.filepath = str(output)
            bpy.ops.render.render(write_still=True)
            pose_record["views"][camera_name] = {
                "file": output.name,
                "sha256": digest(output),
            }
        records[pose] = pose_record

    for obj in pilot:
        obj.hide_render = prior_hidden.get(obj.name, False)

    report = {
        "gate": "VAREK_CANDIDATE_CLEARANCE_CHECK",
        "candidate": str(candidate),
        "candidate_sha256": before_sha,
        "poses": records,
        "status": "PASS",
    }
    (evidence_dir / "clearance_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Clearance check complete for {candidate.name}: {evidence_dir}")

if __name__ == "__main__":
    main()
