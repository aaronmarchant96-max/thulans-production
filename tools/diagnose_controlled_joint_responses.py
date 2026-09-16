from __future__ import annotations
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector, Quaternion, Matrix

ROOT = Path("/home/aaron/animation/thulans-production")
TEST_BLEND = ROOT / "blender/candidates/varek-v55-hand-physics.blend"
READBACK_JSON = ROOT / "evidence/varek-v55-mechanical-grip/full-hand-readback.json"

SUSPECT_JOINTS = [
    ("Digit2 MCP", "Palm_Plate_L", "Digit2_Phalanx1_L"),
    ("Digit2 PIP", "Digit2_Phalanx1_L", "Digit2_Phalanx2_L"),
    ("Digit2 DIP", "Digit2_Phalanx2_L", "Digit2_Phalanx3_L"),
    ("Thumb Proximal", "Palm_Plate_L", "Thumb_Phalanx1_L"),
    ("Thumb Distal", "Thumb_Phalanx1_L", "Thumb_Phalanx2_L")
]

ALL_JOINTS = [
    ("Palm_Plate_L", "Gimbal_Yoke_Outer_L"),
    ("Gimbal_Yoke_Outer_L", "Gimbal_Yoke_Inner_L"),
    ("Palm_Plate_L", "Digit1_Phalanx1_L"),
    ("Digit1_Phalanx1_L", "Digit1_Phalanx2_L"),
    ("Digit1_Phalanx2_L", "Digit1_Phalanx3_L"),
    ("Palm_Plate_L", "Digit2_Phalanx1_L"),
    ("Digit2_Phalanx1_L", "Digit2_Phalanx2_L"),
    ("Digit2_Phalanx2_L", "Digit2_Phalanx3_L"),
    ("Palm_Plate_L", "Digit3_Phalanx1_L"),
    ("Digit3_Phalanx1_L", "Digit3_Phalanx2_L"),
    ("Digit3_Phalanx2_L", "Digit3_Phalanx3_L"),
    ("Palm_Plate_L", "Thumb_Phalanx1_L"),
    ("Thumb_Phalanx1_L", "Thumb_Phalanx2_L")
]

def calculate_signed_twist(q_delta: Quaternion, axis_parent: Vector) -> float:
    q_v = Vector((q_delta.x, q_delta.y, q_delta.z))
    proj = q_v.dot(axis_parent)
    twist_q = Quaternion((q_delta.w, axis_parent.x * proj, axis_parent.y * proj, axis_parent.z * proj)).normalized()
    angle = 2.0 * math.atan2(Vector((twist_q.x, twist_q.y, twist_q.z)).length, twist_q.w)
    if Vector((twist_q.x, twist_q.y, twist_q.z)).dot(axis_parent) < 0:
        angle = -angle
    return math.degrees(angle)

