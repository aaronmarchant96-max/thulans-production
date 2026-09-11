"""Rigid articulation study: three discrete poses, no claim of a finished walk."""
import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

ROOT=Path('/home/aaron/animation/thulans-production')
SOURCE=ROOT/'blender/candidates/varek-simplified-donor-v3.blend'
OUT=ROOT/'blender/candidates/varek-simplified-rig-v4.blend'
REVIEW=ROOT/'evidence/varek-simplified-rig-v4'
EXPECTED='22801e4e4195948b916be146d445c61ab3f55e14b0a3c7a88eda2fec56b4398a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(SOURCE)==EXPECTED
assert not OUT.exists()
REVIEW.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene; collection=bpy.data.collections['Varek_Editable_Parts']
F=json.loads((ROOT/'evidence/varek-simplified-donor-v2/build.json').read_text())['normalization_factor']
V=lambda xyz:Vector(xyz)*F

def evaluated_vertices(o):
    e=o.evaluated_get(bpy.context.evaluated_depsgraph_get()); m=e.to_mesh()
    result=[e.matrix_world@v.co for v in m.vertices]; e.to_mesh_clear(); return result

baseline={o.name:evaluated_vertices(o) for o in collection.objects if o.type=='MESH'}
raw_signature=lambda:hashlib.sha256(repr([(o.name,[tuple(v.co) for v in o.data.vertices]) for o in collection.objects if o.type=='MESH']).encode()).hexdigest()
mesh_before=raw_signature()
rest_objects={o.name:o.matrix_world.copy() for o in collection.objects}
data=bpy.data.armatures.new('Varek simple articulation')
rig=bpy.data.objects.new('Varek simple articulation',data); scene.collection.objects.link(rig); rig.show_in_front=True
bpy.ops.object.select_all(action='DESELECT'); rig.select_set(True); bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT')

def bone(name,a,b,parent=None):
    o=data.edit_bones.new(name); o.head=V(a); o.tail=V(b)
    if parent:o.parent=data.edit_bones[parent]

bone('root',(0,0,0),(0,0,.2))
bone('pelvis',(0,.03,1.035),(0,.03,1.25),'root')
bone('spine',(0,.03,1.25),(0,.03,1.92),'pelvis')
bone('head',(0,-.015,1.94),(0,-.015,2.18),'spine')
bone('tool',(-.86,-.17,.12),(-.86,-.17,1.36),'root')
for side,s in [('L',1),('R',-1)]:
    bone('upper_arm.'+side,(s*.48,0,1.82),(s*.585,0,1.42),'spine')
    bone('forearm.'+side,(s*.585,0,1.42),(s*.59,-.04,1.11),'upper_arm.'+side)
    bone('hand.'+side,(s*.59,-.04,1.11),(s*.59,-.065,.96),'forearm.'+side)
    bone('thigh.'+side,(s*.245,.015,1.035),(s*.245,.015,.65),'pelvis')
    bone('shin.'+side,(s*.245,.015,.65),(s*.26,.025,.235),'thigh.'+side)
    bone('foot.'+side,(s*.26,.025,.235),(s*.26,-.20,.235),'shin.'+side)
bpy.ops.object.mode_set(mode='OBJECT')
assign={}
central={'Pelvic cradle':'pelvis','Abdominal protection':'pelvis','Neck seat':'spine','Operator cell':'head','Visor recessed seat':'head','Amber protected slit':'head','Helmet brow':'head','Gren Skildus':'upper_arm.L','Inner oath':'spine','Thoracic protective hull':'spine','Continuous forged yoke':'spine','Integrated engine':'spine','Exhaust':'spine','Winch cable drum':'spine'}
groups={'upper_arm':['Shoulder pivot','Shoulder collar','Donor upper arm'], 'forearm':['Elbow axle','Donor forearm'],'hand':['Donor rescue hand','Wrist coupling','Gauntlet dorsal guard','Gauntlet knuckle bar'],'thigh':['Hip axle','Donor thigh','Thigh guard'],'shin':['Knee axle','Knee bearing','Donor shin'],'foot':['Forged foot housing','Anchor sole','Folded heel anchor'],'spine':['Thoracic rail','Dorsal rail','Yoke bearing']}
for o in collection.objects:
    name=o.name
    if name.startswith('Calf ram '):assign[name]='TELESCOPIC';continue
    driver=central.get(name)
    if name.startswith(('Maul ','Fault Maul','Forged oath collar')):driver='tool'
    if name.startswith(('Cooling louvre','Winch flange')):driver='spine'
    for region,prefixes in groups.items():
        for side in ['L','R']:
            if any(name==prefix+' '+side for prefix in prefixes):driver=region if region=='spine' else region+'.'+side
    if driver is None:raise RuntimeError('Unclassified module: '+name)
    if name.startswith(('Donor ','Gauntlet ')) and driver in ['spine','pelvis','root']:raise RuntimeError('Limb assigned centrally')
    assign[name]=driver; o['rigid_driver_bone']=driver
    if o.type=='MESH':
        group=o.vertex_groups.new(name=driver); group.add(list(range(len(o.data.vertices))),1,'REPLACE')
        mod=o.modifiers.new('Rigid single bone','ARMATURE');mod.object=rig
    else:
        # Personal text travels with the torso without changing its rest transform.
        con=o.constraints.new('CHILD_OF');con.target=rig;con.subtarget=driver
        con.inverse_matrix=(rig.matrix_world@rig.data.bones[driver].matrix_local).inverted()

