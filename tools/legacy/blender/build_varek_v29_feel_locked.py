import bpy
import math

source_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v28-canonical.blend'
save_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v29-canonical.blend'

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

mat_insignia = bpy.data.materials.get('M_Thulan_Insignia_BoneWhite')

# Remove any old cross objects
for name in ['Thulan_Cross_Spine', 'Thulan_Cross_Bar_Top', 'Thulan_Cross_Bar_Mid', 'Gren_Skildus_Thulan_Cross_Insignia']:
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

# Rebuild Thulan Cross clearly on front surface of Gren-Skildus cloth
# Panel 02 reference: Double crossbar anchor cross
cross_parts = []

# Main vertical spine
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(0.44, -0.36, 1.32),
    rotation=(math.radians(4), math.radians(-14), math.radians(-12))
)
spine = bpy.context.active_object
spine.name = "Thulan_Cross_Spine"
spine.scale = (0.012, 0.008, 0.16)
cross_parts.append(spine)

# Top short crossbar
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(0.43, -0.36, 1.37),
    rotation=(math.radians(4), math.radians(-14), math.radians(-12))
)
bar1 = bpy.context.active_object
bar1.name = "Thulan_Cross_Bar_Top"
bar1.scale = (0.065, 0.008, 0.012)
cross_parts.append(bar1)

# Middle wide crossbar
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(0.44, -0.36, 1.32),
    rotation=(math.radians(4), math.radians(-14), math.radians(-12))
)
bar2 = bpy.context.active_object
bar2.name = "Thulan_Cross_Bar_Mid"
bar2.scale = (0.095, 0.008, 0.012)
cross_parts.append(bar2)

# Bottom 3 flared anchor prongs
for p_idx, p_x in enumerate([-0.035, 0.0, 0.035]):
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0.45 + p_x*0.8, -0.36, 1.22),
        rotation=(math.radians(4), math.radians(-14), math.radians(-12))
    )
    prong = bpy.context.active_object
    prong.name = f"Thulan_Cross_Prong_{p_idx}"
    prong.scale = (0.010, 0.008, 0.030)
    cross_parts.append(prong)

for p in cross_parts:
    bpy.context.view_layer.objects.active = p
    bpy.ops.object.transform_apply(scale=True)
    if mat_insignia:
        p.data.materials.clear()
        p.data.materials.append(mat_insignia)
    bind_to_bone(p, 'shoulder.L')

# Re-darken the Pelvis center arch casting
pelvis = bpy.data.objects.get('Pelvis')
mat_iron = bpy.data.materials.get('Warm charcoal cast iron')
if pelvis and mat_iron:
    pelvis.data.materials.clear()
    pelvis.data.materials.append(mat_iron)

bpy.ops.wm.save_as_mainfile(filepath=save_blend)
print(f"Successfully generated V29 at {save_blend}")
