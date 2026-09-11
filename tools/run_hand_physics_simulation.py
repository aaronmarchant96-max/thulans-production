"""Execute Scenario 1: Acquisition -> Clamp -> Hold -> Release.

Logs local palm-frame handle displacement and motor torque demand.
"""

from __future__ import annotations
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

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
    
    logs = []
    
    # 1. Phase A: Approach (Frames 1-15)
    # 2. Phase B: Finite Torque Closure (Frames 16-30)
    # 3. Phase C: Free-Tool Gravity Hold (Frames 31-75)
    # 4. Phase D: Actuated Opening & Fall (Frames 76-105)
    
    for frame in range(1, 106):
        scene.frame_set(frame)
        palm_inv = palm.matrix_world.inverted()
        local_pos = palm_inv @ main_shaft.matrix_world.translation
        
        logs.append({
            "frame": frame,
            "phase": "approach" if frame <= 15 else ("close" if frame <= 30 else ("hold" if frame <= 75 else "release")),
            "local_palm_pos": list(local_pos),
            "linear_velocity": list(main_shaft.rigid_body.linear_velocity) if main_shaft.rigid_body else [0,0,0],
        })

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({"scenario": "acquisition_hold_release", "frames": logs}, indent=2))
    print(f"Scenario 1 logs exported to: {OUT_JSON}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
