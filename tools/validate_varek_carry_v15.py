"""Validate varek-carry-v15.blend: topology + 240-frame sweep.
Writes evidence/varek-carry-v15/validation.json.
"""
import bpy, bmesh, hashlib, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
from datetime import datetime, timezone

R = Path('/home/aaron/animation/thulans-production')
SRC = R/'blender/candidates/varek-carry-v15.blend'
E = R/'evidence/varek-carry-v15'
assert SRC.exists(), SRC

bpy.ops.wm.open_mainfile(filepath=str(SRC))
s = bpy.context.scene
rig = bpy.data.objects['Varek simple articulation']
pelvis = bpy.data.objects['Pelvic cradle']

# topology
bm = bmesh.new(); bm.from_mesh(pelvis.data)
edge_count = {}
for f in bm.faces:
    for i in range(len(f.verts)):
        a = f.verts[i].index; b = f.verts[(i+1) % len(f.verts)].index
        edge_count[frozenset((a,b))] = edge_count.get(frozenset((a,b)), 0) + 1
boundary = sum(1 for c in edge_count.values() if c == 1)
nonmanifold = sum(1 for c in edge_count.values() if c > 2)
bm.free()

def cache(name):
    o = bpy.data.objects[name]; driver = o['rigid_driver_bone']
    e = o.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = e.to_mesh()
    pts = [o.matrix_world @ v.co for v in m.vertices]; fs = [tuple(p.vertices) for p in m.polygons]
    e.to_mesh_clear()
    inv = (rig.matrix_world @ rig.pose.bones[driver].matrix).inverted()
    return driver, [inv @ p for p in pts], fs

guard_cache = {n: cache(n) for n in ['Thigh guard L','Thigh guard R','Donor thigh L','Donor thigh R']}

rig.data.pose_position = 'POSE'; bpy.context.view_layer.update()
failures = []
for frame in range(1, 241):
    s.frame_set(frame); bpy.context.view_layer.update()
    e = pelvis.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = e.to_mesh()
    pv = [pelvis.matrix_world @ v.co for v in m.vertices]; pf = [tuple(p.vertices) for p in m.polygons]
    e.to_mesh_clear()
    body = BVHTree.FromPolygons(pv, pf)
    hits = []
    for name, (driver, pts, fs) in guard_cache.items():
        mw = rig.matrix_world @ rig.pose.bones[driver].matrix
        gw = [mw @ p for p in pts]
        if body.overlap(BVHTree.FromPolygons(gw, fs)):
            hits.append(name)
    if hits:
        failures.append({'frame': frame, 'hits': hits})

sha = hashlib.sha256(SRC.read_bytes()).hexdigest()
result = {
    'candidate': str(SRC),
    'candidate_sha256': sha,
    'validated_utc': datetime.now(timezone.utc).isoformat(),
    'sweep_frames': 240,
    'crossing_frames': len(failures),
    'boundary_edges': boundary,
    'non_manifold_edges': nonmanifold,
    'status': 'PASS' if (not failures and boundary == 0 and nonmanifold == 0) else 'FAIL',
}
E.mkdir(parents=True, exist_ok=True)
(E/'validation.json').write_text(json.dumps(result, indent=2))
print('VALIDATION', json.dumps(result))
print('first_failures', failures[:5])
