import bpy
import math
from mathutils import Vector, Euler
from pathlib import Path

R = Path('/home/aaron/animation/thulans-production')
fp = R / 'blender/candidates/varek-carry-v15.blend'
frames = [1, 46, 49, 88, 91]

bpy.ops.wm.open_mainfile(filepath=str(fp))
s = bpy.context.scene
s.render.engine = 'BLENDER_WORKBENCH'
s.render.resolution_x = 1080
s.render.resolution_y = 1920
s.render.resolution_percentage = 100
s.render.image_settings.file_format = 'PNG'

# lights
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

# Full-character camera back-left
# For L-hip worst frames (88-91) a +x side view is more informative.
# We'll render two angles per frame group? Keep it simple: use the existing
# diagnostic camera that shows both hips from back-left.
cam.location = Vector((-2.8, -5.0, 1.6))
target = Vector((0.0, 0.0, 1.0))
direction = target - cam.location
rot = direction.to_track_quat('-Z', 'Y')
cam.rotation_euler = rot.to_euler()
cam.data.lens = 50
s.camera = cam

for frame in frames:
    s.frame_set(frame)
    bpy.context.view_layer.update()
    out = R / f'renders/varek-carry-v15-frame{frame:03d}.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    s.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)
    print('RENDER_SAVED', frame, out)

# Also render a hip close-up from the +x side to show the notch at frame 90
s.frame_set(90)
bpy.context.view_layer.update()
cam.location = Vector((3.0, -2.5, 1.1))
target = Vector((0.0, -0.1, 0.98))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 85
out = R / 'renders/varek-carry-v15-hip-notch-L.png'
s.render.filepath = str(out)
bpy.ops.render.render(write_still=True)
print('RENDER_SAVED', 'hip-notch-L', out)
