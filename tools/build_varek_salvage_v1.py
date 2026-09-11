"""Static Varek donor study. Run in a fresh Blender process; no legacy files edited."""
import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector

ROOT = Path('/home/aaron/animation/thulans-production')
DONOR = ROOT/'assets/donors/quaternius-mechs/Animated Mech Pack - March 2021/Blends/Stan.blend'
OUT = ROOT/'blender/candidates/varek-simplified-donor-v2.blend'
REVIEW = ROOT/'evidence/varek-simplified-donor-v2'
REVIEW.mkdir(parents=True, exist_ok=True)
if OUT.exists():
    raise RuntimeError('Candidate already exists; choose a new version')

# Read donor mesh and rest-bone positions only. No donor scripts or rig execution.
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(DONOR), link=False) as (src, dst):
    dst.objects = src.objects
source = next(o for o in dst.objects if o.type == 'MESH')
rig = next(o for o in dst.objects if o.type == 'ARMATURE')
donor_records = []
character = bpy.data.collections.new('Varek_Editable_Parts')
bpy.context.scene.collection.children.link(character)

def put(o, name, mat):
    o.name = name
    for c in list(o.users_collection): c.objects.unlink(o)
    character.objects.link(o)
    if mat: o.data.materials.append(mat)
    return o

def material(name, color, metal=.7, rough=.5):
    m=bpy.data.materials.new(name); m.use_nodes=True
    n=m.node_tree.nodes; l=m.node_tree.links
    p=n.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=85
    bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.12; bump.inputs['Distance'].default_value=.0007
    l.new(noise.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs['Normal'],p.inputs['Normal'])
    ramp=n.new('ShaderNodeMapRange'); ramp.inputs['To Min'].default_value=rough-.1; ramp.inputs['To Max'].default_value=rough+.12
    l.new(noise.outputs['Fac'],ramp.inputs['Value']); l.new(ramp.outputs['Result'],p.inputs['Roughness'])
    m.diffuse_color=(*color,1)
    return m

iron=material('Warm charcoal cast iron',(.065,.059,.048),.75,.48)
black=material('Oily joint steel',(.015,.019,.019),.7,.34)
brass=material('Aged brass',(.13,.075,.025),.8,.53)
jade=material('Cinderback jade paint',(.012,.075,.032),.15,.52)
bone=material('Old bone white',(.57,.51,.37),.1,.66)
steel=material('Working piston steel',(.28,.30,.29),.9,.27)
amber=material('Amber visor',(.25,.075,.006),.3,.3)
amber.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value=(1,.27,.015,1)
amber.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=2

def bevel(o, width=.012):
    mod=o.modifiers.new('Manufactured edges','BEVEL'); mod.width=width; mod.segments=3
    mod=o.modifiers.new('Face normals','WEIGHTED_NORMAL'); mod.keep_sharp=True
    return o

def box(name, loc, size, mat=iron, b=.012):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=put(bpy.context.object,name,mat); o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return bevel(o,b) if b else o

def cyl(name, a, b, radius, mat=black, verts=32):
    a,b=Vector(a),Vector(b); d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=radius,depth=d.length,location=(a+b)/2)
    o=put(bpy.context.object,name,mat); o.rotation_mode='QUATERNION'; o.rotation_quaternion=d.to_track_quat('Z','Y')
    bevel(o,.006)
    for p in o.data.polygons: p.use_smooth=True
    return o

def beam(name,a,b,w,d,mat=iron):
    a,b=Vector(a),Vector(b)
    o=box(name,(a+b)/2,(w,d,(b-a).length),mat)
    o.rotation_mode='QUATERNION'; o.rotation_quaternion=(b-a).to_track_quat('Z','Y'); return o

def hull(name,levels,mat=iron):
    # Chamfered rectangular ring loft: (z, width, depth, y-centre).
    verts=[]
    for z,w,d,y in levels:
        c=min(w,d)*.19
        verts += [(x,yy+y,z) for x,yy in [(-w/2+c,-d/2),(w/2-c,-d/2),(w/2,-d/2+c),(w/2,d/2-c),(w/2-c,d/2),(-w/2+c,d/2),(-w/2,d/2-c),(-w/2,-d/2+c)]]
    faces=[tuple(reversed(range(8)))]
    for r in range(len(levels)-1):
        for i in range(8): faces.append((r*8+i,r*8+(i+1)%8,(r+1)*8+(i+1)%8,(r+1)*8+i))
    faces.append(tuple(range(len(verts)-8,len(verts))))
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(name,mesh); character.objects.link(o); o.data.materials.append(mat)
    return bevel(o,.012)

