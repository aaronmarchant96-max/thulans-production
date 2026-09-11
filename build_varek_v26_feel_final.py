import bpy
import math
from mathutils import Euler, Quaternion, Vector

source_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v25-canonical.blend'
save_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v26-canonical.blend'

bpy.ops.wm.open_mainfile(filepath=source_blend)

# =========================================================================
# 1. SHADER OVERHAUL: ORGANIC CHIPPED-EDGE CAST IRON
# =========================================================================

mat_iron = bpy.data.materials.get('Warm charcoal cast iron')
if mat_iron and mat_iron.node_tree:
    nodes = mat_iron.node_tree.nodes
    links = mat_iron.node_tree.links
    nodes.clear()

    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    out_node.location = (1600, 0)
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (1300, 0)
    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])

    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-1600, 0)
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-1400, 0)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

    # Micro-pitting noise
    noise_fine = nodes.new(type='ShaderNodeTexNoise')
    noise_fine.location = (-1100, 400)
    noise_fine.inputs['Scale'].default_value = 180.0
    noise_fine.inputs['Detail'].default_value = 8.0
    noise_fine.inputs['Roughness'].default_value = 0.7
    links.new(mapping.outputs['Vector'], noise_fine.inputs['Vector'])

    # Irregular Chipping & Scratch Noise
    noise_scratch = nodes.new(type='ShaderNodeTexNoise')
    noise_scratch.location = (-1100, -100)
    noise_scratch.inputs['Scale'].default_value = 55.0
    noise_scratch.inputs['Detail'].default_value = 10.0
    noise_scratch.inputs['Roughness'].default_value = 0.85
    links.new(mapping.outputs['Vector'], noise_scratch.inputs['Vector'])

    # Musgrave / Perlin Macro Mottling
    noise_macro = nodes.new(type='ShaderNodeTexNoise')
    noise_macro.location = (-1100, -400)
    noise_macro.inputs['Scale'].default_value = 12.0
    noise_macro.inputs['Detail'].default_value = 6.0
    noise_macro.inputs['Roughness'].default_value = 0.5
    links.new(mapping.outputs['Vector'], noise_macro.inputs['Vector'])

    # Curvature / Bevel Dot Product Mask
    geom = nodes.new(type='ShaderNodeNewGeometry')
    geom.location = (-1100, -700)

    bevel = nodes.new(type='ShaderNodeBevel')
    bevel.location = (-1100, -900)
    bevel.inputs['Radius'].default_value = 0.022
    bevel.samples = 8

    dot_prod = nodes.new(type='ShaderNodeVectorMath')
    dot_prod.operation = 'DOT_PRODUCT'
    dot_prod.location = (-850, -800)
    links.new(geom.outputs['Normal'], dot_prod.inputs[0])
    links.new(bevel.outputs['Normal'], dot_prod.inputs[1])

    inv_dot = nodes.new(type='ShaderNodeMath')
    inv_dot.operation = 'SUBTRACT'
    inv_dot.location = (-650, -800)
    inv_dot.inputs[0].default_value = 1.0
    links.new(dot_prod.outputs['Value'], inv_dot.inputs[1])

    # Edge Curvature Ramp
    ramp_edge_raw = nodes.new(type='ShaderNodeValToRGB')
    ramp_edge_raw.location = (-450, -800)
    ramp_edge_raw.color_ramp.elements[0].position = 0.005
    ramp_edge_raw.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp_edge_raw.color_ramp.elements[1].position = 0.035
    ramp_edge_raw.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    links.new(inv_dot.outputs['Value'], ramp_edge_raw.inputs['Fac'])

    # Break up edge wear with scratch noise (so it's chipped, not a solid line)
    mix_chipped = nodes.new(type='ShaderNodeMix')
    mix_chipped.data_type = 'FLOAT'
    mix_chipped.blend_type = 'MULTIPLY'
    mix_chipped.location = (-200, -700)
    mix_chipped.inputs['Factor'].default_value = 0.85
    links.new(ramp_edge_raw.outputs['Color'], mix_chipped.inputs['A'])
    links.new(noise_scratch.outputs['Fac'], mix_chipped.inputs['B'])

    # Base Dark Iron Charcoal Ramp
    ramp_base = nodes.new(type='ShaderNodeValToRGB')
    ramp_base.location = (-450, 300)
    ramp_base.color_ramp.elements[0].position = 0.15
    ramp_base.color_ramp.elements[0].color = (0.012, 0.013, 0.015, 1.0) # deepest anthracite
    ramp_base.color_ramp.elements[1].position = 0.85
    ramp_base.color_ramp.elements[1].color = (0.024, 0.025, 0.028, 1.0) # cold cast grain
    links.new(noise_fine.outputs['Fac'], ramp_base.inputs['Fac'])

    # Edge Color Mix (Base Charcoal -> Exposed Weathered Bronze / Bare Steel)
    mix_color = nodes.new(type='ShaderNodeMix')
    mix_color.data_type = 'RGBA'
    mix_color.location = (200, 100)
    links.new(mix_chipped.outputs['Result'], mix_color.inputs['Factor'])
    links.new(ramp_base.outputs['Color'], mix_color.inputs['A'])
    mix_color.inputs['B'].default_value = (0.58, 0.42, 0.18, 1.0) # chipped bronze/steel
    links.new(mix_color.outputs['Result'], bsdf.inputs['Base Color'])

    # Roughness Mix
    mix_rough = nodes.new(type='ShaderNodeMix')
    mix_rough.data_type = 'FLOAT'
    mix_rough.location = (500, -200)
    links.new(mix_chipped.outputs['Result'], mix_rough.inputs['Factor'])
    mix_rough.inputs['A'].default_value = 0.68 # rough cast iron
    mix_rough.inputs['B'].default_value = 0.30 # polished/scraped edge
    links.new(mix_rough.outputs['Result'], bsdf.inputs['Roughness'])

    # Normal Bump Map
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (850, -450)
    bump.inputs['Strength'].default_value = 0.035
    bump.inputs['Distance'].default_value = 0.002
    links.new(noise_fine.outputs['Fac'], bump.inputs['Height'])
    links.new(bevel.outputs['Normal'], bump.inputs['Normal'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Specular IOR Level'].default_value = 0.52


# =========================================================================
# 2. PELVIS & BODY ARMOR MATERIAL ASSIGNMENTS
# =========================================================================

# Ensure pelvis main casting uses cast iron (not all bronze)
pelvis = bpy.data.objects.get('Pelvis')
if pelvis and mat_iron:
    pelvis.data.materials.clear()
    pelvis.data.materials.append(mat_iron)

# Ensure feet, cleats, and shins use cast iron
for obj in bpy.data.objects:
    if any(k in obj.name for k in ['Foot', 'Cleat', 'Tread', 'Knuckle', 'RollCage', 'Anvil', 'Brow', 'Spine']):
        if obj.data and hasattr(obj.data, 'materials') and mat_iron:
            obj.data.materials.clear()
            obj.data.materials.append(mat_iron)


# =========================================================================
# 3. GREN-SKILDUS CLOTH OVERHAUL (DARK HEAVY MONASTIC CANVAS)
# =========================================================================

mat_cloth = bpy.data.materials.get('Cinderback jade paint')
if mat_cloth and mat_cloth.node_tree:
    c_nodes = mat_cloth.node_tree.nodes
    c_links = mat_cloth.node_tree.links
    c_nodes.clear()

    c_out = c_nodes.new(type='ShaderNodeOutputMaterial')
    c_out.location = (1200, 0)
    c_bsdf = c_nodes.new(type='ShaderNodeBsdfPrincipled')
    c_bsdf.location = (900, 0)
    c_links.new(c_bsdf.outputs['BSDF'], c_out.inputs['Surface'])

    c_tex = c_nodes.new(type='ShaderNodeTexCoord')
    c_tex.location = (-1000, 0)
    
    # Heavy woven canvas thread pattern
    c_wave = c_nodes.new(type='ShaderNodeTexWave')
    c_wave.location = (-700, 200)
    c_wave.inputs['Scale'].default_value = 180.0
    c_wave.inputs['Distortion'].default_value = 3.5
    c_wave.inputs['Detail'].default_value = 4.0
    c_links.new(c_tex.outputs['Object'], c_wave.inputs['Vector'])

    c_noise = c_nodes.new(type='ShaderNodeTexNoise')
    c_noise.location = (-700, -150)
    c_noise.inputs['Scale'].default_value = 220.0
    c_noise.inputs['Detail'].default_value = 6.0
    c_links.new(c_tex.outputs['Object'], c_noise.inputs['Vector'])

    # Mix wave + noise for fabric roughness
    c_mix_bump = nodes.new(type='ShaderNodeMix')
    c_mix_bump.data_type = 'FLOAT'
    c_mix_bump.location = (-400, 0)
    c_mix_bump.inputs['Factor'].default_value = 0.5
    c_links.new(c_wave.outputs['Color'], c_mix_bump.inputs['A'])
    c_links.new(c_noise.outputs['Fac'], c_mix_bump.inputs['B'])

    c_bump = c_nodes.new(type='ShaderNodeBump')
    c_bump.location = (-150, -200)
    c_bump.inputs['Strength'].default_value = 0.09
    c_bump.inputs['Distance'].default_value = 0.004
    c_links.new(c_mix_bump.outputs['Result'], c_bump.inputs['Height'])
    c_links.new(c_bump.outputs['Normal'], c_bsdf.inputs['Normal'])

    # Dark muted military monastic green (matching reference Panel 02)
    c_ramp = c_nodes.new(type='ShaderNodeValToRGB')
    c_ramp.location = (-150, 150)
    c_ramp.color_ramp.elements[0].position = 0.2
    c_ramp.color_ramp.elements[0].color = (0.016, 0.038, 0.024, 1.0) # deep dark muted olive
    c_ramp.color_ramp.elements[1].position = 0.8
    c_ramp.color_ramp.elements[1].color = (0.028, 0.055, 0.036, 1.0)
    c_links.new(c_noise.outputs['Fac'], c_ramp.inputs['Fac'])
    c_links.new(c_ramp.outputs['Color'], c_bsdf.inputs['Base Color'])

    c_bsdf.inputs['Metallic'].default_value = 0.0
    c_bsdf.inputs['Roughness'].default_value = 0.98
    c_bsdf.inputs['Sheen Weight'].default_value = 0.65


# =========================================================================
# 4. THULAN CROSS EMBLEM TEXTURING (ERODED STAMPED BONE WHITE)
# =========================================================================

mat_insignia = bpy.data.materials.get('M_Thulan_Insignia_BoneWhite')
if mat_insignia and mat_insignia.node_tree:
    i_nodes = mat_insignia.node_tree.nodes
    i_links = mat_insignia.node_tree.links
    i_nodes.clear()

    i_out = i_nodes.new(type='ShaderNodeOutputMaterial')
    i_out.location = (800, 0)
    i_bsdf = i_nodes.new(type='ShaderNodeBsdfPrincipled')
    i_bsdf.location = (500, 0)
    i_links.new(i_bsdf.outputs['BSDF'], i_out.inputs['Surface'])

    i_bsdf.inputs['Base Color'].default_value = (0.68, 0.66, 0.58, 1.0) # aged weathered bone/chalk
    i_bsdf.inputs['Roughness'].default_value = 0.92
    i_bsdf.inputs['Metallic'].default_value = 0.0


# =========================================================================
# 5. ENVIRONMENT & VOLUMETRIC FORGE LIGHTING
# =========================================================================

# Forge rim raking light
rim = bpy.data.objects.get('Rim')
if rim:
    rim.data.energy = 4200.0
    rim.data.color = (1.0, 0.68, 0.32) # warm industrial orange/gold
    rim.location = (3.5, 4.2, 3.5)
    rim.data.size = 2.8

# Key light
key = bpy.data.objects.get('Key')
if key:
    key.data.energy = 1500.0
    key.data.color = (0.92, 0.95, 1.0)
    key.location = (-3.8, -4.8, 3.8)

# Fill light
fill = bpy.data.objects.get('Fill')
if fill:
    fill.data.energy = 450.0
    fill.data.color = (0.75, 0.80, 0.90)

bpy.ops.wm.save_as_mainfile(filepath=save_blend)
print(f"Successfully generated V26 at {save_blend}")
