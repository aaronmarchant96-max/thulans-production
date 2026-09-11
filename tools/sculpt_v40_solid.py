import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler
from pathlib import Path

source_parent = '/home/aaron/animation/thulans-production/blender/candidates/varek-v2b7-anchor-grounded.blend'
target_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v40-osint-juggernaut.blend'
bpy.ops.wm.open_mainfile(filepath=source_parent)
scene = bpy.context.scene

keep_exact = ['Varek_Original_Rig', 'Armature']
for obj in list(bpy.data.objects):
    if obj.name not in keep_exact and obj.type == 'MESH':
        bpy.data.objects.remove(obj, do_unlink=True)

arm = bpy.data.objects.get('Varek_Original_Rig') or bpy.data.objects.get('Armature')

def get_col(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        scene.collection.children.link(c)
    return c

col_hull = get_col('02_OPERATOR_HULL')
col_frame = get_col('03_LOAD_FRAME')
col_legs = get_col('05_LOWER_CHASSIS')
col_tools = get_col('06_MANIPULATORS')
col_mantle = get_col('08_REGALIA')

def get_mat(name, color, metallic=0.0, roughness=0.5, emit=0.0):
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        bsdf = m.node_tree.nodes.get('Principled BSDF')
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
        if emit > 0:
            bsdf.inputs['Emission Color'].default_value = color
            bsdf.inputs['Emission Strength'].default_value = emit
    return m

mat_iron = get_mat('QA_Cast_Iron', (0.12, 0.12, 0.13, 1.0), metallic=0.90, roughness=0.38)
mat_bronze = get_mat('QA_Cast_Bronze', (0.52, 0.34, 0.15, 1.0), metallic=0.92, roughness=0.30)
mat_amber = get_mat('QA_Amber_Visor', (1.0, 0.55, 0.05, 1.0), emit=8.0)
mat_dark_iron = get_mat('QA_Dark_Iron', (0.06, 0.06, 0.07, 1.0), metallic=0.94, roughness=0.32)
mat_cloth_green = get_mat('QA_Mantle_Green', (0.08, 0.14, 0.09, 1.0), metallic=0.0, roughness=0.92)
mat_leather = get_mat('QA_Belt_Leather', (0.15, 0.11, 0.07, 1.0), metallic=0.1, roughness=0.75)
mat_joint_rubber = get_mat('QA_Rubber_Bellows', (0.04, 0.04, 0.04, 1.0), metallic=0.05, roughness=0.85)

def finalize_obj(obj, name, col, mat=mat_iron, driver='spine'):
    obj.name = name
    obj['production_geometry'] = True
    obj['form_importance'] = 'PRIMARY'
    obj['rigid_driver_bone'] = driver
    if mat:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    if obj.name not in col.objects:
        col.objects.link(obj)
    if obj.name in scene.collection.objects:
        scene.collection.objects.unlink(obj)
    for p in obj.data.polygons:
        p.use_smooth = True
    if arm and 'Rigid_Armature' not in obj.modifiers:
        mod = obj.modifiers.new(name='Rigid_Armature', type='ARMATURE')
        mod.object = arm
    return obj

# -----------------------------------------------------------------------------
# 1. TORSO CUIRASS & HIGH U-SHAPED GORGET COLLAR
# -----------------------------------------------------------------------------
bm_cuirass = bmesh.new()
# Rings from crotch up into high gorget: (Z, rx, ry_front, ry_back, center_y)
c_profile = [
    (0.98, 0.28, -0.18, 0.16, 0.00),  # Pelvic crotch junction
    (1.18, 0.36, -0.24, 0.22, 0.00),  # Waist / belt level
    (1.38, 0.40, -0.28, 0.25, 0.00),  # Lower ribs
    (1.58, 0.46, -0.32, 0.28, -0.01), # Mid chest breadth
    (1.78, 0.48, -0.34, 0.30, -0.01), # Clavicle shelf
    (1.92, 0.38, -0.30, 0.28, 0.01),  # Gorget base
    (2.04, 0.30, -0.24, 0.30, 0.03),  # Gorget louver tier
    (2.18, 0.28, -0.20, 0.33, 0.05),  # High U-Collar top rim
]
c_rings = []
for z, rx, ry_f, ry_b, cy in c_profile:
    ring = []
    for i in range(32):
        th = 2.0 * math.pi * i / 32.0
        x = rx * math.sin(th)
        y_r = ry_f if math.cos(th) < 0 else ry_b
        y = cy + y_r * math.cos(th)
        ring.append(bm_cuirass.verts.new((x, y, z)))
    c_rings.append(ring)

for i in range(len(c_rings) - 1):
    r1, r2 = c_rings[i], c_rings[i+1]
    for j in range(32):
        bm_cuirass.faces.new((r1[j], r1[(j+1)%32], r2[(j+1)%32], r2[j]))

bm_cuirass.faces.new(reversed(c_rings[0]))
bmesh.ops.bevel(bm_cuirass, geom=list(bm_cuirass.edges), offset=0.012, segments=2, affect='EDGES')
me_cuirass = bpy.data.meshes.new('Operator_Cuirass_Mesh')
bm_cuirass.to_mesh(me_cuirass)
bm_cuirass.free()
obj_cuirass = bpy.data.objects.new('Operator_Cuirass_Gorget', me_cuirass)
scene.collection.objects.link(obj_cuirass)
finalize_obj(obj_cuirass, 'Operator_Cuirass_Gorget', col_hull, mat_iron, driver='spine')

# Gorget Bronze Trim
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.29, minor_radius=0.018,
    location=(0.0, 0.06, 2.18),
    rotation=(math.radians(12), 0, 0)
)
finalize_obj(bpy.context.active_object, 'Gorget_Top_Rim_Bronze', col_hull, mat_bronze, driver='spine')

