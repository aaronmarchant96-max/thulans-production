"""Build full 14-body, 13-joint mechanical physics harness (Hardened Core Engine v2).

Fixes:
1. Exact COM origin shift without secondary matrix mutation discrepancy.
2. Complete Parent Isolation Audit for 14 Hand Bodies.
3. Cryptographic SHA-256 hash calculation and manifest binding.
4. Hard assertions on exact 0.3200 m ± 0.0005 m axial COM projection and <= 0.0005 m lateral error.
"""

from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector, Matrix, Euler, Quaternion

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v55-mechanical-grip.blend"
OUT = ROOT / "blender/candidates/varek-v55-hand-physics.blend"
READBACK_JSON = ROOT / "evidence/varek-v55-mechanical-grip/full-hand-readback.json"

EXPECTED_HAND_BODIES = [
    "Palm_Plate_L", "Gimbal_Yoke_Outer_L", "Gimbal_Yoke_Inner_L",
    "Digit1_Phalanx1_L", "Digit1_Phalanx2_L", "Digit1_Phalanx3_L",
    "Digit2_Phalanx1_L", "Digit2_Phalanx2_L", "Digit2_Phalanx3_L",
    "Digit3_Phalanx1_L", "Digit3_Phalanx2_L", "Digit3_Phalanx3_L",
    "Thumb_Phalanx1_L", "Thumb_Phalanx2_L"
]

JOINT_SPECS = [
    ("Palm_Plate_L", "Gimbal_Yoke_Outer_L", "wrist_pitch.L", Vector((1.0, 0.0, 0.0)), 2.0, 3.0, -20.0, 45.0, 1.0),
    ("Gimbal_Yoke_Outer_L", "Gimbal_Yoke_Inner_L", "wrist_yaw.L", Vector((0.0, 1.0, 0.0)), 1.8, 3.0, -15.0, 25.0, 1.0),
    ("Palm_Plate_L", "Digit1_Phalanx1_L", "digit1_01.L", None, 1.2, 2.0, -10.0, 90.0, 1.5),
    ("Digit1_Phalanx1_L", "Digit1_Phalanx2_L", "digit1_02.L", None, 0.6, 1.0, 0.0, 80.0, 1.5),
    ("Digit1_Phalanx2_L", "Digit1_Phalanx3_L", "digit1_03.L", None, 0.3, 0.5, 0.0, 80.0, 1.5),
    ("Palm_Plate_L", "Digit2_Phalanx1_L", "digit2_01.L", None, 1.2, 2.0, -10.0, 90.0, 1.5),
    ("Digit2_Phalanx1_L", "Digit2_Phalanx2_L", "digit2_02.L", None, 0.6, 1.0, 0.0, 80.0, 1.5),
    ("Digit2_Phalanx2_L", "Digit2_Phalanx3_L", "digit2_03.L", None, 0.3, 0.5, 0.0, 80.0, 1.5),
    ("Palm_Plate_L", "Digit3_Phalanx1_L", "digit3_01.L", None, 1.2, 2.0, -10.0, 90.0, 1.5),
    ("Digit3_Phalanx1_L", "Digit3_Phalanx2_L", "digit3_02.L", None, 0.6, 1.0, 0.0, 80.0, 1.5),
    ("Digit3_Phalanx2_L", "Digit3_Phalanx3_L", "digit3_03.L", None, 0.3, 0.5, 0.0, 80.0, 1.5),
    ("Palm_Plate_L", "Thumb_Phalanx1_L", "thumb_01.L", None, 1.5, 2.5, -15.0, 85.0, 1.2),
    ("Thumb_Phalanx1_L", "Thumb_Phalanx2_L", "thumb_02.L", None, 0.8, 1.2, 0.0, 80.0, 1.2)
]

