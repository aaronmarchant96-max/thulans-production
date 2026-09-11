import bpy
import math
from mathutils import Euler, Quaternion, Vector

source_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v23-cloth.blend'
save_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v24-canonical.blend'

bpy.ops.wm.open_mainfile(filepath=source_blend)
arm = bpy.data.objects['Varek simple articulation']

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
out_node.location = (1200, 0)
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.location = (900, 0)
links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])

tex_coord = nodes.new(type='ShaderNodeTexCoord')
tex_coord.location = (-1200, 0)
mapping = nodes.new(type='ShaderNodeMapping')
mapping.location = (-1000, 0)
links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

# Fine cast tooth noise
noise_fine = nodes.new(type='ShaderNodeTexNoise')
noise_fine.location = (-750, 250)
noise_fine.inputs['Scale'].default_value = 120.0
noise_fine.inputs['Detail'].default_value = 6.0
noise_fine.inputs['Roughness'].default_value = 0.6
links.new(mapping.outputs['Vector'], noise_fine.inputs['Vector'])

# Scratch / Scrape Noise
noise_scratch = nodes.new(type='ShaderNodeTexNoise')
noise_scratch.location = (-750, -50)
noise_scratch.inputs['Scale'].default_value = 35.0
noise_scratch.inputs['Detail'].default_value = 8.0
noise_scratch.inputs['Roughness'].default_value = 0.8
links.new(mapping.outputs['Vector'], noise_scratch.inputs['Vector'])

# Ambient Occlusion for Crevices
ao = nodes.new(type='ShaderNodeAmbientOcclusion')
ao.location = (-450, 450)
ao.inputs['Distance'].default_value = 0.16

# Bevel Node for Edge-Wear
bevel = nodes.new(type='ShaderNodeBevel')
bevel.location = (-750, -350)
bevel.inputs['Radius'].default_value = 0.022
bevel.samples = 8

# Geometry Pointiness for Sharp Edges
geom = nodes.new(type='ShaderNodeNewGeometry')
geom.location = (-750, -600)

# Pointiness Color Ramp
ramp_point = nodes.new(type='ShaderNodeValToRGB')
ramp_point.location = (-450, -450)
ramp_point.color_ramp.elements[0].position = 0.45
ramp_point.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
ramp_point.color_ramp.elements[1].position = 0.65
ramp_point.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
links.new(geom.outputs['Pointiness'], ramp_point.inputs['Fac'])

# Scratch Mask
ramp_scratch = nodes.new(type='ShaderNodeValToRGB')
ramp_scratch.location = (-450, -150)
ramp_scratch.color_ramp.elements[0].position = 0.52
ramp_scratch.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
ramp_scratch.color_ramp.elements[1].position = 0.80
ramp_scratch.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
links.new(noise_scratch.outputs['Fac'], ramp_scratch.inputs['Fac'])

# Combine Edge + Scratches
mix_chip_fac = nodes.new(type='ShaderNodeMix')
mix_chip_fac.data_type = 'FLOAT'
mix_chip_fac.blend_type = 'ADD'
mix_chip_fac.location = (-200, -250)
mix_chip_fac.inputs['Factor'].default_value = 0.75
links.new(ramp_point.outputs['Color'], mix_chip_fac.inputs['A'])
links.new(ramp_scratch.outputs['Color'], mix_chip_fac.inputs['B'])

# Base Dark Cast Iron Color Ramp
ramp_base = nodes.new(type='ShaderNodeValToRGB')
ramp_base.location = (-450, 150)
ramp_base.color_ramp.elements[0].position = 0.2
ramp_base.color_ramp.elements[0].color = (0.020, 0.022, 0.024, 1.0) # dark ferrous
ramp_base.color_ramp.elements[1].position = 0.8
ramp_base.color_ramp.elements[1].color = (0.040, 0.042, 0.046, 1.0)
links.new(noise_fine.outputs['Fac'], ramp_base.inputs['Fac'])

# Chipped Edge Color (Warm Bronze + Bare Steel)
mix_edge_color = nodes.new(type='ShaderNodeMix')
mix_edge_color.data_type = 'RGBA'
mix_edge_color.location = (150, 50)
links.new(mix_chip_fac.outputs['Result'], mix_edge_color.inputs['Factor'])
links.new(ramp_base.outputs['Color'], mix_edge_color.inputs['A'])
mix_edge_color.inputs['B'].default_value = (0.65, 0.46, 0.20, 1.0) # warm chipped bronze/gold edge

# Multiply with AO
mix_final_color = nodes.new(type='ShaderNodeMix')
mix_final_color.data_type = 'RGBA'
mix_final_color.blend_type = 'MULTIPLY'
mix_final_color.location = (450, 150)
mix_final_color.inputs['Factor'].default_value = 0.80
links.new(mix_edge_color.outputs['Result'], mix_final_color.inputs['A'])
links.new(ao.outputs['Color'], mix_final_color.inputs['B'])
links.new(mix_final_color.outputs['Result'], bsdf.inputs['Base Color'])

