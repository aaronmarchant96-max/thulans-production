import bpy
from pathlib import Path

ROOT = Path("/home/aaron/animation/thulans-production")
DONOR = ROOT / "assets/donors/graviton-manipulator-R.blend"

bpy.ops.wm.open_mainfile(filepath=str(DONOR))
for o in bpy.data.objects:
    print("Object:", o.name, "type:", o.type)
    if o.type == "MESH":
        print("  verts:", len(o.data.vertices))
        print("  vgroups:", [vg.name for vg in o.vertex_groups])
