"""Inspect why v15 still crosses after inset."""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path

R = Path('/home/aaron/animation/thulans-production')
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/candidates/varek-carry-v15.blend'))
s = bpy.context.scene
rig = bpy.data.objects['Varek simple articulation']
pelvis = bpy.data.objects['Pelvic cradle']

def cache(name):
    o = bpy.data.objects[name]; driver = o['rigid_driver_bone']
    e = o.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = e.to_mesh()
    pts = [o.matrix_world @ v.co for v in m.vertices]; fs = [tuple(p.vertices) for p in m.polygons]
    e.to_mesh_clear()
    inv = (rig.matrix_world @ rig.pose.bones[driver].matrix).inverted()
    return driver, [inv @ p for p in pts], fs

guard_cache = {n: cache(n) for n in ['Thigh guard L','Thigh guard R','Donor thigh L','Donor thigh R']}

rig.data.pose_position = 'POSE'; bpy.context.view_layer.update()
for frame in [44, 46, 88, 90]:
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
            pair = min(ov, key=lambda p: pv[p[0]].x) if 'R' in name else max(ov, key=lambda p: pv[p[0]].x)
            cp = (pv[pair[0]] + gw[pair[1]])/2
            print(f'FRAME {frame} {name} pairs={len(ov)} contact={[(round(c,4) for c in cp)]}')
            break
