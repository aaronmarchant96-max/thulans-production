"""Read saved V14 geometry independently; render a labeled kinematic preview."""
import hashlib
import json
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

R=Path('/home/aaron/animation/thulans-production')
E=R/'evidence/varek-carry-v14'
P=R/'blender/candidates/varek-carry-v14.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected=json.loads((E/'measurements.json').read_text())['candidate_sha256']
assert sha(P)==expected and not (E/'saved-readback.json').exists()
bpy.ops.wm.open_mainfile(filepath=str(P))
s=bpy.context.scene;r=bpy.data.objects['Varek simple articulation']
def points(name):
    obj=bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=obj.to_mesh()
    verts=[obj.matrix_world@v.co for v in mesh.vertices]
    faces=[list(p.vertices) for p in mesh.polygons]
    obj.to_mesh_clear()
    return verts,faces

s.frame_set(1);bpy.context.view_layer.update()
grip=r.pose.bones['hand.R'].matrix.inverted()@r.pose.bones['tool'].matrix
rows=[];previous={};failures=[]
for frame in range(1,241):
    s.frame_set(frame);bpy.context.view_layer.update()
    body=BVHTree.FromPolygons(*points('Pelvic cradle'))
    hits={}
    for side in ['L','R']:
        for kind in ['Thigh guard','Donor thigh']:
            name=kind+' '+side
            count=len(body.overlap(BVHTree.FromPolygons(*points(name))))
            if count:hits[name]=count
    soles={};slide={}
    for side in ['L','R']:
        verts,_=points('Anchor sole '+side)
        soles[side]=min(v.z for v in verts)
        centre=sum(verts,Vector())/len(verts)
        planted=abs(soles[side])<1e-6
        if planted and side in previous and previous[side][0]:
            slide[side]=(centre-previous[side][1]).length
        previous[side]=(planted,centre)
    actual=r.pose.bones['hand.R'].matrix.inverted()@r.pose.bones['tool'].matrix
    drift=max(abs(actual[i][j]-grip[i][j]) for i in range(4) for j in range(4))
    row={'frame':frame,'hip_surface_crossings':hits,'sole_min_z_m':soles,
         'planted_slide_m':slide,'hand_tool_matrix_error':drift}
    rows.append(row)
    if hits or min(soles.values())<-.00025 or max(slide.values(),default=0)>1e-5 or drift>1e-5:
        failures.append(row)
report={'candidate_sha256':expected,'claim_class':'OBSERVED',
    'result':'SCOPED_KINEMATIC_PASS' if not failures else 'FAIL',
    'frames':rows,'failures':failures,'physical_handoff_authorized':False,
    'limits':['integer frames only','specified hip surface pairs only; not all solid containment',
              'keyed tool: no force or strength validation']}
(E/'saved-readback.json').write_text(json.dumps(report,indent=2))
print('V14_READBACK',json.dumps({'frames':len(rows),'failed_frames':len(failures),
    'max_planted_slide_m':max((v for row in rows for v in row['planted_slide_m'].values()),default=0),
    'max_grip_matrix_error':max(row['hand_tool_matrix_error'] for row in rows)}),flush=True)
if failures:raise RuntimeError('Saved-file readback failed; no review render')

cam=s.camera.copy();cam.data=s.camera.data.copy();s.collection.objects.link(cam);s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=12
s.render.resolution_percentage=100;s.render.resolution_x=640;s.render.resolution_y=800
def framing(close=False):
    target=Vector((0,-.12,.99)) if close else Vector((0,-.18,1.18))
    cam.location=target+(Vector((-2,-4,.15)) if close else Vector((-4,-7,2.8)))
    cam.data.ortho_scale=.90 if close else 3.15
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
framing()
for frame,name in [(60,'mid-step'),(240,'planted')]:
    s.frame_set(frame);s.render.filepath=str(E/(name+'.png'));bpy.ops.render.render(write_still=True)
framing(True);s.frame_set(100);s.render.resolution_x=s.render.resolution_y=640
s.render.filepath=str(E/'hip-clearance.png');bpy.ops.render.render(write_still=True)
framing();s.render.resolution_x=384;s.render.resolution_y=480;s.cycles.samples=4
out=E/'motion';out.mkdir();images=[]
for index,frame in enumerate(range(1,241,3)):
    s.frame_set(frame);path=out/f'{index:03d}.png'
    s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
    images.append({'frame':frame,'file':path.name,'sha256':sha(path)})
(out/'manifest.json').write_text(json.dumps({'candidate_sha256':expected,'source_fps':24,
    'preview_fps':8,'status':'KINEMATIC DIAGNOSTIC ONLY','frames':images},indent=2))
assert sha(P)==expected
print('V14_PREVIEW_READY',flush=True)
