#!/usr/bin/env python3
"""Independent read-only validator for the frozen Varek Motion Chassis V1 blend."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "spec" / "varek_motion_chassis_v1_contract.json"
MEASUREMENTS_PATH = ROOT / "evidence" / "varek-motion-chassis-v1" / "measurements.json"
OUTPUT_PATH = ROOT / "evidence" / "varek-motion-chassis-v1" / "validation.json"
BUILDER_PATH = ROOT / "tools" / "build_varek_motion_chassis_v1.py"
PLAN_PATH = ROOT / "docs" / "VAREK_MOTION_CHASSIS_PLAN.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--measurements", type=Path, default=MEASUREMENTS_PATH)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    return parser.parse_args(argv)


def world_bounds(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points))), Vector(
        (max(p.x for p in points), max(p.y for p in points), max(p.z for p in points))
    )


def aabb_penetration(a, b):
    amin, amax = world_bounds(a)
    bmin, bmax = world_bounds(b)
    overlaps = [min(amax[i], bmax[i]) - max(amin[i], bmin[i]) for i in range(3)]
    return max(0.0, min(overlaps)) if all(value > 0 for value in overlaps) else 0.0


def aabb_gap(a, b):
    amin, amax = world_bounds(a)
    bmin, bmax = world_bounds(b)
    gaps = [max(0.0, amin[i] - bmax[i], bmin[i] - amax[i]) for i in range(3)]
    return max(gaps)


def check(name, passed, observed, expected):
    return {"rule": name, "pass": bool(passed), "observed": observed, "expected": expected}


def validate(contract, measurements, blend_path):
    scene = bpy.context.scene
    checks = []
    blend_sha = sha256(blend_path)
    checks.append(check("candidate.sha256", blend_sha == measurements["candidate"]["sha256"], blend_sha, measurements["candidate"]["sha256"]))
    checks.append(check("scene.plan_id", scene.get("plan_id") == contract["plan_id"], scene.get("plan_id"), contract["plan_id"]))
    checks.append(check("scene.claim_boundary", scene.get("claim_boundary") == "MACHINE_PASS_DOES_NOT_EQUAL_CHASSIS_APPROVAL", scene.get("claim_boundary"), "MACHINE_PASS_DOES_NOT_EQUAL_CHASSIS_APPROVAL"))
    checks.append(check("concept.hash", sha256(ROOT / contract["approved_concept"]["path"]) == contract["approved_concept"]["sha256"], sha256(ROOT / contract["approved_concept"]["path"]), contract["approved_concept"]["sha256"]))
    checks.append(check("plan.hash", sha256(PLAN_PATH) == measurements["plan_file_sha256"], sha256(PLAN_PATH), measurements["plan_file_sha256"]))
    checks.append(check("builder.hash", sha256(BUILDER_PATH) == measurements["builder_script_sha256"], sha256(BUILDER_PATH), measurements["builder_script_sha256"]))
    checks.append(check("validator.hash", sha256(Path(__file__).resolve()) == measurements["validator_script_sha256"], sha256(Path(__file__).resolve()), measurements["validator_script_sha256"]))

    collection_names = sorted(collection.name for collection in bpy.data.collections)
    missing_collections = sorted(set(contract["required_collections"]) - set(collection_names))
    checks.append(check("collections.required", not missing_collections, missing_collections, []))
    checks.append(check("scene.unit_system", scene.unit_settings.system == contract["scene"]["unit_system"], scene.unit_settings.system, contract["scene"]["unit_system"]))
    checks.append(check("scene.unit_scale", abs(scene.unit_settings.scale_length - contract["scene"]["unit_scale"]) < 1e-9, scene.unit_settings.scale_length, contract["scene"]["unit_scale"]))
    checks.append(check("scene.fps", scene.render.fps == contract["scene"]["fps"], scene.render.fps, contract["scene"]["fps"]))
    checks.append(check("scene.frame_range", [scene.frame_start, scene.frame_end] == [contract["scene"]["frame_start"], contract["scene"]["frame_end"]], [scene.frame_start, scene.frame_end], [contract["scene"]["frame_start"], contract["scene"]["frame_end"]]))

    scene.frame_set(1)
    height_objects = [obj for obj in scene.objects if obj.type == "MESH" and obj.get("qa_count_height", False)]
    bounds = [world_bounds(obj) for obj in height_objects]
    min_z = min(pair[0].z for pair in bounds)
    max_z = max(pair[1].z for pair in bounds)
    height = max_z - min_z
    dims = contract["dimensions_m"]
    checks.append(check("dimensions.overall_height", abs(height - dims["overall_height_target"]) <= dims["overall_height_tolerance"], height, {"target": dims["overall_height_target"], "tolerance": dims["overall_height_tolerance"]}))
    checks.append(check("dimensions.ground", abs(min_z - dims["ground_z_target"]) <= dims["ground_z_tolerance"], min_z, {"target": dims["ground_z_target"], "tolerance": dims["ground_z_tolerance"]}))
    bad_scales = {obj.name: list(obj.scale) for obj in height_objects if any(abs(value - 1.0) > 1e-6 for value in obj.scale)}
    checks.append(check("rigid.applied_scales", not bad_scales, bad_scales, {}))
    nonrigid = [obj.name for obj in height_objects if not obj.get("rigid_module", False)]
    checks.append(check("rigid.module_tags", not nonrigid, nonrigid, []))

    joint_offsets = {}
    for frame in contract["motion"]["tracked_frames"]:
        scene.frame_set(frame)
        joint_offsets[str(frame)] = {}
        for side in ("L", "R"):
            for role in ("SHOULDER", "ELBOW", "HIP", "KNEE", "ANKLE"):
                p_name = f"PILOT_JOINT_{role}_{side}"
                c_name = f"CHASSIS_JOINT_{role}_{side}"
                distance = (scene.objects[p_name].matrix_world.translation - scene.objects[c_name].matrix_world.translation).length
                joint_offsets[str(frame)][f"{role}_{side}"] = distance
    max_joint_offset = max(value for frame in joint_offsets.values() for value in frame.values())
    checks.append(check("pilot.articulation_offsets_reported", set(joint_offsets) == {str(frame) for frame in contract["motion"]["tracked_frames"]}, sorted(joint_offsets), contract["motion"]["tracked_frames"]))

    foot_positions = {}
    for frame in contract["motion"]["planted_frames"]:
        scene.frame_set(frame)
        foot_positions[str(frame)] = {side: list(scene.objects[f"CTRL_Foot_{side}"].matrix_world.translation) for side in ("L", "R")}
    reference = foot_positions[str(contract["motion"]["planted_frames"][0])]
    max_foot_translation = max((Vector(position) - Vector(reference[side])).length for positions in foot_positions.values() for side, position in positions.items())
    checks.append(check("motion.primary_foot_translation", max_foot_translation <= contract["motion"]["primary_foot_translation_max_m"], max_foot_translation, contract["motion"]["primary_foot_translation_max_m"]))

    collision_by_frame = {}
    max_collision = 0.0
    for frame in contract["motion"]["tracked_frames"]:
        scene.frame_set(frame)
        collision_by_frame[str(frame)] = {}
        for left, right in contract["collision"]["pairs"]:
            depth = aabb_penetration(scene.objects[left], scene.objects[right])
            collision_by_frame[str(frame)][f"{left}::{right}"] = depth
            max_collision = max(max_collision, depth)
    checks.append(check("collision.provisional_aabb", max_collision <= contract["collision"]["provisional_penetration_max_m"], max_collision, contract["collision"]["provisional_penetration_max_m"]))

    scene.frame_set(72)
    hand_gaps = {side: aabb_gap(scene.objects[f"Manipulator_Hand_{side}"], scene.objects["QA_Overhead_Load"]) for side in ("L", "R")}
    checks.append(check("motion.overhead_hand_contact", max(hand_gaps.values()) <= contract["motion"]["overhead_hand_contact_gap_max_m"], hand_gaps, contract["motion"]["overhead_hand_contact_gap_max_m"]))

    ground_modes = sorted({obj.get("ground_mode") for obj in scene.objects if obj.get("ground_mode")})
    expected_modes = sorted([contract["motion"]["trailer_anchor_mode"], *contract["motion"]["isolated_static_modes"]])
    checks.append(check("ground.modes", ground_modes == expected_modes, ground_modes, expected_modes))

    camera_names = {"Cam_Front", "Cam_Rear", "Cam_Side", "Cam_ThreeQuarter", "Cam_TrailerPose"}
    missing_cameras = sorted(camera_names - set(scene.objects.keys()))
    checks.append(check("review.cameras", not missing_cameras, missing_cameras, []))
    scene.frame_set(1)
    return checks, {
        "height_m": height,
        "ground_min_z_m": min_z,
        "max_pilot_to_chassis_joint_offset_m": max_joint_offset,
        "pilot_to_chassis_offsets_m": joint_offsets,
        "primary_foot_reference_positions": foot_positions,
        "max_primary_foot_translation_m": max_foot_translation,
        "collision_representation": contract["collision"]["representation"],
        "collision_by_frame_m": collision_by_frame,
        "max_provisional_collision_penetration_m": max_collision,
        "overhead_hand_contact_gaps_m": hand_gaps,
        "claim_boundary": "MEASUREMENTS_DO_NOT_ESTABLISH_HUMAN_VISUAL_APPROVAL_OR_ENGINEERING_CAPACITY",
    }


def main():
    args = parse_args()
    blend_path = Path(bpy.data.filepath).resolve() if bpy.data.filepath else None
    if not blend_path or not blend_path.exists():
        raise RuntimeError("validator requires an opened frozen candidate blend")
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    measurements = json.loads(args.measurements.read_text(encoding="utf-8"))
    before_sha = sha256(blend_path)
    checks, readback = validate(contract, measurements, blend_path)
    after_sha = sha256(blend_path)
    checks.append(check("validator.read_only", before_sha == after_sha, after_sha, before_sha))
    failures = [item["rule"] for item in checks if not item["pass"]]
    record = {
        "schema_version": "1.0",
        "claim_class": "OBSERVED",
        "gate": "VAREK_MOTION_CHASSIS_V1_INDEPENDENT_VALIDATION",
        "overall": "PASS" if not failures else "FAIL",
        "candidate_sha256": before_sha,
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "failures": failures,
        "readback": readback,
        "human_approval": "REQUIRED",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    if failures:
        print("VAREK_MOTION_CHASSIS_V1_VALIDATION_FAIL=" + ",".join(failures), file=sys.stderr)
        raise SystemExit(1)
    print(f"VAREK_MOTION_CHASSIS_V1_VALIDATION_PASS={before_sha}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        print(f"VAREK_MOTION_CHASSIS_V1_VALIDATION_ERROR={exc}", file=sys.stderr)
        raise SystemExit(1)
