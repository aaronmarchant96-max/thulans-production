import bpy
import math
from mathutils import Euler, Quaternion, Vector

# Load candidate varek-walk-v17
source_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-walk-v17.blend'
save_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-aura-v18.blend'

# 1. SHADER NETWORK BUILDERS

def create_cast_iron_shader(mat):
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Output
    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    out_node.location = (600, 0)
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
    
    # Texture Coordinate & Mapping
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-900, 0)
    
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-700, 0)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    
    # Noise 1: Fine Cast Texture
    noise_fine = nodes.new(type='ShaderNodeTexNoise')
    noise_fine.location = (-500, 200)
    noise_fine.inputs['Scale'].default_value = 85.0
    noise_fine.inputs['Detail'].default_value = 6.0
    noise_fine.inputs['Roughness'].default_value = 0.65
    links.new(mapping.outputs['Vector'], noise_fine.inputs['Vector'])
    
    # Noise 2: Mill Scale Mottling
    noise_scale = nodes.new(type='ShaderNodeTexNoise')
    noise_scale.location = (-500, -100)
    noise_scale.inputs['Scale'].default_value = 8.0
    noise_scale.inputs['Detail'].default_value = 3.5
    noise_scale.inputs['Roughness'].default_value = 0.5
    links.new(mapping.outputs['Vector'], noise_scale.inputs['Vector'])
    
    # Color Ramp for Base Color (Cold Dark Ferrous / Cast Iron)
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-200, 200)
    color_ramp.color_ramp.elements[0].position = 0.3
    color_ramp.color_ramp.elements[0].color = (0.025, 0.026, 0.028, 1.0) # deep dark iron
    color_ramp.color_ramp.elements[1].position = 0.8
    color_ramp.color_ramp.elements[1].color = (0.065, 0.068, 0.072, 1.0) # weathered cast surface
    links.new(noise_scale.outputs['Fac'], color_ramp.inputs['Fac'])
    
    # Ambient Occlusion node for crevice grime
    ao = nodes.new(type='ShaderNodeAmbientOcclusion')
    ao.location = (-200, 400)
    ao.inputs['Distance'].default_value = 0.15
    
    # Mix Color: Base + Crevice Darkening
    mix_color = nodes.new(type='ShaderNodeMix')
    mix_color.data_type = 'RGBA'
    mix_color.blend_type = 'MULTIPLY'
    mix_color.location = (50, 200)
    mix_color.inputs['Factor'].default_value = 0.65
    links.new(color_ramp.outputs['Color'], mix_color.inputs['A'])
    links.new(ao.outputs['Color'], mix_color.inputs['B'])
    links.new(mix_color.outputs['Result'], bsdf.inputs['Base Color'])
    
    # Roughness Map Range
    rough_map = nodes.new(type='ShaderNodeMapRange')
    rough_map.location = (-200, -100)
    rough_map.inputs['From Min'].default_value = 0.2
    rough_map.inputs['From Max'].default_value = 0.8
    rough_map.inputs['To Min'].default_value = 0.45
    rough_map.inputs['To Max'].default_value = 0.72
    links.new(noise_fine.outputs['Fac'], rough_map.inputs['Value'])
    links.new(rough_map.outputs['Result'], bsdf.inputs['Roughness'])
    
    # Bump Node
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (50, -200)
    bump.inputs['Strength'].default_value = 0.08
    bump.inputs['Distance'].default_value = 0.005
    links.new(noise_fine.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    # Material Settings
    bsdf.inputs['Metallic'].default_value = 0.85
    bsdf.inputs['Specular IOR Level'].default_value = 0.55

def create_aged_bronze_shader(mat):
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    out_node.location = (600, 0)
    
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
    
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-900, 0)
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-700, 0)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-500, 100)
    noise.inputs['Scale'].default_value = 35.0
    noise.inputs['Detail'].default_value = 5.0
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-200, 100)
    color_ramp.color_ramp.elements[0].position = 0.2
    color_ramp.color_ramp.elements[0].color = (0.32, 0.18, 0.06, 1.0) # deep oily bronze
    color_ramp.color_ramp.elements[1].position = 0.8
    color_ramp.color_ramp.elements[1].color = (0.58, 0.38, 0.16, 1.0) # warm polished phosphor bronze
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (50, -100)
    bump.inputs['Strength'].default_value = 0.04
    bump.inputs['Distance'].default_value = 0.003
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    bsdf.inputs['Metallic'].default_value = 0.94
    bsdf.inputs['Roughness'].default_value = 0.32
    bsdf.inputs['Anisotropic'].default_value = 0.35

