"""Bounded hammer handling study; static design preserved, no walking claim."""
import bpy, math, json, hashlib, ast
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path('/home/aaron/animation/thulans-production')
SOURCE=ROOT/'blender/candidates/varek-simplified-rig-v4.blend'
OUT=ROOT/'blender/candidates/varek-hammer-study-v5.blend'
REVIEW=ROOT/'evidence/varek-hammer-study-v5'
EXPECTED='775960dd420ca8832964ef1f3d624ef1516e596375e77740f95da5232c6073a7'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(SOURCE)==EXPECTED
assert not OUT.exists(), 'Do not overwrite a frozen candidate'
REVIEW.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene; rig=bpy.data.objects['Varek simple articulation']
collection=bpy.data.collections['Varek_Editable_Parts']
F=json.loads((ROOT/'evidence/varek-simplified-donor-v2/build.json').read_text())['normalization_factor']
V=lambda a:Vector(a)*F
# Reuse only audited pure helper definitions, never the previous build entrypoint.
tree=ast.parse((ROOT/'tools/rig_varek_salvage_v4.py').read_text())
helpers=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'evaluated_vertices','set_segment','solve'}],type_ignores=[])
exec(compile(helpers,'v4-helper-definitions','exec'),globals())
scene.frame_set(1)
for o in [rig]+[o for o in collection.objects if o.name.startswith('Calf ram ')]:
    o.animation_data_clear()
for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()
signature=lambda:hashlib.sha256(repr([(o.name,[tuple(v.co) for v in o.data.vertices]) for o in collection.objects if o.type=='MESH']).encode()).hexdigest()
before=signature()
hand_rest=rig.data.bones['hand.R'].matrix_local.copy()
contact_rest=V((-.59,-.105,.985))
tool_contact_rest=V((-.86,-.17,1.24))
delta_rotation=Matrix.Rotation(-math.pi/2,4,'Y')
contact_offset=delta_rotation.to_3x3()@(contact_rest-rig.data.bones['hand.R'].head_local)
tool_objects=[o for o in collection.objects if o.get('rigid_driver_bone')=='tool']
rows=[]
def smooth(t):return t*t*(3-2*t)
for frame in range(1,73):
    scene.frame_set(frame)
    for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
    # Twelve-frame settle, slow lift, hold, deliberate return, final contact hold.
    lift=0 if frame<=12 else (.18*smooth((frame-12)/24) if frame<=36 else (.18 if frame<=44 else (.18*(1-smooth((frame-44)/20)) if frame<=64 else 0)))
    contact=V((-.66,-.32,1.24+lift)); wrist=contact-contact_offset
    bpy.context.view_layer.update()
    upper=rig.pose.bones['upper_arm.R']; a=upper.head.copy()
    elbow=solve(a,wrist,upper.bone.length,rig.data.bones['forearm.R'].length,V((-1.2,-.12,1.5)))
    set_segment('upper_arm.R',a,elbow);set_segment('forearm.R',elbow,wrist)
    rig.pose.bones['hand.R'].matrix=Matrix.Translation(wrist)@delta_rotation@hand_rest.to_3x3().to_4x4()
    rig.pose.bones['tool'].matrix=Matrix.Translation(contact-tool_contact_rest)@rig.data.bones['tool'].matrix_local
    rig.pose.bones['head'].rotation_mode='QUATERNION'
    rig.pose.bones['head'].rotation_quaternion=Matrix.Rotation(.06*math.sin(math.pi*(frame-1)/71),4,'Y').to_quaternion()
    bpy.context.view_layer.update()
    actual_hand=rig.pose.bones['hand.R'].matrix@hand_rest.inverted()@contact_rest
    actual_tool=rig.pose.bones['tool'].matrix@rig.data.bones['tool'].matrix_local.inverted()@tool_contact_rest
    gap=(actual_hand-actual_tool).length
    feet={s:min(v.z for v in evaluated_vertices(bpy.data.objects['Anchor sole '+s])) for s in ['L','R']}
    tool_z=min(v.z for o in tool_objects if o.type=='MESH' for v in evaluated_vertices(o))
    assert gap<1e-5, ('grip transform drift',frame,gap)
    assert all(abs(z)<.00025 for z in feet.values()), ('feet',frame,feet)
    assert tool_z>=-.00025, ('hammer floor',frame,tool_z)
    for p in rig.pose.bones:
        p.rotation_mode='QUATERNION'
        for channel in ['location','rotation_quaternion','scale']:p.keyframe_insert(channel)
    rows.append({'frame':frame,'grip_reference_gap_m':gap,'sole_min_z_m':feet,'tool_min_z_m':tool_z})
for layer in rig.animation_data.action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for curve in bag.fcurves:
                for key in curve.keyframe_points:key.interpolation='LINEAR'
scene.timeline_markers.clear()
for f,label in [(1,'GRIPPED / FLOOR'),(36,'LIFT'),(44,'HOLD'),(64,'PLANT')]:scene.timeline_markers.new(label,frame=f)
scene.frame_start=1;scene.frame_end=72;scene.render.fps=24
scene['status']='HAMMER_HANDLING_STUDY';scene['continuous_motion_validated']=False
scene['grip_validation']='REFERENCE_TRANSFORMS_ONLY; physical finger contact requires image review'
scene.camera=bpy.data.objects['Front threequarter']
scene.render.resolution_x=640;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.engine='CYCLES';scene.cycles.samples=32
scene.frame_set(36)
assert before==signature() and sha(SOURCE)==EXPECTED
bpy.ops.wm.save_as_mainfile(filepath=str(OUT)); frozen=sha(OUT)
record={'source_sha256':EXPECTED,'candidate_sha256':frozen,'geometry_unchanged':before==signature(),'claim_class':'OBSERVED','scope':'72 integer frames: reference grip alignment, soles and tool floor; no physical finger-contact or full collision certification','frames':rows,'human_review':'PENDING','result':'KINEMATIC_CHECKS_PASS_VISUAL_REVIEW_PENDING'}
(REVIEW/'measurements.json').write_text(json.dumps(record,indent=2))
scene.render.filepath=str(REVIEW/'lift.png');bpy.ops.render.render(write_still=True)
assert sha(OUT)==frozen and sha(SOURCE)==EXPECTED
print('GRIP_REVIEW_READY',str(OUT),flush=True)
