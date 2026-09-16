"""Execute Causally Isolated Scenarios A1 (Digit Closure) & A2 (Wrist Gimbal) & Scenario B (Maul Drop).

Fixes:
1. Frame-consistent Signed Twist Angle Calculation around local hinge axis:
   Qrest = Qparent_rest.inv() * Qchild_rest
   Qcurr = Qparent_curr.inv() * Qchild_curr
   Qdelta = Qrest.inv() * Qcurr
   hinge_axis_parent = Qparent_curr.inv() * hinge_axis_world
   signed_angle = extract_signed_twist(Qdelta, hinge_axis_parent)
2. Decoupled A1 (Digits open -> close -> reopen with wrist held neutral).
3. Decoupled A2 (Wrist pitch & yaw exercised independently with digits neutral).
4. Grasp Envelope Aperture Distance Logging (Fingertips -> Grip Center).
"""

from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector, Quaternion, Matrix

ROOT = Path("/home/aaron/animation/thulans-production")
TEST_BLEND = ROOT / "blender/candidates/varek-v55-hand-physics.blend"
READBACK_JSON = ROOT / "evidence/varek-v55-mechanical-grip/full-hand-readback.json"
OUT_DIAGNOSTIC_JSON = ROOT / "evidence/varek-v55-mechanical-grip/full-hand-diagnostic.json"
OUT_MAUL_DROP_JSON = ROOT / "evidence/varek-v55-mechanical-grip/isolated-maul-drop.json"

WRIST_JOINT_SPECS = [
    ("Palm_Plate_L", "Gimbal_Yoke_Outer_L", 1.0),
    ("Gimbal_Yoke_Outer_L", "Gimbal_Yoke_Inner_L", 1.0)
]

DIGIT_JOINT_SPECS = [
    ("Palm_Plate_L", "Digit1_Phalanx1_L", 1.5, +1.0),
    ("Digit1_Phalanx1_L", "Digit1_Phalanx2_L", 1.5, +1.0),
    ("Digit1_Phalanx2_L", "Digit1_Phalanx3_L", 1.5, +1.0),
    ("Palm_Plate_L", "Digit2_Phalanx1_L", 1.5, +1.0),
    ("Digit2_Phalanx1_L", "Digit2_Phalanx2_L", 1.5, +1.0),
    ("Digit2_Phalanx2_L", "Digit2_Phalanx3_L", 1.5, +1.0),
    ("Palm_Plate_L", "Digit3_Phalanx1_L", 1.5, +1.0),
    ("Digit3_Phalanx1_L", "Digit3_Phalanx2_L", 1.5, +1.0),
    ("Digit3_Phalanx2_L", "Digit3_Phalanx3_L", 1.5, +1.0),
    ("Palm_Plate_L", "Thumb_Phalanx1_L", 1.2, +1.0),
    ("Thumb_Phalanx1_L", "Thumb_Phalanx2_L", 1.2, +1.0)
]

def calculate_signed_twist(q_delta: Quaternion, axis_parent: Vector) -> float:
    q_v = Vector((q_delta.x, q_delta.y, q_delta.z))
    proj = q_v.dot(axis_parent)
    twist_q = Quaternion((q_delta.w, axis_parent.x * proj, axis_parent.y * proj, axis_parent.z * proj)).normalized()
    angle = 2.0 * math.atan2(Vector((twist_q.x, twist_q.y, twist_q.z)).length, twist_q.w)
    if Vector((twist_q.x, twist_q.y, twist_q.z)).dot(axis_parent) < 0:
        angle = -angle
    return math.degrees(angle)