def create_piston_steel_shader(mat):
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    out_node.location = (600, 0)
    
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
    
    bsdf.inputs['Base Color'].default_value = (0.55, 0.58, 0.60, 1.0) # machined hardened steel
    bsdf.inputs['Metallic'].default_value = 0.98
    bsdf.inputs['Roughness'].default_value = 0.14
    bsdf.inputs['Specular IOR Level'].default_value = 0.65

def create_amber_visor_shader(mat):
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    out_node.location = (600, 0)
    
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
    
    # Molten amber forge glow
    bsdf.inputs['Base Color'].default_value = (1.0, 0.45, 0.05, 1.0)
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.52, 0.08, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 18.0
    bsdf.inputs['Roughness'].default_value = 0.1

def create_gren_skildus_shader(mat):
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    out_node.location = (600, 0)
    
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
    
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-900, 0)
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-700, 0)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    
    # Fabric Weave Pattern (Wave X & Y)
    wave_x = nodes.new(type='ShaderNodeTexWave')
    wave_x.location = (-500, 200)
    wave_x.inputs['Scale'].default_value = 220.0
    wave_x.inputs['Distortion'].default_value = 1.5
    links.new(mapping.outputs['Vector'], wave_x.inputs['Vector'])
    
    wave_y = nodes.new(type='ShaderNodeTexWave')
    wave_y.location = (-500, -100)
    wave_y.wave_type = 'BANDS'
    wave_y.bands_direction = 'Y'
    wave_y.inputs['Scale'].default_value = 220.0
    wave_y.inputs['Distortion'].default_value = 1.5
    links.new(mapping.outputs['Vector'], wave_y.inputs['Vector'])
    
    mix_weave = nodes.new(type='ShaderNodeMix')
    mix_weave.data_type = 'FLOAT'
    mix_weave.blend_type = 'ADD'
    mix_weave.location = (-200, 100)
    mix_weave.inputs['Factor'].default_value = 0.5
    links.new(wave_x.outputs['Color'], mix_weave.inputs['A'])
    links.new(wave_y.outputs['Color'], mix_weave.inputs['B'])
    
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (50, -100)
    bump.inputs['Strength'].default_value = 0.15
    bump.inputs['Distance'].default_value = 0.002
    links.new(mix_weave.outputs['Result'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    # Sovereign Thulan Field-Green Canvas
    bsdf.inputs['Base Color'].default_value = (0.045, 0.12, 0.065, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.85
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Sheen Weight'].default_value = 0.75
    bsdf.inputs['Sheen Tint'].default_value = (0.1, 0.25, 0.12, 1.0)

def create_studio_floor_shader(mat):
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    out_node.location = (600, 0)
    
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
    
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-900, 0)
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-700, 0)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-500, 0)
    noise.inputs['Scale'].default_value = 12.0
    noise.inputs['Detail'].default_value = 4.0
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-200, 100)
    color_ramp.color_ramp.elements[0].position = 0.2
    color_ramp.color_ramp.elements[0].color = (0.035, 0.035, 0.038, 1.0) # damp iron flagstone
    color_ramp.color_ramp.elements[1].position = 0.8
    color_ramp.color_ramp.elements[1].color = (0.075, 0.075, 0.080, 1.0)
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (50, -100)
    bump.inputs['Strength'].default_value = 0.06
    bump.inputs['Distance'].default_value = 0.005
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    bsdf.inputs['Metallic'].default_value = 0.4
    bsdf.inputs['Roughness'].default_value = 0.45

