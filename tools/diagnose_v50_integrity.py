"""Integrity diagnostic: floating pieces + limb binding sanity.

Reports, for every mesh in a candidate:
  - whether it has an ARMATURE modifier and which bones drive it
  - its world center / bounds
  - number of disconnected loose islands
  - distance from the overall character bounds (far => likely floating)

Run:
  flatpak run --filesystem=host org.blender.Blender --background \
    --python-exit-code 1 --python tools/diagnose_v50_integrity.py -- \
    blender/candidates/varek-v50-golden-baseline.blend
"""

from __future__ import annotations

import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector

ROOT = Path("/home/aaron/animation/thulans-production")
EXCLUDE = {"Studio floor", "Atmospheric_Forge_Haze"}


def world_center(obj) -> Vector:
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return sum(pts, Vector()) / 8.0


def world_bounds(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx


def islands(obj) -> int:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    seen = set()
    count = 0
    for v in bm.verts:
        if v.index in seen:
            continue
        count += 1
        stack = [v]
        seen.add(v.index)
        while stack:
            cur = stack.pop()
            for e in cur.link_edges:
                o = e.other_vert(cur)
                if o.index not in seen:
                    seen.add(o.index)
                    stack.append(o)
    bm.free()
    return count


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    candidate = Path(argv[0]) if argv else (
        ROOT / "blender/candidates/varek-v50-golden-baseline.blend"
    )
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    bpy.ops.wm.open_mainfile(filepath=str(candidate))

    arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    rig = arms[0]
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and o.name not in EXCLUDE]

    gmin = Vector((1e9, 1e9, 1e9))
    gmax = Vector((-1e9, -1e9, -1e9))
    for o in meshes:
        mn, mx = world_bounds(o)
        for i in range(3):
            gmin[i] = min(gmin[i], mn[i])
            gmax[i] = max(gmax[i], mx[i])
    diag = (gmax - gmin).length
    print(f"candidate: {candidate}")
    print(f"rig: {rig.name} bones={len(rig.data.bones)}")
    print(f"character bounds: min={tuple(round(v,3) for v in gmin)} "
          f"max={tuple(round(v,3) for v in gmax)} diag={diag:.3f}")
    print(f"meshes: {len(meshes)}")

    unbound = []
    floating = []
    multi_island = []
    for o in sorted(meshes, key=lambda x: x.name):
        has_arm = any(m.type == "ARMATURE" for m in o.modifiers)
        groups = [g.name for g in o.vertex_groups]
        c = world_center(o)
        n_isl = islands(o)
        if not has_arm:
            unbound.append((o.name, tuple(round(v, 3) for v in c)))
        # distance from global center, normalized by diag
        gc = (gmin + gmax) / 2.0
        d = (c - gc).length
        if d > 0.6 * diag:
            floating.append((o.name, round(d, 3), tuple(round(v, 3) for v in c)))
        if n_isl > 1:
            multi_island.append((o.name, n_isl, len(o.data.vertices)))

    print(f"\n=== UNBOUND ({len(unbound)}) ===")
    for n, c in unbound:
        print(f"  {n}  center={c}")

    print(f"\n=== FAR-FROM-BODY / possibly floating ({len(floating)}) ===")
    for n, d, c in floating:
        print(f"  {n}  dist={d}  center={c}")

    print(f"\n=== MULTI-ISLAND meshes ({len(multi_island)}) ===")
    for n, k, v in sorted(multi_island, key=lambda x: -x[1]):
        print(f"  {n}  islands={k}  verts={v}")

    print("\n=== BINDING MAP ===")
    for o in sorted(meshes, key=lambda x: x.name):
        groups = [g.name for g in o.vertex_groups]
        if groups:
            print(f"  {o.name}: {groups}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
