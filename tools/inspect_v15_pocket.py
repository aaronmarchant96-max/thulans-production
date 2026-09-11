import bpy
from pathlib import Path
R = Path('/home/aaron/animation/thulans-production')
fp = R/'blender/candidates/varek-carry-v15.blend'
bpy.ops.wm.open_mainfile(filepath=str(fp))
r = bpy.data.objects['Varek simple articulation']
r.data.pose_position = 'REST'
bpy.context.view_layer.update()
o = bpy.data.objects['Pelvic cradle']
# box region for L side pocket
inside = [v.co for v in o.data.vertices
          if 0.07 < v.co.x < 0.42 and -0.19 < v.co.y < 0.17 and 0.89 < v.co.z < 1.08]
print('verts inside L pocket column', len(inside))
if inside:
    print('x', min(v.x for v in inside), max(v.x for v in inside))
    print('y', min(v.y for v in inside), max(v.y for v in inside))
    print('z', min(v.z for v in inside), max(v.z for v in inside))
# all verts in medial-lower region
region = [v.co for v in o.data.vertices if v.co.x > 0.06 and v.co.y < -0.05]
print('region verts', len(region), 'z range', (min(v.z for v in region), max(v.z for v in region)) if region else None)
