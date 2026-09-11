import bpy
import math
from mathutils import Euler, Quaternion, Vector

source_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v20-canonical.blend'
save_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v20-canonical.blend'

bpy.ops.wm.open_mainfile(filepath=source_blend)
arm = bpy.data.objects['Varek simple articulation']

# 1. FIX THE CAST IRON SHADER (DEEP SOVEREIGN DARK FERROUS IRON)
mat_iron = bpy.data.materials.get('Warm charcoal cast iron')
if mat_iron:
    nodes = mat_iron.node_tree.nodes
    links = mat_iron.node_tree.links
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
    
    # Very fine micro-noise for cold cast iron tooth
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-500, 100)
    noise.inputs['Scale'].default_value = 140.0
    noise.inputs['Detail'].default_value = 4.0
    noise.inputs['Roughness'].default_value = 0.6
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    
    # Ambient Occlusion for deep crevices
    ao = nodes.new(type='ShaderNodeAmbientOcclusion')
    ao.location = (-200, 250)
    ao.inputs['Distance'].default_value = 0.15
    
    # Base dark iron color
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-200, 50)
    color_ramp.color_ramp.elements[0].position = 0.3
    color_ramp.color_ramp.elements[0].color = (0.020, 0.021, 0.023, 1.0) # deep grimdark steel
    color_ramp.color_ramp.elements[1].position = 0.7
    color_ramp.color_ramp.elements[1].color = (0.038, 0.040, 0.044, 1.0) # subtle cold highlight
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    
    mix_ao = nodes.new(type='ShaderNodeMix')
    mix_ao.data_type = 'RGBA'
    mix_ao.blend_type = 'MULTIPLY'
    mix_ao.location = (50, 100)
    mix_ao.inputs['Factor'].default_value = 0.75
    links.new(color_ramp.outputs['Color'], mix_ao.inputs['A'])
    links.new(ao.outputs['Color'], mix_ao.inputs['B'])
    links.new(mix_ao.outputs['Result'], bsdf.inputs['Base Color'])
    
    # Bump
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (50, -150)
    bump.inputs['Strength'].default_value = 0.035
    bump.inputs['Distance'].default_value = 0.003
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    bsdf.inputs['Metallic'].default_value = 0.92
    bsdf.inputs['Roughness'].default_value = 0.42
    bsdf.inputs['Specular IOR Level'].default_value = 0.55

# 2. FIX MAUL INSCRIBED CHEEK PLATES (FLUSH ON HAMMER HEAD)
maul_head = bpy.data.objects.get('Fault Maul head')
p_top = bpy.data.objects.get('Maul_Inscribed_CheekPlate_Top')
p_bot = bpy.data.objects.get('Maul_Inscribed_CheekPlate_Bottom')

if maul_head and p_top and p_bot:
    # Hammer head center is around (-0.85, -0.75, 0.12)
    p_top.location = (-0.854, -0.92, 0.22)
    p_top.scale = (0.24, 0.02, 0.08)
    p_top.rotation_euler = (0, 0, 0)
    
    p_bot.location = (-0.854, -0.92, 0.02)
    p_bot.scale = (0.24, 0.02, 0.08)
    p_bot.rotation_euler = (0, 0, 0)

# 3. FIX LEFT THIGH PLAQUE (FLUSH ON THIGH GUARD)
thigh_plaque = bpy.data.objects.get('Thigh_Fairgunjis_Plaque')
v_left = bpy.data.objects.get('Thigh_V_Left')
v_right = bpy.data.objects.get('Thigh_V_Right')

if thigh_plaque:
    thigh_plaque.location = (0.243, -0.28, 0.92)
    thigh_plaque.rotation_euler = (math.radians(-15), 0, 0)
    thigh_plaque.scale = (0.14, 0.02, 0.18)

