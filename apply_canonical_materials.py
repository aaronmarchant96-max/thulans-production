import bpy
import math

source_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v21-canonical.blend'
save_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v22-materials.blend'

bpy.ops.wm.open_mainfile(filepath=source_blend)

# =========================================================================
# 1. MASTER PROCEDURAL WEATHERED CAST IRON WITH CHIPPED BRONZE/STEEL EDGES
# =========================================================================

mat_iron = bpy.data.materials.get('Warm charcoal cast iron')
if not mat_iron:
    mat_iron = bpy.data.materials.new(name='Warm charcoal cast iron')

mat_iron.use_nodes = True
nodes = mat_iron.node_tree.nodes
links = mat_iron.node_tree.links
nodes.clear()

out_node = nodes.new(type='ShaderNodeOutputMaterial')
out_node.location = (1100, 0)

bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.location = (800, 0)
links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])

# Coordinates & Mapping
tex_coord = nodes.new(type='ShaderNodeTexCoord')
tex_coord.location = (-1200, 0)
mapping = nodes.new(type='ShaderNodeMapping')
mapping.location = (-1000, 0)
links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

# Noise 1: Fine Cast Mill Scale Texture
noise_fine = nodes.new(type='ShaderNodeTexNoise')
noise_fine.location = (-750, 300)
noise_fine.inputs['Scale'].default_value = 110.0
noise_fine.inputs['Detail'].default_value = 6.0
noise_fine.inputs['Roughness'].default_value = 0.65
links.new(mapping.outputs['Vector'], noise_fine.inputs['Vector'])

# Noise 2: Organic Edge Wear & Scratches
noise_scratch = nodes.new(type='ShaderNodeTexNoise')
noise_scratch.location = (-750, -50)
noise_scratch.inputs['Scale'].default_value = 18.0
noise_scratch.inputs['Detail'].default_value = 8.0
noise_scratch.inputs['Roughness'].default_value = 0.8
links.new(mapping.outputs['Vector'], noise_scratch.inputs['Vector'])

# Noise 3: Large Color Variation / Oxidation Patina
noise_macro = nodes.new(type='ShaderNodeTexNoise')
noise_macro.location = (-750, -350)
noise_macro.inputs['Scale'].default_value = 4.0
noise_macro.inputs['Detail'].default_value = 3.0
links.new(mapping.outputs['Vector'], noise_macro.inputs['Vector'])

# Ambient Occlusion for Cavity Grime / Grease
ao = nodes.new(type='ShaderNodeAmbientOcclusion')
ao.location = (-450, 450)
ao.inputs['Distance'].default_value = 0.18

# Bevel Node for Convex Edge Detection (Chipped Edges)
bevel = nodes.new(type='ShaderNodeBevel')
bevel.location = (-450, -200)
bevel.inputs['Radius'].default_value = 0.018
bevel.samples = 8

# Base Iron Color Ramp (Dark gunmetal / cold cast steel)
ramp_base = nodes.new(type='ShaderNodeValToRGB')
ramp_base.location = (-450, 200)
ramp_base.color_ramp.elements[0].position = 0.2
ramp_base.color_ramp.elements[0].color = (0.022, 0.024, 0.026, 1.0) # deep dark iron
ramp_base.color_ramp.elements[1].position = 0.8
ramp_base.color_ramp.elements[1].color = (0.045, 0.048, 0.052, 1.0) # weathered cast plate
links.new(noise_fine.outputs['Fac'], ramp_base.inputs['Fac'])

# Edge Wear / Chipped Color Ramp (Revealing warm bronze undertone & bare bright steel)
ramp_edge = nodes.new(type='ShaderNodeValToRGB')
ramp_edge.location = (-450, 0)
ramp_edge.color_ramp.elements[0].position = 0.40
ramp_edge.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0) # unchipped
el_mid = ramp_edge.color_ramp.elements.new(0.68)
el_mid.color = (0.55, 0.38, 0.16, 1.0) # warm oxidized bronze chip
ramp_edge.color_ramp.elements[-1].position = 0.88
ramp_edge.color_ramp.elements[-1].color = (0.75, 0.65, 0.42, 1.0) # bright gold/steel edge highlight
links.new(noise_scratch.outputs['Fac'], ramp_edge.inputs['Fac'])

