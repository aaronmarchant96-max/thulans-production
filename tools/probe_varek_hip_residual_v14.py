"""Read-only localization of the residual V14 intersections."""
import json
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/home/aaron/animation/thulans-production')
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/candidates/varek-carry-v14.blend'))
s=bpy.context.scene;r=bpy.data.objects['Varek simple articulation']
def mesh(name):
    o=bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get());m=o.to_mesh()
    v=[o.matrix_world@p.co for p in m.vertices];f=[list(p.vertices) for p in m.polygons]
    o.to_mesh_clear();return v,f
rows=[]
cache={}
s.frame_set(1);bpy.context.view_layer.update()
for name in ['Thigh guard L','Thigh guard R']:
    obj=bpy.data.objects[name];v,f=mesh(name)
    inv=(r.matrix_world@r.pose.bones[obj['rigid_driver_bone']].matrix).inverted()
    cache[name]=[inv@p for p in v]
    print('MODIFIERS',name,[(m.name,m.type) for m in obj.modifiers],flush=True)
for frame in [1,24,60,100,144,180,216,240]:
    s.frame_set(frame);bpy.context.view_layer.update()
    v,f=mesh('Pelvic cradle');tree=BVHTree.FromPolygons(v,f)
    to_rest=r.matrix_world@r.data.bones['pelvis'].matrix_local@(r.matrix_world@r.pose.bones['pelvis'].matrix).inverted()
    for name in ['Thigh guard L','Thigh guard R','Donor thigh L','Donor thigh R']:
        vv,ff=mesh(name);hits=tree.overlap(BVHTree.FromPolygons(vv,ff))
        if frame==60 and name=='Thigh guard R':
            matrix=r.matrix_world@r.pose.bones[bpy.data.objects[name]['rigid_driver_bone']].matrix
            print('CACHE_ERROR',max((p-matrix@q).length for p,q in zip(vv,cache[name])),flush=True)
            print('HIT_VERTS',json.dumps([{'body':[list(to_rest@v[i]) for i in f[a]],'guard':[list(to_rest@vv[i]) for i in ff[b]]} for a,b in hits]),flush=True)
        centers=[to_rest@(sum((v[i] for i in f[a]),Vector())/len(f[a])) for a,b in hits]
        rows.append({'frame':frame,'part':name,'hits':len(hits),
                     'pelvis_face_centers_rest':sorted(set(tuple(round(c,6) for c in p) for p in centers))})
print('RESIDUAL',json.dumps(rows),flush=True)
