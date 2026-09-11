"""One bounded hand-interface refinement: wrap, palm seat, single wrist axis."""
import bpy,math,json,hashlib,ast
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/home/aaron/animation/thulans-production');S=R/'blender/candidates/varek-grip-v8.blend';P=R/'blender/candidates/varek-hand-v9.blend';E=R/'evidence/varek-hand-v9';E.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='0c162d02e1ed46a7a312543ea75c61e203465ecd9d97f9149ef8277fda24d054'
assert sha(S)==expected and not P.exists()
bpy.ops.wm.open_mainfile(filepath=str(S));s=bpy.context.scene;r=bpy.data.objects['Varek simple articulation'];collection=bpy.data.collections['Varek_Editable_Parts']
allowed={'Donor rescue hand R','Gauntlet dorsal guard R','Gauntlet knuckle bar R','Wrist coupling R','Donor forearm R'}
def signature():
    return hashlib.sha256(repr(sorted((o.name,tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons),tuple(m.name if m else None for m in o.data.materials)) for o in collection.objects if o.type=='MESH' and o.name not in allowed)).encode()).hexdigest()
before=signature();F=json.loads((R/'evidence/varek-simplified-donor-v2/build.json').read_text())['normalization_factor']
hand=bpy.data.objects['Donor rescue hand R'];mat=hand.data.materials[0];verts=[];faces=[]
# Import geometry-only definitions, never run an earlier producer.
tree=ast.parse((R/'tools/fit_varek_grip_v7.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'arc','box','assign_mesh','surface'}],type_ignores=[]),'grip-mesh-helpers','exec'),globals())
for y in [-.065,-.02,.025]:
    for a,b in [(165,245),(247,327),(329,410)]:arc(y,.034,a,b,inner=.0377,outer=.064)
arc(.073,.042,12,155,inner=.042,outer=.068)
# Palm contact plane just behind the existing rib envelope. Not soft-metal squash.
box((-.647,-.005,1.012),(.035,.20,.12))
assign_mesh(hand)
for name,center,size in [('Gauntlet dorsal guard R',(-.627,-.005,1.085),(.105,.175,.034)),('Gauntlet knuckle bar R',(-.666,-.005,.964),(.020,.185,.018))]:
    o=bpy.data.objects[name];verts=[];faces=[];box(center,size)
    inverse=o.matrix_world.inverted();verts=[tuple(inverse@(Vector(v)*F)) for v in verts];assign_mesh(o)
# Preserve the proximal forearm and its topology; taper only its distal housing.
forearm=bpy.data.objects['Donor forearm R'];distal_changed=0
for v in forearm.data.vertices:
    if v.co.z<1.23:
        u=max(0,min(1,(1.23-v.co.z)/.145));factor=1-.52*u
        v.co.x=-.585+(v.co.x+.585)*factor;v.co.y=-.025+(v.co.y+.025)*factor;distal_changed+=1
forearm.data.update()
# A single cross-wrist bearing axis, instead of the large longitudinal disk.
o=bpy.data.objects['Wrist coupling R'];verts=[];faces=[];N=32
for x,radius in [(-.625,.036),(-.621,.056),(-.559,.056),(-.555,.036)]:
    for i in range(N):
        a=2*math.pi*i/N;verts.append((x,-.04+radius*math.cos(a),1.11+radius*math.sin(a)))
faces.append(tuple(reversed(range(N))));faces.append(tuple(range(3*N,4*N)))
for j in range(3):
    for i in range(N):faces.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
inverse=o.matrix_world.inverted();verts=[tuple(inverse@(Vector(v)*F)) for v in verts]
saved_mat=mat;mat=o.data.materials[0];assign_mesh(o);mat=saved_mat
assert before==signature()
s.frame_set(36);bpy.context.view_layer.update();crossings={}
tools=[o for o in collection.objects if o.type=='MESH' and o.get('rigid_driver_bone')=='tool']
for name in allowed:
    h=surface(bpy.data.objects[name])
    for o in tools:
        n=len(h.overlap(surface(o)))
        if n:crossings[name+' / '+o.name]=n
# Right hand/tool relative transform must stay constant through saved animation.
relative=[]
for frame in range(1,73):
    s.frame_set(frame);bpy.context.view_layer.update()
    m=r.pose.bones['hand.R'].matrix.inverted()@r.pose.bones['tool'].matrix
    relative.append([v for row in m for v in row])
drift=max(abs(a-b) for row in relative for a,b in zip(row,relative[0]));assert drift<1e-5
s.frame_set(36);s['status']='HAND_INTERFACE_REFINEMENT_REVIEW'
bpy.ops.wm.save_as_mainfile(filepath=str(P));frozen=sha(P)
record={'claim_class':'OBSERVED','source_sha256':expected,'candidate_sha256':frozen,'changed_meshes':sorted(allowed),'other_meshes_and_material_slots_unchanged':before==signature(),'distal_forearm_vertices_changed':distal_changed,'finger_wrap_degrees':245,'nominal_finger_inner_radius_m_pre_normalization':.0377,'wrist_bearing_radius_m_pre_normalization':.056,'frames_checked':len(relative),'max_relative_hand_tool_matrix_drift':drift,'tool_surface_crossings':crossings,'result':'CONTACT_CROSSING_FAIL' if crossings else 'MACHINE_CHECKS_PASS_VISUAL_REVIEW_PENDING','human_review':'PENDING','exclusions':['full suit collision certification','finger opening animation','load simulation','left hand changes']}
(E/'measurements.json').write_text(json.dumps(record,indent=2))
s.camera=bpy.data.objects['Front threequarter'];s.render.resolution_x=640;s.render.resolution_y=800;s.cycles.samples=24;s.render.filepath=str(E/'full.png');bpy.ops.render.render(write_still=True)
target=r.pose.bones['hand.R'].matrix@r.data.bones['hand.R'].matrix_local.inverted()@(Vector((-.59,-.04,1.00))*F)
cam=s.camera;cam.data.ortho_scale=.48;s.render.resolution_x=640;s.render.resolution_y=640
for name,offset in [('grip-detail',(-1.2,-1.8,-.3)),('thumb-side',(1.2,-1.8,-.2))]:
    cam.location=target+Vector(offset);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(E/(name+'.png'));bpy.ops.render.render(write_still=True)
assert sha(S)==expected and sha(P)==frozen
print(record['result'],flush=True)
