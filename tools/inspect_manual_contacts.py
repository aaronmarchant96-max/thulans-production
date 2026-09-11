"""Inspect where contacts remain after manual pocket deletion."""
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
import json

R = Path('/home/aaron/animation/thulans-production')
SRC = R/'blender/candidates/varek-carry-v15-manual-cut.blend'
bpy.ops.wm.open_mainfile(filepath=str(SRC))
s = bpy.context.scene
rig = bpy.data.objects['Varek simple articulation']
pelvis = bpy.data.objects['Pelvic cradle']
F = json.loads((R/'evidence/varek-simplified-donor-v2/build.json').read_text())['normalization_factor']

def cache_world(name):
    o = bpy.data.objects[name]; driver = o['rigid_driver_bone']
    e = o.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = e.to_mesh()
    pts = [o.matrix_world @ v.co for v in m.vertices]; fs = [tuple(p.vertices) for p in m.polygons]
    e.to_mesh_clear()
    inv = (rig.matrix_world @ rig.pose.bones[driver].matrix).inverted()
    return driver, [inv @ p for p in pts], fs

guard_cache = {n: cache_world(n) for n in ['Thigh guard L','Thigh guard R','Donor thigh L','Donor thigh R']}

# find first few failing frames and sample contact points
for frame in range(1, 241):
    s.frame_set(frame); bpy.context.view_layer.update()
    e = pelvis.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = e.to_mesh()
    pv = [pelvis.matrix_world @ v.co for v in m.vertices]; pf = [tuple(p.vertices) for p in m.polygons]
    e.to_mesh_clear()
    body = BVHTree.FromPolygons(pv, pf)
    for name, (driver, pts, fs) in guard_cache.items():
        mw = rig.matrix_world @ rig.pose.bones[driver].matrix
        gw = [mw @ p for p in pts]
        ov = body.overlap(BVHTree.FromPolygons(gw, fs))
        if ov:
            # pick deepest point per side
            if 'L' in name:
                pair = min(ov, key=lambda p: (pv[p[0]].x + gw[p[1]].x))
            else:
                pair = max(ov, key=lambda p: (pv[p[0]].x + gw[p[1]].x))
            pidx, gidx = pair
            cp = (pv[pidx] + gw[gidx]) / 2
            print('FRAME', frame, 'OBJ', name, 'pairs', len(ov), 'contact_world', [round(c,5) for c in cp])
            break
    if frame > 60:
        break

# also print pelvis evaluated bounds at frame 50
s.frame_set(50); bpy.context.view_layer.update()
e = pelvis.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = e.to_mesh()
pv = [pelvis.matrix_world @ v.co for v in m.vertices]
print('pelvis_world_bounds_50', {
    'x': [round(min(v.x for v in pv),5), round(max(v.x for v in pv),5)],
    'y': [round(min(v.y for v in pv),5), round(max(v.y for v in pv),5)],
    'z': [round(min(v.z for v in pv),5), round(max(v.z for v in pv),5)],
})
e.to_mesh_clear()
