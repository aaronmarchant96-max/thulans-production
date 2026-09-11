import bpy
import math
import mathutils
from mathutils import Vector, Euler, Quaternion
import os

source_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v31-canonical.blend'
save_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v33-canonical.blend'

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

mat_iron = bpy.data.materials.get('Warm charcoal cast iron')
mat_brass = bpy.data.materials.get('Aged brass')
mat_cloth = bpy.data.materials.get('Cinderback jade paint')
mat_insignia = bpy.data.materials.get('M_Thulan_Insignia_BoneWhite')

# =========================================================================
# 1. PURGE PREVIOUS CLOAK & PLACEHOLDERS
# =========================================================================
for o in list(bpy.data.objects):
    if any(k in o.name for k in ['Thulan_Cross_', 'Gren Skildus', 'Gren_Skildus_Cloak', 'Thulan_Cross_Insignia']):
        bpy.data.objects.remove(o, do_unlink=True)

# =========================================================================
# 2. CANONICAL ORGANIC DRAPED GREN-SKILDUS CLOAK (3D CURVED WRAP)
# =========================================================================
# Authentic draped fabric cowl mesh over the left shoulder covering both front, side and back
rows = 5
cols = 6
verts = []
faces = []

for j in range(rows):
    v = j / (rows - 1)  # 0 top -> 1 bottom
    for i in range(cols):
        u = i / (cols - 1)  # 0 front -> 1 back

        x_inner = 0.40 + 0.12 * v
        x_outer = 0.54 + 0.15 * v
        x = x_inner + (x_outer - x_inner) * u

        y_base = -0.22 * math.cos(math.pi * u)
        front_bulge = -0.06 * math.sin(math.pi * u) * (1.0 - v)
        back_drape = 0.05 * math.sin(math.pi * u) * v
        y = y_base + front_bulge + back_drape

        z = 1.88 - 0.58 * v
        fold = 0.02 * math.sin(u * math.pi * 3.0) * (0.3 + 0.7 * v)
        z += fold

        verts.append((x, y, z))

for j in range(rows - 1):
    for i in range(cols - 1):
        a = j * cols + i
        b = j * cols + (i + 1)
        c = (j + 1) * cols + (i + 1)
        d = (j + 1) * cols + i
        faces.append((a, b, c, d))

mesh = bpy.data.meshes.new(name="Gren_Skildus_Canvas_Cloak")
mesh.from_pydata(verts, [], faces)
mesh.update()

cloth_obj = bpy.data.objects.new("Gren Skildus", mesh)
bpy.context.scene.collection.objects.link(cloth_obj)

for poly in mesh.polygons:
    poly.use_smooth = True

solid = cloth_obj.modifiers.new(name='Thickness', type='SOLIDIFY')
solid.thickness = 0.02
solid.offset = 0.0

subsurf = cloth_obj.modifiers.new(name='Subdivision', type='SUBSURF')
subsurf.levels = 2
subsurf.render_levels = 2

if mat_cloth:
    cloth_obj.data.materials.append(mat_cloth)
bind_to_bone(cloth_obj, 'upper_arm.L')

# Bronze Brooch Pin at Shoulder Crest
brooch = bpy.data.objects.get('Gren_Skildus_Bronze_Brooch')
if not brooch:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.025, location=(0.50, -0.02, 1.86))
    brooch = bpy.context.active_object
    brooch.name = 'Gren_Skildus_Bronze_Brooch'
    if mat_brass:
        brooch.data.materials.append(mat_brass)
else:
    brooch.location = (0.50, -0.02, 1.86)
bind_to_bone(brooch, 'upper_arm.L')

# =========================================================================
# 3. THULAN DOUBLE CROSS INSIGNIA (ON CLOAK FRONT FACE)
# =========================================================================
# Vertical Bar
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.56, -0.22, 1.48))
v_bar = bpy.context.active_object
v_bar.name = "Thulan_Cross_Vertical"
v_bar.scale = (0.018, 0.008, 0.12)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
if mat_insignia:
    v_bar.data.materials.append(mat_insignia)
