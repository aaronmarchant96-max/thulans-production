import bpy
from mathutils import Vector

bpy.ops.wm.open_mainfile(filepath='/home/aaron/animation/thulans-production/blender/candidates/varek-v37-helmet-final.blend')

pilot_objs = bpy.data.collections.get('01_PILOT_ENVELOPE').objects
for o in pilot_objs:
    verts = [o.matrix_world @ v.co for v in o.data.vertices]
    min_x = min(v.x for v in verts)
    max_x = max(v.x for v in verts)
    min_y = min(v.y for v in verts)
    max_y = max(v.y for v in verts)
    min_z = min(v.z for v in verts)
    max_z = max(v.z for v in verts)
    print(f'{o.name}: verts={len(verts)}, X:[{min_x:.3f}, {max_x:.3f}], Y:[{min_y:.3f}, {max_y:.3f}], Z:[{min_z:.3f}, {max_z:.3f}]')
