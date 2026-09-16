"""Single-Joint Isolation Characterization Diagnostic Harness.
"""
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

def evaluate_single_joint_command(label: str, p_name: str, c_name: str, command_sign: float, readback_limits: dict) -> dict:
    bpy.ops.wm.open_mainfile(filepath=str(TEST_BLEND))
    scene = bpy.context.scene

    for p, c in ALL_JOINTS:
        m = bpy.data.objects.get(f"Constraint_Motor_{p}_to_{c}")
        if m and m.rigid_body_constraint:
            m.rigid_body_constraint.motor_ang_target_velocity = 0.0

    target_m = bpy.data.objects.get(f"Constraint_Motor_{p_name}_to_{c_name}")
    target_h = bpy.data.objects.get(f"Constraint_Hinge_{p_name}_to_{c_name}")
    p_obj = bpy.data.objects.get(p_name)
    c_obj = bpy.data.objects.get(c_name)

    motor_cap = target_m.rigid_body_constraint.motor_ang_max_impulse if target_m and target_m.rigid_body_constraint else 0.0
    if target_m and target_m.rigid_body_constraint:
        target_m.rigid_body_constraint.motor_ang_target_velocity = command_sign * 1.5

    scene.frame_set(1)
    p_q_rest = p_obj.matrix_world.to_quaternion()
    c_q_rest = c_obj.matrix_world.to_quaternion()
    q_rest = p_q_rest.inverted() @ c_q_rest

    pivot_rest_world = target_h.matrix_world.translation.copy()
    start_angle = 0.0

    for f in range(1, 31):
        scene.frame_set(f)

    p_q_end = p_obj.matrix_world.to_quaternion()
    c_q_end = c_obj.matrix_world.to_quaternion()
    q_curr = p_q_end.inverted() @ c_q_end
    q_delta_parent = q_curr @ q_rest.inverted()

    hinge_z_world_end = target_h.matrix_world.to_3x3() @ Vector((0.0, 0.0, 1.0))
    hinge_axis_parent_end = (p_q_end.inverted() @ hinge_z_world_end).normalized()
    end_angle = calculate_signed_twist(q_delta_parent, hinge_axis_parent_end)
    signed_delta = end_angle - start_angle

    pivot_end_world = target_h.matrix_world.translation.copy()
    pivot_translation_error_m = (pivot_end_world - pivot_rest_world).length

    low_lim, up_lim = readback_limits.get(f"{p_name}->{c_name}", (-10.0, 90.0))
    dist_to_lower_stop_deg = end_angle - low_lim
    dist_to_upper_stop_deg = up_lim - end_angle

    return {
        "joint_label": label,
        "parent": p_name,
        "child": c_name,
        "command_sign": command_sign,
        "start_angle_deg": start_angle,
        "end_angle_deg": end_angle,
        "signed_delta_deg": signed_delta,
        "limit_contract_deg": [low_lim, up_lim],
        "dist_to_lower_stop_deg": dist_to_lower_stop_deg,
        "dist_to_upper_stop_deg": dist_to_upper_stop_deg,
        "motor_impulse_cap": motor_cap,
        "pivot_translation_error_m": pivot_translation_error_m
    }

def main() -> int:
    if not TEST_BLEND.exists() or not READBACK_JSON.exists():
        print("HARD FAIL: Blend or readback JSON missing.")
        return 1

    rb = json.loads(READBACK_JSON.read_text())
    readback_limits = {f"{j["parent"]}->{j["child"]}": tuple(j["hinge_limits_deg"]) for j in rb.get("serialized_joints", [])}

    results = []
    print("=== SINGLE-JOINT ISOLATION CHARACTERIZATION BATTERY ===")

    for label, p_name, c_name in SUSPECT_JOINTS:
        res_pos = evaluate_single_joint_command(label, p_name, c_name, +1.0, readback_limits)
        res_neg = evaluate_single_joint_command(label, p_name, c_name, -1.0, readback_limits)
        results.extend([res_pos, res_neg])

        for r in [res_pos, res_neg]:
            print(f"{r["joint_label"]} | Cmd={r["command_sign"]:+.1f} | Start={r["start_angle_deg"]:+.2f}deg | End={r["end_angle_deg"]:+.2f}deg | Delta={r["signed_delta_deg"]:+.2f}deg | Limits={r["limit_contract_deg"]} | MotorCap={r["motor_impulse_cap"]:.1f} | PivotErr={r["pivot_translation_error_m"]*1000.0:.3f}mm")

    out_data = {
        "derivative_file": str(TEST_BLEND),
        "derivative_sha256": rb.get("derivative_sha256"),
        "single_joint_isolation_results": results
    }
    
    tmp_out = Path("/tmp/single-joint-response-isolation.json")
    tmp_out.write_text(json.dumps(out_data, indent=2), encoding="utf-8")
    print(f"\nSaved Isolation Characterization Report to: {tmp_out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
