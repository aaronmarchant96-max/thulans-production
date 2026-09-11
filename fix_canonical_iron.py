import bpy

source_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v22-materials.blend'
save_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v22-materials.blend'

bpy.ops.wm.open_mainfile(filepath=source_blend)

mat_iron = bpy.data.materials.get('Warm charcoal cast iron')
if mat_iron:
    nodes = mat_iron.node_tree.nodes
    links = mat_iron.node_tree.links
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
    
    # Micro fine surface noise
    noise_fine = nodes.new(type='ShaderNodeTexNoise')
    noise_fine.location = (-550, 150)
    noise_fine.inputs['Scale'].default_value = 160.0
    noise_fine.inputs['Detail'].default_value = 5.0
    noise_fine.inputs['Roughness'].default_value = 0.55
    links.new(mapping.outputs['Vector'], noise_fine.inputs['Vector'])
    
    # Ambient Occlusion for deep seam dirt
    ao = nodes.new(type='ShaderNodeAmbientOcclusion')
    ao.location = (-300, 350)
    ao.inputs['Distance'].default_value = 0.12
    
    # Base dark cast iron color ramp (Sovereign dark ferrous)
    ramp_base = nodes.new(type='ShaderNodeValToRGB')
    ramp_base.location = (-300, 100)
    ramp_base.color_ramp.elements[0].position = 0.2
    ramp_base.color_ramp.elements[0].color = (0.016, 0.017, 0.019, 1.0) # deep grimdark iron
    ramp_base.color_ramp.elements[1].position = 0.8
    ramp_base.color_ramp.elements[1].color = (0.028, 0.030, 0.033, 1.0) # subtle cold steel sheen
    links.new(noise_fine.outputs['Fac'], ramp_base.inputs['Fac'])
    
    # Multiply with AO
    mix_ao = nodes.new(type='ShaderNodeMix')
    mix_ao.data_type = 'RGBA'
    mix_ao.blend_type = 'MULTIPLY'
    mix_ao.location = (50, 150)
    mix_ao.inputs['Factor'].default_value = 0.85
    links.new(ramp_base.outputs['Color'], mix_ao.inputs['A'])
    links.new(ao.outputs['Color'], mix_ao.inputs['B'])
    links.new(mix_ao.outputs['Result'], bsdf.inputs['Base Color'])
    
    # Fine bump
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (200, -150)
    bump.inputs['Strength'].default_value = 0.025
    bump.inputs['Distance'].default_value = 0.002
    links.new(noise_fine.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    bsdf.inputs['Metallic'].default_value = 0.94
    bsdf.inputs['Roughness'].default_value = 0.44
    bsdf.inputs['Specular IOR Level'].default_value = 0.55

bpy.ops.wm.save_as_mainfile(filepath=save_blend)
print("Updated pure dark cast iron shader!")
