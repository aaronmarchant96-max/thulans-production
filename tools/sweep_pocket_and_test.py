"""Compute thigh guard swept AABB in pelvis rest space and carve pocket by face deletion."""
import bpy, bmesh, hashlib, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path

R = Path('/home/aaron/animation/thulans-production')
SRC = R/'blender/candidates/varek-carry-v14.blend'
E = R/'evidence/varek-carry-v14'
expected = json.loads((E/'measurements.json').read_text())['candidate_sha256']
assert hashlib.sha256(SRC.read_bytes()).hexdigest() == expected

bpy.ops.wm.open_mainfile(filepath=str(SRC))
s = bpy.context.scene
rig = bpy.data.objects['Varek simple articulation']
pelvis = bpy.data.objects['Pelvic cradle']
F = json.loads((R/'evidence/varek-simplified-donor-v2/build.json').read_text())['normalization_factor']

# compute pelvis rest local AABB of each thigh guard over all frames
rig.data.pose_position = 'POSE'; bpy.context.view_layer.update()
pelvis_inv = pelvis.matrix_world.inverted()
# Actually we want points in pelvis local rest space. The guard points in world, then pelvis local.
side_data = {}
for name in ['Thigh guard L','Thigh guard R']:
    o = bpy.data.objects[name]; driver = o['rigid_driver_bone']
    all_local = []
    for frame in range(1, 241):
        s.frame_set(frame); bpy.context.view_layer.update()
        e = o.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = e.to_mesh()
        mw = rig.matrix_world @ rig.pose.bones[driver].matrix
        for v in m.vertices:
            world = o.matrix_world @ v.co
            # local in pelvis rest space: pelvis world is identity-ish, but use its inverse
            all_local.append(pelvis_inv @ world)
        e.to_mesh_clear()
    xs = [p.x for p in all_local]; ys = [p.y for p in all_local]; zs = [p.z for p in all_local]
    side_data[name] = {
        'x': (min(xs), max(xs)),
        'y': (min(ys), max(ys)),
        'z': (min(zs), max(zs)),
    }
print('GUARD_SWEEPS', json.dumps(side_data, indent=2))

# Now carve pockets: expand by margin
margin = Vector((0.02, 0.02, 0.02))
pockets = []
for name, bd in side_data.items():
    side = 'L' if 'L' in name else 'R'
    bmin = Vector((bd['x'][0]-margin.x, bd['y'][0]-margin.y, bd['z'][0]-margin.z))
    bmax = Vector((bd['x'][1]+margin.x, bd['y'][1]+margin.y, bd['z'][1]+margin.z))
    pockets.append((side, bmin, bmax))
print('POCKETS', pockets)

# reload to apply deletions on clean V14
bpy.ops.wm.open_mainfile(filepath=str(SRC))
s = bpy.context.scene; rig = bpy.data.objects['Varek simple articulation']; pelvis = bpy.data.objects['Pelvic cradle']

bpy.ops.object.select_all(action='DESELECT')
pelvis.select_set(True); bpy.context.view_layer.objects.active = pelvis
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(pelvis.data)
bm.faces.ensure_lookup_table()
for side, bmin, bmax in pockets:
    to_del = []
    for f in bm.faces:
        c = f.calc_center_median()
        if bmin.x < c.x < bmax.x and bmin.y < c.y < bmax.y and bmin.z < c.z < bmax.z:
            to_del.append(f)
    print(f'deleting {side} faces', len(to_del), 'bmin', [round(c,4) for c in bmin], 'bmax', [round(c,4) for c in bmax])
    bmesh.ops.delete(bm, geom=to_del, context='FACES')
bmesh.update_edit_mesh(pelvis.data); pelvis.data.update(); bpy.ops.object.mode_set(mode='OBJECT')

# sweep
def cache_world(name):
    o = bpy.data.objects[name]; driver = o['rigid_driver_bone']
    e = o.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = e.to_mesh()
    pts = [o.matrix_world @ v.co for v in m.vertices]; fs = [tuple(p.vertices) for p in m.polygons]
    e.to_mesh_clear()
    inv = (rig.matrix_world @ rig.pose.bones[driver].matrix).inverted()
    return driver, [inv @ p for p in pts], fs

guard_cache = {n: cache_world(n) for n in ['Thigh guard L','Thigh guard R','Donor thigh L','Donor thigh R']}
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
print('object_counts', json.dumps(dict(__import__('collections').Counter(n for f in failures for n in f['hits']))))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/candidates/varek-carry-v15-sweep-pocket.blend'))
print('saved varek-carry-v15-sweep-pocket.blend')
