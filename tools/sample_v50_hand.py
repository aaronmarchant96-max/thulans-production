"""Sample hand.R / forearm.R world position across the walk action."""
from __future__ import annotations
import sys
from pathlib import Path
import bpy

ROOT = Path("/home/aaron/animation/thulans-production")


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    cand = Path(argv[0]) if argv else ROOT / "blender/candidates/varek-v50-golden-baseline.blend"
    if not cand.is_absolute():
        cand = ROOT / cand
    bpy.ops.wm.open_mainfile(filepath=str(cand))
    rig = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    act = rig.animation_data.action
    f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
    sc = bpy.context.scene
    print(f"action={act.name} frames={f0}-{f1}")
    for f in range(f0, f1 + 1, 6):
        sc.frame_set(f)
        bpy.context.view_layer.update()
        hb = rig.pose.bones["hand.R"]
        hw = rig.matrix_world @ hb.head
        fb = rig.pose.bones["forearm.R"]
        fw = rig.matrix_world @ fb.head
        print(f"  f={f:3d} hand.R=({hw.x:+.3f},{hw.y:+.3f},{hw.z:+.3f}) "
              f"forearm.R=({fw.x:+.3f},{fw.y:+.3f},{fw.z:+.3f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
