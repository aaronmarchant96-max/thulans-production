"""v53: Thulan Graviton Manipulator (kitbash) on the right arm (RULING 023).

Appends the CC0 Quaternius donor right manipulator hand (extracted to
assets/donors/graviton-manipulator-R.blend), scales/rotates/positions it at
Varek's right wrist with fingers pointing forward, applies Varek's materials,
and binds it rigidly to `hand.R`.

Replaces the old claw hand (removed). Writes varek-v53-graviton.blend.
"""

from __future__ import annotations

import sys
from math import radians
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v52-graviton.blend"
DONOR = ROOT / "assets/donors/graviton-manipulator-R.blend"
OUT = ROOT / "blender/candidates/varek-v53-graviton.blend"

ARM = None
HAND_NAME = "Graviton_Manipulator_R"
SCALE = 0.28
ROT = Matrix.Rotation(radians(90), 4, "Z")  # fingers -x -> -y


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

    # remove the old right-hand claw + gauntlet (keep the wrist coupling)
    for name in ("Donor rescue hand R", "Gauntlet dorsal guard R",
                 "Gauntlet knuckle bar R", "Gauntlet_Knuckle_Bar_R_0",
                 "Gauntlet_Knuckle_Bar_R_1", "Gauntlet_Knuckle_Bar_R_2"):
        o = bpy.data.objects.get(name)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)
            print(f"removed {name}")

    # append the donor hand
    before = set(bpy.data.objects)
    with bpy.data.libraries.load(str(DONOR), link=False) as (src, dst):
        dst.objects = [n for n in src.objects]
    hand = None
    for o in bpy.data.objects:
        if o.name == HAND_NAME and o not in before:
            if o.name not in [x.name for x in bpy.context.scene.collection.objects]:
                bpy.context.scene.collection.objects.link(o)
            hand = o
    if hand is None:
        print("FATAL: donor hand not appended")
        return 2
    print(f"appended {hand.name} verts={len(hand.data.vertices)}")

    # bake world transform into the mesh, reset object matrix
    hand.data.transform(hand.matrix_world)
    hand.matrix_world = Matrix.Identity(4)

    # center at origin
    acc = Vector()
    for v in hand.data.vertices:
        acc += v.co
    c = acc / len(hand.data.vertices)
    for v in hand.data.vertices:
        v.co -= c
    print(f"hand centroid (donor) {tuple(round(v,3) for v in c)}")

    # scale + rotate (fingers -> -y)
    for v in hand.data.vertices:
        v.co = SCALE * (ROT @ v.co)

    # seat at the right wrist; fingers point forward (-y)
    wrist = Vector((-0.586, -0.040, 1.102))
    forward = Vector((0.0, -0.18, 0.0))
    for v in hand.data.vertices:
        v.co += wrist + forward

    # bounds check
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for v in hand.data.vertices:
        for i in range(3):
            mn[i] = min(mn[i], v.co[i])
            mx[i] = max(mx[i], v.co[i])
    print(f"hand world bounds min={tuple(round(v,3) for v in mn)} "
          f"max={tuple(round(v,3) for v in mx)}")

    # materials
    cast = bpy.data.materials.get("Warm charcoal cast iron")
    hand.data.materials.clear()
    if cast:
        hand.data.materials.append(cast)
    else:
        print("WARN: cast iron material missing")

    bind(hand, "hand.R")
    print("bound to hand.R")

    bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
    print(f"saved: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
