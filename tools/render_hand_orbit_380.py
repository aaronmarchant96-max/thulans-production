"""20-angle failure diagnostic; review-only isolation, never save the blend."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('/home/aaron/animation/thulans-production');P=R/'blender/candidates/varek-hand-v10.blend';E=R/'evidence/varek-hand-v10/orbit-380'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='9bf78724a82a0573e0c816597ed278e7214975e3aebdb027de63aa7084df810d'
assert sha(P)==expected and not E.exists(), 'Source drift or existing evidence'
E.mkdir();bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;s.frame_set(36)
r=bpy.data.objects['Varek simple articulation'];F=json.loads((R/'evidence/varek-simplified-donor-v2/build.json').read_text())['normalization_factor']
grip=r.pose.bones['hand.R'].matrix@r.data.bones['hand.R'].matrix_local.inverted()@(Vector((-.59,-.04,1))*F)
wrist=r.pose.bones['hand.R'].head.copy();target=(grip+wrist)/2+Vector((0,0,.04))
hidden=[]
for o in bpy.data.collections['Varek_Editable_Parts'].objects:
    driver=o.get('rigid_driver_bone')
    if driver not in ['upper_arm.R','forearm.R','hand.R','tool']:
        o.hide_render=True;hidden.append(o.name)
cam=s.camera;cam.data.type='ORTHO';cam.data.ortho_scale=.70
s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True
s.render.resolution_x=480;s.render.resolution_y=480;s.render.resolution_percentage=100
# Camera-relative diagnostic fill makes the reverse surfaces inspectable.
light=bpy.data.lights.new('Review orbit fill','AREA');light.energy=100;light.shape='DISK';light.size=1.5
lamp=bpy.data.objects.new('Review orbit fill',light);s.collection.objects.link(lamp)
record={'candidate_sha256':expected,'claim_class':'OBSERVED','status':'REJECTED_CANDIDATE_DIAGNOSTIC_ONLY','frame':36,'angles_degrees':list(range(0,381,20)),'review_only_hidden_objects':hidden,'review_only_lighting':'one camera-relative area fill; original lights retained','camera_target_m':list(target),'samples':8,'renders':[]}
(E/'manifest.json').write_text(json.dumps(record,indent=2))
for i,deg in enumerate(record['angles_degrees']):
    theta=math.radians(deg-120);offset=Vector((1.2*math.cos(theta),1.2*math.sin(theta),.20))
    cam.location=target+offset;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    lamp.location=cam.location+Vector((0,0,.35));lamp.rotation_euler=(target-lamp.location).to_track_quat('-Z','Y').to_euler()
    file=E/f'{i:03d}.png';s.render.filepath=str(file);bpy.ops.render.render(write_still=True)
    record['renders'].append({'angle_degrees':deg,'file':file.name,'sha256':sha(file)})
    print('ORBIT_ANGLE_COMPLETE',deg,flush=True)
assert sha(P)==expected;record['candidate_unchanged']=True
(E/'manifest.json').write_text(json.dumps(record,indent=2))
print('ORBIT_COMPLETE',len(record['renders']),flush=True)
