import bpy
from pathlib import Path

ROOT = Path("/home/aaron/animation/thulans-production")
DONOR = ROOT / "assets/donors/quaternius-mechs/Animated Mech Pack - March 2021/Blends/Mike.blend"

bpy.ops.wm.open_mainfile(filepath=str(DONOR))
mesh = next(o for o in bpy.data.objects if o.type == "MESH")
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
print("Mesh:", mesh.name, "verts:", len(mesh.data.vertices))
print("Vertex groups:")
for vg in mesh.vertex_groups:
    if any(k in vg.name for k in ["Hand", "Palm", "Index", "Ring", "Pinky", "Thumb", "Wrist"]):
        print(f"  {vg.name} (index {vg.index})")

print("Bones:")
for b in arm.data.bones:
    if any(k in b.name for k in ["Hand", "Palm", "Index", "Ring", "Pinky", "Thumb", "Wrist"]):
        print(f"  {b.name} head={tuple(round(x,3) for x in b.head)} tail={tuple(round(x,3) for x in b.tail)}")