# Gorget Vertical Ventilation Slots
for idx, x_louver in enumerate([-0.10, -0.06, -0.02, 0.02, 0.06, 0.10]):
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(x_louver, -0.24, 1.96),
        scale=(0.015, 0.015, 0.04)
    )
    finalize_obj(bpy.context.active_object, f'Gorget_Vent_Louver_{idx+1}', col_hull, mat_dark_iron, driver='spine')

# Central Pectoral Seal / 3-Spoke Hatch Wheel
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.11, depth=0.03,
    location=(0.0, -0.31, 1.62),
    rotation=(math.radians(88), 0, 0)
)
finalize_obj(bpy.context.active_object, 'Pectoral_Hatch_Flange', col_hull, mat_bronze, driver='spine')

bpy.ops.mesh.primitive_torus_add(
    major_radius=0.068, minor_radius=0.012,
    location=(0.0, -0.33, 1.62),
    rotation=(math.radians(88), 0, 0)
)
finalize_obj(bpy.context.active_object, 'Pectoral_Hatch_Handwheel', col_hull, mat_dark_iron, driver='spine')

for s_idx, rot in enumerate([0, 120, 240]):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.009, depth=0.12,
        location=(0.0, -0.33, 1.62),
        rotation=(math.radians(88), math.radians(rot), 0)
    )
    finalize_obj(bpy.context.active_object, f'Pectoral_Hatch_Spoke_{s_idx+1}', col_hull, mat_dark_iron, driver='spine')

# Heavy Utility Belt & Bronze Buckle
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.38, depth=0.08,
    location=(0.0, 0.0, 1.18),
    scale=(1.0, 0.76, 1.0)
)
finalize_obj(bpy.context.active_object, 'Operator_Utility_Belt', col_hull, mat_leather, driver='pelvis')

bpy.ops.mesh.primitive_cube_add(
    size=1.0, location=(0.0, -0.29, 1.18),
    scale=(0.10, 0.025, 0.09)
)
finalize_obj(bpy.context.active_object, 'Operator_Belt_Buckle', col_hull, mat_bronze, driver='pelvis')

# Belt Pouches & Hanging Rope Coil
bpy.ops.mesh.primitive_cube_add(
    size=1.0, location=(-0.26, -0.22, 1.18),
    scale=(0.07, 0.06, 0.08)
)
finalize_obj(bpy.context.active_object, 'Operator_Utility_Pouch', col_hull, mat_leather, driver='pelvis')

