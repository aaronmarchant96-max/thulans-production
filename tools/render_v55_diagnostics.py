"""Render diagnostic still frames for v55 left hand mechanical rig (Cycles, POSE mode enabled)."""

from __future__ import annotations
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ROOT = Path("/home/aaron/animation/thulans-production")
CAND = ROOT / "blender/candidates/varek-v55-mechanical-grip.blend"
OUT_DIR = ROOT / "evidence/varek-v55-mechanical-grip"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def setup_camera(scene, name="DiagnosticCam"):
    for c in list(bpy.data.cameras):
        bpy.data.cameras.remove(c)
    for o in [x for x in bpy.data.objects if x.type == "CAMERA"]:
        bpy.data.objects.remove(o)
    cd = bpy.data.cameras.new(name)
    cd.type = "PERSP"
    cd.lens = 75.0
    cam = bpy.data.objects.new(name, cd)
    scene.collection.objects.link(cam)
    scene.camera = cam
    scene.render.film_transparent = False
    return cam

def main() -> int:
    print(f"Loading candidate: {CAND}")
    bpy.ops.wm.open_mainfile(filepath=str(CAND))
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 24
    scene.cycles.adaptive_threshold = 0.1
    scene.render.resolution_x = 800
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100

    arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    arm.data.pose_position = "POSE"  # CRITICAL: enable pose bone animations!
    bpy.context.view_layer.update()

    cam = setup_camera(scene)

    shots = [
        # 1. Closed grip around maul haft (frame 48)
        {
            "name": "left_hand_grip_closeup.png",
            "frame": 48,
            "target": Vector((0.586, -0.070, 0.98)),
            "loc": Vector((1.35, -0.90, 1.10)),
            "lens": 70.0,
        },
        # 2. Open hand rest closeup (frame 1)
        {
            "name": "left_hand_rest_closeup.png",
            "frame": 1,
            "target": Vector((0.586, -0.055, 1.02)),
            "loc": Vector((1.35, -0.95, 1.18)),
            "lens": 70.0,
        },
    ]

    for s in shots:
        scene.frame_set(s["frame"])
        bpy.context.view_layer.update()
        cam.data.lens = s["lens"]
        cam.location = s["loc"]
        cam.rotation_euler = (s["target"] - s["loc"]).to_track_quat("-Z", "Y").to_euler()

        out_fp = OUT_DIR / s["name"]
        scene.render.filepath = str(out_fp)
        print(f"Rendering: {out_fp} (frame {s['frame']})...")
        bpy.ops.render.render(write_still=True)
        print(f"  Done: {out_fp}")

    print("Diagnostic renders completed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
