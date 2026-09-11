import bpy
from pathlib import Path
from mathutils import Vector

ROOT = Path("/home/aaron/animation/thulans-production")
DONOR = ROOT / "assets/donors/quaternius-mechs/Animated Mech Pack - March 2021/Blends/Mike.blend"

bpy.ops.wm.open_mainfile(filepath=str(DONOR))
mesh = next(o for o in bpy.data.objects if o.type == "MESH")

vg_idx1 = mesh.vertex_groups.get("Index1.R").index
vg_idx2 = mesh.vertex_groups.get("Index2.R").index
vg_palm = mesh.vertex_groups.get("PalmI.R").index

v_idx1 = [v.co.copy() for v in mesh.data.vertices if any(g.group == vg_idx1 and g.weight > 0.1 for g in v.groups)]
v_idx2 = [v.co.copy() for v in mesh.data.vertices if any(g.group == vg_idx2 and g.weight > 0.1 for g in v.groups)]
v_palm = [v.co.copy() for v in mesh.data.vertices if any(g.group == vg_palm and g.weight > 0.1 for g in v.groups)]

all_v = v_idx1 + v_idx2 + v_palm
base = sum(v_palm, Vector()) / len(v_palm)
tip = sum(v_idx2, Vector()) / len(v_idx2)
print(f"Index talon: {len(all_v)} verts")
print(f"  base centroid (in Mike): {tuple(round(x,3) for x in base)}")
print(f"  tip centroid (in Mike): {tuple(round(x,3) for x in tip)}")
print(f"  vector from base to tip: {tuple(round(x,3) for x in (tip - base))}")
print(f"  length: {(tip - base).length:.3f} m (scaled 0.28: {(tip - base).length * 0.28:.3f} m)")
