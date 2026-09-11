import bpy
import math
from mathutils import Vector
from pathlib import Path

R = Path('/home/aaron/animation/thulans-production')
TARGET_BLEND = R / 'blender/candidates/varek-v37-helmet-final.blend'
OUT_PATH = R / 'evidence/varek-v37-helmet-final/views/diagnostic_pilot_vs_chassis.png'
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=str(TARGET_BLEND))
s = bpy.context.scene

# Ensure Pilot collection is visible and given high contrast material
pilot_col = bpy.data.collections.get('01_PILOT_ENVELOPE')
mat_human = bpy.data.materials.new('Human_Suit_Orange')
mat_human.use_nodes = True
bsdf = mat_human.node_tree.nodes.get('Principled BSDF')
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.8, 0.3, 0.05, 1.0) # High-vis hazard orange
    bsdf.inputs['Roughness'].default_value = 0.6

for o in pilot_col.objects:
    o.hide_render = False
    o.hide_viewport = False
    if o.data and hasattr(o.data, 'materials'):
        if o.data.materials:
            o.data.materials[0] = mat_human
        else:
            o.data.materials.append(mat_human)

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

cam.location = Vector((2.2, -3.8, 1.8))
target = Vector((0.0, 0.0, 1.3))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 50.0

s.render.filepath = str(OUT_PATH)
bpy.ops.render.render(write_still=True)
print(f'Rendered pilot diagnostic to {OUT_PATH}')
