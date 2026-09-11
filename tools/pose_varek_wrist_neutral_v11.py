"""Pose-only failure diagnostic: straight wrist, hand free of parked hammer."""
import bpy,ast,json,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('/home/aaron/animation/thulans-production');S=R/'blender/candidates/varek-hand-v10.blend';P=R/'blender/candidates/varek-wrist-neutral-v11.blend';E=R/'evidence/varek-wrist-neutral-v11'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='9bf78724a82a0573e0c816597ed278e7214975e3aebdb027de63aa7084df810d'
assert sha(S)==expected and not P.exists() and not E.exists();E.mkdir()
bpy.ops.wm.open_mainfile(filepath=str(S));scene=bpy.context.scene;rig=bpy.data.objects['Varek simple articulation'];parts=bpy.data.collections['Varek_Editable_Parts'].objects
signature=lambda:hashlib.sha256(repr(sorted((o.name,tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons)) for o in parts if o.type=='MESH')).encode()).hexdigest()
baseline=signature();scene.frame_set(1)
for o in [rig]+[o for o in parts if o.name.startswith('Calf ram ')]:o.animation_data_clear()
for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()
F=json.loads((R/'evidence/varek-simplified-donor-v2/build.json').read_text())['normalization_factor'];V=lambda v:Vector(v)*F
tree=ast.parse((R/'tools/rig_varek_salvage_v4.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'set_segment','solve','evaluated_vertices'}],type_ignores=[]),'pose-helpers','exec'),globals())
wrist=V((-.62,-.38,1.37));upper=rig.pose.bones['upper_arm.R'];a=upper.head.copy()
elbow=solve(a,wrist,upper.bone.length,rig.data.bones['forearm.R'].length,V((-1.2,-.10,1.50)))
set_segment('upper_arm.R',a,elbow);set_segment('forearm.R',elbow,wrist)
# Zero local wrist rotation: preserve the forearm-to-hand rest relationship.
rig.pose.bones['hand.R'].matrix_basis=Matrix.Identity(4);bpy.context.view_layer.update()
forearm=rig.pose.bones['forearm.R'];hand=rig.pose.bones['hand.R']
angle=math.degrees((forearm.tail-forearm.head).angle(hand.tail-hand.head))
assert angle<5,angle
feet={side:min(v.z for v in evaluated_vertices(bpy.data.objects['Anchor sole '+side])) for side in ['L','R']}
tool_min=min(v.z for o in parts if o.type=='MESH' and o.get('rigid_driver_bone')=='tool' for v in evaluated_vertices(o))
assert all(abs(z)<.00025 for z in feet.values()) and abs(tool_min)<.00025
assert baseline==signature();scene.frame_start=1;scene.frame_end=1;scene.timeline_markers.clear()
scene['status']='REJECTED_HAND_POSE_DIAGNOSTIC';scene['physical_handoff_authorized']=False
scene.camera=bpy.data.objects['Front threequarter'];scene.render.resolution_x=640;scene.render.resolution_y=800;scene.cycles.samples=24
bpy.ops.wm.save_as_mainfile(filepath=str(P));frozen=sha(P)
record={'candidate_sha256':frozen,'source_sha256':expected,'claim_class':'OBSERVED','geometry_unchanged':baseline==signature(),'wrist_local_rotation':'rest / identity','forearm_hand_axis_angle_degrees':angle,'sole_min_z_m':feet,'hammer_min_z_m':tool_min,'result':'POSE_DIAGNOSTIC_ONLY','physics_gate':'STILL_BLOCKED','notes':['Hammer is parked separately; no gripping claim','Existing closed finger geometry unchanged; not an open-hand pose','No human approval or real-world-function claim']}
(E/'measurements.json').write_text(json.dumps(record,indent=2))
scene.render.filepath=str(E/'full.png');bpy.ops.render.render(write_still=True)
target=(hand.head+hand.tail)/2;cam=scene.camera;cam.data.ortho_scale=.65;scene.render.resolution_x=640;scene.render.resolution_y=640
for name,offset in [('wrist-front',(-1.2,-1.8,.20)),('wrist-side',(-1.8,.5,.15))]:
    cam.location=target+Vector(offset);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(E/(name+'.png'));bpy.ops.render.render(write_still=True)
assert sha(S)==expected and sha(P)==frozen
print('POSE_DIAGNOSTIC_READY',flush=True)
