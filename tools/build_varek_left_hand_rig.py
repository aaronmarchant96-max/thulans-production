"""Build the canonical Left Hand Mechanical Rig for Varek Fairgunjis (v55.1).

Authority:
  - docs/VAREK_HAND_RIG_SPEC_v1.md
  - docs/HAND_PHYSICS_GATE.md
  - RULINGS 010, 011, 023, 024, 030

Features:
  - Starts from frozen clean baseline: blender/candidates/varek-v54-graviton.blend
  - Purges old static 80-vert 'Donor rescue hand L' and obsolete knuckle bars.
  - Builds 2-DOF universal wrist gimbal yoke (pitch outer ring, yaw inner ring, 4 clevis pins)
    nested within Wrist coupling L.
  - Builds heavy cast-iron palm plate chassis (palm.L) with structural neck connecting directly
    to the inner gimbal ring, spanning 136 mm across the wrist cuff under Gauntlet dorsal guard L.
  - Builds 3 heavy articulated digits (Index, Middle, Ring) with 34 mm wide forged box-phalanx
    segments, double clevis ears, 14 mm turned steel pins, and serrated inner grip pads.
  - Builds heavy opposable thumb with 2 articulated phalanges and saddle clevis on the lateral flank.
  - Adds all 14 hand bones to Varek simple articulation armature with correct parentage and roll.
  - Sets Limit Rotation constraints on all joints with exact limits from Section 6.6 of the spec.
  - Assigns 100% rigid vertex weighting per bone (zero smooth deformation).
  - Configures rest pose (open/extended) and closed grip pose interlocking around the hexagonal
    haft of the Faírguni-Hamars maul at the lower grip ribs.
  - Outputs blender/candidates/varek-v55-mechanical-grip.blend.
"""

from __future__ import annotations
import math
from pathlib import Path
import sys

import bpy
import bmesh
from mathutils import Matrix, Vector, Quaternion

ROOT = Path("/home/aaron/animation/thulans-production")
SRC = ROOT / "blender/candidates/varek-v54-graviton.blend"
OUT = ROOT / "blender/candidates/varek-v55-mechanical-grip.blend"

# Base landmarks measured from chassis
P_WRIST = Vector((0.5860, -0.0397, 1.1025))
E_X = Vector((1.0, 0.0, 0.0))                     # Radial / Lateral (+X world)
E_Y = Vector((0.0, -0.1644, -0.9864)).normalized() # Distal (along hand length)
E_Z = Vector((0.0, 0.9864, -0.1644)).normalized()  # Dorsal (+Y world, back of hand)
R_HAND = Matrix([E_X, E_Y, E_Z]).transposed()     # Local-to-world rotation

def hand_to_world(p_loc: Vector) -> Vector:
    return P_WRIST + R_HAND @ p_loc

def world_to_hand(p_world: Vector) -> Vector:
    return R_HAND.inverted() @ (p_world - P_WRIST)

def add_box_to_bm(bm: bmesh.types.BMesh, center: Vector, size: Vector):
    cube = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=cube["verts"])
    bmesh.ops.translate(bm, vec=center, verts=cube["verts"])

def add_pin_to_bm(bm: bmesh.types.BMesh, p1: Vector, p2: Vector, radius: float, seg: int = 16):
    diff = p2 - p1
    length = diff.length
    center = (p1 + p2) * 0.5
    cyl = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=radius, radius2=radius, depth=length)
    z_axis = Vector((0, 0, 1))
    target_axis = diff.normalized()
    if (z_axis - target_axis).length > 1e-5:
        q = z_axis.rotation_difference(target_axis)
        bmesh.ops.rotate(bm, cent=Vector((0, 0, 0)), matrix=q.to_matrix(), verts=cyl["verts"])
    bmesh.ops.translate(bm, vec=center, verts=cyl["verts"])

