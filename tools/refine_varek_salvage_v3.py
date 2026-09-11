"""Bounded shape and maul refinement of the accepted donor starting draft."""
import bpy, math, json, hashlib, ast
from pathlib import Path
from mathutils import Vector

ROOT=Path('/home/aaron/animation/thulans-production')
SOURCE=ROOT/'blender/candidates/varek-simplified-donor-v2.blend'
OUT=ROOT/'blender/candidates/varek-simplified-donor-v3.blend'
REVIEW=ROOT/'evidence/varek-simplified-donor-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
expected='751985a4a5b9fc21fc2a5edb386b9b8001901af0f16f15b445b8ed085bc49c88'
assert sha(SOURCE)==expected, 'Source changed'
assert not OUT.exists(), 'Use a new output version'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
REVIEW.mkdir(parents=True,exist_ok=True)
character=bpy.data.collections['Varek_Editable_Parts']
iron=bpy.data.materials['Warm charcoal cast iron']; black=bpy.data.materials['Oily joint steel']
brass=bpy.data.materials['Aged brass']; steel=bpy.data.materials['Working piston steel']; bone=bpy.data.materials['Old bone white']
# Reuse geometry utilities only; never execute the producer's scene-building body.
tree=ast.parse((ROOT/'tools/build_varek_salvage_v1.py').read_text())
utilities={'put','bevel','box','cyl','beam','hull','label'}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in utilities],type_ignores=[]),'<geometry utilities>','exec'))
factor=json.loads((ROOT/'evidence/varek-simplified-donor-v2/build.json').read_text())['normalization_factor']
for o in character.objects:o.location/=factor; o.scale/=factor

# Curved faceted torso: central protected hull now follows a broad human chest.
o=bpy.data.objects['Thoracic protective hull']
levels=[(1.22,.43,.34,.03),(1.38,.55,.41,.015),(1.59,.70,.50,.015),(1.78,.77,.49,.025),(1.91,.61,.38,.025)]
verts=[]; N=20
for z,w,d,cy in levels:
    for i in range(N):
        t=2*math.pi*i/N
        x=w/2*math.copysign(abs(math.cos(t))**.65,math.cos(t))
        y=cy+d/2*math.copysign(abs(math.sin(t))**.65,math.sin(t))
        verts.append((x,y,z))
faces=[tuple(reversed(range(N)))]
for j in range(len(levels)-1):
    for i in range(N):faces.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
faces.append(tuple(range(len(verts)-N,len(verts))))
m=bpy.data.meshes.new('Curved thoracic shell v3'); m.from_pydata(verts,[],faces); m.update(); m.materials.append(iron); o.data=m
for p in m.polygons:p.use_smooth=len(p.vertices)==4

for side,s in [('L',1),('R',-1)]:
    o=bpy.data.objects['Donor shin '+side]
    # Preserve the donor form but restore volume toward its pinched lower section.
    for v in o.data.vertices:
        u=max(0,min(1,(.605-v.co.z)/.37))
        v.co.x=s*.26+(v.co.x-s*.26)*(1+.22*u)
        v.co.y=.025+(v.co.y-.025)*(1+.32*u)
    o['adaptation_v3']='Lower shin widened and deepened about its own centreline'
    o=bpy.data.objects['Donor rescue hand '+side]
    for v in o.data.vertices:
        if v.co.z<1.015:
            u=max(0,min(1,(1.015-v.co.z)/.11))
            v.co.y+=.035*u
            v.co.z+=.016*u*u
    box('Gauntlet dorsal guard '+side,(s*.59,.015,1.025),(.21,.072,.125),iron,.025)
    cyl('Gauntlet knuckle bar '+side,(s*.59-.085,-.072,.992),(s*.59+.085,-.072,.992),.024,black)

# Give the tool a clear impact face, rear pressure unit, reinforced collar and grips.
head=bpy.data.objects['Fault Maul head']; head.dimensions=(.47,.28,.24)
for x in [-1.115,-.605]:
    box('Maul replaceable striking shoe',(x,-.17,.12),(.06,.315,.24),steel,.014)
# Existing rear piston becomes the short visible ram joining the head to its shoe.
cyl('Maul pressure chamber',(-1.055,-.17,.247),(-.68,-.17,.247),.044,black)
for x in [-1.045,-.69]:
    cyl('Maul accumulator band',(x-.011,-.17,.247),(x+.011,-.17,.247),.05,brass)