def main() -> int:
    if not TEST_BLEND.exists() or not READBACK_JSON.exists():
        raise FileNotFoundError("HARD FAIL: Required blend or readback audit missing")

    current_sha256 = hashlib.sha256(TEST_BLEND.read_bytes()).hexdigest()
    readback_data = json.loads(READBACK_JSON.read_text())
    if current_sha256 != readback_data.get("derivative_sha256"):
        raise RuntimeError("PROV FAIL: Cryptographic hash mismatch!")

    # =========================================================================
    # SCENARIO A1: Digit Closure & Reopen (Wrist Neutral)
    # =========================================================================
    bpy.ops.wm.open_mainfile(filepath=str(TEST_BLEND))
    scene = bpy.context.scene
    palm = bpy.data.objects.get("Palm_Plate_L")

    # Record baseline rest transform quaternions (Frame 1)
    scene.frame_set(1)
    rest_quats = {}
    for p_name, c_name, *_ in DIGIT_JOINT_SPECS + WRIST_JOINT_SPECS:
        p_obj = bpy.data.objects.get(p_name)
        c_obj = bpy.data.objects.get(c_name)
        p_q = p_obj.matrix_world.to_quaternion()
        c_q = c_obj.matrix_world.to_quaternion()
        rest_quats[f"{p_name}->{c_name}"] = p_q.inverted() @ c_q

    # Capture rest pose grip shaft axis in palm-local frame
    main_shaft = next(o for o in bpy.data.objects if 'shaft' in o.name.lower() and o.type == 'MESH')
    palm_rest_inv = palm.matrix_world.inverted()
    grip_point_palm = palm_rest_inv @ main_shaft.matrix_world.translation
    grip_dir_world = (main_shaft.matrix_world.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
    grip_dir_palm = (palm_rest_inv.to_3x3() @ grip_dir_world).normalized()

    a1_logs = []
    for frame in range(1, 61):
        for item in DIGIT_JOINT_SPECS:
            p_name, c_name = item[0], item[1]
            close_vel = item[2]
            drive_sign = item[3] if len(item) > 3 else +1.0
            m_obj = bpy.data.objects.get(f"Constraint_Motor_{p_name}_to_{c_name}")
            if m_obj and m_obj.rigid_body_constraint:
                if frame <= 15:
                    m_obj.rigid_body_constraint.motor_ang_target_velocity = -close_vel * drive_sign
                elif frame <= 40:
                    m_obj.rigid_body_constraint.motor_ang_target_velocity = +close_vel * drive_sign
                else:
                    m_obj.rigid_body_constraint.motor_ang_target_velocity = -close_vel * drive_sign

        for p_name, c_name, _ in WRIST_JOINT_SPECS:
            m_obj = bpy.data.objects.get(f"Constraint_Motor_{p_name}_to_{c_name}")
            if m_obj and m_obj.rigid_body_constraint:
                m_obj.rigid_body_constraint.motor_ang_target_velocity = 0.0

        scene.frame_set(frame)
        
        joint_signed_twists = {}
        for p_name, c_name, *_ in DIGIT_JOINT_SPECS:
            p_obj = bpy.data.objects.get(p_name)
            c_obj = bpy.data.objects.get(c_name)
            h_obj = bpy.data.objects.get(f"Constraint_Hinge_{p_name}_to_{c_name}")
            
            p_q = p_obj.matrix_world.to_quaternion()
            c_q = c_obj.matrix_world.to_quaternion()
            q_curr = p_q.inverted() @ c_q
            q_rest = rest_quats[f"{p_name}->{c_name}"]
            q_delta_parent = q_curr @ q_rest.inverted()
            
            hinge_z_world = h_obj.matrix_world.to_3x3() @ Vector((0.0, 0.0, 1.0))
            hinge_axis_parent = (p_q.inverted() @ hinge_z_world).normalized()
            
            joint_signed_twists[f"{p_name}->{c_name}"] = calculate_signed_twist(q_delta_parent, hinge_axis_parent)

        # Grasp Envelope Distance Metrics
        fingertip_names = ["Digit1_Phalanx3_L", "Digit2_Phalanx3_L", "Digit3_Phalanx3_L", "Thumb_Phalanx2_L"]
        palm_curr_inv = palm.matrix_world.inverted()
        
        point_aperture_distances = {}
        radial_aperture_distances = {}
        for name in fingertip_names:
            ft_obj = bpy.data.objects.get(name)
            if ft_obj:
                pt_palm = palm_curr_inv @ ft_obj.matrix_world.translation
                point_aperture_distances[name] = pt_palm.length
                
                v = pt_palm - grip_point_palm
                v_perp = v - (v.dot(grip_dir_palm)) * grip_dir_palm
                radial_aperture_distances[name] = v_perp.length

        a1_logs.append({
            "frame": frame,
            "phase": "open" if frame <= 15 else ("close" if frame <= 40 else "reopen"),
            "relative_signed_twist_deg": joint_signed_twists,
            "fingertip_aperture_distances_m": point_aperture_distances,
            "fingertip_radial_aperture_distances_m": radial_aperture_distances
        })

    # Helper function for A2 joint state sampling
    def run_a2_subscenario(actuated_wrist_joint: str, close_vel: float) -> list[dict]:
        bpy.ops.wm.open_mainfile(filepath=str(TEST_BLEND))
        sub_scene = bpy.context.scene
        
        # Neutralize all digit motors
        for p_name, c_name, *_ in DIGIT_JOINT_SPECS:
            m_obj = bpy.data.objects.get(f"Constraint_Motor_{p_name}_to_{c_name}")
            if m_obj and m_obj.rigid_body_constraint:
                m_obj.rigid_body_constraint.motor_ang_target_velocity = 0.0
                
        # Neutralize all wrist motors first
        for p_name, c_name, *_ in WRIST_JOINT_SPECS:
            m_obj = bpy.data.objects.get(f"Constraint_Motor_{p_name}_to_{c_name}")
            if m_obj and m_obj.rigid_body_constraint:
                m_obj.rigid_body_constraint.motor_ang_target_velocity = 0.0

        sub_logs = []
        for frame in range(1, 61):
            # Actuate only the targeted wrist joint
            for p_name, c_name, vel in WRIST_JOINT_SPECS:
                key = f"{p_name}->{c_name}"
                if key == actuated_wrist_joint:
                    m_obj = bpy.data.objects.get(f"Constraint_Motor_{p_name}_to_{c_name}")
                    if m_obj and m_obj.rigid_body_constraint:
                        m_obj.rigid_body_constraint.motor_ang_target_velocity = vel if frame <= 30 else -vel

            sub_scene.frame_set(frame)
            
            all_twists = {}
            for p_name, c_name, *_ in WRIST_JOINT_SPECS + DIGIT_JOINT_SPECS:
                p_obj = bpy.data.objects.get(p_name)
                c_obj = bpy.data.objects.get(c_name)
                h_obj = bpy.data.objects.get(f"Constraint_Hinge_{p_name}_to_{c_name}")
                
                p_q = p_obj.matrix_world.to_quaternion()
                c_q = c_obj.matrix_world.to_quaternion()
                q_curr = p_q.inverted() @ c_q
                q_rest = rest_quats[f"{p_name}->{c_name}"]
                q_delta_parent = q_curr @ q_rest.inverted()
                
                hinge_z_world = h_obj.matrix_world.to_3x3() @ Vector((0.0, 0.0, 1.0))
                hinge_axis_parent = (p_q.inverted() @ hinge_z_world).normalized()
                all_twists[f"{p_name}->{c_name}"] = calculate_signed_twist(q_delta_parent, hinge_axis_parent)

            sub_logs.append({
                "frame": frame,
                "phase": "forward" if frame <= 30 else "reverse",
                "signed_twist_deg": all_twists
            })
        return sub_logs

    # =========================================================================
    # SCENARIO A2-PITCH & A2-YAW (Independent Wrist Gimbal Exercises)
    # =========================================================================
    a2_pitch_logs = run_a2_subscenario("Palm_Plate_L->Gimbal_Yoke_Outer_L", 1.0)
    a2_yaw_logs = run_a2_subscenario("Gimbal_Yoke_Outer_L->Gimbal_Yoke_Inner_L", 1.0)

    runner_path = Path(__file__).resolve()
    runner_sha256 = hashlib.sha256(runner_path.read_bytes()).hexdigest()
    oracle_path = ROOT / "tools/validate_hand_physics_results.py"
    oracle_sha256 = hashlib.sha256(oracle_path.read_bytes()).hexdigest() if oracle_path.exists() else "NONE"

    diag_evidence = {
        "derivative_file": str(TEST_BLEND),
        "derivative_sha256": current_sha256,
        "runner_file": str(runner_path),
        "runner_sha256": runner_sha256,
        "oracle_file": str(oracle_path),
        "oracle_sha256": oracle_sha256,
        "scenario_contract_version": "1.0.0",
        "scenario_id": "SCENARIO_A_EMPTY_HAND_DIAGNOSTIC",
        "blender_version": bpy.app.version_string,
        "scenario_a1_digit_closure_frames": a1_logs,
        "scenario_a2_pitch_wrist_frames": a2_pitch_logs,
        "scenario_a2_yaw_wrist_frames": a2_yaw_logs
    }
    tmp_diag = Path("/tmp/full-hand-diagnostic.json")
    tmp_diag.write_text(json.dumps(diag_evidence, indent=2), encoding='utf-8')
    print(f"Exported Scenario A Telemetry to: {tmp_diag}")

    # =========================================================================
    # SCENARIO B: Isolated Maul Compound Drop Test (Fresh Reload)
    # =========================================================================
    bpy.ops.wm.open_mainfile(filepath=str(TEST_BLEND))
    scene = bpy.context.scene
    main_shaft = next(o for o in bpy.data.objects if 'shaft' in o.name.lower() and o.type == 'MESH')
    
    mesh = bpy.data.meshes.new("DropPlateMesh")
    plate = bpy.data.objects.new("Maul_Drop_Plate", mesh)
    scene.collection.objects.link(plate)
    
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(mesh)
    bm.free()
    
    plate.scale = Vector((10.0, 10.0, 0.2))
    plate.location = main_shaft.matrix_world.translation - Vector((0.0, 0.0, 0.6))
    
    bpy.ops.object.select_all(action='DESELECT')
    plate.select_set(True)
    scene.view_layers[0].objects.active = plate
    bpy.ops.rigidbody.object_add()
    plate.rigid_body.type = 'PASSIVE'
    plate.rigid_body.collision_shape = 'BOX'
    plate.rigid_body.friction = 0.55

    child_initial_rel_transforms = {}
    shaft_inv_init = main_shaft.matrix_world.inverted()
    for child in main_shaft.children:
        child_initial_rel_transforms[child.name] = list((shaft_inv_init @ child.matrix_world).translation)

    drop_logs = []
    max_rigidity_error = 0.0
    for frame in range(1, 31):
        scene.frame_set(frame)
        shaft_inv_curr = main_shaft.matrix_world.inverted()
        frame_rigidity_errors = {}
        for child in main_shaft.children:
            curr_rel_pos = (shaft_inv_curr @ child.matrix_world).translation
            init_rel_pos = Vector(child_initial_rel_transforms[child.name])
            err = (curr_rel_pos - init_rel_pos).length
            frame_rigidity_errors[child.name] = err
            if err > max_rigidity_error:
                max_rigidity_error = err

        drop_logs.append({
            "frame": frame,
            "maul_shaft_location": list(main_shaft.matrix_world.translation),
            "max_child_rigidity_error_m": max([frame_rigidity_errors[k] for k in frame_rigidity_errors]) if frame_rigidity_errors else 0.0
        })

    drop_evidence = {
        "derivative_file": str(TEST_BLEND),
        "derivative_sha256": current_sha256,
        "scenario_id": "SCENARIO_B_ISOLATED_MAUL_COMPOUND_DROP",
        "blender_version": bpy.app.version_string,
        "floor_plate_location": list(plate.location),
        "compound_children_evaluated": len(child_initial_rel_transforms),
        "max_compound_rigidity_error_m": max_rigidity_error,
        "isolated_maul_drop_frames": drop_logs
    }
    tmp_drop = Path("/tmp/isolated-maul-drop.json")
    tmp_drop.write_text(json.dumps(drop_evidence, indent=2), encoding='utf-8')
    print(f"Exported Scenario B Telemetry to: {tmp_drop}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
