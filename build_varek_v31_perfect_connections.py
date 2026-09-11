import bpy
import math
from mathutils import Euler, Quaternion, Vector

source_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v30-canonical.blend'
save_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v31-canonical.blend'

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
# 1. PURGE ALL ORPHANED / FLOATING FRAGMENTS
# =========================================================================

for o in list(bpy.data.objects):
    if any(k in o.name for k in ['Thulan_Cross_', 'Gren Skildus']):
        bpy.data.objects.remove(o, do_unlink=True)


# =========================================================================
# 2. CANONICAL ORGANIC DRAPED GREN-SKILDUS CLOAK (PANEL 02)
# =========================================================================

# Build an authentic draped fabric cowl mesh over the left shoulder
verts = [
    # Top pin at brooch
    (0.48, -0.04, 1.84),
    (0.44, +0.06, 1.84),
    (0.54, +0.04, 1.83),
    # Mid shoulder wrap
    (0.42, -0.16, 1.68),
    (0.58, -0.12, 1.66),
    (0.62, +0.08, 1.66),
    (0.44, +0.16, 1.68),
    # Lower drape fold
    (0.38, -0.22, 1.48),
    (0.52, -0.20, 1.46),
    (0.66, -0.06, 1.46),
    (0.62, +0.18, 1.48),
    # Bottom ragged hem
    (0.36, -0.26, 1.28),
    (0.48, -0.25, 1.25),
    (0.58, -0.22, 1.26),
    (0.68, -0.12, 1.26),
    (0.64, +0.14, 1.28)
]

faces = [
    (0, 1, 6, 3), (0, 3, 4, 2), (2, 4, 5, 1),
    (3, 4, 8, 7), (4, 5, 9, 8), (5, 6, 10, 9),
    (7, 8, 12, 11), (8, 9, 13, 12), (9, 14, 13, 8), (9, 10, 15, 14)
]

mesh = bpy.data.meshes.new(name="Gren_Skildus_Canvas_Cloak")
mesh.from_pydata(verts, [], faces)
mesh.update()

cloth_obj = bpy.data.objects.new("Gren Skildus", mesh)
bpy.context.scene.collection.objects.link(cloth_obj)

# Add Solidify modifier for heavy canvas thickness + Subdivision
solid = cloth_obj.modifiers.new(name='Thickness', type='SOLIDIFY')
solid.thickness = 0.012

subsurf = cloth_obj.modifiers.new(name='Subdivision', type='SUBSURF')
subsurf.levels = 2
subsurf.render_levels = 2

if mat_cloth:
    cloth_obj.data.materials.append(mat_cloth)
bind_to_bone(cloth_obj, 'upper_arm.L')

# Bronze Brooch Pin
brooch = bpy.data.objects.get('Gren_Skildus_Bronze_Brooch')
if brooch:
    brooch.location = (0.47, -0.02, 1.84)
    brooch.rotation_euler = (math.radians(20), math.radians(10), 0)
    bind_to_bone(brooch, 'upper_arm.L')


# =========================================================================
# 3. EMBEDDED THULAN CROSS EMBLEM ON DRAPED CLOTH FRONT
# =========================================================================

cross_parts = []
# Vertical spine
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(0.47, -0.21, 1.48),
    rotation=(math.radians(18), math.radians(8), math.radians(-5))
)
c_spine = bpy.context.active_object
c_spine.name = "Thulan_Cross_Spine"
c_spine.scale = (0.010, 0.004, 0.16)
cross_parts.append(c_spine)

# Top Bar
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(0.46, -0.20, 1.54),
    rotation=(math.radians(18), math.radians(8), math.radians(-5))
)
c_bar1 = bpy.context.active_object
c_bar1.name = "Thulan_Cross_Bar_Top"
c_bar1.scale = (0.055, 0.004, 0.010)
cross_parts.append(c_bar1)

# Mid Bar
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(0.47, -0.21, 1.48),
    rotation=(math.radians(18), math.radians(8), math.radians(-5))
)
c_bar2 = bpy.context.active_object
c_bar2.name = "Thulan_Cross_Bar_Mid"
c_bar2.scale = (0.085, 0.004, 0.010)
cross_parts.append(c_bar2)

for p in cross_parts:
    bpy.context.view_layer.objects.active = p
    bpy.ops.object.transform_apply(scale=True)
    if mat_insignia:
        p.data.materials.clear()
        p.data.materials.append(mat_insignia)
    bind_to_bone(p, 'upper_arm.L')


# =========================================================================
# 4. REAR SHIN HYDRAULIC STRUTS & ANKLE CLEVIS ALIGNMENT
# =========================================================================

for side, s_bone, f_bone, x_pos in [('L', 'shin.L', 'foot.L', 0.24), ('R', 'shin.R', 'foot.R', -0.24)]:
    # Rear Knee-to-Heel Heavy Hydraulic Strut
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.038,
        depth=0.28,
        location=(x_pos, 0.16, 0.44),
        rotation=(math.radians(-22), 0, 0)
    )
    piston_cyl = bpy.context.active_object
    piston_cyl.name = f"Rear_Shin_Piston_Cylinder_{side}"
    bpy.ops.object.transform_apply(scale=True)
    if mat_iron:
        piston_cyl.data.materials.append(mat_iron)
    bind_to_bone(piston_cyl, s_bone)

    # Hydraulic Rod entering Heel Mount
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.022,
        depth=0.22,
        location=(x_pos, 0.19, 0.28),
        rotation=(math.radians(-22), 0, 0)
    )
    piston_rod = bpy.context.active_object
    piston_rod.name = f"Rear_Shin_Piston_Rod_{side}"
    bpy.ops.object.transform_apply(scale=True)
    if mat_brass:
        piston_rod.data.materials.append(mat_brass)
    bind_to_bone(piston_rod, f_bone)

    # Heel Ankle Clevis Bracket
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(x_pos, 0.22, 0.18),
        rotation=(0, 0, 0)
    )
    clevis_mount = bpy.context.active_object
    clevis_mount.name = f"Heel_Ankle_Clevis_Mount_{side}"
    clevis_mount.scale = (0.08, 0.08, 0.10)
    bpy.ops.object.transform_apply(scale=True)
    if mat_iron:
        clevis_mount.data.materials.append(mat_iron)
    bind_to_bone(clevis_mount, f_bone)

bpy.ops.wm.save_as_mainfile(filepath=save_blend)
print(f"Successfully generated V31 Perfect Connections at {save_blend}")
