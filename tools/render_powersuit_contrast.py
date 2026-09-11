import bpy
from mathutils import Vector
from pathlib import Path

bpy.ops.wm.open_mainfile(filepath='/home/aaron/animation/thulans-production/blender/candidates/varek-v37-helmet-final.blend')

# Run lighting setup
exec(open('/home/aaron/animation/thulans-production/tools/setup_powersuit_lighting.py').read())

s = bpy.context.scene
s.render.resolution_x = 1080
s.render.resolution_y = 1350
s.render.resolution_percentage = 100
s.render.image_settings.file_format = 'PNG'

cam = s.objects.get('Camera')
if cam is None:
    cam_data = bpy.data.cameras.new('Camera')
    cam = bpy.data.objects.new('Camera', cam_data)
    s.collection.objects.link(cam)
s.camera = cam

# View 1: 3/4 Full Body Power Suit Read
cam.location = Vector((2.2, -3.8, 1.8))
target = Vector((0.0, 0.0, 1.1))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 50.0

out_path = '/home/aaron/animation/thulans-production/evidence/varek-v37-helmet-final/views/powersuit_human_contrast_render.png'
s.render.filepath = out_path
bpy.ops.render.render(write_still=True)
print(f'Rendered full body powersuit view to {out_path}')