def run_controlled_test(label: str, p_name: str, c_name: str, command_sign: float, readback_limits: dict) -> dict:
    bpy.ops.wm.open_mainfile(filepath=str(TEST_BLEND))
    scene = bpy.context.scene

    scene.use_gravity = False
    scene.gravity = (0.0, 0.0, 0.0)

    # Disable rigid body collision processing on all non-evaluated finger colliders
    for obj in bpy.data.objects:
        if obj.rigid_body and obj.name not in (p_name, c_name):
            obj.rigid_body.enabled = False

    p_obj = bpy.data.objects.get(p_name)
    c_obj = bpy.data.objects.get(c_name)

    # Make parent body kinematic passive anchor during isolation test
    if p_obj and p_obj.rigid_body:
        p_obj.rigid_body.type = "PASSIVE"
        p_obj.rigid_body.kinematic = True

    for p, c in ALL_JOINTS:
        m = bpy.data.objects.get(f"Constraint_Motor_{p}_to_{c}")
        if m and m.rigid_body_constraint:
            m.rigid_body_constraint.motor_ang_target_velocity = 0.0

    target_m = bpy.data.objects.get(f"Constraint_Motor_{p_name}_to_{c_name}")
    target_h = bpy.data.objects.get(f"Constraint_Hinge_{p_name}_to_{c_name}")

    if target_m and target_m.rigid_body_constraint:
        target_m.rigid_body_constraint.motor_ang_target_velocity = command_sign * 1.5

    scene.frame_set(1)
    p_q_rest = p_obj.matrix_world.to_quaternion()
    c_q_rest = c_obj.matrix_world.to_quaternion()
    q_rest = p_q_rest.inverted() @ c_q_rest

    pivot_rest_world = target_h.matrix_world.translation.copy()
    p_anchor_local = p_obj.matrix_world.inverted() @ pivot_rest_world
    c_anchor_local = c_obj.matrix_world.inverted() @ pivot_rest_world

    low_lim, up_lim = readback_limits.get(f"{p_name}->{c_name}", (-10.0, 90.0))

    frame_logs = []
    max_anchor_error = 0.0

    for f in range(1, 31):
        scene.frame_set(f)
        p_q_curr = p_obj.matrix_world.to_quaternion()
        c_q_curr = c_obj.matrix_world.to_quaternion()
        q_curr = p_q_curr.inverted() @ c_q_curr
        q_delta_parent = q_curr @ q_rest.inverted()

        hinge_z_world = target_h.matrix_world.to_3x3() @ Vector((0.0, 0.0, 1.0))
        hinge_axis_parent = (p_q_curr.inverted() @ hinge_z_world).normalized()
        angle = calculate_signed_twist(q_delta_parent, hinge_axis_parent)

        p_anchor_curr = p_obj.matrix_world @ p_anchor_local
        c_anchor_curr = c_obj.matrix_world @ c_anchor_local
        anchor_err = (p_anchor_curr - c_anchor_curr).length
        if anchor_err > max_anchor_error:
            max_anchor_error = anchor_err

        frame_logs.append({
            "frame": f,
            "angle_deg": angle,
            "anchor_error_m": anchor_err
        })

    f1_ang = frame_logs[0]["angle_deg"]
    f5_ang = frame_logs[4]["angle_deg"]
    initial_delta_f1_f5 = f5_ang - f1_ang

    return {
        "joint_label": label,
        "parent": p_name,
        "child": c_name,
        "command_sign": command_sign,
        "configured_limits": [low_lim, up_lim],
        "initial_delta_f1_f5_deg": initial_delta_f1_f5,
        "final_angle_f30_deg": frame_logs[-1]["angle_deg"],
        "max_anchor_separation_error_m": max_anchor_error,
        "frame_logs": frame_logs
    }

def main() -> int:
    if not TEST_BLEND.exists() or not READBACK_JSON.exists():
        print("HARD FAIL: Blend or readback JSON missing.")
        return 1

    rb = json.loads(READBACK_JSON.read_text())
    readback_limits = {}
    for j in rb.get("serialized_joints", []):
        key = j["parent"] + "->" + j["child"]
        readback_limits[key] = tuple(j["hinge_limits_deg"])

    print("=== ISOLATED CONTROLLED DIAGNOSTIC BATTERY (PARENT KINEMATIC ANCHORED, GRAVITY OFF) ===")

    all_control_results = []
    for label, p_name, c_name in SUSPECT_JOINTS:
        c_pos = run_controlled_test(label, p_name, c_name, +1.0, readback_limits)
        c_neg = run_controlled_test(label, p_name, c_name, -1.0, readback_limits)
        all_control_results.extend([c_pos, c_neg])

        for r in [c_pos, c_neg]:
            f1_str = f"{r["frame_logs"][0]["angle_deg"]:+.2f}"
            f5_str = f"{r["frame_logs"][4]["angle_deg"]:+.2f}"
            delta_str = f"{r["initial_delta_f1_f5_deg"]:+.2f}"
            f30_str = f"{r["final_angle_f30_deg"]:+.2f}"
            anc_mm = r["max_anchor_separation_error_m"] * 1000.0
            print(f"{r["joint_label"]} | Cmd={r["command_sign"]:+.1f} | F1={f1_str}deg | F5={f5_str}deg | F1-F5_Delta={delta_str}deg | F30={f30_str}deg | MaxAnchorErr={anc_mm:.6f}mm")

    out_data = {
        "derivative_file": str(TEST_BLEND),
        "derivative_sha256": rb.get("derivative_sha256"),
        "controlled_test_results": all_control_results
    }
    tmp_out = Path("/tmp/controlled-joint-responses.json")
    tmp_out.write_text(json.dumps(out_data, indent=2), encoding="utf-8")
    print(f"\nExported Controlled Diagnostics to: {tmp_out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
