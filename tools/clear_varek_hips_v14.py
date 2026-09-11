"""Authorized local hip pockets, derived from the frozen V13 motion envelope.

Probe includes both underlying thigh housings and outer guards. Apply removes
only their measured upper sweep plus 2 mm clearance from the pelvic casing.
Rig, animation, hand, materials and all other meshes stay unchanged.
"""
import hashlib
import itertools
import json
import sys
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

R=Path('/home/aaron/animation/thulans-production')
S=R/'blender/candidates/varek-carry-v13-transfer.blend'
P=R/'blender/candidates/varek-carry-v14.blend'
E=R/'evidence/varek-carry-v14'
EXPECTED='e63336bf783a5ae82e352f07b8d75d7c5a5f7387256f25c1137261cfb058e09a'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(S)==EXPECTED and not P.exists()
E.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S))
s=bpy.context.scene;r=bpy.data.objects['Varek simple articulation']
parts=bpy.data.collections['Varek_Editable_Parts']
pelvis=bpy.data.objects['Pelvic cradle']
F=json.loads((R/'evidence/varek-simplified-donor-v2/build.json').read_text())['normalization_factor']

def other_signature():
    return hashlib.sha256(repr(sorted((o.name,tuple(tuple(v.co) for v in o.data.vertices),
        tuple(tuple(p.vertices) for p in o.data.polygons),tuple(m.name if m else None for m in o.data.materials))
        for o in parts.objects if o.type=='MESH' and o!=pelvis)).encode()).hexdigest()

def animation_signature():
    records=[]
    for o in [r]+[o for o in parts.objects if o.name.startswith('Calf ram ')]:
        if o.animation_data and o.animation_data.action:
            for layer in o.animation_data.action.layers:
                for strip in layer.strips:
                    for bag in strip.channelbags:
                        for c in bag.fcurves:
                            records.append((o.name,c.data_path,c.array_index,tuple((tuple(k.co),k.interpolation) for k in c.keyframe_points)))
    return hashlib.sha256(repr(records).encode()).hexdigest()

def evaluated(o):
    e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh()
    points=[e.matrix_world@v.co for v in m.vertices];polys=[list(p.vertices) for p in m.polygons]
    e.to_mesh_clear();return points,polys

before=other_signature();anim_before=animation_signature()
rest_before={b.name:tuple(tuple(row) for row in b.matrix_local) for b in r.data.bones}
materials_before=tuple(m.name for m in pelvis.data.materials)
names=['Pelvic cradle']+[kind+' '+side for side in ['L','R'] for kind in ['Thigh guard','Donor thigh']]
s.frame_set(1);bpy.context.view_layer.update()
cache={}
for name in names:
    o=bpy.data.objects[name];driver=o['rigid_driver_bone'];p,f=evaluated(o)
    inv=(r.matrix_world@r.pose.bones[driver].matrix).inverted()
    cache[name]=(driver,[inv@v for v in p],f)

def cached_world(name):
    driver,p,f=cache[name];m=r.matrix_world@r.pose.bones[driver].matrix
    return [m@v for v in p],f

probe_file=E/'probe.json'
if not probe_file.exists():
    sweep={'L':{},'R':{}};rows=[]
    for frame in range(1,241):
        s.frame_set(frame);bpy.context.view_layer.update()
        p,f=cached_world('Pelvic cradle');body=BVHTree.FromPolygons(p,f)
        to_rest=r.matrix_world@r.data.bones['pelvis'].matrix_local@(r.matrix_world@r.pose.bones['pelvis'].matrix).inverted()
        hits={}
        for side in ['L','R']:
            for kind in ['Thigh guard','Donor thigh']:
                name=kind+' '+side;p,f=cached_world(name)
                hits[name]=len(body.overlap(BVHTree.FromPolygons(p,f)))
                for point in p:
                    v=to_rest@point
                    if v.z>.925*F:
                        key=tuple(round(c,5) for c in v)
                        sweep[side][key]=list(v)
        rows.append({'frame':frame,'crossings':hits})
    probe={'source_sha256':EXPECTED,'frames':rows,'margin_m':.002,
           'sweep_points':{side:list(points.values()) for side,points in sweep.items()}}
    probe['bounds']={side:{'min':[min(p[i] for p in pts.values()) for i in range(3)],
                          'max':[max(p[i] for p in pts.values()) for i in range(3)]} for side,pts in sweep.items()}
    probe_file.write_text(json.dumps(probe,indent=2))
else:probe=json.loads(probe_file.read_text())
assert probe['source_sha256']==EXPECTED
print('HIP_PROBE',json.dumps({'bounds':probe['bounds'],
    'crossing_frames':{n:sum(bool(row['crossings'][n]) for row in probe['frames']) for n in names[1:]}}),flush=True)
if '--apply' not in sys.argv:sys.exit(0)

