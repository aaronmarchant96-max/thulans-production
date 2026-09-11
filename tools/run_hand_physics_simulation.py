"""Execute Causally Isolated Diagnostics (Scenario A: Empty Hand, Scenario B: Maul Compound Rigidity Drop).

Includes SHA-256 evidence binding and signed hinge-axis rotation extraction.
"""

from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector, Quaternion

ROOT = Path("/home/aaron/animation/thulans-production")
TEST_BLEND = ROOT / "blender/candidates/varek-v55-hand-physics.blend"
READBACK_JSON = ROOT / "evidence/varek-v55-mechanical-grip/full-hand-readback.json"
OUT_DIAGNOSTIC_JSON = ROOT / "evidence/varek-v55-mechanical-grip/full-hand-diagnostic.json"
OUT_MAUL_DROP_JSON = ROOT / "evidence/varek-v55-mechanical-grip/isolated-maul-drop.json"

JOINT_SPECS = [
    ("Palm_Plate_L", "Gimbal_Yoke_Outer_L", 1.0),
    ("Gimbal_Yoke_Outer_L", "Gimbal_Yoke_Inner_L", 1.0),
    ("Palm_Plate_L", "Digit1_Phalanx1_L", 1.5),
    ("Digit1_Phalanx1_L", "Digit1_Phalanx2_L", 1.5),
    ("Digit1_Phalanx2_L", "Digit1_Phalanx3_L", 1.5),
    ("Palm_Plate_L", "Digit2_Phalanx1_L", 1.5),
    ("Digit2_Phalanx1_L", "Digit2_Phalanx2_L", 1.5),
    ("Digit2_Phalanx2_L", "Digit2_Phalanx3_L", 1.5),
    ("Palm_Plate_L", "Digit3_Phalanx1_L", 1.5),
    ("Digit3_Phalanx1_L", "Digit3_Phalanx2_L", 1.5),
    ("Digit3_Phalanx2_L", "Digit3_Phalanx3_L", 1.5),
    ("Palm_Plate_L", "Thumb_Phalanx1_L", 1.2),
    ("Thumb_Phalanx1_L", "Thumb_Phalanx2_L", 1.2)
]

def main() -> int:
    if not TEST_BLEND.exists() or not READBACK_JSON.exists():
        raise FileNotFoundError("HARD FAIL: Required blend or readback audit missing")

    # Cryptographic Hash Binding Audit
    derivative_bytes = TEST_BLEND.read_bytes()
    current_sha256 = hashlib.sha256(derivative_bytes).hexdigest()
    readback_data = json.loads(READBACK_JSON.read_text())
    readback_sha256 = readback_data.get("derivative_sha256")

    if current_sha256 != readback_sha256:
        raise RuntimeError(f"PROV FAIL: Cryptographic hash mismatch! Derivative: {current_sha256[:12]} != Readback: {readback_sha256[:12] if readback_sha256 else 'None'}")

    # =========================================================================
    # SCENARIO A: Causally Isolated Empty-Hand Diagnostic (Fresh Scene Load)
    # =========================================================================
    bpy.ops.wm.open_mainfile(filepath=str(TEST_BLEND))
    scene = bpy.context.scene

    diag_logs = []
    for frame in range(1, 61):
        for p_name, c_name, close_vel in JOINT_SPECS:
            m_obj = bpy.data.objects.get(f"Constraint_Motor_{p_name}_to_{c_name}")
            if m_obj and m_obj.rigid_body_constraint:
                if frame <= 15:
                    m_obj.rigid_body_constraint.motor_ang_target_velocity = -close_vel
                elif frame <= 40:
                    m_obj.rigid_body_constraint.motor_ang_target_velocity = close_vel
                else:
                    m_obj.rigid_body_constraint.motor_ang_target_velocity = -close_vel

        scene.frame_set(frame)
        
        # Log PARENT -> CHILD signed relative rotation angle along declared hinge axis
        joint_signed_angles = {}
        for p_name, c_name, _ in JOINT_SPECS:
            p_obj = bpy.data.objects.get(p_name)
            c_obj = bpy.data.objects.get(c_name)
            h_obj = bpy.data.objects.get(f"Constraint_Hinge_{p_name}_to_{c_name}")
            
            p_q = p_obj.matrix_world.to_quaternion()
            c_q = c_obj.matrix_world.to_quaternion()
            rel_q = p_q.to_matrix().inverted().to_quaternion() @ c_q
            
            # Project rotation angle onto Hinge Z-axis
            hinge_z = h_obj.matrix_world.to_3x3() @ Vector((0.0, 0.0, 1.0))
            signed_angle = math.degrees(rel_q.angle) * (1.0 if rel_q.axis.dot(hinge_z) >= 0 else -1.0)
            joint_signed_angles[f"{p_name}->{c_name}"] = signed_angle

        diag_logs.append({
            "frame": frame,
            "phase": "open" if frame <= 15 else ("close" if frame <= 40 else "reopen"),
            "relative_signed_joint_angles_deg": joint_signed_angles
        })

    diag_evidence = {
        "derivative_file": str(TEST_BLEND),
        "derivative_sha256": current_sha256,
        "scenario_id": "SCENARIO_A_EMPTY_HAND_DIAGNOSTIC",
        "blender_version": bpy.app.version_string,
        "empty_hand_closure_frames": diag_logs
    }
    OUT_DIAGNOSTIC_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_DIAGNOSTIC_JSON.write_text(json.dumps(diag_evidence, indent=2), encoding='utf-8')
    print(f"Exported Scenario A Diagnostic Evidence: {OUT_DIAGNOSTIC_JSON}")

    # =========================================================================
    # SCENARIO B: Causally Isolated Maul Compound Drop Test (Fresh Reload!)
    # =========================================================================
    bpy.ops.wm.open_mainfile(filepath=str(TEST_BLEND))
    scene = bpy.context.scene
    main_shaft = next(o for o in bpy.data.objects if 'shaft' in o.name.lower() and o.type == 'MESH')
    
    # Construct Physical Floor Plate (10.0m x 10.0m x 0.2m solid mesh)
    mesh = bpy.data.meshes.new("DropPlateMesh")
    plate = bpy.data.objects.new("Maul_Drop_Plate", mesh)
    scene.collection.objects.link(plate)
    
    # Simple box geometry
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

    # Record initial relative transforms for all 26 child compound meshes
    child_initial_rel_transforms = {}
    shaft_inv_init = main_shaft.matrix_world.inverted()
    for child in main_shaft.children:
        child_initial_rel_transforms[child.name] = list((shaft_inv_init @ child.matrix_world).translation)

    drop_logs = []
    max_rigidity_error = 0.0
    for frame in range(1, 31):
        scene.frame_set(frame)
        
        # Verify 26-child compound rigidity relative transform errors during drop & impact
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
    OUT_MAUL_DROP_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MAUL_DROP_JSON.write_text(json.dumps(drop_evidence, indent=2), encoding='utf-8')
    print(f"Exported Scenario B Maul Drop Evidence: {OUT_MAUL_DROP_JSON}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
