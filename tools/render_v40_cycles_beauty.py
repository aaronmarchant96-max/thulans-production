import bpy
import math
from pathlib import Path

blend_path = '/home/aaron/animation/thulans-production/blender/candidates/varek-v40-osint-juggernaut.blend'
out_dir = Path('/home/aaron/.gemini/antigravity/brain/c8d29359-41cb-4a73-aa95-01cade4cb5b7')

bpy.ops.wm.open_mainfile(filepath=blend_path)
scene = bpy.context.scene

# Set Cycles Render
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.preview_samples = 32
scene.render.resolution_x = 1280
scene.render.resolution_y = 1920
scene.render.image_settings.file_format = 'PNG'

# Three-point studio lighting setup
world = scene.world or bpy.data.worlds.new("Studio_World")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs['Color'].default_value = (0.05, 0.05, 0.06, 1.0)
    bg.inputs['Strength'].default_value = 0.6

# Key Light
key_data = bpy.data.lights.new(name="Key_Light", type='AREA')
key_data.energy = 800.0
key_data.size = 2.0
key_obj = bpy.data.objects.new(name="Key_Light", object_data=key_data)
scene.collection.objects.link(key_obj)
key_obj.location = (2.5, -3.5, 3.0)
key_obj.rotation_euler = (math.radians(55), 0, math.radians(35))

# Fill Light
fill_data = bpy.data.lights.new(name="Fill_Light", type='AREA')
fill_data.energy = 350.0
fill_data.size = 3.0
fill_obj = bpy.data.objects.new(name="Fill_Light", object_data=fill_data)
scene.collection.objects.link(fill_obj)
fill_obj.location = (-3.0, -2.5, 2.2)
fill_obj.rotation_euler = (math.radians(60), 0, math.radians(-50))

# Rim / Kicker Light
rim_data = bpy.data.lights.new(name="Rim_Light", type='SPOT')
rim_data.energy = 1200.0
rim_data.spot_size = math.radians(65)
rim_obj = bpy.data.objects.new(name="Rim_Light", object_data=rim_data)
scene.collection.objects.link(rim_obj)
rim_obj.location = (0.0, 3.2, 3.2)
rim_obj.rotation_euler = (math.radians(-50), 0, math.radians(180))

# Camera
cam_data = bpy.data.cameras.new('Beauty_Cam')
cam_data.lens = 70.0
cam_obj = bpy.data.objects.new('Beauty_Cam', cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

# 1. Full Body Front Beauty
cam_obj.location = (0.0, -4.6, 1.25)
cam_obj.rotation_euler = (math.radians(90), 0, 0)
scene.render.filepath = str(out_dir / 'v40_cycles_beauty_front.png')
bpy.ops.render.render(write_still=True)
print(f"Rendered: {scene.render.filepath}")

# 2. Three-Quarter Hero Beauty
cam_obj.location = (3.4, -3.4, 1.35)
cam_obj.rotation_euler = (math.radians(80), 0, math.radians(45))
scene.render.filepath = str(out_dir / 'v40_cycles_beauty_threequarter.png')
bpy.ops.render.render(write_still=True)
print(f"Rendered: {scene.render.filepath}")

