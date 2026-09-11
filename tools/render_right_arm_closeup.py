import bpy
from pathlib import Path
from mathutils import Vector

ROOT = Path("/home/aaron/animation/thulans-production")
cand = ROOT / "blender/candidates/varek-v54-graviton.blend"
bpy.ops.wm.open_mainfile(filepath=str(cand))
scene = bpy.context.scene

for c in list(bpy.data.cameras):
    bpy.data.cameras.remove(c)
for o in [x for x in bpy.data.objects if x.type == "CAMERA"]:
    bpy.data.objects.remove(o)

cd = bpy.data.cameras.new("CamClose")
cd.type = "PERSP"
cd.lens = 65.0
cam = bpy.data.objects.new("CamClose", cd)
scene.collection.objects.link(cam)
scene.camera = cam
scene.render.resolution_x = 900
scene.render.resolution_y = 1200

# Target right wrist area: (-0.586, -0.040, 1.08)
target = Vector((-0.58, -0.1, 1.05))
# Camera looking from front-right
loc = Vector((-1.8, -2.4, 1.35))
cam.location = loc
cam.rotation_euler = (target - loc).to_track_quat("-Z", "Y").to_euler()

rig = next(o for o in bpy.data.objects if o.type == "ARMATURE")
rig.data.pose_position = "REST"
scene.frame_set(1)
bpy.context.view_layer.update()

out_fp = ROOT / "evidence/varek-v54-graviton/manipulator_closeup.png"
scene.render.filepath = str(out_fp)
bpy.ops.render.render(write_still=True)
print(f"Rendered: {out_fp}")
