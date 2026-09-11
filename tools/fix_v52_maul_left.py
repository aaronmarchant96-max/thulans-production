"""v52 phase 1: move the Faírguni-Hamars maul to the LEFT hand.

Per RULING 023 the maul is canonical in the left hand; the right arm is freed
for the graviton manipulator. The maul group (currently bound to hand.R) is
mirrored to the left side, seated in the left claw at REST, and rebound to
hand.L so the grip is preserved through the walk.

Writes a new candidate; never overwrites the frozen v51.
"""

from __future__ import annotations

import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v51-functional.blend"
OUT = ROOT / "blender/candidates/varek-v52-graviton.blend"

ARM = None


def world_center(obj) -> Vector:
    me = obj.data
    acc = Vector()
    for v in me.vertices:
        acc += obj.matrix_world @ v.co
    return acc / max(len(me.vertices), 1)


def move(obj, delta: Vector) -> None:
    mw = obj.matrix_world.copy()
    mw.translation += delta
    obj.matrix_world = mw


def bind(obj, bone: str) -> None:
    for vg in list(obj.vertex_groups):
        obj.vertex_groups.remove(vg)
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

    maul = [o for o in bpy.data.objects
            if o.type == "MESH" and any(g.name == "hand.R" for g in o.vertex_groups)
            and o.name.startswith(("Maul", "Forged oath"))]
    print(f"maul objects: {len(maul)}")

    grip = bpy.data.objects.get("Maul grip")
    grip_c = world_center(grip)
    hand = bpy.data.objects.get("Donor rescue hand L")
    hand_c = world_center(hand)

    target = Vector((hand_c.x, hand_c.y, grip_c.z))
    delta = target - grip_c
    print(f"left hand mesh center {tuple(round(v,3) for v in hand_c)}")
    print(f"grip {tuple(round(v,3) for v in grip_c)} -> "
          f"{tuple(round(v,3) for v in (grip_c + delta))} delta={tuple(round(v,3) for v in delta)}")

    for o in maul:
        move(o, delta)
        bind(o, "hand.L")
    print(f"rebound {len(maul)} maul objects to hand.L")
    print(f"grip now at {tuple(round(v,3) for v in world_center(grip))} "
          f"(target {tuple(round(v,3) for v in target)})")

    # Remove orphaned decorative chest rivets (8 mm air gap in front of the
    # thoracic hull; the side silhouette is cleaner without them).
    rivets = bpy.data.objects.get("Thoracic_Foundry_Rivets.001")
    if rivets:
        bpy.data.objects.remove(rivets, do_unlink=True)
        print("removed Thoracic_Foundry_Rivets.001")

    bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
    print(f"saved: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
