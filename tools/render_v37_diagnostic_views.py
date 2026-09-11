import bpy
import math
from mathutils import Vector
from pathlib import Path

R = Path('/home/aaron/animation/thulans-production')
TARGET_BLEND = R / 'blender/candidates/varek-v37-helmet-final.blend'
OUT_DIR = R / 'evidence/varek-v37-helmet-final/views'
OUT_DIR.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=str(TARGET_BLEND))
s = bpy.context.scene

s.frame_set(1)
s.render.engine = 'BLENDER_WORKBENCH'
s.display.shading.light = 'MATCAP'
s.display.shading.studio_light = 'check_normal+y.exr'
s.render.image_settings.file_format = 'PNG'
s.render.resolution_percentage = 100

cam = s.objects.get('Camera')
if cam is None:
    cam_data = bpy.data.cameras.new('Camera')
    cam = bpy.data.objects.new('Camera', cam_data)
    s.collection.objects.link(cam)
s.camera = cam

views = [
    {
        'name': 'v37_front_threequarter_portrait.png',
        'res_x': 1080, 'res_y': 1350,
        'loc': Vector((1.2, -2.4, 2.05)),
        'target': Vector((0.0, 0.0, 1.85)),
        'lens': 65.0
    },
    {
        'name': 'v37_strict_side_profile.png',
        'res_x': 1080, 'res_y': 1350,
        'loc': Vector((2.6, 0.0, 1.85)),
        'target': Vector((0.0, 0.0, 1.85)),
        'lens': 65.0
    },
    {
        'name': 'v37_middistance_fullbody.png',
        'res_x': 1080, 'res_y': 1350,
        'loc': Vector((2.4, -4.6, 1.8)),
        'target': Vector((0.0, 0.0, 1.1)),
        'lens': 50.0
    }
]

for v in views:
    s.render.resolution_x = v['res_x']
    s.render.resolution_y = v['res_y']
    cam.location = v['loc']
    cam.rotation_euler = (v['target'] - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = v['lens']
    out_path = OUT_DIR / v['name']
    s.render.filepath = str(out_path)
    bpy.ops.render.render(write_still=True)
    print(f'Rendered {v["name"]} to {out_path}')
