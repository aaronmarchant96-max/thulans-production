import bpy
from pathlib import Path
R = Path('/home/aaron/animation/thulans-production')
fp = R/'blender/candidates/varek-carry-v13-transfer.blend'
bpy.ops.wm.open_mainfile(filepath=str(fp))
r = bpy.data.objects['Varek simple articulation']
r.data.pose_position = 'REST'
bpy.context.view_layer.update()
o = bpy.data.objects['Pelvic cradle']
print('V13-transfer verts', len(o.data.vertices), 'faces', len(o.data.polygons), 'mods', [m.type for m in o.modifiers])
vs = [v.co for v in o.data.vertices if v.co.y < -0.05 and v.co.x > 0.07]
if vs:
    print('V13 L-pocket-region bounds',
          [min(v.x for v in vs), max(v.x for v in vs),
           min(v.y for v in vs), max(v.y for v in vs),
           min(v.z for v in vs), max(v.z for v in vs)])
