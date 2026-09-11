#!/usr/bin/env python3
"""Add an original rigid-machine armature and clearance poses to approved V2D."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path("/home/aaron/animation/thulans-production")
SOURCE = ROOT / "blender/candidates/motion-chassis-v2d.blend"
SOURCE_SHA = "d6947f4328dc9aa9a5fb0f701270d34999c221006aadb40484a9213e302341ed"
OUTPUT = ROOT / "blender/candidates/varek-v2b5-rig-clearance.blend"
EVIDENCE = ROOT / "evidence/varek-v2b5-rig"
sys.path.insert(0, str(ROOT / "tools"))
import build_varek_chassis_v2a as base
from varek_rig_assignment import bone_for_name, validate_assignment


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def add_bone(armature, name, head, tail, parent=None):
    bone = armature.edit_bones.new(name)
    bone.head = head
    bone.tail = tail
    if parent:
        bone.parent = armature.edit_bones[parent]
    return bone


def create_rig():
    data = bpy.data.armatures.new("Varek_Original_Rig_Data")
    rig = bpy.data.objects.new("Varek_Original_Rig", data)
    collection = bpy.data.collections.new("09_RIG")
    bpy.context.scene.collection.children.link(collection)
    collection.objects.link(rig)
    rig.show_in_front = True
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    add_bone(data, "root", (0, 0, 0), (0, 0, 0.28))
    add_bone(data, "pelvis", (0, 0.03, 0.98), (0, 0.03, 1.22), "root")
    add_bone(data, "spine", (0, 0.03, 1.18), (0, 0.03, 1.82), "pelvis")
    add_bone(data, "yoke", (0, 0.04, 1.78), (0, 0.04, 2.40), "spine")
    for side, sign in (("L", -1), ("R", 1)):
        add_bone(data, f"thigh.{side}", (sign * 0.28, 0.02, 1.02), (sign * 0.33, 0.0, 0.61), "pelvis")
        add_bone(data, f"shin.{side}", (sign * 0.33, 0.0, 0.61), (sign * 0.35, -0.01, 0.24), f"thigh.{side}")
        add_bone(data, f"foot.{side}", (sign * 0.35, -0.01, 0.24), (sign * 0.35, -0.30, 0.10), f"shin.{side}")
        add_bone(data, f"upper_arm.{side}", (sign * 0.62, 0.0, 1.78), (sign * 0.70, -0.01, 1.29), "spine")
        add_bone(data, f"forearm.{side}", (sign * 0.70, -0.01, 1.29), (sign * 0.72, -0.03, 0.91), f"upper_arm.{side}")
        add_bone(data, f"hand.{side}", (sign * 0.72, -0.03, 0.91), (sign * 0.72, -0.04, 0.56), f"forearm.{side}")
    bpy.ops.object.mode_set(mode="POSE")
    for bone in rig.pose.bones:
        bone.rotation_mode = "XYZ"
    bpy.ops.object.mode_set(mode="OBJECT")
    rig.select_set(False)
    return rig


def bind_rigid_objects(rig):
    assignments = {}
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or not obj.get("production_geometry"):
            continue
        bone = bone_for_name(obj.name)
        try:
            validate_assignment(obj.name, bone)
        except ValueError as error:
            raise RuntimeError(str(error)) from error
        if bone not in rig.data.bones:
            raise RuntimeError(f"missing bone assignment for {obj.name}: {bone}")
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        obj.select_set(False)
        group = obj.vertex_groups.new(name=bone)
        group.add([vertex.index for vertex in obj.data.vertices], 1.0, "REPLACE")
        modifier = obj.modifiers.new("Rigid_Armature", "ARMATURE")
        modifier.object = rig
        modifier.use_vertex_groups = True
        obj["rigid_driver_bone"] = bone
        assignments[obj.name] = bone
    return assignments


def key_pose(rig, frame, rotations, root_location=None):
    bpy.context.scene.frame_set(frame)
    for pose_bone in rig.pose.bones:
        pose_bone.rotation_euler = (0.0, 0.0, 0.0)
        pose_bone.location = (0.0, 0.0, 0.0)
    if root_location:
        rig.pose.bones["root"].location = root_location
    for name, rotation in rotations.items():
        rig.pose.bones[name].rotation_euler = rotation
    for pose_bone in rig.pose.bones:
        pose_bone.keyframe_insert("rotation_euler", frame=frame)
        pose_bone.keyframe_insert("location", frame=frame)


def author_clearance_poses(rig):
    key_pose(rig, 1, {})
    key_pose(rig, 20, {
        "upper_arm.L": (0.0, 0.0, -0.72),
        "upper_arm.R": (0.0, 0.0, 0.72),
        "forearm.L": (0.0, 0.0, -0.12),
        "forearm.R": (0.0, 0.0, 0.12),
    })
    key_pose(rig, 40, {
        "thigh.L": (0.24, 0.0, 0.0),
        "shin.L": (-0.18, 0.0, 0.0),
        "thigh.R": (-0.22, 0.0, 0.0),
        "shin.R": (0.12, 0.0, 0.0),
        "upper_arm.L": (-0.14, 0.0, 0.0),
        "upper_arm.R": (0.14, 0.0, 0.0),
    })
    key_pose(rig, 60, {
        "upper_arm.L": (0.0, 0.0, -1.75),
        "upper_arm.R": (0.0, 0.0, 1.75),
        "forearm.L": (0.0, 0.0, -0.55),
        "forearm.R": (0.0, 0.0, 0.55),
    })
    key_pose(rig, 80, {
        "thigh.L": (0.0, 0.0, -0.14),
        "thigh.R": (0.0, 0.0, 0.14),
        "shin.L": (0.10, 0.0, 0.0),
        "shin.R": (0.10, 0.0, 0.0),
        "upper_arm.L": (0.0, 0.0, -0.22),
        "upper_arm.R": (0.0, 0.0, 0.22),
    }, root_location=(0.0, 0.0, -0.05))
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 80


def main():
    if Path(bpy.data.filepath).resolve() != SOURCE.resolve() or digest(SOURCE) != SOURCE_SHA:
        raise RuntimeError("approved static chassis identity mismatch")
    if OUTPUT.exists() or EVIDENCE.exists():
        raise RuntimeError("V2B output collision")
    scene = bpy.context.scene
    rig = create_rig()
    assignments = bind_rigid_objects(rig)
    author_clearance_poses(rig)
    scene["milestone"] = "V2B_RIG_CLEARANCE"
    scene["static_source_sha256"] = SOURCE_SHA
    scene["human_motion_approval"] = "REQUIRED"
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    candidate_sha = digest(OUTPUT)

    EVIDENCE.mkdir(parents=True)
    pilot_objects = list(bpy.data.collections["01_PILOT_ENVELOPE"].objects)
    for obj in pilot_objects:
        obj.hide_render = True
    renders = {}
    for frame, label, camera in (
        (1, "neutral", "Cam_ThreeQuarter"),
        (20, "wide-a", "Cam_Front"),
        (40, "stride", "Cam_ThreeQuarter"),
        (60, "overhead-brace", "Cam_Front"),
        (80, "anchor-state", "Cam_ThreeQuarter"),
    ):
        scene.frame_set(frame)
        scene.camera = scene.objects[camera]
        path = EVIDENCE / f"f{frame:03d}-{label}-clay.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        renders[path.name] = {"frame": frame, "pose": label, "camera": camera, "sha256": digest(path), "candidate_sha256": candidate_sha}
    for obj in pilot_objects:
        obj.hide_render = False
    if digest(OUTPUT) != candidate_sha or digest(SOURCE) != SOURCE_SHA:
        raise RuntimeError("frozen-byte gate failed")
    record = {
        "schema_version": "1.0",
        "claim_class": "OBSERVED",
        "gate": "VAREK_V2B_RIG_CLEARANCE",
        "machine_result": "PASS",
        "human_motion_gate": "PENDING",
        "source_sha256": SOURCE_SHA,
        "candidate_sha256": candidate_sha,
        "rig": "Varek_Original_Rig",
        "rigid_control_architecture": "single-bone full-weight armature deformation per rigid object",
        "bones": sorted(bone.name for bone in rig.data.bones),
        "rigid_parent_assignments": assignments,
        "frames": [1, 20, 40, 60, 80],
        "renders": renders,
    }
    (EVIDENCE / "measurements.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"VAREK_V2B_RIG_PASS={candidate_sha}")


if __name__ == "__main__":
    main()
