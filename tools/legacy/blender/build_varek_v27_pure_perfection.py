import bpy
import math

source_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v24-canonical.blend'
save_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v27-canonical.blend'

bpy.ops.wm.open_mainfile(filepath=source_blend)

# =========================================================================
# 1. CLEAN MASTER CAST IRON PBR SHADER WITH CYCLES BEVEL SPECULAR EDGES
# =========================================================================

mat_iron = bpy.data.materials.get('Warm charcoal cast iron')
if not mat_iron:
    mat_iron = bpy.data.materials.new(name='Warm charcoal cast iron')

mat_iron.use_nodes = True
nodes = mat_iron.node_tree.nodes
links = mat_iron.node_tree.links
nodes.clear()

out_node = nodes.new(type='ShaderNodeOutputMaterial')
out_node.location = (1000, 0)
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.location = (700, 0)
links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])

tex_coord = nodes.new(type='ShaderNodeTexCoord')
tex_coord.location = (-1000, 0)
mapping = nodes.new(type='ShaderNodeMapping')
mapping.location = (-800, 0)
links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

# High frequency micro pitting
noise_fine = nodes.new(type='ShaderNodeTexNoise')
noise_fine.location = (-550, 200)
noise_fine.inputs['Scale'].default_value = 140.0
noise_fine.inputs['Detail'].default_value = 8.0
noise_fine.inputs['Roughness'].default_value = 0.7
links.new(mapping.outputs['Vector'], noise_fine.inputs['Vector'])

# Dark Gunmetal / Ferrous Charcoal Color Ramp
ramp_base = nodes.new(type='ShaderNodeValToRGB')
ramp_base.location = (-250, 200)
ramp_base.color_ramp.elements[0].position = 0.2
ramp_base.color_ramp.elements[0].color = (0.015, 0.016, 0.018, 1.0) # deep dark gunmetal
ramp_base.color_ramp.elements[1].position = 0.8
ramp_base.color_ramp.elements[1].color = (0.032, 0.034, 0.038, 1.0) # subtle micro-grain
links.new(noise_fine.outputs['Fac'], ramp_base.inputs['Fac'])
links.new(ramp_base.outputs['Color'], bsdf.inputs['Base Color'])

# Bevel Node for rounded edge reflections
bevel = nodes.new(type='ShaderNodeBevel')
bevel.location = (-250, -300)
bevel.inputs['Radius'].default_value = 0.008
bevel.samples = 12

# Bump node combining micro-tooth noise and bevel normal
bump = nodes.new(type='ShaderNodeBump')
bump.location = (200, -200)
bump.inputs['Strength'].default_value = 0.04
bump.inputs['Distance'].default_value = 0.002
links.new(noise_fine.outputs['Fac'], bump.inputs['Height'])
links.new(bevel.outputs['Normal'], bump.inputs['Normal'])
links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

# Roughness
rough_ramp = nodes.new(type='ShaderNodeValToRGB')
rough_ramp.location = (-250, -50)
rough_ramp.color_ramp.elements[0].position = 0.2
rough_ramp.color_ramp.elements[0].color = (0.45, 0.45, 0.45, 1.0)
rough_ramp.color_ramp.elements[1].position = 0.8
rough_ramp.color_ramp.elements[1].color = (0.65, 0.65, 0.65, 1.0)
links.new(noise_fine.outputs['Fac'], rough_ramp.inputs['Fac'])
links.new(rough_ramp.outputs['Color'], bsdf.inputs['Roughness'])

bsdf.inputs['Metallic'].default_value = 0.96
bsdf.inputs['Specular IOR Level'].default_value = 0.55


# =========================================================================
# 2. AGED PHOSPHOR BRONZE / BRASS (ACCENTS, FASTENERS, AXLES)
# =========================================================================

mat_brass = bpy.data.materials.get('Aged brass')
if mat_brass:
    mat_brass.use_nodes = True
    b_nodes = mat_brass.node_tree.nodes
    b_links = mat_brass.node_tree.links
    b_nodes.clear()

    b_out = b_nodes.new(type='ShaderNodeOutputMaterial')
    b_out.location = (600, 0)
    b_bsdf = b_nodes.new(type='ShaderNodeBsdfPrincipled')
    b_bsdf.location = (300, 0)
    b_links.new(b_bsdf.outputs['BSDF'], b_out.inputs['Surface'])

    b_bsdf.inputs['Base Color'].default_value = (0.52, 0.35, 0.14, 1.0) # rich Thulan bronze
    b_bsdf.inputs['Metallic'].default_value = 0.95
    b_bsdf.inputs['Roughness'].default_value = 0.38


# =========================================================================
# 3. GREN-SKILDUS CLOTH SHADER (MUTED WEATHERED MILITARY OLIVE CANVAS)
# =========================================================================

