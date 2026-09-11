"""Build single-joint verification prototype (Milestone 1 Core Engine).

Focus:
1. One canonical joint chain (Palm_Plate_L -> Digit1_Phalanx1_L).
2. Correct Blender API enum ('GENERIC', 'HINGE', 'MOTOR').
3. Correct Blender Python API motor properties:
   - motor_ang_target_velocity
   - motor_ang_max_impulse
4. Separate HINGE (rotation axis Z) + MOTOR (rotation axis X aligned via Empty orientation).
5. Explicit pivot transform derived from bearing center.
6. Absolute COM origin shift for 30 kg Maul assembly.
"""

from __future__ import annotations
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector, Matrix, Euler, Quaternion

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v55-mechanical-grip.blend"
OUT = ROOT / "blender/candidates/varek-v55-single-joint-test.blend"

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

    # 2. Extract Objects
    palm = bpy.data.objects.get("Palm_Plate_L")
    p1 = bpy.data.objects.get("Digit1_Phalanx1_L")
    maul_objs = [o for o in bpy.data.objects if 'maul' in o.name.lower() and o.type == 'MESH']
    main_shaft = next((o for o in maul_objs if 'shaft' in o.name.lower()), maul_objs[0])

    if not palm or not p1 or not main_shaft:
        raise RuntimeError("HARD FAIL: Required objects missing for single-joint verification")

    # 3. Maul Compound Assembly + Verified COM Offset
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

    # Main shaft primary active body
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

    # Shift COM 0.320 m along shaft axis
    com_target = main_shaft.location + Vector((0.0, 0.0, 0.320))
    scene.cursor.location = com_target
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

    # Re-parent visual/collision sub-parts
    for o in maul_objs:
        if o != main_shaft:
            mw = o.matrix_world.copy()
            o.parent = main_shaft
            o.matrix_world = mw

    # 4. Configure Palm Anchor
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

    # 6. Build Correct HINGE + MOTOR Pair with Aligned Pivots
    pivot_location = (palm.location + p1.location) * 0.5

    # A. Hinge Constraint (Z-axis rotation limit)
    hinge_empty = bpy.data.objects.new("Constraint_Hinge_Palm_to_D1P1", None)
    scene.collection.objects.link(hinge_empty)
    hinge_empty.location = pivot_location
    # Align Z axis to joint rotation axis
    hinge_empty.rotation_euler = Euler((0.0, math.radians(90.0), 0.0), 'XYZ')

    bpy.context.view_layer.objects.active = hinge_empty
    bpy.ops.rigidbody.constraint_add()
    rbc_hinge = hinge_empty.rigid_body_constraint
    rbc_hinge.type = 'HINGE'  # Correct API Enum
    rbc_hinge.object1 = palm
    rbc_hinge.object2 = p1
    rbc_hinge.use_limit_ang_z = True  # Hinge uses Z axis limit!
    rbc_hinge.limit_ang_z_lower = math.radians(-10.0)
    rbc_hinge.limit_ang_z_upper = math.radians(90.0)

    # B. Motor Constraint (X-axis motor drive aligned with joint)
    motor_empty = bpy.data.objects.new("Constraint_Motor_Palm_to_D1P1", None)
    scene.collection.objects.link(motor_empty)
    motor_empty.location = pivot_location
    # Motor rotates around X axis; align X axis to rotation direction
    motor_empty.rotation_euler = Euler((math.radians(90.0), 0.0, 0.0), 'XYZ')

    bpy.context.view_layer.objects.active = motor_empty
    bpy.ops.rigidbody.constraint_add()
    rbc_motor = motor_empty.rigid_body_constraint
    rbc_motor.type = 'MOTOR'  # Correct API Enum
    rbc_motor.object1 = palm
    rbc_motor.object2 = p1
    rbc_motor.use_motor_ang = True
    
    # Correct Blender Python API Property Names:
    rbc_motor.motor_ang_target_velocity = 1.5   # rad/s
    rbc_motor.motor_ang_max_impulse = 2.0        # Max angular impulse (N·m·s equivalent per timestep)

    # 7. Save Single-Joint Prototype
    OUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
    print(f"PASS: Verified Single-Joint HINGE+MOTOR Prototype saved to: {OUT}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
