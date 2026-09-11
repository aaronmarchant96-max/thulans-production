import bpy, bmesh
from mathutils import Vector
from pathlib import Path

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def make_box(name, bmin, bmax):
    bm = bmesh.new()
    vs = [bm.verts.new(Vector((x,y,z))) for x in (bmin.x,bmax.x) for y in (bmin.y,bmax.y) for z in (bmin.z,bmax.z)]
    # ordering: minx,miny,minz=0; maxx,miny,minz=1; maxx,maxy,minz=2; minx,maxy,minz=3; minx,miny,maxz=4; maxx,miny,maxz=5; maxx,maxy,maxz=6; minx,maxy,maxz=7
    corners = [vs[0],vs[1],vs[5],vs[4], vs[2],vs[3],vs[7],vs[6]]
    faces = [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    for f in faces:
        bm.faces.new([corners[i] for i in f])
    bm.normal_update()
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh); bm.free()
    return mesh

# target cube 1m
mesh = make_box('target', Vector((-1,-1,-1)), Vector((1,1,1)))
o = bpy.data.objects.new('target', mesh); bpy.context.collection.objects.link(o)
# cutter cube 2m
cmesh = make_box('cutter', Vector((-0.5,-2,-2)), Vector((2,2,2)))
c = bpy.data.objects.new('cutter', cmesh); bpy.context.collection.objects.link(c)
bpy.context.view_layer.objects.active = o; o.select_set(True)
mod = o.modifiers.new('bool','BOOLEAN')
mod.operation='DIFFERENCE'; mod.object=c
bpy.ops.object.modifier_apply(modifier='bool')
print('verts', len(o.data.vertices), 'faces', len(o.data.polygons))
print('bounds x', min(v.co.x for v in o.data.vertices), max(v.co.x for v in o.data.vertices))
print('bounds y', min(v.co.y for v in o.data.vertices), max(v.co.y for v in o.data.vertices))
print('bounds z', min(v.co.z for v in o.data.vertices), max(v.co.z for v in o.data.vertices))
# check vertices inside cutter region
inside = [v.co for v in o.data.vertices if -0.5<v.co.x<2 and -2<v.co.y<2 and -2<v.co.z<2]
print('verts inside cutter AABB', len(inside))