def main() -> int:
    print(f"Loading source candidate: {SRC}")
    if not SRC.exists():
        raise FileNotFoundError(f"Source candidate missing: {SRC}")

    bpy.ops.wm.open_mainfile(filepath=str(SRC))
    scene = bpy.context.scene

    if not scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()
    rbw = scene.rigidbody_world
    rbw.use_split_impulse = True
    rbw.substeps_per_frame = 60
    rbw.solver_iterations = 50
    scene.use_gravity = True
    scene.gravity = Vector((0.0, 0.0, -9.810))

    # 1. Hard binding checks (No fallbacks!)
    arm = bpy.data.objects.get("Varek simple articulation")
    if not arm or arm.type != 'ARMATURE':
        raise RuntimeError("HARD FAIL: Canonical armature 'Varek simple articulation' missing")

    maul_objs = [o for o in bpy.data.objects if 'maul' in o.name.lower() and o.type == 'MESH']
    if not maul_objs:
        raise RuntimeError("HARD FAIL: Maul meshes missing from candidate")
        
    main_shaft = next((o for o in maul_objs if 'shaft' in o.name.lower()), None)
    if not main_shaft:
        raise RuntimeError("HARD FAIL: 'Maul shaft' mesh missing")

    grip_collar = next((o for o in maul_objs if 'lower grip rib' in o.name.lower()), None)
    if not grip_collar:
        raise RuntimeError("HARD FAIL: 'Maul lower grip rib' reference missing")

    missing_hand_objs = [name for name in EXPECTED_HAND_BODIES if not bpy.data.objects.get(name)]
    if missing_hand_objs:
        raise RuntimeError(f"HARD FAIL: Missing expected hand colliders: {missing_hand_objs}")

    # 2. Hand Rig Isolation Audit (Strip parenting, constraints, modifiers, animation)
    for name in EXPECTED_HAND_BODIES:
        o = bpy.data.objects.get(name)
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

    # 3. Maul Compound Assembly & Normalized Shaft Local-Z COM Shift
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

    collar_loc = grip_collar.matrix_world.translation.copy()
    shaft_matrix = main_shaft.matrix_world.copy()
    shaft_axis_world = (shaft_matrix.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
    com_world_target = collar_loc + shaft_axis_world * 0.320

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

    # 4. Configure Palm Anchor
    palm = bpy.data.objects.get("Palm_Plate_L")
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

    # 5. Build 13 Rigid Body HINGE + MOTOR Joint Pairs
    alignment_audits = []

    for p_name, c_name, b_name, axis_override, mass, max_imp, low_deg, up_deg, close_vel in JOINT_SPECS:
        p_obj = bpy.data.objects.get(p_name)
        c_obj = bpy.data.objects.get(c_name)
        bone = arm.pose.bones.get(b_name)
        if not bone:
            raise RuntimeError(f"HARD FAIL: Expected bone hardpoint '{b_name}' missing from armature")

        if c_name != "Palm_Plate_L":
            bpy.ops.object.select_all(action='DESELECT')
            c_obj.select_set(True)
            bpy.context.view_layer.objects.active = c_obj
            if not c_obj.rigid_body:
                bpy.ops.rigidbody.object_add()
            rb = c_obj.rigid_body
            rb.type = 'ACTIVE'
            rb.mass = mass
            rb.friction = 0.55
            rb.restitution = 0.05
            rb.collision_shape = 'CONVEX_HULL'
            rb.use_margin = True
            rb.collision_margin = 0.001

        pivot_loc = arm.matrix_world @ bone.head
        if axis_override is not None:
            transverse_axis_x = (arm.matrix_world.to_3x3() @ axis_override).normalized()
        else:
            transverse_axis_x = (arm.matrix_world.to_3x3() @ bone.matrix.to_3x3() @ Vector((1.0, 0.0, 0.0))).normalized()

        hinge_quat = Vector((0.0, 0.0, 1.0)).rotation_difference(transverse_axis_x)
        hinge_name = f"Constraint_Hinge_{p_name}_to_{c_name}"
        hinge_empty = bpy.data.objects.get(hinge_name) or bpy.data.objects.new(hinge_name, None)
        if hinge_empty.name not in scene.collection.objects:
            scene.collection.objects.link(hinge_empty)
        hinge_empty.location = pivot_loc
        hinge_empty.rotation_euler = hinge_quat.to_euler()

        bpy.ops.object.select_all(action='DESELECT')
        hinge_empty.select_set(True)
        bpy.context.view_layer.objects.active = hinge_empty
        if not hinge_empty.rigid_body_constraint:
            bpy.ops.rigidbody.constraint_add()
        rbc_h = hinge_empty.rigid_body_constraint
        rbc_h.type = 'HINGE'
        rbc_h.object1 = p_obj
        rbc_h.object2 = c_obj
        rbc_h.use_limit_ang_z = True
        rbc_h.limit_ang_z_lower = math.radians(low_deg)
        rbc_h.limit_ang_z_upper = math.radians(up_deg)

        motor_quat = Vector((1.0, 0.0, 0.0)).rotation_difference(transverse_axis_x)
        motor_name = f"Constraint_Motor_{p_name}_to_{c_name}"
        motor_empty = bpy.data.objects.get(motor_name) or bpy.data.objects.new(motor_name, None)
        if motor_empty.name not in scene.collection.objects:
            scene.collection.objects.link(motor_empty)
        motor_empty.location = pivot_loc
        motor_empty.rotation_euler = motor_quat.to_euler()

        bpy.ops.object.select_all(action='DESELECT')
        motor_empty.select_set(True)
        bpy.context.view_layer.objects.active = motor_empty
        if not motor_empty.rigid_body_constraint:
            bpy.ops.rigidbody.constraint_add()
        rbc_m = motor_empty.rigid_body_constraint
        rbc_m.type = 'MOTOR'
        rbc_m.object1 = p_obj
        rbc_m.object2 = c_obj
        rbc_m.use_motor_ang = True
        rbc_m.motor_ang_target_velocity = close_vel
        rbc_m.motor_ang_max_impulse = max_imp

        hinge_z = hinge_empty.matrix_world.to_3x3() @ Vector((0.0, 0.0, 1.0))
        motor_x = motor_empty.matrix_world.to_3x3() @ Vector((1.0, 0.0, 0.0))
        dot_val = abs(hinge_z.dot(motor_x))
        alignment_audits.append({"joint": f"{p_name}->{c_name}", "alignment_dot": dot_val})
        if dot_val < 0.999:
            raise RuntimeError(f"HARD FAIL: Constraint alignment failure on {p_name}->{c_name}: dot {dot_val} < 0.999")

    # 6. Save Derivative & Compute Hash
    OUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
    out_sha256 = hashlib.sha256(OUT.read_bytes()).hexdigest()
    print(f"Saved Full-Hand Physics Harness: {OUT} (SHA256: {out_sha256[:12]})")

    # 7. Post-Reopen Disk Readback Audit with Hard COM Tolerance Assertion
    bpy.ops.wm.open_mainfile(filepath=str(OUT))
    r_maul_objs = [o for o in bpy.data.objects if 'maul' in o.name.lower() and o.type == 'MESH']
    r_shaft = next(o for o in r_maul_objs if 'shaft' in o.name.lower())
    r_collar = next(o for o in r_maul_objs if 'lower grip rib' in o.name.lower())

    shaft_com_world = r_shaft.matrix_world.translation.copy()
    collar_world = r_collar.matrix_world.translation.copy()
    com_delta = shaft_com_world - collar_world
    shaft_local_z = (r_shaft.matrix_world.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
    axial_projection = com_delta.dot(shaft_local_z)
    lateral_error = (com_delta - (shaft_local_z * axial_projection)).length

    print(f"Readback COM Axial Projection: {axial_projection:.6f} m (Target: 0.320000 m)")
    print(f"Readback COM Lateral Error:     {lateral_error:.6f} m (Limit: 0.000500 m)")

    if abs(axial_projection - 0.320) > 0.0005:
        raise RuntimeError(f"PROV FAIL: COM axial projection error: {axial_projection:.6f} m != 0.3200 m (diff: {abs(axial_projection-0.320)*1000:.3f} mm > 0.5 mm)")

    if lateral_error > 0.0005:
        raise RuntimeError(f"PROV FAIL: COM lateral error: {lateral_error:.6f} m > 0.0005 m")

    readback_joints = []
    reopened_audits_passed = 0
    for p_name, c_name, _, _, mass, max_imp, low_deg, up_deg, _ in JOINT_SPECS:
        h_obj = bpy.data.objects.get(f"Constraint_Hinge_{p_name}_to_{c_name}")
        m_obj = bpy.data.objects.get(f"Constraint_Motor_{p_name}_to_{c_name}")
        
        h_z = h_obj.matrix_world.to_3x3() @ Vector((0.0, 0.0, 1.0))
        m_x = m_obj.matrix_world.to_3x3() @ Vector((1.0, 0.0, 0.0))
        dot_recalc = abs(h_z.dot(m_x))
        if dot_recalc >= 0.999:
            reopened_audits_passed += 1

        readback_joints.append({
            "parent": p_name,
            "child": c_name,
            "hinge_type": h_obj.rigid_body_constraint.type,
            "hinge_z_limit": h_obj.rigid_body_constraint.use_limit_ang_z,
            "hinge_limits_deg": [low_deg, up_deg],
            "motor_type": m_obj.rigid_body_constraint.type,
            "motor_max_impulse": m_obj.rigid_body_constraint.motor_ang_max_impulse,
            "reopened_alignment_dot": dot_recalc
        })

    readback = {
        "derivative_file": str(OUT),
        "derivative_sha256": out_sha256,
        "total_hand_bodies": len(EXPECTED_HAND_BODIES),
        "total_joint_pairs": len(JOINT_SPECS),
        "reopened_alignment_audits_passed": reopened_audits_passed,
        "maul_origin_world": list(shaft_com_world),
        "maul_collar_world": list(collar_world),
        "maul_com_axial_projection_m": axial_projection,
        "maul_com_lateral_error_m": lateral_error,
        "maul_mass_kg": r_shaft.rigid_body.mass,
        "maul_collision_shape": r_shaft.rigid_body.collision_shape,
        "maul_compound_children_count": len([c for c in r_shaft.children if c.rigid_body]),
        "serialized_joints": readback_joints
    }

    READBACK_JSON.parent.mkdir(parents=True, exist_ok=True)
    READBACK_JSON.write_text(json.dumps(readback, indent=2), encoding='utf-8')
    print(f"Saved Hardened Readback Audit to: {READBACK_JSON}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
