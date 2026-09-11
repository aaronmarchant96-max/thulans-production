"""Inspect the conduit curve points + list armatures."""
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

    print("=== ARMATURES ===")
    for o in bpy.data.objects:
        if o.type == "ARMATURE":
            n_mesh_bound = sum(
                1 for m in bpy.data.objects
                if m.type == "MESH" and any(md.type == "ARMATURE" and md.object == o for md in m.modifiers)
            )
            print(f"  {o.name} bones={len(o.data.bones)} meshes_bound={n_mesh_bound} "
                  f"parent={o.parent.name if o.parent else None}")

    o = bpy.data.objects.get("Maul_Braided_Hydraulic_Conduit")
    if not o:
        print("no conduit")
        return 0
    print(f"\n=== CONDUIT ===\n  parent={o.parent} parent_type={o.parent_type} "
          f"matrix_world.translation={tuple(round(v,3) for v in o.matrix_world.translation)}")
    print(f"  dimensions={tuple(round(v,3) for v in o.dimensions)}")
    for si, sp in enumerate(o.data.splines):
        if sp.type == "BEZIER":
            cps = sp.bezier_points
        else:
            cps = sp.points
        print(f"  spline {si}: type={sp.type} points={len(cps)}")
        for p in cps:
            local = Vector(p.co[:3])
            world = o.matrix_world @ local
            print(f"    local=({local.x:+.3f},{local.y:+.3f},{local.z:+.3f}) "
                  f"world=({world.x:+.3f},{world.y:+.3f},{world.z:+.3f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
