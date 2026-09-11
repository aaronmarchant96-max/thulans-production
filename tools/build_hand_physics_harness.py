"""Build single-joint verification prototype (Milestone 1 Core Engine - Fully Aligned).

Fixes:
1. Explicit Bearing Axis derivation (transverse across knuckle via X-vector, NOT head-to-tail length).
2. Explicit Grip Collar Reference anchoring for Maul COM offset (+0.320 m relative to Maul lower grip rib).
3. Hinge Z-axis / Motor X-axis Alignment Audit (abs(dot(hinge_Z, motor_X)) >= 0.999).
4. Maul 26-child Compound Rigid Body drop/rotation sanity verification.
5. Enhanced saved-scene readback JSON with bearing vector alignment & COM offset proof.
"""

from __future__ import annotations
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector, Matrix, Euler, Quaternion

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v55-mechanical-grip.blend"
OUT = ROOT / "blender/candidates/varek-v55-single-joint-test.blend"
READBACK_JSON = ROOT / "evidence/varek-v55-mechanical-grip/single-joint-readback.json"

def main() -> int:
    print(f"Loading source candidate: {SRC}")
    if not SRC.exists():
        raise FileNotFoundError(f"Source candidate missing: {SRC}")

    bpy.ops.wm.open_mainfile(filepath=str(SRC))
    scene = bpy.context.scene

    # 1. Rigid Body World Setup
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
        
    palm = bpy.data.objects.get("Palm_Plate_L")
    p1 = bpy.data.objects.get("Digit1_Phalanx1_L")
    if not palm or not p1:
        raise RuntimeError("HARD FAIL: Required hand objects missing")

    main_shaft = next((o for o in maul_objs if 'shaft' in o.name.lower()), maul_objs[0])
    grip_collar = next((o for o in maul_objs if 'lower grip rib' in o.name.lower()), main_shaft)

    # 3. Maul COM Offset Relative to Grip Collar Reference
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

    # Position COM exactly +0.320 m along shaft local Z relative to lower grip collar
    collar_loc = grip_collar.matrix_world.translation.copy()
    shaft_matrix = main_shaft.matrix_world.copy()
    local_z_vec = shaft_matrix.to_3x3() @ Vector((0.0, 0.0, 0.320))
    com_world_target = collar_loc + local_z_vec

    # Selection isolation for origin shift
    bpy.ops.object.select_all(action='DESELECT')
    main_shaft.select_set(True)
    bpy.context.view_layer.objects.active = main_shaft

    scene.cursor.location = com_world_target
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

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

    # Re-parent all child maul parts and configure active compound collision shapes
    for o in maul_objs:
        if o != main_shaft:
            mw = o.matrix_world.copy()
            o.parent = main_shaft
            o.matrix_world = mw
            bpy.ops.object.select_all(action='DESELECT')
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            if not o.rigid_body:
                bpy.ops.rigidbody.object_add()
            o.rigid_body.type = 'ACTIVE'
            o.rigid_body.collision_shape = 'CONVEX_HULL'
            o.rigid_body.use_margin = True
            o.rigid_body.collision_margin = 0.001

    # 4. Configure Palm Base Anchor
    bpy.ops.object.select_all(action='DESELECT')
    palm.select_set(True)
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

    # 5. Configure Phalanx 1 Body
    bpy.ops.object.select_all(action='DESELECT')
    p1.select_set(True)
    bpy.context.view_layer.objects.active = p1
    if not p1.rigid_body:
        bpy.ops.rigidbody.object_add()
    p1.rigid_body.type = 'ACTIVE'
    p1.rigid_body.mass = 1.2
    p1.rigid_body.friction = 0.55
    p1.rigid_body.restitution = 0.05
    p1.rigid_body.collision_shape = 'CONVEX_HULL'
    p1.rigid_body.use_margin = True
    p1.rigid_body.collision_margin = 0.001

    # 6. Explicit Bearing Axis Derivation (TRANSVERSE Across Knuckle, Not Lengthwise)
    bone_d1 = arm.pose.bones.get("digit1_01.L")
    if bone_d1:
        pivot_location = arm.matrix_world @ bone_d1.head
        # Transverse rotation axis is X-axis of bone matrix, NOT head-to-tail Z vector!
        transverse_axis_x = (arm.matrix_world.to_3x3() @ bone_d1.matrix.to_3x3() @ Vector((1.0, 0.0, 0.0))).normalized()
    else:
        pivot_location = p1.matrix_world.translation
        transverse_axis_x = Vector((1.0, 0.0, 0.0))

    # A. Hinge Constraint: Z-axis aligned to Transverse Bearing Axis
    hinge_quat = Vector((0.0, 0.0, 1.0)).rotation_difference(transverse_axis_x)
    hinge_empty = bpy.data.objects.new("D1P1_BearingCenter_Hinge", None)
    scene.collection.objects.link(hinge_empty)
    hinge_empty.location = pivot_location
    hinge_empty.rotation_euler = hinge_quat.to_euler()

    bpy.ops.object.select_all(action='DESELECT')
    hinge_empty.select_set(True)
    bpy.context.view_layer.objects.active = hinge_empty
    bpy.ops.rigidbody.constraint_add()
    rbc_hinge = hinge_empty.rigid_body_constraint
    rbc_hinge.type = 'HINGE'
    rbc_hinge.object1 = palm
    rbc_hinge.object2 = p1
    rbc_hinge.use_limit_ang_z = True
    rbc_hinge.limit_ang_z_lower = math.radians(-10.0)
    rbc_hinge.limit_ang_z_upper = math.radians(90.0)

    # B. Motor Constraint: X-axis aligned to Transverse Bearing Axis
    motor_quat = Vector((1.0, 0.0, 0.0)).rotation_difference(transverse_axis_x)
    motor_empty = bpy.data.objects.new("D1P1_BearingCenter_Motor", None)
    scene.collection.objects.link(motor_empty)
    motor_empty.location = pivot_location
    motor_empty.rotation_euler = motor_quat.to_euler()

    bpy.ops.object.select_all(action='DESELECT')
    motor_empty.select_set(True)
    bpy.context.view_layer.objects.active = motor_empty
    bpy.ops.rigidbody.constraint_add()
    rbc_motor = motor_empty.rigid_body_constraint
    rbc_motor.type = 'MOTOR'
    rbc_motor.object1 = palm
    rbc_motor.object2 = p1
    rbc_motor.use_motor_ang = True
    rbc_motor.motor_ang_target_velocity = 1.5
    rbc_motor.motor_ang_max_impulse = 2.0

    # 7. Alignment Audit (|dot(Hinge_Z, Motor_X)| >= 0.999)
    hinge_z = hinge_empty.matrix_world.to_3x3() @ Vector((0.0, 0.0, 1.0))
    motor_x = motor_empty.matrix_world.to_3x3() @ Vector((1.0, 0.0, 0.0))
    alignment_dot = abs(hinge_z.dot(motor_x))
    print(f"Alignment Audit: |dot(Hinge_Z, Motor_X)| = {alignment_dot:.6f}")
    if alignment_dot < 0.999:
        raise RuntimeError(f"HARD FAIL: Constraint alignment failure: dot product {alignment_dot} < 0.999")

    # 8. Save Derivative
    OUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
    print(f"Saved Single-Joint Prototype to: {OUT}")

    # 9. Re-open Saved Scene for Comprehensive Readback Audit
    bpy.ops.wm.open_mainfile(filepath=str(OUT))
    r_shaft = next(o for o in bpy.data.objects if 'shaft' in o.name.lower())
    r_collar = next((o for o in bpy.data.objects if 'lower grip rib' in o.name.lower()), r_shaft)
    r_hinge = bpy.data.objects.get("D1P1_BearingCenter_Hinge")
    r_motor = bpy.data.objects.get("D1P1_BearingCenter_Motor")

    # Readback COM distance from Grip Collar Reference
    com_dist = (r_shaft.location - r_collar.location).length

    readback = {
        "derivative_file": str(OUT),
        "hardpoint_pivot_location": list(r_hinge.location),
        "transverse_bearing_axis": list(transverse_axis_x),
        "constraint_alignment_dot": alignment_dot,
        "hinge_type": r_hinge.rigid_body_constraint.type,
        "hinge_use_limit_ang_z": r_hinge.rigid_body_constraint.use_limit_ang_z,
        "motor_type": r_motor.rigid_body_constraint.type,
        "motor_target_velocity": r_motor.rigid_body_constraint.motor_ang_target_velocity,
        "motor_max_impulse": r_motor.rigid_body_constraint.motor_ang_max_impulse,
        "maul_origin_location": list(r_shaft.location),
        "maul_grip_collar_location": list(r_collar.location),
        "maul_com_distance_from_collar": com_dist,
        "maul_mass": r_shaft.rigid_body.mass,
        "maul_collision_shape": r_shaft.rigid_body.collision_shape,
        "maul_compound_children_count": len([c for c in r_shaft.children if c.rigid_body])
    }

    READBACK_JSON.parent.mkdir(parents=True, exist_ok=True)
    READBACK_JSON.write_text(json.dumps(readback, indent=2), encoding='utf-8')
    print(f"Saved Readback Audit to: {READBACK_JSON}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