box('Maul cylinder saddle',(-.865,-.17,.218),(.29,.12,.055),iron,.008)
collar=box('Forged oath collar',(-.86,-.17,.33),(.27,.108,.108),brass,.014)
for z in [.40,.92,1.055,1.355]:
    cyl('Maul shaft ferrule',(-.86,-.17,z-.014),(-.86,-.17,z+.014),.04,brass)
for z in [.56,.60,.64,.68,.72,.76]:
    cyl('Maul lower grip rib',(-.86,-.17,z-.012),(-.86,-.17,z+.012),.034,black)
for z in [1.10,1.15,1.20,1.25,1.30]:
    cyl('Maul upper grip rib',(-.86,-.17,z-.014),(-.86,-.17,z+.014),.037,black)
# Oath is now cut into its specified collar, not printed on the striking head.
old=bpy.data.objects['Maul oath']; bpy.data.objects.remove(old,do_unlink=True)
c=bpy.data.curves.new('Oath cutting stencil','FONT'); c.body='FORTIS ET LIBER'; c.align_x='CENTER'; c.size=.025; c.extrude=.002
cut=bpy.data.objects.new('Temporary oath cutter',c); character.objects.link(cut); cut.location=(-.86,-.223,.319); cut.rotation_euler=(math.pi/2,0,0)
bpy.ops.object.select_all(action='DESELECT'); cut.select_set(True); bpy.context.view_layer.objects.active=cut
bpy.ops.object.convert(target='MESH'); cut=bpy.context.object
bpy.context.view_layer.objects.active=collar
mod=collar.modifiers.new('Stamped FORTIS ET LIBER','BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cut
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(cut,do_unlink=True)
collar['inscription']='FORTIS ET LIBER'; collar['construction']='Boolean recessed lettering'

# Less polished brass and more readable dark metal; no full weathering pass yet.
for mat,col,rough in [(iron,(.038,.036,.031),.57),(brass,(.10,.06,.023),.60)]:
    p=mat.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*col,1)
    mat.diffuse_color=(*col,1)
    for n in mat.node_tree.nodes:
        if n.bl_idname=='ShaderNodeMapRange':
            n.inputs['To Min'].default_value=rough-.08; n.inputs['To Max'].default_value=rough+.10
for o in character.objects:o.location*=factor; o.scale*=factor
bpy.context.view_layer.update()
scene=bpy.context.scene
camdata=bpy.data.cameras.new('Maul detail'); cam=bpy.data.objects.new('Maul detail',camdata); scene.collection.objects.link(cam)
cam.location=(-2.1,-3,1.25); cam.rotation_euler=(Vector((-.86,-.17,.65))-cam.location).to_track_quat('-Z','Y').to_euler(); camdata.type='ORTHO'; camdata.ortho_scale=1.65
scene.camera=bpy.data.objects['Front threequarter']; scene.render.filepath=str(REVIEW/'front.png')
scene['status']='STATIC_REFINEMENT_REQUIRES_VISUAL_REVIEW'; scene['rig_validated']=False
bpy.ops.wm.save_as_mainfile(filepath=str(OUT)); frozen=sha(OUT)
deps=bpy.context.evaluated_depsgraph_get()
pts=[o.evaluated_get(deps).matrix_world@Vector(v) for o in character.objects if o.type=='MESH' for v in o.evaluated_get(deps).bound_box]
height=max(v.z for v in pts)-min(v.z for v in pts)
assert abs(height-2.4384)<.0005 and abs(min(v.z for v in pts))<.00025
record={'source_sha256':expected,'candidate_sha256':frozen,'height_m':height,'floor_z':min(v.z for v in pts),'donor_objects':[o.name for o in character.objects if 'donor' in o],'changes':['curved tapered chest','fuller donor shins','donor hand curl and protective guards','powered maul hardware','recessed collar oath','subdued iron/brass'],'rig_validated':False,'human_review':'PENDING','source_unchanged':sha(SOURCE)==expected}
(REVIEW/'build.json').write_text(json.dumps(record,indent=2))
for name,file in [('Front threequarter','front.png'),('Maul detail','maul.png')]:
    scene.camera=bpy.data.objects[name]; scene.render.filepath=str(REVIEW/file)
    bpy.ops.render.render(write_still=True)
assert sha(OUT)==frozen and sha(SOURCE)==expected
record['renders']={f:sha(REVIEW/f) for f in ['front.png','maul.png']}
(REVIEW/'build.json').write_text(json.dumps(record,indent=2))
print('REFINEMENT_COMPLETE',str(OUT),flush=True)
