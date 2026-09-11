import bpy
from pathlib import Path

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v52-graviton.blend"

bpy.ops.wm.open_mainfile(filepath=str(SRC))
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
action = arm.animation_data.action if arm.animation_data else None
if action:
    print("action type:", type(action), dir(action))
    if hasattr(action, "layers"):
        for l in action.layers:
            print(" layer:", l.name)
            for s in l.strips:
                print("   strip:", s.name)
                for cb in s.channelbags:
                    print("     channelbag:", cb)
                    for f in cb.fcurves:
                        if "finger.R" in f.data_path:
                            print("       fcurve:", f.data_path, f.array_index)
