import bpy
import math
from mathutils import Euler, Quaternion, Vector

# Load candidate varek-carry-v15
arm_obj = bpy.data.objects.get('Varek simple articulation')
if not arm_obj:
    raise ValueError("Armature 'Varek simple articulation' not found!")

# Set scene timeline
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 48
scene.frame_current = 1

# Ensure pose mode / clean animation data if any
if not arm_obj.animation_data:
    arm_obj.animation_data_create()

action_name = "Varek_Heavy_Walk_Cycle_48F"
action = bpy.data.actions.get(action_name)
if not action:
    action = bpy.data.actions.new(name=action_name)
arm_obj.animation_data.action = action

pbones = arm_obj.pose.bones

# Set quaternion rotation mode on all pose bones
for pb in pbones:
    pb.rotation_mode = 'QUATERNION'

# Helper to set Euler (deg) -> Quaternion
def set_rot(pb, x_deg, y_deg, z_deg, frame):
    euler = Euler((math.radians(x_deg), math.radians(y_deg), math.radians(z_deg)), 'XYZ')
    pb.rotation_quaternion = euler.to_quaternion()
    pb.keyframe_insert(data_path="rotation_quaternion", frame=frame)

def set_loc(pb, loc_tuple, frame):
    pb.location = Vector(loc_tuple)
    pb.keyframe_insert(data_path="location", frame=frame)

# Baseline root location: (0, 0, 0.3576)
root_base_z = 0.3576

# 48-frame heavy walk cycle (1 to 49 loop)
keyframes_data = {
    # Frame 1: L Contact / R Push-off
    1: {
        'root_loc': (0.0, 0.0, root_base_z - 0.015),
        'pelvis_rot': (3.0, 4.0, -2.0),
        'spine_rot': (-2.0, -3.0, 1.0),
        'head_rot': (2.0, -1.0, 0.0),
        'thigh_L': (18.0, 0.0, 0.0),
        'shin_L': (-6.0, 0.0, 0.0),
        'foot_L': (12.0, 0.0, 0.0),
        'thigh_R': (-16.0, 0.0, 0.0),
        'shin_R': (-26.0, 0.0, 0.0),
        'foot_R': (-18.0, 0.0, 0.0),
        'upper_arm_L': (-12.0, 0.0, -5.0),
        'forearm_L': (10.0, 0.0, 0.0),
    },
    # Frame 7: L Down / Impact
    7: {
        'root_loc': (0.0, 0.0, root_base_z - 0.038),
        'pelvis_rot': (1.0, 2.0, -3.0),
        'spine_rot': (0.0, -1.5, 2.0),
        'head_rot': (1.0, -0.5, 0.0),
        'thigh_L': (12.0, 0.0, 0.0),
        'shin_L': (-18.0, 0.0, 0.0),
        'foot_L': (0.0, 0.0, 0.0),
        'thigh_R': (-10.0, 0.0, 0.0),
        'shin_R': (-45.0, 0.0, 0.0),
        'foot_R': (10.0, 0.0, 0.0),
        'upper_arm_L': (-6.0, 0.0, -5.0),
        'forearm_L': (15.0, 0.0, 0.0),
    },
    # Frame 13: L Mid-stance / Passing
    13: {
        'root_loc': (0.0, 0.0, root_base_z + 0.012),
        'pelvis_rot': (0.0, 0.0, 1.0),
        'spine_rot': (0.0, 0.0, -1.0),
        'head_rot': (0.0, 0.0, 0.0),
        'thigh_L': (0.0, 0.0, 0.0),
        'shin_L': (-3.0, 0.0, 0.0),
        'foot_L': (0.0, 0.0, 0.0),
        'thigh_R': (10.0, 0.0, 0.0),
        'shin_R': (-55.0, 0.0, 0.0),
        'foot_R': (15.0, 0.0, 0.0),
        'upper_arm_L': (2.0, 0.0, -5.0),
        'forearm_L': (20.0, 0.0, 0.0),
    },
    # Frame 19: L Push / R Reach
    19: {
        'root_loc': (0.0, 0.0, root_base_z - 0.010),
        'pelvis_rot': (2.0, -2.0, 2.0),
        'spine_rot': (-1.0, 1.5, -1.5),
        'head_rot': (1.0, 0.5, 0.0),
        'thigh_L': (-10.0, 0.0, 0.0),
        'shin_L': (-15.0, 0.0, 0.0),
        'foot_L': (-10.0, 0.0, 0.0),
        'thigh_R': (16.0, 0.0, 0.0),
        'shin_R': (-12.0, 0.0, 0.0),
        'foot_R': (10.0, 0.0, 0.0),
        'upper_arm_L': (10.0, 0.0, -5.0),
        'forearm_L': (25.0, 0.0, 0.0),
    },
    # Frame 25: Right Heel Contact / Left Push-off (Mirror of Frame 1)
    25: {
        'root_loc': (0.0, 0.0, root_base_z - 0.015),
        'pelvis_rot': (3.0, -4.0, 2.0),
        'spine_rot': (-2.0, 3.0, -1.0),
        'head_rot': (2.0, 1.0, 0.0),
        'thigh_L': (-16.0, 0.0, 0.0),
        'shin_L': (-26.0, 0.0, 0.0),
        'foot_L': (-18.0, 0.0, 0.0),
        'thigh_R': (18.0, 0.0, 0.0),
        'shin_R': (-6.0, 0.0, 0.0),
        'foot_R': (12.0, 0.0, 0.0),
        'upper_arm_L': (16.0, 0.0, -5.0),
        'forearm_L': (28.0, 0.0, 0.0),
    },
    # Frame 31: R Down / Impact (Mirror of Frame 7)
    31: {
        'root_loc': (0.0, 0.0, root_base_z - 0.038),
        'pelvis_rot': (1.0, -2.0, 3.0),
        'spine_rot': (0.0, 1.5, -2.0),
        'head_rot': (1.0, 0.5, 0.0),
        'thigh_L': (-10.0, 0.0, 0.0),
        'shin_L': (-45.0, 0.0, 0.0),
        'foot_L': (10.0, 0.0, 0.0),
        'thigh_R': (12.0, 0.0, 0.0),
        'shin_R': (-18.0, 0.0, 0.0),
        'foot_R': (0.0, 0.0, 0.0),
        'upper_arm_L': (10.0, 0.0, -5.0),
        'forearm_L': (22.0, 0.0, 0.0),
    },
    # Frame 37: R Mid-stance / Passing (Mirror of Frame 13)
    37: {
        'root_loc': (0.0, 0.0, root_base_z + 0.012),
        'pelvis_rot': (0.0, 0.0, -1.0),
        'spine_rot': (0.0, 0.0, 1.0),
        'head_rot': (0.0, 0.0, 0.0),
        'thigh_L': (10.0, 0.0, 0.0),
        'shin_L': (-55.0, 0.0, 0.0),
        'foot_L': (15.0, 0.0, 0.0),
        'thigh_R': (0.0, 0.0, 0.0),
        'shin_R': (-3.0, 0.0, 0.0),
        'foot_R': (0.0, 0.0, 0.0),
        'upper_arm_L': (0.0, 0.0, -5.0),
        'forearm_L': (16.0, 0.0, 0.0),
    },
    # Frame 43: R Push / L Reach (Mirror of Frame 19)
    43: {
        'root_loc': (0.0, 0.0, root_base_z - 0.010),
        'pelvis_rot': (2.0, 2.0, -2.0),
        'spine_rot': (-1.0, -1.5, 1.5),
        'head_rot': (1.0, -0.5, 0.0),
        'thigh_L': (16.0, 0.0, 0.0),
        'shin_L': (-12.0, 0.0, 0.0),
        'foot_L': (10.0, 0.0, 0.0),
        'thigh_R': (-10.0, 0.0, 0.0),
        'shin_R': (-15.0, 0.0, 0.0),
        'foot_R': (-10.0, 0.0, 0.0),
        'upper_arm_L': (-8.0, 0.0, -5.0),
        'forearm_L': (12.0, 0.0, 0.0),
    },
    # Frame 49: Exact loop of Frame 1
    49: {
        'root_loc': (0.0, 0.0, root_base_z - 0.015),
        'pelvis_rot': (3.0, 4.0, -2.0),
        'spine_rot': (-2.0, -3.0, 1.0),
        'head_rot': (2.0, -1.0, 0.0),
        'thigh_L': (18.0, 0.0, 0.0),
        'shin_L': (-6.0, 0.0, 0.0),
        'foot_L': (12.0, 0.0, 0.0),
        'thigh_R': (-16.0, 0.0, 0.0),
        'shin_R': (-26.0, 0.0, 0.0),
        'foot_R': (-18.0, 0.0, 0.0),
        'upper_arm_L': (-12.0, 0.0, -5.0),
        'forearm_L': (10.0, 0.0, 0.0),
    }
}

