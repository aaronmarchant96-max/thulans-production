"""v54: Build Thulan Graviton Manipulator (Faírg-Tygil) on Varek's right arm.

Governed by RULING 023, RULING 024, and AGY Operating Contract.
- Starts from frozen clean baseline: varek-v52-graviton.blend
- Purges old 4-finger right hand and gauntlet bars.
- Builds dedicated procedural M_Copper material.
- Builds copper induction ring (open torus) centered at the right wrist.
- Builds cast-iron housing collar docking to Wrist coupling R.
- Mounts 3 articulated hydraulic talons from Mike.blend (CC0 Quaternius)
  arranged in a 120-degree 3-jaw chuck around the ring in a semi-open ready flare.
- Binds talons to finger.R.0.*, finger.R.1.*, finger.R.2.* and ring/collar to hand.R.
- Adds braided forearm hydraulic conduits bound to forearm.R.
- Outputs blender/candidates/varek-v54-graviton.blend.
"""

from __future__ import annotations
import math
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Matrix, Vector, Quaternion

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v52-graviton.blend"
DONOR = ROOT / "assets/donors/quaternius-mechs/Animated Mech Pack - March 2021/Blends/Mike.blend"
OUT = ROOT / "blender/candidates/varek-v54-graviton.blend"

SCALE = 0.26


def create_copper_material():
    mat = bpy.data.materials.get("M_Copper")
    if not mat:
        mat = bpy.data.materials.new(name="M_Copper")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.955, 0.637, 0.538, 1.0)
        bsdf.inputs["Metallic"].default_value = 1.0
        bsdf.inputs["Roughness"].default_value = 0.36
    return mat