# Roughness
rough_map = nodes.new(type='ShaderNodeMapRange')
rough_map.location = (450, -100)
rough_map.inputs['From Min'].default_value = 0.2
rough_map.inputs['From Max'].default_value = 0.8
rough_map.inputs['To Min'].default_value = 0.38
rough_map.inputs['To Max'].default_value = 0.62
links.new(noise_fine.outputs['Fac'], rough_map.inputs['Value'])
links.new(rough_map.outputs['Result'], bsdf.inputs['Roughness'])

# Bump
bump = nodes.new(type='ShaderNodeBump')
bump.location = (650, -250)
bump.inputs['Strength'].default_value = 0.045
bump.inputs['Distance'].default_value = 0.003
links.new(noise_fine.outputs['Fac'], bump.inputs['Height'])
links.new(bevel.outputs['Normal'], bump.inputs['Normal'])
links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

bsdf.inputs['Metallic'].default_value = 0.94
bsdf.inputs['Specular IOR Level'].default_value = 0.58


# =========================================================================
# 2. FOOT TREAD HOUSING & HEEL TRENCH ACTUATORS (BOTTOM PANEL ALIGNMENT)
# =========================================================================

for side, f_bone, x_pos, f_sign in [('L', 'foot.L', 0.243, 1.0), ('R', 'foot.R', -0.243, -1.0)]:
    # Segmented Toe Tread Bars (3 heavy steel cleats across front sole)
    for t_idx in range(3):
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(x_pos, -0.42 - t_idx*0.065, 0.04),
            rotation=(0, 0, 0)
        )
        cleat = bpy.context.active_object
        cleat.name = f"Foot_Toe_Cleat_{side}_{t_idx}"
        cleat.scale = (0.24, 0.038, 0.045)
        bpy.ops.object.transform_apply(scale=True)
        if mat_iron:
            cleat.data.materials.append(mat_iron)
        bind_to_bone(cleat, f_bone)
    
    # Side Tread Armor Plates
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(x_pos + f_sign*0.13, -0.32, 0.12),
        rotation=(0, 0, 0)
    )
    side_plate = bpy.context.active_object
    side_plate.name = f"Foot_Side_Armor_{side}"
    side_plate.scale = (0.035, 0.28, 0.14)
    bpy.ops.object.transform_apply(scale=True)
    if mat_iron:
        side_plate.data.materials.append(mat_iron)
    bind_to_bone(side_plate, f_bone)


# =========================================================================
# 3. HEAVY GAUNTLET KNUCKLE ARTICULATION & CYLINDERS (PANEL 04)
# =========================================================================

for side, h_bone, x_pos, f_sign in [('L', 'hand.L', 0.58, 1.0), ('R', 'hand.R', -0.58, -1.0)]:
    # 3 Heavy rectangular knuckle bars across hand dorsum
    for k_idx in range(3):
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(x_pos, -0.15 - k_idx*0.045, 1.12),
            rotation=(math.radians(15), 0, 0)
        )
        knuckle = bpy.context.active_object
        knuckle.name = f"Gauntlet_Knuckle_Bar_{side}_{k_idx}"
        knuckle.scale = (0.12, 0.032, 0.035)
        bpy.ops.object.transform_apply(scale=True)
        if mat_iron:
            knuckle.data.materials.append(mat_iron)
        bind_to_bone(knuckle, h_bone)


# =========================================================================
# 4. GREN-SKILDUS CLOTH FINE-TUNING (PANEL 02)
# =========================================================================

# Ensure cloth material has rich dark weathered sage green
mat_cloth = bpy.data.materials.get('Cinderback jade paint')
if mat_cloth and mat_cloth.node_tree:
    bsdf_c = None
    for n in mat_cloth.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            bsdf_c = n
            break
    if bsdf_c:
        bsdf_c.inputs['Base Color'].default_value = (0.028, 0.065, 0.036, 1.0) # dark rich weathered army green
        bsdf_c.inputs['Roughness'].default_value = 0.94


# =========================================================================
# 5. CINEMATIC GRIMDARK LIGHTING & RIM HIGHLIGHTS
# =========================================================================

key = bpy.data.objects.get('Key')
if key:
    key.data.energy = 950.0
    key.data.color = (1.0, 0.92, 0.82) # warm industrial lantern
    key.data.size = 3.0

rim = bpy.data.objects.get('Rim')
if rim:
    rim.data.energy = 2200.0 # intense back-rim to ignite all beveled edge-chipping!
    rim.data.color = (0.80, 0.90, 1.0)
    rim.location = (2.5, 5.0, 4.2)
    rim.data.size = 3.5

fill = bpy.data.objects.get('Fill')
if fill:
    fill.data.energy = 250.0
    fill.data.color = (0.4, 0.5, 0.65) # dark moody fill

# Save candidate V24
bpy.context.scene.render.filepath = '/home/aaron/animation/thulans-production/assets/art/varek_v24_feel_frame_'
bpy.ops.wm.save_as_mainfile(filepath=save_blend)
print(f"Successfully generated Varek Canonical V24 Feel Overhaul at {save_blend}")