bpy.context.view_layer.update()
neutral_error=max((a-b).length for name,old in baseline.items() for a,b in zip(old,evaluated_vertices(bpy.data.objects[name])))
assert neutral_error<1e-5,neutral_error

def set_segment(name,start,end):
    pb=rig.pose.bones[name]; rb=rig.data.bones[name]
    q=(rb.tail_local-rb.head_local).rotation_difference(end-start)
    pb.matrix=Matrix.Translation(start)@q.to_matrix().to_4x4()@rb.matrix_local.to_3x3().to_4x4()
    bpy.context.view_layer.update()

def solve(a,c,l1,l2,pole):
    delta=c-a; dist=delta.length
    if dist>l1+l2+1e-6 or dist<abs(l1-l2):raise RuntimeError('Unreachable pose')
    axis=delta.normalized(); x=(l1*l1-l2*l2+dist*dist)/(2*dist)
    perpendicular=pole-a-axis*(pole-a).dot(axis)
    return a+axis*x+perpendicular.normalized()*math.sqrt(max(0,l1*l1-x*x))

def move_arm(side,target):
    upper=rig.pose.bones['upper_arm.'+side]; a=upper.head.copy()
    l1=rig.data.bones[upper.name].length;l2=rig.data.bones['forearm.'+side].length
    s=1 if side=='L' else -1
    b=solve(a,target,l1,l2,V((s*1.2,-.25,1.8)))
    set_segment(upper.name,a,b);set_segment('forearm.'+side,b,target)
    hand=rig.pose.bones['hand.'+side]
    # Continue the wrist in the same direction as the forearm.
    set_segment(hand.name,target,target+(target-b).normalized()*hand.bone.length)

def telescope(side):
    shin=rig.pose.bones['shin.'+side];foot=rig.pose.bones['foot.'+side]
    s=1 if side=='L' else -1
    # Re-seat the upper socket 7 cm lower on the same calf housing. The .20 m
    # barrel and .16 m rod now overlap in neutral instead of meeting tip-to-tip.
    upper=shin.matrix@shin.bone.matrix_local.inverted()@V((s*.27,.21,.49))
    lower=foot.matrix@foot.bone.matrix_local.inverted()@V((s*.27,.21,.20))
    axis=(upper-lower).normalized(); distance=(upper-lower).length
    if not .20*F<=distance<=.355*F:
        failure={'result':'FAIL','interface':'calf-piston.stroke','frame':scene.frame_current,'side':side,'socket_distance_m':distance,'declared_range_m':[.20*F,.355*F],'source_sha256':EXPECTED}
        (REVIEW/'failure.json').write_text(json.dumps(failure,indent=2))
        print('FAILURE',json.dumps(failure),flush=True)
        raise RuntimeError('Calf piston stroke exceeded')
    for name,mid in [('Calf ram body '+side,upper-axis*.10*F),('Calf ram rod '+side,lower+axis*.08*F)]:
        o=bpy.data.objects[name];o.location=mid;o.rotation_mode='QUATERNION';o.rotation_quaternion=axis.to_track_quat('Z','Y')
        o.keyframe_insert('location');o.keyframe_insert('rotation_quaternion')
    return distance

pose_records=[]
for frame,label,drop in [(1,'neutral',0),(30,'raised-arms',0),(60,'planted-work',.055)]:
    scene.frame_set(frame)
    for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
    bpy.context.view_layer.update()
    if drop:
        rig.pose.bones['pelvis'].location.y=-drop*F;bpy.context.view_layer.update()
        for side,s in [('L',1),('R',-1)]:
            thigh=rig.pose.bones['thigh.'+side];a=thigh.head.copy()
            ankle=rig.data.bones['foot.'+side].head_local.copy()
            knee=solve(a,ankle,thigh.bone.length,rig.data.bones['shin.'+side].length,V((s*.245,-1,.65)))
            set_segment(thigh.name,a,knee);set_segment('shin.'+side,knee,ankle)
            foot=rig.data.bones['foot.'+side];set_segment(foot.name,ankle,ankle+foot.tail_local-foot.head_local)
        move_arm('L',V((.70,-.48,1.45)));move_arm('R',V((-.65,-.46,1.40)))
    if label=='raised-arms':
        move_arm('L',V((.72,-.17,2.40)));move_arm('R',V((-.72,-.17,2.40)))
    strokes={side:telescope(side) for side in ['L','R']}
    for p in rig.pose.bones:
        p.rotation_mode='QUATERNION'
        p.keyframe_insert('location');p.keyframe_insert('rotation_quaternion');p.keyframe_insert('scale')
    bpy.context.view_layer.update()
    feet={side:min(v.z for v in evaluated_vertices(bpy.data.objects['Anchor sole '+side])) for side in ['L','R']}
    assert all(abs(z)<.00025 for z in feet.values()),feet
    endpoints={side:(rig.pose.bones['upper_arm.'+side].tail-rig.pose.bones['forearm.'+side].head).length for side in ['L','R']}
    assert max(endpoints.values())<1e-5
    pose_records.append({'frame':frame,'pose':label,'sole_min_z_m':feet,'elbow_chain_gap_m':endpoints,'calf_socket_distance_m':strokes})

