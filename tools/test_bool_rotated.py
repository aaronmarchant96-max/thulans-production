"""Test Boolean with rotated cutter to avoid coplanar issues."""
import bpy, bmesh, hashlib, json
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from pathlib import Path

R = Path('/home/aaron/animation/thulans-production')
SRC = R/'blender/candidates/varek-carry-v14.blend'

bpy.ops.wm.open_mainfile(filepath=str(SRC))
s = bpy.context.scene
rig = bpy.data.objects['Varek simple articulation']
pelvis = bpy.data.objects['Pelvic cradle']
# recalc normals
bpy.ops.object.select_all(action='DESELECT'); pelvis.select_set(True); bpy.context.view_layer.objects.active = pelvis
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode='OBJECT')

rig.data.pose_position = 'REST'; bpy.context.view_layer.update()

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
mesh = make_box(bmin, bmax)
cutter = bpy.data.objects.new('cutter', mesh)
s.collection.objects.link(cutter)

# rotate cutter slightly around y and z
cutter.rotation_euler = (0.0, 0.0174533, 0.0174533)  # 1 deg each
bpy.context.view_layer.update()

for solver in ['EXACT','MANIFOLD']:
    bpy.ops.wm.open_mainfile(filepath=str(SRC))
    s = bpy.context.scene; rig = bpy.data.objects['Varek simple articulation']; pelvis = bpy.data.objects['Pelvic cradle']
    bpy.ops.object.select_all(action='DESELECT'); pelvis.select_set(True); bpy.context.view_layer.objects.active = pelvis
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode='OBJECT')
    rig.data.pose_position = 'REST'; bpy.context.view_layer.update()
    mesh = make_box(bmin, bmax); cutter = bpy.data.objects.new('cutter_'+solver, mesh); s.collection.objects.link(cutter)
    cutter.rotation_euler = (0.0, 0.0174533, 0.0174533); bpy.context.view_layer.update()
    mod = pelvis.modifiers.new('bool', 'BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver=solver; mod.object=cutter
    while list(pelvis.modifiers).index(mod)>0:
        bpy.ops.object.modifier_move_up(modifier=mod.name)
    bpy.ops.object.modifier_apply(modifier='bool')
    # ray test
    e = pelvis.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = e.to_mesh()
    pv = [pelvis.matrix_world @ v.co for v in m.vertices]; pf = [tuple(p.vertices) for p in m.polygons]; e.to_mesh_clear()
    body = BVHTree.FromPolygons(pv, pf)
    origin = Vector((0.45, -0.10, 1.00)); direction = Vector((-1.0,0.0,0.0))
    hit = body.ray_cast(origin, direction)
    inside = [v.co for v in pelvis.data.vertices if bmin.x < v.co.x < bmax.x and bmin.y < v.co.y < bmax.y and bmin.z < v.co.z < bmax.z]
    print(solver, 'verts', len(pelvis.data.vertices), 'inside', len(inside), 'ray_hit', hit[0] is not None, 'dist', (hit[3] if hit[0] is not None else None))
    bpy.data.objects.remove(cutter, do_unlink=True); bpy.data.meshes.remove(mesh)
