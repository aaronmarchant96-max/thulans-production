import bpy
from pathlib import Path
R = Path('/home/aaron/animation/thulans-production')
fp = R/'blender/candidates/varek-carry-v15.blend'
bpy.ops.wm.open_mainfile(filepath=str(fp))
r = bpy.data.objects['Varek simple articulation']
r.data.pose_position = 'REST'
bpy.context.view_layer.update()
o = bpy.data.objects['Pelvic cradle']
vs = [v.co for v in o.data.vertices if 0.06 < v.co.x < 0.12 and -0.17 < v.co.y < -0.04]
print('n verts in region', len(vs))
if vs:
    zs = sorted(set(round(v.z, 4) for v in vs))
    print('z values', zs[:20], '...', zs[-20:])
    print('z min', min(v.z for v in vs), 'z max', max(v.z for v in vs))
