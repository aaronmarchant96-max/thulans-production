"""List all objects by type; flag curves/empties and unbound objects."""
from __future__ import annotations
import sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path("/home/aaron/animation/thulans-production")


def wc(o):
    try:
        pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
        return sum(pts, Vector()) / 8.0
    except Exception:
        return Vector((0, 0, 0))


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    cand = Path(argv[0]) if argv else ROOT / "blender/candidates/varek-v51-functional.blend"
    if not cand.is_absolute():
        cand = ROOT / cand
    bpy.ops.wm.open_mainfile(filepath=str(cand))
    from collections import Counter
    types = Counter(o.type for o in bpy.data.objects)
    print(f"object types: {dict(types)}")
    for o in bpy.data.objects:
        if o.type not in ("MESH", "ARMATURE"):
            c = wc(o)
            print(f"  {o.type:8s} {o.name:40s} parent={o.parent.name if o.parent else None} "
                  f"c=({c.x:.2f},{c.y:.2f},{c.z:.2f})")
    print("\nobjects with 'conduit/hose/braid/line/pipe/tube/cable' in name:")
    for o in bpy.data.objects:
        n = o.name.lower()
        if any(k in n for k in ("conduit", "hose", "braid", "pipe", "tube", "cable", "wire", "cord")):
            c = wc(o)
            mods = [m.type for m in o.modifiers]
            print(f"  {o.type:8s} {o.name:40s} c=({c.x:.2f},{c.y:.2f},{c.z:.2f}) "
                  f"g={[g.name for g in o.vertex_groups]} mods={mods}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
