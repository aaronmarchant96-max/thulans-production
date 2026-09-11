"""Read-only nonadjacent digit surface sweep and outboard diagnostic stills."""
import hashlib
import itertools
import json
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

R=Path('/home/aaron/animation/thulans-production')
P=R/'blender/candidates/varek-articulated-grip-v12.blend'
E=R/'evidence/varek-articulated-grip-v12'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
digest=sha(P)
assert digest=='c420feaa0d01d0604ce466cc8fca8f7d032fe01f3c761083471484702fdc81ad'
assert not (E/'digit-clearance.json').exists()
bpy.ops.wm.open_mainfile(filepath=str(P))
s=bpy.context.scene;r=bpy.data.objects['Varek simple articulation']
h=bpy.data.objects['Donor rescue hand R']
drivers={v.index:h.vertex_groups[max(v.groups,key=lambda g:g.weight).group].name for v in h.data.vertices}
groups={}
for p in h.data.polygons:
    names={drivers[i] for i in p.vertices}
    assert len(names)==1
    groups.setdefault(names.pop(),[]).append(list(p.vertices))
pairs=[];exclusions=[]
for a,b in itertools.combinations(groups,2):
    if r.data.bones[a].parent.name==b or r.data.bones[b].parent.name==a:
        exclusions.append([a,b,'adjacent hinge / palm root seating'])
    else:pairs.append((a,b))
rows=[]
for frame in range(1,169):
    s.frame_set(frame);bpy.context.view_layer.update()
    transform={n:r.matrix_world@r.pose.bones[n].matrix@r.data.bones[n].matrix_local.inverted() for n in groups}
    points=[transform[drivers[v.index]]@h.matrix_world@v.co for v in h.data.vertices]
    trees={n:BVHTree.FromPolygons(points,polys) for n,polys in groups.items()}
    hits={a+' / '+b:len(trees[a].overlap(trees[b])) for a,b in pairs}
    rows.append({'frame':frame,'nonadjacent_crossings':{k:v for k,v in hits.items() if v}})
record={'candidate_sha256':digest,'claim_class':'OBSERVED','frames':rows,
        'excluded_adjacent_pairs':exclusions,'checked_group_pairs':len(pairs),
        'geometry':'base mesh before bevel; conservative box/pin surfaces',
        'limits':['surface sweep, not full volumetric containment or force test',
                  'intentional adjacent hinge seating excluded'],
        'physical_handoff_authorized':False}
(E/'digit-clearance.json').write_text(json.dumps(record,indent=2))
print('DIGIT_CLEARANCE',json.dumps({'frames':len(rows),'pairs':len(pairs),
    'crossing_frames':sum(bool(row['nonadjacent_crossings']) for row in rows)}),flush=True)
cam=s.camera;cam.data.ortho_scale=.64
s.render.engine='CYCLES';s.cycles.samples=16
s.render.resolution_x=s.render.resolution_y=640
for frame,name in [(60,'wrist-outboard'),(24,'open-outboard')]:
    s.frame_set(frame);bpy.context.view_layer.update()
    target=r.pose.bones['hand.R'].head+Vector((-.01,-.05,.02))
    cam.location=target+Vector((-1.8,.8,.4))
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    s.render.filepath=str(E/(name+'.png'));bpy.ops.render.render(write_still=True)
assert sha(P)==digest