def donor_part(name, groups, bone_name, center, size):
    idx={g.index for g in source.vertex_groups if g.name in groups}
    selected={v.index for v in source.data.vertices if sum(g.weight for g in v.groups if g.group in idx)>.5}
    faces=[p for p in source.data.polygons if all(v in selected for v in p.vertices)]
    used=sorted({v for p in faces for v in p.vertices})
    if not faces: raise RuntimeError('No donor faces: '+name)
    # Rotate the rest limb's longitudinal axis onto Z, then proportion it as a rigid unit.
    bone_data=rig.data.bones[bone_name]
    direction=(rig.matrix_world.to_3x3() @ (bone_data.tail_local-bone_data.head_local)).normalized()
    q=direction.rotation_difference(Vector((0,0,-1)))
    points=[q @ (source.matrix_world @ source.data.vertices[i].co) for i in used]
    lo=Vector(tuple(min(v[k] for v in points) for k in range(3)))
    hi=Vector(tuple(max(v[k] for v in points) for k in range(3)))
    points=[tuple((v[k]-(lo[k]+hi[k])/2)*size[k]/max(hi[k]-lo[k],1e-6)+center[k] for k in range(3)) for v in points]
    remap={old:i for i,old in enumerate(used)}
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(points,[],[tuple(remap[v] for v in p.vertices) for p in faces]); mesh.update()
    o=bpy.data.objects.new(name,mesh); character.objects.link(o); mesh.materials.append(iron)
    o['donor']='Quaternius / Stan / CC0'; o['source_groups']=', '.join(groups)
    bevel(o,.005)
    donor_records.append({'object':name,'groups':groups,'vertices':len(points),'faces':len(faces)})
    return o

# Human-scale arrangement. Front is -Y, character-left is +X.
hull('Thoracic protective hull',[(1.22,.48,.36,.03),(1.44,.64,.46,.015),(1.79,.78,.49,.025),(1.92,.62,.39,.025)])
hull('Pelvic cradle',[(.99,.39,.29,.03),(1.14,.64,.38,.03),(1.26,.51,.34,.03)],black)
hull('Abdominal protection',[(1.12,.31,.33,-.10),(1.35,.40,.35,-.10)])
cyl('Neck seat',(0,0,1.86),(0,0,1.98),.14,black)
hull('Operator cell',[(1.88,.21,.25,-.055),(2.02,.28,.29,-.045),(2.14,.255,.27,-.015),(2.20,.17,.20,.005)])
box('Visor recessed seat',(0,-.192,2.075),(.238,.022,.065),black,.008)
box('Amber protected slit',(0,-.208,2.075),(.206,.009,.022),amber,.004)
box('Helmet brow',(0,-.21,2.115),(.265,.047,.043),iron,.008)

