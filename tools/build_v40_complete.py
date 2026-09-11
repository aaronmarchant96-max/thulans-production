import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler
from pathlib import Path

# -----------------------------------------------------------------------------
# 1. LOAD LAST KNOWN GOOD BASELINE AND INITIALIZE
# -----------------------------------------------------------------------------
source_parent = '/home/aaron/animation/thulans-production/blender/candidates/varek-v2b7-anchor-grounded.blend'
target_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v40-osint-juggernaut.blend'

bpy.ops.wm.open_mainfile(filepath=source_parent)
scene = bpy.context.scene

def get_or_create_col(name):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        scene.collection.children.link(col)
    return col

col_hull = get_or_create_col('02_OPERATOR_HULL')
col_frame = get_or_create_col('03_LOAD_FRAME')
col_legs = get_or_create_col('05_LOWER_CHASSIS')
col_tools = get_or_create_col('06_MANIPULATORS')
col_mantle = get_or_create_col('08_REGALIA')

# -----------------------------------------------------------------------------
# 2. MATERIALS
# -----------------------------------------------------------------------------
def get_or_create_mat(name, color, metallic=0.0, roughness=0.5, emit=0.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
        if emit > 0:
            bsdf.inputs['Emission Color'].default_value = color
            bsdf.inputs['Emission Strength'].default_value = emit
    return mat

mat_iron = get_or_create_mat('QA_Cast_Iron', (0.12, 0.12, 0.13, 1.0), metallic=0.88, roughness=0.38)
mat_dark_iron = get_or_create_mat('QA_Dark_Steel', (0.07, 0.07, 0.08, 1.0), metallic=0.92, roughness=0.30)
mat_bronze = get_or_create_mat('QA_Cast_Bronze', (0.50, 0.32, 0.14, 1.0), metallic=0.90, roughness=0.32)
mat_amber = get_or_create_mat('QA_Amber_Visor', (1.0, 0.55, 0.05, 1.0), emit=6.0)
mat_rubber = get_or_create_mat('QA_Joint_Rubber', (0.03, 0.03, 0.04, 1.0), metallic=0.05, roughness=0.85)
mat_cloth = get_or_create_mat('QA_Gren_Skildus_Wool', (0.18, 0.06, 0.06, 1.0), metallic=0.0, roughness=0.90)

arm = bpy.data.objects.get('Varek_Original_Rig') or bpy.data.objects.get('Armature')

def tag_obj(obj, name, col, mat=mat_iron, driver='spine'):
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
    for poly in obj.data.polygons:
        poly.use_smooth = True
    if arm and 'Rigid_Armature' not in obj.modifiers:
        mod = obj.modifiers.new(name='Rigid_Armature', type='ARMATURE')
        mod.object = arm
    return obj

# Purge any old / prototype test objects
purge_patterns = [
    'Operator_Pressure_Helmet', 'Operator_Respirator', 'Operator_Visor', 'Operator_Cuirass',
    'Operator_Thoracic', 'Operator_Cell', 'Thoracic_Wing', 'Thoracic_Center', 'Abdominal_Cage',
    'Tool_Drill', 'Tool_Shear', 'Gren_Skildus', 'Puldron', 'Pectoral_Crest', 'Anchor_Boot_Plate',
    'Thigh_Guard', 'Shin_Guard', 'Pneumatic_Accumulator', 'Spreader_Jaw', 'Drill_Bit'
]
for obj in list(bpy.data.objects):
    for pat in purge_patterns:
        if pat in obj.name:
            bpy.data.objects.remove(obj, do_unlink=True)
            break

# -----------------------------------------------------------------------------
# 3. PHASE 1: JUGGERNAUT CUIRASS, HIGH GORGET RAMPART, HELMET, MANTLE
# -----------------------------------------------------------------------------
# 3A. CAST-IRON CUIRASS & HIGH GORGET
# Authentic 8-foot proportions: heavy trapezoidal chest tapering to armored waist
bm_cuirass = bmesh.new()
cuirass_profile = [
    (1.18, 0.32, -0.20, 0.20, 0.00), # Pelvic flange
    (1.36, 0.36, -0.25, 0.24, -0.01), # Mid abdominal
    (1.58, 0.44, -0.30, 0.28, -0.02), # Lower pectoral breadth
    (1.78, 0.46, -0.32, 0.30, -0.01), # Clavicle shelf
    (1.94, 0.34, -0.28, 0.28, 0.02),  # Gorget base
    (2.06, 0.28, -0.25, 0.30, 0.05),  # High gorget lip / chin guard
]
rings = []
for z, rx, ry_f, ry_b, cy in cuirass_profile:
    ring = []
    for i in range(24):
        th = 2.0 * math.pi * i / 24.0
        x = rx * math.sin(th)
        y_r = ry_f if math.cos(th) < 0 else ry_b
        y = cy + y_r * math.cos(th)
        ring.append(bm_cuirass.verts.new((x, y, z)))
    rings.append(ring)

for i in range(len(rings) - 1):
    r1, r2 = rings[i], rings[i+1]
    for j in range(24):
        bm_cuirass.faces.new((r1[j], r1[(j+1)%24], r2[(j+1)%24], r2[j]))

bm_cuirass.faces.new(reversed(rings[0]))
bmesh.ops.bevel(bm_cuirass, geom=list(bm_cuirass.edges), offset=0.015, segments=2, affect='EDGES')
me_cuirass = bpy.data.meshes.new('Operator_Cuirass_Gorget_Mesh')
bm_cuirass.to_mesh(me_cuirass)
bm_cuirass.free()

obj_cuirass = bpy.data.objects.new('Operator_Cuirass_Gorget', me_cuirass)
scene.collection.objects.link(obj_cuirass)
tag_obj(obj_cuirass, 'Operator_Cuirass_Gorget', col_hull, mat_iron, driver='spine')

# 3B. ENTOMBED HELMET (WELDED ENCLOSURE WITH AMBER NARROW SLIT & FILTER BOSSES)
bm_helm = bmesh.new()
# Welded faceted skull vault
bmesh.ops.create_cube(bm_helm, size=0.28)
for v in bm_helm.verts:
    v.co.z = 2.04 + v.co.z * 1.15
    v.co.y = 0.02 + v.co.y * 1.10
    v.co.x = v.co.x * 1.05
    if v.co.z > 2.10:
        v.co.x *= 0.85
        v.co.y *= 0.88
bmesh.ops.bevel(bm_helm, geom=list(bm_helm.edges), offset=0.025, segments=3, affect='EDGES')
me_helm = bpy.data.meshes.new('Operator_Pressure_Helmet_Mesh')
bm_helm.to_mesh(me_helm)
bm_helm.free()
obj_helm = bpy.data.objects.new('Operator_Pressure_Helmet', me_helm)
scene.collection.objects.link(obj_helm)
tag_obj(obj_helm, 'Operator_Pressure_Helmet', col_hull, mat_iron, driver='head')

# Amber Visor Optical Slit
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.138, 2.06), scale=(0.09, 0.012, 0.018))
obj_visor = bpy.context.active_object
tag_obj(obj_visor, 'Operator_Visor_Optical_Slit', col_hull, mat_amber, driver='head')

