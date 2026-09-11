import bpy
import math
from mathutils import Euler, Quaternion, Vector

source_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-juggernaut-v19.blend'
save_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v20-canonical.blend'

# Open file
bpy.ops.wm.open_mainfile(filepath=source_blend)

arm = bpy.data.objects.get('Varek simple articulation')

# Helper: add vertex group and armature modifier
def bind_to_bone(obj, bone_name):
    if not obj or not arm:
        return
    vg = obj.vertex_groups.get(bone_name)
    if not vg:
        vg = obj.vertex_groups.new(name=bone_name)
    vg.add([v.index for v in obj.data.vertices], 1.0, 'REPLACE')
    
    arm_mod = None
    for m in obj.modifiers:
        if m.type == 'ARMATURE':
            arm_mod = m
            break
    if not arm_mod:
        arm_mod = obj.modifiers.new(name='Rigid single bone', type='ARMATURE')
    arm_mod.object = arm

mat_cast_iron = bpy.data.materials.get('Warm charcoal cast iron')
mat_bronze = bpy.data.materials.get('Aged brass')
mat_steel = bpy.data.materials.get('Working piston steel')
mat_visor = bpy.data.materials.get('Amber visor')

# =========================================================================
# 1. HELMET / HEAD SUITE (PANEL 01)
# =========================================================================

# A. Reinforced Brow Overhang
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(0.0, -0.32, 2.22),
    rotation=(math.radians(12), 0, 0)
)
brow_obj = bpy.context.active_object
brow_obj.name = "Helmet_Reinforced_Brow"
brow_obj.scale = (0.28, 0.14, 0.045)
bpy.ops.object.transform_apply(scale=True)
if mat_cast_iron:
    brow_obj.data.materials.append(mat_cast_iron)
bind_to_bone(brow_obj, 'head')

# B. Dual Respirator Intake Grilles (Jaw Left & Right)
for side, x_pos in [('L', 0.095), ('R', -0.095)]:
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(x_pos, -0.31, 1.97),
        rotation=(0, 0, math.radians(-10 if side=='L' else 10))
    )
    resp_obj = bpy.context.active_object
    resp_obj.name = f"Helmet_Respirator_Intake_{side}"
    resp_obj.scale = (0.065, 0.08, 0.12)
    bpy.ops.object.transform_apply(scale=True)
    if mat_cast_iron:
        resp_obj.data.materials.append(mat_cast_iron)
    bind_to_bone(resp_obj, 'head')
    
    # Intake louvre ribs
    for r_idx in range(3):
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(x_pos, -0.355, 1.94 + r_idx*0.032),
            rotation=(math.radians(25), 0, math.radians(-10 if side=='L' else 10))
        )
        rib = bpy.context.active_object
        rib.name = f"Respirator_Rib_{side}_{r_idx}"
        rib.scale = (0.05, 0.012, 0.008)
        bpy.ops.object.transform_apply(scale=True)
        if mat_bronze:
            rib.data.materials.append(mat_bronze)
        bind_to_bone(rib, 'head')

# C. Segmented Neck Collar Ring
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.18,
    minor_radius=0.032,
    location=(0.0, -0.10, 1.86),
    rotation=(math.radians(10), 0, 0)
)
neck_ring = bpy.context.active_object
neck_ring.name = "Neck_Segmented_Collar_Ring"
if mat_bronze:
    neck_ring.data.materials.append(mat_bronze)
bind_to_bone(neck_ring, 'head')


# =========================================================================
# 2. INTEGRATED CHEST WINCH & RECOVERY CLEVIS SHACKLE (PANEL 03)
# =========================================================================

# A. Heavy Winch Drum Housing
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.095,
    depth=0.34,
    location=(0.0, -0.38, 1.46),
    rotation=(0, math.radians(90), 0)
)
winch_drum = bpy.context.active_object
winch_drum.name = "Chest_Winch_Drum_Housing"
if mat_cast_iron:
    winch_drum.data.materials.append(mat_cast_iron)
bind_to_bone(winch_drum, 'spine')

