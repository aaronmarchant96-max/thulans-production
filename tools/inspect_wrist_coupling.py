import bpy
from pathlib import Path
from mathutils import Vector

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v52-graviton.blend"

bpy.ops.wm.open_mainfile(filepath=str(SRC))
wc = bpy.data.objects.get("Wrist coupling R")
if wc:
    print("Wrist coupling R:", wc.name)
    print("  matrix_world:", wc.matrix_world.translation)
    bb = [wc.matrix_world @ Vector(b) for b in wc.bound_box]
    mn = Vector((min(p.x for p in bb), min(p.y for p in bb), min(p.z for p in bb)))
    mx = Vector((max(p.x for p in bb), max(p.y for p in bb), max(p.z for p in bb)))
    print(f"  bounds min={tuple(round(v,3) for v in mn)} max={tuple(round(v,3) for v in mx)}")
    print(f"  center={tuple(round(v,3) for v in (mn+mx)/2)}")

arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
hand_r = arm.data.bones.get("hand.R")
if hand_r:
    print(f"hand.R head (bone local)={hand_r.head}")
    print(f"hand.R head (armature space)={hand_r.matrix_local.translation}")
    print(f"hand.R head (world)={arm.matrix_world @ hand_r.matrix_local.translation}")