# Respirator Filter Bosses (Dual High-Pressure Canisters)
for side, x_pos in [('L', 0.125), ('R', -0.125)]:
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.042, depth=0.08,
        location=(x_pos, -0.09, 1.98),
        rotation=(math.radians(25), math.radians(20 if side=='L' else -20), 0)
    )
    obj_can = bpy.context.active_object
    tag_obj(obj_can, f'Operator_Respirator_Boss_{side}', col_hull, mat_bronze, driver='head')

# 3C. HEAVY ROLL-CAGE YOKE & DORSAL POWER PACK
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.38, minor_radius=0.038,
    location=(0.0, 0.02, 1.88),
    rotation=(math.radians(15), 0, 0)
)
obj_yoke = bpy.context.active_object
tag_obj(obj_yoke, 'Structural_RollCage_Yoke', col_frame, mat_dark_iron, driver='chest')

# Dorsal Compressor / Power Core Housing
bpy.ops.mesh.primitive_cube_add(
    size=1.0, location=(0.0, 0.28, 1.62),
    scale=(0.28, 0.16, 0.32)
)
obj_pack = bpy.context.active_object
tag_obj(obj_pack, 'Dorsal_Power_Compressor_Unit', col_frame, mat_dark_iron, driver='chest')

# Dorsal Heat Shield Louvers
for idx, z_louver in enumerate([1.50, 1.58, 1.66, 1.74]):
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(0.0, 0.37, z_louver),
        scale=(0.22, 0.015, 0.025),
        rotation=(math.radians(-25), 0, 0)
    )
    obj_louver = bpy.context.active_object
    tag_obj(obj_louver, f'Dorsal_Heat_Louver_{idx+1}', col_frame, mat_bronze, driver='chest')

