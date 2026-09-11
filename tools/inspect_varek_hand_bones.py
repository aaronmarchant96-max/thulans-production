import bpy
from pathlib import Path

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v52-graviton.blend"

bpy.ops.wm.open_mainfile(filepath=str(SRC))
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
print("Varek Armature:", arm.name)
bones = [b.name for b in arm.data.bones if any(k in b.name.lower() for k in ["hand.r", "finger.r", "wrist.r", "thumb.r"])]
for b in sorted(bones):
    bone = arm.data.bones[b]
    parent = bone.parent.name if bone.parent else "None"
    print(f"  {b:20} parent={parent:20} head={tuple(round(x,3) for x in bone.head)} tail={tuple(round(x,3) for x in bone.tail)}")
