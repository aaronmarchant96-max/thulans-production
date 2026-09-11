import bpy
from pathlib import Path
from mathutils import Vector

ROOT = Path("/home/aaron/animation/thulans-production")
DONOR = ROOT / "assets/donors/quaternius-mechs/Animated Mech Pack - March 2021/Blends/Mike.blend"

bpy.ops.wm.open_mainfile(filepath=str(DONOR))
mesh = next(o for o in bpy.data.objects if o.type == "MESH")

for prefix in ["PalmI.R", "PalmR.R", "PalmP.R", "PalmT.R"]:
    vg = mesh.vertex_groups.get(prefix)
    if vg:
        v_indices = [v.index for v in mesh.data.vertices if any(g.group == vg.index and g.weight > 0.1 for g in v.groups)]
        if v_indices:
            coords = [mesh.data.vertices[i].co for i in v_indices]
            mn = Vector((min(p.x for p in coords), min(p.y for p in coords), min(p.z for p in coords)))
            mx = Vector((max(p.x for p in coords), max(p.y for p in coords), max(p.z for p in coords)))
            print(f"{prefix:10}: {len(v_indices)} verts, bounds min={tuple(round(x,3) for x in mn)} max={tuple(round(x,3) for x in mx)}")
