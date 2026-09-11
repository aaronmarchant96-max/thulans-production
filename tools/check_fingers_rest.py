import bpy
from pathlib import Path

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v52-graviton.blend"

bpy.ops.wm.open_mainfile(filepath=str(SRC))
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
arm.data.pose_position = "REST"
bpy.context.view_layer.update()

for b in sorted([b.name for b in arm.data.bones if "finger" in b.name.lower() and ".r" in b.name.lower()]):
    pb = arm.pose.bones[b]
    print(f"REST {b:15}: head={tuple(round(x,3) for x in pb.head)} tail={tuple(round(x,3) for x in pb.tail)}")
