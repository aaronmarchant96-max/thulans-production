import bpy
import bmesh
from pathlib import Path

v51 = Path("/home/aaron/animation/thulans-production/blender/candidates/varek-v51-functional.blend")
bpy.ops.wm.open_mainfile(filepath=str(v51))

hand = bpy.data.objects.get("Donor rescue hand L")
if hand:
    bm = bmesh.new()
    bm.from_mesh(hand.data)
    islands = []
    unvisited = set(bm.verts)
    while unvisited:
        v = unvisited.pop()
        island = {v}
        stack = [v]
        while stack:
            curr = stack.pop()
            for edge in curr.link_edges:
                other = edge.other_vert(curr)
                if other in unvisited:
                    unvisited.remove(other)
                    island.add(other)
                    stack.append(other)
        islands.append(island)
    print(f"\nDonor rescue hand L has {len(islands)} separate mesh islands!")
    for idx, isl in enumerate(islands):
        coords = [v.co for v in isl]
        min_z = min(c.z for c in coords)
        max_z = max(c.z for c in coords)
        dim_x = max(c.x for c in coords) - min(c.x for c in coords)
        dim_y = max(c.y for c in coords) - min(c.y for c in coords)
        dim_z = max_z - min_z
        print(f"  Island {idx}: {len(isl)} verts, dim=({dim_x:.3f}, {dim_y:.3f}, {dim_z:.3f})")
    bm.free()
