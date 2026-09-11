"""Measured thumb/collar clearance correction; freeze and inspect fitted grip."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/home/aaron/animation/thulans-production');S=R/'blender/candidates/varek-grip-v7.blend';P=R/'blender/candidates/varek-grip-v8.blend';E=R/'evidence/varek-grip-v8';E.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(S)=='77f96f511642aebc099b05116c46ff034b3573a10c2e59fff9d57e51448a17cf' and not P.exists()
bpy.ops.wm.open_mainfile(filepath=str(S));s=bpy.context.scene;s.frame_set(36);r=bpy.data.objects['Varek simple articulation'];h=bpy.data.objects['Donor rescue hand R']
# Last sector is the opposed thumb (22 rings x 4 verts), followed by 8 palm verts.
start=len(h.data.vertices)-96;changed=0
for i in range(22):
    for j in [0,3]:
        v=h.data.vertices[start+i*4+j];dx=v.co.x+.59;dz=v.co.z-1
        assert abs(math.hypot(dx,dz)-.038)<1e-6
        v.co.x=-.59+dx*.042/.038;v.co.z=1+dz*.042/.038;changed+=1
h.data.update();bpy.context.view_layer.update()
def surface(o):
    e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();b=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[list(p.vertices) for p in m.polygons]);e.to_mesh_clear();return b
parts=bpy.data.collections['Varek_Editable_Parts'].objects
crossings={}
for name in ['Donor rescue hand R','Gauntlet dorsal guard R','Gauntlet knuckle bar R']:
    a=surface(bpy.data.objects[name])
    for o in parts:
        if o.type=='MESH' and o.get('rigid_driver_bone')=='tool':
            n=len(a.overlap(surface(o)))
            if n:crossings[name+' / '+o.name]=n
result='PASS' if not crossings else 'FAIL'
bpy.ops.wm.save_as_mainfile(filepath=str(P));frozen=sha(P)
(E/'measurements.json').write_text(json.dumps({'candidate_sha256':frozen,'source_sha256':sha(S),'changed_thumb_inner_vertices':changed,'thumb_inner_radius_m_pre_normalization':.042,'surface_crossings':crossings,'surface_crossing_result':result,'human_review':'PENDING'},indent=2))
F=json.loads((R/'evidence/varek-simplified-donor-v2/build.json').read_text())['normalization_factor']
target=r.pose.bones['hand.R'].matrix@r.data.bones['hand.R'].matrix_local.inverted()@(Vector((-.59,-.04,1.00))*F)
cam=s.camera;cam.data.ortho_scale=.5;cam.location=target+Vector((-1.2,-1.8,-.3));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.cycles.samples=24;s.render.resolution_x=640;s.render.resolution_y=640
s.render.filepath=str(E/'grip-detail.png');bpy.ops.render.render(write_still=True)
for o in parts:
    o.hide_render=not(o==h or o.get('rigid_driver_bone')=='tool')
s.render.filepath=str(E/'isolated-fingers.png');bpy.ops.render.render(write_still=True)
assert sha(P)==frozen
print('THUMB_CLEARANCE',result,flush=True)
