"""V14 read-only residual diagnostic (revised to contract). No geometry changes.
Evidence output only: evidence/varek-carry-v14/residual-diagnostic.json
"""
import hashlib
import json
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

R = Path('/home/aaron/animation/thulans-production')
E = R / 'evidence/varek-carry-v14'
P = R / 'blender/candidates/varek-carry-v14.blend'
expected = json.loads((E / 'measurements.json').read_text())['candidate_sha256']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P) == expected

bpy.ops.wm.open_mainfile(filepath=str(P))
s = bpy.context.scene
r = bpy.data.objects['Varek simple articulation']
F = json.loads((R / 'evidence/varek-simplified-donor-v2/build.json').read_text())['normalization_factor']
WEB = 0.035 * F
TOL = 2e-4
DEPTH_THRESHOLD = 0.5e-3  # meaningful penetration threshold (mm) for classifications

probe = json.loads((E / 'probe.json').read_text())
assert probe['source_sha256'] == 'e63336bf783a5ae82e352f07b8d75d7c5a5f7387256f25c1137261cfb058e09a'

def evaluated(name):
    o = bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get())
    m = o.to_mesh()
    verts = [o.matrix_world @ v.co for v in m.vertices]
    faces = [list(p.vertices) for p in m.polygons]
    o.to_mesh_clear()
    return verts, faces

# Cutter coverage from the recorded sweep envelope (cutter = convex hull of sweep points
# expanded +/-2 mm axis-aligned around each hull vertex). Every hull vertex has z >= z_floor
# (the 0.925*F filter applied before sweep points were stored) and |x| >= x_medial_limit
# (bounding box of the sweep). The expanded cutter's axis-aligned bounds are therefore
# [z_floor-0.002, ...] and [x_medial_limit-0.002, ...]. Any point beyond those bounds is
# OUTSIDE the cutter volume by construction; the axis gap is a certified lower bound on the
# true signed plane distance. Points inside the band are marked UNKNOWN (hull facets are not
# certified here after the reconstruction corruption observed with bmesh convex_hull at this
# scale). This replaces fragile hull reconstruction with provable coverage bounds.
cutter_coverage = {}
for side in ['L', 'R']:
    pts = [Vector(p) for p in probe['sweep_points'][side]]
    xvals = [p.x for p in pts]; zvals = [p.z for p in pts]
    cov = {
        'z_floor_m': min(zvals),
        'x_medial_limit_m': min(abs(p.x) for p in pts),
        'x_lateral_limit_m': max(abs(p.x) for p in pts),
        'n_points': len(pts),
    }
    cutter_coverage[side] = cov
    print('CUTTER_COVERAGE', json.dumps({side: cov}, separators=(',', ':')), flush=True)
CUTTER_MARGIN_M = 0.002

def in_solid(tree, p):
    origin = p.copy()
    origin.x += 1e-4
    count = 0
    loc, _, _, _ = tree.ray_cast(origin, Vector((1, 0, 0)))
    while loc is not None:
        count += 1
        origin = loc + Vector((1e-4, 0, 0))
        loc, _, _, _ = tree.ray_cast(origin, Vector((1, 0, 0)))
    return count % 2 == 1

def ranges(frames):
    if not frames:
        return []
    out = []
    start = prev = frames[0]
    for f in frames[1:]:
        if f == prev + 1:
            prev = f
            continue
        out.append((start, prev))
        start = prev = f
    out.append((start, prev))
    return [f'F{a}-F{b}' if a != b else f'F{a}' for a, b in out]

# --- pelvis watertight audit (frame 240; an evaluated frame representative of the mesh) ---
s.frame_set(240); bpy.context.view_layer.update()
pv, pf = evaluated('Pelvic cradle')
from collections import defaultdict
edge_use = defaultdict(int)
for f in pf:
    k = len(f)
    for i in range(k):
        edge_use[frozenset((f[i], f[(i + 1) % k]))] += 1
boundary_edges = sum(1 for c in edge_use.values() if c == 1)
non_manifold_edges = sum(1 for c in edge_use.values() if c > 2)
watertight = boundary_edges == 0 and non_manifold_edges == 0
print('PELVIS_TOPOLOGY', json.dumps({'boundary_edges': boundary_edges,
                                     'non_manifold_edges': non_manifold_edges,
                                     'watertight': watertight}), flush=True)

# --- pelvic pose stability (does pelvis-rest space vary over the envelope?) ---
pelvis_frames = {}
for frame in [1, 60, 100, 144, 240]:
    s.frame_set(frame); bpy.context.view_layer.update()
    pelvis_frames[frame] = [list(row) for row in (r.matrix_world @ r.pose.bones['pelvis'].matrix)]
print('PELVIS_POSE_SAMPLES', json.dumps(pelvis_frames), flush=True)

# --- main sweep ---
records = {name: {'frame_overlap': [], 'frame_pen': [], 'overlap_pairs': {},
                  'pen_verts_rest': [], 'contact_centroids_rest': []}
           for name in ['Thigh guard L', 'Thigh guard R', 'Donor thigh L', 'Donor thigh R']}

