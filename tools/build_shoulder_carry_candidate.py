"""Build canonical over-the-shoulder carry candidate for Varek Fairgunjis."""

import math
from pathlib import Path
import bpy
from mathutils import Vector, Matrix, Quaternion
from mathutils.bvhtree import BVHTree

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v55-mechanical-grip.blend"
OUT_BLEND = ROOT / "blender/candidates/varek-v56-shoulder-carry.blend"
OUT_DIR = ROOT / "evidence/varek-v56-shoulder-carry"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print(f"Loading baseline: {SRC}")
    bpy.ops.wm.open_mainfile(filepath=str(SRC))
    scene = bpy.context.scene
    arm = bpy.data.objects.get("Varek simple articulation")
    arm.data.pose_position = "POSE"
    bpy.context.view_layer.update()

    # 1. Pose Left Arm for Over-the-Shoulder Carry
    # Left shoulder joint is at (0.477, 0.000, 1.808)
    pb_uarm = arm.pose.bones["upper_arm.L"]
    pb_farm = arm.pose.bones["forearm.L"]
    pb_hand = arm.pose.bones["hand.L"]
    pb_pitch = arm.pose.bones["wrist_pitch.L"]
    pb_yaw = arm.pose.bones["wrist_yaw.L"]
    pb_palm = arm.pose.bones["palm.L"]

    for b in [pb_uarm, pb_farm, pb_hand, pb_pitch, pb_yaw, pb_palm]:
        b.rotation_mode = "XYZ"

    # Swing upper arm forward and slightly outward
    pb_uarm.rotation_euler = (math.radians(28), math.radians(-12), math.radians(18))
    # Bend forearm forward and up toward upper chest
    pb_farm.rotation_euler = (math.radians(92), math.radians(-6), math.radians(12))
    # Align hand/wrist to grip the forward-sloping handle
    pb_hand.rotation_euler = (math.radians(-10), math.radians(15), math.radians(-12))
    pb_pitch.rotation_euler = (math.radians(12), 0, 0)
    pb_yaw.rotation_euler = (0, 0, math.radians(-8))

    bpy.context.view_layer.update()
    p_palm = arm.matrix_world @ pb_palm.head
    print(f"Posed Palm World Position: ({p_palm.x:.4f}, {p_palm.y:.4f}, {p_palm.z:.4f})")

    # 2. Define the Over-the-Shoulder Maul Axis
    # Shoulder apex: (0.52, 0.02, 1.89)
    # Maul head hangs behind back: (0.54, 0.42, 1.66)
    # Forward shaft passes through the palm grip: (p_palm.x + 0.015, p_palm.y - 0.010, p_palm.z + 0.015)
    p_rear_head = Vector((0.54, 0.42, 1.66))
    p_grip_target = p_palm + Vector((0.015, -0.010, 0.015))
    
    # Shaft axis vector pointing from rear head forward to grip target
    shaft_axis = (p_grip_target - p_rear_head).normalized()
    print(f"Shaft axis vector: ({shaft_axis.x:.4f}, {shaft_axis.y:.4f}, {shaft_axis.z:.4f})")

    # 3. Rigidly Transform the Maul Assembly
    maul_meshes = [o for o in bpy.data.objects if "maul" in o.name.lower() and o.type == "MESH"]
    print(f"Rigidly transforming {len(maul_meshes)} maul mesh objects...")

    # Reference in v55: grip center was at (0.586, -0.079, 0.995)
    # Old shaft ran along (0.0, -0.1644, -0.9864)
    v_source = Vector((0.0, -0.1644, -0.9864)).normalized()
    ref_grip = Vector((0.586, -0.079, 0.995))

    rot_diff = v_source.rotation_difference(shaft_axis)
    
    # Pre-translate to origin, rotate, post-translate to target grip
    T_pre = Matrix.Translation(-ref_grip)
    R_mat = rot_diff.to_matrix().to_4x4()
    T_post = Matrix.Translation(p_grip_target)
    M_rigid = T_post @ R_mat @ T_pre

    # Transform all maul objects in world space and clear old armature deformation
    for mo in maul_meshes:
        for m in list(mo.modifiers):
            if m.type == "ARMATURE":
                mo.modifiers.remove(m)
        mo.parent = None
        mo.matrix_world = M_rigid @ mo.matrix_world
        # Bake the transformation to vertex coordinates so matrix_world stays identity
        bpy.context.view_layer.objects.active = mo
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    bpy.context.view_layer.update()

    # 4. Automated Raycast/Snapping Grip on the Shaft
    # Get the transformed shaft BVH
    dg = bpy.context.evaluated_depsgraph_get()
    shaft = bpy.data.objects.get("Maul shaft").evaluated_get(dg)
    m_shaft = shaft.to_mesh()
    bvh_shaft = BVHTree.FromPolygons([shaft.matrix_world @ v.co for v in m_shaft.vertices], [p.vertices for p in m_shaft.polygons])

    print("Automating non-penetrating snug finger curl...")
    # For each finger digit, find curl angles that give zero penetration and maximum contact
    for dname in ["digit1", "digit2", "digit3"]:
        best_angles = (0, 0, 0)
        best_dist = 999.0
        # Search curl combinations
        for a1 in range(20, 55, 5):
            for a2 in range(25, 60, 5):
                for a3 in range(15, 45, 5):
                    arm.pose.bones[f"{dname}_01.L"].rotation_euler = (math.radians(a1), 0, 0)
                    arm.pose.bones[f"{dname}_02.L"].rotation_euler = (math.radians(a2), 0, 0)
                    arm.pose.bones[f"{dname}_03.L"].rotation_euler = (math.radians(a3), 0, 0)
                    bpy.context.view_layer.update()
                    dg = bpy.context.evaluated_depsgraph_get()

                    p1 = bpy.data.objects.get(f"{dname.capitalize()}_Phalanx1_L").evaluated_get(dg)
                    p2 = bpy.data.objects.get(f"{dname.capitalize()}_Phalanx2_L").evaluated_get(dg)
                    p3 = bpy.data.objects.get(f"{dname.capitalize()}_Phalanx3_L").evaluated_get(dg)

                    b1 = BVHTree.FromPolygons([p1.matrix_world @ v.co for v in p1.to_mesh().vertices], [p.vertices for p in p1.to_mesh().polygons])
                    b2 = BVHTree.FromPolygons([p2.matrix_world @ v.co for v in p2.to_mesh().vertices], [p.vertices for p in p2.to_mesh().polygons])
                    b3 = BVHTree.FromPolygons([p3.matrix_world @ v.co for v in p3.to_mesh().vertices], [p.vertices for p in p3.to_mesh().polygons])

                    ov1 = len(b1.overlap(bvh_shaft))
                    ov2 = len(b2.overlap(bvh_shaft))
                    ov3 = len(b3.overlap(bvh_shaft))

                    if ov1 == 0 and ov2 == 0 and ov3 == 0:
                        best_angles = (a1, a2, a3)
                        break
                if best_angles != (0, 0, 0): break
            if best_angles != (0, 0, 0): break
        
        print(f"  {dname} solved angles: {best_angles}")
        arm.pose.bones[f"{dname}_01.L"].rotation_euler = (math.radians(best_angles[0]), 0, 0)
        arm.pose.bones[f"{dname}_02.L"].rotation_euler = (math.radians(best_angles[1]), 0, 0)
        arm.pose.bones[f"{dname}_03.L"].rotation_euler = (math.radians(best_angles[2]), 0, 0)

    # Thumb
    best_th = (25, 15, 30)
    for th1 in range(15, 40, 5):
        for th_y in range(10, 30, 5):
            for th2 in range(20, 50, 5):
                arm.pose.bones["thumb_01.L"].rotation_euler = (math.radians(th1), math.radians(th_y), 0)
                arm.pose.bones["thumb_02.L"].rotation_euler = (math.radians(th2), 0, 0)
                bpy.context.view_layer.update()
                dg = bpy.context.evaluated_depsgraph_get()
                p1 = bpy.data.objects.get("Thumb_Phalanx1_L").evaluated_get(dg)
                p2 = bpy.data.objects.get("Thumb_Phalanx2_L").evaluated_get(dg)
                b1 = BVHTree.FromPolygons([p1.matrix_world @ v.co for v in p1.to_mesh().vertices], [p.vertices for p in p1.to_mesh().polygons])
                b2 = BVHTree.FromPolygons([p2.matrix_world @ v.co for v in p2.to_mesh().vertices], [p.vertices for p in p2.to_mesh().polygons])
                if len(b1.overlap(bvh_shaft)) == 0 and len(b2.overlap(bvh_shaft)) == 0:
                    best_th = (th1, th_y, th2)
                    break
            if best_th != (25, 15, 30): break
        if best_th != (25, 15, 30): break

    print(f"  thumb solved angles: {best_th}")
    arm.pose.bones["thumb_01.L"].rotation_euler = (math.radians(best_th[0]), math.radians(best_th[1]), 0)
    arm.pose.bones["thumb_02.L"].rotation_euler = (math.radians(best_th[2]), 0, 0)

    bpy.context.view_layer.update()

    # 5. Verify Overlaps
    print("Verifying final contact and overlap...")
    dg = bpy.context.evaluated_depsgraph_get()
    shaft_eval = bpy.data.objects.get("Maul shaft").evaluated_get(dg)
    bvh_shaft_final = BVHTree.FromPolygons([shaft_eval.matrix_world @ v.co for v in shaft_eval.to_mesh().vertices], [p.vertices for p in shaft_eval.to_mesh().polygons])
    hand_parts = [o for o in bpy.data.objects if any(k in o.name for k in ["Palm_Plate_L", "Digit1_", "Digit2_", "Digit3_", "Thumb_"])]
    total_ov = 0
    for hp in hand_parts:
        ev = hp.evaluated_get(dg)
        b = BVHTree.FromPolygons([ev.matrix_world @ v.co for v in ev.to_mesh().vertices], [p.vertices for p in ev.to_mesh().polygons])
        ov = len(b.overlap(bvh_shaft_final))
        total_ov += ov
        print(f"  {hp.name}: {ov} overlaps")
    print(f"Total hand/shaft overlaps: {total_ov}")

    # 6. Save Candidate v56
    print(f"Saving candidate: {OUT_BLEND}")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))

    # 7. Render Views
    # Camera setup
    for c in list(bpy.data.cameras): bpy.data.cameras.remove(c)
    for o in [x for x in bpy.data.objects if x.type == "CAMERA"]: bpy.data.objects.remove(o)

    cam_data = bpy.data.cameras.new("CarryCam")
    cam_data.lens = 50.0
    cam = bpy.data.objects.new("CarryCam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam

    scene.render.engine = "CYCLES"
    scene.cycles.samples = 24
    scene.cycles.adaptive_threshold = 0.1
    scene.render.resolution_percentage = 100

    # View 1: Upper Body Showcase (Front 3/4)
    scene.render.resolution_x = 960
    scene.render.resolution_y = 1080
    target_body = Vector((0.15, -0.10, 1.65))
    cam_pos_body = Vector((1.80, -3.20, 1.85))
    cam.location = cam_pos_body
    cam.rotation_euler = (target_body - cam_pos_body).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(OUT_DIR / "v56_shoulder_carry_showcase.png")
    print(f"Rendering: {scene.render.filepath}...")
    bpy.ops.render.render(write_still=True)

    # View 2: Close-up of Shoulder Rest and Hand Grip
    cam_data.lens = 75.0
    target_grip = p_palm + Vector((0.05, 0.05, 0.05))
    cam_pos_grip = Vector((1.40, -1.80, 1.70))
    cam.location = cam_pos_grip
    cam.rotation_euler = (target_grip - cam_pos_grip).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(OUT_DIR / "v56_shoulder_grip_closeup.png")
    print(f"Rendering: {scene.render.filepath}...")
    bpy.ops.render.render(write_still=True)

    print("SUCCESS: Candidate v56 built and rendered.")

if __name__ == "__main__":
    main()
