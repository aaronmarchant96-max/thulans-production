"""Read frozen articulated candidate; measure joints/contact, optionally render.

No scene saves, no free-tool/engineering claims. All preview frames come from
the candidate's keyed animation, not an independently reconstructed pose.
"""
import argparse
import ast
import hashlib
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

parser=argparse.ArgumentParser()
parser.add_argument('--candidate',required=True,type=Path)
parser.add_argument('--evidence',required=True,type=Path)
parser.add_argument('--render',action='store_true')
a=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
R=Path('/home/aaron/animation/thulans-production')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
digest=sha(a.candidate)
assert not (a.evidence/'saved-readback.json').exists()
bpy.ops.wm.open_mainfile(filepath=str(a.candidate))
scene=bpy.context.scene
rig=bpy.data.objects['Varek simple articulation']
collection=bpy.data.collections['Varek_Editable_Parts']
F=json.loads((R/'evidence/varek-simplified-donor-v2/build.json').read_text())['normalization_factor']
tree=ast.parse((R/'tools/fit_varek_grip_v7.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='surface'],type_ignores=[]),'bvh-helper','exec'))
hand=bpy.data.objects['Donor rescue hand R']
rb=rig.data.bones['hand.R']
X0=(rb.tail_local-rb.head_local).normalized()
Y0=Vector((1,0,0));Z0=Y0.cross(X0)
H0=Matrix((X0,Y0,Z0)).transposed()
tool_parts=[o for o in collection.objects if o.type=='MESH' and o.get('rigid_driver_bone')=='tool']
rows=[]
for frame in range(scene.frame_start,scene.frame_end+1):
    scene.frame_set(frame);bpy.context.view_layer.update()
    joints={}
    for b in rig.pose.bones:
        if b.name.startswith(('finger.','thumb.')) and b.parent.name!='hand.R':
            joints[b.name]=(b.head-b.parent.tail).length
    wrist_gap=(rig.pose.bones['hand.R'].head-rig.pose.bones['forearm.R'].tail).length
    if max([wrist_gap]+list(joints.values()))>.00001:
        raise RuntimeError(('joint disconnected',frame,wrist_gap,joints))
    rows.append({'frame':frame,'wrist_gap_m':wrist_gap,'digit_joint_gaps_m':joints})
scene.frame_set(60);bpy.context.view_layer.update()
world=lambda p:rig.pose.bones['hand.R'].matrix@rb.matrix_local.inverted()@(rb.head_local+H0@(Vector(p)*F))
hb=surface(hand);tb=[surface(o) for o in tool_parts]
samples=[('palm',(.115,0,.018))]
ys=list(scene.get('grip_finger_rows',[-.045,.005,.055]))
for i,y in enumerate(ys):
    for j,deg in enumerate([-45,25,95]):
        t=math.radians(deg)
        samples.append((f'finger_{i}_{j}',(.115+.037*math.cos(t),y,.055+.037*math.sin(t))))
samples += [('thumb_proximal',(.081,.080,.055)),
            ('thumb_distal',(.115-.034*math.sin(math.radians(35)),.080,.055+.034*math.cos(math.radians(35))))]
contacts=[]
for label,p in samples:
    target=world(p)
    actual=hb.find_nearest(target)[0]
    distance=min(b.find_nearest(actual)[3] for b in tb)
    contacts.append({'pad':label,'pad_to_tool_gap_m':distance,'target_to_hand_m':(actual-target).length})
report={'claim_class':'OBSERVED','candidate_sha256':digest,'joint_frames':rows,
        'closed_pose_contact_samples':contacts,'contact_tolerance_m':.00075,
        'contact_samples_within_tolerance':all(r['pad_to_tool_gap_m']<=.00075 for r in contacts),
        'physical_handoff_authorized':False,'tool_motion':'KEYED, NOT FREE DYNAMICS',
        'limitations':['integer-frame joints only','sampled pad gaps, not full contact patches',
                       'no force/load or self-collision certification']}
(a.evidence/'saved-readback.json').write_text(json.dumps(report,indent=2))
print('SAVED_JOINT_FRAMES',len(rows),'CONTACT_SAMPLES',json.dumps(contacts),flush=True)
if a.render:
    out=a.evidence/'motion';assert not out.exists();out.mkdir()
    scene.render.engine='CYCLES';scene.cycles.samples=8
    scene.render.resolution_x=scene.render.resolution_y=480
    scene.render.resolution_percentage=100
    cam=scene.camera;cam.data.ortho_scale=.76
    # Fixed review camera: no orbit that could conceal a failed phase.
    target=world((.10,0,.045)) + Vector((0,0,.045))
    cam.location=target+Vector((-1.2,-1.8,.45))
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    frames=[]
    for index,frame in enumerate(range(1,169,3)):
        scene.frame_set(frame)
        file=out/f'{index:03d}.png'
        scene.render.filepath=str(file);bpy.ops.render.render(write_still=True)
        frames.append({'frame':frame,'file':file.name,'sha256':sha(file)})
    (out/'manifest.json').write_text(json.dumps({'candidate_sha256':digest,
        'source_fps':24,'render_sample_fps':8,'render_engine':'CYCLES','frames':frames,
        'status':'KINEMATIC DIAGNOSTIC, NOT PHYSICS APPROVAL'},indent=2))
assert sha(a.candidate)==digest
print('FROZEN_READBACK_COMPLETE',flush=True)
