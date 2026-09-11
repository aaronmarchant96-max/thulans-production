"""Readable right grip: distinct forearm termination, wrist, palm and digits."""
import bpy,math,json,hashlib,ast
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path('/home/aaron/animation/thulans-production');S=R/'blender/candidates/varek-hand-v9.blend';P=R/'blender/candidates/varek-hand-v10.blend';E=R/'evidence/varek-hand-v10';E.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='d3aaa436ecd90ed1118ea1eb1beacf77d88a3cfb7fea6bce8f223b147fffa3ff'
assert sha(S)==expected and not P.exists()
bpy.ops.wm.open_mainfile(filepath=str(S));scene=bpy.context.scene;rig=bpy.data.objects['Varek simple articulation'];collection=bpy.data.collections['Varek_Editable_Parts']
allowed={'Donor rescue hand R','Donor forearm R','Wrist coupling R','Gauntlet dorsal guard R','Gauntlet knuckle bar R'}
def signature():
    return hashlib.sha256(repr(sorted((o.name,tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons),tuple(m.name if m else None for m in o.data.materials)) for o in collection.objects if o.type=='MESH' and o.name not in allowed)).encode()).hexdigest()
baseline=signature();F=json.loads((R/'evidence/varek-simplified-donor-v2/build.json').read_text())['normalization_factor'];V=lambda a:Vector(a)*F
for file,names in [('fit_varek_grip_v7.py',{'arc','box','surface'}),('rig_varek_salvage_v4.py',{'set_segment','solve'})]:
    tree=ast.parse((R/'tools'/file).read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),file+'-helpers','exec'),globals())
verts=[];faces=[]
def bind_mesh(name,driver):
    o=bpy.data.objects[name];material=o.data.materials[0];inverse=o.matrix_world.inverted()
    m=bpy.data.meshes.new(name+' readable v10');m.from_pydata([inverse@V(v) for v in verts],[],faces);m.update();m.materials.append(material);o.data=m
    group=o.vertex_groups.get(driver) or o.vertex_groups.new(name=driver);group.add(list(range(len(m.vertices))),1,'REPLACE')
    for mod in o.modifiers:
        if mod.type=='BEVEL':mod.width=.0012;mod.segments=2
    o['geometry_origin']='Original Thulan right-hand interface v10'
    if 'donor' in o:del o['donor']
def cylinder_z(z0,z1,radius,x=-.585,y=-.025,N=24):
    start=len(verts)
    for z in [z0,z1]:
        for i in range(N):
            a=2*math.pi*i/N;verts.append((x+radius*math.cos(a),y+radius*math.sin(a),z))
    faces.extend([tuple(start+i for i in reversed(range(N))),tuple(start+N+i for i in range(N))])
    for i in range(N):faces.append((start+i,start+(i+1)%N,start+N+(i+1)%N,start+N+i))
# Three distinct curled digits and a thumb. A curved palm replaces the solid slab.
for y in [-.065,-.02,.025]:
    for a,b in [(150,230),(233,313),(316,400)]:arc(y,.032,a,b,inner=.0377,outer=.061)
arc(.073,.040,12,150,inner=.042,outer=.063)
arc(-.025,.150,145,220,inner=.0382,outer=.064)
bind_mesh('Donor rescue hand R','hand.R')
for name,center,size in [('Gauntlet dorsal guard R',(-.635,-.03,1.078),(.075,.140,.025)),('Gauntlet knuckle bar R',(-.654,-.025,1.045),(.018,.145,.020))]:
    verts=[];faces=[];box(center,size);bind_mesh(name,'hand.R')
# One restrained tapered forearm casing; it ends before the wrist articulation.
verts=[];faces=[];N=8
for z,w,d in [(1.18,.112,.120),(1.225,.16,.16),(1.36,.225,.205),(1.405,.19,.17)]:
    for i in range(N):
        a=2*math.pi*i/N;verts.append((-.585+math.cos(a)*w/2,-.025+math.sin(a)*d/2,z))
faces.extend([tuple(reversed(range(N))),tuple(range(3*N,4*N))])
for j in range(3):
    for i in range(N):faces.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
