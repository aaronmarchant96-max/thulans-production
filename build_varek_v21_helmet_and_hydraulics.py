import bpy
import math
from mathutils import Euler, Quaternion, Vector

source_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v20-canonical.blend'
save_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v21-canonical.blend'

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
mat_bronze = bpy.data.materials.get('Aged brass')
mat_steel = bpy.data.materials.get('Working piston steel')
mat_visor = bpy.data.materials.get('Amber visor')

# =========================================================================
# 1. CANONICAL HELMET RECONSTRUCTION (PANEL 01 EXACT BLUEPRINT)
# =========================================================================

# Remove old primitive helmet components if present
for old_name in ['Helmet brow', 'Amber protected slit', 'Visor recessed seat', 'Helmet_Reinforced_Brow', 
                 'Helmet_Respirator_Intake_L', 'Helmet_Respirator_Intake_R', 'Neck_Segmented_Collar_Ring']:
    old_obj = bpy.data.objects.get(old_name)
    if old_obj:
        bpy.data.objects.remove(old_obj, do_unlink=True)
    # Remove old ribs
    for side in ['L', 'R']:
        for r in range(4):
            rib = bpy.data.objects.get(f'Respirator_Rib_{side}_{r}')
            if rib:
                bpy.data.objects.remove(rib, do_unlink=True)

# A. Multi-Faceted Skull Dome (Crown)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=8,
    radius=0.17,
    depth=0.18,
    location=(0.0, -0.08, 2.18),
    rotation=(0, 0, math.radians(22.5))
)
crown = bpy.context.active_object
crown.name = "Helmet_Crown_Octagonal_Dome"
crown.scale = (0.95, 1.10, 0.90)
bpy.ops.object.transform_apply(scale=True)
if mat_iron:
    crown.data.materials.append(mat_iron)
bind_to_bone(crown, 'head')

# Top Crown Vent Hub
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.045,
    depth=0.035,
    location=(0.0, -0.06, 2.27),
    rotation=(0, 0, 0)
)
top_hub = bpy.context.active_object
top_hub.name = "Helmet_Top_Vent_Hub"
if mat_bronze:
    top_hub.data.materials.append(mat_bronze)
bind_to_bone(top_hub, 'head')

# B. Stepped Reinforced Brow Overhang (Panel 01)
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(0.0, -0.22, 2.16),
    rotation=(math.radians(14), 0, 0)
)
brow = bpy.context.active_object
brow.name = "Helmet_Reinforced_Brow_Armor"
brow.scale = (0.29, 0.16, 0.055)
bpy.ops.object.transform_apply(scale=True)
if mat_iron:
    brow.data.materials.append(mat_iron)
bind_to_bone(brow, 'head')

# Brow Bronze Retaining Bolts
for b_x in [-0.11, 0.11]:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=6,
        radius=0.012,
        depth=0.015,
        location=(b_x, -0.29, 2.17),
        rotation=(math.radians(104), 0, 0)
    )
    b_bolt = bpy.context.active_object
    b_bolt.name = f"Helmet_Brow_Bolt_{b_x}"
    if mat_bronze:
        b_bolt.data.materials.append(mat_bronze)
    bind_to_bone(b_bolt, 'head')

# C. Recessed Amber Visor Housing & Optical Slit
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(0.0, -0.21, 2.07),
    rotation=(math.radians(5), 0, 0)
)
visor_recess = bpy.context.active_object
visor_recess.name = "Helmet_Visor_Recessed_Seat"
visor_recess.scale = (0.24, 0.08, 0.07)
bpy.ops.object.transform_apply(scale=True)
if mat_iron:
    visor_recess.data.materials.append(mat_iron)
bind_to_bone(visor_recess, 'head')

# Glowing Amber Slit Core
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(0.0, -0.245, 2.07),
    rotation=(math.radians(5), 0, 0)
)
amber_slit = bpy.context.active_object
amber_slit.name = "Helmet_Amber_Optical_Slit"
amber_slit.scale = (0.20, 0.015, 0.028)
bpy.ops.object.transform_apply(scale=True)
if mat_visor:
    amber_slit.data.materials.append(mat_visor)
bind_to_bone(amber_slit, 'head')

# Internal Horizontal Heat Baffle Vanes (Panel 01)
for v_idx in [-0.008, 0.008]:
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0.0, -0.248, 2.07 + v_idx),
        rotation=(math.radians(5), 0, 0)
    )
    baffle = bpy.context.active_object
    baffle.name = f"Helmet_Visor_Heat_Baffle_{v_idx}"
    baffle.scale = (0.19, 0.008, 0.004)
    bpy.ops.object.transform_apply(scale=True)
    if mat_iron:
        baffle.data.materials.append(mat_iron)
    bind_to_bone(baffle, 'head')

