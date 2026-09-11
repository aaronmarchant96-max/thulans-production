import bpy
from pathlib import Path

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v52-graviton.blend"

bpy.ops.wm.open_mainfile(filepath=str(SRC))
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
for name in ["upper_arm.R", "forearm.R", "hand.R"]:
    pb = arm.pose.bones[name]
    print(f"PoseBone {name}: loc={tuple(round(x,3) for x in pb.location)} head={tuple(round(x,3) for x in pb.head)} tail={tuple(round(x,3) for x in pb.tail)}")
