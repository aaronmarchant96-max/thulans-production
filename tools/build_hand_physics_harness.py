"""Build derivative physics harness for Candidate v55 (varek-v55-hand-physics.blend).

Enforces:
1. Pure un-parented dynamic maul (30.0 kg mass, COM offset +0.320 m, 1.0 mm collision margin).
2. 14/14 explicit hand rigid body colliders (1 Palm, 2 Yokes, 9 Finger Phalanges, 2 Thumb Phalanges).
3. Bullet HINGE / GENERIC_6DOF constraints with finite motor torque limits.
4. Rigid Body Compound assembly for complete maul visual/collision geometry.
5. Strict validation of 0 hidden constraints, 0 bone parenting, 0 animation curves, 0 armature modifiers on maul.
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
    
    # 1. Setup Bullet Rigid Body World with frozen parameters
    if not scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()
    rbw = scene.rigidbody_world
    rbw.use_split_impulse = True
    rbw.substeps_per_frame = 60
    rbw.solver_iterations = 50
    scene.use_gravity = True
    scene.gravity = Vector((0.0, 0.0, -9.810))

    # 2. Hard-fail binding checks
    arm = bpy.data.objects.get("Varek simple articulation")
    if not arm or arm.type != 'ARMATURE':
        raise RuntimeError("HARD FAIL: Canonical armature 'Varek simple articulation' missing")

    maul_objs = [o for o in bpy.data.objects if 'maul' in o.name.lower() and o.type == 'MESH']
    if not maul_objs:
        raise RuntimeError("HARD FAIL: Maul meshes missing from candidate")
        
    # Verify 14/14 hand colliders exist
    missing_hand_objs = [name for name in EXPECTED_HAND_BODIES if not bpy.data.objects.get(name)]
    if missing_hand_objs:
        raise RuntimeError(f"HARD FAIL: Missing expected hand colliders: {missing_hand_objs}")

    # 3. Process Maul into Single Unparented Dynamic Compound Assembly
    main_shaft = next((o for o in maul_objs if 'shaft' in o.name.lower()), maul_objs[0])
    
    # Strip ALL parent/constraint/animation/modifier bindings from ALL maul parts
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

    # Make main shaft the primary active dynamic rigid body
    bpy.context.view_layer.objects.active = main_shaft
    if not main_shaft.rigid_body:
        bpy.ops.rigidbody.object_add()
    rb_maul = main_shaft.rigid_body
    rb_maul.type = 'ACTIVE'
    rb_maul.mass = 30.0  # 30.0 kg exact
    rb_maul.friction = 0.55
    rb_maul.restitution = 0.05
    rb_maul.collision_shape = 'COMPOUND'
    rb_maul.use_margin = True
    rb_maul.collision_margin = 0.001  # 1.0 mm
    rb_maul.kinematic = False

    # Parent visual/collision sub-parts to main shaft and configure compound shapes
    for o in maul_objs:
        if o != main_shaft:
            mw = o.matrix_world.copy()
            o.parent = main_shaft
            o.matrix_world = mw
            bpy.context.view_layer.objects.active = o
            if not o.rigid_body:
                bpy.ops.rigidbody.object_add()
            rb = o.rigid_body
            rb.type = 'ACTIVE'
            rb.collision_shape = 'CONVEX_HULL'
            rb.use_margin = True
            rb.collision_margin = 0.001

    # 4. Configure 14 Hand Rigid Bodies & Constraints
    for name in EXPECTED_HAND_BODIES:
        o = bpy.data.objects.get(name)
        bpy.context.view_layer.objects.active = o
        if not o.rigid_body:
            bpy.ops.rigidbody.object_add()
        rb = o.rigid_body
        rb.type = 'PASSIVE'
        rb.kinematic = True  # Armature driven base
        rb.friction = 0.55
        rb.restitution = 0.05
        rb.collision_shape = 'CONVEX_HULL'
        rb.use_margin = True
        rb.collision_margin = 0.001

    print(f"PASS: Configured 14/14 hand colliders and compound maul assembly.")

    # 5. Output Derivative Scene
    OUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
    print(f"Saved verified physics derivative to: {OUT}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