# B. Wound Steel Cable Rings
for c_idx in range(11):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.088,
        minor_radius=0.014,
        location=(-0.14 + c_idx*0.028, -0.38, 1.46),
        rotation=(0, math.radians(90), 0)
    )
    cable_ring = bpy.context.active_object
    cable_ring.name = f"Winch_Cable_Coil_{c_idx}"
    if mat_steel:
        cable_ring.data.materials.append(mat_steel)
    bind_to_bone(cable_ring, 'spine')

# C. Winch Flanges / End Brackets
for f_side, f_x in [('L', 0.18), ('R', -0.18)]:
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.125,
        depth=0.035,
        location=(f_x, -0.38, 1.46),
        rotation=(0, math.radians(90), 0)
    )
    flange = bpy.context.active_object
    flange.name = f"Winch_Side_Flange_{f_side}"
    if mat_bronze:
        flange.data.materials.append(mat_bronze)
    bind_to_bone(flange, 'spine')

# D. Heavy Recovery U-Shackle (Clevis)
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.052,
    minor_radius=0.018,
    location=(0.0, -0.40, 1.30),
    rotation=(math.radians(90), 0, 0)
)
shackle = bpy.context.active_object
shackle.name = "Chest_Recovery_U_Shackle"
shackle.scale = (1.0, 1.0, 1.25)
bpy.ops.object.transform_apply(scale=True)
if mat_bronze:
    shackle.data.materials.append(mat_bronze)
bind_to_bone(shackle, 'spine')

# Shackle Cross-Pin
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.018,
    depth=0.14,
    location=(0.0, -0.40, 1.35),
    rotation=(0, math.radians(90), 0)
)
shackle_pin = bpy.context.active_object
shackle_pin.name = "Chest_Shackle_Cross_Pin"
if mat_steel:
    shackle_pin.data.materials.append(mat_steel)
bind_to_bone(shackle_pin, 'spine')

# E. Breastplate Central Thulan Cross Crest
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.415, 1.74))
crest_vert = bpy.context.active_object
crest_vert.name = "Breastplate_Thulan_Cross_Vertical"
crest_vert.scale = (0.024, 0.015, 0.18)
bpy.ops.object.transform_apply(scale=True)
if mat_bronze:
    crest_vert.data.materials.append(mat_bronze)
bind_to_bone(crest_vert, 'spine')

# Upper Crossbar
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.415, 1.78))
crest_h1 = bpy.context.active_object
crest_h1.name = "Breastplate_Thulan_Cross_UpperBar"
crest_h1.scale = (0.09, 0.015, 0.022)
bpy.ops.object.transform_apply(scale=True)
if mat_bronze:
    crest_h1.data.materials.append(mat_bronze)
bind_to_bone(crest_h1, 'spine')

# Lower Crossbar
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.415, 1.72))
crest_h2 = bpy.context.active_object
crest_h2.name = "Breastplate_Thulan_Cross_LowerBar"
crest_h2.scale = (0.065, 0.015, 0.020)
bpy.ops.object.transform_apply(scale=True)
if mat_bronze:
    crest_h2.data.materials.append(mat_bronze)
bind_to_bone(crest_h2, 'spine')


# =========================================================================
# 3. LEFT THIGH PLAQUE ("V FAIRGUNJIS") (PANEL 03)
# =========================================================================

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.28, -0.41, 0.98), rotation=(math.radians(10), 0, 0))
thigh_plaque = bpy.context.active_object
thigh_plaque.name = "Thigh_Fairgunjis_Plaque"
thigh_plaque.scale = (0.16, 0.025, 0.20)
bpy.ops.object.transform_apply(scale=True)
if mat_cast_iron:
    thigh_plaque.data.materials.append(mat_cast_iron)
bind_to_bone(thigh_plaque, 'thigh.L')

# Bronze Roman V Crest
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.012,
    depth=0.08,
    location=(0.265, -0.425, 1.02),
    rotation=(math.radians(10), math.radians(20), 0)
)
v_left = bpy.context.active_object
v_left.name = "Thigh_V_Left"
if mat_bronze:
    v_left.data.materials.append(mat_bronze)
