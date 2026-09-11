"""Saved-byte carry review; explicitly retain the hip-clearance failure."""
import hashlib
import json
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

R=Path('/home/aaron/animation/thulans-production')
P=R/'blender/candidates/varek-carry-v13-transfer.blend'
E=R/'evidence/varek-carry-v13-transfer'
EXPECTED='e63336bf783a5ae82e352f07b8d75d7c5a5f7387256f25c1137261cfb058e09a'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P)==EXPECTED and not (E/'saved-readback.json').exists()
bpy.ops.wm.open_mainfile(filepath=str(P))
s=bpy.context.scene;r=bpy.data.objects['Varek simple articulation']
def points(name):
    o=bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get());m=o.to_mesh()
    p=[o.matrix_world@v.co for v in m.vertices];f=[list(p.vertices) for p in m.polygons]
    o.to_mesh_clear();return p,f

rows=[];previous={};source=json.loads((E/'measurements.json').read_text())
s.frame_set(1);bpy.context.view_layer.update()
grip=r.pose.bones['hand.R'].matrix.inverted()@r.pose.bones['tool'].matrix
for frame in range(1,241):
    s.frame_set(frame);bpy.context.view_layer.update()
    feet={side:points('Anchor sole '+side)[0] for side in ['L','R']}
    soles={side:min(p.z for p in pnts) for side,pnts in feet.items()}
    centres={side:sum(pnts,Vector())/len(pnts) for side,pnts in feet.items()}
    slide={}
    for side in ['L','R']:
        planted=abs(soles[side])<.000001
        if side in previous and planted and previous[side][0]:
            slide[side]=(centres[side]-previous[side][1]).length
            assert slide[side]<.00001,(frame,side,'foot slide',slide[side])
        previous[side]=(planted,centres[side])
        assert soles[side]>=-.00025,(frame,side,'floor penetration')
    actual=r.pose.bones['hand.R'].matrix.inverted()@r.pose.bones['tool'].matrix
    drift=max(abs(actual[i][j]-grip[i][j]) for i in range(4) for j in range(4))
    assert drift<.00001,(frame,'grip drift',drift)
    rows.append({'frame':frame,'sole_min_z_m':soles,'planted_slide_m':slide,'hand_tool_matrix_error':drift})
# Quantify vertices inside the CLOSED pelvic mesh using ray parity; diagnostic
# penetration depths are geometry measurements, not material/contact mechanics.
inside=[]
for frame in [24,60,100,144,180,216]:
    s.frame_set(frame);bpy.context.view_layer.update()
    p,f=points('Pelvic cradle');tree=BVHTree.FromPolygons(p,f)
    for side in ['L','R']:
        depths=[]
        for v in points('Thigh guard '+side)[0]:
            origin=v.copy();direction=Vector((1,.371,.173)).normalized();count=0
            for _ in range(12):
                hit=tree.ray_cast(origin,direction,3)
                if hit[0] is None:break
                count+=1;origin=hit[0]+direction*.000001
            if count%2:depths.append(tree.find_nearest(v)[3])
        inside.append({'frame':frame,'side':side,'vertices_inside_pelvis':len(depths),
                       'max_inside_vertex_depth_m':max(depths,default=0)})
report={'candidate_sha256':EXPECTED,'claim_class':'OBSERVED','frames':rows,
        'hip_penetration_samples':inside,'result':'HIP_CLEARANCE_FAIL',
        'physical_handoff_authorized':False,'limits':['integer-frame checks','vertex-depth samples, not maximum solid overlap','keyed tool, not force-tested']}
(E/'saved-readback.json').write_text(json.dumps(report,indent=2))
print('CARRY_READBACK',json.dumps({'frames':len(rows),
    'max_planted_slide_m':max((d for row in rows for d in row['planted_slide_m'].values()),default=0),
    'max_grip_matrix_error':max(row['hand_tool_matrix_error'] for row in rows),
    'hip_samples':inside}),flush=True)

cam=s.camera.copy();cam.data=s.camera.data.copy();cam.name='Carry review camera'
s.collection.objects.link(cam);s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=12
s.render.resolution_x=640;s.render.resolution_y=800;s.render.resolution_percentage=100
target=Vector((0,-.18,1.18));cam.location=target+Vector((-4,-7,2.8));cam.data.ortho_scale=3.15
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
for frame,name in [(60,'mid-step'),(240,'planted')]:
    s.frame_set(frame);s.render.filepath=str(E/(name+'.png'));bpy.ops.render.render(write_still=True)
s.frame_set(100);target=Vector((0,-.12,.99))
cam.location=target+Vector((-2,-4,.15));cam.data.ortho_scale=.90
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.resolution_x=s.render.resolution_y=640
s.render.filepath=str(E/'hip-clearance.png');bpy.ops.render.render(write_still=True)

out=E/'motion';assert not out.exists();out.mkdir()
target=Vector((0,-.18,1.18));cam.location=target+Vector((-4,-7,2.8));cam.data.ortho_scale=3.15
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.resolution_x=384;s.render.resolution_y=480;s.cycles.samples=4
images=[]
for index,frame in enumerate(range(1,241,3)):
    s.frame_set(frame);p=out/f'{index:03d}.png'
    s.render.filepath=str(p);bpy.ops.render.render(write_still=True)
    images.append({'frame':frame,'file':p.name,'sha256':sha(p)})
(out/'manifest.json').write_text(json.dumps({'candidate_sha256':EXPECTED,'source_fps':24,'preview_fps':8,
    'status':'HIP CLEARANCE FAIL — DIAGNOSTIC ONLY','frames':images},indent=2))
assert sha(P)==EXPECTED
print('CARRY_DIAGNOSTIC_READY',flush=True)
