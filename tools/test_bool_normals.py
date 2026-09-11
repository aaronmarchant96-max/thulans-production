import bpy, bmesh, hashlib, json
from mathutils import Vector
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

# recalc normals outside
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

for side, bmin, bmax in [
    ('L', Vector((0.07, -0.20, 0.88)), Vector((0.42, 0.18, 1.30))),
    ('R', Vector((-0.42, -0.20, 0.88)), Vector((-0.07, 0.18, 1.30)))
]:
    mesh = make_box(bmin, bmax)
    cutter = bpy.data.objects.new(f'cutter_{side}', mesh)
    s.collection.objects.link(cutter)
    mod = pelvis.modifiers.new(f'bool_{side}', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'; mod.solver = 'EXACT'; mod.object = cutter
    while list(pelvis.modifiers).index(mod) > 0:
        bpy.ops.object.modifier_move_up(modifier=mod.name)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    bpy.data.meshes.remove(mesh)

verts = list(pelvis.data.vertices)
print('POST_BOOL_NORMALS', json.dumps({
    'verts': len(verts),
    'bounds': {
        'x': [min(v.co.x for v in verts), max(v.co.x for v in verts)],
        'y': [min(v.co.y for v in verts), max(v.co.y for v in verts)],
        'z': [min(v.co.z for v in verts), max(v.co.z for v in verts)],
    }
}))
inside = [v.co for v in verts if 0.07 < v.co.x < 0.42 and -0.20 < v.co.y < 0.18 and 0.88 < v.co.z < 1.30]
print('verts_inside_L_column', len(inside), 'z_min_inside', min(v.z for v in inside) if inside else None)
# save for visual inspection
bpy.ops.wm.save_as_mainfile(filepath=str(R/'/tmp/opencode/v14_bool_normals.blend'))
print('saved')
