import bpy,json,hashlib
from mathutils.bvhtree import BVHTree
from pathlib import Path
from mathutils import Vector
R=Path('/home/aaron/animation/thulans-production');E=R/'evidence/varek-grip-v6';P=R/'blender/candidates/varek-grip-v6.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
frozen=sha(P);assert frozen==json.loads((E/'measurements.json').read_text())['candidate_sha256']
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;s.frame_set(36)
r=bpy.data.objects['Varek simple articulation'];F=json.loads((R/'evidence/varek-simplified-donor-v2/build.json').read_text())['normalization_factor']
target=r.pose.bones['hand.R'].matrix@r.data.bones['hand.R'].matrix_local.inverted()@(Vector((-.59,-.04,1.00))*F)
cam=s.camera;cam.data.ortho_scale=.55;s.render.resolution_x=640;s.render.resolution_y=640;s.cycles.samples=24
def surface(o):
    e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh()
    b=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[list(p.vertices) for p in m.polygons]);e.to_mesh_clear();return b
hand=surface(bpy.data.objects['Donor rescue hand R'])
crossings={o.name:len(hand.overlap(surface(o))) for o in bpy.data.collections['Varek_Editable_Parts'].objects if o.type=='MESH' and o.get('rigid_driver_bone')=='tool'}
(E/'contact-crossings.json').write_text(json.dumps({'candidate_sha256':frozen,'frame':36,'surface_triangle_crossings':{k:v for k,v in crossings.items() if v},'scope':'donor hand versus tool meshes; contact tolerance not classified'},indent=2))
for name in ['Gauntlet dorsal guard R','Gauntlet knuckle bar R','Wrist coupling R']:
    bpy.data.objects[name].hide_render=True
for name,offset in [('isolated-contact',(-1.2,-1.8,-.8))]:
    cam.location=target+Vector(offset);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    s.render.filepath=str(E/(name+'.png'));bpy.ops.render.render(write_still=True)
assert sha(P)==frozen
