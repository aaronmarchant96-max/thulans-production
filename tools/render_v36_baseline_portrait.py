import bpy
from mathutils import Vector, Euler
from pathlib import Path

R = Path('/home/aaron/animation/thulans-production')
fp = R / 'blender/candidates/varek-v36-helmet-pass.blend'
out = R / 'evidence/varek-v36-helmet-pass/baseline_portrait_workbench.png'
out.parent.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=str(fp))
s = bpy.context.scene
s.frame_set(1)
bpy.context.view_layer.update()

s.render.engine = 'BLENDER_WORKBENCH'
s.display.shading.light = 'MATCAP'
s.display.shading.studio_light = 'check_normal+y.exr'
s.render.resolution_x = 1080
s.render.resolution_y = 1350
s.render.resolution_percentage = 100
s.render.image_settings.file_format = 'PNG'
s.render.filepath = str(out)

cam = s.objects.get('Camera')
if cam is None:
    cam_data = bpy.data.cameras.new('Camera')
    cam = bpy.data.objects.new('Camera', cam_data)
    s.collection.objects.link(cam)

cam.location = Vector((1.2, -2.4, 2.05))
target = Vector((0.0, 0.0, 2.00))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 65.0
s.camera = cam

bpy.ops.render.render(write_still=True)
print(f"Rendered baseline portrait to {out}")
