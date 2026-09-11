"""True Front-View Over-the-Shoulder Carry for Varek Fairgunjis (Varek faces +Y)."""

import math
from pathlib import Path
import bpy
from mathutils import Vector, Matrix

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v55-mechanical-grip.blend"
OUT_BLEND = ROOT / "blender/candidates/varek-v56-shoulder-carry.blend"
OUT_IMG = ROOT / "evidence/varek-v56-shoulder-carry/v56_shoulder_carry_front_q34.png"

def main():
    print(f"Loading: {SRC}")
    bpy.ops.wm.open_mainfile(filepath=str(SRC))
    scene = bpy.context.scene
    arm = bpy.data.objects.get("Varek simple articulation")
    arm.data.pose_position = "POSE"
    bpy.context.view_layer.update()

    # VAREK FACES +Y. Back is -Y. Left arm is +X. Right arm is -X.
    # 1. Maul Over-the-Shoulder Geometry:
    # Heavy head sits behind left shoulder: X=0.55, Y=-0.40 (rear), Z=1.65
    # Shaft crosses shoulder cowl at: X=0.52, Y=0.00, Z=1.89
    # Forward handle extends forward across upper chest: X=0.42, Y=+0.42 (front), Z=1.50
    p_head_rear = Vector((0.55, -0.40, 1.65))
    p_haft_front = Vector((0.40, 0.42, 1.50))
    shaft_axis = (p_haft_front - p_head_rear).normalized()

    # Hand grip location on forward haft:
    p_grip = p_head_rear + shaft_axis * 0.72  # in front of left chest at Y ~ +0.18, Z ~ 1.55

    # 2. Rigid transformation of all 27 maul meshes
    maul_meshes = [o for o in bpy.data.objects if "maul" in o.name.lower() and o.type == "MESH"]
    ref_grip = Vector((0.586, -0.079, 0.995))
    # In v55, shaft pointed down (-Z)
    v_source = Vector((0.0, -0.1644, -0.9864)).normalized()
    rot_diff = v_source.rotation_difference(shaft_axis)

    T_pre = Matrix.Translation(-ref_grip)
    R_mat = rot_diff.to_matrix().to_4x4()
    T_post = Matrix.Translation(p_grip)
    M_rigid = T_post @ R_mat @ T_pre

    for mo in maul_meshes:
        for m in list(mo.modifiers):
            if m.type == "ARMATURE":
                mo.modifiers.remove(m)
        mo.parent = None
        mo.matrix_world = M_rigid @ mo.matrix_world
        bpy.context.view_layer.objects.active = mo
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    bpy.context.view_layer.update()

    # 3. Pose Left Arm with IK toward p_grip
    target_empty = bpy.data.objects.get("Maul_IK_Target")
    if not target_empty:
        target_empty = bpy.data.objects.new("Maul_IK_Target", None)
        scene.collection.objects.link(target_empty)
    # Position IK target so palm cradles the forward shaft
    target_empty.location = p_grip + Vector((0.02, -0.03, -0.02))

    pb_farm = arm.pose.bones["forearm.L"]
    c_ik = pb_farm.constraints.get("Maul_IK")
    if not c_ik:
        c_ik = pb_farm.constraints.new(type="IK")
        c_ik.name = "Maul_IK"
    c_ik.target = target_empty
    c_ik.chain_count = 2
    c_ik.iterations = 50

    # Wrist alignment
    pb_pitch = arm.pose.bones["wrist_pitch.L"]
    pb_yaw = arm.pose.bones["wrist_yaw.L"]
    pb_pitch.rotation_euler = (math.radians(15), 0, 0)
    pb_yaw.rotation_euler = (0, 0, math.radians(-10))

    # Digits curl around shaft
    for dname in ["digit1", "digit2", "digit3"]:
        arm.pose.bones[f"{dname}_01.L"].rotation_euler = (math.radians(40), 0, 0)
        arm.pose.bones[f"{dname}_02.L"].rotation_euler = (math.radians(45), 0, 0)
        arm.pose.bones[f"{dname}_03.L"].rotation_euler = (math.radians(35), 0, 0)

    arm.pose.bones["thumb_01.L"].rotation_euler = (math.radians(25), math.radians(15), 0)
    arm.pose.bones["thumb_02.L"].rotation_euler = (math.radians(35), 0, 0)

    bpy.context.view_layer.update()

    # 4. Camera Setup: TRUE FRONT THREEQUARTER (+Y view)
    for c in list(bpy.data.cameras): bpy.data.cameras.remove(c)
    for o in [x for x in bpy.data.objects if x.type == "CAMERA"]: bpy.data.objects.remove(o)

    cam_data = bpy.data.cameras.new("FrontCam")
    cam_data.lens = 55.0
    cam = bpy.data.objects.new("FrontCam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam

    # Looking at Varek from FRONT (+Y) and left-quarter (+X)
    target = Vector((0.15, 0.05, 1.55))
    cam_loc = Vector((2.20, 4.20, 2.05))
    cam.location = cam_loc
    cam.rotation_euler = (target - cam_loc).to_track_quat("-Z", "Y").to_euler()

    scene.render.engine = "CYCLES"
    scene.cycles.samples = 24
    scene.cycles.adaptive_threshold = 0.1
    scene.render.resolution_x = 960
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(OUT_IMG)

    print(f"Saving candidate: {OUT_BLEND}")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))

    print(f"Rendering: {OUT_IMG}...")
    bpy.ops.render.render(write_still=True)
    print(f"Render completed: {OUT_IMG}")

if __name__ == "__main__":
    main()
