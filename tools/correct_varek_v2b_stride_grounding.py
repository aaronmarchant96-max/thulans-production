#!/usr/bin/env python3
"""Create a pose-only V2B6 derivative with frame-40 support-foot grounding."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path("/home/aaron/animation/thulans-production")
SOURCE = ROOT / "blender/candidates/varek-v2b5-rig-clearance.blend"
SOURCE_SHA = "c40f2a3123655c0d266948e1f35ae1bccfc26231f4afdf0afbba25052bbe292b"
OUTPUT = ROOT / "blender/candidates/varek-v2b6-stride-grounded.blend"
EVIDENCE = ROOT / "evidence/varek-v2b6-stride-grounded"
FRAME = 40
SUPPORT_SIDE = "R"
TOLERANCE_M = 0.001


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


def mesh_signature(scene) -> str:
    value = hashlib.sha256()
    for obj in sorted((item for item in scene.objects if item.type == "MESH"), key=lambda item: item.name):
        value.update(obj.name.encode())
        for vertex in obj.data.vertices:
            value.update(f"{vertex.co.x:.9f},{vertex.co.y:.9f},{vertex.co.z:.9f};".encode())
    return value.hexdigest()


def main() -> None:
    if Path(bpy.data.filepath).resolve() != SOURCE.resolve() or digest(SOURCE) != SOURCE_SHA:
        raise RuntimeError("V2B5 source identity mismatch")
    if OUTPUT.exists() or EVIDENCE.exists():
        raise RuntimeError("V2B6 output collision")

    scene = bpy.context.scene
    rig = scene.objects["Varek_Original_Rig"]
    floor = scene.objects["QA_Floor"]
    floor_z = max((floor.matrix_world @ Vector(corner)).z for corner in floor.bound_box)
    geometry_before = mesh_signature(scene)

    scene.frame_set(FRAME)
    before = {side: foot_min_z(scene, side) - floor_z for side in ("L", "R")}
    correction = -before[SUPPORT_SIDE]
    if correction <= 0.0:
        raise RuntimeError("support foot is not below the floor; correction contract is stale")
    root = rig.pose.bones["root"]
    # The root bone points along world +Z, so bone-local +Y is world vertical.
    root.location.y += correction
    root.keyframe_insert("location", frame=FRAME)
    scene.frame_set(FRAME - 1)
    scene.frame_set(FRAME)
    bpy.context.view_layer.update()
    after = {side: foot_min_z(scene, side) - floor_z for side in ("L", "R")}

    if abs(after[SUPPORT_SIDE]) > TOLERANCE_M:
        raise RuntimeError(f"support foot contact failed: {after[SUPPORT_SIDE]:.6f} m")
    transition_side = "L"
    if after[transition_side] <= TOLERANCE_M:
        raise RuntimeError(f"transition foot failed to clear floor: {after[transition_side]:.6f} m")
    if mesh_signature(scene) != geometry_before:
        raise RuntimeError("pose-only correction changed mesh geometry")

    scene["milestone"] = "V2B_STRIDE_GROUNDING_CORRECTION"
    scene["human_motion_approval"] = "REQUIRED"
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    candidate_sha = digest(OUTPUT)

    EVIDENCE.mkdir(parents=True)
    pilot = list(bpy.data.collections["01_PILOT_ENVELOPE"].objects)
    prior_hidden = {obj.name: obj.hide_render for obj in pilot}
    for obj in pilot:
        obj.hide_render = True
    renders = {}
    for camera_name in ("Cam_ThreeQuarter", "Cam_CharacterRight"):
        scene.camera = scene.objects[camera_name]
        slug = camera_name.removeprefix("Cam_").lower()
        path = EVIDENCE / f"f040-asymmetric-stride-{slug}.png"
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
        "gate": "VAREK_V2B_STRIDE_GROUNDING",
        "machine_result": "PASS",
        "human_motion_gate": "PENDING",
        "source_sha256": SOURCE_SHA,
        "candidate_sha256": candidate_sha,
        "frame": FRAME,
        "floor_world_z_m": round(floor_z, 6),
        "support_foot": SUPPORT_SIDE,
        "transition_foot": transition_side,
        "root_world_vertical_correction_m": round(correction, 6),
        "root_translation_channel": "pose_bone.location.y (root local Y == world Z)",
        "foot_clearance_before_m": {side: round(value, 6) for side, value in before.items()},
        "foot_clearance_after_m": {side: round(value, 6) for side, value in after.items()},
        "support_contact_pass": abs(after[SUPPORT_SIDE]) <= TOLERANCE_M,
        "transition_clearance_pass": after[transition_side] > TOLERANCE_M,
        "mesh_geometry_unchanged": mesh_signature(scene) == geometry_before,
        "renders": renders,
    }
    (EVIDENCE / "measurements.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"VAREK_V2B6_STRIDE_PASS={candidate_sha}")


if __name__ == "__main__":
    main()
