import bpy
from pathlib import Path

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v52-graviton.blend"

bpy.ops.wm.open_mainfile(filepath=str(SRC))
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
action = arm.animation_data.action if arm.animation_data else None
if action:
    print("Action:", action.name)
    finger_fcurves = [fc for fc in action.fcurves if "finger.R" in fc.data_path]
    print(f"Total finger.R fcurves: {len(finger_fcurves)}")
    for fc in finger_fcurves[:10]:
        print(f"  {fc.data_path}[{fc.array_index}] keyframes: {len(fc.keyframe_points)}")
else:
    print("No action found")