bpy.ops.mesh.primitive_torus_add(
    major_radius=0.11, minor_radius=0.022,
    location=(-0.38, -0.12, 1.05),
    rotation=(math.radians(75), math.radians(-20), 0)
)
finalize_obj(bpy.context.active_object, 'Operator_Equipment_Rope_Coil', col_hull, mat_dark_iron, driver='pelvis')

# -----------------------------------------------------------------------------
# 2. ENTOMBED HELMET & AMBER VISOR
# -----------------------------------------------------------------------------
bm_h = bmesh.new()
bmesh.ops.create_uvsphere(bm_h, u_segments=24, v_segments=16, radius=0.15)
for v in bm_h.verts:
    v.co.z = 2.05 + v.co.z * 1.15
    v.co.y = 0.04 + v.co.y * 1.05
    if v.co.y < 0:
        v.co.y *= 0.82
me_h = bpy.data.meshes.new('Operator_Pressure_Helmet_Mesh')
bm_h.to_mesh(me_h)
bm_h.free()
obj_h = bpy.data.objects.new('Operator_Pressure_Helmet', me_h)
scene.collection.objects.link(obj_h)
finalize_obj(obj_h, 'Operator_Pressure_Helmet', col_hull, mat_dark_iron, driver='yoke')

bpy.ops.mesh.primitive_cube_add(
    size=1.0, location=(0.0, -0.105, 2.08),
    scale=(0.11, 0.015, 0.022)
)
finalize_obj(bpy.context.active_object, 'Operator_Visor_Optical_Slit', col_hull, mat_amber, driver='yoke')

for side, x_pos in [('L', -0.105), ('R', 0.105)]:
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.038, depth=0.065,
        location=(x_pos, -0.068, 1.98),
        rotation=(math.radians(25), math.radians(-25 if side=='L' else 25), 0)
    )
    finalize_obj(bpy.context.active_object, f'Operator_Respirator_Boss_{side}', col_hull, mat_bronze, driver='yoke')

# -----------------------------------------------------------------------------
# 3. RIGHT ARM: ATLAS COPCO ROTARY-PERCUSSION DRILL ARM
# -----------------------------------------------------------------------------
# Bicep sleeve
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.125, depth=0.36,
    location=(0.66, -0.01, 1.54),
    rotation=(0, 0, 0)
)
finalize_obj(bpy.context.active_object, 'Armor_Bicep_R', col_tools, mat_iron, driver='upper_arm.R')

# Elbow flexible corrugated rubber bellows
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.11, depth=0.16,
    location=(0.70, -0.01, 1.30),
    rotation=(0, 0, 0)
)
finalize_obj(bpy.context.active_object, 'Arm_Elbow_Bellows_R', col_tools, mat_joint_rubber, driver='upper_arm.R')

# Forearm Armored Cylinder Sleeve
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.115, depth=0.40,
    location=(0.71, -0.02, 1.10),
    rotation=(0, 0, 0)
)
finalize_obj(bpy.context.active_object, 'Tool_Drill_Housing_Cuff', col_tools, mat_dark_iron, driver='forearm.R')

# Bronze Collar Ribs
for z_rib in [1.25, 1.10, 0.94]:
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.12, minor_radius=0.012,
        location=(0.71, -0.02, z_rib),
        rotation=(0, 0, 0)
    )
    finalize_obj(bpy.context.active_object, f'Tool_Drill_Collar_Rib_{z_rib}', col_tools, mat_bronze, driver='forearm.R')

# Analog Pressure Gauge Dial
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.035, depth=0.02,
    location=(0.79, -0.10, 1.20),
    rotation=(math.radians(35), math.radians(45), 0)
)
finalize_obj(bpy.context.active_object, 'Tool_Drill_Pressure_Gauge', col_tools, mat_bronze, driver='forearm.R')

# Hydraulic Accumulator & Piping Lines
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.034, depth=0.34,
    location=(0.83, -0.04, 1.12),
    rotation=(0, 0, 0)
)
finalize_obj(bpy.context.active_object, 'Tool_Drill_Hydraulic_Accumulator', col_tools, mat_iron, driver='forearm.R')

