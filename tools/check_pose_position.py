import bpy
from pathlib import Path

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v52-graviton.blend"

bpy.ops.wm.open_mainfile(filepath=str(SRC))
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
print("arm.data.pose_position:", arm.data.pose_position)
