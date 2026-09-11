"""Establish the green baseline from v41-clean-functional.

Root defect: every mesh carries duplicated modifier pairs, e.g.
[BEVEL, WEIGHTED_NORMAL, ARMATURE, WEIGHTED_NORMAL, BEVEL]. The trailing
BEVEL/WEIGHTED_NORMAL run *after* the armature, inflating evaluated geometry
(Donor thigh 254 -> 5452 verts) and causing self-intersections and armor
interpenetration.

Fix: keep only the first BEVEL and first WEIGHTED_NORMAL (which sit before the
armature), drop any duplicate or post-armature BEVEL/WEIGHTED_NORMAL.

Does NOT touch locked architecture, rig, or animation.

Usage:
  flatpak run --filesystem=host org.blender.Blender --background \
    --python-exit-code 1 --python tools/fix_v48_baseline.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v41-clean-functional.blend"
OUT = ROOT / "blender/candidates/varek-v48-baseline-green.blend"

DUP_TYPES = {"BEVEL", "WEIGHTED_NORMAL"}

# Internal body parts: shrink so they sit inside the armor.
DONOR_PARTS = [
    "Donor thigh L", "Donor thigh R",
    "Donor shin L", "Donor shin R",
    "Donor upper arm L", "Donor upper arm R",
    "Donor forearm L", "Donor forearm R",
    "Donor rescue hand L", "Donor rescue hand R",
]
DONOR_SHRINK = 0.40


def merge(obj, dist: float = 1e-4) -> None:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=dist)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-5, edges=bm.edges[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def convex_hull(obj) -> None:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    res = bmesh.ops.convex_hull(bm, input=bm.verts[:], use_existing_faces=False)
    interior = res.get("geom_interior", []) + res.get("geom_unused", [])
    if interior:
        bmesh.ops.delete(bm, geom=interior, context="VERTS")
    holes = res.get("geom_holes", [])
    if holes:
        bmesh.ops.delete(bm, geom=holes, context="FACES")
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context="VERTS")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def rebind(obj) -> None:
    bone = obj.get("rigid_driver_bone")
    if not bone:
        return
    obj.vertex_groups.clear()
    g = obj.vertex_groups.new(name=bone)
    g.add(list(range(len(obj.data.vertices))), 1.0, "REPLACE")


def shrink(obj, factor: float) -> None:
    me = obj.data
    c = Vector()
    for v in me.vertices:
        c += v.co
    c /= len(me.vertices)
    for v in me.vertices:
        v.co = c + (v.co - c) * factor
    me.update()


def replace_with_box(obj) -> None:
    """Replace mesh with a clean manifold box fitted to its bounds.

    bmesh.ops.convex_hull on this input leaves non-manifold edges (52 on a
    donor thigh), which self-intersect under pose. Internal body parts only
    need a clean convex volume, so a box is sufficient and always manifold.
    """
    me = obj.data
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    mn = Vector((min(xs), min(ys), min(zs)))
    mx = Vector((max(xs), max(ys), max(zs)))
    center = (mn + mx) / 2.0
    size = mx - mn
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts[:])
    bmesh.ops.translate(bm, vec=center, verts=bm.verts[:])
    bm.to_mesh(me)
    bm.free()
    me.update()


def self_union_safe(obj) -> None:
    """Boolean self-union on a modifier-free copy, then rebind.

    Running the operator on the live object bakes the armature deformation into
    the edit mesh and corrupts the binding; the temp copy has no modifiers.
    """
    tmp = bpy.data.objects.new(obj.name + "_su", obj.data.copy())
    bpy.context.collection.objects.link(tmp)
    try:
        bpy.ops.object.select_all(action="DESELECT")
        tmp.select_set(True)
        bpy.context.view_layer.objects.active = tmp
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.intersect_boolean(operation="UNION", use_self=True, solver="EXACT")
        bpy.ops.object.mode_set(mode="OBJECT")
        new_data = tmp.data
        old_data = obj.data
        obj.data = new_data
        bpy.data.meshes.remove(old_data)
    finally:
        bpy.data.objects.remove(tmp)
    rebind(obj)


def fix_modifiers(obj) -> list[str]:
    removed = []
    arm_index = next((i for i, m in enumerate(obj.modifiers) if m.type == "ARMATURE"), len(obj.modifiers))
    seen = set()
    for m in list(obj.modifiers):
        if m.type not in DUP_TYPES:
            continue
        index = obj.modifiers.find(m.name)
        if m.type in seen or index > arm_index:
            removed.append(m.name)
            obj.modifiers.remove(m)
        else:
            seen.add(m.type)
    return removed


def main() -> int:
    bpy.ops.wm.open_mainfile(filepath=str(SRC))
    print(f"source: {SRC}")

    total = 0
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        removed = fix_modifiers(obj)
        if removed:
            total += len(removed)
    print(f"removed {total} duplicate modifier instances across meshes")

    for name in DONOR_PARTS:
        o = bpy.data.objects.get(name)
        if o:
            # internal parts: keep only the armature bind (no bevel/normals)
            for m in list(o.modifiers):
                if m.type != "ARMATURE":
                    o.modifiers.remove(m)
            replace_with_box(o)
            rebind(o)
            shrink(o, DONOR_SHRINK)
            print(f"box+rebind+shrink {name} x{DONOR_SHRINK}")

    # hip clearance: lower the thigh-guard tops so they clear the pelvis in stride
    for name in ("Thigh guard L", "Thigh guard R"):
        o = bpy.data.objects.get(name)
        if o:
            zmax = max(v.co.z for v in o.data.vertices)
            for v in o.data.vertices:
                if v.co.z > zmax - 0.06:
                    v.co.z -= 0.025
            o.data.update()
            print(f"lower top {name} by 0.025")

    # Forged oath collar: its bevel self-intersects on the thin ring even at
    # reduced width; remove the bevel (base mesh and armature are both clean).
    collar = bpy.data.objects.get("Forged oath collar")
    if collar:
        for m in list(collar.modifiers):
            if m.type == "BEVEL":
                collar.modifiers.remove(m)
                print("removed collar bevel")

    # Pelvic cradle: self-intersects even unposed (base mesh defect)
    pel = bpy.data.objects.get("Pelvic cradle")
    if pel:
        merge(pel, dist=0.002)
        self_union_safe(pel)
        merge(pel)
        print(f"merge+self-union Pelvic cradle: {len(pel.data.vertices)} verts")

    # report resulting evaluated density for the worst offenders
    dg = bpy.context.evaluated_depsgraph_get()
    for name in ("Donor thigh L", "Donor rescue hand R", "Forged oath collar", "Pelvic cradle"):
        o = bpy.data.objects.get(name)
        if o:
            e = o.evaluated_get(dg)
            m = e.to_mesh()
            print(f"  {name}: eval_v={len(m.vertices)} eval_f={len(m.polygons)} mods={[mo.type for mo in o.modifiers]}")
            e.to_mesh_clear()

    bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
    print(f"saved: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
