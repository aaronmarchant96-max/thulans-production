"""Locate hands, tool bone, and detached/floating objects.

Run:
  flatpak run --filesystem=host org.blender.Blender --background \
    --python-exit-code 1 --python tools/probe_v50_hands.py -- \
    blender/candidates/varek-v50-golden-baseline.blend
"""

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
    cand = Path(argv[0]) if argv else ROOT / "blender/candidates/varek-v50-golden-baseline.blend"
    if not cand.is_absolute():
        cand = ROOT / cand
    bpy.ops.wm.open_mainfile(filepath=str(cand))
    rig = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    print(f"candidate: {cand}")
    print(f"rig: {rig.name}")

    print("\n=== BONES (world head/tail, rest) ===")
    for b in rig.data.bones:
        h = rig.matrix_world @ b.head_local
        t = rig.matrix_world @ b.tail_local
        print(f"  {b.name:14s} head={tuple(round(v,3) for v in h)} tail={tuple(round(v,3) for v in t)}")

    print("\n=== HAND / TOOL region meshes ===")
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name in EXCLUDE:
            continue
        grp = [g.name for g in o.vertex_groups]
        if any(g in ("hand.L", "hand.R", "tool", "forearm.L", "forearm.R") for g in grp):
            print(f"  {o.name:40s} center={tuple(round(v,3) for v in wc(o))} "
                  f"bounds={tuple(round(v,2) for v in bounds(o)[0])}..{tuple(round(v,2) for v in bounds(o)[1])} groups={grp}")

    print("\n=== ISOLATED objects (no other mesh within 0.12m) ===")
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and o.name not in EXCLUDE]
    centers = [(o, wc(o)) for o in meshes]
    for o, c in centers:
        near = 0
        for o2, c2 in centers:
            if o2 is o:
                continue
            if (c - c2).length < 0.12:
                near += 1
        if near == 0:
            print(f"  ISOLATED {o.name:40s} center={tuple(round(v,3) for v in c)} groups={[g.name for g in o.vertex_groups]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
