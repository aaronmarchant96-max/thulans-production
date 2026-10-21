import bpy
import math
from mathutils import Euler, Quaternion, Vector

source_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v27-canonical.blend'
save_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v28-canonical.blend'

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
# 1. MATERIALS DEFINITION
# =========================================================================

mat_iron = bpy.data.materials.get('Warm charcoal cast iron')
mat_brass = bpy.data.materials.get('Aged brass')
mat_cloth = bpy.data.materials.get('Cinderback jade paint')
mat_insignia = bpy.data.materials.get('M_Thulan_Insignia_BoneWhite')

# Refined Gren-Skildus Cloth Shader (Deep Monastic Olive Canvas)
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
    c_tex.location = (-900, 0)
    c_noise = c_nodes.new(type='ShaderNodeTexNoise')
    c_noise.location = (-600, 0)
    c_noise.inputs['Scale'].default_value = 180.0
    c_noise.inputs['Detail'].default_value = 6.0
    c_noise.inputs['Roughness'].default_value = 0.75
    c_links.new(c_tex.outputs['Object'], c_noise.inputs['Vector'])

    c_bump = c_nodes.new(type='ShaderNodeBump')
    c_bump.location = (-200, -200)
    c_bump.inputs['Strength'].default_value = 0.06
    c_bump.inputs['Distance'].default_value = 0.003
    c_links.new(c_noise.outputs['Fac'], c_bump.inputs['Height'])
    c_links.new(c_bump.outputs['Normal'], c_bsdf.inputs['Normal'])

    # Deep military olive drab
    c_ramp = c_nodes.new(type='ShaderNodeValToRGB')
    c_ramp.location = (-200, 150)
    c_ramp.color_ramp.elements[0].position = 0.2
    c_ramp.color_ramp.elements[0].color = (0.012, 0.032, 0.018, 1.0) # rich dark olive
    c_ramp.color_ramp.elements[1].position = 0.8
    c_ramp.color_ramp.elements[1].color = (0.022, 0.048, 0.028, 1.0)
    c_links.new(c_noise.outputs['Fac'], c_ramp.inputs['Fac'])
    c_links.new(c_ramp.outputs['Color'], c_bsdf.inputs['Base Color'])

    c_bsdf.inputs['Metallic'].default_value = 0.0
    c_bsdf.inputs['Roughness'].default_value = 0.92
    c_bsdf.inputs['Sheen Weight'].default_value = 0.0 # disable sheen to prevent desaturation


# Dark Cable Steel Material
mat_cable = bpy.data.materials.get('M_Dark_Winch_Cable')
if not mat_cable:
    mat_cable = bpy.data.materials.new(name='M_Dark_Winch_Cable')
    mat_cable.use_nodes = True
    cb_nodes = mat_cable.node_tree.nodes
    cb_links = mat_cable.node_tree.links
    cb_nodes.clear()
    
    cb_out = cb_nodes.new(type='ShaderNodeOutputMaterial')
    cb_bsdf = cb_nodes.new(type='ShaderNodeBsdfPrincipled')
    cb_links.new(cb_bsdf.outputs['BSDF'], cb_out.inputs['Surface'])
    cb_bsdf.inputs['Base Color'].default_value = (0.06, 0.065, 0.07, 1.0)
    cb_bsdf.inputs['Metallic'].default_value = 0.92
    cb_bsdf.inputs['Roughness'].default_value = 0.40


# =========================================================================
# 2. ASSIGN CORRECT MATERIALS TO ALL OBJECTS
# =========================================================================

# Winch Coils -> Dark Steel Cable
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        if 'Winch_Cable_Coil' in obj.name or 'Chest_Winch_Drum' in obj.name:
            obj.data.materials.clear()
            obj.data.materials.append(mat_cable)

# Fault Maul Parts
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        if 'Maul' in obj.name or 'Fault Maul' in obj.name:
            if any(k in obj.name for k in ['CheekPlate', 'Pommel', 'collar', 'piston', 'ferrule', 'band']):
                obj.data.materials.clear()
                obj.data.materials.append(mat_brass)
            elif 'grip' in obj.name:
                obj.data.materials.clear()
                obj.data.materials.append(mat_cable)
            else: # Head and striking shoes
                obj.data.materials.clear()
                obj.data.materials.append(mat_iron)

# Pelvis & Thigh Armor
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        if any(k in obj.name for k in ['Pelvis', 'Thigh', 'Shin', 'Foot', 'Cleat', 'Tread', 'RollCage', 'Anvil', 'Brow', 'Chest_Armor']):
            if not any(k in obj.name for k in ['Bolt', 'Ring', 'Brooch', 'Plaque_Text', 'Pin']):
                obj.data.materials.clear()
                obj.data.materials.append(mat_iron)




# =========================================================================
# 3. CANONICAL THULAN CROSS EMBLEM RECONSTRUCTION (PANEL 02)
# =========================================================================

# Remove old blocky cross mesh
old_cross = bpy.data.objects.get('Gren_Skildus_Thulan_Cross_Insignia')
if old_cross:
    bpy.data.objects.remove(old_cross, do_unlink=True)

# Build accurate Thulan Cross on the cloth surface
# Cross layout: Central vertical spine + Top short crossbar + Middle wider crossbar + Bottom flared anchor prongs
cross_parts = []

# Main vertical spine
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(0.42, -0.28, 1.48),
    rotation=(0, math.radians(-12), math.radians(-8))
)
spine = bpy.context.active_object
spine.name = "Thulan_Cross_Spine"
spine.scale = (0.010, 0.004, 0.16)
cross_parts.append(spine)

# Top short crossbar
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(0.42, -0.28, 1.54),
    rotation=(0, math.radians(-12), math.radians(-8))
)
bar1 = bpy.context.active_object
bar1.name = "Thulan_Cross_Bar_Top"
bar1.scale = (0.065, 0.004, 0.010)
cross_parts.append(bar1)

# Middle wide crossbar
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(0.42, -0.28, 1.48),
    rotation=(0, math.radians(-12), math.radians(-8))
)
bar2 = bpy.context.active_object
bar2.name = "Thulan_Cross_Bar_Mid"
bar2.scale = (0.095, 0.004, 0.010)
cross_parts.append(bar2)

# Apply transforms, materials, and binding
for p in cross_parts:
    bpy.context.view_layer.objects.active = p
    bpy.ops.object.transform_apply(scale=True)
    if mat_insignia:
        p.data.materials.clear()
        p.data.materials.append(mat_insignia)
    bind_to_bone(p, 'shoulder.L')


# =========================================================================
# 4. SAVE V28 MASTER
# =========================================================================

bpy.ops.wm.save_as_mainfile(filepath=save_blend)
print(f"Successfully generated V28 at {save_blend}")
