"""Build a refined outer-upper hip clearance by displacing pelvis vertices inward.
Uses measured contact cloud; preserves manifold topology; runs full POSE sweep.
"""
import bpy, bmesh, hashlib, json, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
from datetime import datetime, timezone

R = Path('/home/aaron/animation/thulans-production')
SRC = R/'blender/candidates/varek-carry-v14.blend'
E = R/'evidence/varek-carry-v14'
CLOUD = R/'evidence/varek-carry-v14/contact-cloud-v14.json'
OUT_BLEND = R/'blender/candidates/varek-carry-v15.blend'
OUT_EVIDENCE = R/'evidence/varek-carry-v15'

expected = json.loads((E/'measurements.json').read_text())['candidate_sha256']
assert hashlib.sha256(SRC.read_bytes()).hexdigest() == expected

cloud = json.loads(CLOUD.read_text())
PEL_BONE = 'pelvis'
MARGIN = Vector((0.020, 0.040, 0.040))

def notch_box(side):
    pts = cloud[side]['points']
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; zs = [p[2] for p in pts]
    bmin = Vector((min(xs)-MARGIN.x, min(ys)-MARGIN.y, min(zs)-MARGIN.z))
    bmax = Vector((max(xs)+MARGIN.x, max(ys)+MARGIN.y, max(zs)+MARGIN.z))
    return bmin, bmax

def sweep(pelvis, rig):
    def cache(name):
        o = bpy.data.objects[name]; driver = o['rigid_driver_bone']
        e = o.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = e.to_mesh()
        pts = [o.matrix_world @ v.co for v in m.vertices]; fs = [tuple(p.vertices) for p in m.polygons]
        e.to_mesh_clear()
        inv = (rig.matrix_world @ rig.pose.bones[driver].matrix).inverted()
        return driver, [inv @ p for p in pts], fs
    guard_cache = {n: cache(n) for n in ['Thigh guard L','Thigh guard R','Donor thigh L','Donor thigh R']}
    failures = []
    for frame in range(1, 241):
        bpy.context.scene.frame_set(frame); bpy.context.view_layer.update()
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
    return failures

def topology_audit(obj):
    bm = bmesh.new(); bm.from_mesh(obj.data)
    edge_count = {}
    for f in bm.faces:
        for i in range(len(f.verts)):
            a = f.verts[i].index; b = f.verts[(i+1) % len(f.verts)].index
            edge_count[frozenset((a,b))] = edge_count.get(frozenset((a,b)), 0) + 1
    boundary = sum(1 for c in edge_count.values() if c == 1)
    nonmanifold = sum(1 for c in edge_count.values() if c > 2)
    bm.free()
    return boundary, nonmanifold

def build_and_test(max_disp_bone):
    bpy.ops.wm.open_mainfile(filepath=str(SRC))
    s = bpy.context.scene
    rig = bpy.data.objects['Varek simple articulation']
    pelvis = bpy.data.objects['Pelvic cradle']
    rig.data.pose_position = 'REST'; bpy.context.view_layer.update()

    # affine map object local -> pelvis bone rest local
    M = (rig.matrix_world @ rig.data.bones[PEL_BONE].matrix_local) @ \
        (rig.matrix_world @ rig.pose.bones[PEL_BONE].matrix).inverted() @ \
        pelvis.matrix_world
    M3 = M.to_3x3()
    Minv3 = M3.inverted()

    bpy.ops.object.select_all(action='DESELECT')
    pelvis.select_set(True); bpy.context.view_layer.objects.active = pelvis
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(pelvis.data)
    bm.verts.ensure_lookup_table()

    moved = 0
    for side in ('L', 'R'):
        bmin, bmax = notch_box(side)
        if side == 'L':
            bmin.x = max(bmin.x, 0.0); bmax.x = min(bmax.x, 0.15)
        else:
            bmin.x = max(bmin.x, -0.15); bmax.x = min(bmax.x, 0.0)
        bmin.z = max(bmin.z, 0.88); bmax.z = min(bmax.z, 1.08)
        center = (bmin + bmax) / 2
        size = bmax - bmin
        print(f"side {side} box bmin {[round(c,4) for c in bmin]} bmax {[round(c,4) for c in bmax]}")
        for v in bm.verts:
            p_bone = M @ v.co
            if not (bmin.x < p_bone.x < bmax.x and bmin.y < p_bone.y < bmax.y and bmin.z < p_bone.z < bmax.z):
                continue
            # smooth falloff from box center (1) to boundary (0)
            t = Vector((
                2*abs(p_bone.x - center.x)/size.x,
                2*abs(p_bone.y - center.y)/size.y,
                2*abs(p_bone.z - center.z)/size.z,
            ))
            w = max(0.0, 1.0 - max(t.x, t.y, t.z))
            w = w*w*(3-2*w)  # smoothstep
            if w <= 0:
                continue
            # displacement in bone local: inward
            d_bone = Vector((-max_disp_bone * w if side == 'L' else max_disp_bone * w, 0.0, 0.0))
            d_obj = Minv3 @ d_bone
            v.co += d_obj
            moved += 1
    print(f"moved {moved} vertices")

    bmesh.update_edit_mesh(pelvis.data)
    pelvis.data.update()
    bpy.ops.object.mode_set(mode='OBJECT')

    boundary, nonmanifold = topology_audit(pelvis)
    print(f"topology boundary={boundary} nonmanifold={nonmanifold}")

    rig.data.pose_position = 'POSE'; bpy.context.view_layer.update()
    failures = sweep(pelvis, rig)
    print(f"max_disp_bone={max_disp_bone} crossing_frames={len(failures)}")
    if failures:
        print('first failures', failures[:5])
    return failures, boundary, nonmanifold, moved

for disp in (0.03, 0.05, 0.08, 0.12):
    result = build_and_test(disp)
    if result is None:
        continue
    failures, boundary, nonmanifold, moved = result
    if not failures and boundary == 0 and nonmanifold == 0:
        print(f"PASS at disp={disp}; saving")
        bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))
        sha = hashlib.sha256(OUT_BLEND.read_bytes()).hexdigest()
        OUT_EVIDENCE.mkdir(parents=True, exist_ok=True)
        (OUT_EVIDENCE/'measurements.json').write_text(json.dumps({
            'candidate': str(OUT_BLEND),
            'candidate_sha256': sha,
            'parent_candidate_sha256': expected,
            'source_cloud': str(CLOUD),
            'build_time_utc': datetime.now(timezone.utc).isoformat(),
            'max_displacement_bone_local': disp,
            'sweep_frames': 240,
            'crossing_frames': len(failures),
            'boundary_edges': boundary,
            'non_manifold_edges': nonmanifold,
            'status': 'PASS',
        }, indent=2))
        print('saved', OUT_BLEND, 'sha', sha)
        sys.exit(0)
    print(f"FAIL at disp={disp}: crossings={len(failures)} boundary={boundary} nonmanifold={nonmanifold}")

print('no passing displacement found')
sys.exit(1)
