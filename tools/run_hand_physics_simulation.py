"""Execute Single-Joint Verification Prototype Scenario (Hardened).

Logs actual matrix transformations, local palm-frame relative quaternion rotation, and motor parameters.
"""

from __future__ import annotations
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector, Quaternion

ROOT = Path("/home/aaron/animation/thulans-production")
TEST_BLEND = ROOT / "blender/candidates/varek-v55-single-joint-test.blend"
OUT_JSON = ROOT / "evidence/varek-v55-mechanical-grip/single-joint-scenario.json"

def main() -> int:
    if not TEST_BLEND.exists():
        raise FileNotFoundError(f"Test blend missing: {TEST_BLEND}")

    bpy.ops.wm.open_mainfile(filepath=str(TEST_BLEND))
    scene = bpy.context.scene
    p1 = bpy.data.objects.get("Digit1_Phalanx1_L")
    palm = bpy.data.objects.get("Palm_Plate_L")
    
    motor_empty = bpy.data.objects.get("D1P1_BearingCenter_Motor")
    rbc_motor = motor_empty.rigid_body_constraint if motor_empty else None

    logs = []
    
    for frame in range(1, 61):
        scene.frame_set(frame)
        
        # Calculate local quaternion relative rotation angle
        palm_q = palm.matrix_world.to_quaternion()
        p1_q = p1.matrix_world.to_quaternion()
        rel_q = palm_q.conjugate() * p1_q
        rel_angle_deg = math.degrees(rel_q.angle)
        
        logs.append({
            "frame": frame,
            "relative_angle_deg": rel_angle_deg,
            "phalanx_location": list(p1.matrix_world.translation),
            "motor_target_velocity": rbc_motor.motor_ang_target_velocity if rbc_motor else 0.0,
            "motor_max_impulse": rbc_motor.motor_ang_max_impulse if rbc_motor else 0.0
        })

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({"scenario": "single_joint_verification", "frames": logs}, indent=2))
    print(f"Single-joint scenario logs exported to: {OUT_JSON}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
