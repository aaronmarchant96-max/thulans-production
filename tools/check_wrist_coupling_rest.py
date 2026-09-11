import bpy
from pathlib import Path
from mathutils import Vector

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v52-graviton.blend"

bpy.ops.wm.open_mainfile(filepath=str(SRC))
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
arm.data.pose_position = "REST"
bpy.context.view_layer.update()

wc = bpy.data.objects.get("Wrist coupling R")
dg = bpy.context.evaluated_depsgraph_get()
wc_eval = wc.evaluated_get(dg)
mesh = wc_eval.to_mesh()
verts = [wc_eval.matrix_world @ v.co for v in mesh.vertices]
mn = Vector((min(p.x for p in verts), min(p.y for p in verts), min(p.z for p in verts)))
mx = Vector((max(p.x for p in verts), max(p.y for p in verts), max(p.z for p in verts)))
center = (mn + mx) / 2
print(f"REST evaluated bounds for Wrist coupling R: min={tuple(round(x,3) for x in mn)} max={tuple(round(x,3) for x in mx)}")
print(f"REST center={tuple(round(x,3) for x in center)}")
wc_eval.to_mesh_clear()

pb_hand = arm.pose.bones["hand.R"]
print(f"REST pose bone hand.R head={tuple(round(x,3) for x in pb_hand.head)} tail={tuple(round(x,3) for x in pb_hand.tail)}")