bind_to_bone(v_bar, 'upper_arm.L')

# Top Cross Bar
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.56, -0.22, 1.51))
t_bar = bpy.context.active_object
t_bar.name = "Thulan_Cross_TopBar"
t_bar.scale = (0.065, 0.008, 0.015)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
if mat_insignia:
    t_bar.data.materials.append(mat_insignia)
bind_to_bone(t_bar, 'upper_arm.L')

# Mid Cross Bar
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.56, -0.22, 1.45))
m_bar = bpy.context.active_object
m_bar.name = "Thulan_Cross_MidBar"
m_bar.scale = (0.09, 0.008, 0.015)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
if mat_insignia:
    m_bar.data.materials.append(mat_insignia)
bind_to_bone(m_bar, 'upper_arm.L')

# =========================================================================
# 4. STRUCTURAL TORSO-PELVIS & SPINE REINFORCEMENTS (SIDE PROFILE FIX)
# =========================================================================
# Heavy Rear Hydraulic Spine Actuators (Dual Cylinders)
for side, sx in [('L', 0.08), ('R', -0.08)]:
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.038,
        depth=0.38,
        location=(sx, -0.12, 1.44),
        rotation=(math.radians(12), 0, 0)
    )
    spine_cyl = bpy.context.active_object
    spine_cyl.name = f"Spine_Hydraulic_Actuator_{side}"
    bpy.ops.object.transform_apply(scale=True)
    if mat_iron:
        spine_cyl.data.materials.append(mat_iron)
    bind_to_bone(spine_cyl, 'spine')

# Lateral Flank Armor Gusset Plates (Bridging Torso Ribs to Pelvis)
for side, sx, b_name in [('L', 0.22, 'spine'), ('R', -0.22, 'spine')]:
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(sx, 0.02, 1.38)
    )
    flank = bpy.context.active_object
    flank.name = f"Flank_Structural_Bridge_{side}"
    flank.scale = (0.06, 0.24, 0.32)
    bpy.ops.object.transform_apply(scale=True)
    if mat_iron:
        flank.data.materials.append(mat_iron)
    bind_to_bone(flank, b_name)

# Pelvic Structural Collar Ring
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.26,
    depth=0.14,
    location=(0.0, 0.0, 1.18)
)
pelvis_collar = bpy.context.active_object
pelvis_collar.name = "Pelvis_Structural_Collar"
bpy.ops.object.transform_apply(scale=True)
if mat_iron:
    pelvis_collar.data.materials.append(mat_iron)
bind_to_bone(pelvis_collar, 'pelvis')

# =========================================================================
# 5. SAVE BLEND
# =========================================================================
bpy.ops.wm.save_as_mainfile(filepath=save_blend)
print(f"V33 successfully built and saved to {save_blend}")

# =========================================================================
# 6. RENDER DIAGNOSTICS (128 SAMPLES CYCLES)
# =========================================================================
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.render.resolution_x = 960
scene.render.resolution_y = 1280
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

# Render Front 3/4
scene.render.filepath = '/home/aaron/animation/thulans-production/assets/art/varek_v33_front34_frame_001.png'
bpy.ops.render.render(write_still=True)

# Render Side Profile View
side_cam = bpy.data.objects.get("Side_Profile_Camera_V33")
if not side_cam:
    side_cam_data = bpy.data.cameras.new(name="Side_Profile_Camera_V33")
    side_cam = bpy.data.objects.new("Side_Profile_Camera_V33", side_cam_data)
    scene.collection.objects.link(side_cam)
    side_cam.location = (4.2, 0.0, 1.4)
    side_cam.rotation_euler = (math.radians(90), 0, math.radians(90))
    side_cam_data.lens = 65.0

scene.camera = side_cam
scene.render.filepath = '/home/aaron/animation/thulans-production/assets/art/varek_v33_side_profile_frame_001.png'
bpy.ops.render.render(write_still=True)

print("V33 Diagnostic Renders completed successfully!")