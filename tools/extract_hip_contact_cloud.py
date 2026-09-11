"""Extract hip/guard contact cloud from V14, F1-F240, with per-frame pelvis-rest transform.
Output: evidence/varek-carry-v14/contact-cloud-v14.json
"""
import bpy, hashlib, json
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

PEL_BONE = 'pelvis'
assert PEL_BONE in rig.data.bones, f"bones: {[b.name for b in rig.data.bones]}"

def build_bvh(obj, world_pts):
    """Triangulated BVH from evaluated mesh. Returns (verts_world, triangles, bvh)."""
    e = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    m = e.to_mesh()
    m.calc_loop_triangles()
    verts = world_pts
    tris = [tuple(t.vertices) for t in m.loop_triangles]
    e.to_mesh_clear()
    return verts, tris, BVHTree.FromPolygons(verts, tris)

def guard_rest_points(name):
    o = bpy.data.objects[name]
    driver = o['rigid_driver_bone']
    e = o.evaluated_get(bpy.context.evaluated_depsgraph_get())
    m = e.to_mesh()
    inv = (rig.matrix_world @ rig.pose.bones[driver].matrix).inverted()
    pts = [inv @ (o.matrix_world @ v.co) for v in m.vertices]
    e.to_mesh_clear()
    return driver, pts

guards = {
    'Thigh guard L': guard_rest_points('Thigh guard L'),
    'Thigh guard R': guard_rest_points('Thigh guard R'),
    'Donor thigh L': guard_rest_points('Donor thigh L'),
    'Donor thigh R': guard_rest_points('Donor thigh R'),
}

contacts = {'L': {'frames': set(), 'points': [], 'pairs': []},
            'R': {'frames': set(), 'points': [], 'pairs': []}}

for frame in range(1, 241):
    s.frame_set(frame)
    bpy.context.view_layer.update()

    # per-frame rest transform: world -> pelvis bone rest local
    to_rest = (rig.matrix_world @ rig.data.bones[PEL_BONE].matrix_local) @ \
              (rig.matrix_world @ rig.pose.bones[PEL_BONE].matrix).inverted()

    # pelvis evaluated world vertices and triangulation
    e = pelvis.evaluated_get(bpy.context.evaluated_depsgraph_get())
    m = e.to_mesh()
    pv_world = [pelvis.matrix_world @ v.co for v in m.vertices]
    _, tris_p, bvh_p = build_bvh(pelvis, pv_world)
    # tri centroids world
    tri_cent_p = {}
    for ti, tri in enumerate(tris_p):
        tri_cent_p[ti] = sum((pv_world[i] for i in tri), Vector()) / 3
    e.to_mesh_clear()

    for name, (driver, rest_pts) in guards.items():
        side = 'L' if 'L' in name else 'R'
        o = bpy.data.objects[name]
        mw = rig.matrix_world @ rig.pose.bones[driver].matrix
        world_pts = [mw @ p for p in rest_pts]
        _, tris_g, bvh_g = build_bvh(o, world_pts)
        tri_cent_g = {ti: sum((world_pts[i] for i in tri), Vector()) / 3 for ti, tri in enumerate(tris_g)}
        ov = bvh_p.overlap(bvh_g)
        if not ov:
            continue
        contacts[side]['frames'].add(frame)
        for ti_p, ti_g in ov:
            cp_world = (tri_cent_p[ti_p] + tri_cent_g[ti_g]) / 2
            cp_rest = to_rest @ cp_world
            pt = [round(c, 6) for c in cp_rest]
            contacts[side]['points'].append(pt)
            # pair-local AABB in pelvis rest space
            pts = [to_rest @ pv_world[i] for i in tris_p[ti_p]] + [to_rest @ world_pts[i] for i in tris_g[ti_g]]
            xs = [p.x for p in pts]; ys = [p.y for p in pts]; zs = [p.z for p in pts]
            contacts[side]['pairs'].append({
                'frame': frame,
                'guard': name,
                'pelvis_tri': ti_p,
                'guard_tri': ti_g,
                'proxy': pt,
                'aabb': {
                    'x': [round(min(xs), 6), round(max(xs), 6)],
                    'y': [round(min(ys), 6), round(max(ys), 6)],
                    'z': [round(min(zs), 6), round(max(zs), 6)],
                }
            })

for side in ('L', 'R'):
    info = contacts[side]
    info['frames'] = sorted(info['frames'])
    pts = info['points']
    if pts:
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; zs = [p[2] for p in pts]
        print(side, 'frames', len(info['frames']), 'points', len(pts),
              'x', (min(xs), max(xs)), 'y', (min(ys), max(ys)), 'z', (min(zs), max(zs)))
    else:
        print(side, 'no contacts')

out = R/'evidence/varek-carry-v14/contact-cloud-v14.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps({
    'source': str(SRC),
    'frames_checked': 240,
    'L': {'frames': contacts['L']['frames'], 'points': contacts['L']['points'],
          'point_count': len(contacts['L']['points'])},
    'R': {'frames': contacts['R']['frames'], 'points': contacts['R']['points'],
          'point_count': len(contacts['R']['points'])},
    'pairs': {side: contacts[side]['pairs'] for side in ('L','R')},
}, indent=2))
print('saved', out)