# Mix: Base Iron + Chipped Edge Wear
mix_edge = nodes.new(type='ShaderNodeMix')
mix_edge.data_type = 'RGBA'
mix_edge.blend_type = 'ADD'
mix_edge.location = (-150, 100)
mix_edge.inputs['Factor'].default_value = 0.60
links.new(ramp_base.outputs['Color'], mix_edge.inputs['A'])
links.new(ramp_edge.outputs['Color'], mix_edge.inputs['B'])

# Multiply with AO for crevice darkening
mix_final_color = nodes.new(type='ShaderNodeMix')
mix_final_color.data_type = 'RGBA'
mix_final_color.blend_type = 'MULTIPLY'
mix_final_color.location = (150, 200)
mix_final_color.inputs['Factor'].default_value = 0.82
links.new(mix_edge.outputs['Result'], mix_final_color.inputs['A'])
links.new(ao.outputs['Color'], mix_final_color.inputs['B'])
links.new(mix_final_color.outputs['Result'], bsdf.inputs['Base Color'])

# Roughness Map Range (Varying between polished wear and matte cast)
rough_map = nodes.new(type='ShaderNodeMapRange')
rough_map.location = (150, -50)
rough_map.inputs['From Min'].default_value = 0.1
rough_map.inputs['From Max'].default_value = 0.9
rough_map.inputs['To Min'].default_value = 0.38
rough_map.inputs['To Max'].default_value = 0.68
links.new(noise_fine.outputs['Fac'], rough_map.inputs['Value'])
links.new(rough_map.outputs['Result'], bsdf.inputs['Roughness'])

# Bump Node (Micro-pit tooth + edge scratches)
bump = nodes.new(type='ShaderNodeBump')
bump.location = (450, -200)
bump.inputs['Strength'].default_value = 0.055
bump.inputs['Distance'].default_value = 0.004
links.new(noise_fine.outputs['Fac'], bump.inputs['Height'])
links.new(bevel.outputs['Normal'], bump.inputs['Normal'])
links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

bsdf.inputs['Metallic'].default_value = 0.92
bsdf.inputs['Specular IOR Level'].default_value = 0.58


# =========================================================================
# 2. MASTER AGED PHOSPHOR BRONZE SHADER (JOINTS, TRUNNIONS, BUSHINGS)
# =========================================================================

mat_bronze = bpy.data.materials.get('Aged brass')
if not mat_bronze:
    mat_bronze = bpy.data.materials.new(name='Aged brass')

mat_bronze.use_nodes = True
b_nodes = mat_bronze.node_tree.nodes
b_links = mat_bronze.node_tree.links
b_nodes.clear()

b_out = b_nodes.new(type='ShaderNodeOutputMaterial')
b_out.location = (1000, 0)
b_bsdf = b_nodes.new(type='ShaderNodeBsdfPrincipled')
b_bsdf.location = (700, 0)
b_links.new(b_bsdf.outputs['BSDF'], b_out.inputs['Surface'])

b_coord = b_nodes.new(type='ShaderNodeTexCoord')
b_coord.location = (-1000, 0)
b_map = b_nodes.new(type='ShaderNodeMapping')
b_map.location = (-800, 0)
b_links.new(b_coord.outputs['Object'], b_map.inputs['Vector'])

b_noise = b_nodes.new(type='ShaderNodeTexNoise')
b_noise.location = (-550, 150)
b_noise.inputs['Scale'].default_value = 45.0
b_noise.inputs['Detail'].default_value = 5.0
b_links.new(b_map.outputs['Vector'], b_noise.inputs['Vector'])

b_ao = b_nodes.new(type='ShaderNodeAmbientOcclusion')
b_ao.location = (-550, 400)
b_ao.inputs['Distance'].default_value = 0.12