s.frame_set(1); bpy.context.view_layer.update()
for frame in range(1, 241):
    s.frame_set(frame); bpy.context.view_layer.update()
    to_rest = r.matrix_world @ r.data.bones['pelvis'].matrix_local @ (r.matrix_world @ r.pose.bones['pelvis'].matrix).inverted()
    pv, pf = evaluated('Pelvic cradle')
    tree = BVHTree.FromPolygons(pv, pf)
    for name in records:
        vv, ff = evaluated(name)
        pairs = tree.overlap(BVHTree.FromPolygons(vv, ff))
        rec = records[name]
        if not pairs:
            continue
        rec['frame_overlap'].append(frame)
        rec['overlap_pairs'][frame] = len(pairs)
        side = 'L' if name.endswith(' L') else 'R'
        for a, b in pairs:
            tri = [vv[i] for i in ff[b]]
            rec['contact_centroids_rest'].append(to_rest @ (sum(tri, Vector()) / len(tri)))
            if watertight:
                for g in tri:
                    if in_solid(tree, g):
                        near = tree.find_nearest(g)[0]
                        depth = (g - near).length if near is not None else None
                        rec['pen_verts_rest'].append({
                            'rest': tuple(round(c, 7) for c in (to_rest @ g)),
                            'depth_m': depth,
                            'web': abs((to_rest @ g).x) < WEB,
                        })
                        rec['frame_pen'].append(frame)

# collapse pen frames uniquely
for name in records:
    records[name]['frame_pen'] = sorted(set(records[name]['frame_pen']))

out = {}
for name, rec in records.items():
    side = 'L' if name.endswith(' L') else 'R'
    pen_verts = rec['pen_verts_rest']
    web_cross = sum(1 for v in pen_verts if v['web']) if watertight else None
    max_depth = max((v['depth_m'] or 0) for v in pen_verts) if (watertight and pen_verts) else None
    max_pairs = max(rec['overlap_pairs'].values(), default=0)
    frame_max_pairs = [f for f, c in rec['overlap_pairs'].items() if c == max_pairs] if rec['overlap_pairs'] else []
    cents = rec['contact_centroids_rest']
    xs = [p.x for p in cents]; ys = [p.y for p in cents]; zs = [p.z for p in cents]
    aabb = {'min': [min(xs), min(ys), min(zs)], 'max': [max(xs), max(ys), max(zs)]} if cents else None
    cutter_out = 0; cutter_unk = 0; cutter_out_min = 1e30; cutter_out_max = 0.0
    x_cut = cutter_coverage[side]['x_medial_limit_m'] - CUTTER_MARGIN_M
    z_cut = cutter_coverage[side]['z_floor_m'] - CUTTER_MARGIN_M
    for p in cents:
        gap = max(x_cut - abs(p.x), z_cut - p.z, 0.0)
        if gap > TOL:
            cutter_out += 1
            cutter_out_min = min(cutter_out_min, gap)
            cutter_out_max = max(cutter_out_max, gap)
        else:
            cutter_unk += 1
    crosses_web = web_cross and web_cross > 0 if watertight else None
    if not rec['frame_overlap']:
        classification = 'CLEAN_NO_INTERSECTION'
    elif not watertight:
        classification = 'UNRESOLVED'
    elif rec['frame_pen'] and (max_depth or 0) >= DEPTH_THRESHOLD:
        classification = 'MEANINGFUL_PENETRATION'
    else:
        classification = 'SURFACE_INTERSECTION_ONLY'
    out[name] = {
        'overlap_frame_ranges': ranges(rec['frame_overlap']),
        'meaningful_penetration_frames': ranges(rec['frame_pen']) if watertight else None,
        'overlap_frame_count': len(rec['frame_overlap']),
        'max_overlap_pairs': max_pairs,
        'frame_of_max_overlap': frame_max_pairs,
        'max_penetration_depth_m': max_depth,
        'rest_aabb': aabb,
        'crosses_central_web': crosses_web,
        'web_cross_contact_points': web_cross,
        'contact_cloud_rest': [[round(c, 7) for c in p] for p in cents],
        'cutter_inside_proved_samples': 0,
        'cutter_inside_band_unknown_samples': cutter_unk,
        'cutter_outside_proved_samples': cutter_out,
        'cutter_outside_min_signed_lb_m': round(cutter_out_min, 6) if cutter_out else 0.0,
        'cutter_outside_max_signed_lb_m': round(cutter_out_max, 6),
        'classification': classification,
    }

result = {
    'candidate_sha256': expected,
    'source_sha256': probe['source_sha256'],
    'pelvis_topology': {'watertight': watertight, 'boundary_edges': boundary_edges,
                        'non_manifold_edges': non_manifold_edges},
    'pelvis_pose_static': pelvis_frames,
    'web_boundary_m': WEB,
    'tolerance_m': TOL,
    'meaningful_penetration_threshold_m': DEPTH_THRESHOLD,
    'cutter_coverage': cutter_coverage,
    'objects': out,
}
(E / 'residual-diagnostic.json').write_text(json.dumps(result, indent=1))
print('RESIDUAL_SUMMARY', json.dumps(out, indent=1), flush=True)
print('DIAGNOSTIC_READY', flush=True)