"""Test whether a big-enough Boolean box clears the thigh-guard contacts on V14."""
import hashlib, json, sys
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

R = Path('/home/aaron/animation/thulans-production')
S = R/'blender/candidates/varek-carry-v14.blend'
E = R/'evidence/varek-carry-v14'
expected = json.loads((E/'measurements.json').read_text())['candidate_sha256']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(S) == expected

bpy.ops.wm.open_mainfile(filepath=str(S))
s = bpy.context.scene
r = bpy.data.objects['Varek simple articulation']
F = json.loads((R/'evidence/varek-simplified-donor-v2/build.json').read_text())['normalization_factor']

names = ['Thigh guard L','Thigh guard R','Donor thigh L','Donor thigh R']
s.frame_set(1); bpy.context.view_layer.update()
cache={}
for name in names:
    o=bpy.data.objects[name]; driver=o['rigid_driver_bone']
    e=o.evaluated_get(bpy.context.evaluated_depsgraph_get()); m=e.to_mesh()
    p=[o.matrix_world @ v.co for v in m.vertices]; f=[list(p.vertices) for p in m.polygons]
    e.to_mesh_clear()
    inv=(r.matrix_world @ r.pose.bones[driver].matrix).inverted()
    cache[name]=(driver,[inv@v for v in p],f)

def cached_world(name):
    driver,p,f=cache[name]; m=r.matrix_world @ r.pose.bones[driver].matrix
    return [m@v for v in p],f

def make_box(bmin,bmax):
    bm=bmesh.new()
    corners=[(bmin.x,bmin.y,bmin.z),(bmax.x,bmin.y,bmin.z),(bmax.x,bmax.y,bmin.z),(bmin.x,bmax.y,bmin.z),
             (bmin.x,bmin.y,bmax.z),(bmax.x,bmin.y,bmax.z),(bmax.x,bmax.y,bmax.z),(bmin.x,bmax.y,bmax.z)]
    vs=[bm.verts.new(Vector(c)) for c in corners]
    for fa in [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]:
        bm.faces.new([vs[i] for i in fa])
    bm.normal_update(); mesh=bpy.data.meshes.new('box'); bm.to_mesh(mesh); bm.free(); return mesh

pelvis=bpy.data.objects['Pelvic cradle']
r.data.pose_position='REST'; bpy.context.view_layer.update()

# big pocket columns L/R
for side,bmin,bmax in [('L',Vector((0.07,-0.19,0.89)),Vector((0.42,0.17,1.30))),
                        ('R',Vector((-0.42,-0.19,0.89)),Vector((-0.07,0.17,1.30)))]:
    mesh=make_box(bmin,bmax); cutter=bpy.data.objects.new('cutter_'+side,mesh); s.collection.objects.link(cutter)
    mod=pelvis.modifiers.new('bool_'+side,'BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cutter
    while list(pelvis.modifiers).index(mod)>0:
        bpy.ops.object.modifier_move_up(modifier=mod.name)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True); bpy.data.meshes.remove(mesh)

r.data.pose_position='POSE'; bpy.context.view_layer.update()
rows=[]
for frame in range(1,241):
    s.frame_set(frame); bpy.context.view_layer.update()
    e=pelvis.evaluated_get(bpy.context.evaluated_depsgraph_get()); m=e.to_mesh()
    pv=[pelvis.matrix_world @ v.co for v in m.vertices]; pf=[list(p.vertices) for p in m.polygons]
    e.to_mesh_clear()
    body=BVHTree.FromPolygons(pv,pf); hits={}
    for name in names:
        p,f=cached_world(name); c=len(body.overlap(BVHTree.FromPolygons(p,f)))
        if c: hits[name]=c
    rows.append({'frame':frame,'hip_surface_crossings':hits})
failures=[r for r in rows if r['hip_surface_crossings']]
print('TEST_RESULT', json.dumps({'checked_frames':len(rows),'crossing_frames':len(failures),'result':'PASS' if not failures else 'FAIL'}))
print('object_counts', json.dumps(dict(__import__('collections').Counter(n for r in failures for n in r['hip_surface_crossings']))))
