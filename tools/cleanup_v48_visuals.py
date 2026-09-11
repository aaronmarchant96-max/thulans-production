"""Visual cleanup pass on v48-baseline-green (authorized contract override).

Fixes defects the clearance gate cannot see:
  1. Floating maul parts (pommel ring, inscribed cheek plates) parked at
     y ~= -1.62 -- re-seat onto the maul and bind to the `tool` bone.
  2. Foot toe cleats unbound and mis-placed -- re-seat onto the toes and bind
     to foot.L / foot.R.
  3. Other unbound foot armour (Foot_Side_Armor_L) -- bind to its foot bone.

Writes a new candidate; never overwrites the audited baseline.
Does NOT touch the rig, animation, or locked architecture.
"""

from __future__ import annotations

import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v48-baseline-green.blend"
OUT = ROOT / "blender/candidates/varek-v49-visual-cleanup.blend"

# maul axis at REST (from the `tool` bone): x=-0.8542, y=-0.1689
MAUL_X, MAUL_Y = -0.8542, -0.1689

ARM = None


def world_center(obj) -> Vector:
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return sum(pts, Vector()) / 8.0


def seat(obj, target: Vector, bone: str) -> None:
    """Unparent (keeping world), translate mesh center to target, bind rigid."""
    mw = obj.matrix_world.copy()
    obj.parent = None
    obj.parent_type = "OBJECT"
    obj.matrix_parent_inverse.identity()
    obj.matrix_world = mw
    obj.matrix_world.translation += (target - world_center(obj))

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
    print(f"source: {SRC}")

    # --- 1. floating maul parts -> maul head / shaft, bound to `tool` --------
    maul_targets = {
        "Maul_Pommel_Recovery_Ring": Vector((MAUL_X, MAUL_Y, 1.271)),
        "Maul_Inscribed_CheekPlate_Top": Vector((MAUL_X, MAUL_Y - 0.048, 0.245)),
        "Maul_Inscribed_CheekPlate_Bottom": Vector((MAUL_X, MAUL_Y + 0.048, 0.245)),
    }
    for name, tgt in maul_targets.items():
        o = bpy.data.objects.get(name)
        if o:
            seat(o, tgt, "tool")
            print(f"seated {name} -> ({tgt.x:.3f},{tgt.y:.3f},{tgt.z:.3f})")

    conduit = bpy.data.objects.get("Maul_Braided_Hydraulic_Conduit")
    if conduit:
        print(f"conduit type={conduit.type} parent={conduit.parent} "
              f"center={tuple(round(v,3) for v in world_center(conduit))}")

    # --- 2. toe cleats -> toes, bound to the foot bones ---------------------
    for side, fx in (("L", 0.258), ("R", -0.258)):
        for i, ty in enumerate((-0.255, -0.315, -0.375)):
            name = f"Foot_Toe_Cleat_{side}_{i}"
            o = bpy.data.objects.get(name)
            if o:
                seat(o, Vector((fx, ty, 0.030)), f"foot.{side}")
                print(f"seated {name} -> ({fx:.3f},{ty:.3f},0.030)")

    # --- 3. other unbound foot armour ---------------------------------------
    fsa = bpy.data.objects.get("Foot_Side_Armor_L")
    if fsa:
        seat(fsa, world_center(fsa), "foot.L")
        print("bound Foot_Side_Armor_L -> foot.L")

    # --- report remaining unbound meshes near the body ----------------------
    unbound = []
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name in ("Studio floor", "Atmospheric_Forge_Haze"):
            continue
        if not any(m.type == "ARMATURE" for m in o.modifiers):
            c = world_center(o)
            unbound.append((o.name, round(c.x, 2), round(c.y, 2), round(c.z, 2)))
    print(f"remaining unbound meshes: {len(unbound)}")
    for n, x, y, z in unbound[:40]:
        print(f"   UNBOUND {n} ({x},{y},{z})")

    bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
    print(f"saved: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
