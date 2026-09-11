"""Read-only saved-state grip/geometry checks; does not grant visual approval."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('/home/aaron/animation/thulans-production');E=R/'evidence/varek-grip-v6'
P=R/'blender/candidates/varek-grip-v6.blend';S=R/'blender/candidates/varek-hammer-study-v5.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record=json.loads((E/'measurements.json').read_text());frozen=sha(P)
assert frozen==record['candidate_sha256'] and sha(S)==record['source_sha256']
def geometry():
    return hashlib.sha256(repr(sorted((o.name,tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons),tuple(m.name if m else None for m in o.data.materials)) for o in bpy.data.collections['Varek_Editable_Parts'].objects if o.type=='MESH')).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(S));baseline=geometry()
bpy.ops.wm.open_mainfile(filepath=str(P));assert geometry()==baseline
rig=bpy.data.objects['Varek simple articulation'];scene=bpy.context.scene
F=json.loads((R/'evidence/varek-simplified-donor-v2/build.json').read_text())['normalization_factor']
g=Vector((-.59,-.04,1.00))*F;t=Vector((-.86,-.17,1.24))*F
def minimum_z(o):
    ob=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ob.to_mesh()
    z=min((ob.matrix_world@v.co).z for v in m.vertices);ob.to_mesh_clear();return z
rows=[]
for f in range(1,73):
    scene.frame_set(f);bpy.context.view_layer.update()
    a=rig.pose.bones['hand.R'].matrix@rig.data.bones['hand.R'].matrix_local.inverted()@g
    b=rig.pose.bones['tool'].matrix@rig.data.bones['tool'].matrix_local.inverted()@t
    gap=(a-b).length;feet=[minimum_z(bpy.data.objects['Anchor sole '+s]) for s in ['L','R']]
    head_z=minimum_z(bpy.data.objects['Fault Maul head'])
    assert gap<1e-5 and all(abs(z)<.00025 for z in feet) and head_z>=-.00025
    rows.append({'frame':f,'grip_reference_gap_m':gap,'sole_z_m':feet,'hammer_head_min_z_m':head_z})
assert sha(P)==frozen and sha(S)==record['source_sha256']
(E/'saved-readback.json').write_text(json.dumps({'claim_class':'OBSERVED','candidate_sha256':frozen,'source_mesh_topology_coordinates_and_material_slots_identical':True,'frames_checked':len(rows),'frames':rows,'result':'SAVED_KINEMATIC_CHECKS_PASS','exclusions':['physical finger contact','full collision detection','between-frame motion','visual approval']},indent=2))
print('SAVED_KINEMATIC_CHECKS_PASS',len(rows),'frames',flush=True)
