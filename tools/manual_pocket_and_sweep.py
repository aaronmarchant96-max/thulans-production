"""Manual face-deletion pocket cut on V14 and sweep test."""
import bpy, bmesh, hashlib, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path

R = Path('/home/aaron/animation/thulans-production')
SRC = R/'blender/candidates/varek-carry-v14.blend'
E = R/'evidence/varek-carry-v14'
expected = json.loads((E/'measurements.json').read_text())['candidate_sha256']
assert hashlib.sha256(SRC.read_bytes()).hexdigest() == expected
F = json.loads((R/'evidence/varek-simplified-donor-v2/build.json').read_text())['normalization_factor']

bpy.ops.wm.open_mainfile(filepath=str(SRC))
s = bpy.context.scene
rig = bpy.data.objects['Varek simple articulation']
pelvis = bpy.data.objects['Pelvic cradle']

# generous pocket columns in pelvis LOCAL coordinates
pockets = [
    ('L', Vector((0.02, -0.22, 0.82)), Vector((0.45, 0.20, 1.05))),
    ('R', Vector((-0.45, -0.22, 0.82)), Vector((-0.02, 0.20, 1.05)))
]

bpy.ops.object.select_all(action='DESELECT')
pelvis.select_set(True); bpy.context.view_layer.objects.active = pelvis
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(pelvis.data)
bm.faces.ensure_lookup_table()
deleted = 0
for side, bmin, bmax in pockets:
    to_del = []
    for f in bm.faces:
        c = f.calc_center_median()
        if bmin.x < c.x < bmax.x and bmin.y < c.y < bmax.y and bmin.z < c.z < bmax.z:
            to_del.append(f)
    bmesh.ops.delete(bm, geom=to_del, context='FACES')
    deleted += len(to_del)
    print(f'deleted {side} faces', len(to_del))
bmesh.update_edit_mesh(pelvis.data)
pelvis.data.update()
bpy.ops.object.mode_set(mode='OBJECT')

# topology after deletion
bm2 = bmesh.new(); bm2.from_mesh(pelvis.data)
edge_count = {}
for f in bm2.faces:
    for i in range(len(f.verts)):
        a=f.verts[i].index; b=f.verts[(i+1)%len(f.verts)].index
        edge_count[frozenset((a,b))] = edge_count.get(frozenset((a,b)),0)+1
boundary = sum(1 for c in edge_count.values() if c==1)
print('topology after delete: verts', len(bm2.verts), 'faces', len(bm2.faces), 'boundary_edges', boundary)
bm2.free()

# sweep
def cache_world(name):
    o = bpy.data.objects[name]; driver = o['rigid_driver_bone']
    e = o.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = e.to_mesh()
    pts = [o.matrix_world @ v.co for v in m.vertices]; fs = [tuple(p.vertices) for p in m.polygons]
    e.to_mesh_clear()
    inv = (rig.matrix_world @ rig.pose.bones[driver].matrix).inverted()
    return driver, [inv @ p for p in pts], fs

guard_cache = {n: cache_world(n) for n in ['Thigh guard L','Thigh guard R','Donor thigh L','Donor thigh R']}

rig.data.pose_position = 'POSE'; bpy.context.view_layer.update()
failures = []
for frame in range(1, 241):
    s.frame_set(frame); bpy.context.view_layer.update()
    e = pelvis.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = e.to_mesh()
    pv = [pelvis.matrix_world @ v.co for v in m.vertices]; pf = [tuple(p.vertices) for p in m.polygons]
    e.to_mesh_clear()
    body = BVHTree.FromPolygons(pv, pf)
    hits = {}
    for name, (driver, pts, fs) in guard_cache.items():
        mw = rig.matrix_world @ rig.pose.bones[driver].matrix
        gw = [mw @ p for p in pts]
        if body.overlap(BVHTree.FromPolygons(gw, fs)):
            hits[name] = True
    if hits:
        failures.append({'frame': frame, 'hits': list(hits.keys())})

print('SWEEP_RESULT', json.dumps({'checked': 240, 'crossing_frames': len(failures)}))
print('first_few', json.dumps(failures[:10]))
print('object_counts', json.dumps(dict(__import__('collections').Counter(n for f in failures for n in f['hits']))))
# save candidate
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/candidates/varek-carry-v15-manual-cut.blend'))
print('saved varek-carry-v15-manual-cut.blend')
