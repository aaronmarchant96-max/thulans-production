import bpy
import math
from mathutils import Euler, Quaternion, Vector

source_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v24-canonical.blend'
save_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v25-canonical.blend'

bpy.ops.wm.open_mainfile(filepath=source_blend)

# =========================================================================
# 1. MASTER PROCEDURAL GRIMDARK CHIPPED-EDGE CAST IRON SHADER
# =========================================================================

mat_iron = bpy.data.materials.get('Warm charcoal cast iron')
if not mat_iron:
    mat_iron = bpy.data.materials.new(name='Warm charcoal cast iron')

mat_iron.use_nodes = True
nodes = mat_iron.node_tree.nodes
links = mat_iron.node_tree.links
nodes.clear()

out_node = nodes.new(type='ShaderNodeOutputMaterial')
out_node.location = (1400, 0)
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.location = (1100, 0)
links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])

tex_coord = nodes.new(type='ShaderNodeTexCoord')
tex_coord.location = (-1400, 0)
mapping = nodes.new(type='ShaderNodeMapping')
mapping.location = (-1200, 0)
links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

# Fine cast tooth noise
noise_fine = nodes.new(type='ShaderNodeTexNoise')
noise_fine.location = (-950, 300)
noise_fine.inputs['Scale'].default_value = 160.0
noise_fine.inputs['Detail'].default_value = 8.0
noise_fine.inputs['Roughness'].default_value = 0.7
links.new(mapping.outputs['Vector'], noise_fine.inputs['Vector'])

# Scrape / Texture Noise
noise_scrape = nodes.new(type='ShaderNodeTexNoise')
noise_scrape.location = (-950, -50)
noise_scrape.inputs['Scale'].default_value = 45.0
noise_scrape.inputs['Detail'].default_value = 6.0
noise_scrape.inputs['Roughness'].default_value = 0.8
links.new(mapping.outputs['Vector'], noise_scrape.inputs['Vector'])

# Geometry Normal & Bevel Node for Edge-Wear
geom = nodes.new(type='ShaderNodeNewGeometry')
geom.location = (-950, -350)

bevel = nodes.new(type='ShaderNodeBevel')
bevel.location = (-950, -550)
bevel.inputs['Radius'].default_value = 0.024
bevel.samples = 8

# Dot Product between Normal and Bevel Normal (Detects Curvature / Chamfers)
dot_prod = nodes.new(type='ShaderNodeVectorMath')
dot_prod.operation = 'DOT_PRODUCT'
dot_prod.location = (-700, -450)
links.new(geom.outputs['Normal'], dot_prod.inputs[0])
links.new(bevel.outputs['Normal'], dot_prod.inputs[1])

# Invert Dot Product (1.0 - Dot) -> 0.0 on flat faces, >0.0 on curved/beveled edges
inv_dot = nodes.new(type='ShaderNodeMath')
inv_dot.operation = 'SUBTRACT'
inv_dot.location = (-500, -450)
inv_dot.inputs[0].default_value = 1.0
links.new(dot_prod.outputs['Value'], inv_dot.inputs[1])

# High-Contrast Color Ramp for Edge Chipping Mask
ramp_edge = nodes.new(type='ShaderNodeValToRGB')
ramp_edge.location = (-280, -450)
ramp_edge.color_ramp.elements[0].position = 0.008
ramp_edge.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
ramp_edge.color_ramp.elements[1].position = 0.045
ramp_edge.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
links.new(inv_dot.outputs['Value'], ramp_edge.inputs['Fac'])

# Base Dark Ferrous Cast Iron Color Ramp (Pure Grimdark Charcoal)
ramp_base = nodes.new(type='ShaderNodeValToRGB')
ramp_base.location = (-450, 200)
ramp_base.color_ramp.elements[0].position = 0.2
ramp_base.color_ramp.elements[0].color = (0.014, 0.014, 0.016, 1.0) # very dark anthracite
ramp_base.color_ramp.elements[1].position = 0.8
ramp_base.color_ramp.elements[1].color = (0.026, 0.027, 0.030, 1.0) # subtle micro-tooth
links.new(noise_fine.outputs['Fac'], ramp_base.inputs['Fac'])

# Edge Color (Rich Warm Bronze / Raw Worn Steel)
mix_edge_color = nodes.new(type='ShaderNodeMix')
mix_edge_color.data_type = 'RGBA'
mix_edge_color.location = (150, 100)
links.new(ramp_edge.outputs['Color'], mix_edge_color.inputs['Factor'])
links.new(ramp_base.outputs['Color'], mix_edge_color.inputs['A'])
mix_edge_color.inputs['B'].default_value = (0.62, 0.44, 0.18, 1.0) # warm chipped bronze/gold edge
links.new(mix_edge_color.outputs['Result'], bsdf.inputs['Base Color'])

# Roughness: Base is matte (0.64), edge is worn semi-gloss (0.32)
mix_rough = nodes.new(type='ShaderNodeMix')
mix_rough.data_type = 'FLOAT'
mix_rough.location = (450, -150)
links.new(ramp_edge.outputs['Color'], mix_rough.inputs['Factor'])
mix_rough.inputs['A'].default_value = 0.65
mix_rough.inputs['B'].default_value = 0.32
links.new(mix_rough.outputs['Result'], bsdf.inputs['Roughness'])

