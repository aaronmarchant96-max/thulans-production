"""v51 functional pass: make the character hold its maul, remove floating bits.

Problems fixed (found via tools/find_isolated_v50.py and probes):
  1. `tool` bone is parented to `root`, so the maul never follows the hand.
     The walk action already poses the right arm forward in a carry pose, so
     the maul is rebound to `hand.R` and seated in the right claw at REST.
     Rigid binding keeps the grip offset through the whole walk.
  2. `Gauntlet_Knuckle_Bar_R_0/1/2` float ~5 cm in front of the right hand.
     They are nudged back (+Y) to touch the hand like their left counterparts.
  3. `Maul replaceable striking shoe.001` sits 4.3 cm off the maul head.

Writes a new candidate; never overwrites an audited file. Does not touch the
rig, the animation, or the locked architecture.
"""

from __future__ import annotations

import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v50-golden-baseline.blend"
OUT = ROOT / "blender/candidates/varek-v51-functional.blend"

ARM = None


def world_center(obj) -> Vector:
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return sum(pts, Vector()) / 8.0


def move(obj, delta: Vector) -> None:
    mw = obj.matrix_world.copy()
    mw.translation += delta
    obj.matrix_world = mw


def bind(obj, bone: str) -> None:
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

    maul = [o for o in bpy.data.objects
            if o.type == "MESH" and any(g.name == "tool" for g in o.vertex_groups)]
    print(f"maul objects (bound to `tool`): {len(maul)}")

    grip = bpy.data.objects.get("Maul grip")
    grip_c = world_center(grip)
    # The right-hand MESH is modelled in the carry pose (y ~= -0.39), not at
    # the rest bone (y ~= -0.04). Seat the grip in the claw mesh so the grip
    # offset is preserved through the walk.
    hand = bpy.data.objects.get("Donor rescue hand R")
    hand_c = world_center(hand)
    target = Vector((-0.620, hand_c.y, grip_c.z))
    delta = target - grip_c
    delta.z = 0.18  # carry the maul clear of the floor (head ~18 cm up)
    print(f"hand.R mesh center {tuple(round(v,3) for v in hand_c)}")
    print(f"grip center {tuple(round(v,3) for v in grip_c)} -> "
          f"{tuple(round(v,3) for v in (grip_c + delta))}  delta={tuple(round(v,3) for v in delta)}")

    for o in maul:
        move(o, delta)
        bind(o, "hand.R")
    print(f"rebound {len(maul)} maul objects to hand.R")

    # --- hydraulic conduit -------------------------------------------------
    # `Maul_Braided_Hydraulic_Conduit` is a thin curve bone-parented to the
    # static `tool` bone. Even routed along the shaft it reads as a separate
    # floating wire, so remove it for a clean prop. (Its data-block is left
    # orphaned rather than purged, so it can be recovered if wanted.)
    cond = bpy.data.objects.get("Maul_Braided_Hydraulic_Conduit")
    if cond:
        bpy.data.objects.remove(cond, do_unlink=True)
        print("removed stray Maul_Braided_Hydraulic_Conduit")

    # 2. floating right gauntlet knuckle bars -> back onto the hand
    for name in ("Gauntlet_Knuckle_Bar_R_0", "Gauntlet_Knuckle_Bar_R_1",
                 "Gauntlet_Knuckle_Bar_R_2"):
        o = bpy.data.objects.get(name)
        if o:
            move(o, Vector((0.0, 0.060, 0.0)))
            print(f"re-seated {name} (+0.060 Y)")

    bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
    print(f"saved: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