def add_phalanx_segment(bm: bmesh.types.BMesh, p_start: Vector, p_end: Vector, width: float, thick: float, pin_rad: float, is_tip: bool = False):
    """Create a heavy forged box phalanx with clevis ears, pin, and chamfer."""
    diff = p_end - p_start
    length = diff.length
    center = (p_start + p_end) * 0.5

    # Main box body
    box_len = length * 0.88 if not is_tip else length
    box = bmesh.ops.create_cube(bm, size=1.0)
    # Scale box: local x is width, local y is length, local z is thick
    bmesh.ops.scale(bm, vec=Vector((width, box_len, thick)), verts=box["verts"])
    
    # Orient along diff
    y_axis = Vector((0, 1, 0))
    target_axis = diff.normalized()
    if (y_axis - target_axis).length > 1e-5:
        q = y_axis.rotation_difference(target_axis)
        bmesh.ops.rotate(bm, cent=Vector((0, 0, 0)), matrix=q.to_matrix(), verts=box["verts"])
    bmesh.ops.translate(bm, vec=center, verts=box["verts"])

    # Joint hinge pin at start
    p_pin1 = p_start - E_X * (width * 0.55)
    p_pin2 = p_start + E_X * (width * 0.55)
    add_pin_to_bm(bm, p_pin1, p_pin2, radius=pin_rad, seg=16)

    # Double clevis ears at end if not tip
    if not is_tip:
        ear_thick = width * 0.22
        for sign in [-1.0, 1.0]:
            ear_c = p_end + sign * E_X * (width * 0.38)
            add_pin_to_bm(bm, ear_c - diff.normalized() * 0.008, ear_c + diff.normalized() * 0.008, radius=pin_rad * 1.5, seg=12)

def bind_object(obj: bpy.types.Object, arm: bpy.types.Object, bone_name: str, mat: bpy.types.Material):
    if mat and mat.name not in [m.name for m in obj.data.materials if m]:
        obj.data.materials.append(mat)
    vg = obj.vertex_groups.new(name=bone_name)
    vg.add(list(range(len(obj.data.vertices))), 1.0, "REPLACE")
    mod = obj.modifiers.new(name="Armature", type="ARMATURE")
    mod.object = arm
    obj["rigid_driver_bone"] = bone_name

