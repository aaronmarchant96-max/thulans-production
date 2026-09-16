from __future__ import annotations
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector, Euler

ROOT = Path("/home/aaron/animation/thulans-production")
TEST_BLEND = ROOT / "blender/candidates/varek-v55-hand-physics.blend"
EVIDENCE_DIR = ROOT / "evidence/varek-v55-mechanical-grip"

def setup_render_settings(scene):
    scene.render.engine = "BLENDER_EEVEE_NEXT" if hasattr(bpy.types, "RenderEngineEEVEENext") else "BLENDER_EEVEE"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.display.shading.type = "SOLID"
    scene.display.shading.color_type = "OBJECT"
    scene.display.shading.show_xray = False

def create_or_get_camera(scene, cam_name: str, location: Vector, rotation_euler: Euler) -> bpy.types.Object:
    cam_obj = bpy.data.objects.get(cam_name)
    if not cam_obj:
        cam_data = bpy.data.cameras.new(cam_name)
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        scene.collection.objects.link(cam_obj)
    cam_obj.location = location
    cam_obj.rotation_euler = rotation_euler
    return cam_obj

def setup_lighting(scene):
    light_name = "Diag_Key_Light"
    light_obj = bpy.data.objects.get(light_name)
    if not light_obj:
        light_data = bpy.data.lights.new(light_name, type="SUN")
        light_data.energy = 3.0
        light_obj = bpy.data.objects.new(light_name, light_data)
        scene.collection.objects.link(light_obj)
    light_obj.location = Vector((2.0, -3.0, 4.0))
    light_obj.rotation_euler = Euler((math.radians(45), math.radians(15), math.radians(30)), "XYZ")

def main():
    if not TEST_BLEND.exists():
        print("HARD FAIL: Candidate blend missing.")
        return 1

    bpy.ops.wm.open_mainfile(filepath=str(TEST_BLEND))
    scene = bpy.context.scene
    setup_render_settings(scene)
    setup_lighting(scene)

    palm = bpy.data.objects.get("Palm_Plate_L")
    if not palm:
        print("HARD FAIL: Palm_Plate_L missing.")
        return 1

    system_center = Vector((0.588, -0.039, 0.998))

    # 1. Palm-Facing Camera (Frontal elevated view showing full hand, wrist, shaft, and fingers)
    cam_palm_loc = system_center + Vector((0.0, -1.9, 0.1))
    cam_palm_rot = Euler((math.radians(85), 0.0, 0.0), "XYZ")
    cam_palm = create_or_get_camera(scene, "Cam_Palm_Facing", cam_palm_loc, cam_palm_rot)

    # 2. Side Profile Camera (Lateral elevated view showing full hand depth and thumb opposition line)
    cam_side_loc = system_center + Vector((1.9, 0.0, 0.1))
    cam_side_rot = Euler((math.radians(85), 0.0, math.radians(90)), "XYZ")
    cam_side = create_or_get_camera(scene, "Cam_Side_Profile", cam_side_loc, cam_side_rot)

    # 3. Oblique Shaft Camera (3/4 view down shaft axis framing complete hand)
    cam_oblique_loc = system_center + Vector((1.4, -1.4, 0.7))
    cam_oblique_rot = Euler((math.radians(60), 0.0, math.radians(40)), "XYZ")
    cam_oblique = create_or_get_camera(scene, "Cam_Oblique_Grip", cam_oblique_loc, cam_oblique_rot)

    # Step rigid body physics frame-by-frame to frame 60 to ensure point cache evaluation
    def step_physics_to(target_frame: int):
        scene.frame_set(1)
        for f in range(1, target_frame + 1):
            scene.frame_set(f)

    frames_to_render = [(15, "f015_open"), (40, "f040_closed"), (60, "f060_reopened")]
    cams = [(cam_palm, "palm"), (cam_side, "side"), (cam_oblique, "oblique")]

    for frame_num, frame_label in frames_to_render:
        step_physics_to(frame_num)
        for cam_obj, cam_label in cams:
            scene.camera = cam_obj
            out_file = Path(f"/tmp/varek_v55_{frame_label}_{cam_label}.png")
            scene.render.filepath = str(out_file)
            bpy.ops.render.render(write_still=True)
            print(f"Rendered Frame {frame_num} {cam_label} View: {out_file}")

    # Also save priority f40 palm image
    step_physics_to(40)
    scene.camera = cam_palm
    out_f40_palm = Path("/tmp/varek_v55_frame040_palm_facing.png")
    scene.render.filepath = str(out_f40_palm)
    bpy.ops.render.render(write_still=True)

    return 0

if __name__ == "__main__":
    sys.exit(main())
