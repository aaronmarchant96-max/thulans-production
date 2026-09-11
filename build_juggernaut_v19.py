import bpy
import math
from mathutils import Euler, Quaternion, Vector

source_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-aura-v18.blend'
save_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-juggernaut-v19.blend'

arm = bpy.data.objects.get('Varek simple articulation')

# 1. EXHAUST HEAT TINT MATERIAL
mat_exhaust = bpy.data.materials.new(name="M_Thulan_Exhaust_HeatTint")
mat_exhaust.use_nodes = True
nodes = mat_exhaust.node_tree.nodes
links = mat_exhaust.node_tree.links
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

# Separate Z for vertical heat gradient
sep_xyz = nodes.new(type='ShaderNodeSeparateXYZ')
sep_xyz.location = (-500, 0)
links.new(mapping.outputs['Vector'], sep_xyz.inputs['Vector'])

color_ramp = nodes.new(type='ShaderNodeValToRGB')
color_ramp.location = (-200, 0)
# Gradient: Dark gunmetal base -> straw yellow -> purple -> titanium blue -> soot black tip
color_ramp.color_ramp.elements[0].position = 0.0
color_ramp.color_ramp.elements[0].color = (0.05, 0.05, 0.06, 1.0)
el1 = color_ramp.color_ramp.elements.new(0.35)
el1.color = (0.75, 0.55, 0.15, 1.0) # straw yellow
el2 = color_ramp.color_ramp.elements.new(0.60)
el2.color = (0.45, 0.12, 0.40, 1.0) # heat purple
el3 = color_ramp.color_ramp.elements.new(0.80)
el3.color = (0.08, 0.22, 0.65, 1.0) # titanium blue
color_ramp.color_ramp.elements[-1].position = 1.0
color_ramp.color_ramp.elements[-1].color = (0.02, 0.02, 0.02, 1.0) # carbon soot
links.new(sep_xyz.outputs['Z'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])

bsdf.inputs['Metallic'].default_value = 0.92
bsdf.inputs['Roughness'].default_value = 0.35

for ex_name in ['Exhaust', 'Cooling louvre', 'Cooling louvre.001', 'Cooling louvre.002']:
    obj = bpy.data.objects.get(ex_name)
    if obj:
        if obj.data.materials:
            obj.data.materials[0] = mat_exhaust
        else:
            obj.data.materials.append(mat_exhaust)

# 2. GREN SKILDUS FORGED BRONZE BROOCH / CLASP
clasp_name = "Gren_Skildus_Bronze_Brooch"
clasp_obj = bpy.data.objects.get(clasp_name)
if not clasp_obj:
    # Heavy annular ring
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.042,
        minor_radius=0.012,
        location=(0.48, -0.52, 1.94),
        rotation=(math.radians(45), math.radians(15), math.radians(-20))
    )
    clasp_obj = bpy.context.active_object
    clasp_obj.name = clasp_name
    
    # Transverse locking pin
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.008,
        depth=0.11,
        location=(0.48, -0.52, 1.94),
        rotation=(math.radians(45), math.radians(105), math.radians(-20))
    )
    pin_obj = bpy.context.active_object
    pin_obj.name = "Gren_Skildus_Brooch_Pin"
    
    # Join ring and pin
    bpy.ops.object.select_all(action='DESELECT')
    clasp_obj.select_set(True)
    pin_obj.select_set(True)
    bpy.context.view_layer.objects.active = clasp_obj
    bpy.ops.object.join()

mat_bronze = bpy.data.materials.get('Aged brass')
if clasp_obj and mat_bronze:
    if clasp_obj.data.materials:
        clasp_obj.data.materials[0] = mat_bronze
    else:
        clasp_obj.data.materials.append(mat_bronze)

# Bind clasp to armature bone 'spine'
if clasp_obj and arm:
    vg = clasp_obj.vertex_groups.get('spine')
    if not vg:
        vg = clasp_obj.vertex_groups.new(name='spine')
    vg.add([v.index for v in clasp_obj.data.vertices], 1.0, 'REPLACE')
    
    arm_mod = None
    for m in clasp_obj.modifiers:
        if m.type == 'ARMATURE':
            arm_mod = m
            break
    if not arm_mod:
        arm_mod = clasp_obj.modifiers.new(name='Rigid single bone', type='ARMATURE')
    arm_mod.object = arm

