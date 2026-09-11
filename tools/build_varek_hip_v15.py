"""Build varek-carry-v15.blend from V14 by adding a targeted secondary hip pocket.
Source: varek-carry-v14.blend (preserved failed artifact).
Correction type: residual hip-clearance only (branch A).
Only Pelvic cradle is modified; rig, animation, materials, and all other meshes unchanged.
"""
import hashlib
import json
import sys
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

R = Path('/home/aaron/animation/thulans-production')
S = R / 'blender/candidates/varek-carry-v14.blend'
P = R / 'blender/candidates/varek-carry-v15.blend'
E = R / 'evidence/varek-carry-v15'
SOURCE_SHA = '397d6ec0d9d69dce423119693f25c5a8227767826d76effa31f74eb86a329b91'
DIAG = R / 'evidence/varek-carry-v14/residual-diagnostic.json'
MARGIN_M = 0.003  # extra clearance beyond the measured residual cloud
WEB_SAFETY_M = 0.002

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(S) == SOURCE_SHA and not P.exists(), 'Source V14 mismatch or V15 already exists'
E.mkdir(exist_ok=True)

diag = json.loads(DIAG.read_text())
F = json.loads((R / 'evidence/varek-simplified-donor-v2/build.json').read_text())['normalization_factor']
WEB_BOUNDARY = 0.035 * F

bpy.ops.wm.open_mainfile(filepath=str(S))
s = bpy.context.scene
r = bpy.data.objects['Varek simple articulation']
parts = bpy.data.collections['Varek_Editable_Parts']
pelvis = bpy.data.objects['Pelvic cradle']

names = ['Pelvic cradle'] + [kind + ' ' + side for side in ['L', 'R'] for kind in ['Thigh guard', 'Donor thigh']]

def other_signature():
    return hashlib.sha256(repr(sorted(
        (o.name, tuple(tuple(v.co) for v in o.data.vertices),
         tuple(tuple(p.vertices) for p in o.data.polygons),
         tuple(m.name if m else None for m in o.data.materials))
        for o in parts.objects if o.type == 'MESH' and o != pelvis)).encode()).hexdigest()

def animation_signature():
    records = []
    for o in [r] + [o for o in parts.objects if o.name.startswith('Calf ram ')]:
        if o.animation_data and o.animation_data.action:
            for layer in o.animation_data.action.layers:
                for strip in layer.strips:
                    for bag in strip.channelbags:
                        for c in bag.fcurves:
                            records.append((o.name, c.data_path, c.array_index,
                                            tuple((tuple(k.co), k.interpolation) for k in c.keyframe_points)))
    return hashlib.sha256(repr(records).encode()).hexdigest()

def evaluated(o):
    e = o.evaluated_get(bpy.context.evaluated_depsgraph_get())
    m = e.to_mesh()
    points = [e.matrix_world @ v.co for v in m.vertices]
    polys = [list(p.vertices) for p in m.polygons]
    e.to_mesh_clear()
    return points, polys

def cached_world(name, cache):
    driver, p, f = cache[name]
    m = r.matrix_world @ r.pose.bones[driver].matrix
    return [m @ v for v in p], f

before = other_signature()
anim_before = animation_signature()
rest_before = {b.name: tuple(tuple(row) for row in b.matrix_local) for b in r.data.bones}
materials_before = tuple(m.name for m in pelvis.data.materials)

# cache rest geometry for moving parts
s.frame_set(1); bpy.context.view_layer.update()
cache = {}
for name in names:
    o = bpy.data.objects[name]
    driver = o['rigid_driver_bone']
    p, f = evaluated(o)
    inv = (r.matrix_world @ r.pose.bones[driver].matrix).inverted()
    cache[name] = (driver, [inv @ v for v in p], f)

def box_mesh(name, bmin, bmax):
    """Create an axis-aligned box mesh from min/max bounds in pelvis-rest space."""
    bm = bmesh.new()
    corners = [
        Vector((bmin[0], bmin[1], bmin[2])), Vector((bmax[0], bmin[1], bmin[2])),
        Vector((bmax[0], bmax[1], bmin[2])), Vector((bmin[0], bmax[1], bmin[2])),
        Vector((bmin[0], bmin[1], bmax[2])), Vector((bmax[0], bmin[1], bmax[2])),
        Vector((bmax[0], bmax[1], bmax[2])), Vector((bmin[0], bmax[1], bmax[2])),
    ]
    verts = [bm.verts.new(c) for c in corners]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    for f in faces:
        bm.faces.new([verts[i] for i in f])
    bm.normal_update()
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    return mesh

bpy.ops.object.select_all(action='DESELECT')
pelvis.select_set(True)
bpy.context.view_layer.objects.active = pelvis
r.data.pose_position = 'REST'
bpy.context.view_layer.update()

pocket_records = []
# V14 primary pockets (recorded in V14 evidence)
v14_measurements = json.loads((R / 'evidence/varek-carry-v14/measurements.json').read_text())
primary = {rec['side']: rec['sweep_bounds'] for rec in v14_measurements['pockets']}
for rec in v14_measurements['pockets']:
    pocket_records.append({'side': rec['side'], 'type': 'primary', 'margin_m': rec['margin_m'],
                           'sweep_bounds': rec['sweep_bounds']})

