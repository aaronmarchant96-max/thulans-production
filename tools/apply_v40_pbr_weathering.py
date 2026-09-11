import bpy
import math
from pathlib import Path

blend_path = '/home/aaron/animation/thulans-production/blender/candidates/varek-v40-osint-juggernaut.blend'
bpy.ops.wm.open_mainfile(filepath=blend_path)
scene = bpy.context.scene

# =============================================================================
# 1. ADVANCED PBR PROCEDURAL WEATHERING SHADER BUILDER
# =============================================================================

def create_weathered_iron_shader():
    mat = bpy.data.materials.get('QA_PBR_Weathered_CastIron')
    if not mat:
        mat = bpy.data.materials.new('QA_PBR_Weathered_CastIron')
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Base Nodes
    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (800, 0)

    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (500, 0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    # 1. Micro-pitted Cast Iron Noise
    noise_micro = nodes.new('ShaderNodeTexNoise')
    noise_micro.location = (-600, 200)
    noise_micro.inputs['Scale'].default_value = 85.0
    noise_micro.inputs['Detail'].default_value = 15.0
    noise_micro.inputs['Roughness'].default_value = 0.7

    # 2. Macro Grunge / Grime Noise
    noise_macro = nodes.new('ShaderNodeTexNoise')
    noise_macro.location = (-600, -100)
    noise_macro.inputs['Scale'].default_value = 6.0
    noise_macro.inputs['Detail'].default_value = 8.0

    # 3. Ambient Occlusion (Dirt in Crevices & Recesses)
    ao_node = nodes.new('ShaderNodeAmbientOcclusion')
    ao_node.location = (-600, -350)
    ao_node.inputs['Distance'].default_value = 0.25

    # 4. Pointiness / Curvature (Edge Wear Exposure)
    geom_node = nodes.new('ShaderNodeNewGeometry')
    geom_node.location = (-600, 450)

    # Ramp for Edge Wear
    ramp_edge = nodes.new('ShaderNodeValToRGB')
    ramp_edge.location = (-300, 450)
    ramp_edge.color_ramp.elements[0].position = 0.46
    ramp_edge.color_ramp.elements[1].position = 0.58
    links.new(geom_node.outputs['Pointiness'], ramp_edge.inputs['Fac'])

    # Ramp for Crevice AO Grime
    ramp_ao = nodes.new('ShaderNodeValToRGB')
    ramp_ao.location = (-300, -350)
    ramp_ao.color_ramp.elements[0].position = 0.2
    ramp_ao.color_ramp.elements[1].position = 0.7
    links.new(ao_node.outputs['Color'], ramp_ao.inputs['Fac'])

    # Mix Base Color: Deep Charcoal Cast Iron (0.07) -> Weathered Dark Steel (0.12) -> Raw Exposed Edge (0.28)
    mix_edge = nodes.new('ShaderNodeMix')
    mix_edge.data_type = 'RGBA'
    mix_edge.location = (0, 300)
    mix_edge.inputs[6].default_value = (0.08, 0.08, 0.09, 1.0) # Base cast iron
    mix_edge.inputs[7].default_value = (0.32, 0.32, 0.35, 1.0) # Edge exposed steel
    links.new(ramp_edge.outputs['Color'], mix_edge.inputs[0])

    mix_grime = nodes.new('ShaderNodeMix')
    mix_grime.data_type = 'RGBA'
    mix_grime.location = (250, 150)
    mix_grime.inputs[7].default_value = (0.03, 0.02, 0.02, 1.0) # Oil / grime in deep crevices
    links.new(mix_edge.outputs[2], mix_grime.inputs[6])
    links.new(ramp_ao.outputs['Color'], mix_grime.inputs[0])
    links.new(mix_grime.outputs[2], bsdf.inputs['Base Color'])

    # Metallic & Roughness
    bsdf.inputs['Metallic'].default_value = 0.88
    
    # Roughness modulated by noise and edge wear
    ramp_rough = nodes.new('ShaderNodeValToRGB')
    ramp_rough.location = (0, 0)
    ramp_rough.color_ramp.elements[0].position = 0.0
    ramp_rough.color_ramp.elements[0].color = (0.35, 0.35, 0.35, 1.0) # Smoother worn edges
    ramp_rough.color_ramp.elements[1].position = 1.0
    ramp_rough.color_ramp.elements[1].color = (0.65, 0.65, 0.65, 1.0) # Rougher pitted surface
    links.new(noise_micro.outputs['Fac'], ramp_rough.inputs['Fac'])
    links.new(ramp_rough.outputs['Color'], bsdf.inputs['Roughness'])

    # Bump Map (Cast Iron Texture + Edge Scratches)
    bump_node = nodes.new('ShaderNodeBump')
    bump_node.location = (250, -200)
    bump_node.inputs['Strength'].default_value = 0.12
    bump_node.inputs['Distance'].default_value = 0.005
    links.new(noise_micro.outputs['Fac'], bump_node.inputs['Height'])
    links.new(bump_node.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_weathered_bronze_shader():
    mat = bpy.data.materials.get('QA_PBR_Weathered_Bronze')
    if not mat:
        mat = bpy.data.materials.new('QA_PBR_Weathered_Bronze')
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    # Bronze Base Color with Oxidized Patina
    geom = nodes.new('ShaderNodeNewGeometry')
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.45
    ramp.color_ramp.elements[0].color = (0.22, 0.14, 0.06, 1.0) # Aged dark bronze
    ramp.color_ramp.elements[1].position = 0.60
    ramp.color_ramp.elements[1].color = (0.58, 0.40, 0.18, 1.0) # Polished highlight rim
    links.new(geom.outputs['Pointiness'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Metallic'].default_value = 0.92
    bsdf.inputs['Roughness'].default_value = 0.32
    return mat

def create_cloth_mantle_shader():
    mat = bpy.data.materials.get('QA_PBR_Gren_Skildus_Wool')
    if not mat:
        mat = bpy.data.materials.new('QA_PBR_Gren_Skildus_Wool')
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    # Deep Forest Green Coarse Wool (Concept Match)
    noise_wool = nodes.new('ShaderNodeTexNoise')
    noise_wool.inputs['Scale'].default_value = 120.0
    noise_wool.inputs['Detail'].default_value = 12.0

    mix_cloth = nodes.new('ShaderNodeMix')
    mix_cloth.data_type = 'RGBA'
    mix_cloth.inputs[6].default_value = (0.05, 0.10, 0.06, 1.0) # Deep shadowed forest green
    mix_cloth.inputs[7].default_value = (0.09, 0.16, 0.10, 1.0) # Surface green
    links.new(noise_wool.outputs['Fac'], mix_cloth.inputs[0])
    links.new(mix_cloth.outputs[2], bsdf.inputs['Base Color'])

    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = 0.92
    bsdf.inputs['Sheen Weight'].default_value = 0.8
    return mat

mat_pbr_iron = create_weathered_iron_shader()
mat_pbr_bronze = create_weathered_bronze_shader()
mat_pbr_cloth = create_cloth_mantle_shader()

# =============================================================================
# 2. ASSIGN ADVANCED PBR MATERIALS TO GEOMETRY
# =============================================================================

for obj in bpy.data.objects:
    if obj.type == 'MESH':
        if 'Mantle' in obj.name:
            obj.data.materials.clear()
            obj.data.materials.append(mat_pbr_cloth)
        elif 'Bronze' in obj.name or 'Trim' in obj.name or 'Cap' in obj.name or 'Pin' in obj.name or 'Boss' in obj.name or 'Flange' in obj.name or 'Tooth' in obj.name or 'Torc' in obj.name or 'Gauge' in obj.name:
            obj.data.materials.clear()
            obj.data.materials.append(mat_pbr_bronze)
        elif 'Visor' in obj.name or 'Slit' in obj.name:
            mat_amber = bpy.data.materials.get('QA_Amber_Visor')
            obj.data.materials.clear()
            obj.data.materials.append(mat_amber)
        else:
            obj.data.materials.clear()
            obj.data.materials.append(mat_pbr_iron)

# Save updated candidate
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"SUCCESS: PBR Weathered Varek V40 saved to {blend_path}")

