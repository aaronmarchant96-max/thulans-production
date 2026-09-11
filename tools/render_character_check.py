import bpy
import math
from mathutils import Vector, Euler
from pathlib import Path

R = Path('/home/aaron/animation/thulans-production')
fp = R / 'blender/candidates/varek-carry-v14.blend'
out = R / 'renders/varek_character_check.png'

bpy.ops.wm.open_mainfile(filepath=str(fp))
s = bpy.context.scene
s.frame_set(1)
bpy.context.view_layer.update()

s.render.engine = 'BLENDER_WORKBENCH'
s.render.resolution_x = 1080
s.render.resolution_y = 1920
s.render.resolution_percentage = 100
s.render.image_settings.file_format = 'PNG'
s.render.filepath = str(out)

# Add a simple three-light setup so the silhouette reads
if 'Key' not in bpy.data.objects:
    key = bpy.data.lights.new('Key', 'SUN')
    key_obj = bpy.data.objects.new('Key', key)
    s.collection.objects.link(key_obj)
    key_obj.location = Vector((-3, -4, 5))
    key_obj.rotation_euler = Euler((0.9, 0.0, -0.6), 'XYZ')
    key.energy = 4.0
if 'Fill' not in bpy.data.objects:
    fill = bpy.data.lights.new('Fill', 'SUN')
    fill_obj = bpy.data.objects.new('Fill', fill)
    s.collection.objects.link(fill_obj)
    fill_obj.location = Vector((3, -2, 4))
    fill_obj.rotation_euler = Euler((1.0, 0.0, 0.8), 'XYZ')
    fill.energy = 2.0

rig = bpy.data.objects.get('Varek simple articulation')
cam = bpy.data.objects.get('Camera')
if cam is None:
    cam_data = bpy.data.cameras.new('Camera')
    cam = bpy.data.objects.new('Camera', cam_data)
    s.collection.objects.link(cam)

# Frame full character: ~2.44 m tall. Camera back-left, looking at mid-torso.
cam.location = Vector((-2.8, -5.0, 1.6))
target = Vector((0.0, 0.0, 1.0))
direction = target - cam.location
rot = direction.to_track_quat('-Z', 'Y')
cam.rotation_euler = rot.to_euler()
cam.data.lens = 50

s.camera = cam

bpy.ops.render.render(write_still=True)
print('RENDER_SAVED', out, flush=True)