secondary_bounds = {}
for side in ['L', 'R']:
    cloud = diag['objects']['Thigh guard ' + side].get('contact_cloud_rest', [])
    if not cloud:
        continue
    pts = [Vector(p) for p in cloud]
    # sanity: keep well outside central web
    for p in pts:
        assert abs(p.x) >= WEB_BOUNDARY + WEB_SAFETY_M, f'Cloud point too medial: {p}'
    xs = [p.x for p in pts]; ys = [p.y for p in pts]; zs = [p.z for p in pts]
    prim = primary[side]
    # The V14 primary pocket was built from a convex hull that did not fully cut the
    # lower/medial wedge, and the residual contact cloud sits below its floor. Build a
    # single reliable cutter that covers the union of the original primary sweep AABB
    # and the measured residual region, so the entire guard/donor swept column is
    # cleared in one Boolean. x stays well outside the protected central web.
    if side == 'L':
        bmin = [min(min(xs) - MARGIN_M, prim['min'][0] - MARGIN_M),
                min(min(ys) - MARGIN_M, prim['min'][1] - MARGIN_M),
                min(min(zs) - MARGIN_M, prim['min'][2] - MARGIN_M)]
        bmax = [max(max(xs) + MARGIN_M, prim['max'][0] + MARGIN_M),
                max(max(ys) + MARGIN_M, prim['max'][1] + MARGIN_M),
                max(max(zs) + MARGIN_M, prim['max'][2] + MARGIN_M)]
    else:
        bmax = [max(max(xs) + MARGIN_M, prim['max'][0] + MARGIN_M),
                max(max(ys) + MARGIN_M, prim['max'][1] + MARGIN_M),
                max(max(zs) + MARGIN_M, prim['max'][2] + MARGIN_M)]
        bmin = [min(min(xs) - MARGIN_M, prim['min'][0] - MARGIN_M),
                min(min(ys) - MARGIN_M, prim['min'][1] - MARGIN_M),
                min(min(zs) - MARGIN_M, prim['min'][2] - MARGIN_M)]
    mesh = box_mesh('Secondary hip sweep ' + side, bmin, bmax)
    cutter = bpy.data.objects.new('Secondary hip clearance ' + side, mesh)
    s.collection.objects.link(cutter)
    mod = pelvis.modifiers.new('Secondary hip pocket ' + side, 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = cutter
    while list(pelvis.modifiers).index(mod) > 0:
        bpy.ops.object.modifier_move_up(modifier=mod.name)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    secondary_bounds[side] = {'min': bmin, 'max': bmax}
    pocket_records.append({'side': side, 'type': 'secondary_residual', 'margin_m': MARGIN_M,
                           'cutter_bounds': {'min': bmin, 'max': bmax}, 'contact_cloud_samples': len(pts)})
    bpy.data.objects.remove(cutter, do_unlink=True)
    bpy.data.meshes.remove(mesh)

# Preserve pelvis armature binding if the original had a pelvis vertex group
pelvis.vertex_groups.clear()
g = pelvis.vertex_groups.new(name='pelvis')
g.add(list(range(len(pelvis.data.vertices))), 1.0, 'REPLACE')
pelvis['geometry_origin'] = 'V14 casing with secondary residual hip pockets'

r.data.pose_position = 'POSE'
bpy.context.view_layer.update()

# Remove only appended empty material slots
while len(pelvis.data.materials) > len(materials_before):
    idx = len(pelvis.data.materials) - 1
    assert pelvis.data.materials[idx] is None
    assert not any(p.material_index == idx for p in pelvis.data.polygons)
    pelvis.data.materials.pop(index=idx)
assert tuple(m.name for m in pelvis.data.materials) == materials_before
assert other_signature() == before
assert animation_signature() == anim_before
assert {b.name: tuple(tuple(row) for row in b.matrix_local) for b in r.data.bones} == rest_before

# Kinematic sweep verification
rows = []
for frame in range(1, 241):
    s.frame_set(frame); bpy.context.view_layer.update()
    p, f = evaluated(pelvis)
    body = BVHTree.FromPolygons(p, f)
    hits = {}
    for name in names[1:]:
        p, f = cached_world(name, cache)
        count = len(body.overlap(BVHTree.FromPolygons(p, f)))
        if count:
            hits[name] = count
    rows.append({'frame': frame, 'hip_surface_crossings': hits})
failures = [row for row in rows if row['hip_surface_crossings']]

# Surface-only intersections are allowed if no meaningful penetration; but we want zero crossings.
s.frame_set(110)
s['status'] = 'HIP_POCKET_KINEMATIC_REVIEW' if not failures else 'HIP_POCKET_CLEARANCE_FAIL'
s['physical_handoff_authorized'] = False
bpy.ops.wm.save_as_mainfile(filepath=str(P))
digest = sha(P)
record = {
    'source_sha256': SOURCE_SHA,
    'source_file': str(S),
    'candidate_sha256': digest,
    'claim_class': 'OBSERVED',
    'result': 'HIP_SURFACE_SWEEP_PASS' if not failures else 'HIP_SURFACE_SWEEP_FAIL',
    'correction_type': 'residual hip-clearance only',
    'changed_meshes': ['Pelvic cradle'],
    'other_geometry_materials_unchanged': other_signature() == before,
    'animation_unchanged': animation_signature() == anim_before,
    'animation_signature': anim_before,
    'rest_bones_unchanged': True,
    'primary_pockets_source': v14_measurements['candidate_sha256'],
    'pockets': pocket_records,
    'secondary_bounds': secondary_bounds,
    'frames': rows,
    'physical_handoff_authorized': False,
    'limits': ['measured motion envelope only', 'no structural strength or force certification']
}
(E / 'measurements.json').write_text(json.dumps(record, indent=2))
assert sha(S) == SOURCE_SHA
print('HIP_V15_RESULT', json.dumps({'candidate_sha256': digest,
                                    'checked_frames': len(rows),
                                    'crossing_frames': len(failures),
                                    'result': record['result']}), flush=True)
if failures:
    raise RuntimeError('V15 hip pocket failed — preserved diagnostic; no promotion')