mat_cloth = bpy.data.materials.get('Cinderback jade paint')
if mat_cloth:
    mat_cloth.use_nodes = True
    c_nodes = mat_cloth.node_tree.nodes
    c_links = mat_cloth.node_tree.links
    c_nodes.clear()

    c_out = c_nodes.new(type='ShaderNodeOutputMaterial')
    c_out.location = (1000, 0)
    c_bsdf = c_nodes.new(type='ShaderNodeBsdfPrincipled')
    c_bsdf.location = (700, 0)
    c_links.new(c_bsdf.outputs['BSDF'], c_out.inputs['Surface'])

    c_tex = c_nodes.new(type='ShaderNodeTexCoord')
    c_tex.location = (-900, 0)
    c_noise = c_nodes.new(type='ShaderNodeTexNoise')
    c_noise.location = (-600, 0)
    c_noise.inputs['Scale'].default_value = 220.0
    c_noise.inputs['Detail'].default_value = 8.0
    c_noise.inputs['Roughness'].default_value = 0.8
    c_links.new(c_tex.outputs['Object'], c_noise.inputs['Vector'])

    c_bump = c_nodes.new(type='ShaderNodeBump')
    c_bump.location = (-200, -200)
    c_bump.inputs['Strength'].default_value = 0.08
    c_bump.inputs['Distance'].default_value = 0.003
    c_links.new(c_noise.outputs['Fac'], c_bump.inputs['Height'])
    c_links.new(c_bump.outputs['Normal'], c_bsdf.inputs['Normal'])

    # Deep weathered olive green (matches Panel 02)
    c_ramp = c_nodes.new(type='ShaderNodeValToRGB')
    c_ramp.location = (-200, 150)
    c_ramp.color_ramp.elements[0].position = 0.2
    c_ramp.color_ramp.elements[0].color = (0.018, 0.042, 0.026, 1.0)
    c_ramp.color_ramp.elements[1].position = 0.8
    c_ramp.color_ramp.elements[1].color = (0.032, 0.065, 0.042, 1.0)
    c_links.new(c_noise.outputs['Fac'], c_ramp.inputs['Fac'])
    c_links.new(c_ramp.outputs['Color'], c_bsdf.inputs['Base Color'])

    c_bsdf.inputs['Metallic'].default_value = 0.0
    c_bsdf.inputs['Roughness'].default_value = 0.96
    c_bsdf.inputs['Sheen Weight'].default_value = 0.6


# =========================================================================
# 4. THULAN CROSS INSIGNIA (AGED WEATHERED BONE CHALK)
# =========================================================================

mat_insignia = bpy.data.materials.get('M_Thulan_Insignia_BoneWhite')
if mat_insignia:
    mat_insignia.use_nodes = True
    i_nodes = mat_insignia.node_tree.nodes
    i_links = mat_insignia.node_tree.links
    i_nodes.clear()

    i_out = i_nodes.new(type='ShaderNodeOutputMaterial')
    i_out.location = (600, 0)
    i_bsdf = i_nodes.new(type='ShaderNodeBsdfPrincipled')
    i_bsdf.location = (300, 0)
    i_links.new(i_bsdf.outputs['BSDF'], i_out.inputs['Surface'])

    i_bsdf.inputs['Base Color'].default_value = (0.62, 0.60, 0.52, 1.0) # monastic chalk/bone
    i_bsdf.inputs['Roughness'].default_value = 0.94
    i_bsdf.inputs['Metallic'].default_value = 0.0


# =========================================================================
# 5. PELVIS, MAUL, AND LIMBS ARMOR MATERIAL FIXES
# =========================================================================

pelvis = bpy.data.objects.get('Pelvis')
if pelvis and mat_iron:
    pelvis.data.materials.clear()
    pelvis.data.materials.append(mat_iron)

# Ensure cloth object uses mat_cloth
cloth_obj = bpy.data.objects.get('Gren Skildus')
if cloth_obj and mat_cloth:
    cloth_obj.data.materials.clear()
    cloth_obj.data.materials.append(mat_cloth)


# =========================================================================
# 6. CINEMATIC GRIMDARK LIGHTING
# =========================================================================

rim = bpy.data.objects.get('Rim')
if rim:
    rim.data.energy = 4500.0
    rim.data.color = (1.0, 0.70, 0.35) # warm forge rim light
    rim.location = (3.2, 4.5, 3.6)
    rim.data.size = 2.5

key = bpy.data.objects.get('Key')
if key:
    key.data.energy = 1600.0
    key.data.color = (0.92, 0.95, 1.0)
    key.location = (-3.8, -4.5, 3.8)

fill = bpy.data.objects.get('Fill')
if fill:
    fill.data.energy = 500.0
    fill.data.color = (0.75, 0.82, 0.95)

bpy.ops.wm.save_as_mainfile(filepath=save_blend)
print(f"Successfully generated V27 at {save_blend}")
