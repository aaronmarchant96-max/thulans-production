import bpy
from mathutils import Vector

blend_path = '/home/aaron/animation/thulans-production/blender/candidates/varek-v40-osint-juggernaut.blend'
bpy.ops.wm.open_mainfile(filepath=blend_path)

arm = bpy.data.objects.get('Varek_Original_Rig') or bpy.data.objects.get('Armature')
print(f"Kinematic rig found: {arm.name if arm else 'NONE'}")

min_z = float('inf')
max_z = float('-inf')

for obj in bpy.data.objects:
    if obj.type == 'MESH':
        for corner in [obj.matrix_world @ Vector(c) for c in obj.bound_box]:
            min_z = min(min_z, corner.z)
            max_z = max(max_z, corner.z)

print(f"Total Height: {max_z - min_z:.4f} m (Target: ~2.4384m)")
print(f"Ground Contact Z: {min_z:.4f} m (Target: 0.0000m)")

