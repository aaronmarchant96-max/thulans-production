"""Ray-cast through expected pocket after Boolean on V14."""
import bpy, bmesh, hashlib, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path

R = Path('/home/aaron/animation/thulans-production')
SRC = R/'blender/candidates/varek-carry-v14.blend'

bpy.ops.wm.open_mainfile(filepath=str(SRC))
s = bpy.context.scene
rig = bpy.data.objects['Varek simple articulation']
pelvis = bpy.data.objects['Pelvic cradle']

# Optional: recalc normals outside
bpy.ops.object.select_all(action='DESELECT')
pelvis.select_set(True); bpy.context.view_layer.objects.active = pelvis
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

rig.data.pose_position = 'REST'; bpy.context.view_layer.update()

def make_box(bmin, bmax):
    bm = bmesh.new()
    vs = [bm.verts.new(Vector((x,y,z))) for x in (bmin.x,bmax.x) for y in (bmin.y,bmax.y) for z in (bmin.z,bmax.z)]
    corners = [vs[0],vs[1],vs[5],vs[4], vs[2],vs[3],vs[7],vs[6]]
    faces = [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    for f in faces:
        bm.faces.new([corners[i] for i in f])
    bm.normal_update(); mesh = bpy.data.meshes.new('cutter'); bm.to_mesh(mesh); bm.free(); return mesh

bmin = Vector((0.07, -0.20, 0.88))
bmax = Vector((0.42, 0.18, 1.30))
mesh = make_box(bmin, bmax)
cutter = bpy.data.objects.new('cutter', mesh)
s.collection.objects.link(cutter)
mod = pelvis.modifiers.new('bool', 'BOOLEAN')
mod.operation = 'DIFFERENCE'; mod.solver = 'EXACT'; mod.object = cutter
while list(pelvis.modifiers).index(mod) > 0:
    bpy.ops.object.modifier_move_up(modifier=mod.name)
bpy.ops.object.modifier_apply(modifier=mod.name)

# build BVH from evaluated post-bool mesh at REST
e = pelvis.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = e.to_mesh()
pv = [pelvis.matrix_world @ v.co for v in m.vertices]
pf = [tuple(p.vertices) for p in m.polygons]
e.to_mesh_clear()
body = BVHTree.FromPolygons(pv, pf)

# ray tests through expected pocket at several y,z
for y,z in [(-0.14,0.91), (-0.10,0.95), (-0.05,1.00), (0.10,1.05)]:
    origin = Vector((0.45, y, z))
    direction = Vector((-1.0, 0.0, 0.0))
    hit = body.ray_cast(origin, direction)
    if hit[0] is not None:
        print(f'RAY y={y:.3f} z={z:.3f} hit=True dist={hit[3]:.4f}')
        print('  hit_loc', [round(c,4) for c in hit[0]], 'normal', [round(c,4) for c in hit[1]], 'face', hit[2])
    else:
        print(f'RAY y={y:.3f} z={z:.3f} hit=None')

# count faces whose centroids are inside the column region
inside_faces = 0
for p in pf:
    tri = [pv[i] for i in p]
    c = sum(tri, Vector())/len(tri)
    if bmin.x < c.x < bmax.x and bmin.y < c.y < bmax.y and bmin.z < c.z < bmax.z:
        inside_faces += 1
print('faces_inside_column', inside_faces)
