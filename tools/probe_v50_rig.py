"""Rig hierarchy + hunt for stray thin/curved geometry."""
from __future__ import annotations
import sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path("/home/aaron/animation/thulans-production")


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
    rig = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    print("=== BONE PARENTS ===")
    for b in rig.data.bones:
        print(f"  {b.name:16s} parent={b.parent.name if b.parent else None}")
    print("\n=== THIN/LONG objects (aspect > 6, low or detached) ===")
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        mn, mx = bounds(o)
        d = mx - mn
        dims = sorted([d.x, d.y, d.z])
        if dims[0] < 1e-6:
            continue
        aspect = dims[2] / max(dims[0], 1e-6)
        if aspect > 6:
            c = (mn + mx) / 2
            print(f"  {o.name:40s} d=({d.x:.3f},{d.y:.3f},{d.z:.3f}) c=({c.x:.2f},{c.y:.2f},{c.z:.2f}) g={[g.name for g in o.vertex_groups]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
