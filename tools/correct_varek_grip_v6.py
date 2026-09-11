"""Grip-only correction: align the shaft across the donor's finger curl planes."""
import bpy,math,json,hashlib,ast
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path('/home/aaron/animation/thulans-production')
SOURCE=ROOT/'blender/candidates/varek-hammer-study-v5.blend'
OUT=ROOT/'blender/candidates/varek-grip-v6.blend'
E=ROOT/'evidence/varek-grip-v6';E.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='639de3e01a4f8fe2475fa8c591ecd6191b2290edbe513ec409e2e77a1694cd07'
assert sha(SOURCE)==expected and not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene;rig=bpy.data.objects['Varek simple articulation']
F=json.loads((ROOT/'evidence/varek-simplified-donor-v2/build.json').read_text())['normalization_factor']
V=lambda a:Vector(a)*F
tree=ast.parse((ROOT/'tools/rig_varek_salvage_v4.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'set_segment','solve'}],type_ignores=[]),'rig-helpers','exec'),globals())
rest=rig.data.bones['hand.R'].matrix_local.copy()
# Components are stacked along donor Y; each finger curls in donor X/Z.
# Map this stack axis to the vertical shaft, not finger length to shaft length.
rotation=Matrix.Rotation(math.pi/2,4,'X')
contact_rest=V((-.59,-.04,1.00))
offset=rotation.to_3x3()@(contact_rest-rig.data.bones['hand.R'].head_local)
tool_rest=V((-.86,-.17,1.24))
rows=[]
for f in range(1,73):
    scene.frame_set(f);bpy.context.view_layer.update()
    # The across-shaft wrist needs the tool closer in depth. Shift outward too
    # so the broad hammer head stays beside, rather than over, the right boot.
    tool_matrix=rig.pose.bones['tool'].matrix.copy()
    tool_matrix.translation+=V((-.08,.10,0))
    rig.pose.bones['tool'].matrix=tool_matrix
    bpy.context.view_layer.update()
    contact=rig.pose.bones['tool'].matrix@rig.data.bones['tool'].matrix_local.inverted()@tool_rest
    wrist=contact-offset;a=rig.pose.bones['upper_arm.R'].head.copy()
    elbow=solve(a,wrist,rig.data.bones['upper_arm.R'].length,rig.data.bones['forearm.R'].length,V((-1.2,-.12,1.5)))
    set_segment('upper_arm.R',a,elbow);set_segment('forearm.R',elbow,wrist)
    rig.pose.bones['hand.R'].matrix=Matrix.Translation(wrist)@rotation@rest.to_3x3().to_4x4()
    bpy.context.view_layer.update()
    actual=rig.pose.bones['hand.R'].matrix@rest.inverted()@contact_rest
    gap=(actual-contact).length;assert gap<1e-5
    rows.append(gap)
    for name in ['upper_arm.R','forearm.R','hand.R','tool']:
        p=rig.pose.bones[name]
        for c in ['location','rotation_quaternion','scale']:p.keyframe_insert(c)
scene.frame_set(36);scene['status']='GRIP_ORIENTATION_REVIEW'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));frozen=sha(OUT)
(E/'measurements.json').write_text(json.dumps({'source_sha256':expected,'candidate_sha256':frozen,'scope':'right arm/wrist orientation and tool position; source geometry unchanged','tool_shift_pre_normalization_m':[-.08,.10,0],'frames_checked':len(rows),'maximum_grip_reference_gap_m':max(rows),'physical_grip_review':'PENDING'},indent=2))
scene.render.resolution_x=640;scene.render.resolution_y=800;scene.cycles.samples=24
scene.render.filepath=str(E/'full.png');bpy.ops.render.render(write_still=True)
target=rig.pose.bones['hand.R'].matrix@rest.inverted()@contact_rest
cam=scene.camera;cam.location=target+Vector((-1.2,-1.8,.65));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.60
scene.render.resolution_x=640;scene.render.resolution_y=640
scene.render.filepath=str(E/'grip-detail.png');bpy.ops.render.render(write_still=True)
assert sha(OUT)==frozen and sha(SOURCE)==expected
print('GRIP_V6_REVIEW_READY',flush=True)