for side in ['L','R']:
    bounds=probe['bounds'][side]
    assert bounds['max'][2]+.002<1.10*F,'Stop: pocket exceeds lower joint region'
    assert (bounds['min'][0]-.002>.035*F if side=='L' else bounds['max'][0]+.002<-.035*F),'Stop: central web would be cut'

def hull(points):
    bm=bmesh.new()
    for p in points:bm.verts.new(p)
    bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
    loose=[v for v in bm.verts if not v.link_faces]
    if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    return bm

bpy.ops.object.select_all(action='DESELECT');pelvis.select_set(True);bpy.context.view_layer.objects.active=pelvis
r.data.pose_position='REST';bpy.context.view_layer.update()
# Bake the existing manufactured edge treatment first. Leaving a 12 mm bevel
# after subtraction would refill the new clearance pockets with fillets.
for mod in list(pelvis.modifiers):
    if mod.type in {'BEVEL','WEIGHTED_NORMAL'}:bpy.ops.object.modifier_apply(modifier=mod.name)
pocket_records=[]
for side in ['L','R']:
    first=hull(probe['sweep_points'][side]);corners=[v.co.copy() for v in first.verts];first.free()
    expanded=[p+Vector(tuple(sign*.002 for sign in signs)) for p in corners for signs in itertools.product([-1,1],repeat=3)]
    bm=hull(expanded);mesh=bpy.data.meshes.new('Temporary hip sweep '+side);bm.to_mesh(mesh);bm.free()
    cutter=bpy.data.objects.new('Temporary hip clearance '+side,mesh);s.collection.objects.link(cutter)
    mod=pelvis.modifiers.new('Measured hip pocket '+side,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    while list(pelvis.modifiers).index(mod)>0:bpy.ops.object.modifier_move_up(modifier=mod.name)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    pocket_records.append({'side':side,'margin_m':.002,'sweep_bounds':probe['bounds'][side]})
    bpy.data.objects.remove(cutter,do_unlink=True)
    bpy.data.meshes.remove(mesh)
# New Boolean vertices must inherit the SAME rigid pelvis driver.
pelvis.vertex_groups.clear();g=pelvis.vertex_groups.new(name='pelvis');g.add(list(range(len(pelvis.data.vertices))),1,'REPLACE')
pelvis['geometry_origin']='Original casing with measured lower hip sweep pockets'
r.data.pose_position='POSE';bpy.context.view_layer.update()
# Boolean operands without materials may append an unused empty slot.
# Remove only appended empty slots; original assignments remain untouched.
while len(pelvis.data.materials)>len(materials_before):
    index=len(pelvis.data.materials)-1
    assert pelvis.data.materials[index] is None
    assert not any(p.material_index==index for p in pelvis.data.polygons)
    pelvis.data.materials.pop(index=index)
assert tuple(m.name for m in pelvis.data.materials)==materials_before
assert other_signature()==before and animation_signature()==anim_before
assert {b.name:tuple(tuple(row) for row in b.matrix_local) for b in r.data.bones}==rest_before

rows=[]
for frame in range(1,241):
    s.frame_set(frame);bpy.context.view_layer.update()
    p,f=evaluated(pelvis);body=BVHTree.FromPolygons(p,f);hits={}
    for name in names[1:]:
        p,f=cached_world(name);count=len(body.overlap(BVHTree.FromPolygons(p,f)))
        if count:hits[name]=count
    rows.append({'frame':frame,'hip_surface_crossings':hits})
failures=[row for row in rows if row['hip_surface_crossings']]
s.frame_set(110)
s['status']='HIP_POCKET_KINEMATIC_REVIEW' if not failures else 'HIP_POCKET_CLEARANCE_FAIL'
s['physical_handoff_authorized']=False
bpy.ops.wm.save_as_mainfile(filepath=str(P));digest=sha(P)
record={'source_sha256':EXPECTED,'candidate_sha256':digest,'claim_class':'OBSERVED',
        'result':'HIP_SURFACE_SWEEP_PASS' if not failures else 'HIP_SURFACE_SWEEP_FAIL',
        'changed_meshes':['Pelvic cradle'],'other_geometry_materials_unchanged':other_signature()==before,
        'animation_unchanged':animation_signature()==anim_before,'animation_signature':anim_before,
        'rest_bones_unchanged':True,'pockets':pocket_records,'frames':rows,
        'physical_handoff_authorized':False,'limits':['measured motion envelope only','no structural strength or force certification']}
(E/'measurements.json').write_text(json.dumps(record,indent=2))
assert sha(S)==EXPECTED
print('HIP_CLEARANCE_RESULT',json.dumps({'candidate_sha256':digest,'checked_frames':len(rows),'crossing_frames':len(failures)}),flush=True)
if failures:raise RuntimeError('Hip pocket failed — preserved diagnostic; no promotion')
