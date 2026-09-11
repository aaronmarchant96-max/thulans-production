import bpy
import math
from pathlib import Path

blend_path = '/home/aaron/animation/thulans-production/blender/candidates/varek-v40-osint-juggernaut.blend'
out_dir = Path('/home/aaron/.gemini/antigravity/brain/c8d29359-41cb-4a73-aa95-01cade4cb5b7')

bpy.ops.wm.open_mainfile(filepath=blend_path)
scene = bpy.context.scene

# Configure Workbench render for pure MatCap geometry clarity
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'MATCAP'
scene.display.shading.studio_light = 'metal_carpaint.exr'
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = 'BOTH'
scene.display.shading.cavity_ridge_factor = 1.5
scene.display.shading.cavity_valley_factor = 2.0

scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.image_settings.file_format = 'PNG'

cam_data = bpy.data.cameras.new('Showcase_Cam')
cam_obj = bpy.data.objects.new('Showcase_Cam', cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

views = [
    ('v40_fullbody_front_workbench.png', (0.0, -4.6, 1.25), (math.radians(90), 0, 0)),
    ('v40_fullbody_threequarter_workbench.png', (3.4, -3.4, 1.35), (math.radians(80), 0, math.radians(45))),
    ('v40_fullbody_side_workbench.png', (4.6, 0.0, 1.25), (math.radians(90), 0, math.radians(90))),
    ('v40_closeup_upper_workbench.png', (1.4, -1.8, 1.75), (math.radians(82), 0, math.radians(38))),
    ('v40_closeup_drill_workbench.png', (-1.8, -1.2, 1.05), (math.radians(85), 0, math.radians(-55))),
    ('v40_closeup_shears_workbench.png', (1.8, -1.2, 1.05), (math.radians(85), 0, math.radians(55)))
]

for filename, loc, rot in views:
    cam_obj.location = loc
    cam_obj.rotation_euler = rot
    scene.render.filepath = str(out_dir / filename)
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {scene.render.filepath}")