# 3. HYDRAULIC BRAIDED HOSE ON FAULT MAUL
hose_name = "Maul_Braided_Hydraulic_Conduit"
hose_obj = bpy.data.objects.get(hose_name)
if not hose_obj:
    # Create curved conduit line on tool head
    curve_data = bpy.data.curves.new(name=hose_name, type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.014
    curve_data.bevel_resolution = 4
    
    spline = curve_data.splines.new(type='BEZIER')
    spline.bezier_points.add(2)
    # 3 points connecting accumulator to hammer pressure chamber
    p0 = spline.bezier_points[0]
    p0.co = (-0.72, -0.65, 0.42)
    p0.handle_left = (-0.72, -0.65, 0.48)
    p0.handle_right = (-0.72, -0.72, 0.38)
    
    p1 = spline.bezier_points[1]
    p1.co = (-0.68, -0.85, 0.32)
    p1.handle_left = (-0.70, -0.78, 0.35)
    p1.handle_right = (-0.65, -0.92, 0.28)
    
    p2 = spline.bezier_points[2]
    p2.co = (-0.62, -0.92, 0.18)
    p2.handle_left = (-0.64, -0.88, 0.22)
    p2.handle_right = (-0.60, -0.95, 0.14)
    
    hose_obj = bpy.data.objects.new(hose_name, curve_data)
    bpy.context.scene.collection.objects.link(hose_obj)

mat_steel = bpy.data.materials.get('Working piston steel')
if hose_obj and mat_steel:
    if hose_obj.data.materials:
        hose_obj.data.materials[0] = mat_steel
    else:
        hose_obj.data.materials.append(mat_steel)

if hose_obj and arm:
    hose_obj.parent = arm
    hose_obj.parent_type = 'BONE'
    hose_obj.parent_bone = 'tool'

# 4. STRUCTURAL BOLTS / FASTENERS ON CHESTPLATE & YOKE
bolts_name = "Thoracic_Foundry_Rivets"
bolts_obj = bpy.data.objects.get(bolts_name)
if not bolts_obj:
    # Add small hex bolt clusters along the yoke arch
    bolt_coords = [
        (0.28, -0.38, 1.88),
        (-0.28, -0.38, 1.88),
        (0.36, -0.25, 2.08),
        (-0.36, -0.25, 2.08),
        (0.20, -0.45, 1.48),
        (-0.20, -0.45, 1.48),
    ]
    mesh = bpy.data.meshes.new(bolts_name)
    bolts_obj = bpy.data.objects.new(bolts_name, mesh)
    bpy.context.scene.collection.objects.link(bolts_obj)
    
    # Build hex bolt geometry
    for i, c in enumerate(bolt_coords):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=6,
            radius=0.016,
            depth=0.018,
            location=c,
            rotation=(math.radians(90), 0, 0)
        )
        b_sub = bpy.context.active_object
        if i == 0:
            bolts_obj = b_sub
            bolts_obj.name = bolts_name
        else:
            bpy.ops.object.select_all(action='DESELECT')
            bolts_obj.select_set(True)
            b_sub.select_set(True)
            bpy.context.view_layer.objects.active = bolts_obj
            bpy.ops.object.join()

if bolts_obj and mat_bronze:
    if bolts_obj.data.materials:
        bolts_obj.data.materials[0] = mat_bronze
    else:
        bolts_obj.data.materials.append(mat_bronze)

if bolts_obj and arm:
    vg = bolts_obj.vertex_groups.get('spine')
    if not vg:
        vg = bolts_obj.vertex_groups.new(name='spine')
    vg.add([v.index for v in bolts_obj.data.vertices], 1.0, 'REPLACE')
    
    arm_mod = None
    for m in bolts_obj.modifiers:
        if m.type == 'ARMATURE':
            arm_mod = m
            break
    if not arm_mod:
        arm_mod = bolts_obj.modifiers.new(name='Rigid single bone', type='ARMATURE')
    arm_mod.object = arm

# 5. CINEMATIC LIGHTING & COMPOSITOR REFINEMENT
scene = bpy.context.scene
scene.render.filepath = '/home/aaron/animation/thulans-production/assets/art/varek_juggernaut_v19_frame_'

# Save as varek-juggernaut-v19.blend
bpy.ops.wm.save_as_mainfile(filepath=save_blend)
print(f"Successfully created Juggernaut V19 candidate at {save_blend}")
