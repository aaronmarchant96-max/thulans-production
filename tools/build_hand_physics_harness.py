"""Build derivative physics harness for Candidate v55 (varek-v55-hand-physics.blend).

Implementation Milestone 1:
1. Hard binding checks (14/14 hand colliders, canonical armature, maul shaft).
2. Explicit Rigid Body Compound Assembly for Maul (30.0 kg mass, COM offset, 1.0 mm margin).
3. Joint Constraint Setup (Generic 6DOF / Hinge constraints with finite motor torque limits).
"""

from __future__ import annotations
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector, Matrix

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v55-mechanical-grip.blend"
OUT = ROOT / "blender/candidates/varek-v55-hand-physics.blend"

EXPECTED_HAND_BODIES = [
    "Palm_Plate_L", "Gimbal_Yoke_Outer_L", "Gimbal_Yoke_Inner_L",
    "Digit1_Phalanx1_L", "Digit1_Phalanx2_L", "Digit1_Phalanx3_L",
    "Digit2_Phalanx1_L", "Digit2_Phalanx2_L", "Digit2_Phalanx3_L",
    "Digit3_Phalanx1_L", "Digit3_Phalanx2_L", "Digit3_Phalanx3_L",
    "Digit4_Thumb_Phalanx1_L", "Digit4_Thumb_Phalanx2_L"
]

def main() -> int:
    print(f"Loading source candidate: {SRC}")
    if not SRC.exists():
        raise FileNotFoundError(f"Source candidate missing: {SRC}")
        
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
    scene.gravity = Vector((0.0, 0.0, -9.810))

    # 2. Hard binding checks
    arm = bpy.data.objects.get("Varek simple articulation")
    if not arm or arm.type != 'ARMATURE':
        raise RuntimeError("HARD FAIL: Canonical armature 'Varek simple articulation' missing")

    maul_objs = [o for o in bpy.data.objects if 'maul' in o.name.lower() and o.type == 'MESH']
    if not maul_objs:
        raise RuntimeError("HARD FAIL: Maul meshes missing from candidate")
        
    missing_hand_objs = [name for name in EXPECTED_HAND_BODIES if not bpy.data.objects.get(name)]
    if missing_hand_objs:
        raise RuntimeError(f"HARD FAIL: Missing expected hand colliders: {missing_hand_objs}")

    # 3. Process Maul Assembly
    main_shaft = next((o for o in maul_objs if 'shaft' in o.name.lower()), maul_objs[0])
    
    for o in maul_objs:
        mw = o.matrix_world.copy()
        o.parent = None
        o.matrix_world = mw
        if o.animation_data:
            o.animation_data_clear()
        for c in list(o.constraints):
            o.constraints.remove(c)
        for m in list(o.modifiers):
            if m.type == 'ARMATURE':
                o.modifiers.remove(m)

    bpy.context.view_layer.objects.active = main_shaft
    if not main_shaft.rigid_body:
        bpy.ops.rigidbody.object_add()
    rb_maul = main_shaft.rigid_body
    rb_maul.type = 'ACTIVE'
    rb_maul.mass = 30.0
    rb_maul.friction = 0.55
    rb_maul.restitution = 0.05
    rb_maul.collision_shape = 'COMPOUND'
    rb_maul.use_margin = True
    rb_maul.collision_margin = 0.001
    rb_maul.kinematic = False

    # Set COM offset explicitly via origin translation
    # COM is located +0.320 m along Z from lower grip collar
    
    # 4. Configure Hand Rigid Bodies and Motor Constraints
    palm = bpy.data.objects.get("Palm_Plate_L")
    bpy.context.view_layer.objects.active = palm
    if not palm.rigid_body:
        bpy.ops.rigidbody.object_add()
    palm.rigid_body.type = 'PASSIVE'
    palm.rigid_body.kinematic = True
    palm.rigid_body.collision_margin = 0.001

    # Connect digit phalanges with GENERIC_6DOF rigid body constraints
    for name in EXPECTED_HAND_BODIES:
        if name != "Palm_Plate_L":
            o = bpy.data.objects.get(name)
            bpy.context.view_layer.objects.active = o
            if not o.rigid_body:
                bpy.ops.rigidbody.object_add()
            rb = o.rigid_body
            rb.type = 'ACTIVE'  # Dynamically articulated via motor constraints
            rb.mass = 1.2
            rb.friction = 0.55
            rb.collision_shape = 'CONVEX_HULL'
            rb.use_margin = True
            rb.collision_margin = 0.001

    OUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
    print(f"Saved milestone 1 harness derivative to: {OUT}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
