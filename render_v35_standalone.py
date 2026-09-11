import bpy
import math
import os
from mathutils import Vector

BLEND_PATH = "/home/aaron/animation/thulans-production/blender/candidates/varek-v35-canonical.blend"
RENDER_HEAD = "/home/aaron/animation/thulans-production/assets/art/varek_v35_head_closeup_frame_001.png"
RENDER_FRONT = "/home/aaron/animation/thulans-production/assets/art/varek_v35_front34_frame_001.png"

bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)
scene = bpy.context.scene

scene.render.engine = 'CYCLES'
scene.cycles.samples = 64
scene.cycles.use_denoising = True
scene.render.resolution_x = 960
scene.render.resolution_y = 1280
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

# 1. Close-up Portrait
cam_head = bpy.data.objects.get("V35_Cam_Head_Portrait")
if not cam_head:
    cam_data = bpy.data.cameras.new("V35_Cam_Head_Portrait")
    cam_head = bpy.data.objects.new("V35_Cam_Head_Portrait", cam_data)
    scene.collection.objects.link(cam_head)
    cam_head.location = (0.75, -1.10, 2.05)
    dir_v = Vector((0.0, 0.0, 2.02)) - cam_head.location
    cam_head.rotation_euler = dir_v.to_track_quat('-Z', 'Y').to_euler()
    cam_data.lens = 85.0

scene.camera = cam_head
scene.render.filepath = RENDER_HEAD
print(f"[render] Rendering portrait to {RENDER_HEAD}...")
bpy.ops.render.render(write_still=True)
print(f"[render] Saved {RENDER_HEAD}")

# 2. Full Front 3/4
cam_front = bpy.data.objects.get("V32_Cam_Front34")
if cam_front:
    scene.camera = cam_front
    scene.render.filepath = RENDER_FRONT
    print(f"[render] Rendering front view to {RENDER_FRONT}...")
    bpy.ops.render.render(write_still=True)
    print(f"[render] Saved {RENDER_FRONT}")

print("[render] All renders completed successfully!")