cylinder_z(1.108,1.190,.030,x=-.59,y=-.04)
bind_mesh('Donor forearm R','forearm.R')
# One defined cross-wrist axis, with a smaller central bearing and raised lip.
verts=[];faces=[];N=32
for x,radius in [(-.618,.030),(-.614,.043),(-.566,.043),(-.562,.030)]:
    for i in range(N):
        a=2*math.pi*i/N;verts.append((x,-.04+radius*math.cos(a),1.11+radius*math.sin(a)))
faces.extend([tuple(reversed(range(N))),tuple(range(3*N,4*N))])
for j in range(3):
    for i in range(N):faces.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
bind_mesh('Wrist coupling R','hand.R')
# Turn the palm away from the hero camera; preserve the exact hammer animation.
rest=rig.data.bones['hand.R'].matrix_local.copy();rotation=Matrix.Rotation(math.pi,4,'Z')@Matrix.Rotation(math.pi/2,4,'X')
contact_rest=V((-.59,-.04,1.00));offset=rotation.to_3x3()@(contact_rest-rig.data.bones['hand.R'].head_local)
tool_rest=V((-.86,-.17,1.24));rows=[];crossings={}
tool_objects=[o for o in collection.objects if o.type=='MESH' and o.get('rigid_driver_bone')=='tool']
for frame in range(1,73):
    scene.frame_set(frame);bpy.context.view_layer.update()
    contact=rig.pose.bones['tool'].matrix@rig.data.bones['tool'].matrix_local.inverted()@tool_rest;wrist=contact-offset
    a=rig.pose.bones['upper_arm.R'].head.copy();elbow=solve(a,wrist,rig.data.bones['upper_arm.R'].length,rig.data.bones['forearm.R'].length,V((-1.2,-.12,1.5)))
    set_segment('upper_arm.R',a,elbow);set_segment('forearm.R',elbow,wrist)
    rig.pose.bones['hand.R'].matrix=Matrix.Translation(wrist)@rotation@rest.to_3x3().to_4x4();bpy.context.view_layer.update()
    actual=rig.pose.bones['hand.R'].matrix@rest.inverted()@contact_rest;gap=(actual-contact).length;assert gap<1e-5
    rows.append(gap)
    for name in ['upper_arm.R','forearm.R','hand.R']:
        for c in ['location','rotation_quaternion','scale']:rig.pose.bones[name].keyframe_insert(c)
    if frame in [1,36,64]:
        hits={}
        for name in allowed:
            a=surface(bpy.data.objects[name])
            for o in tool_objects:
                n=len(a.overlap(surface(o)))
                if n:hits[name+' / '+o.name]=n
        if hits:crossings[str(frame)]=hits
assert baseline==signature();scene.frame_set(36);scene['status']='READABLE_HAND_INTERFACE_REVIEW'
bpy.ops.wm.save_as_mainfile(filepath=str(P));frozen=sha(P)
record={'claim_class':'OBSERVED','source_sha256':expected,'candidate_sha256':frozen,'changed_meshes':sorted(allowed),'other_geometry_and_material_slots_unchanged':baseline==signature(),'grip_reference_frames_checked':len(rows),'max_grip_reference_gap_m':max(rows),'contact_frames_checked':[1,36,64],'tool_surface_crossings':crossings,'result':'CONTACT_FAIL' if crossings else 'SAMPLED_MACHINE_CHECKS_PASS_VISUAL_REVIEW_PENDING','human_review':'PENDING','limits':['fixed closed-hand configuration; finger opening not rigged','no full suit collision certification','no load simulation']}
(E/'measurements.json').write_text(json.dumps(record,indent=2))
scene.camera=bpy.data.objects['Front threequarter'];scene.render.resolution_x=640;scene.render.resolution_y=800;scene.cycles.samples=24;scene.render.filepath=str(E/'full.png');bpy.ops.render.render(write_still=True)
target=rig.pose.bones['hand.R'].matrix@rest.inverted()@contact_rest;cam=scene.camera;cam.data.ortho_scale=.49;scene.render.resolution_x=640;scene.render.resolution_y=640
for name,delta in [('grip-detail',(-1.2,-1.8,-.20)),('wrist-side',(-1.8,.8,.25))]:
    cam.location=target+Vector(delta);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(E/(name+'.png'));bpy.ops.render.render(write_still=True)
assert sha(S)==expected and sha(P)==frozen
print(record['result'],flush=True)
