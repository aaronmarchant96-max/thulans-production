"""True Over-the-Shoulder Rest for Varek Fairgunjis."""

import math
from pathlib import Path
import bpy
from mathutils import Vector, Matrix

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v55-mechanical-grip.blend"
OUT_BLEND = ROOT / "blender/candidates/varek-v56-shoulder-rest.blend"
OUT_IMG = ROOT / "evidence/varek-v56-shoulder-carry/v56_shoulder_rest_front.png"

def main():
    print(f"Loading: {SRC}")
    bpy.ops.wm.open_mainfile(filepath=str(SRC))
    scene = bpy.context.scene
    arm = bpy.data.objects.get("Varek simple articulation")
    arm.data.pose_position = "POSE"
    bpy.context.view_layer.update()

    # 1. Geometry of the Over-the-Shoulder Rest:
    # The shaft rests across the top apex of the Gren-Skildus plate at X=0.54, Y=0.00, Z=1.92
    # The striking head hangs down behind the left back: X=0.55, Y=-0.45, Z=1.55
    # The forward shaft extends forward and down: X=0.50, Y=+0.45, Z=1.75
    p_rear_head = Vector((0.55, -0.45, 1.55))
    p_front_tip = Vector((0.50, 0.45, 1.75))
    shaft_dir = (p_front_tip - p_rear_head).normalized()

    # Hand grip position along the forward shaft:
    p_grip = p_rear_head + shaft_dir * 0.72  # in front of left shoulder at Y ~ +0.20, Z ~ 1.70

    # Rigid transformation of the entire 27-part Maul assembly
    maul_meshes = [o for o in bpy.data.objects if "maul" in o.name.lower() and o.type == "MESH"]
    ref_grip = Vector((0.586, -0.079, 0.995))
    v_source = Vector((0.0, -0.1644, -0.9864)).normalized()
    rot_diff = v_source.rotation_difference(shaft_dir)

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

    # 2. Pose Left Arm to reach up and steady the shaft on the shoulder
    target_empty = bpy.data.objects.get("Maul_IK_Target")
    if not target_empty:
        target_empty = bpy.data.objects.new("Maul_IK_Target", None)
        scene.collection.objects.link(target_empty)
    target_empty.location = p_grip + Vector((0.01, -0.02, -0.03))

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
    pb_pitch.rotation_euler = (math.radians(20), 0, 0)
    pb_yaw.rotation_euler = (0, 0, math.radians(-10))

    # Digits curl around shaft
    for dname in ["digit1", "digit2", "digit3"]:
        arm.pose.bones[f"{dname}_01.L"].rotation_euler = (math.radians(45), 0, 0)
        arm.pose.bones[f"{dname}_02.L"].rotation_euler = (math.radians(45), 0, 0)
        arm.pose.bones[f"{dname}_03.L"].rotation_euler = (math.radians(35), 0, 0)

    arm.pose.bones["thumb_01.L"].rotation_euler = (math.radians(25), math.radians(15), 0)
    arm.pose.bones["thumb_02.L"].rotation_euler = (math.radians(35), 0, 0)

    bpy.context.view_layer.update()

    # 3. Setup Camera: Front Threequarter (+Y view)
    for c in list(bpy.data.cameras): bpy.data.cameras.remove(c)
    for o in [x for x in bpy.data.objects if x.type == "CAMERA"]: bpy.data.objects.remove(o)

    cam_data = bpy.data.cameras.new("FrontCam")
    cam_data.lens = 55.0
    cam = bpy.data.objects.new("FrontCam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam

    # Looking at Varek from FRONT (+Y) and left-quarter (+X)
    target = Vector((0.15, 0.05, 1.65))
    cam_loc = Vector((2.20, 4.20, 2.15))
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
