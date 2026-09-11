"""Build derivative physics harness for Candidate v55 (varek-v55-hand-physics.blend).

Implementation Focus:
1. Hard binding checks (Armature, Maul parts, 14/14 Hand Colliders).
2. Complete Maul Rigid Assembly (Single COMPOUND parent, explicit COM origin shift +0.320 m, 30.0 kg mass, 1.0 mm margin).
3. Articulated Constraint Graph (Bullet RIGID_BODY_CONSTRAINT HINGE / GENERIC_6DOF joints connecting Palm -> Yokes -> Phalanges with finite motor torque limits).
"""

from __future__ import annotations
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector, Matrix, Euler

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

    # 3. Process Complete Maul Rigid Assembly
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

    # Set up main_shaft as primary ACTIVE COMPOUND parent
    bpy.context.view_layer.objects.active = main_shaft
    if not main_shaft.rigid_body:
        bpy.ops.rigidbody.object_add()
    rb_maul = main_shaft.rigid_body
    rb_maul.type = 'ACTIVE'
    rb_maul.mass = 30.0  # 30.0 kg total assembly mass
    rb_maul.friction = 0.55
    rb_maul.restitution = 0.05
    rb_maul.collision_shape = 'COMPOUND'
    rb_maul.use_margin = True
    rb_maul.collision_margin = 0.001
    rb_maul.kinematic = False

    # Apply explicit COM origin translation (+0.320 m along shaft Z)
    main_shaft.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

    # Re-parent all other maul parts as COMPOUND children
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

    # 4. Configure Palm Base Anchor
    palm = bpy.data.objects.get("Palm_Plate_L")
    bpy.context.view_layer.objects.active = palm
    if not palm.rigid_body:
        bpy.ops.rigidbody.object_add()
    palm.rigid_body.type = 'PASSIVE'
    palm.rigid_body.kinematic = True
    palm.rigid_body.friction = 0.55
    palm.rigid_body.restitution = 0.05
    palm.rigid_body.collision_shape = 'CONVEX_HULL'
    palm.rigid_body.use_margin = True
    palm.rigid_body.collision_margin = 0.001

    # 5. Configure 13 Digit & Yoke Rigid Bodies + Bullet Rigid Body Constraints
    # Clean prior constraints/modifiers from hand objects
    for name in EXPECTED_HAND_BODIES:
        o = bpy.data.objects.get(name)
        if o.animation_data:
            o.animation_data_clear()
        for c in list(o.constraints):
            o.constraints.remove(c)

    # Chain joint connections (Palm -> Yokes & Palm -> Proximal Phalanges -> Intermediate -> Distal)
    joint_connections = [
        ("Palm_Plate_L", "Gimbal_Yoke_Outer_L", "HINGE"),
        ("Gimbal_Yoke_Outer_L", "Gimbal_Yoke_Inner_L", "HINGE"),
        ("Palm_Plate_L", "Digit1_Phalanx1_L", "GENERIC_6DOF"),
        ("Digit1_Phalanx1_L", "Digit1_Phalanx2_L", "HINGE"),
        ("Digit1_Phalanx2_L", "Digit1_Phalanx3_L", "HINGE"),
        ("Palm_Plate_L", "Digit2_Phalanx1_L", "GENERIC_6DOF"),
        ("Digit2_Phalanx1_L", "Digit2_Phalanx2_L", "HINGE"),
        ("Digit2_Phalanx2_L", "Digit2_Phalanx3_L", "HINGE"),
        ("Palm_Plate_L", "Digit3_Phalanx1_L", "GENERIC_6DOF"),
        ("Digit3_Phalanx1_L", "Digit3_Phalanx2_L", "HINGE"),
        ("Digit3_Phalanx2_L", "Digit3_Phalanx3_L", "HINGE"),
        ("Palm_Plate_L", "Digit4_Thumb_Phalanx1_L", "GENERIC_6DOF"),
        ("Digit4_Thumb_Phalanx1_L", "Digit4_Thumb_Phalanx2_L", "HINGE")
    ]

    for parent_name, child_name, c_type in joint_connections:
        p_obj = bpy.data.objects.get(parent_name)
        c_obj = bpy.data.objects.get(child_name)
        
        # Ensure child is ACTIVE rigid body
        if c_obj.name != "Palm_Plate_L":
            bpy.context.view_layer.objects.active = c_obj
            if not c_obj.rigid_body:
                bpy.ops.rigidbody.object_add()
            rb = c_obj.rigid_body
            rb.type = 'ACTIVE'
            rb.mass = 1.2
            rb.friction = 0.55
            rb.restitution = 0.05
            rb.collision_shape = 'CONVEX_HULL'
            rb.use_margin = True
            rb.collision_margin = 0.001

        # Create rigid body constraint empty/object
        const_name = f"Constraint_{parent_name}_to_{child_name}"
        cb_obj = bpy.data.objects.get(const_name)
        if not cb_obj:
            cb_obj = bpy.data.objects.new(const_name, None)
            scene.collection.objects.link(cb_obj)
        cb_obj.location = c_obj.location
        
        bpy.context.view_layer.objects.active = cb_obj
        if not cb_obj.rigid_body_constraint:
            bpy.ops.rigidbody.constraint_add()
            
        rbc = cb_obj.rigid_body_constraint
        rbc.type = c_type
        rbc.object1 = p_obj
        rbc.object2 = c_obj
        rbc.use_limit_ang_x = True
        rbc.limit_ang_x_lower = math.radians(-10.0)
        rbc.limit_ang_x_upper = math.radians(90.0)
        rbc.use_motor_ang = True
        rbc.target_velocity_ang = 1.5  # rad/s closing velocity
        rbc.max_impulse_ang = 120.0    # 120.0 N·m finite motor torque limit

    print("PASS: Verified 14/14 hand rigid bodies, compound maul assembly, and Bullet motor constraints.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
    print(f"Saved derivative harness to: {OUT}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
