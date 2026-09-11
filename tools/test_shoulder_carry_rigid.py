"""Rigid over-the-shoulder carry test for Varek and the Faírguni-Hamars maul."""

import math
from pathlib import Path
import bpy
from mathutils import Vector, Matrix, Euler, Quaternion

ROOT = Path("/home/aaron/animation/thulans-production")
CAND = ROOT / "blender/candidates/varek-v55-mechanical-grip.blend"
OUT_IMG = ROOT / "evidence/varek-v55-mechanical-grip/shoulder_carry_test.png"

def main():
    print(f"Loading: {CAND}")
    bpy.ops.wm.open_mainfile(filepath=str(CAND))
    scene = bpy.context.scene
    arm = bpy.data.objects.get("Varek simple articulation")
    arm.data.pose_position = "POSE"
    bpy.context.view_layer.update()

    # 1. Pose Left Arm for over-the-shoulder steady grip
    pb_uarm = arm.pose.bones["upper_arm.L"]
    pb_farm = arm.pose.bones["forearm.L"]
    pb_hand = arm.pose.bones["hand.L"]
    pb_pitch = arm.pose.bones["wrist_pitch.L"]
    pb_yaw = arm.pose.bones["wrist_yaw.L"]
    pb_palm = arm.pose.bones["palm.L"]

    for b in [pb_uarm, pb_farm, pb_hand, pb_pitch, pb_yaw, pb_palm]:
        b.rotation_mode = "XYZ"

    # Pose arm: elbow bent ~100 deg, upper arm forward ~30 deg
    pb_uarm.rotation_euler = (math.radians(30), math.radians(-10), math.radians(20))
    pb_farm.rotation_euler = (math.radians(95), math.radians(-5), math.radians(15))
    pb_hand.rotation_euler = (math.radians(-15), math.radians(10), math.radians(-10))
    pb_pitch.rotation_euler = (math.radians(10), 0, 0)
    pb_yaw.rotation_euler = (0, 0, math.radians(-10))

    bpy.context.view_layer.update()
    p_palm_w = arm.matrix_world @ pb_palm.head
    print(f"Posed palm head world: {p_palm_w}")

    # 2. Define the rigid shoulder-carry line
    # Maul head behind left shoulder, haft resting on shoulder cowl, handle extending to hand
    # Point on shoulder rest: (0.54, 0.05, 1.84)
    # Point at hand grip: (p_palm_w.x + 0.02, p_palm_w.y + 0.02, p_palm_w.z)
    p_shoulder_rest = Vector((0.54, 0.05, 1.84))
    p_hand_grip = p_palm_w + Vector((0.02, 0.01, 0.00))
    
    # Direction of shaft from head (behind) to pommel (in front)
    shaft_axis = (p_hand_grip - p_shoulder_rest).normalized()
    print(f"Shaft axis vector: {shaft_axis}")

    # 3. Rigid transform of the entire Maul assembly
    maul_meshes = [o for o in bpy.data.objects if "maul" in o.name.lower() and o.type == "MESH"]
    print(f"Found {len(maul_meshes)} maul meshes")

    # Current reference points in candidate v55 (before posing)
    # Maul lower grip center was around (0.586, -0.079, 0.995)
    # Maul shaft direction was (0.0, -0.1644, -0.9864).normalized()
    ref_grip = Vector((0.586, -0.079, 0.995))
    v_source = Vector((0.0, -0.1644, -0.9864)).normalized()
    
    # Rotation to align shaft with new axis
    rot_diff = v_source.rotation_difference(shaft_axis)
    
    # Rigid transformation matrix for world space
    # M_rigid maps any world point: p_new = p_hand_grip + rot_diff @ (p_old - ref_grip)
    T_pre = Matrix.Translation(-ref_grip)
    R_mat = rot_diff.to_matrix().to_4x4()
    T_post = Matrix.Translation(p_hand_grip)
    M_rigid = T_post @ R_mat @ T_pre

    # Apply rigidly to each maul object without distorting individual vertex coordinates
    for o in maul_meshes:
        # Clear any armature modifier or parenting on maul for this carry pose study
        for m in list(o.modifiers):
            if m.type == "ARMATURE":
                o.modifiers.remove(m)
        o.parent = None
        o.matrix_world = M_rigid @ o.matrix_world

    # Curl digits comfortably around the shaft
    for dname in ["digit1", "digit2", "digit3"]:
        arm.pose.bones[f"{dname}_01.L"].rotation_euler = (math.radians(45), 0, 0)
        arm.pose.bones[f"{dname}_02.L"].rotation_euler = (math.radians(50), 0, 0)
        arm.pose.bones[f"{dname}_03.L"].rotation_euler = (math.radians(35), 0, 0)

    arm.pose.bones["thumb_01.L"].rotation_euler = (math.radians(30), math.radians(20), 0)
    arm.pose.bones["thumb_02.L"].rotation_euler = (math.radians(40), 0, 0)

    bpy.context.view_layer.update()

    # 4. Setup Camera for 3/4 Front Upper Body View
    for c in list(bpy.data.cameras): bpy.data.cameras.remove(c)
    for o in [x for x in bpy.data.objects if x.type == "CAMERA"]: bpy.data.objects.remove(o)

    cam_data = bpy.data.cameras.new("ShoulderCam")
    cam_data.lens = 55.0
    cam = bpy.data.objects.new("ShoulderCam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam

    # Looking at upper torso from 3/4 front-left
    # Varek faces -Y (front). So camera should be at -Y (e.g. Y = -3.5) and +X (e.g. X = 1.8)
    target = Vector((0.20, -0.10, 1.65))
    cam_pos = Vector((1.60, -3.20, 1.85))
    cam.location = cam_pos
    cam.rotation_euler = (target - cam_pos).to_track_quat("-Z", "Y").to_euler()

    scene.render.engine = "CYCLES"
    scene.cycles.samples = 24
    scene.cycles.adaptive_threshold = 0.1
    scene.render.resolution_x = 960
    scene.render.resolution_y = 1100
    scene.render.filepath = str(OUT_IMG)

    print(f"Rendering: {OUT_IMG}...")
    bpy.ops.render.render(write_still=True)
    print(f"Render completed: {OUT_IMG}")

if __name__ == "__main__":
    main()