# Heavy Fluted Spiral Boring Head (Directly joined to forearm base at Z: 0.90 down to 0.44)
bm_bit = bmesh.new()
bmesh.ops.create_cone(
    bm_bit, segments=24, radius1=0.095, radius2=0.008, depth=0.46
)
for v in bm_bit.verts:
    ang = (v.co.z + 0.23) * 10.0
    x0, y0 = v.co.x, v.co.y
    v.co.x = (x0 * math.cos(ang) - y0 * math.sin(ang)) * (1.0 + 0.12 * math.cos(ang * 2))
    v.co.y = (x0 * math.sin(ang) + y0 * math.cos(ang)) * (1.0 + 0.12 * math.cos(ang * 2))
    v.co.z = 0.90 - (v.co.z + 0.23)
    v.co.x += 0.71
    v.co.y -= 0.02

me_bit = bpy.data.meshes.new('Tool_Drill_Spiral_Bit_Mesh')
bm_bit.to_mesh(me_bit)
bm_bit.free()
obj_bit = bpy.data.objects.new('Tool_Drill_Spiral_Bit', me_bit)
scene.collection.objects.link(obj_bit)
finalize_obj(obj_bit, 'Tool_Drill_Spiral_Bit', col_tools, mat_dark_iron, driver='forearm.R')

# -----------------------------------------------------------------------------
# 4. LEFT ARM: HOLMATRO 700-BAR RESCUE SHEARS
# -----------------------------------------------------------------------------
# Bicep sleeve
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.125, depth=0.36,
    location=(-0.66, -0.01, 1.54),
    rotation=(0, 0, 0)
)
finalize_obj(bpy.context.active_object, 'Armor_Bicep_L', col_tools, mat_iron, driver='upper_arm.L')

# Elbow flexible bellows
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.11, depth=0.16,
    location=(-0.70, -0.01, 1.30),
    rotation=(0, 0, 0)
)
finalize_obj(bpy.context.active_object, 'Arm_Elbow_Bellows_L', col_tools, mat_joint_rubber, driver='upper_arm.L')

# Forearm Armored Cylinder Sleeve
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.115, depth=0.40,
    location=(-0.71, -0.02, 1.10),
    rotation=(0, 0, 0)
)
finalize_obj(bpy.context.active_object, 'Tool_Shear_Housing_Cuff', col_tools, mat_dark_iron, driver='forearm.L')

# Dual Actuator Piston Rams
for dy, col_mat in [(-0.06, mat_bronze), (0.06, mat_iron)]:
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.034, depth=0.32,
        location=(-0.83, dy - 0.02, 1.10),
        rotation=(0, 0, 0)
    )
    finalize_obj(bpy.context.active_object, f'Tool_Shear_Actuator_Ram_{dy}', col_tools, col_mat, driver='forearm.L')

# Side Debris Mesh / Protective Shroud
bpy.ops.mesh.primitive_cube_add(
    size=1.0, location=(-0.81, -0.02, 0.92),
    scale=(0.04, 0.14, 0.16)
)
finalize_obj(bpy.context.active_object, 'Tool_Shear_Debris_Shroud', col_tools, mat_bronze, driver='forearm.L')

# Heavy Pivot Boss Hub
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.075, depth=0.14,
    location=(-0.71, -0.03, 0.88),
    rotation=(math.radians(90), 0, 0)
)
finalize_obj(bpy.context.active_object, 'Tool_Shear_Pivot_Boss', col_tools, mat_bronze, driver='forearm.L')

# Curved Stepped Demolition Cutting Blades (Directly continuous below wrist)
for j_idx, (j_name, dy_off, r_z) in enumerate([('Upper', 0.045, 18), ('Lower', -0.045, -22)]):
    bm_blade = bmesh.new()
    bmesh.ops.create_cube(bm_blade, size=1.0)
    for v in bm_blade.verts:
        v.co.x = v.co.x * 0.035 - 0.71
        v.co.y = v.co.y * 0.075 + dy_off - 0.03
        v.co.z = v.co.z * 0.22 + 0.74
        if v.co.z < 0.72:
            v.co.y += (-0.05 if j_name=='Upper' else 0.05)
    bmesh.ops.bevel(bm_blade, geom=list(bm_blade.edges), offset=0.008, segments=2, affect='EDGES')
    me_blade = bpy.data.meshes.new(f'Tool_Shear_Blade_{j_name}_Mesh')
    bm_blade.to_mesh(me_blade)
    bm_blade.free()
    obj_blade = bpy.data.objects.new(f'Tool_Shear_Blade_{j_name}', me_blade)
    scene.collection.objects.link(obj_blade)
    finalize_obj(obj_blade, f'Tool_Shear_Blade_{j_name}', col_tools, mat_dark_iron, driver='forearm.L')

