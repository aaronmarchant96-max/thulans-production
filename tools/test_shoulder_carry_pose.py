"""Test positioning the Faírguni-Hamars maul carried over Varek's left shoulder."""

import math
from pathlib import Path
import bpy
from mathutils import Vector, Matrix

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

    # 1. Pose Left Arm to rest hand on the forward haft across the chest/shoulder
    pb_uarm = arm.pose.bones["upper_arm.L"]
    pb_uarm.rotation_mode = "XYZ"
    pb_farm = arm.pose.bones["forearm.L"]
    pb_farm.rotation_mode = "XYZ"
    pb_hand = arm.pose.bones["hand.L"]
    pb_hand.rotation_mode = "XYZ"

    # Swing upper arm slightly forward and out
    pb_uarm.rotation_euler = (math.radians(25), math.radians(-10), math.radians(15))
    # Bend forearm forward and up
    pb_farm.rotation_euler = (math.radians(95), math.radians(0), math.radians(15))

    # Wrist pitch and yaw to align with diagonal shaft
    pb_pitch = arm.pose.bones["wrist_pitch.L"]
    pb_pitch.rotation_euler = (math.radians(20), 0, 0)
    pb_yaw = arm.pose.bones["wrist_yaw.L"]
    pb_yaw.rotation_euler = (0, 0, math.radians(15))

    bpy.context.view_layer.update()
    pb_palm = arm.pose.bones["palm.L"]
    palm_world_loc = arm.matrix_world @ pb_palm.head
    print(f"Posed Palm World Location: {palm_world_loc}")

    # 2. Position the Maul over the left shoulder
    # The shaft rests on the top of the left shoulder armor
    # Striking head is behind the back: X=0.60, Y=0.45, Z=1.65
    # Shaft passes over shoulder at X=0.55, Y=0.05, Z=1.88
    # Forward haft extends down across front chest toward hand at X=0.48, Y=-0.35, Z=1.55
    p_head = Vector((0.58, 0.40, 1.68))
    p_front = Vector((0.46, -0.45, 1.48))
    new_shaft_dir = (p_front - p_head).normalized()

    maul_meshes = [o for o in bpy.data.objects if "maul" in o.name.lower() and o.type == "MESH"]
    
    # Original shaft ran along (0, -0.1644, -0.9864)
    v_old = Vector((0.0, -0.1644, -0.9864)).normalized()
    rot_q = v_old.rotation_difference(new_shaft_dir)
    
    # In the original maul, the lower grip was at Vector((0.586, -0.055, 0.995))
    # In the shoulder carry, we want the lower grip zone to be near the hand:
    target_grip = palm_world_loc + Vector((0.02, 0.02, -0.01))
    old_grip_center = Vector((0.586, -0.055, 0.995))

    for mo in maul_meshes:
        for v in mo.data.vertices:
            wco = mo.matrix_world @ v.co
            rel = wco - old_grip_center
            new_wco = target_grip + (rot_q @ rel)
            v.co = mo.matrix_world.inverted() @ new_wco
        mo.data.update()

    # Digits curl around the diagonal shaft
    digit_x_offsets = ["digit1", "digit2", "digit3"]
    for dname in digit_x_offsets:
        arm.pose.bones[f"{dname}_01.L"].rotation_euler = (math.radians(45), 0.0, 0.0)
        arm.pose.bones[f"{dname}_02.L"].rotation_euler = (math.radians(50), 0.0, 0.0)
        arm.pose.bones[f"{dname}_03.L"].rotation_euler = (math.radians(40), 0.0, 0.0)

    arm.pose.bones["thumb_01.L"].rotation_euler = (math.radians(30), math.radians(20), 0.0)
    arm.pose.bones["thumb_02.L"].rotation_euler = (math.radians(40), 0.0, 0.0)

    bpy.context.view_layer.update()

    # 3. Setup Camera for Upper Body Showcase (3/4 front view)
    for c in list(bpy.data.cameras): bpy.data.cameras.remove(c)
    for o in [x for x in bpy.data.objects if x.type == "CAMERA"]: bpy.data.objects.remove(o)

    cam_data = bpy.data.cameras.new("ShoulderCarryCam")
    cam_data.lens = 55.0
    cam_obj = bpy.data.objects.new("ShoulderCarryCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Position camera to see the full upper torso, both arms, and the maul resting on the shoulder
    target = Vector((0.15, 0.0, 1.65))
    cam_loc = Vector((1.75, -2.30, 1.85))
    cam_obj.location = cam_loc
    cam_obj.rotation_euler = (target - cam_loc).to_track_quat("-Z", "Y").to_euler()

    # Render settings
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 24
    scene.cycles.adaptive_threshold = 0.1
    scene.render.resolution_x = 960
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(OUT_IMG)

    print(f"Rendering: {OUT_IMG}...")
    bpy.ops.render.render(write_still=True)
    print(f"Render finished: {OUT_IMG}")

if __name__ == "__main__":
    main()
