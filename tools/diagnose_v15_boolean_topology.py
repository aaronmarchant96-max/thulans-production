"""Topology + face-identity diagnostic after Boolean pocket cut on V14."""
import bpy, bmesh, hashlib, json, sys
from collections import defaultdict
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

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

# 1. base mesh counts and bounds
rig.data.pose_position = 'REST'
bpy.context.view_layer.update()
base_verts = [v.co.copy() for v in pelvis.data.vertices]
base_faces = [tuple(p.vertices) for p in pelvis.data.polygons]
print('BASE_PELVIS', json.dumps({
    'vertices': len(pelvis.data.vertices),
    'edges': len(pelvis.data.edges),
    'faces': len(pelvis.data.polygons),
    'bounds': {
        'x': [min(v.x for v in base_verts), max(v.x for v in base_verts)],
        'y': [min(v.y for v in base_verts), max(v.y for v in base_verts)],
        'z': [min(v.z for v in base_verts), max(v.z for v in base_verts)],
    }
}))

# 2. transforms and modifier order
print('TRANSFORMS', json.dumps({
    'pelvis': {
        'location': list(pelvis.location),
        'rotation': list(pelvis.rotation_euler),
        'scale': list(pelvis.scale),
        'matrix_world_scale': list(pelvis.matrix_world.to_scale()),
        'parent': pelvis.parent.name if pelvis.parent else None,
    },
    'rig_root_scale': list(rig.matrix_world.to_scale()),
    'modifier_order': [m.name for m in pelvis.modifiers],
    'normalization_factor': F,
}))

