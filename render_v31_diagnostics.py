import bpy
import math

source_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v31-canonical.blend'
bpy.ops.wm.open_mainfile(filepath=source_blend)

# 1. Front 3/4 Render
bpy.context.scene.render.filepath = '/home/aaron/animation/thulans-production/assets/art/varek_v31_front34_frame_001.png'
bpy.ops.render.render(write_still=True)

# 2. Side Profile Render
side_cam_data = bpy.data.cameras.new(name="Side_Profile_Camera_V31")
side_cam_obj = bpy.data.objects.new("Side_Profile_Camera_V31", side_cam_data)
bpy.context.scene.collection.objects.link(side_cam_obj)
side_cam_obj.location = (4.2, 0.0, 1.4)
side_cam_obj.rotation_euler = (math.radians(90), 0, math.radians(90))
side_cam_data.lens = 65.0

bpy.context.scene.camera = side_cam_obj
bpy.context.scene.render.filepath = '/home/aaron/animation/thulans-production/assets/art/varek_v31_side_profile_frame_001.png'
bpy.ops.render.render(write_still=True)

print("Rendered V31 frames successfully!")
