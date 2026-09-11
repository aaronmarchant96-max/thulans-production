import bpy
import math
from mathutils import Euler, Quaternion, Vector

source_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v23-cloth.blend'
save_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v23-cloth.blend'

bpy.ops.wm.open_mainfile(filepath=source_blend)
arm = bpy.data.objects['Varek simple articulation']

# Remove previous cloth & cross objects
for name in ['Gren Skildus', 'Gren_Skildus_Thulan_Cross_Insignia', 'Gren_Skildus_Cross_Vertical', 'Gren_Skildus_Cross_UpperBar', 'Gren_Skildus_Cross_LowerBar']:
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

# Generate Broad Heavy Draped Shoulder Cloak (Panel 02 Spec)
rows = 36
cols = 28

verts = []
faces = []

width = 0.68  # Wide shoulder & upper arm coverage
height = 0.62 # Longer hanging drape

for r in range(rows):
    v_norm = r / (rows - 1) # 0 at top gather, 1 at bottom frayed hem
    z = 1.98 - v_norm * height
    
    # Gathering contour: narrow at top pin, spreads wide over shoulder curve, then hangs down
    width_factor = 0.32 + 0.68 * math.pow(v_norm, 0.45)
    
    for c in range(cols):
        u_norm = (c / (cols - 1)) - 0.5 # -0.5 (inner chest) to +0.5 (outer shoulder/arm)
        
        # Center X over left shoulder (0.54)
        x = 0.54 + u_norm * width * width_factor
        
        # Organic cloth ripple folds
        fold1 = 0.035 * math.sin(u_norm * math.pi * 5.0) * math.sin(v_norm * math.pi * 1.1 + 0.2)
        fold2 = 0.018 * math.cos(u_norm * math.pi * 9.0 + 0.6) * math.sqrt(v_norm)
        
        # Shoulder curvature wrapping (curves forward over chest and back over dorsal rail)
        shoulder_arch = -0.09 * math.cos(u_norm * math.pi * 0.9)
        forward_sag = -0.08 * (1.0 - math.exp(-v_norm * 2.8))
        
        y = -0.38 + shoulder_arch + forward_sag + fold1 + fold2
        
        # Tattered / ragged frayed hem
        if r == rows - 1:
            z += 0.024 * math.sin(c * 3.1) + 0.015 * math.cos(c * 6.2)
            y += 0.010 * math.sin(c * 3.8)
        elif r == rows - 2:
            z += 0.008 * math.sin(c * 3.1)
            
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

for poly in mesh.polygons:
    poly.use_smooth = True

cloth_obj = bpy.data.objects.new("Gren Skildus", mesh)
bpy.context.scene.collection.objects.link(cloth_obj)

sol_mod = cloth_obj.modifiers.new(name="Cloth_Thickness", type='SOLIDIFY')
sol_mod.thickness = 0.0045
sol_mod.offset = 0.0

sub_mod = cloth_obj.modifiers.new(name="Cloth_Subsurf", type='SUBSURF')
sub_mod.levels = 1
sub_mod.render_levels = 2

# Apply Canvas Material
mat_cloth = bpy.data.materials.get('Cinderback jade paint')
if cloth_obj and mat_cloth:
    cloth_obj.data.materials.append(mat_cloth)

# Embossed Bone-White Thulan Cross on Front Fold
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.52, -0.53, 1.72), rotation=(math.radians(8), 0, math.radians(-10)))
c_vert = bpy.context.active_object
c_vert.name = "Gren_Skildus_Cross_Vertical"
c_vert.scale = (0.024, 0.012, 0.22)
bpy.ops.object.transform_apply(scale=True)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.52, -0.53, 1.78), rotation=(math.radians(8), 0, math.radians(-10)))
c_h1 = bpy.context.active_object
c_h1.name = "Gren_Skildus_Cross_UpperBar"
c_h1.scale = (0.11, 0.012, 0.022)
bpy.ops.object.transform_apply(scale=True)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.52, -0.53, 1.70), rotation=(math.radians(8), 0, math.radians(-10)))
c_h2 = bpy.context.active_object
c_h2.name = "Gren_Skildus_Cross_LowerBar"
c_h2.scale = (0.08, 0.012, 0.018)
bpy.ops.object.transform_apply(scale=True)

mat_insignia = bpy.data.materials.get('M_Thulan_Insignia_BoneWhite')
if not mat_insignia:
    mat_insignia = bpy.data.materials.new(name="M_Thulan_Insignia_BoneWhite")
    mat_insignia.use_nodes = True
    nodes = mat_insignia.node_tree.nodes
    links = mat_insignia.node_tree.links
    nodes.clear()
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = (0.75, 0.72, 0.65, 1.0) # bone white
    bsdf.inputs['Roughness'].default_value = 0.90

for c_part in [c_vert, c_h1, c_h2]:
    c_part.data.materials.append(mat_insignia)

bpy.ops.object.select_all(action='DESELECT')
c_vert.select_set(True)
c_h1.select_set(True)
c_h2.select_set(True)
bpy.context.view_layer.objects.active = c_vert
bpy.ops.object.join()
cross_obj = c_vert
cross_obj.name = "Gren_Skildus_Thulan_Cross_Insignia"

# Bind to armature
for obj in [cloth_obj, cross_obj]:
    vg = obj.vertex_groups.get('spine')
    if not vg:
        vg = obj.vertex_groups.new(name='spine')
    vg.add([v.index for v in obj.data.vertices], 1.0, 'REPLACE')
    
    arm_mod = obj.modifiers.new(name='Rigid single bone', type='ARMATURE')
    arm_mod.object = arm

# Reposition Bronze Brooch to top gather point
brooch = bpy.data.objects.get('Gren_Skildus_Bronze_Brooch')
if brooch:
    brooch.location = (0.52, -0.42, 1.97)

bpy.ops.wm.save_as_mainfile(filepath=save_blend)
print("Successfully generated broad canonical shoulder cloth!")
