import bpy
import math
from mathutils import Euler, Quaternion, Vector

source_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v22-materials.blend'
save_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v23-cloth.blend'

bpy.ops.wm.open_mainfile(filepath=source_blend)
arm = bpy.data.objects['Varek simple articulation']

# 1. REMOVE OLD RIGID SKILDUS MESH
old_skildus = bpy.data.objects.get('Gren Skildus')
if old_skildus:
    bpy.data.objects.remove(old_skildus, do_unlink=True)

# 2. GENERATE DRAPED CLOTH MESH WITH ORGANIC FOLDS
# Create a subdivided grid with natural gravity drape and gathering ripples
rows = 32
cols = 24

verts = []
faces = []

width = 0.44  # X span
height = 0.48 # Z span

for r in range(rows):
    v_norm = r / (rows - 1) # 0 at top, 1 at bottom
    z = 1.94 - v_norm * height
    
    # Gather factor: narrow at top gather point, wider at bottom hem
    width_factor = 0.35 + 0.65 * math.sqrt(v_norm)
    
    for c in range(cols):
        u_norm = (c / (cols - 1)) - 0.5 # -0.5 to 0.5
        
        # Base X around left shoulder (0.48)
        x = 0.48 + u_norm * width * width_factor
        
        # Y drape contour over shoulder curve (curves outward over shoulder then drapes down)
        # Add organic cloth ripple folds (catenary wave)
        fold_wave = 0.022 * math.sin(u_norm * math.pi * 4.5) * math.sin(v_norm * math.pi * 1.2 + 0.3)
        secondary_wave = 0.012 * math.cos(u_norm * math.pi * 7.0 + 0.5) * v_norm
        
        # Shoulder curvature sag
        shoulder_arch = -0.055 * math.cos(u_norm * math.pi)
        y = -0.42 + shoulder_arch - 0.06 * (1.0 - math.exp(-v_norm * 3.0)) + fold_wave + secondary_wave
        
        # Tattered / frayed bottom edge variation
        if r == rows - 1:
            z += 0.018 * math.sin(c * 2.8) + 0.012 * math.cos(c * 5.4)
            y += 0.008 * math.sin(c * 3.2)
        elif r == rows - 2:
            z += 0.006 * math.sin(c * 2.8)
            
        verts.append((x, y, z))

for r in range(rows - 1):
    for c in range(cols - 1):
        i0 = r * cols + c
        i1 = r * cols + (c + 1)
        i2 = (r + 1) * cols + (c + 1)
        i3 = (r + 1) * cols + c
        faces.append((i0, i1, i2, i3))

mesh = bpy.data.meshes.new("Gren_Skildus_Cloth_Mesh")
mesh.from_pydata(verts, [], faces)
mesh.update()

# Calculate smooth normals
for poly in mesh.polygons:
    poly.use_smooth = True

cloth_obj = bpy.data.objects.new("Gren Skildus", mesh)
bpy.context.scene.collection.objects.link(cloth_obj)

# Add Solidify modifier for realistic heavy wool canvas thickness (2mm)
sol_mod = cloth_obj.modifiers.new(name="Cloth_Thickness", type='SOLIDIFY')
sol_mod.thickness = 0.004
sol_mod.offset = 0.0

# Add Subdivision surface for silk-smooth fold curves
sub_mod = cloth_obj.modifiers.new(name="Cloth_Subsurf", type='SUBSURF')
sub_mod.levels = 1
sub_mod.render_levels = 2

# 3. 3D EMBOSSED THULAN CROSS INSIGNIA ON CLOTH
# Vertical spine of cross
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.48, -0.485, 1.76), rotation=(0, 0, 0))
c_vert = bpy.context.active_object
c_vert.name = "Gren_Skildus_Cross_Vertical"
c_vert.scale = (0.018, 0.008, 0.16)
bpy.ops.object.transform_apply(scale=True)

# Upper crossbar
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.48, -0.485, 1.80), rotation=(0, 0, 0))
c_h1 = bpy.context.active_object
c_h1.name = "Gren_Skildus_Cross_UpperBar"
c_h1.scale = (0.08, 0.008, 0.016)
bpy.ops.object.transform_apply(scale=True)

# Lower crossbar
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.48, -0.485, 1.74), rotation=(0, 0, 0))
c_h2 = bpy.context.active_object
c_h2.name = "Gren_Skildus_Cross_LowerBar"
c_h2.scale = (0.055, 0.008, 0.014)
bpy.ops.object.transform_apply(scale=True)