def build_torus_mesh(name, major_r, minor_r, seg_major=32, seg_minor=16):
    bm = bmesh.new()
    verts = []
    for i in range(seg_major):
        theta = 2.0 * math.pi * i / seg_major
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        ring_verts = []
        for j in range(seg_minor):
            phi = 2.0 * math.pi * j / seg_minor
            x = (major_r + minor_r * math.cos(phi)) * cos_t
            y = (major_r + minor_r * math.cos(phi)) * sin_t
            z = minor_r * math.sin(phi)
            v = bm.verts.new(Vector((x, y, z)))
            ring_verts.append(v)
        verts.append(ring_verts)

    bm.verts.ensure_lookup_table()
    for i in range(seg_major):
        i_next = (i + 1) % seg_major
        for j in range(seg_minor):
            j_next = (j + 1) % seg_minor
            v1 = verts[i][j]
            v2 = verts[i_next][j]
            v3 = verts[i_next][j_next]
            v4 = verts[i][j_next]
            bm.faces.new((v1, v2, v3, v4))

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def build_cylinder_mesh(name, r_outer, r_inner, length, seg=32):
    bm = bmesh.new()
    top_outer, bot_outer = [], []
    top_inner, bot_inner = [], []
    z_top = length * 0.5
    z_bot = -length * 0.5

    for i in range(seg):
        th = 2.0 * math.pi * i / seg
        c, s = math.cos(th), math.sin(th)
        top_outer.append(bm.verts.new(Vector((r_outer * c, r_outer * s, z_top))))
        bot_outer.append(bm.verts.new(Vector((r_outer * c, r_outer * s, z_bot))))
        top_inner.append(bm.verts.new(Vector((r_inner * c, r_inner * s, z_top))))
        bot_inner.append(bm.verts.new(Vector((r_inner * c, r_inner * s, z_bot))))

    bm.verts.ensure_lookup_table()
    for i in range(seg):
        i_next = (i + 1) % seg
        # outer wall
        bm.faces.new((top_outer[i], bot_outer[i], bot_outer[i_next], top_outer[i_next]))
        # inner wall
        bm.faces.new((top_inner[i_next], bot_inner[i_next], bot_inner[i], top_inner[i]))
        # top rim
        bm.faces.new((top_inner[i], top_inner[i_next], top_outer[i_next], top_outer[i]))
        # bot rim
        bm.faces.new((bot_outer[i], bot_outer[i_next], bot_inner[i_next], bot_inner[i]))

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def build_conduit_mesh(name, r=0.008, length=0.22, seg=16):
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=seg,
        radius1=r,
        radius2=r,
        depth=length
    )
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def main() -> int:
    print(f"Loading {SRC}...")
    bpy.ops.wm.open_mainfile(filepath=str(SRC))
    arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    arm.data.pose_position = "REST"
    bpy.context.view_layer.update()

    # 1. Remove old right hand + gauntlet bars
    old_names = [
        "Donor rescue hand R",
        "Gauntlet dorsal guard R",
        "Gauntlet knuckle bar R",
        "Gauntlet_Knuckle_Bar_R_0",
        "Gauntlet_Knuckle_Bar_R_1",
        "Gauntlet_Knuckle_Bar_R_2"
    ]
    for n in old_names:
        ob = bpy.data.objects.get(n)
        if ob:
            bpy.data.objects.remove(ob, do_unlink=True)
            print(f"  Removed: {n}")

    # Materials
    mat_copper = create_copper_material()
    mat_cast = bpy.data.materials.get("Warm charcoal cast iron")
    mat_steel = bpy.data.materials.get("Working piston steel") or bpy.data.materials.get("Oily joint steel")

    # REST orientation for right wrist:
    # hand.R head=(-0.586, -0.040, 1.102), tail=(-0.586, -0.065, 0.954)
    # Forward vector along hand: (0.0, -0.025, -0.148)
    wrist_head = Vector((-0.586, -0.040, 1.102))
    wrist_tail = Vector((-0.586, -0.065, 0.954))
    axis_z = (wrist_tail - wrist_head).normalized()  # primary arm direction (down + slightly forward)
    # define local frame: z along arm, y pointing forward (-y world), x pointing lateral (-x world)
    axis_y = Vector((0.0, -1.0, 0.0))
    axis_x = axis_y.cross(axis_z).normalized()
    axis_y = axis_z.cross(axis_x).normalized()
    rot_frame = Matrix([
        [axis_x.x, axis_y.x, axis_z.x, 0.0],
        [axis_x.y, axis_y.y, axis_z.y, 0.0],
        [axis_x.z, axis_y.z, axis_z.z, 0.0],
        [0.0,      0.0,      0.0,      1.0]
    ])

    wrist_center = wrist_head + axis_z * 0.045  # 4.5 cm down from wrist coupling

    # 2. Build Copper Induction Ring
    ring_mesh = build_torus_mesh("Graviton_Induction_Ring_R_Mesh", major_r=0.048, minor_r=0.010)
    ring_obj = bpy.data.objects.new("Graviton_Induction_Ring_R", ring_mesh)
    bpy.context.scene.collection.objects.link(ring_obj)
    ring_obj.data.materials.append(mat_copper)

    # Position & orient ring at wrist center
    ring_obj.matrix_world = Matrix.Translation(wrist_center) @ rot_frame
    ring_obj.data.transform(ring_obj.matrix_world)
    ring_obj.matrix_world = Matrix.Identity(4)

    # Bind ring to hand.R
    vg_ring = ring_obj.vertex_groups.new(name="hand.R")
    vg_ring.add(list(range(len(ring_mesh.vertices))), 1.0, "REPLACE")
    mod_ring = ring_obj.modifiers.new(name="Armature", type="ARMATURE")
    mod_ring.object = arm
    ring_obj["rigid_driver_bone"] = "hand.R"
    print("  Created Graviton_Induction_Ring_R")

    # 3. Build Cast-Iron Docking Collar
    collar_mesh = build_cylinder_mesh("Graviton_Collar_R_Mesh", r_outer=0.060, r_inner=0.044, length=0.038)
    collar_obj = bpy.data.objects.new("Graviton_Collar_R", collar_mesh)
    bpy.context.scene.collection.objects.link(collar_obj)
    if mat_cast:
        collar_obj.data.materials.append(mat_cast)

    collar_pos = wrist_head + axis_z * 0.020  # sits between wrist coupling and ring
    collar_obj.matrix_world = Matrix.Translation(collar_pos) @ rot_frame
    collar_obj.data.transform(collar_obj.matrix_world)
    collar_obj.matrix_world = Matrix.Identity(4)

    vg_col = collar_obj.vertex_groups.new(name="hand.R")
    vg_col.add(list(range(len(collar_mesh.vertices))), 1.0, "REPLACE")
    mod_col = collar_obj.modifiers.new(name="Armature", type="ARMATURE")
    mod_col.object = arm
    collar_obj["rigid_driver_bone"] = "hand.R"
    print("  Created Graviton_Collar_R")

    # 4. Extract Donor Talons from Mike.blend
    print(f"Loading donor {DONOR}...")
    with bpy.data.libraries.load(str(DONOR), link=False) as (src, dst):
        dst.objects = ["Mike"]

    mike_obj = dst.objects[0]
    bpy.context.scene.collection.objects.link(mike_obj)

    # Extract the 3 finger groups: Index (Talon 1), Ring (Talon 2), Pinky (Talon 3)
    talon_defs = [
        ("Talon_Dorsal_R",  ["PalmI.R", "Index1.R", "Index2.R"],  "finger.R.2", math.radians(90)),   # Top
        ("Talon_Inboard_R", ["PalmR.R", "Ring1.R",  "Ring2.R"],   "finger.R.1", math.radians(210)),  # Lower Inboard
        ("Talon_Outboard_R",["PalmP.R", "Pinky1.R", "Pinky2.R"],  "finger.R.0", math.radians(330)),  # Lower Outboard
    ]

    for talon_name, vgroups, bone_prefix, angle in talon_defs:
        v_indices = set()
        v_weights = {}  # v_idx -> {bone_name: weight}
        for gname in vgroups:
            vg = mike_obj.vertex_groups.get(gname)
            if vg:
                sub_bone = bone_prefix + ".0"
                if "1.R" in gname:
                    sub_bone = bone_prefix + ".1"
                elif "2.R" in gname:
                    sub_bone = bone_prefix + ".2"
                elif "Palm" in gname:
                    sub_bone = "hand.R"

                for v in mike_obj.data.vertices:
                    for g in v.groups:
                        if g.group == vg.index and g.weight > 0.1:
                            v_indices.add(v.index)
                            if v.index not in v_weights:
                                v_weights[v.index] = {}
                            v_weights[v.index][sub_bone] = g.weight

        v_list = sorted(list(v_indices))
        # Build local bmesh for this talon
        bm_talon = bmesh.new()
        vert_map = {}
        coords = [mike_obj.data.vertices[i].co.copy() for i in v_list]
        center_raw = sum(coords, Vector()) / len(coords)

        # In Mike, fingers point in -x. Rotate so finger points in +z (along arm extension)
        # and flexes toward center (-radius).
        rot_align = Matrix.Rotation(math.radians(-90), 4, "Y") @ Matrix.Rotation(math.radians(-90), 4, "Z")

        for i, idx in enumerate(v_list):
            co = coords[i] - center_raw
            co_scaled = SCALE * (rot_align @ co)
            nv = bm_talon.verts.new(co_scaled)
            vert_map[idx] = nv

        bm_talon.verts.ensure_lookup_table()
        # Copy faces
        orig_indices = set(v_list)
        for f in mike_obj.data.polygons:
            if all(vi in orig_indices for vi in f.vertices):
                try:
                    bm_talon.faces.new([vert_map[vi] for vi in f.vertices])
                except ValueError:
                    pass

        t_mesh = bpy.data.meshes.new(f"{talon_name}_Mesh")
        bm_talon.to_mesh(t_mesh)
        bm_talon.free()

        t_obj = bpy.data.objects.new(talon_name, t_mesh)
        bpy.context.scene.collection.objects.link(t_obj)
        if mat_cast:
            t_obj.data.materials.append(mat_cast)

        # Radial positioning around ring:
        # radius = 0.052 m from wrist_center
        # angle around axis_z
        radial_vec = (math.cos(angle) * axis_x + math.sin(angle) * axis_y) * 0.052
        flare_rot = Matrix.Rotation(math.radians(25), 4, radial_vec.cross(axis_z).normalized())
        talon_pos = wrist_center + radial_vec + axis_z * 0.035

        # Orient talon
        t_mat = Matrix.Translation(talon_pos) @ flare_rot @ rot_frame @ Matrix.Rotation(angle, 4, "Z")
        t_obj.matrix_world = t_mat
        t_obj.data.transform(t_obj.matrix_world)
        t_obj.matrix_world = Matrix.Identity(4)

        # Assign vertex groups
        for bone_name in ["hand.R", f"{bone_prefix}.0", f"{bone_prefix}.1", f"{bone_prefix}.2"]:
            t_obj.vertex_groups.new(name=bone_name)

        for i, old_idx in enumerate(v_list):
            weights = v_weights.get(old_idx, {"hand.R": 1.0})
            for bname, w in weights.items():
                vg = t_obj.vertex_groups.get(bname)
                if vg:
                    vg.add([i], w, "REPLACE")

        mod_t = t_obj.modifiers.new(name="Armature", type="ARMATURE")
        mod_t.object = arm
        print(f"  Created {talon_name} (verts={len(t_mesh.vertices)})")

    # Remove temporary Mike object
    bpy.data.objects.remove(mike_obj, do_unlink=True)

    # 5. Build Braided Forearm Conduits
    conduit_mesh = build_conduit_mesh("Graviton_Conduit_R_Mesh", r=0.007, length=0.22)
    conduit_obj = bpy.data.objects.new("Graviton_Conduit_Forearm_R", conduit_mesh)
    bpy.context.scene.collection.objects.link(conduit_obj)
    if mat_steel:
        conduit_obj.data.materials.append(mat_steel)

    # Place conduit snug along the inboard side of forearm.R
    conduit_pos = wrist_head - axis_z * 0.11 + axis_x * 0.035 - axis_y * 0.020
    conduit_obj.matrix_world = Matrix.Translation(conduit_pos) @ rot_frame
    conduit_obj.data.transform(conduit_obj.matrix_world)
    conduit_obj.matrix_world = Matrix.Identity(4)

    vg_cnd = conduit_obj.vertex_groups.new(name="forearm.R")
    vg_cnd.add(list(range(len(conduit_mesh.vertices))), 1.0, "REPLACE")
    mod_cnd = conduit_obj.modifiers.new(name="Armature", type="ARMATURE")
    mod_cnd.object = arm
    conduit_obj["rigid_driver_bone"] = "forearm.R"
    print("  Created Graviton_Conduit_Forearm_R")

    arm.data.pose_position = "POSE"
    # Save output candidate
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
    print(f"Successfully saved {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
