import bpy
from pathlib import Path
from mathutils import Vector

ROOT = Path("/home/aaron/animation/thulans-production")
DONOR = ROOT / "assets/donors/quaternius-mechs/Animated Mech Pack - March 2021/Blends/Mike.blend"

bpy.ops.wm.open_mainfile(filepath=str(DONOR))
mesh = next(o for o in bpy.data.objects if o.type == "MESH")

groups_3talons = [
    "PalmI.R", "Index1.R", "Index2.R",
    "PalmR.R", "Ring1.R", "Ring2.R",
    "PalmP.R", "Pinky1.R", "Pinky2.R"
]

v_indices = set()
for gname in groups_3talons:
    vg = mesh.vertex_groups.get(gname)
    if vg:
        for v in mesh.data.vertices:
            for g in v.groups:
                if g.group == vg.index and g.weight > 0.1:
                    v_indices.add(v.index)

print(f"Total verts in 3 talons (no thumb): {len(v_indices)}")
coords = [mesh.data.vertices[i].co for i in v_indices]
mn = Vector((min(p.x for p in coords), min(p.y for p in coords), min(p.z for p in coords)))
mx = Vector((max(p.x for p in coords), max(p.y for p in coords), max(p.z for p in coords)))
print(f"Bounds: min={tuple(round(x,3) for x in mn)} max={tuple(round(x,3) for x in mx)} size={tuple(round(x,3) for x in (mx-mn))}")
