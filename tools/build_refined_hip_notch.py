"""Build a refined outer-upper hip notch from measured contact cloud.
Loads varek-carry-v14.blend, carves only the contact envelope, caps/recesses via
bmesh inset_region, runs full 240-frame sweep, saves the first passing candidate.
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
MARGIN = Vector((0.010, 0.020, 0.020))

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

def build_and_test(depth):
    bpy.ops.wm.open_mainfile(filepath=str(SRC))
    s = bpy.context.scene
    rig = bpy.data.objects['Varek simple articulation']
    pelvis = bpy.data.objects['Pelvic cradle']
    rig.data.pose_position = 'REST'; bpy.context.view_layer.update()

    to_rest = (rig.matrix_world @ rig.data.bones[PEL_BONE].matrix_local) @ \
              (rig.matrix_world @ rig.pose.bones[PEL_BONE].matrix).inverted()

    bpy.ops.object.select_all(action='DESELECT')
    pelvis.select_set(True); bpy.context.view_layer.objects.active = pelvis
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(pelvis.data)
    bm.faces.ensure_lookup_table()

    selection_counts = {}
    for side in ('L', 'R'):
        bmin, bmax = notch_box(side)
        if side == 'L':
            bmin.x = max(bmin.x, 0.0); bmax.x = min(bmax.x, 0.12)
        else:
            bmin.x = max(bmin.x, -0.12); bmax.x = min(bmax.x, 0.0)
        bmin.z = max(bmin.z, 0.90); bmax.z = min(bmax.z, 1.05)
        print(f"side {side} notch box bmin {[round(c,4) for c in bmin]} bmax {[round(c,4) for c in bmax]}")

        sel = []
        for f in bm.faces:
            c = f.calc_center_median()
            cb = to_rest @ (pelvis.matrix_world @ c)
            if bmin.x < cb.x < bmax.x and bmin.y < cb.y < bmax.y and bmin.z < cb.z < bmax.z:
                f.select = True
                sel.append(f)
        selection_counts[side] = len(sel)
        print(f"selected {len(sel)} faces for {side}")
        if not sel:
            continue
        try:
            bmesh.ops.inset_region(bm, faces=sel, use_boundary=True, use_even_offset=True,
                                   use_interpolate=True, thickness=0.005, depth=-depth)
        except Exception as ex:
            print(f"inset_region failed for {side}: {ex}")
            return None

    bmesh.update_edit_mesh(pelvis.data)
    pelvis.data.update()
    bpy.ops.object.mode_set(mode='OBJECT')

    boundary, nonmanifold = topology_audit(pelvis)
    print(f"topology boundary={boundary} nonmanifold={nonmanifold}")

    rig.data.pose_position = 'POSE'
    bpy.context.view_layer.update()

    failures = sweep(pelvis, rig)
    print(f"depth={depth} crossing_frames={len(failures)}")
    if failures:
        print('first failures', failures[:5])
    return failures, boundary, nonmanifold, selection_counts

for depth in (0.03, 0.05, 0.08, 0.12, 0.18):
    result = build_and_test(depth)
    if result is None:
        continue
    failures, boundary, nonmanifold, selection_counts = result
    if not failures and boundary == 0 and nonmanifold == 0:
        print(f"PASS at depth={depth}; saving candidate")
        bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))
        sha = hashlib.sha256(OUT_BLEND.read_bytes()).hexdigest()
        OUT_EVIDENCE.mkdir(parents=True, exist_ok=True)
        (OUT_EVIDENCE/'measurements.json').write_text(json.dumps({
            'candidate': str(OUT_BLEND),
            'candidate_sha256': sha,
            'parent_candidate_sha256': expected,
            'source_cloud': str(CLOUD),
            'build_time_utc': datetime.now(timezone.utc).isoformat(),
            'depth': depth,
            'inset_thickness': 0.005,
            'selected_faces': selection_counts,
            'sweep_frames': 240,
            'crossing_frames': len(failures),
            'boundary_edges': boundary,
            'non_manifold_edges': nonmanifold,
            'status': 'PASS',
        }, indent=2))
        print('saved', OUT_BLEND, 'sha', sha)
        sys.exit(0)
    print(f"FAIL at depth={depth}: crossings={len(failures)} boundary={boundary} nonmanifold={nonmanifold}")

print('no passing depth found')
sys.exit(1)