for s,side in [(1,'L'),(-1,'R')]:
    # Deep rails carry the yoke into the pelvic structure.
    beam('Thoracic rail '+side,(s*.27,-.24,1.33),(s*.32,-.19,2.16),.115,.13)
    beam('Dorsal rail '+side,(s*.24,.25,1.16),(s*.32,.24,2.17),.105,.12)
    cyl('Yoke bearing '+side,(s*.32,-.11,2.15),(s*.32,-.23,2.15),.08,brass)
    cyl('Shoulder pivot '+side,(s*.39,0,1.82),(s*.51,0,1.82),.135,black)
    cyl('Shoulder collar '+side,(s*.50,0,1.82),(s*.535,0,1.82),.095,brass)
    donor_part('Donor upper arm '+side,['UpperArm.'+side],'UpperArm.'+side,(s*.53,.015,1.63),(.24,.28,.34))
    cyl('Elbow axle '+side,(s*.49,0,1.42),(s*.64,0,1.42),.092,brass)
    donor_part('Donor forearm '+side,['LowerArm.'+side],'LowerArm.'+side,(s*.585,-.025,1.245),(.29,.31,.32))
    handgroups=[g.name for g in source.vertex_groups if g.name.endswith('.'+side) and any(t in g.name for t in ['Palm','Pinky','Ring','Index','Thumb'])]
    donor_part('Donor rescue hand '+side,handgroups,'LowerArm.'+side,(s*.59,-.065,1.015),(.225,.20,.22))
    cyl('Wrist coupling '+side,(s*.59,-.04,1.085),(s*.59,-.04,1.135),.09,black)
    cyl('Hip axle '+side,(s*.19,.02,1.035),(s*.33,.02,1.035),.115,brass)
    donor_part('Donor thigh '+side,['UpperLeg.'+side],'UpperLeg.'+side,(s*.245,.015,.84),(.30,.32,.32))
    guard=hull('Thigh guard '+side,[(.685,.24,.245,-.045),(.80,.31,.30,-.045),(.98,.30,.29,-.025)])
    guard.location.x=s*.245
    cyl('Knee axle '+side,(s*.17,-.015,.65),(s*.34,-.015,.65),.10,black)
    cyl('Knee bearing '+side,(s*.335,-.015,.65),(s*.36,-.015,.65),.065,brass)
    donor_part('Donor shin '+side,['LowerLeg.'+side],'LowerLeg.'+side,(s*.26,.025,.42),(.29,.32,.37))
    # Stan's Foot groups are IK controls without mesh weights; build ground equipment.
    foot=box('Forged foot housing '+side,(s*.27,-.07,.135),(.30,.40,.19),iron,.045)
    box('Anchor sole '+side,(s*.27,-.065,.038),(.36,.49,.076),iron,.025)
    box('Folded heel anchor '+side,(s*.27,.205,.12),(.30,.075,.20),black,.014)
    cyl('Calf ram body '+side,(s*.27,.21,.56),(s*.27,.21,.36),.035,black)
    cyl('Calf ram rod '+side,(s*.27,.21,.36),(s*.27,.21,.20),.019,steel)

# Continuous forged yoke, with joined mitres rather than separate beam ends.
profile=[(-.41,2.10),(-.41,2.31),(-.28,2.455),(.28,2.455),(.41,2.31),(.41,2.10),(.29,2.10),(.29,2.265),(.225,2.335),(-.225,2.335),(-.29,2.265),(-.29,2.10)]
verts=[(x,y,z) for y in [-.07,.15] for x,z in profile]
n=len(profile); faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
mesh=bpy.data.meshes.new('Continuous yoke'); mesh.from_pydata(verts,[],faces); mesh.update()
o=bpy.data.objects.new('Continuous forged yoke',mesh); character.objects.link(o); mesh.materials.append(iron); bevel(o,.012)

# A single curved ancestral plate, no detached badge panel.
verts=[]; rows=5; cols=9
for j in range(rows):
    v=j/(rows-1)
    for i in range(cols):
        t=-1.2+2.4*i/(cols-1)
        width=[.16,.22,.23,.21,.17][j]
        verts.append((.49+width*math.sin(t),-.025-(.23+.01*v)*math.cos(t),1.98-.34*v+.035*math.cos(t)))
faces=[]
for j in range(rows-1):
    for i in range(cols-1):
        a=j*cols+i; faces.append((a,a+1,a+1+cols,a+cols))
mesh=bpy.data.meshes.new('Ancestral plate'); mesh.from_pydata(verts,[],faces); mesh.update()
plate=bpy.data.objects.new('Gren Skildus',mesh); character.objects.link(plate); mesh.materials.append(jade)
for p in mesh.polygons:p.use_smooth=True
sol=plate.modifiers.new('Forged plate thickness','SOLIDIFY'); sol.thickness=.025
bevel(plate,.008)

box('Integrated engine',(0,.34,1.65),(.48,.29,.55),black,.045)
for z in [1.75,1.81,1.87]:box('Cooling louvre',(0,.496,z),(.37,.025,.026),iron,.003)
cyl('Exhaust',(-.21,.38,1.9),(-.21,.38,2.15),.043,black)
cyl('Winch cable drum',(-.17,.41,1.27),(.17,.41,1.27),.088,black)
for s in [-1,1]:cyl('Winch flange',(s*.17,.41,1.27),(s*.20,.41,1.27),.115,brass)

