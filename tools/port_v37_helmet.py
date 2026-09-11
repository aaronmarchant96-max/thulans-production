"""Port the canonical curved Operator_Pressure_Helmet from v37 into v49.

Replaces the v48 "duckbill" brow pieces:
  - removes Varek_Helmet_BrowGuard, Helmet_Reinforced_Brow_Armor
  - appends Operator_Pressure_Helmet + visor frame/slit from v37
  - scales them to fit the v48 cranium and seats them on the head
  - binds rigidly to the `head` bone
"""

from __future__ import annotations

import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v49-visual-cleanup.blend"
V37 = ROOT / "blender/candidates/varek-v37-helmet-final.blend"

PORT = [
    "Operator_Pressure_Helmet",
    "Operator_Visor_Aperture_Frame",
    "Operator_Visor_Optical_Slit",
    "Operator_Respirator_Boss_L",
    "Operator_Respirator_Boss_R",
]
REMOVE = ["Varek_Helmet_BrowGuard", "Helmet_Reinforced_Brow_Armor"]
ARM = None


def wb(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))


def bind(obj, bone):
    obj.parent = None
    obj.parent_type = "OBJECT"
    obj.matrix_parent_inverse.identity()
    obj.vertex_groups.clear()
    g = obj.vertex_groups.new(name=bone)
    g.add(list(range(len(obj.data.vertices))), 1.0, "REPLACE")
    if not any(m.type == "ARMATURE" for m in obj.modifiers):
        obj.modifiers.new("Armature", "ARMATURE")
    for m in obj.modifiers:
        if m.type == "ARMATURE":
            m.object = ARM
    obj["rigid_driver_bone"] = bone


def main() -> int:
    global ARM
    bpy.ops.wm.open_mainfile(filepath=str(SRC))
    ARM = next(o for o in bpy.data.objects if o.type == "ARMATURE")

    cranium = bpy.data.objects["Varek_Helmet_Cranium"]
    cmn, cmx = wb(cranium)
    c_center = (cmn + cmx) / 2.0
    c_width = cmx.x - cmn.x
    print(f"v48 cranium center=({c_center.x:.3f},{c_center.y:.3f},{c_center.z:.3f}) width={c_width:.3f}")

    # append the v37 helmet objects
    for name in PORT:
        bpy.ops.wm.append(
            filepath=str(V37),
            directory=str(V37) + "/Object/",
            filename=name,
        )
    appended = [bpy.data.objects.get(n) for n in PORT if bpy.data.objects.get(n)]
    print(f"appended: {[o.name for o in appended]}")

    # scale to the cranium width
    hel = bpy.data.objects["Operator_Pressure_Helmet"]
    hmn, hmx = wb(hel)
    h_width = hmx.x - hmn.x
    s = c_width / h_width
    print(f"v37 helmet width={h_width:.3f} -> scale={s:.4f}")

    for o in appended:
        o.scale = (o.scale.x * s, o.scale.y * s, o.scale.z * s)
    bpy.context.view_layer.update()

    # seat: align the pressure-helmet shell centre to the cranium centre
    hmn, hmx = wb(hel)
    delta = c_center - (hmn + hmx) / 2.0
    for o in appended:
        o.location += delta
    bpy.context.view_layer.update()
    hmn, hmx = wb(hel)
    print(f"seated helmet z[{hmn.z:.3f},{hmx.z:.3f}] x[{hmn.x:.3f},{hmx.x:.3f}] y[{hmn.y:.3f},{hmx.y:.3f}]")

    for o in appended:
        bind(o, "head")

    for n in REMOVE:
        o = bpy.data.objects.get(n)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)
            print(f"removed {n}")

    bpy.ops.wm.save_as_mainfile(filepath=str(SRC))
    print(f"saved: {SRC}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
