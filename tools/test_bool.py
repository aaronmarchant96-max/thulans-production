import bpy
import bmesh
from mathutils import Vector
from pathlib import Path
R = Path('/home/aaron/animation/thulans-production')
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/candidates/varek-carry-v14.blend'))
s = bpy.context.scene
r = bpy.data.objects['Varek simple articulation']
pelvis = bpy.data.objects['Pelvic cradle']
print('verts before', len(pelvis.data.vertices), 'mods', [m.type for m in pelvis.modifiers])
r.data.pose_position = 'REST'
bpy.context.view_layer.update()

def make_box(name, bmin, bmax):
    bm = bmesh.new()
    corners = [(bmin[0],bmin[1],bmin[2]),(bmax[0],bmin[1],bmin[2]),(bmax[0],bmax[1],bmin[2]),(bmin[0],bmax[1],bmin[2]),
               (bmin[0],bmin[1],bmax[2]),(bmax[0],bmin[1],bmax[2]),(bmax[0],bmax[1],bmax[2]),(bmin[0],bmax[1],bmax[2])]
    vs = [bm.verts.new(Vector(c)) for c in corners]
    for f in [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]:
        bm.faces.new([vs[i] for i in f])
    bm.normal_update()
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    return mesh

for solver in ['EXACT','FAST']:
    # reload file each iteration
    bpy.ops.wm.open_mainfile(filepath=str(R/'blender/candidates/varek-carry-v14.blend'))
    s = bpy.context.scene
    r = bpy.data.objects['Varek simple articulation']
    pelvis = bpy.data.objects['Pelvic cradle']
    r.data.pose_position = 'REST'
    bpy.context.view_layer.update()
    mesh = make_box('test_cutter_'+solver, (0.08, -0.16, 0.9), (0.12, -0.05, 1.1))
    cutter = bpy.data.objects.new('test_cutter_'+solver, mesh)
    s.collection.objects.link(cutter)
    mod = pelvis.modifiers.new('test_bool_'+solver, 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = solver
    mod.object = cutter
    while list(pelvis.modifiers).index(mod) > 0:
        bpy.ops.object.modifier_move_up(modifier=mod.name)
    print('solver', solver, 'before apply', len(pelvis.data.vertices))
    # evaluate modifier without applying
    dg = bpy.context.evaluated_depsgraph_get()
    ev = pelvis.evaluated_get(dg)
    em = ev.to_mesh()
    print('solver', solver, 'evaluated verts', len(em.vertices))
    ev.to_mesh_clear()
    bpy.ops.object.modifier_apply(modifier=mod.name)
    print('solver', solver, 'after apply', len(pelvis.data.vertices))
    bpy.data.objects.remove(cutter, do_unlink=True)
    bpy.data.meshes.remove(mesh)
