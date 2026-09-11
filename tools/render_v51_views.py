"""Render v51 at REST and at walk frames to verify the maul grip."""
from __future__ import annotations
import sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path("/home/aaron/animation/thulans-production")


def setup_camera(scene):
    for c in list(bpy.data.cameras):
        bpy.data.cameras.remove(c)
    for o in [x for x in bpy.data.objects if x.type == "CAMERA"]:
        bpy.data.objects.remove(o)
    cd = bpy.data.cameras.new("Cam")
    cd.type = "PERSP"
    cd.lens = 50.0
    cam = bpy.data.objects.new("Cam", cd)
    scene.collection.objects.link(cam)
    scene.camera = cam
    scene.render.resolution_x = 900
    scene.render.resolution_y = 1200
    scene.render.film_transparent = False
    return cam


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    cand = Path(argv[0]) if argv else ROOT / "blender/candidates/varek-v51-functional.blend"
    if not cand.is_absolute():
        cand = ROOT / cand
    bpy.ops.wm.open_mainfile(filepath=str(cand))
    out = ROOT / "evidence" / cand.stem
    out.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    rig = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    cam = setup_camera(scene)

    def shoot(tag):
        scene.frame_set(scene.frame_current)
        bpy.context.view_layer.update()
        target = Vector((0.0, -0.15, 1.15))
        for label, loc in (
            ("front", Vector((0.0, -4.6, target.z))),
            ("side", Vector((4.6, 0.0, target.z))),
            ("q34", Vector((3.1, -3.6, target.z + 0.9))),
        ):
            cam.location = loc
            cam.rotation_euler = (target - loc).to_track_quat("-Z", "Y").to_euler()
            fp = out / f"{tag}_{label}.png"
            scene.render.filepath = str(fp)
            bpy.ops.render.render(write_still=True)
            print(f"render {fp}")

    rig.data.pose_position = "REST"
    scene.frame_set(1)
    bpy.context.view_layer.update()
    shoot("rest")

    rig.data.pose_position = "POSE"
    for f in (1, 25):
        scene.frame_set(f)
        bpy.context.view_layer.update()
        shoot(f"pose{f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