# -----------------------------------------------------------------------------
# 4. PHASE 2: TOOL STATIONS & FOREARM MANIPULATORS
# -----------------------------------------------------------------------------
# 4A. RIGHT FOREARM: HEAVY ATLAS COPCO HYDRAULIC ROTARY-PERCUSSION DRILL ARM
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.095, depth=0.36,
    location=(-0.60, 0.00, 1.05),
    rotation=(0, 0, 0)
)
obj_drill_housing = bpy.context.active_object
tag_obj(obj_drill_housing, 'Tool_Drill_Percussion_Motor_Housing', col_tools, mat_dark_iron, driver='forearm.R')

# Pneumatic Accumulator Cylinder on outer flank
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.045, depth=0.30,
    location=(-0.70, -0.03, 1.06),
    rotation=(0, 0, 0)
)
obj_drill_accum = bpy.context.active_object
tag_obj(obj_drill_accum, 'Tool_Drill_Pneumatic_Accumulator', col_tools, mat_bronze, driver='forearm.R')

# Twin External Thrust Feed Cylinders
for cy_idx, (dy, dx) in enumerate([(-0.06, -0.06), (0.06, -0.06)]):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.022, depth=0.38,
        location=(-0.60 + dx, dy, 1.02),
        rotation=(0, 0, 0)
    )
    obj_cyl = bpy.context.active_object
    tag_obj(obj_cyl, f'Tool_Drill_Thrust_Cylinder_{cy_idx+1}', col_tools, mat_iron, driver='forearm.R')

# Chuck / Collar Flange
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.075, depth=0.08,
    location=(-0.60, 0.00, 0.84),
    rotation=(0, 0, 0)
)
obj_drill_chuck = bpy.context.active_object
tag_obj(obj_drill_chuck, 'Tool_Drill_Hardened_Chucking_Collar', col_tools, mat_bronze, driver='hand.R')

# Fluted Spiral Boring Head
bm_drill = bmesh.new()
bmesh.ops.create_cone(
    bm_drill, segments=16, radius1=0.065, radius2=0.012, depth=0.28
)
for v in bm_drill.verts:
    angle = (v.co.z + 0.14) * 8.0
    x_old = v.co.x
    y_old = v.co.y
    v.co.x = x_old * math.cos(angle) - y_old * math.sin(angle)
    v.co.y = x_old * math.sin(angle) + y_old * math.cos(angle)
    v.co.z += 0.68
    v.co.x -= 0.60

me_drill_bit = bpy.data.meshes.new('Tool_Drill_Spiral_Bit_Mesh')
bm_drill.to_mesh(me_drill_bit)
bm_drill.free()
obj_drill_bit = bpy.data.objects.new('Tool_Drill_Spiral_Bit', me_drill_bit)
scene.collection.objects.link(obj_drill_bit)
tag_obj(obj_drill_bit, 'Tool_Drill_Spiral_Bit', col_tools, mat_dark_iron, driver='hand.R')

# 4B. LEFT FOREARM: HOLMATRO 700-BAR DEMOLITION SPREADER / RESCUE SHEAR
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.095, depth=0.36,
    location=(0.60, 0.00, 1.05),
    rotation=(0, 0, 0)
)
obj_shear_body = bpy.context.active_object
tag_obj(obj_shear_body, 'Tool_Shear_Actuator_Chassis', col_tools, mat_dark_iron, driver='forearm.L')

