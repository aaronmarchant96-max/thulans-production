import bpy
import math
from mathutils import Vector, Euler
from pathlib import Path

R = Path('/home/aaron/animation/thulans-production')
fp = R / 'blender/candidates/varek-carry-v14.blend'
out = R / 'renders/varek_character_portrait.png'

bpy.ops.wm.open_mainfile(filepath=str(fp))
s = bpy.context.scene
s.frame_set(1)
bpy.context.view_layer.update()

s.render.engine = 'BLENDER_WORKBENCH'
s.render.resolution_x = 1080
s.render.resolution_y = 1350
s.render.resolution_percentage = 100
s.render.image_settings.file_format = 'PNG'
s.render.filepath = str(out)

# Lighter world so the silhouette reads
if s.world is None:
    s.world = bpy.data.worlds.new('World')
s.world.color = (0.18, 0.18, 0.20)

# Three-point lighting
for name, loc, rot, energy in [
    ('Key', (-3.5, -4.5, 4.0), (0.85, 0.0, -0.65), 6.0),
    ('Fill', (3.5, -3.0, 3.5), (0.95, 0.0, 0.75), 3.0),
    ('Rim', (0.5, 4.0, 3.0), (2.2, 0.0, 0.1), 5.0),
]:
    if name not in bpy.data.objects:
        lt = bpy.data.lights.new(name, 'SUN')
        lt.energy = energy
        obj = bpy.data.objects.new(name, lt)
        s.collection.objects.link(obj)
        obj.location = Vector(loc)
        obj.rotation_euler = Euler(rot, 'XYZ')

cam = bpy.data.objects.get('Camera')
if cam is None:
    cam_data = bpy.data.cameras.new('Camera')
    cam = bpy.data.objects.new('Camera', cam_data)
    s.collection.objects.link(cam)

# Chest/head portrait, slightly low angle, heroic but human scale
cam.location = Vector((-1.3, -2.7, 1.9))
target = Vector((0.0, 0.0, 1.95))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 65

s.camera = cam

bpy.ops.render.render(write_still=True)
print('RENDER_SAVED', out, flush=True)
