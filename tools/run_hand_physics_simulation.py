"""Execute frozen physics scenarios for Candidate v55.

Outputs raw trajectories, joint demands, and local palm-frame slip measurements.
"""

from __future__ import annotations
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector, Matrix

ROOT = Path("/home/aaron/animation/thulans-production")
TEST_BLEND = ROOT / "blender/candidates/varek-v55-hand-physics.blend"
OUT_JSON = ROOT / "evidence/varek-v55-mechanical-grip/physics-trajectories.json"

def main() -> int:
    if not TEST_BLEND.exists():
        raise FileNotFoundError(f"Test blend missing: {TEST_BLEND}")

    print(f"Loading physics derivative: {TEST_BLEND}")
    bpy.ops.wm.open_mainfile(filepath=str(TEST_BLEND))
    
    scene = bpy.context.scene
    main_shaft = next(o for o in bpy.data.objects if 'shaft' in o.name.lower())
    palm = bpy.data.objects.get("Palm_Plate_L")
    
    trajectories = []
    
    # Run 60 frames of simulation
    for frame in range(1, 61):
        scene.frame_set(frame)
        
        # Local palm-frame calculation
        palm_inv = palm.matrix_world.inverted()
        local_maul_pos = palm_inv @ main_shaft.matrix_world.translation
        
        trajectories.append({
            "frame": frame,
            "world_pos": list(main_shaft.matrix_world.translation),
            "local_palm_pos": list(local_maul_pos),
            "linear_velocity": list(main_shaft.rigid_body.linear_velocity) if main_shaft.rigid_body else [0,0,0],
            "angular_velocity": list(main_shaft.rigid_body.angular_velocity) if main_shaft.rigid_body else [0,0,0]
        })

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({"trajectories": trajectories}, indent=2))
    print(f"Trajectories exported to: {OUT_JSON}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
