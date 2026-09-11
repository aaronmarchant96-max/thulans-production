"""Dump every mesh with world bounds as CSV for review."""
from __future__ import annotations
import sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path("/home/aaron/animation/thulans-production")
EXCLUDE = {"Studio floor", "Atmospheric_Forge_Haze"}


def bounds(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    cand = Path(argv[0]) if argv else ROOT / "blender/candidates/varek-v50-golden-baseline.blend"
    if not cand.is_absolute():
        cand = ROOT / cand
    bpy.ops.wm.open_mainfile(filepath=str(cand))
    rows = []
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name in EXCLUDE:
            continue
        mn, mx = bounds(o)
        c = (mn + mx) / 2
        dim = mx - mn
        rows.append((o.name, c, dim, mn, mx, [g.name for g in o.vertex_groups]))
    rows.sort(key=lambda r: r[1].z)
    for n, c, d, mn, mx, g in rows:
        print(f"{n}\t"
              f"c=({c.x:.3f},{c.y:.3f},{c.z:.3f})\t"
              f"d=({d.x:.3f},{d.y:.3f},{d.z:.3f})\t"
              f"z=[{mn.z:.3f},{mx.z:.3f}]\tg={g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