# -----------------------------------------------------------------------------
# 5. LOWER CHASSIS: CUISSE, DOMED KNEE CUPS, GREAVES, 4-TOE TECTONIC BOOTS
# -----------------------------------------------------------------------------
for side, x_leg in [('L', -0.30), ('R', 0.30)]:
    thigh_drv = f'thigh.{side}'
    shin_drv = f'shin.{side}'
    foot_drv = f'foot.{side}'

    # Thigh / Cuisse Deflector Armor
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.18, depth=0.42,
        location=(x_leg, 0.01, 0.88),
        scale=(1.0, 0.88, 1.0)
    )
    finalize_obj(bpy.context.active_object, f'Armor_Cuisse_{side}', col_legs, mat_iron, driver=thigh_drv)

    # Bronze Cuisse Lower Flange Trim
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.18, minor_radius=0.015,
        location=(x_leg, 0.01, 0.68),
        rotation=(0, 0, 0)
    )
    finalize_obj(bpy.context.active_object, f'Armor_Cuisse_Trim_{side}', col_legs, mat_bronze, driver=thigh_drv)

    # Knee flexible rubber bellows seal
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.15, depth=0.12,
        location=(x_leg, 0.01, 0.62),
        rotation=(0, 0, 0)
    )
    finalize_obj(bpy.context.active_object, f'Knee_Rubber_Bellows_{side}', col_legs, mat_joint_rubber, driver=shin_drv)

    # Spherical Domed Knee Articulation Cop
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.135,
        location=(x_leg, -0.06, 0.62)
    )
    finalize_obj(bpy.context.active_object, f'Armor_Knee_Cop_{side}', col_legs, mat_iron, driver=shin_drv)

    # Bronze Knee Pivot Roundel Boss
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.045, depth=0.03,
        location=(x_leg + (-0.14 if side=='L' else 0.14), -0.06, 0.62),
        rotation=(0, math.radians(90), 0)
    )
    finalize_obj(bpy.context.active_object, f'Armor_Knee_Boss_{side}', col_legs, mat_bronze, driver=shin_drv)

    # Heavy Curved Greave (Shin Guard)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.17, depth=0.44,
        location=(x_leg, -0.01, 0.38),
        scale=(0.95, 0.84, 1.0)
    )
    finalize_obj(bpy.context.active_object, f'Armor_Greave_{side}', col_legs, mat_iron, driver=shin_drv)

    # Bronze Greave Ankle Collar Trim
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.165, minor_radius=0.015,
        location=(x_leg, -0.01, 0.17),
        rotation=(0, 0, 0)
    )
    finalize_obj(bpy.context.active_object, f'Armor_Greave_Ankle_Trim_{side}', col_legs, mat_bronze, driver=shin_drv)

    # Rear Hydraulic Stabilizer Ram on Calf
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.028, depth=0.28,
        location=(x_leg, 0.17, 0.38),
        rotation=(math.radians(-10), 0, 0)
    )
    finalize_obj(bpy.context.active_object, f'Armor_Calf_Stabilizer_Ram_{side}', col_legs, mat_bronze, driver=shin_drv)

    # Multi-Segment Tectonic Anchor Boot Chassis (Directly joined to ground contact at Z: 0.00)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(x_leg, -0.06, 0.07),
        scale=(0.26, 0.44, 0.14)
    )
    finalize_obj(bpy.context.active_object, f'Anchor_Boot_Chassis_{side}', col_legs, mat_dark_iron, driver=foot_drv)

    # 4-Segment Articulated Excavator Toe Claws
    for t_idx, x_toe_off in enumerate([-0.09, -0.03, 0.03, 0.09]):
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(x_leg + x_toe_off, -0.28, 0.04),
            scale=(0.048, 0.12, 0.07),
            rotation=(math.radians(18), 0, 0)
        )
        finalize_obj(bpy.context.active_object, f'Anchor_Toe_Segment_{side}_{t_idx+1}', col_legs, mat_iron, driver=foot_drv)