bind_to_bone(v_left, 'thigh.L')

bpy.ops.mesh.primitive_cylinder_add(
    radius=0.012,
    depth=0.08,
    location=(0.295, -0.425, 1.02),
    rotation=(math.radians(10), math.radians(-20), 0)
)
v_right = bpy.context.active_object
v_right.name = "Thigh_V_Right"
if mat_bronze:
    v_right.data.materials.append(mat_bronze)
bind_to_bone(v_right, 'thigh.L')


# =========================================================================
# 4. FOREARM HYDRAULIC RAMS (PANEL 04)
# =========================================================================

for side, f_bone, f_x, f_sign in [('L', 'forearm.L', 0.52, 1.0), ('R', 'forearm.R', -0.52, -1.0)]:
    for h_idx, y_off in enumerate([-0.04, 0.04]):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.022,
            depth=0.18,
            location=(f_x + f_sign*0.08, -0.10 + y_off, 1.38),
            rotation=(math.radians(15), 0, 0)
        )
        cyl = bpy.context.active_object
        cyl.name = f"Forearm_Hydraulic_Cylinder_{side}_{h_idx}"
        if mat_cast_iron:
            cyl.data.materials.append(mat_cast_iron)
        bind_to_bone(cyl, f_bone)
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.012,
            depth=0.16,
            location=(f_x + f_sign*0.08, -0.14 + y_off, 1.25),
            rotation=(math.radians(15), 0, 0)
        )
        rod = bpy.context.active_object
        rod.name = f"Forearm_Hydraulic_Rod_{side}_{h_idx}"
        if mat_steel:
            rod.data.materials.append(mat_steel)
        bind_to_bone(rod, f_bone)
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.028,
            depth=0.025,
            location=(f_x + f_sign*0.08, -0.10 + y_off, 1.45),
            rotation=(math.radians(15), 0, 0)
        )
        mount = bpy.context.active_object
        mount.name = f"Forearm_Hydraulic_Mount_{side}_{h_idx}"
        if mat_bronze:
            mount.data.materials.append(mat_bronze)
        bind_to_bone(mount, f_bone)


# =========================================================================
# 5. FAULT MAUL DEMOLITION DRIVER UPGRADES (BOTTOM PANEL)
# =========================================================================

for c_side, z_off in [('Top', 0.12), ('Bottom', -0.12)]:
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(-0.65, -0.78, 0.12 + z_off)
    )
    plate = bpy.context.active_object
    plate.name = f"Maul_Inscribed_CheekPlate_{c_side}"
    plate.scale = (0.29, 0.32, 0.035)
    bpy.ops.object.transform_apply(scale=True)
    if mat_bronze:
        plate.data.materials.append(mat_bronze)
    plate.parent = arm
    plate.parent_type = 'BONE'
    plate.parent_bone = 'tool'

bpy.ops.mesh.primitive_torus_add(
    major_radius=0.045,
    minor_radius=0.014,
    location=(-0.854, -0.0795, 1.48),
    rotation=(0, math.radians(90), 0)
)
pommel_ring = bpy.context.active_object
pommel_ring.name = "Maul_Pommel_Recovery_Ring"
if mat_bronze:
    pommel_ring.data.materials.append(mat_bronze)
pommel_ring.parent = arm
pommel_ring.parent_type = 'BONE'
pommel_ring.parent_bone = 'tool'


# =========================================================================
# 6. ENHANCED PROCEDURAL CHIPPED-EDGE CAST IRON SHADER
# =========================================================================

