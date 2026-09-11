"""Measure the ACTUAL rendered (deformed) world positions of maul vs hand."""
from __future__ import annotations
import sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path("/home/aaron/animation/thulans-production")


def eval_center(name, dg):
    o = bpy.data.objects[name]
    eo = o.evaluated_get(dg)
    me = eo.to_mesh()
    if me is None or len(me.vertices) == 0:
        eo.to_mesh_clear()
        return None
    acc = Vector()
    for v in me.vertices:
        acc += eo.matrix_world @ v.co
    c = acc / len(me.vertices)
    eo.to_mesh_clear()
    return c


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    cand = Path(argv[0]) if argv else ROOT / "blender/candidates/varek-v52-graviton.blend"
    if not cand.is_absolute():
        cand = ROOT / cand
    bpy.ops.wm.open_mainfile(filepath=str(cand))
    rig = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    sc = bpy.context.scene

    # --- inspect maul binding ---
    shaft = bpy.data.objects["Maul shaft"]
    print("=== Maul shaft binding ===")
    for m in shaft.modifiers:
        mobj = getattr(m, "object", None)
        print(f"  mod {m.name} type={m.type} obj={mobj.name if mobj else None} "
              f"show_render={m.show_render} verts={getattr(m,'use_vertex_groups',None)}")
    print(f"  vertex groups: {[g.name for g in shaft.vertex_groups]}")

    names = ["Maul shaft", "Maul grip", "Donor rescue hand L", "Donor rescue hand R",
             "Wrist coupling L"]

    for pose in ("REST", "POSE"):
        rig.data.pose_position = pose
        sc.frame_set(1)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        print(f"\n=== {pose} (deformed, rendered) ===")
        for n in names:
            c = eval_center(n, dg)
            if c is not None:
                print(f"  {n:24s} ({c.x:+.3f},{c.y:+.3f},{c.z:+.3f})")

    # grip-to-hand distance at POSE
    rig.data.pose_position = "POSE"
    sc.frame_set(1)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    g = eval_center("Maul grip", dg)
    h = eval_center("Donor rescue hand L", dg)
    print(f"\nPOSE grip->hand.L distance = {(g - h).length:.3f}")

    # also print bone head/tail rest and pose
    print("\n=== bones ===")
    for pose in ("REST", "POSE"):
        rig.data.pose_position = pose
        sc.frame_set(1)
        bpy.context.view_layer.update()
        b = rig.pose.bones["hand.L"]
        print(f"  {pose} hand.L head={tuple(round(v,3) for v in (rig.matrix_world @ b.head))} "
              f"tail={tuple(round(v,3) for v in (rig.matrix_world @ b.tail))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
