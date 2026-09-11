"""Inspect the face hit by ray in the pocket."""
import bpy, bmesh, hashlib, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path

R = Path('/home/aaron/animation/thulans-production')
SRC = R/'blender/candidates/varek-carry-v14.blend'
bpy.ops.wm.open_mainfile(filepath=str(SRC))
s = bpy.context.scene; rig = bpy.data.objects['Varek simple articulation']; pelvis = bpy.data.objects['Pelvic cradle']
bpy.ops.object.select_all(action='DESELECT'); pelvis.select_set(True); bpy.context.view_layer.objects.active = pelvis
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode='OBJECT')
rig.data.pose_position = 'REST'; bpy.context.view_layer.update()

base_verts = [v.co.copy() for v in pelvis.data.vertices]
base_set = set((round(v.x,6), round(v.y,6), round(v.z,6)) for v in base_verts)

def make_box(bmin, bmax):
    bm = bmesh.new()
    vs = [bm.verts.new(Vector((x,y,z))) for x in (bmin.x,bmax.x) for y in (bmin.y,bmax.y) for z in (bmin.z,bmax.z)]
    corners = [vs[0],vs[1],vs[5],vs[4], vs[2],vs[3],vs[7],vs[6]]
    faces = [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    for f in faces:
        bm.faces.new([corners[i] for i in f])
    bm.normal_update(); mesh = bpy.data.meshes.new('cutter'); bm.to_mesh(mesh); bm.free(); return mesh

bmin = Vector((0.06, -0.21, 0.85))
bmax = Vector((0.45, 0.19, 1.35))
mesh = make_box(bmin, bmax); cutter = bpy.data.objects.new('cutter', mesh); s.collection.objects.link(cutter)
mod = pelvis.modifiers.new('bool', 'BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cutter
while list(pelvis.modifiers).index(mod)>0:
    bpy.ops.object.modifier_move_up(modifier=mod.name)
bpy.ops.object.modifier_apply(modifier='bool')

# save blend
bpy.ops.wm.save_as_mainfile(filepath=str(R/'/tmp/opencode/v14_bool_inspect.blend'))

e = pelvis.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = e.to_mesh()
pv = [pelvis.matrix_world @ v.co for v in m.vertices]; pf = [tuple(p.vertices) for p in m.polygons]
e.to_mesh_clear()
body = BVHTree.FromPolygons(pv, pf)
origin = Vector((0.45, -0.10, 1.00)); direction = Vector((-1.0,0.0,0.0))
hit = body.ray_cast(origin, direction)
print('HIT', hit)
if hit[0] is not None:
    fi = hit[2]
    tri = [pv[i] for i in pf[fi]]
    local_tri = [pelvis.data.vertices[i].co for i in pf[fi]]
    cls = []
    for v in local_tri:
        key = (round(v.x,6), round(v.y,6), round(v.z,6))
        cls.append('OLD' if key in base_set else 'NEW')
    print('face_index', fi)
    print('world_tri', [[round(c,5) for c in v] for v in tri])
    print('local_tri', [[round(c,5) for c in v] for v in local_tri])
    print('vertex_class', cls)
    # face normal in world
    e2 = pelvis.evaluated_get(bpy.context.evaluated_depsgraph_get()); m2 = e2.to_mesh()
    print('face_normal', [round(c,4) for c in m2.polygons[fi].normal])
    e2.to_mesh_clear()