# Powered maul: single mechanism and broad hammer head. Parked next to right hand.
box('Fault Maul head',(-.86,-.17,.12),(.43,.28,.24),iron,.04)
cyl('Maul impact piston',(-1.10,-.17,.12),(-.96,-.17,.12),.065,brass)
cyl('Maul head collar',(-.86,-.17,.22),(-.86,-.17,.32),.059,brass)
cyl('Maul shaft',(-.86,-.17,.28),(-.86,-.17,1.36),.027,black)
cyl('Maul grip',(-.86,-.17,1.07),(-.86,-.17,1.35),.034,black)

def label(name,text,loc,size,mat):
    c=bpy.data.curves.new(name,'FONT'); c.body=text; c.align_x='CENTER'; c.size=size; c.extrude=0
    o=bpy.data.objects.new(name,c); character.objects.link(o); o.location=loc; o.rotation_euler=(math.pi/2,0,0); c.materials.append(mat)
label('Maul oath','FORTIS ET LIBER',(-.86,-.313,.135),.028,brass)
# Personal inscription on protected inner plate, not public chest slogan.
label('Inner oath','ORA ET LABORA',(.34,-.12,1.80),.018,bone)

for o in list(dst.objects):
    if o: bpy.data.objects.remove(o,do_unlink=True)

# Normalize the full chassis including its forged yoke. Ground remains exactly Z=0.
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
points=[o.evaluated_get(deps).matrix_world@Vector(c) for o in character.objects if o.type=='MESH' for c in o.evaluated_get(deps).bound_box]
height=max(p.z for p in points)-min(p.z for p in points)
factor=2.4384/height
for o in character.objects: o.location*=factor; o.scale*=factor
bpy.context.view_layer.update()

scene=bpy.context.scene; scene.unit_settings.system='METRIC'
scene.render.engine='CYCLES'; scene.cycles.samples=128; scene.cycles.use_denoising=True
scene.cycles.max_bounces=6
scene.render.resolution_x=1050; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Neutral studio'); scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.24,.27,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.35
scene.view_settings.view_transform='AgX'
floor=material('Studio warm grey',(.13,.12,.105),0,.8)
bpy.ops.mesh.primitive_plane_add(size=200)
ground=bpy.context.object; ground.name='Studio floor'; ground.data.materials.append(floor)

def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for name,loc,power,size,color in [('Key',(-3,-4,5),700,4,(1,.91,.78)),('Fill',(3,-2,3),500,3,(.78,.87,1)),('Rim',(1,3,4),950,3,(1,.88,.68))]:
    d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.shape='DISK'; d.size=size; d.color=color
    o=bpy.data.objects.new(name,d); scene.collection.objects.link(o); o.location=loc; aim(o,(0,0,1.2))
for name,loc in [('Front threequarter',(3,-6,2.9)),('Rear threequarter',(-3,6,2.8))]:
    d=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,d); scene.collection.objects.link(o); o.location=loc; aim(o,(-.12,0,1.2)); d.type='ORTHO'; d.ortho_scale=3.0
scene.camera=bpy.data.objects['Front threequarter']
scene.render.filepath=str(REVIEW/'front.png')
scene['status']='STATIC_DRAFT_REQUIRES_VISUAL_REVIEW'
scene['rig_validated']=False
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D': area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
frozen=sha(OUT)
record={'status':'STATIC_DRAFT','candidate_sha256':frozen,'source':str(DONOR),'source_sha256':sha(DONOR),'author':'Quaternius','license':'CC0-1.0','source_url':'https://opengameart.org/content/animated-mech-pack','adaptations':'Extracted rest-mesh limb groups, rotated and proportioned; replaced donor materials; new original torso, yoke, head, shoulder, engine and maul. Original rig not transferred.','donor_parts':donor_records,'normalization_factor':factor,'target_height_m':2.4384,'rig_validated':False,'human_approval':False,'motto_note':'Temporary maul head placement; collar engraving refinement deferred.'}
(REVIEW/'build.json').write_text(json.dumps(record,indent=2))
for cam,file in [('Front threequarter','front.png'),('Rear threequarter','rear.png')]:
    scene.camera=bpy.data.objects[cam]; scene.render.filepath=str(REVIEW/file)
    bpy.ops.render.render(write_still=True)
assert sha(OUT)==frozen
record['renders']={f:sha(REVIEW/f) for f in ['front.png','rear.png']}
(REVIEW/'build.json').write_text(json.dumps(record,indent=2))
print('DRAFT_COMPLETE',OUT,flush=True)