if v_left and v_right:
    v_left.location = (0.225, -0.295, 0.94)
    v_left.rotation_euler = (math.radians(-15), math.radians(20), 0)
    v_left.scale = (1.0, 1.0, 0.8)
    
    v_right.location = (0.260, -0.295, 0.94)
    v_right.rotation_euler = (math.radians(-15), math.radians(-20), 0)
    v_right.scale = (1.0, 1.0, 0.8)

# 4. FIX FOREARM HYDRAULIC RAMS (TIGHT TO FOREARMS)
for side, sign in [('L', 1.0), ('R', -1.0)]:
    for h_idx, offset_x in enumerate([-0.03, 0.03]):
        cyl = bpy.data.objects.get(f'Forearm_Hydraulic_Cylinder_{side}_{h_idx}')
        rod = bpy.data.objects.get(f'Forearm_Hydraulic_Rod_{side}_{h_idx}')
        mount = bpy.data.objects.get(f'Forearm_Hydraulic_Mount_{side}_{h_idx}')
        
        base_x = sign * 0.58 + offset_x
        if cyl:
            cyl.location = (base_x, -0.05, 1.32)
            cyl.rotation_euler = (math.radians(10), 0, 0)
            cyl.scale = (0.7, 0.7, 0.8)
        if rod:
            rod.location = (base_x, -0.07, 1.20)
            rod.rotation_euler = (math.radians(10), 0, 0)
            rod.scale = (0.7, 0.7, 0.8)
        if mount:
            mount.location = (base_x, -0.05, 1.38)
            mount.rotation_euler = (math.radians(10), 0, 0)
            mount.scale = (0.7, 0.7, 0.7)

# 5. GREN-SKILDUS CLOTH TEXTURE WITH THULAN CREST (PANEL 02)
mat_cloth = bpy.data.materials.get('Cinderback jade paint')
if mat_cloth:
    nodes = mat_cloth.node_tree.nodes
    links = mat_cloth.node_tree.links
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
    
    # Weave bump
    wave_x = nodes.new(type='ShaderNodeTexWave')
    wave_x.location = (-600, 200)
    wave_x.inputs['Scale'].default_value = 180.0
    links.new(mapping.outputs['Vector'], wave_x.inputs['Vector'])
    
    wave_y = nodes.new(type='ShaderNodeTexWave')
    wave_y.location = (-600, 0)
    wave_y.wave_type = 'BANDS'
    wave_y.bands_direction = 'Y'
    wave_y.inputs['Scale'].default_value = 180.0
    links.new(mapping.outputs['Vector'], wave_y.inputs['Vector'])
    
    mix_weave = nodes.new(type='ShaderNodeMix')
    mix_weave.data_type = 'FLOAT'
    mix_weave.blend_type = 'ADD'
    mix_weave.location = (-350, 100)
    mix_weave.inputs['Factor'].default_value = 0.5
    links.new(wave_x.outputs['Color'], mix_weave.inputs['A'])
    links.new(wave_y.outputs['Color'], mix_weave.inputs['B'])
    
    # Procedural Thulan Cross Insignia on cloth
    # Mask vertical stripe & horizontal bars
    sep = nodes.new(type='ShaderNodeSeparateXYZ')
    sep.location = (-600, -250)
    links.new(mapping.outputs['Vector'], sep.inputs['Vector'])
    
    # Cloth base color: Dark treated field-green
    bsdf.inputs['Base Color'].default_value = (0.038, 0.082, 0.048, 1.0) # weathered Thulan field green
    bsdf.inputs['Roughness'].default_value = 0.88
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Sheen Weight'].default_value = 0.85
    bsdf.inputs['Sheen Tint'].default_value = (0.1, 0.25, 0.12, 1.0)
    
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (200, -100)
    bump.inputs['Strength'].default_value = 0.12
    bump.inputs['Distance'].default_value = 0.002
    links.new(mix_weave.outputs['Result'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

# Save refined canonical V20
bpy.ops.wm.save_as_mainfile(filepath=save_blend)
print("Successfully refined V20 Canonical candidate!")
