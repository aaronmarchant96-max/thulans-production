"""Pose-only carry study on the visually accepted V12 hand and frozen suit.

User authorized full-body animation preview; physical load gate remains open.
No topology, materials, rest bones, tool geometry or existing camera edits.
"""
import ast
import hashlib
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

R=Path('/home/aaron/animation/thulans-production')
S=R/'blender/candidates/varek-articulated-grip-v12.blend'
transfer_fix='--transfer-fix' in sys.argv
upright='--upright' in sys.argv or transfer_fix
tag='varek-carry-v13-transfer' if transfer_fix else ('varek-carry-v13-upright' if upright else 'varek-carry-v13')
P=R/('blender/candidates/'+tag+'.blend')
E=R/('evidence/'+tag)
STEP=.12 if upright else .28
DROP=.018 if upright else .065
SWAY=.085 if upright else .14
TOE_CLEARANCE=.018 if upright else .075
EXPECTED='c420feaa0d01d0604ce466cc8fca8f7d032fe01f3c761083471484702fdc81ad'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(S)==EXPECTED and not P.exists() and not E.exists()
E.mkdir()
bpy.ops.wm.open_mainfile(filepath=str(S))
scene=bpy.context.scene;rig=bpy.data.objects['Varek simple articulation']
parts=bpy.data.collections['Varek_Editable_Parts']
F=json.loads((R/'evidence/varek-simplified-donor-v2/build.json').read_text())['normalization_factor']
V=lambda p:Vector(p)*F
tree=ast.parse((R/'tools/rig_varek_salvage_v4.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='solve'],type_ignores=[]),'two-link-solver','exec'))

def geometry_signature():
    return hashlib.sha256(repr(sorted((o.name,tuple(tuple(v.co) for v in o.data.vertices),
        tuple(tuple(p.vertices) for p in o.data.polygons),tuple(m.name if m else None for m in o.data.materials))
        for o in parts.objects if o.type=='MESH')).encode()).hexdigest()

geom_before=geometry_signature()
rest={b.name:b.matrix_local.copy() for b in rig.data.bones}
scene.frame_set(60);bpy.context.view_layer.update()
closed={b.name:b.matrix.copy() for b in rig.pose.bones}
grip_relation=closed['hand.R'].inverted()@closed['tool']
digits=[n for n in closed if n.startswith(('finger.','thumb.'))]
digit_relation={n:closed['hand.R'].inverted()@closed[n] for n in digits}
hand_direction=(rig.pose.bones['hand.R'].tail-rig.pose.bones['hand.R'].head).normalized()

# Frozen evaluated meshes in driver-local space, including bevels. The hand's
# relative digit pose stays closed, so its complete evaluated mesh is rigid in
# hand.R space throughout this carry study.
cache={}
for o in parts.objects:
    if o.type!='MESH' or o.get('rigid_driver_bone') not in closed:continue
    driver=o['rigid_driver_bone']
    e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=e.to_mesh()
    inv=(rig.matrix_world@closed[driver]).inverted()
    cache[o.name]=(driver,[inv@e.matrix_world@v.co for v in mesh.vertices],
                   [list(p.vertices) for p in mesh.polygons])
    e.to_mesh_clear()
tool_names=[n for n,(d,_,_) in cache.items() if d=='tool']
pairs=[]
for side in ['L','R']:
    for arm in ['Donor upper arm ','Donor forearm ','Donor rescue hand ']:
        for obstacle in ['Continuous forged yoke','Thoracic protective hull','Thoracic rail '+side]:
            pairs.append((arm+side,obstacle))
    pairs += [('Donor shin '+side,'Thigh guard '+side),
              ('Pelvic cradle','Thigh guard '+side)]
    for tool in tool_names:
        for lower in ['Anchor sole ','Forged foot housing ','Donor shin ','Thigh guard ']:
            pairs.append((tool,lower+side))
for tool in tool_names:pairs.append(('Donor forearm R',tool))
pair_objects=set(n for pair in pairs for n in pair)

def world_points(name,poses):
    driver,pts,_=cache[name]
    m=rig.matrix_world@poses[driver]
    return [m@p for p in pts]

def crossings(poses):
    trees={n:BVHTree.FromPolygons(world_points(n,poses),cache[n][2]) for n in pair_objects}
    return {a+' / '+b:len(trees[a].overlap(trees[b])) for a,b in pairs}

baseline_hits=crossings(closed)
for o in [rig]+[o for o in parts.objects if o.name.startswith('Calf ram ')]:o.animation_data_clear()
for b in rig.pose.bones:b.rotation_mode='QUATERNION'
foot_rest={side:rig.data.bones['foot.'+side].head_local.copy() for side in ['L','R']}
step_specs=[('L',0,-STEP),('R',0,-2*STEP),('L',-STEP,-3*STEP),('R',-2*STEP,-3*STEP)]

def smooth(t):
    t=min(1.,max(0.,t));return t*t*(3-2*t)

def segment(poses,name,a,b):
    bone=rig.data.bones[name]
    q=(bone.tail_local-bone.head_local).rotation_difference(b-a)
    poses[name]=Matrix.Translation(a)@q.to_matrix().to_4x4()@rest[name].to_3x3().to_4x4()

def around(point,rotation):return Matrix.Translation(point)@rotation@Matrix.Translation(-point)

rows=[]
try:
    for frame in range(1,241):
        scene.frame_set(frame)
        activity=smooth((frame-1)/35)*(1-smooth((frame-205)/35))
        bx=by=rise=0.;support=None;moving=None;swing_t=0.;arm_swing=0.
        foot_delta={'L':0.,'R':0.};foot_lift={'L':0.,'R':0.}
        if 37<=frame<=204:
            k=(frame-37)//42;u=((frame-37)%42)/41
            moving,start,end=step_specs[k];support='R' if moving=='L' else 'L'
            for old_side,_,old_end in step_specs[:k]:foot_delta[old_side]=old_end
            mean0=sum(foot_delta.values())/2
            support_y=foot_delta[support]+(.02 if transfer_fix else -.04)
            transfer=smooth(u/.22);landing=smooth((u-.76)/.24)
            bx=(SWAY if support=='L' else -SWAY)*transfer*(1-landing)
            mean1=(foot_delta[support]+end)/2
            by=(mean0+(support_y-mean0)*transfer)*(1-landing)+mean1*landing
            swing_t=min(1.,max(0.,(u-.22)/.54))
            foot_delta[moving]=start+(end-start)*smooth(swing_t)
            foot_lift[moving]=TOE_CLEARANCE*math.sin(math.pi*swing_t)**2
            rise=(.002 if upright else .006)*math.sin(math.pi*swing_t)**2
            arm_swing=(.07 if moving=='L' else -.07)*math.sin(math.pi*u)**2
            if not .22<u<.76:support=None
        elif frame>204:
            by=-3*STEP;foot_delta={'L':-3*STEP,'R':-3*STEP}
        drop=DROP*activity-rise
        body=(Matrix.Translation(V((bx,by,-drop)))
              @around(V((0,.03,1.035)),Matrix.Rotation(math.radians(.5 if upright else 2)*activity,4,'X')))
        poses={n:body@m for n,m in rest.items()}
        # Small opposite arm swing; same rigid parts and original joint axes.
        left=around(rig.data.bones['upper_arm.L'].head_local,Matrix.Rotation(arm_swing,4,'X'))
        for name in ['upper_arm.L','forearm.L','hand.L']:poses[name]=body@left@rest[name]
        head_p=rig.data.bones['head'].head_local
        poses['head']=body@around(head_p,Matrix.Rotation(.09*(1-activity),4,'X'))@rest['head']
        for side in ['L','R']:
            ankle=foot_rest[side]+V((0,foot_delta[side],foot_lift[side]))
            hip=poses['thigh.'+side].translation.copy()
            knee=solve(hip,ankle,rig.data.bones['thigh.'+side].length,
                       rig.data.bones['shin.'+side].length,hip+Vector((0,-1,0)))
            segment(poses,'thigh.'+side,hip,knee)
            segment(poses,'shin.'+side,knee,ankle)
            poses['foot.'+side]=Matrix.Translation(ankle-foot_rest[side])@rest['foot.'+side]
        # Upright maul clear of the boots, independently of side-to-side torso
        # motion. Hand and digits retain the exact V12 closed relationship.
        carry_delta=V((-.10*activity,by,.16*activity))
        poses['hand.R']=Matrix.Translation(carry_delta)@closed['hand.R']
        poses['tool']=poses['hand.R']@grip_relation
        for name in digits:poses[name]=poses['hand.R']@digit_relation[name]
        shoulder=poses['upper_arm.R'].translation.copy()
        wrist=poses['hand.R'].translation.copy()
        elbow=solve(shoulder,wrist,rig.data.bones['upper_arm.R'].length,
                    rig.data.bones['forearm.R'].length,shoulder+Vector((0,0,-1)))
        segment(poses,'upper_arm.R',shoulder,elbow)
        segment(poses,'forearm.R',elbow,wrist)
        wrist_angle=math.degrees((wrist-elbow).angle(hand_direction))
        assert wrist_angle<45,(frame,'wrist deflection',wrist_angle)
        for pb in rig.pose.bones:
            rb=pb.bone
            pb.matrix_basis=(rest[pb.name].inverted()@rest[rb.parent.name]@poses[rb.parent.name].inverted()@poses[pb.name]
                             if rb.parent else rest[pb.name].inverted()@poses[pb.name])
        bpy.context.view_layer.update()
        for n,m in poses.items():
            assert max(abs(rig.pose.bones[n].matrix[i][j]-m[i][j]) for i in range(4) for j in range(4))<.00001,(frame,n,'pose matrix')
        # Existing calf rams telescope without scaling their fixed-length meshes.
        strokes={}
        for side,sign in [('L',1),('R',-1)]:
            upper=poses['shin.'+side]@rest['shin.'+side].inverted()@V((sign*.27,.21,.49))
            lower=poses['foot.'+side]@rest['foot.'+side].inverted()@V((sign*.27,.21,.20))
            axis=(upper-lower).normalized();distance=(upper-lower).length
            assert .20*F<=distance<=.355*F,(frame,side,'calf stroke',distance)
            strokes[side]=distance
            for name,mid in [('Calf ram body '+side,upper-axis*.10*F),('Calf ram rod '+side,lower+axis*.08*F)]:
                o=bpy.data.objects[name];o.location=mid;o.rotation_mode='QUATERNION';o.rotation_quaternion=axis.to_track_quat('Z','Y')
                o.keyframe_insert('location');o.keyframe_insert('rotation_quaternion')
        feet={s:world_points('Anchor sole '+s,poses) for s in ['L','R']}
        sole_z={s:min(p.z for p in pts) for s,pts in feet.items()}
        for side,z in sole_z.items():assert abs(z-foot_lift[side]*F)<.00025,(frame,side,'sole height',z)
        tool_z=min(p.z for name in tool_names for p in world_points(name,poses))
        assert tool_z>=-.00025,(frame,'tool floor',tool_z)
        proxy_inside=None
        if support:
            # Pelvis point is a geometric staging proxy, NOT a mass-based COM.
            proxy=poses['pelvis'].translation;pts=feet[support]
            proxy_inside=all(min(p[i] for p in pts)-.005<=proxy[i]<=max(p[i] for p in pts)+.005 for i in [0,1])
            assert proxy_inside,(frame,'pelvis projection outside support sole')
        hit=crossings(poses)
        new={k:v for k,v in hit.items() if v and not baseline_hits[k]}
        rows.append({'frame':frame,'single_support':support,'sole_min_z_m':sole_z,
                     'ankles_world':{s:list(poses['foot.'+s].translation) for s in ['L','R']},
                     'tool_min_z_m':tool_z,'wrist_deflection_deg':wrist_angle,
                     'calf_socket_distance_m':strokes,'pelvis_proxy_inside_support':proxy_inside,
                     'new_surface_crossings':new})
        for pb in rig.pose.bones:
            for channel in ['location','rotation_quaternion','scale']:pb.keyframe_insert(channel)
        if frame%24==0:print('CARRY_FRAME',frame,'new crossings',new,flush=True)
except Exception as error:
    last=rows[-1]['frame'] if rows else 1
    scene.frame_set(last);scene.frame_end=last
    scene['status']='FAILED_CARRY_DIAGNOSTIC';scene['physical_handoff_authorized']=False
    failed_candidate=E/'failure-stop.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(failed_candidate))
    (E/'failure.json').write_text(json.dumps({'result':'FAIL','frame':frame,'error':str(error),'frames_completed':rows,
        'source_sha256':EXPECTED,'candidate_saved':False,'failure_diagnostic_sha256':sha(failed_candidate)},indent=2))
    raise

for o in [rig]+[o for o in parts.objects if o.name.startswith('Calf ram ')]:
    if o.animation_data and o.animation_data.action:
        for layer in o.animation_data.action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        for key in curve.keyframe_points:key.interpolation='LINEAR'
scene.frame_start=1;scene.frame_end=240;scene.render.fps=24
scene.timeline_markers.clear()
for f,name in [(1,'GRIPPED'),(36,'LIFTED'),(37,'STEP L'),(79,'STEP R'),(121,'STEP L'),(163,'CLOSE STANCE'),(205,'PLANT'),(240,'REST')]:
    scene.timeline_markers.new(name,frame=f)
scene['status']='FULL_BODY_CARRY_KINEMATIC_REVIEW'
scene['physical_handoff_authorized']=False
scene['continuous_motion_validated']=False
scene.frame_set(110)
assert geometry_signature()==geom_before and sha(S)==EXPECTED
assert all(tuple(tuple(row) for row in rig.data.bones[n].matrix_local)==tuple(tuple(row) for row in m) for n,m in rest.items())
bpy.ops.wm.save_as_mainfile(filepath=str(P));digest=sha(P)
report={'candidate_sha256':digest,'source_sha256':EXPECTED,'claim_class':'OBSERVED',
        'pose_parameters':{'step_m_pre_normalization':STEP,'drop_m':DROP,'sway_m':SWAY,'toe_clearance_m':TOE_CLEARANCE,'support_y_bias_m':.02 if transfer_fix else -.04},
        'result':'KINEMATIC_REVIEW_ONLY','geometry_materials_rest_bones_unchanged':True,
        'physical_handoff_authorized':False,'frames':rows,
        'baseline_surface_crossings':{k:v for k,v in baseline_hits.items() if v},
        'limits':['surface checks, not volume containment','pelvis projection is not mass-based COM',
                  'tool is keyed, no physical load proof','integer frames, not continuous sweep'],
        'scope_authority':'Aaron requested full animation after approving V12 preview; physics gate not waived'}
(E/'measurements.json').write_text(json.dumps(report,indent=2))
print('CARRY_FROZEN',digest,'new_collision_frames',sum(bool(r['new_surface_crossings']) for r in rows),flush=True)