def upgrade_master_chipped_iron():
    mat = bpy.data.materials.get('Warm charcoal cast iron')
    if not mat:
        return
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    out_node.location = (800, 0)
    
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (500, 0)
    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
    
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-1000, 0)
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-800, 0)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    
    # Noise: Fine cast mill scale
    noise_fine = nodes.new(type='ShaderNodeTexNoise')
    noise_fine.location = (-600, 200)
    noise_fine.inputs['Scale'].default_value = 75.0
    noise_fine.inputs['Detail'].default_value = 5.0
    noise_fine.inputs['Roughness'].default_value = 0.65
    links.new(mapping.outputs['Vector'], noise_fine.inputs['Vector'])
    
    # Noise: Edge Chipping / Abrasion
    noise_chip = nodes.new(type='ShaderNodeTexNoise')
    noise_chip.location = (-600, -150)
    noise_chip.inputs['Scale'].default_value = 24.0
    noise_chip.inputs['Detail'].default_value = 6.0
    noise_chip.inputs['Roughness'].default_value = 0.75
    links.new(mapping.outputs['Vector'], noise_chip.inputs['Vector'])
    
    # Ambient Occlusion for cavity grime and edge detection
    ao = nodes.new(type='ShaderNodeAmbientOcclusion')
    ao.location = (-350, 350)
    ao.inputs['Distance'].default_value = 0.20
    
    # Base cast iron color ramp
    iron_ramp = nodes.new(type='ShaderNodeValToRGB')
    iron_ramp.location = (-350, 150)
    iron_ramp.color_ramp.elements[0].position = 0.25
    iron_ramp.color_ramp.elements[0].color = (0.022, 0.024, 0.026, 1.0) # deep dark iron
    iron_ramp.color_ramp.elements[1].position = 0.75
    iron_ramp.color_ramp.elements[1].color = (0.055, 0.058, 0.062, 1.0) # cast plate surface
    links.new(noise_fine.outputs['Fac'], iron_ramp.inputs['Fac'])
    
    # Edge Chipping Color Ramp (Warm worn bronze/gold undertone + exposed steel highlight)
    chip_ramp = nodes.new(type='ShaderNodeValToRGB')
    chip_ramp.location = (-350, -100)
    chip_ramp.color_ramp.elements[0].position = 0.45
    chip_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    chip_ramp.color_ramp.elements[1].position = 0.75
    chip_ramp.color_ramp.elements[1].color = (0.62, 0.44, 0.18, 1.0) # warm worn bronze edge wear
    links.new(noise_chip.outputs['Fac'], chip_ramp.inputs['Fac'])
    
    # Mix Iron Base + Edge Chipping
    mix_edge = nodes.new(type='ShaderNodeMix')
    mix_edge.data_type = 'RGBA'
    mix_edge.blend_type = 'ADD'
    mix_edge.location = (-50, 100)
    mix_edge.inputs['Factor'].default_value = 0.45
    links.new(iron_ramp.outputs['Color'], mix_edge.inputs['A'])
    links.new(chip_ramp.outputs['Color'], mix_edge.inputs['B'])
    
    # Multiply with AO crevice grime
    mix_ao = nodes.new(type='ShaderNodeMix')
    mix_ao.data_type = 'RGBA'
    mix_ao.blend_type = 'MULTIPLY'
    mix_ao.location = (200, 150)
    mix_ao.inputs['Factor'].default_value = 0.70
    links.new(mix_edge.outputs['Result'], mix_ao.inputs['A'])
    links.new(ao.outputs['Color'], mix_ao.inputs['B'])
    links.new(mix_ao.outputs['Result'], bsdf.inputs['Base Color'])
    
    # Bump Node
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (200, -200)
    bump.inputs['Strength'].default_value = 0.09
    bump.inputs['Distance'].default_value = 0.006
    links.new(noise_fine.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    bsdf.inputs['Metallic'].default_value = 0.90
    bsdf.inputs['Roughness'].default_value = 0.52
    bsdf.inputs['Specular IOR Level'].default_value = 0.60

upgrade_master_chipped_iron()

# Save canonical V20 candidate
bpy.context.scene.render.filepath = '/home/aaron/animation/thulans-production/assets/art/varek_v20_canonical_frame_'
bpy.ops.wm.save_as_mainfile(filepath=save_blend)
print(f"Successfully generated Varek Canonical V20 candidate at {save_blend}")