for frame, d in keyframes_data.items():
    set_loc(pbones['root'], d['root_loc'], frame)
    set_rot(pbones['pelvis'], *d['pelvis_rot'], frame)
    set_rot(pbones['spine'], *d['spine_rot'], frame)
    set_rot(pbones['head'], *d['head_rot'], frame)
    set_rot(pbones['thigh.L'], *d['thigh_L'], frame)
    set_rot(pbones['shin.L'], *d['shin_L'], frame)
    set_rot(pbones['foot.L'], *d['foot_L'], frame)
    set_rot(pbones['thigh.R'], *d['thigh_R'], frame)
    set_rot(pbones['shin.R'], *d['shin_R'], frame)
    set_rot(pbones['foot.R'], *d['foot_R'], frame)
    set_rot(pbones['upper_arm.L'], *d['upper_arm_L'], frame)
    set_rot(pbones['forearm.L'], *d['forearm_L'], frame)

# Set F-Curve interpolation to BEZIER
fcurves_list = []
if hasattr(action, 'fcurves'):
    fcurves_list.extend(action.fcurves)
elif hasattr(action, 'layers'):
    for layer in action.layers:
        for strip in layer.strips:
            for cbag in strip.channelbags:
                fcurves_list.extend(cbag.fcurves)

for fcurve in fcurves_list:
    for kf in fcurve.keyframe_points:
        kf.interpolation = 'BEZIER'
        kf.handle_left_type = 'AUTO_CLAMPED'
        kf.handle_right_type = 'AUTO_CLAMPED'

# Save as varek-walk-v17.blend
save_path = '/home/aaron/animation/thulans-production/blender/candidates/varek-walk-v17.blend'
bpy.ops.wm.save_as_mainfile(filepath=save_path)
print(f"Successfully generated walk cycle and saved to {save_path}")
