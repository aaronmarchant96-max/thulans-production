"""Find isolated objects: build adjacency (AABB gap < tol) and report singletons."""
from __future__ import annotations
import sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path("/home/aaron/animation/thulans-production")
EXCLUDE = {"Studio floor", "Atmospheric_Forge_Haze"}
TOL = 0.02


def bounds(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))


def gap(a, b):
    (amn, amx), (bmn, bmx) = a, b
    dx = max(amn.x - bmx.x, bmn.x - amx.x, 0.0)
    dy = max(amn.y - bmx.y, bmn.y - amx.y, 0.0)
    dz = max(amn.z - bmx.z, bmn.z - amx.z, 0.0)
    return (dx * dx + dy * dy + dz * dz) ** 0.5


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    cand = Path(argv[0]) if argv else ROOT / "blender/candidates/varek-v50-golden-baseline.blend"
    if not cand.is_absolute():
        cand = ROOT / cand
    bpy.ops.wm.open_mainfile(filepath=str(cand))
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and o.name not in EXCLUDE]
    B = {o.name: bounds(o) for o in meshes}
    names = list(B)
    adj = {n: set() for n in names}
    nearest = {}
    for i, a in enumerate(names):
        best = (1e9, None)
        for b in names:
            if a == b:
                continue
            g = gap(B[a], B[b])
            if g < best[0]:
                best = (g, b)
            if g <= TOL:
                adj[a].add(b)
                adj[b].add(a)
        nearest[a] = best

    seen = set()
    comps = []
    for n in names:
        if n in seen:
            continue
        stack = [n]
        seen.add(n)
        comp = []
        while stack:
            c = stack.pop()
            comp.append(c)
            for m in adj[c]:
                if m not in seen:
                    seen.add(m)
                    stack.append(m)
        comps.append(comp)

    print(f"objects={len(names)} components={len(comps)}")
    print("\n=== SINGLETON components (isolated) ===")
    for comp in sorted(comps, key=len):
        if len(comp) == 1:
            n = comp[0]
            g, b = nearest[n]
            c = (B[n][0] + B[n][1]) / 2
            print(f"  {n:40s} c=({c.x:.2f},{c.y:.2f},{c.z:.2f}) nearest={b} gap={g:.3f}")

    print("\n=== largest components ===")
    for comp in sorted(comps, key=len, reverse=True)[:5]:
        print(f"  size={len(comp)}: {sorted(comp)[:6]}{'...' if len(comp)>6 else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
