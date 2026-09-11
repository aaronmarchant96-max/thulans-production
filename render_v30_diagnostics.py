import bpy
import math

source_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v30-canonical.blend'
bpy.ops.wm.open_mainfile(filepath=source_blend)

# 1. Render Default Camera (Front 3/4)
bpy.context.scene.render.filepath = '/home/aaron/animation/thulans-production/assets/art/varek_v30_front34_frame_001.png'
bpy.ops.render.render(write_still=True)

# 2. Setup Side Profile Camera (looking directly from +X side)
side_cam_data = bpy.data.cameras.new(name="Side_Profile_Camera")
side_cam_obj = bpy.data.objects.new("Side_Profile_Camera", side_cam_data)
bpy.context.scene.collection.objects.link(side_cam_obj)
side_cam_obj.location = (4.5, 0.0, 1.4)
side_cam_obj.rotation_euler = (math.radians(90), 0, math.radians(90))
side_cam_data.lens = 65.0

bpy.context.scene.camera = side_cam_obj
bpy.context.scene.render.filepath = '/home/aaron/animation/thulans-production/assets/art/varek_v30_side_profile_frame_001.png'
bpy.ops.render.render(write_still=True)

print("Finished rendering V30 front 3/4 and side profile diagnostic frames!")
