import bpy
import math
from mathutils import Euler, Quaternion, Vector

source_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v29-canonical.blend'
save_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v30-canonical.blend'

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
# 1. SHOULDER CLOTH (GREN-SKILDUS) SNAPPING & DRAPING TO ACTUAL SHOULDER
# =========================================================================

# Remove disconnected cloth and rebuild draped directly on upper_arm.L / shoulder
old_cloth = bpy.data.objects.get('Gren Skildus')
if old_cloth:
    bpy.data.objects.remove(old_cloth, do_unlink=True)

# Build form-fitting draped shoulder cloth centered on the left shoulder (X=+0.50, Y=0.00, Z=1.75)
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.18,
    depth=0.45,
    vertices=16,
    location=(0.50, 0.00, 1.62),
    rotation=(math.radians(10), math.radians(15), 0)
)
cloth = bpy.context.active_object
cloth.name = "Gren Skildus"
cloth.scale = (1.1, 0.9, 1.0)
bpy.ops.object.transform_apply(scale=True)

# Flatten back and drape front
for v in cloth.data.vertices:
    # Flare hem outward at bottom
    if v.co.z < -0.10:
        v.co.x *= 1.3
        v.co.y *= 1.4
    # Fold ripples
    v.co.y += 0.025 * math.sin(v.co.x * 25.0)

cloth.data.update()
if mat_cloth:
    cloth.data.materials.clear()
    cloth.data.materials.append(mat_cloth)
bind_to_bone(cloth, 'upper_arm.L')

# Re-position Bronze Brooch on top of the cloth on the shoulder
brooch = bpy.data.objects.get('Gren_Skildus_Bronze_Brooch')
if brooch:
    brooch.location = (0.48, -0.05, 1.84)
    bind_to_bone(brooch, 'upper_arm.L')

# Rebuild Thulan Cross directly on the draped cloth face (Y = -0.15)
for name in ['Thulan_Cross_Spine', 'Thulan_Cross_Bar_Top', 'Thulan_Cross_Bar_Mid', 'Thulan_Cross_Prong_0', 'Thulan_Cross_Prong_1', 'Thulan_Cross_Prong_2']:
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

cross_parts = []
# Spine
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(0.51, -0.14, 1.62),
    rotation=(math.radians(10), math.radians(15), 0)
)
c_spine = bpy.context.active_object
c_spine.name = "Thulan_Cross_Spine"
c_spine.scale = (0.010, 0.006, 0.15)
cross_parts.append(c_spine)

# Top bar
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(0.50, -0.14, 1.67),
    rotation=(math.radians(10), math.radians(15), 0)
)
c_bar1 = bpy.context.active_object
c_bar1.name = "Thulan_Cross_Bar_Top"
c_bar1.scale = (0.060, 0.006, 0.010)
cross_parts.append(c_bar1)

# Mid bar
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(0.51, -0.14, 1.62),
    rotation=(math.radians(10), math.radians(15), 0)
)
c_bar2 = bpy.context.active_object
c_bar2.name = "Thulan_Cross_Bar_Mid"
c_bar2.scale = (0.090, 0.006, 0.010)
cross_parts.append(c_bar2)

for p in cross_parts:
    bpy.context.view_layer.objects.active = p
    bpy.ops.object.transform_apply(scale=True)
    if mat_insignia:
        p.data.materials.clear()
        p.data.materials.append(mat_insignia)
    bind_to_bone(p, 'upper_arm.L')


# =========================================================================
# 2. TORSO CHASSIS & ROLL-CAGE STRUCTURAL CONNECTION (CLOSING THE GAP)
# =========================================================================

# Connect the front roll-cage pillars (Y = -0.32) back to the spine/torso frame (Y = +0.10)
for side, x_pos, s_sign in [('L', 0.36, 1.0), ('R', -0.36, -1.0)]:
    # Horizontal Rib Brackets (3 tiers of heavy I-beams connecting front cage to rear chassis)
    for r_idx, z_pos in enumerate([1.50, 1.75, 2.05]):
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(x_pos, -0.12, z_pos),
            rotation=(0, 0, 0)
        )
        rib = bpy.context.active_object
        rib.name = f"Torso_Structural_Rib_{side}_{r_idx}"
        rib.scale = (0.07, 0.42, 0.06)
        bpy.ops.object.transform_apply(scale=True)
        if mat_iron:
            rib.data.materials.append(mat_iron)
        bind_to_bone(rib, 'spine')

    # Flank Armor Plates (closing the side body void completely)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(x_pos - s_sign*0.03, -0.10, 1.65),
        rotation=(0, 0, 0)
    )
    flank = bpy.context.active_object
    flank.name = f"Torso_Side_Flank_Armor_{side}"
    flank.scale = (0.04, 0.36, 0.45)
    bpy.ops.object.transform_apply(scale=True)
    if mat_iron:
        flank.data.materials.append(mat_iron)
    bind_to_bone(flank, 'spine')


# =========================================================================
# 3. KNEE JOINT STRUCTURAL CHASSIS & BEARING CUFFS
# =========================================================================

for side, t_bone, s_bone, x_pos in [('L', 'thigh.L', 'shin.L', 0.24), ('R', 'thigh.R', 'shin.R', -0.24)]:
    # Heavy cylindrical knee knuckle hub (Y = 0.01, Z = 0.65)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.10,
        depth=0.22,
        location=(x_pos, 0.01, 0.65),
        rotation=(0, math.radians(90), 0)
    )
    knee_hub = bpy.context.active_object
    knee_hub.name = f"Knee_Mechanical_Rotary_Hub_{side}"
    bpy.ops.object.transform_apply(scale=True)
    if mat_iron:
        knee_hub.data.materials.append(mat_iron)
    bind_to_bone(knee_hub, t_bone)

    # Bronze Knee Pivot End Cap
    for c_sign in [-1.0, 1.0]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.065,
            depth=0.04,
            location=(x_pos + c_sign*0.12, 0.01, 0.65),
            rotation=(0, math.radians(90), 0)
        )
        k_cap = bpy.context.active_object
        k_cap.name = f"Knee_Pivot_Cap_{side}_{c_sign}"
        bpy.ops.object.transform_apply(scale=True)
        if mat_brass:
            k_cap.data.materials.append(mat_brass)
        bind_to_bone(k_cap, t_bone)

    # Shin structural core connecting knee to foot
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(x_pos, -0.05, 0.45),
        rotation=(0, 0, 0)
    )
    shin_core = bpy.context.active_object
    shin_core.name = f"Shin_Structural_Core_{side}"
    shin_core.scale = (0.18, 0.26, 0.38)
    bpy.ops.object.transform_apply(scale=True)
    if mat_iron:
        shin_core.data.materials.append(mat_iron)
    bind_to_bone(shin_core, s_bone)


# =========================================================================
# 4. HIP SOCKET GIMBALS (CONNECTING PELVIS TO THIGHS)
# =========================================================================

for side, t_bone, x_pos in [('L', 'thigh.L', 0.24), ('R', 'thigh.R', -0.24)]:
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.12,
        depth=0.14,
        location=(x_pos, 0.02, 1.02),
        rotation=(0, math.radians(90), 0)
    )
    hip_gimbal = bpy.context.active_object
    hip_gimbal.name = f"Hip_Gimbal_Housing_{side}"
    bpy.ops.object.transform_apply(scale=True)
    if mat_iron:
        hip_gimbal.data.materials.append(mat_iron)
    bind_to_bone(hip_gimbal, 'pelvis')

bpy.ops.wm.save_as_mainfile(filepath=save_blend)
print(f"Successfully generated V30 Structural Integrity at {save_blend}")