# -----------------------------------------------------------------------------
# 6. PAULDRONS & GREN-SKILDUS CEREMONIAL MANTLE
# -----------------------------------------------------------------------------
for side, x_sh in [('L', -0.58), ('R', 0.58)]:
    sh_drv = f'upper_arm.{side}'
    for tier, (z_p, sc, rot_y) in enumerate([
        (1.92, (0.28, 0.32, 0.09), -22 if side=='L' else 22),
        (1.83, (0.26, 0.30, 0.08), -14 if side=='L' else 14),
        (1.74, (0.24, 0.28, 0.07), -6 if side=='L' else 6)
    ]):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=1.0, depth=1.0,
            location=(x_sh, 0.00, z_p),
            rotation=(0, math.radians(rot_y), 0)
        )
        obj_paul = bpy.context.active_object
        obj_paul.scale = sc
        finalize_obj(obj_paul, f'Puldron_Tier_{tier+1}_{side}', col_frame, mat_iron, driver=sh_drv)

        if tier == 0:
            bpy.ops.mesh.primitive_torus_add(
                major_radius=0.30, minor_radius=0.015,
                location=(x_sh, 0.00, z_p + 0.04),
                rotation=(0, math.radians(rot_y), 0)
            )
            finalize_obj(bpy.context.active_object, f'Puldron_Trim_{side}', col_frame, mat_bronze, driver=sh_drv)

# Forest Green Gren-Skildus Heavy Ceremonial Mantle
bm_m = bmesh.new()
m_grid = [
    # Top shoulder loop
    [(0.36, -0.18, 1.96), (0.46, -0.06, 1.98), (0.48, 0.12, 1.96), (0.38, 0.24, 1.92)],
    # Mid drape
    [(0.34, -0.22, 1.65), (0.48, -0.08, 1.62), (0.50, 0.14, 1.60), (0.36, 0.26, 1.58)],
    # Lower flank fold
    [(0.32, -0.20, 1.30), (0.46, -0.08, 1.25), (0.48, 0.14, 1.22), (0.34, 0.24, 1.20)],
    # Tattered hem
    [(0.30, -0.18, 0.95), (0.44, -0.06, 0.90), (0.46, 0.12, 0.88), (0.32, 0.22, 0.86)]
]

v_rows = []
for row in m_grid:
    v_rows.append([bm_m.verts.new(pt) for pt in row])

for r in range(len(v_rows) - 1):
    for c in range(3):
        bm_m.faces.new((v_rows[r][c], v_rows[r][c+1], v_rows[r+1][c+1], v_rows[r+1][c]))

bmesh.ops.solidify(bm_m, geom=list(bm_m.faces), thickness=0.025)
me_m = bpy.data.meshes.new('Gren_Skildus_Mantle_Mesh')
bm_m.to_mesh(me_m)
bm_m.free()
obj_m = bpy.data.objects.new('Gren_Skildus_Mantle', me_m)
scene.collection.objects.link(obj_m)
finalize_obj(obj_m, 'Gren_Skildus_Mantle', col_mantle, mat_cloth_green, driver='spine')

# Ancient Circular Bronze Ring Brooch / Torc Clasp
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.085, minor_radius=0.016,
    location=(0.36, -0.24, 1.86),
    rotation=(math.radians(45), math.radians(-25), 0)
)
finalize_obj(bpy.context.active_object, 'Gren_Skildus_Torc_Clasp', col_mantle, mat_bronze, driver='spine')

# -----------------------------------------------------------------------------
# 7. SAVE COMPLETE V40 BLEND FILE
# -----------------------------------------------------------------------------
bpy.ops.wm.save_as_mainfile(filepath=target_blend)
print(f"SUCCESS: Solid Aligned V40 Juggernaut saved to {target_blend}")

