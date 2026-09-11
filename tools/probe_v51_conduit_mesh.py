"""Probe the converted conduit mesh: object matrix + local vertex bounds."""
from __future__ import annotations
import sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path("/home/aaron/animation/thulans-production")


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    cand = Path(argv[0]) if argv else ROOT / "blender/candidates/varek-v51-functional.blend"
    if not cand.is_absolute():
        cand = ROOT / cand
    bpy.ops.wm.open_mainfile(filepath=str(cand))
    o = bpy.data.objects.get("Maul_Braided_Hydraulic_Conduit")
    if not o:
        print("no conduit")
        return 0
    print(f"type={o.type} parent={o.parent} parent_type={o.parent_type} "
          f"parent_bone={o.parent_bone}")
    print("matrix_world:")
    for row in o.matrix_world:
        print("   ", tuple(round(v, 4) for v in row))
    me = o.data
    print(f"verts={len(me.vertices)} polys={len(me.polygons)}")
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for v in me.vertices:
        for i in range(3):
            mn[i] = min(mn[i], v.co[i])
            mx[i] = max(mx[i], v.co[i])
    print(f"local bounds min={tuple(round(v,3) for v in mn)} max={tuple(round(v,3) for v in mx)}")
    wmn = Vector((1e9, 1e9, 1e9))
    wmx = Vector((-1e9, -1e9, -1e9))
    for v in me.vertices:
        w = o.matrix_world @ v.co
        for i in range(3):
            wmn[i] = min(wmn[i], w[i])
            wmx[i] = max(wmx[i], w[i])
    print(f"world bounds min={tuple(round(v,3) for v in wmn)} max={tuple(round(v,3) for v in wmx)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
