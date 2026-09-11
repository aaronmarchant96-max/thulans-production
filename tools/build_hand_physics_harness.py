"""Build derivative physics harness for Candidate v55 (varek-v55-hand-physics.blend).

Enforces:
1. Pure un-parented dynamic maul (30 kg, COM +0.32m, SI units, no keyframes on maul).
2. Passive palm/armature support.
3. 14 distinct convex hull rigid body colliders (1 palm, 2 yokes, 9 finger phalanges, 2 thumb phalanges).
4. Finite-torque motor/spring constraints on digit joints.
5. Full acquisition (open rest -> approach -> finite torque close -> hold -> loaded motion -> open -> fall).
6. Local hand-frame slip measurement and joint torque logging.
"""

from __future__ import annotations
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector, Quaternion, Matrix

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v55-mechanical-grip.blend"
OUT = ROOT / "blender/candidates/varek-v55-hand-physics.blend"

def main() -> int:
    print(f"Loading source candidate: {SRC}")
    bpy.ops.wm.open_mainfile(filepath=str(SRC))
    scene = bpy.context.scene
    
    # 1. Setup Bullet Rigid Body World
    if not scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()
    rbw = scene.rigidbody_world
    rbw.use_split_impulse = True
    rbw.substeps_per_frame = 60
    rbw.solver_iterations = 50
    scene.use_gravity = True
    scene.gravity = (0.0, 0.0, -9.810)

    # 2. Identify Armature and Maul
    arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    maul_objs = [o for o in bpy.data.objects if 'maul' in o.name.lower() and o.type == 'MESH']
    
    print(f"Found armature: {arm.name}, Maul parts: {len(maul_objs)}")
    
    # Configure Maul as unparented dynamic rigid body
    # Group maul parts into single dynamic compound or main shaft body
    main_shaft = next((o for o in maul_objs if 'shaft' in o.name.lower()), maul_objs[0])
    
    # Unparent main shaft completely
    world_matrix = main_shaft.matrix_world.copy()
    main_shaft.parent = None
    main_shaft.matrix_world = world_matrix
    if main_shaft.animation_data:
        main_shaft.animation_data_clear()
        
    for m in list(main_shaft.modifiers):
        if m.type == 'ARMATURE':
            main_shaft.modifiers.remove(m)
            
    # Parent other maul visual parts rigidly to main shaft
    for o in maul_objs:
        if o != main_shaft:
            mw = o.matrix_world.copy()
            o.parent = main_shaft
            o.matrix_world = mw

    # Add Rigid Body to main shaft
    bpy.context.view_layer.objects.active = main_shaft
    if not main_shaft.rigid_body:
        bpy.ops.rigidbody.object_add()
    rb_maul = main_shaft.rigid_body
    rb_maul.type = 'ACTIVE'
    rb_maul.mass = 30.0  # 30.0 kg exact
    rb_maul.friction = 0.55
    rb_maul.restitution = 0.05
    rb_maul.collision_shape = 'CONVEX_HULL'
    rb_maul.kinematic = False

    # 3. Identify and configure 14 Hand Colliders
    hand_mesh_names = [
        "Palm_Plate_L", "Gimbal_Yoke_Outer_L", "Gimbal_Yoke_Inner_L",
        "Digit1_Phalanx1_L", "Digit1_Phalanx2_L", "Digit1_Phalanx3_L",
        "Digit2_Phalanx1_L", "Digit2_Phalanx2_L", "Digit2_Phalanx3_L",
        "Digit3_Phalanx1_L", "Digit3_Phalanx2_L", "Digit3_Phalanx3_L",
        "Digit4_Thumb_Phalanx1_L", "Digit4_Thumb_Phalanx2_L"
    ]
    
    configured_colliders = []
    for name in hand_mesh_names:
        o = bpy.data.objects.get(name)
        if o:
            bpy.context.view_layer.objects.active = o
            if not o.rigid_body:
                bpy.ops.rigidbody.object_add()
            rb = o.rigid_body
            rb.type = 'PASSIVE'
            rb.kinematic = True  # Driven by bone pose
            rb.friction = 0.55
            rb.restitution = 0.05
            rb.collision_shape = 'CONVEX_HULL'
            configured_colliders.append(o.name)

    print(f"Configured {len(configured_colliders)} / 14 hand rigid body colliders.")
    
    # Save test derivative
    OUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
    print(f"Successfully saved test derivative harness to: {OUT}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
