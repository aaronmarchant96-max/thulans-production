import bpy
import math
from mathutils import Vector
from pathlib import Path

R = Path('/home/aaron/animation/thulans-production')
TARGET_BLEND = R / 'blender/candidates/varek-v38-cloth-pass.blend'
OUT_PATH = R / 'evidence/varek-v38-cloth-pass/views/v38_shoulder_cloth_portrait.png'
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=str(TARGET_BLEND))
s = bpy.context.scene

s.frame_set(1)
s.render.engine = 'BLENDER_WORKBENCH'
s.display.shading.light = 'MATCAP'
s.display.shading.studio_light = 'check_normal+y.exr'
s.render.image_settings.file_format = 'PNG'
s.render.resolution_percentage = 100
s.render.resolution_x = 1080
s.render.resolution_y = 1350

cam = s.objects.get('Camera')
if cam is None:
    cam_data = bpy.data.cameras.new('Camera')
    cam = bpy.data.objects.new('Camera', cam_data)
    s.collection.objects.link(cam)
s.camera = cam

cam.location = Vector((-1.6, -2.2, 1.95))
target = Vector((-0.35, -0.05, 1.75))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 65.0

s.render.filepath = str(OUT_PATH)
bpy.ops.render.render(write_still=True)
print(f'Rendered shoulder cloth portrait to {OUT_PATH}')
