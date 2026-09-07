#!/usr/bin/env python3
"""Build the hash-bound Varek Motion Chassis V1 test article in Blender 5.2."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "VAREK_MOTION_CHASSIS_PLAN.md"
CONTRACT_PATH = ROOT / "spec" / "varek_motion_chassis_v1_contract.json"
VALIDATOR = ROOT / "tools" / "validate_varek_motion_chassis_v1.py"
DEFAULT_OUTPUT = ROOT / "blender" / "candidates" / "varek-motion-chassis-v1.blend"
EVIDENCE_DIR = ROOT / "evidence" / "varek-motion-chassis-v1"
FAILURE_PATH = EVIDENCE_DIR / "failure.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(phase: str, message: str, details=None) -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "schema_version": "1.0",
        "claim_class": "OBSERVED",
        "gate": "VAREK_MOTION_CHASSIS_V1",
        "overall": "FAIL",
        "phase": phase,
        "message": message,
        "details": details or {},
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    FAILURE_PATH.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    raise RuntimeError(f"{phase}: {message}")


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--source-git-commit", required=True)
    parser.add_argument("--source-repo-state", choices=("CLEAN",), required=True)
    parser.add_argument("--plan-git-commit", required=True)
    return parser.parse_args(argv)


def link_only(obj, collection) -> None:
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    collection.objects.link(obj)


def make_material(name: str, color: tuple[float, float, float, float], metallic=0.0, roughness=0.72):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def apply_scale(obj) -> None:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.select_set(False)


def parent_keep_world(obj, parent) -> None:
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = world


def add_box(name, location, dimensions, collection, material, bevel=0.015, rotation=(0.0, 0.0, 0.0), parent=None):
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    apply_scale(obj)
    if bevel:
        modifier = obj.modifiers.new("Manufactured_Radius", "BEVEL")
        modifier.width = min(bevel, min(dimensions) * 0.2)
        modifier.segments = 2
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        obj.select_set(False)
    obj.data.materials.append(material)
    link_only(obj, collection)
    obj["rigid_module"] = True
    obj["qa_count_height"] = True
    if parent:
        parent_keep_world(obj, parent)
    return obj


def add_cylinder(name, location, radius, depth, collection, material, rotation=(0.0, 0.0, 0.0), parent=None, vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    apply_scale(obj)
    obj.data.materials.append(material)
    link_only(obj, collection)
    obj["rigid_module"] = True
    obj["qa_count_height"] = True
    if parent:
        parent_keep_world(obj, parent)
    return obj


def add_uv_sphere(name, location, scale, collection, material, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    apply_scale(obj)
    obj.data.materials.append(material)
    link_only(obj, collection)
    obj["rigid_module"] = True
    obj["qa_count_height"] = True
    if parent:
        parent_keep_world(obj, parent)
    return obj


def add_control(name, location, collection, parent=None):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = 0.08
    collection.objects.link(obj)
    if parent:
        world_location = Vector(location)
        obj.parent = parent
        obj.matrix_parent_inverse = Matrix.Identity(4)
        obj.location = world_location - Vector(parent["rest_world_location"])
    else:
        obj.location = location
    obj["rest_world_location"] = list(location)
    return obj


def add_joint_marker(name, location, collection, parent, role):
    obj = add_control(name, location, collection, parent)
    obj.empty_display_type = "SPHERE"
    obj.empty_display_size = 0.025
    obj["joint_role"] = role
    return obj


def key(obj, frame, location=None, rotation=None):
    if location is not None:
        obj.location = location
    if rotation is not None:
        obj.rotation_euler = rotation
    obj.keyframe_insert("location", frame=frame)
    obj.keyframe_insert("rotation_euler", frame=frame)


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def world_bounds(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points))), Vector(
        (max(p.x for p in points), max(p.y for p in points), max(p.z for p in points))
    )


def aabb_penetration(a, b) -> float:
    amin, amax = world_bounds(a)
    bmin, bmax = world_bounds(b)
    overlaps = [min(amax[i], bmax[i]) - max(amin[i], bmin[i]) for i in range(3)]
    return max(0.0, min(overlaps)) if all(value > 0 for value in overlaps) else 0.0


def aabb_gap(a, b) -> float:
    amin, amax = world_bounds(a)
    bmin, bmax = world_bounds(b)
    gaps = [max(0.0, amin[i] - bmax[i], bmin[i] - amax[i]) for i in range(3)]
    return max(gaps)


def clear_factory_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def create_collections(names):
    output = {}
    for name in names:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
        output[name] = collection
    return output


def build_scene(contract):
    clear_factory_scene()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.render.fps = 24
    scene.frame_start = 1
    scene.frame_end = 96
    collections = create_collections(contract["required_collections"])
    controls = collections["06_CONTROLS"]

    clay = make_material("QA_Clay_Iron", (0.19, 0.21, 0.22, 1.0), metallic=0.15, roughness=0.65)
    dark = make_material("QA_Clay_Dark", (0.055, 0.065, 0.07, 1.0), metallic=0.05, roughness=0.78)
    pilot = make_material("QA_Pilot_Envelope", (0.24, 0.09, 0.075, 1.0), roughness=0.85)
    concept_green = make_material("QA_Gren_Skildus_Clay", (0.055, 0.18, 0.105, 1.0), metallic=0.05, roughness=0.8)

    ctrl_torso = add_control("CTRL_Torso", (0.0, 0.0, 1.58), controls)
    ctrl_pelvis = add_control("CTRL_Pelvis", (0.0, 0.0, 1.12), controls)
    ctrl_arm_l = add_control("CTRL_Arm_L", (-0.64, 0.0, 1.91), controls)
    ctrl_arm_r = add_control("CTRL_Arm_R", (0.64, 0.0, 1.91), controls)
    ctrl_fore_l = add_control("CTRL_Forearm_L", (-0.64, 0.0, 1.30), controls, ctrl_arm_l)
    ctrl_fore_r = add_control("CTRL_Forearm_R", (0.64, 0.0, 1.30), controls, ctrl_arm_r)
    ctrl_hand_l = add_control("CTRL_Hand_L", (-0.64, 0.0, 0.86), controls, ctrl_fore_l)
    ctrl_hand_r = add_control("CTRL_Hand_R", (0.64, 0.0, 0.86), controls, ctrl_fore_r)
    ctrl_leg_l = add_control("CTRL_Leg_L", (-0.245, 0.0, 1.08), controls)
    ctrl_leg_r = add_control("CTRL_Leg_R", (0.245, 0.0, 1.08), controls)
    ctrl_foot_l = add_control("CTRL_Foot_L", (-0.27, -0.045, 0.12), controls)
    ctrl_foot_r = add_control("CTRL_Foot_R", (0.27, -0.045, 0.12), controls)
    ctrl_out_l = add_control("CTRL_Outrigger_L", (-0.27, 0.0, 0.075), controls)
    ctrl_out_r = add_control("CTRL_Outrigger_R", (0.27, 0.0, 0.075), controls)

    hull = collections["02_HUMAN_HULL"]
    frame = collections["03_LOAD_FRAME"]
    power = collections["04_POWERPLANT"]
    ground = collections["05_GROUND_INTERFACE"]
    refs = collections["00_REFERENCE"]
    pilot_col = collections["01_PILOT_ENVELOPE"]

    # Human hull and operator cell.
    add_box("Hull_Thoracic", (0.0, -0.015, 1.59), (0.56, 0.38, 0.58), hull, dark, 0.07, parent=ctrl_torso)
    add_uv_sphere("Hull_Helmet", (0.0, -0.055, 2.055), (0.18, 0.15, 0.20), hull, dark, ctrl_torso)
    add_box("Hull_Visor", (0.0, -0.196, 2.07), (0.22, 0.025, 0.055), hull, clay, 0.006, parent=ctrl_torso)
    add_box("Hull_Pelvis", (0.0, -0.005, 1.145), (0.49, 0.34, 0.24), hull, dark, 0.045, parent=ctrl_pelvis)

    # Dominant external load path.
    add_box("Frame_Yoke_Top", (0.0, 0.025, 2.4184), (1.08, 0.18, 0.04), frame, clay, 0.012, parent=ctrl_torso)
    add_box("Frame_Yoke_L", (-0.49, 0.025, 2.225), (0.10, 0.17, 0.38), frame, clay, 0.025, parent=ctrl_torso)
    add_box("Frame_Yoke_R", (0.49, 0.025, 2.225), (0.10, 0.17, 0.38), frame, clay, 0.025, parent=ctrl_torso)
    add_box("Frame_Thoracic_Rail_L", (-0.34, 0.13, 1.64), (0.09, 0.10, 0.92), frame, clay, 0.018, parent=ctrl_torso)
    add_box("Frame_Thoracic_Rail_R", (0.34, 0.13, 1.64), (0.09, 0.10, 0.92), frame, clay, 0.018, parent=ctrl_torso)
    add_box("Frame_Crossmember_Upper", (0.0, 0.12, 1.91), (0.76, 0.10, 0.10), frame, clay, 0.016, parent=ctrl_torso)
    add_box("Frame_Crossmember_Lower", (0.0, 0.12, 1.30), (0.66, 0.11, 0.11), frame, clay, 0.016, parent=ctrl_torso)
    add_box("Frame_Dorsal_Left", (-0.23, 0.285, 1.71), (0.09, 0.10, 0.76), frame, clay, 0.015, parent=ctrl_torso)
    add_box("Frame_Dorsal_Right", (0.23, 0.285, 1.71), (0.09, 0.10, 0.76), frame, clay, 0.015, parent=ctrl_torso)

    # Integrated powerplant, deliberately structural rather than backpack-like.
    add_box("Powerplant_Core", (0.0, 0.42, 1.69), (0.34, 0.18, 0.58), power, dark, 0.035, parent=ctrl_torso)
    for x in (-0.23, 0.23):
        side = "L" if x < 0 else "R"
        add_cylinder(f"Powerplant_Accumulator_{side}", (x, 0.39, 1.63), 0.065, 0.52, power, clay, parent=ctrl_torso)
        add_cylinder(f"Exhaust_{side}", (x, 0.40, 2.14), 0.045, 0.40, power, dark, parent=ctrl_torso)
    add_box("Powerplant_Radiator", (0.0, 0.525, 1.72), (0.30, 0.045, 0.30), power, clay, 0.008, parent=ctrl_torso)

    # Shoulder interfaces and asymmetry.
    add_cylinder("Joint_Shoulder_L", (-0.64, 0.0, 1.92), 0.105, 0.13, frame, clay, rotation=(math.pi / 2, 0, 0), parent=ctrl_arm_l)
    add_cylinder("Joint_Shoulder_R", (0.64, 0.0, 1.92), 0.105, 0.13, frame, clay, rotation=(math.pi / 2, 0, 0), parent=ctrl_arm_r)
    add_box("Gren_Skildus", (-0.72, -0.02, 1.81), (0.24, 0.22, 0.50), frame, concept_green, 0.055, rotation=(0.0, -0.10, -0.04), parent=ctrl_arm_l)
    add_box("Tool_Station_R", (0.71, 0.015, 1.82), (0.24, 0.25, 0.42), frame, clay, 0.035, parent=ctrl_arm_r)
    add_box("Tool_Proxy_R", (0.88, -0.03, 1.60), (0.12, 0.16, 0.34), refs, dark, 0.02, parent=ctrl_arm_r)

    # Long rescue arms and manipulators.
    arm_controls = {
        "L": (ctrl_arm_l, ctrl_fore_l, ctrl_hand_l),
        "R": (ctrl_arm_r, ctrl_fore_r, ctrl_hand_r),
    }
    for side, sign, ctrl in (("L", -1, ctrl_arm_l), ("R", 1, ctrl_arm_r)):
        fore_ctrl, hand_ctrl = arm_controls[side][1:]
        x = sign * 0.64
        add_box(f"Frame_UpperArm_{side}", (x, 0.0, 1.58), (0.18, 0.20, 0.54), frame, clay, 0.035, parent=ctrl)
        add_cylinder(f"Joint_Elbow_{side}", (x, 0.0, 1.30), 0.09, 0.18, frame, dark, rotation=(math.pi / 2, 0, 0), parent=ctrl)
        add_box(f"Frame_Forearm_{side}", (x, -0.01, 1.09), (0.16, 0.18, 0.36), frame, clay, 0.03, parent=fore_ctrl)
        add_box(f"Manipulator_Hand_{side}", (x, -0.025, 0.86), (0.17, 0.16, 0.17), frame, dark, 0.04, parent=hand_ctrl)
        for finger in range(3):
            add_cylinder(
                f"Manipulator_{side}_Finger_{finger}",
                (x + sign * (finger - 1) * 0.038, -0.04, 0.735),
                0.018,
                0.18,
                frame,
                clay,
                parent=hand_ctrl,
                vertices=12,
            )

    # Pelvis-to-ground columns.
    add_box("Frame_Pelvic_Cradle", (0.0, 0.10, 1.12), (0.66, 0.16, 0.20), frame, clay, 0.035, parent=ctrl_pelvis)
    for side, sign, leg_ctrl, foot_ctrl in (("L", -1, ctrl_leg_l, ctrl_foot_l), ("R", 1, ctrl_leg_r, ctrl_foot_r)):
        x = sign * 0.27
        add_cylinder(f"Joint_Hip_{side}", (x, 0.0, 1.12), 0.10, 0.16, frame, dark, rotation=(math.pi / 2, 0, 0), parent=leg_ctrl)
        add_box(f"Frame_Femur_{side}", (x, 0.0, 0.89), (0.20, 0.22, 0.40), frame, clay, 0.035, parent=leg_ctrl)
        add_cylinder(f"Joint_Knee_{side}", (x, -0.015, 0.655), 0.105, 0.18, frame, dark, rotation=(math.pi / 2, 0, 0), parent=leg_ctrl)
        add_box(f"Frame_Shin_{side}", (x, 0.0, 0.42), (0.22, 0.24, 0.38), frame, clay, 0.035, parent=leg_ctrl)
        add_cylinder(f"Joint_Ankle_{side}", (x, -0.02, 0.225), 0.075, 0.16, frame, dark, rotation=(math.pi / 2, 0, 0), parent=foot_ctrl)
        foot = add_box(f"Foot_Chassis_{side}", (x, -0.075, 0.105), (0.34, 0.46, 0.21), ground, clay, 0.035, parent=foot_ctrl)
        foot["primary_foot_reference"] = True

    # Three modes exist, only debris outriggers participate in trailer motion.
    for side, sign, ctrl in (("L", -1, ctrl_out_l), ("R", 1, ctrl_out_r)):
        out = add_box(f"Outrigger_{side}", (sign * 0.39, 0.02, 0.055), (0.28, 0.18, 0.11), ground, dark, 0.018, parent=ctrl)
        out["ground_mode"] = "DEBRIS_OUTRIGGER"
        pin = add_cylinder(f"Rock_Pin_{side}", (sign * 0.27, 0.10, 0.08), 0.026, 0.16, ground, dark, parent=ctrl, vertices=12)
        pin["ground_mode"] = "ROCK_PIN"
        pin.hide_render = True
        clamp = add_box(f"Structural_Clamp_{side}", (sign * 0.27, 0.08, 0.08), (0.18, 0.12, 0.10), ground, dark, 0.01, parent=ctrl)
        clamp["ground_mode"] = "STRUCTURAL_CLAMP"
        clamp.hide_render = True

    # Provisional human envelope and paired articulation landmarks.
    add_uv_sphere("Pilot_Head", (0.0, -0.05, 2.045), (0.105, 0.09, 0.13), pilot_col, pilot, ctrl_torso)
    add_box("Pilot_Torso", (0.0, -0.03, 1.58), (0.34, 0.22, 0.52), pilot_col, pilot, 0.08, parent=ctrl_torso)
    add_box("Pilot_Pelvis", (0.0, -0.02, 1.20), (0.30, 0.20, 0.18), pilot_col, pilot, 0.06, parent=ctrl_pelvis)
    for side, sign, arm_ctrl, leg_ctrl, foot_ctrl in (("L", -1, ctrl_arm_l, ctrl_leg_l, ctrl_foot_l), ("R", 1, ctrl_arm_r, ctrl_leg_r, ctrl_foot_r)):
        fore_ctrl, hand_ctrl = arm_controls[side][1:]
        add_cylinder(f"Pilot_UpperArm_{side}", (sign * 0.31, -0.035, 1.56), 0.038, 0.50, pilot_col, pilot, parent=arm_ctrl, vertices=12)
        add_cylinder(f"Pilot_Forearm_{side}", (sign * 0.31, -0.035, 1.08), 0.034, 0.40, pilot_col, pilot, parent=fore_ctrl, vertices=12)
        add_cylinder(f"Pilot_Leg_{side}", (sign * 0.14, -0.025, 0.76), 0.052, 0.82, pilot_col, pilot, parent=leg_ctrl, vertices=12)
        pilot_joints = {
            "SHOULDER": (sign * 0.31, -0.035, 1.82),
            "ELBOW": (sign * 0.31, -0.035, 1.30),
            "HIP": (sign * 0.14, -0.025, 1.16),
            "KNEE": (sign * 0.14, -0.025, 0.65),
            "ANKLE": (sign * 0.14, -0.025, 0.24),
        }
        chassis_joints = {
            "SHOULDER": (sign * 0.64, 0.0, 1.92),
            "ELBOW": (sign * 0.64, 0.0, 1.30),
            "HIP": (sign * 0.27, 0.0, 1.12),
            "KNEE": (sign * 0.27, -0.015, 0.655),
            "ANKLE": (sign * 0.27, -0.02, 0.225),
        }
        parents = {"SHOULDER": arm_ctrl, "ELBOW": fore_ctrl, "HIP": leg_ctrl, "KNEE": leg_ctrl, "ANKLE": foot_ctrl}
        for role in pilot_joints:
            add_joint_marker(f"PILOT_JOINT_{role}_{side}", pilot_joints[role], pilot_col, parents[role], role)
            add_joint_marker(f"CHASSIS_JOINT_{role}_{side}", chassis_joints[role], controls, parents[role], role)

    # Review load and floor are excluded from chassis height.
    floor = add_box("QA_Substrate", (0.0, 0.0, -0.04), (4.0, 4.0, 0.08), refs, dark, 0.0)
    floor["qa_count_height"] = False
    load = add_box("QA_Overhead_Load", (0.0, -0.03, 2.48), (1.30, 0.28, 0.08), refs, dark, 0.01)
    load["qa_count_height"] = False
    load.hide_render = True

    # Deterministic test motion. Foot chassis controls remain fixed after F48.
    all_ctrls = (
        ctrl_torso, ctrl_pelvis, ctrl_arm_l, ctrl_arm_r, ctrl_fore_l, ctrl_fore_r,
        ctrl_hand_l, ctrl_hand_r, ctrl_leg_l, ctrl_leg_r, ctrl_foot_l, ctrl_foot_r,
        ctrl_out_l, ctrl_out_r,
    )
    neutral_locations = {ctrl.name: tuple(ctrl.location) for ctrl in all_ctrls}
    for ctrl in all_ctrls:
        key(ctrl, 1, neutral_locations[ctrl.name], (0.0, 0.0, 0.0))
    key(ctrl_leg_l, 24, (-0.245, -0.12, 1.17), (0.28, 0.0, 0.0))
    key(ctrl_foot_l, 24, (-0.27, -0.16, 0.18), (0.18, 0.0, 0.0))
    key(ctrl_torso, 24, (0.0, 0.03, 1.58), (0.0, 0.0, -0.025))
    for ctrl in all_ctrls:
        key(ctrl, 48, neutral_locations[ctrl.name], (0.0, 0.0, 0.0))
    key(ctrl_torso, 60, (0.0, 0.0, 1.52), (0.0, 0.0, 0.0))
    key(ctrl_pelvis, 60, (0.0, 0.0, 1.06), (0.0, 0.0, 0.0))
    key(ctrl_out_l, 60, (-0.42, 0.0, 0.075), (0.0, 0.0, -0.32))
    key(ctrl_out_r, 60, (0.42, 0.0, 0.075), (0.0, 0.0, 0.32))
    for ctrl in (ctrl_foot_l, ctrl_foot_r):
        key(ctrl, 60, tuple(ctrl.location), (0.0, 0.0, 0.0))
    key(ctrl_arm_l, 72, neutral_locations[ctrl_arm_l.name], (0.0, -2.95, 0.0))
    key(ctrl_arm_r, 72, neutral_locations[ctrl_arm_r.name], (0.0, 2.95, 0.0))
    key(ctrl_fore_l, 72, neutral_locations[ctrl_fore_l.name], (0.0, 1.75, 0.0))
    key(ctrl_fore_r, 72, neutral_locations[ctrl_fore_r.name], (0.0, -1.75, 0.0))
    for ctrl in (ctrl_torso, ctrl_pelvis, ctrl_hand_l, ctrl_hand_r, ctrl_leg_l, ctrl_leg_r, ctrl_foot_l, ctrl_foot_r, ctrl_out_l, ctrl_out_r):
        key(ctrl, 72, tuple(ctrl.location), tuple(ctrl.rotation_euler))
    for ctrl in all_ctrls:
        key(ctrl, 96, tuple(ctrl.location), tuple(ctrl.rotation_euler))

    # Cameras and neutral lighting are saved as QA infrastructure.
    camera_specs = {
        "Cam_Front": ((0.0, -6.2, 1.25), (0.0, 0.0, 1.25), 3.05),
        "Cam_Rear": ((0.0, 6.2, 1.25), (0.0, 0.0, 1.25), 3.05),
        "Cam_Side": ((5.5, 0.0, 1.25), (0.0, 0.0, 1.25), 3.05),
        "Cam_ThreeQuarter": ((4.2, -4.8, 1.38), (0.0, 0.0, 1.30), 3.05),
        "Cam_TrailerPose": ((3.8, -5.4, 1.05), (0.0, 0.0, 1.38), 3.00),
    }
    for name, (location, target, ortho) in camera_specs.items():
        data = bpy.data.cameras.new(name)
        data.type = "ORTHO"
        data.ortho_scale = ortho
        cam = bpy.data.objects.new(name, data)
        cam.location = location
        look_at(cam, target)
        collections["07_QA_CAMERAS"].objects.link(cam)

    world = bpy.data.worlds.new("QA_Neutral_World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.055, 0.06, 0.07, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.45
    scene.world = world
    for name, location, energy, size in (
        ("QA_Key", (-3.5, -4.0, 5.0), 1100.0, 4.0),
        ("QA_Fill", (3.0, -2.0, 3.0), 650.0, 3.0),
        ("QA_Rim", (0.0, 3.0, 4.0), 900.0, 2.5),
    ):
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        lamp = bpy.data.objects.new(name, data)
        lamp.location = location
        look_at(lamp, (0.0, 0.0, 1.2))
        refs.objects.link(lamp)

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 720
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.frame_set(1)
    return collections


def measure_scene(contract):
    scene = bpy.context.scene
    height_objects = [obj for obj in scene.objects if obj.type == "MESH" and obj.get("qa_count_height", False)]
    mins, maxs = zip(*(world_bounds(obj) for obj in height_objects))
    min_z = min(value.z for value in mins)
    max_z = max(value.z for value in maxs)
    height = max_z - min_z
    target = contract["dimensions_m"]["overall_height_target"]
    tolerance = contract["dimensions_m"]["overall_height_tolerance"]
    gates = {
        "height": {"measured_m": height, "target_m": target, "tolerance_m": tolerance, "pass": abs(height - target) <= tolerance},
        "ground": {"measured_min_z_m": min_z, "target_m": 0.0, "tolerance_m": contract["dimensions_m"]["ground_z_tolerance"], "pass": abs(min_z) <= contract["dimensions_m"]["ground_z_tolerance"]},
    }
    scales = {obj.name: list(obj.scale) for obj in height_objects}
    gates["rigid_scales"] = {
        "invalid": [name for name, scale in scales.items() if any(abs(value - 1.0) > 1e-6 for value in scale)],
    }
    gates["rigid_scales"]["pass"] = not gates["rigid_scales"]["invalid"]

    joint_offsets = {}
    for frame in contract["motion"]["tracked_frames"]:
        scene.frame_set(frame)
        joint_offsets[str(frame)] = {}
        for side in ("L", "R"):
            for role in ("SHOULDER", "ELBOW", "HIP", "KNEE", "ANKLE"):
                pilot = scene.objects[f"PILOT_JOINT_{role}_{side}"].matrix_world.translation
                chassis = scene.objects[f"CHASSIS_JOINT_{role}_{side}"].matrix_world.translation
                joint_offsets[str(frame)][f"{role}_{side}"] = (pilot - chassis).length

    foot_positions = {}
    for frame in contract["motion"]["planted_frames"]:
        scene.frame_set(frame)
        foot_positions[str(frame)] = {
            side: list(scene.objects[f"CTRL_Foot_{side}"].matrix_world.translation) for side in ("L", "R")
        }
    reference = foot_positions[str(contract["motion"]["planted_frames"][0])]
    max_foot_translation = max(
        (Vector(position) - Vector(reference[side])).length
        for positions in foot_positions.values()
        for side, position in positions.items()
    )
    gates["planted_feet"] = {
        "reference_points": foot_positions,
        "max_translation_m": max_foot_translation,
        "threshold_m": contract["motion"]["primary_foot_translation_max_m"],
        "pass": max_foot_translation <= contract["motion"]["primary_foot_translation_max_m"],
    }

    collision_results = {}
    max_allowed = contract["collision"]["provisional_penetration_max_m"]
    for frame in contract["motion"]["tracked_frames"]:
        scene.frame_set(frame)
        collision_results[str(frame)] = {}
        for left, right in contract["collision"]["pairs"]:
            depth = aabb_penetration(scene.objects[left], scene.objects[right])
            collision_results[str(frame)][f"{left}::{right}"] = depth
    max_collision = max(value for frame in collision_results.values() for value in frame.values())
    gates["provisional_collisions"] = {
        "representation": contract["collision"]["representation"],
        "threshold_m": max_allowed,
        "by_frame": collision_results,
        "max_penetration_m": max_collision,
        "pass": max_collision <= max_allowed,
    }

    scene.frame_set(72)
    hand_gaps = {
        side: aabb_gap(scene.objects[f"Manipulator_Hand_{side}"], scene.objects["QA_Overhead_Load"])
        for side in ("L", "R")
    }
    gates["overhead_hand_contact"] = {
        "frame": 72,
        "gaps_m": hand_gaps,
        "threshold_m": contract["motion"]["overhead_hand_contact_gap_max_m"],
        "pass": max(hand_gaps.values()) <= contract["motion"]["overhead_hand_contact_gap_max_m"],
    }

    support = {}
    for frame in (48, 60, 72, 96):
        scene.frame_set(frame)
        left = scene.objects["CTRL_Foot_L"].matrix_world.translation
        right = scene.objects["CTRL_Foot_R"].matrix_world.translation
        center = scene.objects["CTRL_Pelvis"].matrix_world.translation
        min_x, max_x = min(left.x, right.x) - 0.17, max(left.x, right.x) + 0.17
        min_y, max_y = min(left.y, right.y) - 0.23, max(left.y, right.y) + 0.23
        support[str(frame)] = {
            "reference_center_xy": [center.x, center.y],
            "support_polygon_aabb_xy": [[min_x, min_y], [max_x, max_y]],
            "inside_diagnostic": min_x <= center.x <= max_x and min_y <= center.y <= max_y,
            "claim_boundary": "DIAGNOSTIC_ONLY_NO_STABILITY_OR_LOAD_CLAIM",
        }

    scene.frame_set(1)
    return {
        "gates": gates,
        "pilot_to_chassis_offsets_m": joint_offsets,
        "support_center_diagnostic": support,
        "rigid_object_scales": scales,
        "rigid_driver_inventory": {
            obj.name: obj.parent.name if obj.parent else None
            for obj in height_objects
            if obj.get("rigid_module", False)
        },
    }


def render_reviews(output_sha: str):
    scene = bpy.context.scene
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    jobs = (
        ("front-clay.png", "Cam_Front", 1),
        ("rear-clay.png", "Cam_Rear", 1),
        ("side-clay.png", "Cam_Side", 1),
        ("three-quarter-clay.png", "Cam_ThreeQuarter", 1),
        ("trailer-pose-clay.png", "Cam_TrailerPose", 96),
    )
    results = {}
    for filename, camera, frame in jobs:
        scene.frame_set(frame)
        scene.objects["QA_Overhead_Load"].hide_render = frame != 96
        scene.camera = scene.objects[camera]
        path = EVIDENCE_DIR / filename
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        results[filename] = {"frame": frame, "camera": camera, "sha256": sha256(path), "candidate_sha256": output_sha}
    return results


def main():
    args = parse_args()
    output = args.output.resolve()
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    if output.exists():
        fail("PRE_BUILD", "output path already exists", {"path": str(output)})
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    concept = ROOT / contract["approved_concept"]["path"]
    actual_concept_sha = sha256(concept)
    if actual_concept_sha != contract["approved_concept"]["sha256"]:
        fail("PRE_BUILD", "approved concept hash mismatch", {"actual": actual_concept_sha})
    if args.source_repo_state != "CLEAN":
        fail("PRE_BUILD", "host reported a dirty repository", {"status": args.source_repo_state})
    if bpy.data.filepath:
        fail("PRE_BUILD", "builder must start from factory startup, not an opened blend", {"filepath": bpy.data.filepath})

    build_scene(contract)
    measurements = measure_scene(contract)
    failed = [name for name, result in measurements["gates"].items() if not result.get("pass", False)]
    if failed:
        fail("MACHINE_GATE", "one or more internal gates failed", {"failed": failed, "gates": measurements["gates"]})

    bpy.context.scene["plan_id"] = contract["plan_id"]
    bpy.context.scene["approved_concept_sha256"] = actual_concept_sha
    bpy.context.scene["claim_boundary"] = "MACHINE_PASS_DOES_NOT_EQUAL_CHASSIS_APPROVAL"
    bpy.context.scene.frame_set(1)
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output), check_existing=False)
    candidate_sha = sha256(output)

    record = {
        "schema_version": "1.0",
        "claim_class": "OBSERVED",
        "gate": "VAREK_MOTION_CHASSIS_V1_MACHINE",
        "overall": "PASS",
        "claim_boundary": "MACHINE_PASS_DOES_NOT_EQUAL_CHASSIS_APPROVAL",
        "plan_id": contract["plan_id"],
        "plan_git_commit": args.plan_git_commit,
        "plan_file_sha256": sha256(PLAN),
        "contract_file_sha256": sha256(CONTRACT_PATH),
        "source_git_commit": args.source_git_commit,
        "source_repository_state": args.source_repo_state,
        "provenance_capture_mode": "HOST_PRECHECKED_ARGUMENTS",
        "builder_script_sha256": sha256(Path(__file__).resolve()),
        "validator_script_sha256": sha256(VALIDATOR),
        "approved_concept": {"path": str(concept.relative_to(ROOT)), "sha256": actual_concept_sha},
        "candidate": {"path": str(output), "sha256": candidate_sha},
        "environment": {
            "platform": platform.platform(),
            "blender_executable": str(Path(bpy.app.binary_path).resolve()),
            "blender_version": bpy.app.version_string,
            "embedded_python": sys.version,
            "build_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        },
        "scene": {
            "unit_system": bpy.context.scene.unit_settings.system,
            "unit_scale": bpy.context.scene.unit_settings.scale_length,
            "fps": bpy.context.scene.render.fps,
        },
        **measurements,
    }
    measurement_path = EVIDENCE_DIR / "measurements.json"
    measurement_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    renders = render_reviews(candidate_sha)
    post_render_sha = sha256(output)
    if post_render_sha != candidate_sha:
        fail("POST_RENDER", "candidate bytes changed during review render", {"before": candidate_sha, "after": post_render_sha})
    record["review_renders"] = renders
    record["candidate"]["post_render_sha256"] = post_render_sha
    measurement_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    if FAILURE_PATH.exists():
        FAILURE_PATH.unlink()
    print(f"VAREK_MOTION_CHASSIS_V1_PASS={candidate_sha}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        print(f"VAREK_MOTION_CHASSIS_V1_FAIL={exc}", file=sys.stderr)
        raise SystemExit(1)
    except Exception as exc:
        if not FAILURE_PATH.exists():
            EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
            FAILURE_PATH.write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "claim_class": "OBSERVED",
                        "gate": "VAREK_MOTION_CHASSIS_V1",
                        "overall": "FAIL",
                        "phase": "UNEXPECTED_EXCEPTION",
                        "message": f"{type(exc).__name__}: {exc}",
                        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
        print(f"VAREK_MOTION_CHASSIS_V1_ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