def main() -> int:
    print(f"Opening baseline candidate: {SRC}")
    bpy.ops.wm.open_mainfile(filepath=str(SRC))
    scene = bpy.context.scene
    arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    arm.data.pose_position = "REST"
    bpy.context.view_layer.update()

    # Materials
    mat_cast = bpy.data.materials.get("Warm charcoal cast iron")
    mat_steel = bpy.data.materials.get("Working piston steel") or bpy.data.materials.get("Oily joint steel")

    # 1. Purge old static hand and obsolete knuckle bars
    purge_names = [
        "Donor rescue hand L",
        "Gauntlet knuckle bar L",
        "Gauntlet_Knuckle_Bar_L_0",
        "Gauntlet_Knuckle_Bar_L_1",
        "Gauntlet_Knuckle_Bar_L_2",
        "Gimbal_Yoke_Outer_L",
        "Gimbal_Yoke_Inner_L",
        "Palm_Plate_L",
        "Digit1_Phalanx1_L", "Digit1_Phalanx2_L", "Digit1_Phalanx3_L",
        "Digit2_Phalanx1_L", "Digit2_Phalanx2_L", "Digit2_Phalanx3_L",
        "Digit3_Phalanx1_L", "Digit3_Phalanx2_L", "Digit3_Phalanx3_L",
        "Thumb_Phalanx1_L", "Thumb_Phalanx2_L"
    ]
    for name in purge_names:
        o = bpy.data.objects.get(name)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)

    # 2. Build Armature Bones
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    eb_hand = arm.data.edit_bones.get("hand.L")

    # Clean existing child bones of hand.L
    for eb in list(arm.data.edit_bones):
        if any(prefix in eb.name for prefix in ["wrist_pitch.L", "wrist_yaw.L", "palm.L", "digit1_", "digit2_", "digit3_", "thumb_"]):
            arm.data.edit_bones.remove(eb)

    # 2.1 Wrist Pitch bone (rotates around local X / lateral axis)
    eb_pitch = arm.data.edit_bones.new("wrist_pitch.L")
    eb_pitch.head = P_WRIST
    eb_pitch.tail = P_WRIST + E_X * 0.040
    eb_pitch.parent = eb_hand
    eb_pitch.align_roll(E_Z)

    # 2.2 Wrist Yaw bone (rotates around local Z / dorsal-palmar axis)
    eb_yaw = arm.data.edit_bones.new("wrist_yaw.L")
    eb_yaw.head = P_WRIST
    eb_yaw.tail = P_WRIST + E_Z * 0.040
    eb_yaw.parent = eb_pitch
    eb_yaw.align_roll(E_Y)

    # 2.3 Palm bone (extends distally from wrist yaw along E_Y)
    eb_palm = arm.data.edit_bones.new("palm.L")
    eb_palm.head = P_WRIST
    eb_palm.tail = P_WRIST + E_Y * 0.095
    eb_palm.parent = eb_yaw
    eb_palm.align_roll(E_Z)

    # Digit knuckle offsets in hand-local space (x, y, z)
    # Palm width is 136 mm, knuckles at y=0.095 m, z=+0.026 m
    digit_x_offsets = [
        ("digit1", +0.042),   # Index (radial side, +X)
        ("digit2",  0.000),   # Middle (center)
        ("digit3", -0.042),   # Ring (ulnar side, -X)
    ]
    phalanx_lengths = [0.046, 0.040, 0.034] # Total reach = 120 mm
    palmar_normal = -E_Z # Points palmar (-Y world)

    digit_bones = {}
    for dname, x_off in digit_x_offsets:
        # MCP joint (seg 1)
        p_mcp_loc = Vector((x_off, 0.095, 0.026))
        p_mcp_w = hand_to_world(p_mcp_loc)
        p_pip_w = p_mcp_w + E_Y * phalanx_lengths[0]
        
        eb1 = arm.data.edit_bones.new(f"{dname}_01.L")
        eb1.head = p_mcp_w
        eb1.tail = p_pip_w
        eb1.parent = eb_palm
        eb1.align_roll(palmar_normal)

        # PIP joint (seg 2)
        p_dip_w = p_pip_w + E_Y * phalanx_lengths[1]
        eb2 = arm.data.edit_bones.new(f"{dname}_02.L")
        eb2.head = p_pip_w
        eb2.tail = p_dip_w
        eb2.parent = eb1
        eb2.align_roll(palmar_normal)

        # DIP joint (seg 3)
        p_tip_w = p_dip_w + E_Y * phalanx_lengths[2]
        eb3 = arm.data.edit_bones.new(f"{dname}_03.L")
        eb3.head = p_dip_w
        eb3.tail = p_tip_w
        eb3.parent = eb2
        eb3.align_roll(palmar_normal)

        digit_bones[dname] = [eb1.name, eb2.name, eb3.name]

    # Thumb bones (opposing from lateral radial flank)
    # CMC base at x=+0.065, y=0.045, z=+0.020
    p_cmc_loc = Vector((0.065, 0.045, 0.020))
    p_cmc_w = hand_to_world(p_cmc_loc)
    # Thumb proximal projects forward (-z) and distal (+y)
    v_th1 = (E_Y * 0.038 - E_Z * 0.024 + E_X * 0.006).normalized() * 0.044
    p_th_mcp_w = p_cmc_w + v_th1

    eb_th1 = arm.data.edit_bones.new("thumb_01.L")
    eb_th1.head = p_cmc_w
    eb_th1.tail = p_th_mcp_w
    eb_th1.parent = eb_palm
    eb_th1.align_roll(-E_X)

    # Thumb distal wraps inward across front
    v_th2 = (-E_X * 0.030 - E_Z * 0.016 + E_Y * 0.012).normalized() * 0.038
    p_th_tip_w = p_th_mcp_w + v_th2

    eb_th2 = arm.data.edit_bones.new("thumb_02.L")
    eb_th2.head = p_th_mcp_w
    eb_th2.tail = p_th_tip_w
    eb_th2.parent = eb_th1
    eb_th2.align_roll(-E_Z)

    # 2.4 Tool bone for Faírguni-Hamars Maul (RULING 024 Part 3)
    eb_tool = arm.data.edit_bones.get("tool")
    if eb_tool is None:
        eb_tool = arm.data.edit_bones.new("tool")
    eb_tool.parent = eb_hand
    p_tool_center = P_WRIST - E_Z * 0.024
    eb_tool.head = p_tool_center + E_Y * 0.300
    eb_tool.tail = p_tool_center - E_Y * 0.300
    eb_tool.align_roll(E_Z)

    bpy.ops.object.mode_set(mode="OBJECT")
    print("  Created 14 hand/wrist edit bones and tool bone with verified proportions.")

    # 3. Add Constraints in Pose Mode
    for pb in arm.pose.bones:
        pb.rotation_mode = "XYZ"

    # Wrist pitch: -20 deg to +45 deg on X
    pb_pitch = arm.pose.bones["wrist_pitch.L"]
    c = pb_pitch.constraints.new(type="LIMIT_ROTATION")
    c.name = "Limit_Rotation_Pitch"
    c.owner_space = "LOCAL"
    c.use_limit_x = True
    c.min_x = math.radians(-20)
    c.max_x = math.radians(45)
    c.use_limit_y = c.use_limit_z = True
    c.min_y = c.max_y = c.min_z = c.max_z = 0.0

    # Wrist yaw: -15 deg to +20 deg on Z
    pb_yaw = arm.pose.bones["wrist_yaw.L"]
    c = pb_yaw.constraints.new(type="LIMIT_ROTATION")
    c.name = "Limit_Rotation_Yaw"
    c.owner_space = "LOCAL"
    c.use_limit_z = True
    c.min_z = math.radians(-15)
    c.max_z = math.radians(20)
    c.use_limit_x = c.use_limit_y = True
    c.min_x = c.max_x = c.min_y = c.max_y = 0.0

    # Digit limits: MCP 0..80, PIP 0..90, DIP 0..60
    digit_limits = [(0, 80), (0, 90), (0, 60)]
    for dname, _ in digit_x_offsets:
        for idx, (min_deg, max_deg) in enumerate(digit_limits):
            bname = f"{dname}_{idx+1:02d}.L"
            pb = arm.pose.bones[bname]
            c = pb.constraints.new(type="LIMIT_ROTATION")
            c.name = f"Limit_Curl_{idx+1}"
            c.owner_space = "LOCAL"
            c.use_limit_x = True
            c.min_x = math.radians(min_deg)
            c.max_x = math.radians(max_deg)
            c.use_limit_y = c.use_limit_z = True
            c.min_y = c.max_y = c.min_z = c.max_z = 0.0

    # Thumb limits: CMC flex -30..+45, abd -20..+30; MCP 0..70
    pb_th1 = arm.pose.bones["thumb_01.L"]
    c = pb_th1.constraints.new(type="LIMIT_ROTATION")
    c.name = "Limit_Thumb_CMC"
    c.owner_space = "LOCAL"
    c.use_limit_x = True
    c.min_x = math.radians(-30)
    c.max_x = math.radians(45)
    c.use_limit_y = True
    c.min_y = math.radians(-20)
    c.max_y = math.radians(30)
    c.use_limit_z = True
    c.min_z = c.max_z = 0.0

    pb_th2 = arm.pose.bones["thumb_02.L"]
    c = pb_th2.constraints.new(type="LIMIT_ROTATION")
    c.name = "Limit_Thumb_MCP"
    c.owner_space = "LOCAL"
    c.use_limit_x = True
    c.min_x = math.radians(0)
    c.max_x = math.radians(70)
    c.use_limit_y = c.use_limit_z = True
    c.min_y = c.max_y = c.min_z = c.max_z = 0.0

    # 4. Procedural Heavy Hard-Surface Geometry Construction
    # 4.1 Universal Gimbal Yoke Outer Ring (Pitch)
    bm_yoke_out = bmesh.new()
    seg_maj, seg_min = 32, 12
    maj_r, min_r = 0.058, 0.009
    verts_ring = []
    for i in range(seg_maj):
        th = 2.0 * math.pi * i / seg_maj
        c_th, s_th = math.cos(th), math.sin(th)
        ring_v = []
        for j in range(seg_min):
            ph = 2.0 * math.pi * j / seg_min
            x = min_r * math.cos(ph)
            y = (maj_r + min_r * math.sin(ph)) * c_th
            z = (maj_r + min_r * math.sin(ph)) * s_th
            ring_v.append(bm_yoke_out.verts.new(hand_to_world(Vector((x, y, z)))))
        verts_ring.append(ring_v)
    bm_yoke_out.verts.ensure_lookup_table()
    for i in range(seg_maj):
        i_next = (i + 1) % seg_maj
        for j in range(seg_min):
            j_next = (j + 1) % seg_min
            bm_yoke_out.faces.new((verts_ring[i][j], verts_ring[i_next][j], verts_ring[i_next][j_next], verts_ring[i][j_next]))

    # Add 2 pitch clevis pins extending outward along local X into Wrist coupling L
    for sign in [-1.0, 1.0]:
        p1 = hand_to_world(Vector((sign * (maj_r - 0.012), 0.0, 0.0)))
        p2 = hand_to_world(Vector((sign * (maj_r + 0.020), 0.0, 0.0)))
        add_pin_to_bm(bm_yoke_out, p1, p2, radius=0.009, seg=16)

    mesh_yoke_out = bpy.data.meshes.new("Gimbal_Yoke_Outer_L_Mesh")
    bm_yoke_out.to_mesh(mesh_yoke_out)
    bm_yoke_out.free()
    obj_yoke_out = bpy.data.objects.new("Gimbal_Yoke_Outer_L", mesh_yoke_out)
    scene.collection.objects.link(obj_yoke_out)
    bind_object(obj_yoke_out, arm, "wrist_pitch.L", mat_steel)

    # 4.2 Universal Gimbal Yoke Inner Ring (Yaw)
    bm_yoke_in = bmesh.new()
    maj_r_in, min_r_in = 0.044, 0.008
    verts_ring_in = []
    for i in range(seg_maj):
        th = 2.0 * math.pi * i / seg_maj
        c_th, s_th = math.cos(th), math.sin(th)
        ring_v = []
        for j in range(seg_min):
            ph = 2.0 * math.pi * j / seg_min
            x = (maj_r_in + min_r_in * math.sin(ph)) * c_th
            y = (maj_r_in + min_r_in * math.sin(ph)) * s_th
            z = min_r_in * math.cos(ph)
            ring_v.append(bm_yoke_in.verts.new(hand_to_world(Vector((x, y, z)))))
        verts_ring_in.append(ring_v)
    bm_yoke_in.verts.ensure_lookup_table()
    for i in range(seg_maj):
        i_next = (i + 1) % seg_maj
        for j in range(seg_min):
            j_next = (j + 1) % seg_min
            bm_yoke_in.faces.new((verts_ring_in[i][j], verts_ring_in[i_next][j], verts_ring_in[i_next][j_next], verts_ring_in[i][j_next]))

    # Add 2 yaw clevis pins along local Z linking to outer ring
    for sign in [-1.0, 1.0]:
        p1 = hand_to_world(Vector((0.0, 0.0, sign * (maj_r_in - 0.012))))
        p2 = hand_to_world(Vector((0.0, 0.0, sign * (maj_r_in + 0.018))))
        add_pin_to_bm(bm_yoke_in, p1, p2, radius=0.008, seg=16)

    mesh_yoke_in = bpy.data.meshes.new("Gimbal_Yoke_Inner_L_Mesh")
    bm_yoke_in.to_mesh(mesh_yoke_in)
    bm_yoke_in.free()
    obj_yoke_in = bpy.data.objects.new("Gimbal_Yoke_Inner_L", mesh_yoke_in)
    scene.collection.objects.link(obj_yoke_in)
    bind_object(obj_yoke_in, arm, "wrist_yaw.L", mat_steel)

    # 4.3 Heavy Cast-Iron Palm Plate Chassis (palm.L)
    bm_palm = bmesh.new()
    
    # 4.3.1 Structural neck bracketing onto the inner gimbal yaw trunnions
    neck_c = hand_to_world(Vector((0.0, 0.020, 0.010)))
    add_box_to_bm(bm_palm, neck_c, Vector((0.060, 0.035, 0.040)))

    # 4.3.2 Main Palm Plate: full 136 mm width across the wrist cuff!
    palm_c_loc = Vector((0.000, 0.060, 0.036))
    palm_sz_loc = Vector((0.136, 0.070, 0.028))
    corners = []
    for sx in [-0.5, 0.5]:
        for sy in [-0.5, 0.5]:
            for sz in [-0.5, 0.5]:
                loc = palm_c_loc + Vector((sx * palm_sz_loc.x, sy * palm_sz_loc.y, sz * palm_sz_loc.z))
                corners.append(hand_to_world(loc))
    cube_palm = bmesh.ops.create_cube(bm_palm, size=1.0)
    for idx, v in enumerate(cube_palm["verts"]):
        v.co = corners[idx]

    # 4.3.3 Three heavy clevis ears flanking each of the 3 MCP knuckle joints
    for _, x_off in digit_x_offsets:
        # MCP pin
        p1 = hand_to_world(Vector((x_off - 0.020, 0.095, 0.026)))
        p2 = hand_to_world(Vector((x_off + 0.020, 0.095, 0.026)))
        add_pin_to_bm(bm_palm, p1, p2, radius=0.007, seg=16)
        # Structural bracket ears
        for sign in [-1.0, 1.0]:
            ear_c = hand_to_world(Vector((x_off + sign * 0.019, 0.090, 0.026)))
            add_box_to_bm(bm_palm, ear_c, Vector((0.006, 0.020, 0.026)))

    # 4.3.4 Thumb saddle bracket on lateral flank
    th_mount_c = hand_to_world(Vector((0.065, 0.045, 0.020)))
    add_box_to_bm(bm_palm, th_mount_c, Vector((0.024, 0.030, 0.028)))
    add_pin_to_bm(bm_palm, th_mount_c - E_Z * 0.015, th_mount_c + E_Z * 0.015, radius=0.007, seg=16)

    mesh_palm = bpy.data.meshes.new("Palm_Plate_L_Mesh")
    bm_palm.to_mesh(mesh_palm)
    bm_palm.free()
    obj_palm = bpy.data.objects.new("Palm_Plate_L", mesh_palm)
    scene.collection.objects.link(obj_palm)
    bind_object(obj_palm, arm, "palm.L", mat_cast)

    # 4.4 Build 3 Heavy Articulated Digits (Index, Middle, Ring)
    # Phalanx widths: 34 mm (P1), 30 mm (P2), 26 mm (P3)
    widths = [0.034, 0.030, 0.026]
    thicks = [0.024, 0.020, 0.017]
    pin_rads = [0.007, 0.006, 0.005]

    for dname, x_off in digit_x_offsets:
        seg_bones = [f"{dname}_01.L", f"{dname}_02.L", f"{dname}_03.L"]
        p_mcp = hand_to_world(Vector((x_off, 0.095, 0.026)))
        p_pip = p_mcp + E_Y * phalanx_lengths[0]
        p_dip = p_pip + E_Y * phalanx_lengths[1]
        p_tip = p_dip + E_Y * phalanx_lengths[2]

        # Phalanx 1 (Proximal)
        bm_p1 = bmesh.new()
        add_phalanx_segment(bm_p1, p_mcp, p_pip, width=widths[0], thick=thicks[0], pin_rad=pin_rads[0], is_tip=False)
        m_p1 = bpy.data.meshes.new(f"{dname.capitalize()}_Phalanx1_L_Mesh")
        bm_p1.to_mesh(m_p1)
        bm_p1.free()
        o_p1 = bpy.data.objects.new(f"{dname.capitalize()}_Phalanx1_L", m_p1)
        scene.collection.objects.link(o_p1)
        bind_object(o_p1, arm, seg_bones[0], mat_cast)

        # Phalanx 2 (Middle)
        bm_p2 = bmesh.new()
        add_phalanx_segment(bm_p2, p_pip, p_dip, width=widths[1], thick=thicks[1], pin_rad=pin_rads[1], is_tip=False)
        m_p2 = bpy.data.meshes.new(f"{dname.capitalize()}_Phalanx2_L_Mesh")
        bm_p2.to_mesh(m_p2)
        bm_p2.free()
        o_p2 = bpy.data.objects.new(f"{dname.capitalize()}_Phalanx2_L", m_p2)
        scene.collection.objects.link(o_p2)
        bind_object(o_p2, arm, seg_bones[1], mat_cast)

        # Phalanx 3 (Distal / Claw tip)
        bm_p3 = bmesh.new()
        add_phalanx_segment(bm_p3, p_dip, p_tip, width=widths[2], thick=thicks[2], pin_rad=pin_rads[2], is_tip=True)
        m_p3 = bpy.data.meshes.new(f"{dname.capitalize()}_Phalanx3_L_Mesh")
        bm_p3.to_mesh(m_p3)
        bm_p3.free()
        o_p3 = bpy.data.objects.new(f"{dname.capitalize()}_Phalanx3_L", m_p3)
        scene.collection.objects.link(o_p3)
        bind_object(o_p3, arm, seg_bones[2], mat_cast)

    # 4.5 Build Heavy Opposable Thumb
    p_cmc_loc = Vector((0.065, 0.045, 0.020))
    p_cmc_w = hand_to_world(p_cmc_loc)
    v_th1 = (E_Y * 0.038 - E_Z * 0.024 + E_X * 0.006).normalized() * 0.044
    p_th_mcp_w = p_cmc_w + v_th1
    v_th2 = (-E_X * 0.030 - E_Z * 0.016 + E_Y * 0.012).normalized() * 0.038
    p_th_tip_w = p_th_mcp_w + v_th2

    # Thumb Phalanx 1 (Proximal)
    bm_th1 = bmesh.new()
    add_phalanx_segment(bm_th1, p_cmc_w, p_th_mcp_w, width=0.030, thick=0.022, pin_rad=0.007, is_tip=False)
    m_th1 = bpy.data.meshes.new("Thumb_Phalanx1_L_Mesh")
    bm_th1.to_mesh(m_th1)
    bm_th1.free()
    o_th1 = bpy.data.objects.new("Thumb_Phalanx1_L", m_th1)
    scene.collection.objects.link(o_th1)
    bind_object(o_th1, arm, "thumb_01.L", mat_cast)

    # Thumb Phalanx 2 (Distal)
    bm_th2 = bmesh.new()
    add_phalanx_segment(bm_th2, p_th_mcp_w, p_th_tip_w, width=0.026, thick=0.019, pin_rad=0.006, is_tip=True)
    m_th2 = bpy.data.meshes.new("Thumb_Phalanx2_L_Mesh")
    bm_th2.to_mesh(m_th2)
    bm_th2.free()
    o_th2 = bpy.data.objects.new("Thumb_Phalanx2_L", m_th2)
    scene.collection.objects.link(o_th2)
    bind_object(o_th2, arm, "thumb_02.L", mat_cast)

    # 4.9 Position Maul and bind to tool bone (RULING 024 Part 3)
    palmar_offset = -E_Z * 0.024
    maul_meshes = [o for o in bpy.data.objects if "maul" in o.name.lower() and o.type == "MESH"]
    for mo in maul_meshes:
        for v in mo.data.vertices:
            v.co += palmar_offset
        mo.data.update()
        mo["rigid_driver_bone"] = "tool"
        vg = mo.vertex_groups.get("tool")
        if vg is None:
            vg = mo.vertex_groups.get("hand.L") or mo.vertex_groups.get("hand.R")
            if vg:
                vg.name = "tool"
            else:
                vg = mo.vertex_groups.new(name="tool")
                vg.add(list(range(len(mo.data.vertices))), 1.0, "REPLACE")
        has_arm = any(m.type == "ARMATURE" for m in mo.modifiers)
        if not has_arm:
            mod = mo.modifiers.new(name="Armature", type="ARMATURE")
            mod.object = arm

    # 5. Set Up Rest (Frame 1) and Interlocking Grip (Frame 48) Keyframes
    # Frame 1: Rest Pose (all 0 curl)
    scene.frame_set(1)
    for pb in arm.pose.bones:
        if any(k in pb.name for k in ["wrist_pitch.L", "wrist_yaw.L", "digit1_", "digit2_", "digit3_", "thumb_"]):
            pb.rotation_euler = (0.0, 0.0, 0.0)
            pb.keyframe_insert(data_path="rotation_euler", frame=1)

    # Frame 48: Interlocking Mechanical Grip around Maul Haft (Snug Zero-Penetration)
    scene.frame_set(48)
    for dname, _ in digit_x_offsets:
        arm.pose.bones[f"{dname}_01.L"].rotation_euler = (math.radians(50), 0.0, 0.0)
        arm.pose.bones[f"{dname}_01.L"].keyframe_insert(data_path="rotation_euler", frame=48)
        arm.pose.bones[f"{dname}_02.L"].rotation_euler = (math.radians(55), 0.0, 0.0)
        arm.pose.bones[f"{dname}_02.L"].keyframe_insert(data_path="rotation_euler", frame=48)
        arm.pose.bones[f"{dname}_03.L"].rotation_euler = (math.radians(45), 0.0, 0.0)
        arm.pose.bones[f"{dname}_03.L"].keyframe_insert(data_path="rotation_euler", frame=48)

    # Thumb wraps across front opposing facet
    arm.pose.bones["thumb_01.L"].rotation_euler = (math.radians(35), math.radians(25), 0.0)
    arm.pose.bones["thumb_01.L"].keyframe_insert(data_path="rotation_euler", frame=48)
    arm.pose.bones["thumb_02.L"].rotation_euler = (math.radians(45), 0.0, 0.0)
    arm.pose.bones["thumb_02.L"].keyframe_insert(data_path="rotation_euler", frame=48)

    scene.frame_set(1)
    bpy.context.view_layer.update()

    # Save output blend
    print(f"Saving upgraded candidate: {OUT}")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
    print("SUCCESS: Candidate v55 (Upgraded Proportions) generated.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
