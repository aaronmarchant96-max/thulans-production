"""Execute Diagnostic Full-Hand Empty Closure, Relative Joint Logging, & Maul Compound Drop.

1. Diagnostic Empty-Hand Closure (Frames 1-60): Logs relative PARENT->CHILD quaternion rotation for all 13 joints.
2. Isolated Maul Compound Drop Test (Frames 61-90): Maul dropped onto passive collider plate to verify 26-child compound shape integrity.
"""

from __future__ import annotations
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector, Quaternion

ROOT = Path("/home/aaron/animation/thulans-production")
TEST_BLEND = ROOT / "blender/candidates/varek-v55-hand-physics.blend"
OUT_JSON = ROOT / "evidence/varek-v55-mechanical-grip/full-hand-diagnostic.json"

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
    if not TEST_BLEND.exists():
        raise FileNotFoundError(f"Test blend missing: {TEST_BLEND}")

    bpy.ops.wm.open_mainfile(filepath=str(TEST_BLEND))
    scene = bpy.context.scene
    main_shaft = next(o for o in bpy.data.objects if 'shaft' in o.name.lower())

    logs = []
    
    # 1. Unloaded Empty-Hand Closure (Frames 1-60)
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
        
        # Log PARENT -> CHILD relative quaternion rotation angle for all 13 joints!
        joint_rotations = {}
        for p_name, c_name, _ in JOINT_SPECS:
            p_obj = bpy.data.objects.get(p_name)
            c_obj = bpy.data.objects.get(c_name)
            p_q = p_obj.matrix_world.to_quaternion()
            c_q = c_obj.matrix_world.to_quaternion()
            rel_q = p_q.to_matrix().inverted().to_quaternion() @ c_q
            joint_rotations[f"{p_name}->{c_name}"] = math.degrees(rel_q.angle)

        logs.append({
            "frame": frame,
            "phase": "open" if frame <= 15 else ("close" if frame <= 40 else "reopen"),
            "relative_joint_angles_deg": joint_rotations
        })

    # 2. Isolated Maul Compound Drop Test (Frames 61-90)
    mesh = bpy.data.meshes.new("DropPlateMesh")
    plate = bpy.data.objects.new("Maul_Drop_Plate", mesh)
    scene.collection.objects.link(plate)
    plate.location = main_shaft.matrix_world.translation - Vector((0.0, 0.0, 0.5))
    
    bpy.ops.object.select_all(action='DESELECT')
    plate.select_set(True)
    scene.view_layers[0].objects.active = plate
    bpy.ops.rigidbody.object_add()
    plate.rigid_body.type = 'PASSIVE'
    plate.rigid_body.collision_shape = 'BOX'

    drop_logs = []
    for frame in range(61, 91):
        scene.frame_set(frame)
        drop_logs.append({
            "frame": frame,
            "maul_location": list(main_shaft.matrix_world.translation)
        })

    evidence = {
        "derivative_file": str(TEST_BLEND),
        "empty_hand_closure_frames": logs,
        "isolated_maul_drop_frames": drop_logs
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(evidence, indent=2), encoding='utf-8')
    print(f"Exported Full-Hand Diagnostic & Drop Evidence to: {OUT_JSON}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
