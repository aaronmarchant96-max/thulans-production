import bpy
from pathlib import Path

ROOT = Path("/home/aaron/animation/thulans-production")
DONOR = ROOT / "assets/donors/quaternius-mechs/Animated Mech Pack - March 2021/Blends/Mike.blend"

bpy.ops.wm.open_mainfile(filepath=str(DONOR))
mesh = next(o for o in bpy.data.objects if o.type == "MESH")
for vg in mesh.vertex_groups:
    if ".R" in vg.name:
        v_indices = [v.index for v in mesh.data.vertices if any(g.group == vg.index and g.weight > 0.1 for g in v.groups)]
        print(f"  {vg.name:15}: {len(v_indices)} verts")
