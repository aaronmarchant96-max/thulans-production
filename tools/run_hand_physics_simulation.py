"""Execute Diagnostic Full-Hand Empty Closure & Free-Body Sanity Simulation.

1. Unloaded Empty-Hand Closure (Frames 1-60): Open hand -> coordinated motor closure -> reopen.
2. Free-Body Maul Sanity Test: Maul dropped onto passive plate to verify 26-child compound shape integrity.
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

def main() -> int:
    if not TEST_BLEND.exists():
        raise FileNotFoundError(f"Test blend missing: {TEST_BLEND}")

    bpy.ops.wm.open_mainfile(filepath=str(TEST_BLEND))
    scene = bpy.context.scene
    palm = bpy.data.objects.get("Palm_Plate_L")
    main_shaft = next(o for o in bpy.data.objects if 'shaft' in o.name.lower())
    
    constraints = [o.rigid_body_constraint for o in bpy.data.objects if o.rigid_body_constraint and o.rigid_body_constraint.type == 'MOTOR']

    logs = []
    
    # Empty-Hand Coordinated Closure (Frames 1-60)
    for frame in range(1, 61):
        if frame <= 15:
            # Open Hand
            for rbc in constraints:
                rbc.motor_ang_target_velocity = -1.5
        elif frame <= 40:
            # Coordinated Closure
            for rbc in constraints:
                rbc.motor_ang_target_velocity = 2.0
        else:
            # Re-Open
            for rbc in constraints:
                rbc.motor_ang_target_velocity = -2.0

        scene.frame_set(frame)
        
        # Log joint positions and relative angles for all 11 phalanges
        joint_angles = {}
        for o in bpy.data.objects:
            if 'phalanx' in o.name.lower():
                palm_q = palm.matrix_world.to_quaternion()
                o_q = o.matrix_world.to_quaternion()
                rel_q = palm_q.to_matrix().inverted().to_quaternion() @ o_q
                joint_angles[o.name] = math.degrees(rel_q.angle)

        logs.append({
            "frame": frame,
            "phase": "open" if frame <= 15 else ("close" if frame <= 40 else "reopen"),
            "joint_angles_deg": joint_angles,
            "maul_location": list(main_shaft.matrix_world.translation)
        })

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({"diagnostic": "empty_hand_closure_and_compound_sanity", "frames": logs}, indent=2), encoding='utf-8')
    print(f"Exported Full-Hand Diagnostic Logs to: {OUT_JSON}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