# Stamped bone-white material
mat_insignia = bpy.data.materials.new(name="M_Thulan_Insignia_BoneWhite")
mat_insignia.use_nodes = True
nodes = mat_insignia.node_tree.nodes
links = mat_insignia.node_tree.links
nodes.clear()

out_node = nodes.new(type='ShaderNodeOutputMaterial')
bsdf_ins = nodes.new(type='ShaderNodeBsdfPrincipled')
links.new(bsdf_ins.outputs['BSDF'], out_node.inputs['Surface'])
bsdf_ins.inputs['Base Color'].default_value = (0.72, 0.69, 0.62, 1.0) # weathered bone white
bsdf_ins.inputs['Roughness'].default_value = 0.90
bsdf_ins.inputs['Metallic'].default_value = 0.0

for c_part in [c_vert, c_h1, c_h2]:
    c_part.data.materials.append(mat_insignia)

# Join cross parts into one insignia mesh
bpy.ops.object.select_all(action='DESELECT')
c_vert.select_set(True)
c_h1.select_set(True)
c_h2.select_set(True)
bpy.context.view_layer.objects.active = c_vert
bpy.ops.object.join()
cross_obj = c_vert
cross_obj.name = "Gren_Skildus_Thulan_Cross_Insignia"

# 4. HEAVY FIELD-GREEN CANVAS MATERIAL
mat_cloth = bpy.data.materials.get('Cinderback jade paint')
if not mat_cloth:
    mat_cloth = bpy.data.materials.new(name='Cinderback jade paint')

mat_cloth.use_nodes = True
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

# Coarse wool/canvas weave
wave_x = nodes.new(type='ShaderNodeTexWave')
wave_x.location = (-600, 200)
wave_x.inputs['Scale'].default_value = 260.0
wave_x.inputs['Distortion'].default_value = 1.8
links.new(mapping.outputs['Vector'], wave_x.inputs['Vector'])

wave_y = nodes.new(type='ShaderNodeTexWave')
wave_y.location = (-600, 0)
wave_y.wave_type = 'BANDS'
wave_y.bands_direction = 'Y'
wave_y.inputs['Scale'].default_value = 260.0
wave_y.inputs['Distortion'].default_value = 1.8
links.new(mapping.outputs['Vector'], wave_y.inputs['Vector'])

mix_weave = nodes.new(type='ShaderNodeMix')
mix_weave.data_type = 'FLOAT'
mix_weave.blend_type = 'ADD'
mix_weave.location = (-350, 100)
mix_weave.inputs['Factor'].default_value = 0.5
links.new(wave_x.outputs['Color'], mix_weave.inputs['A'])
links.new(wave_y.outputs['Color'], mix_weave.inputs['B'])

bump = nodes.new(type='ShaderNodeBump')
bump.location = (200, -100)
bump.inputs['Strength'].default_value = 0.18
bump.inputs['Distance'].default_value = 0.0025
links.new(mix_weave.outputs['Result'], bump.inputs['Height'])
links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

# Weathered Thulan Sage/Field-Green (Panel 02)
bsdf.inputs['Base Color'].default_value = (0.042, 0.088, 0.052, 1.0)
bsdf.inputs['Roughness'].default_value = 0.92
bsdf.inputs['Metallic'].default_value = 0.0
bsdf.inputs['Sheen Weight'].default_value = 0.85
bsdf.inputs['Sheen Tint'].default_value = (0.12, 0.28, 0.15, 1.0)

cloth_obj.data.materials.append(mat_cloth)

# 5. BIND CLOTH & EMBOSSED INSIGNIA TO ARMATURE
for obj in [cloth_obj, cross_obj]:
    vg = obj.vertex_groups.get('spine')
    if not vg:
        vg = obj.vertex_groups.new(name='spine')
    vg.add([v.index for v in obj.data.vertices], 1.0, 'REPLACE')
    
    arm_mod = obj.modifiers.new(name='Rigid single bone', type='ARMATURE')
    arm_mod.object = arm

# Update brooch location to clasp top of cloth
brooch = bpy.data.objects.get('Gren_Skildus_Bronze_Brooch')
if brooch:
    brooch.location = (0.48, -0.44, 1.95)

# Save candidate V23
bpy.context.scene.render.filepath = '/home/aaron/animation/thulans-production/assets/art/varek_v23_cloth_frame_'
bpy.ops.wm.save_as_mainfile(filepath=save_blend)
print(f"Successfully created Varek Canonical V23 with draped cloth at {save_blend}")
