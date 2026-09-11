"""Frozen-byte full-body companion to the articulated grip diagnostic."""
import hashlib
import json
from pathlib import Path
import bpy

R=Path('/home/aaron/animation/thulans-production')
P=R/'blender/candidates/varek-articulated-grip-v12.blend'
E=R/'evidence/varek-articulated-grip-v12/motion-full'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
digest=sha(P)
assert digest=='c420feaa0d01d0604ce466cc8fca8f7d032fe01f3c761083471484702fdc81ad'
assert not E.exists();E.mkdir()
bpy.ops.wm.open_mainfile(filepath=str(P))
s=bpy.context.scene;s.camera=bpy.data.objects['Front threequarter']
s.render.engine='CYCLES';s.cycles.samples=4
s.render.resolution_x=384;s.render.resolution_y=480;s.render.resolution_percentage=100
rows=[]
for index,frame in enumerate(range(1,169,3)):
    s.frame_set(frame);p=E/f'{index:03d}.png'
    s.render.filepath=str(p);bpy.ops.render.render(write_still=True)
    rows.append({'frame':frame,'file':p.name,'sha256':sha(p)})
(E/'manifest.json').write_text(json.dumps({'candidate_sha256':digest,'source_fps':24,
    'render_sample_fps':8,'render_engine':'CYCLES','frames':rows,
    'status':'KINEMATIC PREVIEW, NOT FREE-TOOL PHYSICS'},indent=2))
assert sha(P)==digest
print('FULL_BODY_PREVIEW_READY',flush=True)