# D. Twin Jaw Respirator Intake Filter Blocks (Panel 01)
for side, x_pos, angle_y in [('L', 0.085, -12), ('R', -0.085, 12)]:
    # Outer housing
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(x_pos, -0.22, 1.94),
        rotation=(math.radians(-5), 0, math.radians(angle_y))
    )
    resp = bpy.context.active_object
    resp.name = f"Helmet_Respirator_Housing_{side}"
    resp.scale = (0.065, 0.095, 0.11)
    bpy.ops.object.transform_apply(scale=True)
    if mat_iron:
        resp.data.materials.append(mat_iron)
    bind_to_bone(resp, 'head')
    
    # 4 Bronze horizontal intake grille louvres
    for l_idx in range(4):
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(x_pos, -0.265, 1.90 + l_idx*0.024),
            rotation=(math.radians(20), 0, math.radians(angle_y))
        )
        louvre = bpy.context.active_object
        louvre.name = f"Helmet_Respirator_Louvre_{side}_{l_idx}"
        louvre.scale = (0.048, 0.012, 0.006)
        bpy.ops.object.transform_apply(scale=True)
        if mat_bronze:
            louvre.data.materials.append(mat_bronze)
        bind_to_bone(louvre, 'head')

# E. Center Jaw Rebreather Anvil Plate
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(0.0, -0.23, 1.92),
    rotation=(math.radians(-8), 0, 0)
)
jaw_center = bpy.context.active_object
jaw_center.name = "Helmet_Jaw_Center_Anvil"
jaw_center.scale = (0.06, 0.08, 0.09)
bpy.ops.object.transform_apply(scale=True)
if mat_iron:
    jaw_center.data.materials.append(mat_iron)
bind_to_bone(jaw_center, 'head')

# F. Beveled Temporal / Cheek Armor Plates
for side, x_pos, rot_z in [('L', 0.16, -25), ('R', -0.16, 25)]:
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(x_pos, -0.12, 2.06),
        rotation=(0, 0, math.radians(rot_z))
    )
    temporal = bpy.context.active_object
    temporal.name = f"Helmet_Temporal_Plate_{side}"
    temporal.scale = (0.045, 0.14, 0.16)
    bpy.ops.object.transform_apply(scale=True)
    if mat_iron:
        temporal.data.materials.append(mat_iron)
    bind_to_bone(temporal, 'head')

# G. Multi-Tier Segmented Neck Seal Bellows
for n_idx in range(3):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.16 - n_idx*0.012,
        minor_radius=0.024,
        location=(0.0, -0.06, 1.84 - n_idx*0.035),
        rotation=(math.radians(8), 0, 0)
    )
    neck_ring = bpy.context.active_object
    neck_ring.name = f"Helmet_Neck_Seal_Ring_{n_idx}"
    if mat_bronze:
        neck_ring.data.materials.append(mat_bronze)
    bind_to_bone(neck_ring, 'head')


# =========================================================================
# 2. PRECISION INDUSTRIAL HYDRAULICS (ELBOWS, KNEES, TRUNNIONS)
# =========================================================================

# A. Elbow Posterior Actuator Rams
for side, arm_bone, x_pos in [('L', 'forearm.L', 0.58), ('R', 'forearm.R', -0.58)]:
    # Barrel
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.024,
        depth=0.14,
        location=(x_pos, 0.08, 1.48),
        rotation=(math.radians(-25), 0, 0)
    )
    e_cyl = bpy.context.active_object
    e_cyl.name = f"Elbow_Hydraulic_Cylinder_{side}"
    if mat_iron:
        e_cyl.data.materials.append(mat_iron)
    bind_to_bone(e_cyl, arm_bone)
    
    # Chrome Piston Rod
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.014,
        depth=0.13,
        location=(x_pos, 0.12, 1.56),
        rotation=(math.radians(-25), 0, 0)
    )
    e_rod = bpy.context.active_object
    e_rod.name = f"Elbow_Hydraulic_Rod_{side}"
    if mat_steel:
        e_rod.data.materials.append(mat_steel)
    bind_to_bone(e_rod, arm_bone)
    
    # Bronze Fluid Port Collar
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.030,
        depth=0.025,
        location=(x_pos, 0.06, 1.43),
        rotation=(math.radians(-25), 0, 0)
    )
    e_port = bpy.context.active_object
    e_port.name = f"Elbow_Hydraulic_Port_{side}"
    if mat_bronze:
        e_port.data.materials.append(mat_bronze)
    bind_to_bone(e_port, arm_bone)

# B. Winch Planetary Gearbox Reduction Drive (Chest Left)
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.082,
    depth=0.08,
    location=(0.23, -0.38, 1.46),
    rotation=(0, math.radians(90), 0)
)
gearbox = bpy.context.active_object
gearbox.name = "Chest_Winch_Planetary_Gearbox"
if mat_iron:
    gearbox.data.materials.append(mat_iron)
bind_to_bone(gearbox, 'spine')

# Gearbox Bolt Flange
for g_idx in range(6):
    angle = g_idx * (2 * math.pi / 6)
    b_y = -0.38 + 0.062 * math.cos(angle)
    b_z = 1.46 + 0.062 * math.sin(angle)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=6,
        radius=0.009,
        depth=0.014,
        location=(0.272, b_y, b_z),
        rotation=(0, math.radians(90), 0)
    )
    g_bolt = bpy.context.active_object
    g_bolt.name = f"Winch_Gearbox_Bolt_{g_idx}"
    if mat_bronze:
        g_bolt.data.materials.append(mat_bronze)
    bind_to_bone(g_bolt, 'spine')

# Save updated candidate V21
bpy.ops.wm.save_as_mainfile(filepath=save_blend)
print(f"Successfully generated Varek Canonical V21 at {save_blend}")
