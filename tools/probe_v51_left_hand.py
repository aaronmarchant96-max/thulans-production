import bpy
from pathlib import Path

v51 = Path("/home/aaron/animation/thulans-production/blender/candidates/varek-v51-functional.blend")
bpy.ops.wm.open_mainfile(filepath=str(v51))

rig = bpy.data.objects.get("Varek simple articulation")
print("\n=== VAREK SIMPLE ARTICULATION BONES (LEFT ARM/HAND) ===")
if rig:
    for b in rig.data.bones:
        if any(k in b.name.lower() for k in ["forearm", "wrist", "hand", "digit", "finger", "thumb", "palm"]):
            print(f"Bone '{b.name}' (parent={b.parent.name if b.parent else 'None'}) head={b.head} tail={b.tail}")

print("\n=== LEFT HAND MESH OBJECTS IN V51 ===")
for o in bpy.data.objects:
    if o.type == 'MESH':
        name = o.name.lower()
        if any(k in name for k in ["hand", "wrist", "finger", "thumb", "palm", "maul", "haft"]) and not ".r" in name and not "_r" in name:
            print(f"Mesh '{o.name}' | Parent: {o.parent.name if o.parent else 'None'} | BBox dim: {o.dimensions}")