# Dual Hydraulic Actuation Rams
for r_idx, dy in enumerate([-0.05, 0.05]):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.038, depth=0.26,
        location=(0.60, dy, 0.98),
        rotation=(0, 0, 0)
    )
    obj_ram = bpy.context.active_object
    tag_obj(obj_ram, f'Tool_Shear_Hydraulic_Ram_{r_idx+1}', col_tools, mat_bronze, driver='forearm.L')

# Shear Jaws Pivot Hub
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.065, depth=0.10,
    location=(0.60, 0.00, 0.84),
    rotation=(math.radians(90), 0, 0)
)
obj_jaw_hub = bpy.context.active_object
tag_obj(obj_jaw_hub, 'Tool_Shear_Central_Pivot_Boss', col_tools, mat_iron, driver='hand.L')

# Left / Right Hardened Stepped Cutting Blades
for jaw_name, x_offset, rot_z in [('Upper', 0.035, 12), ('Lower', -0.035, -12)]:
    bm_jaw = bmesh.new()
    bmesh.ops.create_cube(bm_jaw, size=1.0)
    for v in bm_jaw.verts:
        v.co.x = v.co.x * 0.025 + (0.60 + x_offset)
        v.co.y = v.co.y * 0.065
        v.co.z = v.co.z * 0.16 + 0.68
        if v.co.z < 0.64:
            v.co.y += 0.03
    me_jaw = bpy.data.meshes.new(f'Tool_Shear_Blade_{jaw_name}_Mesh')
    bm_jaw.to_mesh(me_jaw)
    bm_jaw.free()
    obj_jaw = bpy.data.objects.new(f'Tool_Shear_Blade_{jaw_name}', me_jaw)
    scene.collection.objects.link(obj_jaw)
    tag_obj(obj_jaw, f'Tool_Shear_Blade_{jaw_name}', col_tools, mat_iron, driver='hand.L')

# -----------------------------------------------------------------------------
# 5. PHASE 3: LOWER CHASSIS & TECTONIC ANCHOR BOOTS
# -----------------------------------------------------------------------------
# 5A. HEAVY THIGH & SHIN ARMOR PLATES
for side, x_leg, leg_driver in [('L', 0.22, 'thigh.L'), ('R', -0.22, 'thigh.R')]:
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.15, depth=0.36,
        location=(x_leg, -0.02, 0.88),
        rotation=(0, 0, 0)
    )
    obj_thigh = bpy.context.active_object
    obj_thigh.scale = (1.0, 0.85, 1.0)
    tag_obj(obj_thigh, f'Thigh_Guard_Plate_{side}', col_legs, mat_iron, driver=leg_driver)

    shin_driver = f'shin.{side}'
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.14, depth=0.38,
        location=(x_leg, -0.03, 0.44),
        rotation=(0, 0, 0)
    )
    obj_shin = bpy.context.active_object
    obj_shin.scale = (0.95, 0.80, 1.0)
    tag_obj(obj_shin, f'Shin_Guard_Plate_{side}', col_legs, mat_iron, driver=shin_driver)

    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(x_leg, -0.16, 0.64),
        scale=(0.14, 0.05, 0.12),
        rotation=(math.radians(20), 0, 0)
    )
    obj_knee = bpy.context.active_object
    tag_obj(obj_knee, f'Knee_Articulation_Cop_{side}', col_legs, mat_bronze, driver=shin_driver)

# 5B. MULTI-SEGMENT TECTONIC ANCHOR BOOTS
for side, x_boot, foot_driver in [('L', 0.22, 'foot.L'), ('R', -0.22, 'foot.R')]:
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(x_boot, 0.04, 0.04),
        scale=(0.22, 0.42, 0.08)
    )
    obj_sole = bpy.context.active_object
    tag_obj(obj_sole, f'Anchor_Boot_Sole_{side}', col_legs, mat_dark_iron, driver=foot_driver)

    for c_idx, x_claw in enumerate([-0.06, 0.0, 0.06]):
        bpy.ops.mesh.primitive_cone_add(
            radius1=0.025, depth=0.10,
            location=(x_boot + x_claw, -0.20, 0.04),
            rotation=(math.radians(90), 0, 0)
        )
        obj_claw = bpy.context.active_object
        tag_obj(obj_claw, f'Anchor_Toe_Claw_{side}_{c_idx+1}', col_legs, mat_bronze, driver=foot_driver)

    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.035, depth=0.16,
        location=(x_boot, 0.24, 0.12),
        rotation=(math.radians(-20), 0, 0)
    )
    obj_heel = bpy.context.active_object
    tag_obj(obj_heel, f'Anchor_Heel_Ram_{side}', col_legs, mat_bronze, driver=foot_driver)

