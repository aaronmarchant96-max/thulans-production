"""Read frozen handling candidate; validate saved grip, render review-only views."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path('/home/aaron/animation/thulans-production')
E=ROOT/'evidence/varek-hammer-study-v5'
P=ROOT/'blender/candidates/varek-hammer-study-v5.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((E/'measurements.json').read_text()); frozen=sha(P)
assert frozen==report['candidate_sha256']
bpy.ops.wm.open_mainfile(filepath=str(P))
s=bpy.context.scene;r=bpy.data.objects['Varek simple articulation']
F=json.loads((ROOT/'evidence/varek-simplified-donor-v2/build.json').read_text())['normalization_factor']
g=Vector((-.59,-.105,.985))*F;t=Vector((-.86,-.17,1.24))*F
max_gap=0
for frame in range(1,73):
    s.frame_set(frame);bpy.context.view_layer.update()
    a=r.pose.bones['hand.R'].matrix@r.data.bones['hand.R'].matrix_local.inverted()@g
    b=r.pose.bones['tool'].matrix@r.data.bones['tool'].matrix_local.inverted()@t
    max_gap=max(max_gap,(a-b).length)
assert max_gap<1e-5,max_gap
(E/'saved-readback.json').write_text(json.dumps({'candidate_sha256':frozen,'frames_checked':72,'maximum_grip_reference_gap_m':max_gap,'result':'SAVED_GRIP_TRANSFORMS_PASS','exclusions':['finger surface contact','continuous subframes','full collision detection']},indent=2))
mode=sys.argv[-1]
if mode=='preview':
    s.render.resolution_x=320;s.render.resolution_y=400;s.cycles.samples=8
    folder=E/'preview-frames';folder.mkdir(exist_ok=True)
    for index,frame in enumerate(range(1,73,2)):
        s.frame_set(frame);s.render.filepath=str(folder/f'{index:04d}.png')
        bpy.ops.render.render(write_still=True)
else:
    s.frame_set(36);bpy.context.view_layer.update()
    cam=s.camera;target=r.pose.bones['hand.R'].matrix@r.data.bones['hand.R'].matrix_local.inverted()@g
    cam.location=target+Vector((-1.2,-1.8,.65));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.ortho_scale=.65;s.render.resolution_x=640;s.render.resolution_y=640;s.cycles.samples=32
    s.render.filepath=str(E/'grip-detail.png');bpy.ops.render.render(write_still=True)
assert sha(P)==frozen
print('FROZEN_REVIEW_COMPLETE',mode,flush=True)