# Bump
bump = nodes.new(type='ShaderNodeBump')
bump.location = (750, -350)
bump.inputs['Strength'].default_value = 0.035
bump.inputs['Distance'].default_value = 0.002
links.new(noise_fine.outputs['Fac'], bump.inputs['Height'])
links.new(bevel.outputs['Normal'], bump.inputs['Normal'])
links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

bsdf.inputs['Metallic'].default_value = 0.95
bsdf.inputs['Specular IOR Level'].default_value = 0.55


# =========================================================================
# 2. CALIBRATED AGED PHOSPHOR BRONZE / BRASS SHADER
# =========================================================================

mat_brass = bpy.data.materials.get('Aged brass')
if mat_brass and mat_brass.node_tree:
    b_nodes = mat_brass.node_tree.nodes
    b_links = mat_brass.node_tree.links
    b_bsdf = None
    for n in b_nodes:
        if n.type == 'BSDF_PRINCIPLED':
            b_bsdf = n
            break
    if b_bsdf:
        b_bsdf.inputs['Base Color'].default_value = (0.44, 0.28, 0.11, 1.0) # rich aged bronze
        b_bsdf.inputs['Metallic'].default_value = 0.94
        b_bsdf.inputs['Roughness'].default_value = 0.42


# =========================================================================
# 3. GREN-SKILDUS CLOTH SHADER (MUTED OLIVE CANVAS WITH ROUGH FIBERS)
# =========================================================================

mat_cloth = bpy.data.materials.get('Cinderback jade paint')
if mat_cloth:
    c_nodes = mat_cloth.node_tree.nodes
    c_links = mat_cloth.node_tree.links
    c_nodes.clear()

    c_out = c_nodes.new(type='ShaderNodeOutputMaterial')
    c_out.location = (1000, 0)
    c_bsdf = c_nodes.new(type='ShaderNodeBsdfPrincipled')
    c_bsdf.location = (700, 0)
    c_links.new(c_bsdf.outputs['BSDF'], c_out.inputs['Surface'])

    c_tex = c_nodes.new(type='ShaderNodeTexCoord')
    c_tex.location = (-800, 0)
    c_noise = c_nodes.new(type='ShaderNodeTexNoise')
    c_noise.location = (-500, 0)
    c_noise.inputs['Scale'].default_value = 250.0
    c_noise.inputs['Detail'].default_value = 8.0
    c_noise.inputs['Roughness'].default_value = 0.85
    c_links.new(c_tex.outputs['Object'], c_noise.inputs['Vector'])

    c_bump = c_nodes.new(type='ShaderNodeBump')
    c_bump.location = (-200, -150)
    c_bump.inputs['Strength'].default_value = 0.08
    c_bump.inputs['Distance'].default_value = 0.003
    c_links.new(c_noise.outputs['Fac'], c_bump.inputs['Height'])
    c_links.new(c_bump.outputs['Normal'], c_bsdf.inputs['Normal'])

    # Rich dark muted military/monastic olive drab canvas
    c_ramp = c_nodes.new(type='ShaderNodeValToRGB')
    c_ramp.location = (-200, 150)
    c_ramp.color_ramp.elements[0].position = 0.3
    c_ramp.color_ramp.elements[0].color = (0.024, 0.052, 0.032, 1.0) # deep olive green
    c_ramp.color_ramp.elements[1].position = 0.7
    c_ramp.color_ramp.elements[1].color = (0.038, 0.075, 0.048, 1.0)
    c_links.new(c_noise.outputs['Fac'], c_ramp.inputs['Fac'])
    c_links.new(c_ramp.outputs['Color'], c_bsdf.inputs['Base Color'])

    c_bsdf.inputs['Metallic'].default_value = 0.0
    c_bsdf.inputs['Roughness'].default_value = 0.95
    c_bsdf.inputs['Sheen Weight'].default_value = 0.5


# =========================================================================
# 4. MAUL STRIKING SHOES & FASTENERS (DARK FORGED STEEL)
# =========================================================================

mat_steel = bpy.data.materials.get('Working piston steel')
if mat_steel and mat_steel.node_tree:
    s_bsdf = None
    for n in mat_steel.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            s_bsdf = n
            break
    if s_bsdf:
        s_bsdf.inputs['Base Color'].default_value = (0.08, 0.085, 0.09, 1.0) # dark forged piston steel
        s_bsdf.inputs['Metallic'].default_value = 0.95
        s_bsdf.inputs['Roughness'].default_value = 0.35


# =========================================================================
# 5. CINEMATIC GRIMDARK LIGHTING CALIBRATION
# =========================================================================

key = bpy.data.objects.get('Key')
if key:
    key.data.energy = 1200.0
    key.data.color = (0.95, 0.96, 1.0) # neutral key
    key.location = (-3.5, -4.5, 4.0)

rim = bpy.data.objects.get('Rim')
if rim:
    rim.data.energy = 3800.0 # powerful warm rim rake to carve the dark iron silhouette
    rim.data.color = (1.0, 0.72, 0.38) # warm forge back-rim
    rim.location = (3.2, 4.8, 3.8)

fill = bpy.data.objects.get('Fill')
if fill:
    fill.data.energy = 500.0
    fill.data.color = (0.8, 0.85, 0.9)


# =========================================================================
# SAVE V25 MASTER
# =========================================================================

bpy.ops.wm.save_as_mainfile(filepath=save_blend)
print(f"Successfully generated Varek Master Feel at {save_blend}")
