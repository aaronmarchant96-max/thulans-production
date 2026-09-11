import bpy
from pathlib import Path
R = Path('/home/aaron/animation/thulans-production')
for label, fp in [('V14', R/'blender/candidates/varek-carry-v14.blend'), ('V15', R/'blender/candidates/varek-carry-v15.blend')]:
    bpy.ops.wm.open_mainfile(filepath=str(fp))
    r = bpy.data.objects['Varek simple articulation']
    r.data.pose_position = 'REST'
    bpy.context.view_layer.update()
    o = bpy.data.objects['Pelvic cradle']
    print(label, 'verts', len(o.data.vertices), 'faces', len(o.data.polygons), 'mods', [m.type for m in o.modifiers])
    vs = [v.co for v in o.data.vertices if v.co.y < -0.05 and v.co.x > 0.07]
    if vs:
        print(label, 'L-pocket-region bounds',
              [min(v.x for v in vs), max(v.x for v in vs),
               min(v.y for v in vs), max(v.y for v in vs),
               min(v.z for v in vs), max(v.z for v in vs)])
