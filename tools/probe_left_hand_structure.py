import bpy
from pathlib import Path
from mathutils import Vector

v51 = Path("/home/aaron/animation/thulans-production/blender/candidates/varek-v51-functional.blend")
bpy.ops.wm.open_mainfile(filepath=str(v51))

hand_l = bpy.data.objects.get("Donor rescue hand L")
wrist_l = bpy.data.objects.get("Wrist coupling L")
forearm_l = bpy.data.objects.get("Donor forearm L")

print("\n=== LEFT HAND & FOREARM INSPECTION ===")
for obj in [forearm_l, wrist_l, hand_l]:
    if obj:
        print(f"\nObject: '{obj.name}'")
        print(f"  Location: {obj.location}")
        print(f"  Matrix World Translation: {obj.matrix_world.translation}")
        print(f"  Dimensions: {obj.dimensions}")
        print(f"  Parent: {obj.parent.name if obj.parent else 'None'}")
        print(f"  Vertex groups: {[vg.name for vg in obj.vertex_groups]}")
        print(f"  Modifiers: {[m.name + ' (' + m.type + ')' for m in obj.modifiers]}")

rig = bpy.data.objects.get("Varek simple articulation")
if rig:
    print(f"\nArmature '{rig.name}' Location: {rig.location}")
    for bname in ['forearm.L', 'hand.L']:
        b = rig.data.bones.get(bname)
        pb = rig.pose.bones.get(bname)
        if b and pb:
            print(f"  Bone '{bname}': head={b.head}, tail={b.tail}, matrix={pb.matrix.translation}")

