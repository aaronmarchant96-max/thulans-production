"""Probe the LEFT arm: hand mesh, wrist, held gadget, and animation pose."""
from __future__ import annotations
import sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path("/home/aaron/animation/thulans-production")
EXCLUDE = {"Studio floor", "Atmospheric_Forge_Haze"}


def wc(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return sum(pts, Vector()) / 8.0


def bounds(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    cand = Path(argv[0]) if argv else ROOT / "blender/candidates/varek-v51-functional.blend"
    if not cand.is_absolute():
        cand = ROOT / cand
    bpy.ops.wm.open_mainfile(filepath=str(cand))
    rig = next(o for o in bpy.data.objects if o.type == "ARMATURE")

    print("=== left-arm bound meshes ===")
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name in EXCLUDE:
            continue
        g = [vg.name for vg in o.vertex_groups]
        if any(n in ("hand.L", "forearm.L", "upper_arm.L") for n in g):
            mn, mx = bounds(o)
            print(f"  {o.name:34s} c=({wc(o).x:.2f},{wc(o).y:.2f},{wc(o).z:.2f}) "
                  f"z=[{mn.z:.2f},{mx.z:.2f}] g={g}")

    print("\n=== hand.L / tool animation (world head) ===")
    sc = bpy.context.scene
    act = rig.animation_data.action
    f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
    for f in range(f0, f1 + 1, 8):
        sc.frame_set(f)
        bpy.context.view_layer.update()
        h = rig.matrix_world @ rig.pose.bones["hand.L"].head
        print(f"  f={f:3d} hand.L=({h.x:+.3f},{h.y:+.3f},{h.z:+.3f})")

    print("\n=== bones parenting (tool) ===")
    b = rig.data.bones.get("tool")
    print(f"  tool parent={b.parent.name if b and b.parent else None}")

    print("\n=== meshes with 'gren'/'skildus'/'plaque'/'gadget' ===")
    for o in bpy.data.objects:
        if o.type == "MESH" and any(k in o.name.lower() for k in ("gren", "skildus", "plaque", "gadget", "slate", "canister")):
            print(f"  {o.name:34s} c=({wc(o).x:.2f},{wc(o).y:.2f},{wc(o).z:.2f}) g={[vg.name for vg in o.vertex_groups]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
