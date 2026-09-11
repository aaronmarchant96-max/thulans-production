import bpy, bmesh
from mathutils import Vector
from pathlib import Path
R = Path('/home/aaron/animation/thulans-production')
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/candidates/varek-carry-v14.blend'))
s=bpy.context.scene; r=bpy.data.objects['Varek simple articulation']; pelvis=bpy.data.objects['Pelvic cradle']
r.data.pose_position='REST'; bpy.context.view_layer.update()

def make_box(bmin,bmax):
    bm=bmesh.new()
    corners=[(bmin.x,bmin.y,bmin.z),(bmax.x,bmin.y,bmin.z),(bmax.x,bmax.y,bmin.z),(bmin.x,bmax.y,bmin.z),
             (bmin.x,bmin.y,bmax.z),(bmax.x,bmin.y,bmax.z),(bmax.x,bmax.y,bmax.z),(bmin.x,bmax.y,bmax.z)]
    vs=[bm.verts.new(Vector(c)) for c in corners]
    for fa in [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]:
        bm.faces.new([vs[i] for i in fa])
    bm.normal_update(); mesh=bpy.data.meshes.new('box'); bm.to_mesh(mesh); bm.free(); return mesh

print('before scale apply: pelvis scale', pelvis.scale, 'matrix scale', pelvis.matrix_world.to_scale())
bpy.ops.object.select_all(action='DESELECT'); pelvis.select_set(True); bpy.context.view_layer.objects.active=pelvis
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
print('after scale apply: pelvis scale', pelvis.scale, 'matrix scale', pelvis.matrix_world.to_scale())

for side,bmin,bmax in [('L',Vector((0.07,-0.19,0.89)),Vector((0.42,0.17,1.30))),
                        ('R',Vector((-0.42,-0.19,0.89)),Vector((-0.07,0.17,1.30)))]:
    mesh=make_box(bmin,bmax); cutter=bpy.data.objects.new('cutter_'+side,mesh); s.collection.objects.link(cutter)
    mod=pelvis.modifiers.new('bool_'+side,'BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cutter
    while list(pelvis.modifiers).index(mod)>0:
        bpy.ops.object.modifier_move_up(modifier=mod.name)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True); bpy.data.meshes.remove(mesh)

inside=[v.co for v in pelvis.data.vertices if 0.07<v.co.x<0.42 and -0.19<v.co.y<0.17 and 0.89<v.co.z<1.30]
print('verts inside L column after scale+bool',len(inside), 'total verts', len(pelvis.data.vertices))
