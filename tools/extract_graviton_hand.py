"""Extract the donor right manipulator hand from Mike.blend (CC0 Quaternius).

Keeps only the right-hand + wrist vertex groups, removes everything else,
saves a clean single-mesh extract with its bounds printed for the fit step.
"""

from __future__ import annotations

import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path("/home/aaron/animation/thulans-production")
DONOR = ROOT / "assets/donors/quaternius-mechs/Animated Mech Pack - March 2021/Blends/Mike.blend"
OUT = ROOT / "assets/donors/graviton-manipulator-R.blend"

HAND_GROUPS = [
    "PalmP.R", "PalmR.R", "PalmI.R", "PalmT.R",
    "Pinky1.R", "Pinky2.R", "Ring1.R", "Ring2.R",
    "Index1.R", "Index2.R", "Thumb1.R", "Thumb2.R",
]


def bounds(obj):
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for v in obj.data.vertices:
        for i in range(3):
            mn[i] = min(mn[i], v.co[i])
            mx[i] = max(mx[i], v.co[i])
    return mn, mx


def main() -> int:
    bpy.ops.wm.open_mainfile(filepath=str(DONOR))
    mesh = next(o for o in bpy.data.objects if o.type == "MESH")
    print(f"donor mesh: {mesh.name} verts={len(mesh.data.vertices)}")

    # keep only the right-hand vertex groups
    keep = [vg for vg in mesh.vertex_groups if vg.name in HAND_GROUPS]
    print(f"hand groups found: {len(keep)} / {len(HAND_GROUPS)}")

    bpy.context.view_layer.objects.active = mesh
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="DESELECT")
    for vg in keep:
        mesh.vertex_groups.active_index = vg.index
        bpy.ops.object.vertex_group_select()
    bpy.ops.mesh.select_all(action="INVERT")
    bpy.ops.mesh.delete(type="VERT")
    bpy.ops.object.mode_set(mode="OBJECT")

    mesh.name = "Graviton_Manipulator_R"
    print(f"extracted verts={len(mesh.data.vertices)}")

    # drop the donor armature and everything else
    for o in [x for x in bpy.data.objects if x is not mesh]:
        bpy.data.objects.remove(o, do_unlink=True)

    mn, mx = bounds(mesh)
    dim = mx - mn
    print(f"bounds min={tuple(round(v,3) for v in mn)} max={tuple(round(v,3) for v in mx)}")
    print(f"size=({dim.x:.3f},{dim.y:.3f},{dim.z:.3f})")

    bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
    print(f"saved: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
