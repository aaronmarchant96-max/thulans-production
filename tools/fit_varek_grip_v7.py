"""Local right-grip replacement after measured donor-hand/shaft penetration."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/home/aaron/animation/thulans-production');S=R/'blender/candidates/varek-grip-v6.blend';P=R/'blender/candidates/varek-grip-v7.blend';E=R/'evidence/varek-grip-v7';E.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='78737cc9e08c4372b9a2b84ad1c9b0d9a895a9d35d988d8f6426c43b783b5876'
assert sha(S)==expected and not P.exists()
bpy.ops.wm.open_mainfile(filepath=str(S));s=bpy.context.scene;r=bpy.data.objects['Varek simple articulation']
collection=bpy.data.collections['Varek_Editable_Parts']
allowed={'Donor rescue hand R','Gauntlet dorsal guard R','Gauntlet knuckle bar R'}
def signature():
    return hashlib.sha256(repr(sorted((o.name,tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons)) for o in collection.objects if o.type=='MESH' and o.name not in allowed)).encode()).hexdigest()
baseline=signature();F=json.loads((R/'evidence/varek-simplified-donor-v2/build.json').read_text())['normalization_factor']
hand=bpy.data.objects['Donor rescue hand R'];mat=hand.data.materials[0]
verts=[];faces=[]
def arc(y,width,a,b,inner=.038,outer=.066):
    start=len(verts);n=math.ceil((b-a)/7)
    for i in range(n+1):
        t=math.radians(a+(b-a)*i/n)
        for radius,yy in [(inner,y-width/2),(outer,y-width/2),(outer,y+width/2),(inner,y+width/2)]:
            verts.append((-.59+radius*math.cos(t),yy,1.00+radius*math.sin(t)))
    faces.append(tuple(start+j for j in [3,2,1,0]));faces.append(tuple(start+n*4+j for j in range(4)))
    for i in range(n):
        for j in range(4):faces.append((start+i*4+j,start+i*4+(j+1)%4,start+(i+1)*4+(j+1)%4,start+(i+1)*4+j))
def box(center,size):
    start=len(verts)
    verts.extend(tuple(center[k]+signs[k]*size[k]/2 for k in range(3)) for signs in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)])
    faces.extend(tuple(start+j for j in ids) for ids in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
def assign_mesh(o):
    m=bpy.data.meshes.new(o.name+' fitted grip');m.from_pydata(verts,[],faces);m.update();m.materials.append(mat);o.data=m
    # New meshes have no per-vertex deform data: explicitly bind every new vertex.
    group=o.vertex_groups.get('hand.R') or o.vertex_groups.new(name='hand.R');group.add(list(range(len(m.vertices))),1,'REPLACE')
    for mod in o.modifiers:
        if mod.type=='BEVEL':mod.width=.0012;mod.segments=2
    o['geometry_origin']='Original Thulan fitted-grip geometry; not donor mesh'
    if 'donor' in o:del o['donor']
for y in [-.065,-.02,.025]:
    # Three articulated-looking phalange masses, with narrow joint breaks.
    for a,b in [(165,230),(232,297),(299,370)]:arc(y,.034,a,b)
# Opposed thumb above the finger stack, closing from the other side.
arc(.073,.042,12,155,inner=.038,outer=.068)
box((-.667,-.005,1.015),(.046,.20,.13))
assign_mesh(hand)
# Re-seat only the right dorsal guard and knuckle rail behind the new palm.
for name,center,size in [('Gauntlet dorsal guard R',(-.635,-.005,1.087),(.145,.20,.052)),('Gauntlet knuckle bar R',(-.67,-.005,.963),(.034,.20,.022))]:
    o=bpy.data.objects[name];verts=[];faces=[];box(center,size)
    # Unlike donor coordinates these objects had their own local transforms.
    world=[Vector(v)*F for v in verts];inverse=o.matrix_world.inverted();verts=[tuple(inverse@v) for v in world]
    assign_mesh(o)
assert signature()==baseline
s.frame_set(36);bpy.context.view_layer.update()
def surface(o):
    e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();b=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[list(p.vertices) for p in m.polygons]);e.to_mesh_clear();return b
crossings={}
for name in allowed:
    h=surface(bpy.data.objects[name])
    for o in collection.objects:
        if o.type=='MESH' and o.get('rigid_driver_bone')=='tool':
            count=len(h.overlap(surface(o)))
            if count:crossings[name+' / '+o.name]=count
record={'source_sha256':expected,'changed_meshes':sorted(allowed),'other_meshes_unchanged':signature()==baseline,'claim_class':'OBSERVED','frame':36,'surface_crossings':crossings,'contact_design':'38 mm inner finger radius around max 37 mm grip ribs, pre-normalization; three fingers plus opposed thumb','human_review':'PENDING'}
record['result']='CONTACT_CROSSING_FAIL' if crossings else 'SURFACE_CROSSING_CHECK_PASS_VISUAL_REVIEW_PENDING'
s['status']='RIGHT_GRIP_REVIEW';bpy.ops.wm.save_as_mainfile(filepath=str(P));frozen=sha(P);record['candidate_sha256']=frozen
(E/'measurements.json').write_text(json.dumps(record,indent=2))
s.render.resolution_x=640;s.render.resolution_y=800;s.cycles.samples=24;s.render.filepath=str(E/'full.png');bpy.ops.render.render(write_still=True)
target=r.pose.bones['hand.R'].matrix@r.data.bones['hand.R'].matrix_local.inverted()@(Vector((-.59,-.04,1.00))*F)
cam=s.camera;cam.data.ortho_scale=.50;s.render.resolution_x=640;s.render.resolution_y=640
for name,offset in [('grip-detail',(-1.2,-1.8,-.30)),('thumb-side',(1.2,-1.8,-.20))]:
    cam.location=target+Vector(offset);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(E/(name+'.png'));bpy.ops.render.render(write_still=True)
assert sha(P)==frozen and sha(S)==expected
print(record['result'],flush=True)