# -----------------------------------------------------------------------------
# 6. PHASE 4: 3-TIER FLARED PAULDRONS & GREN-SKILDUS MANTLE
# -----------------------------------------------------------------------------
# 6A. 3-TIER FLARED SHOULDER PAULDRONS
for side, x_shoulder, shoulder_driver in [('L', 0.48, 'shoulder.L'), ('R', -0.48, 'shoulder.R')]:
    for tier, (z_p, scale_p, rot_y) in enumerate([
        (1.88, (0.24, 0.28, 0.08), 25 if side=='L' else -25),
        (1.80, (0.22, 0.26, 0.07), 15 if side=='L' else -15),
        (1.72, (0.20, 0.24, 0.06), 5 if side=='L' else -5)
    ]):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=1.0, depth=1.0,
            location=(x_shoulder, 0.00, z_p),
            rotation=(0, math.radians(rot_y), 0)
        )
        obj_p = bpy.context.active_object
        obj_p.scale = scale_p
        tag_obj(obj_p, f'Puldron_Tier_{tier+1}_{side}', col_frame, mat_iron, driver=shoulder_driver)

# 6B. GREN-SKILDUS HEAVY CEREMONIAL MANTLE & ANCIENT CLASP
bm_mantle = bmesh.new()
mantle_verts = [
    (0.38, -0.22, 1.84), (0.20, -0.32, 1.70), (0.00, -0.32, 1.55), (-0.18, -0.28, 1.40),
    (0.44, 0.00, 1.86),  (0.24, 0.00, 1.72),  (0.02, 0.00, 1.57),  (-0.16, 0.00, 1.42),
    (0.40, 0.24, 1.84),  (0.22, 0.28, 1.70),  (0.00, 0.28, 1.55),  (-0.18, 0.26, 1.40)
]
v_objs = [bm_mantle.verts.new(pt) for pt in mantle_verts]
for row in range(2):
    for col in range(3):
        i0 = row * 4 + col
        i1 = i0 + 1
        i2 = i0 + 5
        i3 = i0 + 4
        bm_mantle.faces.new((v_objs[i0], v_objs[i1], v_objs[i2], v_objs[i3]))

bmesh.ops.solidify(bm_mantle, geom=list(bm_mantle.faces), thickness=0.03)
me_mantle = bpy.data.meshes.new('Gren_Skildus_Mantle_Mesh')
bm_mantle.to_mesh(me_mantle)
bm_mantle.free()

obj_mantle = bpy.data.objects.new('Gren_Skildus_Mantle', me_mantle)
scene.collection.objects.link(obj_mantle)
tag_obj(obj_mantle, 'Gren_Skildus_Mantle', col_mantle, mat_cloth, driver='chest')

# Ancient Heavy Bronze Ring Brooch Clasp
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.07, minor_radius=0.015,
    location=(0.28, -0.26, 1.78),
    rotation=(math.radians(35), math.radians(-25), 0)
)
obj_clasp = bpy.context.active_object
tag_obj(obj_clasp, 'Gren_Skildus_Ring_Clasp', col_mantle, mat_bronze, driver='chest')

# Pectoral Crest Seal
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.08, depth=0.02,
    location=(0.0, -0.32, 1.66),
    rotation=(math.radians(85), 0, 0)
)
obj_crest = bpy.context.active_object
tag_obj(obj_crest, 'Pectoral_Crest_Seal', col_hull, mat_bronze, driver='chest')

# -----------------------------------------------------------------------------
# 7. SAVE COMPLETE V40 JUGGERNAUT BLEND FILE
# -----------------------------------------------------------------------------
bpy.ops.wm.save_as_mainfile(filepath=target_blend)
print(f"SUCCESS: Complete Varek V40 OSINT Juggernaut saved to {target_blend}")

