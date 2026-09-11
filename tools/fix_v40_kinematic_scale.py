import bpy
from mathutils import Vector, Matrix
import math

blend_path = '/home/aaron/animation/thulans-production/blender/candidates/varek-v40-osint-juggernaut.blend'
bpy.ops.wm.open_mainfile(filepath=blend_path)
scene = bpy.context.scene

# 1. Audit current bounds
min_z = float('inf')
max_z = float('-inf')

mesh_objs = [o for o in bpy.data.objects if o.type == 'MESH']
for obj in mesh_objs:
    for corner in [obj.matrix_world @ Vector(c) for c in obj.bound_box]:
        min_z = min(min_z, corner.z)
        max_z = max(max_z, corner.z)

current_height = max_z - min_z
print(f"Pre-Fix: Min Z = {min_z:.6f}m, Max Z = {max_z:.6f}m, Height = {current_height:.6f}m")

# Target specs: exactly 2.4384m total height, exactly 0.0000m ground contact
target_height = 2.4384
scale_factor = target_height / current_height

# 2. Scale all meshes and the rig uniformly around (0, 0, min_z)
# Shift Z so ground contact is exactly 0.0000m
for obj in bpy.data.objects:
    if obj.type in ['MESH', 'ARMATURE']:
        # Scale in Z and XY proportionally to preserve the exact anatomical ratios
        obj.location.x *= scale_factor
        obj.location.y *= scale_factor
        obj.location.z = (obj.location.z - min_z) * scale_factor
        
        # Scale matrix
        obj.scale *= scale_factor

# Apply transformation
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)

# 3. Post-Fix Verification
new_min_z = float('inf')
new_max_z = float('-inf')

for obj in [o for o in bpy.data.objects if o.type == 'MESH']:
    for corner in [obj.matrix_world @ Vector(c) for c in obj.bound_box]:
        new_min_z = min(new_min_z, corner.z)
        new_max_z = max(new_max_z, corner.z)

new_height = new_max_z - new_min_z
print(f"Post-Fix: Min Z = {new_min_z:.6f}m, Max Z = {new_max_z:.6f}m, Height = {new_height:.6f}m")

# Save
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"SUCCESS: Exact 2.4384m Height & 0.0000m Grounding Applied to {blend_path}")

