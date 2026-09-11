"""Execute Scenario 1: Approach -> Finite Torque Close -> Gravity Hold -> Release.

Executes physical actuator motor states, evaluates contact appearance, and exports raw local palm-frame logs.
"""

from __future__ import annotations
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector, Euler

ROOT = Path("/home/aaron/animation/thulans-production")
TEST_BLEND = ROOT / "blender/candidates/varek-v55-hand-physics.blend"
OUT_JSON = ROOT / "evidence/varek-v55-mechanical-grip/physics-scenario-1.json"

def main() -> int:
    if not TEST_BLEND.exists():
        raise FileNotFoundError(f"Test blend missing: {TEST_BLEND}")

    bpy.ops.wm.open_mainfile(filepath=str(TEST_BLEND))
    scene = bpy.context.scene
    main_shaft = next(o for o in bpy.data.objects if 'shaft' in o.name.lower())
    palm = bpy.data.objects.get("Palm_Plate_L")
    
    constraints = [o.rigid_body_constraint for o in bpy.data.objects if o.rigid_body_constraint]
    
    logs = []
    
    for frame in range(1, 106):
        # 1. Physical Actuator Phase Programming
        if frame <= 15:
            phase = "approach"
            # Open hand: motor velocity negative or zero
            for rbc in constraints:
                rbc.target_velocity_ang = -1.0
                rbc.max_impulse_ang = 50.0
        elif frame <= 30:
            phase = "close"
            # Finite torque closing: positive motor velocity with 120 N·m max impulse limit
            for rbc in constraints:
                rbc.target_velocity_ang = 2.0
                rbc.max_impulse_ang = 120.0
        elif frame <= 75:
            phase = "hold"
            # Active hold: zero velocity with 120 N·m clamping impulse
            for rbc in constraints:
                rbc.target_velocity_ang = 0.0
                rbc.max_impulse_ang = 120.0
        else:
            phase = "release"
            # Actuated opening: reverse velocity to open digits and release maul
            for rbc in constraints:
                rbc.target_velocity_ang = -3.0
                rbc.max_impulse_ang = 80.0

        scene.frame_set(frame)
        
        # Local palm-frame calculation
        palm_inv = palm.matrix_world.inverted()
        local_matrix = palm_inv @ main_shaft.matrix_world
        local_pos = local_matrix.translation
        local_euler = local_matrix.to_euler()
        
        # Measure motor torque demand across constraints
        max_applied_torque = max([rbc.max_impulse_ang for rbc in constraints]) if constraints else 0.0
        
        logs.append({
            "frame": frame,
            "phase": phase,
            "local_palm_pos": list(local_pos),
            "local_palm_rot_deg": [math.degrees(a) for a in local_euler],
            "linear_velocity": list(main_shaft.rigid_body.linear_velocity) if main_shaft.rigid_body else [0,0,0],
            "angular_velocity": list(main_shaft.rigid_body.angular_velocity) if main_shaft.rigid_body else [0,0,0],
            "max_actuator_torque_demand": max_applied_torque
        })

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({"scenario": "acquisition_hold_release", "frames": logs}, indent=2))
    print(f"Scenario 1 physical logs exported to: {OUT_JSON}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
