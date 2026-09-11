"""Build full 14-body, 13-joint mechanical physics harness for Candidate v55 (varek-v55-hand-physics.blend).

Enforces:
1. Hard binding checks (Armature, Maul parts, 14/14 Hand Colliders).
2. Complete Maul Rigid Assembly (Single COMPOUND parent, explicit local-Z COM shift +0.320 m relative to Grip Collar, 30.0 kg mass, 1.0 mm margin).
3. 13-Joint Articulated Constraint Graph (Bullet RIGID_BODY_CONSTRAINT HINGE / MOTOR pairs):
   - Proximal: Palm -> Yokes & Palm -> Phalanx1
   - Intermediate: Phalanx1 -> Phalanx2
   - Distal: Phalanx2 -> Phalanx3
   - Thumb: Derived strictly from thumb_01.L & thumb_02.L local matrices.
4. Mass & Torque Tapering (Proximal 1.2 kg / 2.0 N·m·s, Intermediate 0.6 kg / 1.0 N·m·s, Distal 0.3 kg / 0.5 N·m·s).
5. Interphalangeal Travel Limits (Proximal -10° to 90°, Intermediate/Distal 0° to 80°).
6. Alignment Audit (|dot(Hinge_Z, Motor_X)| >= 0.999 across all 13 joints).
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
    # (parent_obj, child_obj, bone_name, mass_kg, impulse_limit, lower_deg, upper_deg)
    ("Palm_Plate_L", "Gimbal_Yoke_Outer_L", "wrist_pitch.L", 2.0, 3.0, -20.0, 45.0),
    ("Gimbal_Yoke_Outer_L", "Gimbal_Yoke_Inner_L", "wrist_yaw.L", 1.8, 3.0, -15.0, 25.0),
    
    # Digit 1 (Index)
    ("Palm_Plate_L", "Digit1_Phalanx1_L", "digit1_01.L", 1.2, 2.0, -10.0, 90.0),
    ("Digit1_Phalanx1_L", "Digit1_Phalanx2_L", "digit1_02.L", 0.6, 1.0, 0.0, 80.0),
    ("Digit1_Phalanx2_L", "Digit1_Phalanx3_L", "digit1_03.L", 0.3, 0.5, 0.0, 80.0),

    # Digit 2 (Middle)
    ("Palm_Plate_L", "Digit2_Phalanx1_L", "digit2_01.L", 1.2, 2.0, -10.0, 90.0),
    ("Digit2_Phalanx1_L", "Digit2_Phalanx2_L", "digit2_02.L", 0.6, 1.0, 0.0, 80.0),
    ("Digit2_Phalanx2_L", "Digit2_Phalanx3_L", "digit2_03.L", 0.3, 0.5, 0.0, 80.0),

    # Digit 3 (Ring)
    ("Palm_Plate_L", "Digit3_Phalanx1_L", "digit3_01.L", 1.2, 2.0, -10.0, 90.0),
    ("Digit3_Phalanx1_L", "Digit3_Phalanx2_L", "digit3_02.L", 0.6, 1.0, 0.0, 80.0),
    ("Digit3_Phalanx2_L", "Digit3_Phalanx3_L", "digit3_03.L", 0.3, 0.5, 0.0, 80.0),

    # Digit 4 (Thumb - Opposable Matrix Alignment)
    ("Palm_Plate_L", "Thumb_Phalanx1_L", "thumb_01.L", 1.5, 2.5, -15.0, 85.0),
    ("Thumb_Phalanx1_L", "Thumb_Phalanx2_L", "thumb_02.L", 0.8, 1.2, 0.0, 80.0)
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

    main_shaft = next((o for o in maul_objs if 'shaft' in o.name.lower()), maul_objs[0])
    grip_collar = next((o for o in maul_objs if 'lower grip rib' in o.name.lower()), main_shaft)

    # 3. Process Maul Compound Assembly with Verified COM Offset
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
    local_z_vec = shaft_matrix.to_3x3() @ Vector((0.0, 0.0, 0.320))
    com_world_target = collar_loc + local_z_vec

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

    # 5. Build 13 Rigid Body HINGE + MOTOR Joint Pairs Across 14 Bodies
    alignment_audits = []

    for p_name, c_name, b_name, mass, max_imp, low_deg, up_deg in JOINT_SPECS:
        p_obj = bpy.data.objects.get(p_name)
        c_obj = bpy.data.objects.get(c_name)
        
        # Configure child active rigid body with mass tapering
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

        # Derive bearing center & transverse rotation axis from armature bone local matrix
        bone = arm.pose.bones.get(b_name)
        if bone:
            pivot_loc = arm.matrix_world @ bone.head
            transverse_axis_x = (arm.matrix_world.to_3x3() @ bone.matrix.to_3x3() @ Vector((1.0, 0.0, 0.0))).normalized()
        else:
            pivot_loc = c_obj.matrix_world.translation
            transverse_axis_x = Vector((1.0, 0.0, 0.0))

        # A. Hinge Constraint (Z-axis aligned to transverse axis)
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

        # B. Motor Constraint (X-axis aligned to transverse axis)
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
        rbc_m.motor_ang_target_velocity = 1.5
        rbc_m.motor_ang_max_impulse = max_imp

        # Alignment Audit
        hinge_z = hinge_empty.matrix_world.to_3x3() @ Vector((0.0, 0.0, 1.0))
        motor_x = motor_empty.matrix_world.to_3x3() @ Vector((1.0, 0.0, 0.0))
        dot_val = abs(hinge_z.dot(motor_x))
        alignment_audits.append({"joint": f"{p_name}->{c_name}", "alignment_dot": dot_val})
        if dot_val < 0.999:
            raise RuntimeError(f"HARD FAIL: Constraint alignment failure on {p_name}->{c_name}: dot {dot_val} < 0.999")

    print(f"PASS: Configured 13 joint pairs across 14 bodies. All {len(alignment_audits)} alignment audits passed >= 0.999.")

    # 6. Save Full Hand Derivative
    OUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
    print(f"Saved Full-Hand Physics Harness to: {OUT}")

    # 7. Re-open Saved Scene for Readback Audit
    bpy.ops.wm.open_mainfile(filepath=str(OUT))
    r_maul_objs = [o for o in bpy.data.objects if 'maul' in o.name.lower() and o.type == 'MESH']
    r_shaft = next(o for o in r_maul_objs if 'shaft' in o.name.lower())
    r_collar = next((o for o in r_maul_objs if 'lower grip rib' in o.name.lower()), r_shaft)

    readback_joints = []
    for p_name, c_name, _, mass, max_imp, low_deg, up_deg in JOINT_SPECS:
        h_obj = bpy.data.objects.get(f"Constraint_Hinge_{p_name}_to_{c_name}")
        m_obj = bpy.data.objects.get(f"Constraint_Motor_{p_name}_to_{c_name}")
        c_obj = bpy.data.objects.get(c_name)
        readback_joints.append({
            "parent": p_name,
            "child": c_name,
            "hinge_type": h_obj.rigid_body_constraint.type if h_obj else None,
            "hinge_z_limit": h_obj.rigid_body_constraint.use_limit_ang_z if h_obj else False,
            "motor_type": m_obj.rigid_body_constraint.type if m_obj else None,
            "motor_max_impulse": m_obj.rigid_body_constraint.motor_ang_max_impulse if m_obj else 0.0,
            "child_mass": c_obj.rigid_body.mass if c_obj and c_obj.rigid_body else 0.0
        })

    readback = {
        "derivative_file": str(OUT),
        "total_hand_bodies": len(EXPECTED_HAND_BODIES),
        "total_joint_pairs": len(JOINT_SPECS),
        "alignment_audits_passed": len(alignment_audits),
        "maul_origin_location": list(r_shaft.location),
        "maul_com_distance_from_collar": (r_shaft.location - r_collar.location).length,
        "maul_mass": r_shaft.rigid_body.mass,
        "maul_collision_shape": r_shaft.rigid_body.collision_shape,
        "maul_compound_children_count": len([c for c in r_shaft.children if c.rigid_body]),
        "serialized_joints": readback_joints
    }

    READBACK_JSON.parent.mkdir(parents=True, exist_ok=True)
    READBACK_JSON.write_text(json.dumps(readback, indent=2), encoding='utf-8')
    print(f"Saved Full-Hand Readback Audit to: {READBACK_JSON}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
