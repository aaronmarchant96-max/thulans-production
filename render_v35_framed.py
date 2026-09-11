import bpy
import math
from mathutils import Vector

BLEND_PATH = "/home/aaron/animation/thulans-production/blender/candidates/varek-v35-canonical.blend"
RENDER_FRONT = "/home/aaron/animation/thulans-production/assets/art/varek_v35_front34_frame_001.png"
RENDER_HEAD = "/home/aaron/animation/thulans-production/assets/art/varek_v35_head_framed_frame_001.png"

bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)
scene = bpy.context.scene

scene.render.engine = 'CYCLES'
scene.cycles.samples = 64
scene.cycles.use_denoising = True
scene.render.resolution_x = 960
scene.render.resolution_y = 1280
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

# 1. Full Body Front 3/4
cam_front = bpy.data.objects.get("V32_Cam_Front34")
if cam_front:
    scene.camera = cam_front
scene.render.filepath = RENDER_FRONT
print(f"[render] Rendering front 3/4 view...")
bpy.ops.render.render(write_still=True)
print(f"[render] Saved {RENDER_FRONT}")

# 2. Correctly Framed Upper Torso & Head Camera
cam_head_data = bpy.data.cameras.new("V35_Cam_Head_Framed")
cam_head_obj = bpy.data.objects.new("V35_Cam_Head_Framed", cam_head_data)
scene.collection.objects.link(cam_head_obj)
# Position in front of the chest looking directly at the helmet
cam_head_obj.location = (0.9, -1.8, 2.05)
dir_v = Vector((0.0, 0.0, 2.02)) - cam_head_obj.location
cam_head_obj.rotation_euler = dir_v.to_track_quat('-Z', 'Y').to_euler()
cam_head_data.lens = 50.0

scene.camera = cam_head_obj
scene.render.filepath = RENDER_HEAD
print(f"[render] Rendering head framed portrait...")
bpy.ops.render.render(write_still=True)
print(f"[render] Saved {RENDER_HEAD}")

print("[render] Both V35 frames finished!")