# Apply shaders to existing materials in scene
for mat in bpy.data.materials:
    if mat.name == 'Warm charcoal cast iron':
        create_cast_iron_shader(mat)
        print('Updated Warm charcoal cast iron')
    elif mat.name in ['Aged brass', 'Oily joint steel']:
        create_aged_bronze_shader(mat)
        print(f'Updated {mat.name}')
    elif mat.name == 'Working piston steel':
        create_piston_steel_shader(mat)
        print('Updated Working piston steel')
    elif mat.name == 'Amber visor':
        create_amber_visor_shader(mat)
        print('Updated Amber visor')
    elif mat.name == 'Cinderback jade paint':
        create_gren_skildus_shader(mat)
        print('Updated Gren Skildus cloth')
    elif mat.name == 'Studio warm grey':
        create_studio_floor_shader(mat)
        print('Updated Studio warm grey floor')

# 2. ADD HEARTH-CORE VISOR LIGHT (EMBEDDED AMBER POINT LIGHT)
arm = bpy.data.objects['Varek simple articulation']
visor_light_name = "Visor_Internal_Hearth_Light"
v_light_obj = bpy.data.objects.get(visor_light_name)
if not v_light_obj:
    v_light_data = bpy.data.lights.new(name=visor_light_name, type='POINT')
    v_light_data.energy = 8.0
    v_light_data.color = (1.0, 0.45, 0.05)
    v_light_data.shadow_soft_size = 0.03
    v_light_obj = bpy.data.objects.new(name=visor_light_name, object_data=v_light_data)
    bpy.context.scene.collection.objects.link(v_light_obj)

# Parent visor light to Head bone
v_light_obj.parent = arm
v_light_obj.parent_type = 'BONE'
v_light_obj.parent_bone = 'head'
v_light_obj.location = (0.0, 0.12, 0.08) # slight forward offset inside visor slit

# 3. ATMOSPHERIC VOLUMETRIC SCATTER BOX (THE FORGE AURA)
vol_name = "Atmospheric_Forge_Haze"
vol_obj = bpy.data.objects.get(vol_name)
if not vol_obj:
    bpy.ops.mesh.primitive_cube_add(size=20.0, location=(0, 0, 5.0))
    vol_obj = bpy.context.active_object
    vol_obj.name = vol_name
    vol_obj.display_type = 'WIRE'
    
    # Volumetric Material
    vol_mat = bpy.data.materials.new(name="M_Atmospheric_Haze")
    vol_mat.use_nodes = True
    v_nodes = vol_mat.node_tree.nodes
    v_links = vol_mat.node_tree.links
    v_nodes.clear()
    
    v_out = v_nodes.new(type='ShaderNodeOutputMaterial')
    v_scatter = v_nodes.new(type='ShaderNodeVolumeScatter')
    v_scatter.inputs['Density'].default_value = 0.003
    v_scatter.inputs['Anisotropy'].default_value = 0.65 # forward-scattering for dramatic rim rays
    v_scatter.inputs['Color'].default_value = (0.85, 0.88, 0.95, 1.0) # subtle cool industrial dust
    v_links.new(v_scatter.outputs['Volume'], v_out.inputs['Volume'])
    
    vol_obj.data.materials.append(vol_mat)

# 4. TWEAK CINEMATIC LIGHTS FOR GRIMDARK MOOD
key_light = bpy.data.objects.get('Key')
if key_light:
    key_light.data.energy = 850.0
    key_light.data.color = (1.0, 0.94, 0.85) # warm tungsten foundry light
    key_light.data.size = 2.5

rim_light = bpy.data.objects.get('Rim')
if rim_light:
    rim_light.data.energy = 1600.0 # powerful edge kicker to define sovereign silhouette
    rim_light.data.color = (0.75, 0.85, 1.0) # cool slate rim rake
    rim_light.data.size = 3.0
    rim_light.location = (2.0, 4.5, 3.8)

fill_light = bpy.data.objects.get('Fill')
if fill_light:
    fill_light.data.energy = 300.0
    fill_light.data.color = (0.5, 0.6, 0.75) # deep ambient bounce

# Save candidate
bpy.context.scene.render.filepath = '/home/aaron/animation/thulans-production/assets/art/varek_aura_v18_frame_'
bpy.ops.wm.save_as_mainfile(filepath=save_blend)
print(f"Successfully generated Varek Aura V18 candidate and saved to {save_blend}")