# Warm machined phosphor bronze gradient
b_ramp = b_nodes.new(type='ShaderNodeValToRGB')
b_ramp.location = (-250, 150)
b_ramp.color_ramp.elements[0].position = 0.15
b_ramp.color_ramp.elements[0].color = (0.28, 0.16, 0.05, 1.0) # deep oily brown patina
b_ramp.color_ramp.elements[1].position = 0.75
b_ramp.color_ramp.elements[1].color = (0.62, 0.42, 0.18, 1.0) # rich warm machined bronze
b_links.new(b_noise.outputs['Fac'], b_ramp.inputs['Fac'])

b_mix_ao = b_nodes.new(type='ShaderNodeMix')
b_mix_ao.data_type = 'RGBA'
b_mix_ao.blend_type = 'MULTIPLY'
b_mix_ao.location = (50, 200)
b_mix_ao.inputs['Factor'].default_value = 0.85
b_links.new(b_ramp.outputs['Color'], b_mix_ao.inputs['A'])
b_links.new(b_ao.outputs['Color'], b_mix_ao.inputs['B'])
b_links.new(b_mix_ao.outputs['Result'], b_bsdf.inputs['Base Color'])

b_bump = b_nodes.new(type='ShaderNodeBump')
b_bump.location = (350, -150)
b_bump.inputs['Strength'].default_value = 0.035
b_bump.inputs['Distance'].default_value = 0.002
b_links.new(b_noise.outputs['Fac'], b_bump.inputs['Height'])
b_links.new(b_bump.outputs['Normal'], b_bsdf.inputs['Normal'])

b_bsdf.inputs['Metallic'].default_value = 0.95
b_bsdf.inputs['Roughness'].default_value = 0.28
b_bsdf.inputs['Anisotropic'].default_value = 0.42


# =========================================================================
# 3. GREN-SKILDUS CLOTH WITH STAMPED THULAN CREST (PANEL 02)
# =========================================================================

mat_cloth = bpy.data.materials.get('Cinderback jade paint')
if not mat_cloth:
    mat_cloth = bpy.data.materials.new(name='Cinderback jade paint')

mat_cloth.use_nodes = True
c_nodes = mat_cloth.node_tree.nodes
c_links = mat_cloth.node_tree.links
c_nodes.clear()

c_out = c_nodes.new(type='ShaderNodeOutputMaterial')
c_out.location = (1100, 0)
c_bsdf = c_nodes.new(type='ShaderNodeBsdfPrincipled')
c_bsdf.location = (800, 0)
c_links.new(c_bsdf.outputs['BSDF'], c_out.inputs['Surface'])

c_coord = c_nodes.new(type='ShaderNodeTexCoord')
c_coord.location = (-1200, 0)
c_map = c_nodes.new(type='ShaderNodeMapping')
c_map.location = (-1000, 0)
c_links.new(c_coord.outputs['Object'], c_map.inputs['Vector'])

# Fabric Weave Pattern
wave_x = c_nodes.new(type='ShaderNodeTexWave')
wave_x.location = (-750, 300)
wave_x.inputs['Scale'].default_value = 240.0
wave_x.inputs['Distortion'].default_value = 1.2
c_links.new(c_map.outputs['Vector'], wave_x.inputs['Vector'])

wave_y = c_nodes.new(type='ShaderNodeTexWave')
wave_y.location = (-750, 50)
wave_y.wave_type = 'BANDS'
wave_y.bands_direction = 'Y'
wave_y.inputs['Scale'].default_value = 240.0
wave_y.inputs['Distortion'].default_value = 1.2
c_links.new(c_map.outputs['Vector'], wave_y.inputs['Vector'])

mix_weave = c_nodes.new(type='ShaderNodeMix')
mix_weave.data_type = 'FLOAT'
mix_weave.blend_type = 'ADD'
mix_weave.location = (-450, 200)
mix_weave.inputs['Factor'].default_value = 0.5
c_links.new(wave_x.outputs['Color'], mix_weave.inputs['A'])
c_links.new(wave_y.outputs['Color'], mix_weave.inputs['B'])