# Discrete review poses: avoid suggesting unvalidated interpolation is a walk.
for obj in [rig]+[o for o in collection.objects if o.name.startswith('Calf ram ')]:
    if obj.animation_data and obj.animation_data.action:
        for layer in obj.animation_data.action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        for key in curve.keyframe_points:key.interpolation='CONSTANT'
scene.frame_start=1;scene.frame_end=60
for frame,label in [(1,'NEUTRAL'),(30,'RAISED ARMS'),(60,'PLANTED WORK')]:scene.timeline_markers.new(label,frame=frame)
scene.frame_set(1);bpy.context.view_layer.update()
assert mesh_before==raw_signature(),'Source mesh modified'
assert sha(SOURCE)==EXPECTED
scene['status']='ARTICULATION_STUDY';scene['rig_validated']=False
scene['continuous_motion_validated']=False
scene.camera=bpy.data.objects['Front threequarter'];scene.camera.data.ortho_scale=3.3
scene.render.resolution_x=800;scene.render.resolution_y=1000
scene.render.filepath=str(REVIEW/'neutral.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));frozen=sha(OUT)

def bvh(name):
    e=bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh()
    result=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[list(p.vertices) for p in m.polygons],all_triangles=False)
    e.to_mesh_clear();return result

# Flag newly crossing surfaces at declared critical interfaces. This is not full
# solid-containment or continuous-motion collision detection. Shared axle contact
# is intentional and excluded from these pairs.
pairs=[]
for side in ['L','R']:
    for part in ['Donor upper arm '+side,'Donor forearm '+side,'Donor rescue hand '+side]:
        for obstacle in ['Continuous forged yoke','Thoracic protective hull','Thoracic rail '+side]:pairs.append((part,obstacle))
    pairs.append(('Donor shin '+side,'Thigh guard '+side))
scene.frame_set(1);bpy.context.view_layer.update()
base_cross={a+' / '+b:len(bvh(a).overlap(bvh(b))) for a,b in pairs}
record={'source_sha256':EXPECTED,'candidate_sha256':frozen,'neutral_binding_vertex_delta_before_piston_reseat_m':neutral_error,'source_mesh_coordinates_unchanged':mesh_before==raw_signature(),'mechanical_adjustment':'Upper calf socket lowered 0.07 * normalization_factor m; cylinder lengths unchanged; neutral overlap added; maximum socket distance .355 * factor for .36 * factor total lengths','assignments':assign,'poses':pose_records,'collision_scope':'New surface intersections at declared arm/yoke/torso and shin/thigh pairs only; baseline intersections reported separately; not full collision certification','baseline_surface_crossings':{k:v for k,v in base_cross.items() if v},'human_review':'PENDING','continuous_motion_validated':False}
findings=[]
for item in pose_records:
    scene.frame_set(item['frame']);bpy.context.view_layer.update()
    crossings={}
    for a,b in pairs:
        key=a+' / '+b; count=len(bvh(a).overlap(bvh(b)))
        if count and not base_cross[key]:crossings[key]=count
    item['new_surface_crossings']=crossings
    if crossings:findings.append({'pose':item['pose'],'interfaces':crossings})
record['findings']=findings
record['result']='REVIEW_COLLISIONS' if findings else 'SAMPLED_CHECKS_PASS_VISUAL_REVIEW_PENDING'
(REVIEW/'measurements.json').write_text(json.dumps(record,indent=2))
for item in pose_records:
    scene.frame_set(item['frame']);scene.render.filepath=str(REVIEW/(item['pose']+'.png'))
    bpy.ops.render.render(write_still=True)
    if item['new_surface_crossings']:break
assert sha(OUT)==frozen and sha(SOURCE)==EXPECTED
record['renders']={p.name:sha(p) for p in REVIEW.glob('*.png')}
(REVIEW/'measurements.json').write_text(json.dumps(record,indent=2))
print('ARTICULATION_STUDY_COMPLETE',record['result'],flush=True)