# 3. build cutter and apply Boolean
def make_box(bmin, bmax):
    bm = bmesh.new()
    corners = [
        (bmin.x, bmin.y, bmin.z), (bmax.x, bmin.y, bmin.z), (bmax.x, bmax.y, bmin.z), (bmin.x, bmax.y, bmin.z),
        (bmin.x, bmin.y, bmax.z), (bmax.x, bmin.y, bmax.z), (bmax.x, bmax.y, bmax.z), (bmin.x, bmax.y, bmax.z)
    ]
    vs = [bm.verts.new(Vector(c)) for c in corners]
    faces = [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    for fa in faces:
        bm.faces.new([vs[i] for i in fa])
    bm.normal_update()
    mesh = bpy.data.meshes.new('cutter')
    bm.to_mesh(mesh); bm.free()
    return mesh

# Use a generous pocket column: x 0.07-0.42, y -0.20-0.18, z 0.88-1.30
for side, bmin, bmax in [
    ('L', Vector((0.07, -0.20, 0.88)), Vector((0.42, 0.18, 1.30))),
    ('R', Vector((-0.42, -0.20, 0.88)), Vector((-0.07, 0.18, 1.30)))
]:
    mesh = make_box(bmin, bmax)
    cutter = bpy.data.objects.new(f'cutter_{side}', mesh)
    s.collection.objects.link(cutter)
    mod = pelvis.modifiers.new(f'bool_{side}', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'; mod.solver = 'EXACT'; mod.object = cutter
    while list(pelvis.modifiers).index(mod) > 0:
        bpy.ops.object.modifier_move_up(modifier=mod.name)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    bpy.data.meshes.remove(mesh)

# 4. post-Boolean base mesh counts
post_verts = [v.co.copy() for v in pelvis.data.vertices]
print('POST_BOOLEAN', json.dumps({
    'vertices': len(pelvis.data.vertices),
    'edges': len(pelvis.data.edges),
    'faces': len(pelvis.data.polygons),
    'delta_vertices': len(pelvis.data.vertices) - len(base_verts),
    'bounds': {
        'x': [min(v.x for v in post_verts), max(v.x for v in post_verts)],
        'y': [min(v.y for v in post_verts), max(v.y for v in post_verts)],
        'z': [min(v.z for v in post_verts), max(v.z for v in post_verts)],
    }
}))

# 5. topology on post-Boolean evaluated mesh at REST
evaluated = pelvis.evaluated_get(bpy.context.evaluated_depsgraph_get())
post_eval_mesh = evaluated.to_mesh()
bm = bmesh.new(); bm.from_mesh(post_eval_mesh)
bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
edge_face_count = defaultdict(int)
for f in bm.faces:
    for i in range(len(f.verts)):
        a = f.verts[i].index; b = f.verts[(i+1) % len(f.verts)].index
        edge_face_count[frozenset((a,b))] += 1
boundary = sum(1 for c in edge_face_count.values() if c == 1)
nonmanifold = sum(1 for c in edge_face_count.values() if c > 2)
print('POST_BOOLEAN_TOPOLOGY', json.dumps({
    'boundary_edges': boundary,
    'non_manifold_edges': nonmanifold,
    'faces': len(bm.faces),
    'verts': len(bm.verts),
}))
evaluated.to_mesh_clear()

# 6. build caches for moving parts; pelvis driver is itself (no bone)
def cache_world(name):
    o = bpy.data.objects[name]
    driver = o.get('rigid_driver_bone')
    if driver:
        e = o.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = e.to_mesh()
        pts = [o.matrix_world @ v.co for v in m.vertices]; fs = [tuple(p.vertices) for p in m.polygons]
        e.to_mesh_clear()
        inv = (rig.matrix_world @ rig.pose.bones[driver].matrix).inverted()
        return driver, [(inv @ p) for p in pts], fs
    else:
        # pelvis: use evaluated mesh directly each frame in world
        return None, None, None

guard_cache = {}
for name in ['Thigh guard L','Thigh guard R','Donor thigh L','Donor thigh R']:
    guard_cache[name] = cache_world(name)

# 7. sweep and record residual details
rig.data.pose_position = 'POSE'
bpy.context.view_layer.update()

# tolerance for classifying vertices
base_set = set((round(v.x,6), round(v.y,6), round(v.z,6)) for v in base_verts)

def classify_triangle(tri_verts):
    # tri_verts: list of 3 Vectors in local coords (rest)
    new = 0
    for v in tri_verts:
        key = (round(v.x,6), round(v.y,6), round(v.z,6))
        if key not in base_set:
            new += 1
    if new == 0: return 'ORIGINAL'
    if new >= 2: return 'BOOLEAN_WALL'
    return 'MIXED'

rows=[]
for frame in range(1, 241):
    s.frame_set(frame); bpy.context.view_layer.update()
    e = pelvis.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = e.to_mesh()
    pv = [pelvis.matrix_world @ v.co for v in m.vertices]
    pf = [tuple(p.vertices) for p in m.polygons]
    e.to_mesh_clear()
    body = BVHTree.FromPolygons(pv, pf)
    row = {'frame': frame, 'contacts': []}
    for name, (driver, pts, fs) in guard_cache.items():
        if pts is None: continue
        # move guard points to world
        mw = rig.matrix_world @ rig.pose.bones[driver].matrix
        gw = [mw @ p for p in pts]
        ov = body.overlap(BVHTree.FromPolygons(gw, fs))
        if ov:
            row['contacts'].append({'object': name, 'pairs': len(ov)})
    rows.append(row)

fail_rows = [r for r in rows if r['contacts']]
print('SWEEP', json.dumps({'frames': len(rows), 'crossing_frames': len(fail_rows)}))

# find representative frames for L and R
rep_L = next((r for r in fail_rows if any('Thigh guard L' in c['object'] for c in r['contacts'])), None)
rep_R = next((r for r in fail_rows if any('Thigh guard R' in c['object'] for c in r['contacts'])), None)

for label, rep, side in [('L', rep_L, 1), ('R', rep_R, -1)]:
    if not rep:
        print('NO_REP', label)
        continue
    s.frame_set(rep['frame']); bpy.context.view_layer.update()
    # get evaluated pelvis
    e = pelvis.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = e.to_mesh()
    pv_local = [v.co.copy() for v in m.vertices]
    pf = [tuple(p.vertices) for p in m.polygons]
    pv_world = [pelvis.matrix_world @ v for v in pv_local]
    body = BVHTree.FromPolygons(pv_world, pf)
    # get guard world
    name = f'Thigh guard {label}'
    driver, pts, fs = guard_cache[name]
    mw = rig.matrix_world @ rig.pose.bones[driver].matrix
    gw = [mw @ p for p in pts]
    ov = body.overlap(BVHTree.FromPolygons(gw, fs))
    # choose a representative overlapping pair: furthest inside (min/max x)
    if side == 1:
        rep_pair = min(ov, key=lambda p: (pv_world[p[0]].x + gw[p[1]].x) / 2)
    else:
        rep_pair = max(ov, key=lambda p: (pv_world[p[0]].x + gw[p[1]].x) / 2)
    pidx, gidx = rep_pair
    pface = pf[pidx]
    # classify vertices in local rest coords (pelvis evaluated mesh at rest)
    # we need the same vertex coords at REST after Boolean
    rig.data.pose_position = 'REST'; bpy.context.view_layer.update()
    e_rest = pelvis.evaluated_get(bpy.context.evaluated_depsgraph_get()); m_rest = e_rest.to_mesh()
    rest_local = [v.co.copy() for v in m_rest.vertices]
    e_rest.to_mesh_clear()
    tri = [rest_local[i] for i in pface]
    cls = classify_triangle(tri)
    # ray through pocket at this y/z
    y = pv_world[pidx].y; z = pv_world[pidx].z
    ray_origin = Vector((side * 0.45, y, z))
    ray_dir = Vector((side * -1.0, 0.0, 0.0))
    hit = body.ray_cast(ray_origin, ray_dir)
    print('REP', json.dumps({
        'side': label,
        'frame': rep['frame'],
        'contact_point': [round(pv_world[pidx].x,6), round(pv_world[pidx].y,6), round(pv_world[pidx].z,6)],
        'face_local_vertices': [[round(c,6) for c in v] for v in tri],
        'face_classification': cls,
        'ray_origin': [round(c,6) for c in ray_origin],
        'ray_hit': None if hit[0] is None else [round(c,6) for c in hit[1]],
        'ray_hit_normal': None if hit[0] is None else [round(c,6) for c in hit[2]],
        'ray_hit_index': hit[3],
    }, default=str))
    rig.data.pose_position = 'POSE'; bpy.context.view_layer.update()

print('DONE')