# Procedural Thulan Cross Insignia Stamp
# Center of Skildus is around X=0.48, Y=-0.52, Z=1.80
# We calculate distance to vertical bar & two horizontal crossbars
tex_pos = c_nodes.new(type='ShaderNodeMapping')
tex_pos.location = (-750, -300)
tex_pos.inputs['Location'].default_value = (-0.48, 0.52, -1.78)
c_links.new(c_coord.outputs['Object'], tex_pos.inputs['Vector'])

sep = c_nodes.new(type='ShaderNodeSeparateXYZ')
sep.location = (-500, -300)
c_links.new(tex_pos.outputs['Vector'], sep.inputs['Vector'])

# Mathematical mask for cross
math_vx = c_nodes.new(type='ShaderNodeMath')
math_vx.operation = 'ABSOLUTE'
math_vx.location = (-300, -200)
c_links.new(sep.outputs['X'], math_vx.inputs[0])

math_vy = c_nodes.new(type='ShaderNodeMath')
math_vy.operation = 'ABSOLUTE'
math_vy.location = (-300, -350)
c_links.new(sep.outputs['Z'], math_vy.inputs[0])

# Combine for cross stamp
math_cross = c_nodes.new(type='ShaderNodeMath')
math_cross.operation = 'LESS_THAN'
math_cross.inputs[1].default_value = 0.022
math_cross.location = (-100, -250)
c_links.new(math_vx.outputs['Value'], math_cross.inputs[0])

# Base Canvas Green Color vs Stamped Bone White
mix_cloth_color = c_nodes.new(type='ShaderNodeMix')
mix_cloth_color.data_type = 'RGBA'
mix_cloth_color.location = (250, 100)
mix_cloth_color.inputs['Factor'].default_value = 0.0 # mostly field-green
mix_cloth_color.inputs['A'].default_value = (0.032, 0.075, 0.042, 1.0) # weathered treated sage/field green
mix_cloth_color.inputs['B'].default_value = (0.65, 0.62, 0.55, 1.0) # bone white insignia
c_links.new(mix_cloth_color.outputs['Result'], c_bsdf.inputs['Base Color'])

c_bump = c_nodes.new(type='ShaderNodeBump')
c_bump.location = (450, -150)
c_bump.inputs['Strength'].default_value = 0.15
c_bump.inputs['Distance'].default_value = 0.002
c_links.new(mix_weave.outputs['Result'], c_bump.inputs['Height'])
c_links.new(c_bump.outputs['Normal'], c_bsdf.inputs['Normal'])

c_bsdf.inputs['Roughness'].default_value = 0.88
c_bsdf.inputs['Metallic'].default_value = 0.0
c_bsdf.inputs['Sheen Weight'].default_value = 0.80
c_bsdf.inputs['Sheen Tint'].default_value = (0.1, 0.25, 0.12, 1.0)


# =========================================================================
# 4. AMBER VISOR FORGE CORE (GLOWING MOLTEN OPTICAL SLIT)
# =========================================================================

mat_vis = bpy.data.materials.get('Amber visor')
if mat_vis:
    mat_vis.use_nodes = True
    v_nodes = mat_vis.node_tree.nodes
    v_links = mat_vis.node_tree.links
    v_nodes.clear()
    
    v_out = v_nodes.new(type='ShaderNodeOutputMaterial')
    v_out.location = (600, 0)
    v_bsdf = v_nodes.new(type='ShaderNodeBsdfPrincipled')
    v_bsdf.location = (300, 0)
    v_links.new(v_bsdf.outputs['BSDF'], v_out.inputs['Surface'])
    
    v_bsdf.inputs['Base Color'].default_value = (1.0, 0.42, 0.03, 1.0)
    v_bsdf.inputs['Emission Color'].default_value = (1.0, 0.48, 0.05, 1.0)
    v_bsdf.inputs['Emission Strength'].default_value = 24.0
    v_bsdf.inputs['Roughness'].default_value = 0.05

# Save candidate V22
bpy.context.scene.render.filepath = '/home/aaron/animation/thulans-production/assets/art/varek_v22_materials_frame_'
bpy.ops.wm.save_as_mainfile(filepath=save_blend)
print(f"Successfully generated Canonical Materials V22 at {save_blend}")
