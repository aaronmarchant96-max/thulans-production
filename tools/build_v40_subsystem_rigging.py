import bpy
import bmesh
from mathutils import Vector, Matrix, Euler
import math

blend_path = '/home/aaron/animation/thulans-production/blender/candidates/varek-v40-osint-juggernaut.blend'
bpy.ops.wm.open_mainfile(filepath=blend_path)
scene = bpy.context.scene

def clean_mesh(obj):
    if not obj or obj.type != 'MESH':
        return
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    wn = next((m for m in obj.modifiers if m.type == 'WEIGHTED_NORMAL'), None)
    if not wn:
        wn = obj.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
        wn.keep_sharp = True

# Materials
mat_iron = bpy.data.materials.get('QA_PBR_Weathered_CastIron')
mat_bronze = bpy.data.materials.get('QA_PBR_Weathered_Bronze')
mat_hose = bpy.data.materials.get('QA_PBR_Braided_HydraulicHose')
mat_steel = bpy.data.materials.get('QA_PBR_Hardened_ToolSteel')

def create_cylinder_mech(name, loc, rot, radius, length, mat):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=radius, radius2=radius, depth=length)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = loc
    obj.rotation_euler = rot
    bpy.context.collection.objects.link(obj)
    clean_mesh(obj)
    if mat:
        obj.data.materials.append(mat)
    return obj

# Remove previous generated objects to avoid duplicates
for o in [obj for obj in bpy.data.objects if obj.name.startswith(('Dorsal_', 'Mech_Thigh_', 'Collar_Conduit_', 'Pelvis_Pivot_Boss_'))]:
    bpy.data.objects.remove(o, do_unlink=True)

# 1. DORSAL HIGH-PRESSURE ACCUMULATOR CYLINDERS (HOLMATRO 720-BAR SURGE PACK)
acc_upper = create_cylinder_mech('Dorsal_Accumulator_Upper', Vector((0.0, -0.36, 1.48)), (0, math.radians(90), 0), radius=0.065, length=0.48, mat=mat_iron)
acc_lower = create_cylinder_mech('Dorsal_Accumulator_Lower', Vector((0.0, -0.36, 1.32)), (0, math.radians(90), 0), radius=0.065, length=0.48, mat=mat_iron)

for acc_name, y_offset, z_offset in [('Upper', -0.36, 1.48), ('Lower', -0.36, 1.32)]:
    for side, sign in [('L', -1), ('R', 1)]:
        cap = create_cylinder_mech(f'Dorsal_Accumulator_Cap_{acc_name}_{side}', Vector((0.245 * sign, y_offset, z_offset)), (0, math.radians(90), 0), radius=0.070, length=0.025, mat=mat_bronze)

# 2. DORSAL THERMAL EXHAUST STACKS
ex_l = create_cylinder_mech('Dorsal_Exhaust_Stack_L', Vector((-0.22, -0.32, 2.05)), (math.radians(-15), math.radians(-10), 0), radius=0.045, length=0.22, mat=mat_iron)
ex_r = create_cylinder_mech('Dorsal_Exhaust_Stack_R', Vector((0.22, -0.32, 2.05)), (math.radians(-15), math.radians(10), 0), radius=0.045, length=0.22, mat=mat_iron)

create_cylinder_mech('Dorsal_Exhaust_Rim_L', Vector((-0.24, -0.35, 2.14)), (math.radians(-15), math.radians(-10), 0), radius=0.052, length=0.03, mat=mat_bronze)
create_cylinder_mech('Dorsal_Exhaust_Rim_R', Vector((0.24, -0.35, 2.14)), (math.radians(-15), math.radians(10), 0), radius=0.052, length=0.03, mat=mat_bronze)

# 3. STRUCTURAL SPINAL LOAD BRIDGE
for i, z_pos in enumerate([1.58, 1.42, 1.26, 1.10]):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.12
        v.co.y *= 0.08
        v.co.z *= 0.05
    me = bpy.data.meshes.new(f'Dorsal_Spine_Link_{i+1}')
    bm.to_mesh(me)
    bm.free()
    spine_obj = bpy.data.objects.new(f'Dorsal_Spine_Link_{i+1}', me)
    spine_obj.location = Vector((0.0, -0.28, z_pos))
    bpy.context.collection.objects.link(spine_obj)
    clean_mesh(spine_obj)
    spine_obj.data.materials.append(mat_iron)

# 4. LATERAL THIGH STRUCTURAL BRACING RODS
for side, sign in [('L', 1), ('R', -1)]:
    rod = create_cylinder_mech(
        f'Mech_Thigh_Bracing_Rod_{side}',
        Vector((0.34 * sign, 0.02, 0.88)),
        (math.radians(10), math.radians(4 * sign), 0),
        radius=0.016,
        length=0.38,
        mat=mat_steel
    )
    create_cylinder_mech(
        f'Mech_Thigh_Bracing_Cap_{side}',
        Vector((0.34 * sign, 0.02, 0.70)),
        (0, math.radians(90), 0),
        radius=0.024,
        length=0.04,
        mat=mat_bronze
    )

# 5. LIFE SUPPORT CONDUITS FRAMING GORGET COLLAR (IMAGE REFERENCE MATCH)
for side, sign in [('L', 1), ('R', -1)]:
    for i, offset_z in enumerate([0.0, 0.04]):
        curve_data = bpy.data.curves.new(name=f'Collar_Conduit_{side}_{i+1}', type='CURVE')
        curve_data.dimensions = '3D'
        curve_data.bevel_depth = 0.014
        curve_data.bevel_resolution = 4
        curve_data.use_fill_caps = True
        spline = curve_data.splines.new(type='BEZIER')
        pts = [
            Vector((0.10 * sign, 0.18, 1.82 + offset_z)),
            Vector((0.18 * sign, 0.16, 1.85 + offset_z)),
            Vector((0.24 * sign, 0.08, 1.88 + offset_z))
        ]
        spline.bezier_points.add(len(pts) - 1)
        for j, pt in enumerate(pts):
            spline.bezier_points[j].co = pt
            spline.bezier_points[j].handle_left_type = 'AUTO'
            spline.bezier_points[j].handle_right_type = 'AUTO'
        obj = bpy.data.objects.new(f'Collar_Conduit_{side}_{i+1}', curve_data)
        bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.convert(target='MESH')
        clean_mesh(obj)
        obj.data.materials.append(mat_hose)

# 6. HEAVY STRUCTURAL PELVIC PIVOT BOSSES (IMAGE REFERENCE MATCH)
for side, sign in [('L', 1), ('R', -1)]:
    create_cylinder_mech(
        f'Pelvis_Pivot_Boss_{side}',
        Vector((0.16 * sign, 0.18, 1.10)),
        (math.radians(90), 0, 0),
        radius=0.038,
        length=0.06,
        mat=mat_bronze
    )

# 7. RIG BINDING
rig = bpy.data.objects.get('Varek_Original_Rig')
if rig:
    for o in bpy.data.objects:
        if o.type == 'MESH':
            if o.name.startswith('Dorsal_') or o.name.startswith('Collar_'):
                if not any(m.type == 'ARMATURE' for m in o.modifiers):
                    mod = o.modifiers.new(name="Armature", type='ARMATURE')
                    mod.object = rig
                    vg = o.vertex_groups.new(name='spine_03')
                    vg.add(range(len(o.data.vertices)), 1.0, 'REPLACE')
            elif o.name.startswith('Pelvis_Pivot_'):
                if not any(m.type == 'ARMATURE' for m in o.modifiers):
                    mod = o.modifiers.new(name="Armature", type='ARMATURE')
                    mod.object = rig
                    vg = o.vertex_groups.new(name='pelvis')
                    vg.add(range(len(o.data.vertices)), 1.0, 'REPLACE')
            elif o.name.startswith('Mech_Thigh_Bracing_'):
                side_str = 'l' if '_L' in o.name else 'r'
                bone_name = f'thigh_{side_str}'
                if not any(m.type == 'ARMATURE' for m in o.modifiers):
                    mod = o.modifiers.new(name="Armature", type='ARMATURE')
                    mod.object = rig
                    vg = o.vertex_groups.new(name=bone_name)
                    vg.add(range(len(o.data.vertices)), 1.0, 'REPLACE')

# 8. KINEMATIC SPECIFICATION LOCK (2.438400m, 0.000000m)
min_z = float('inf')
max_z = float('-inf')
for obj in [o for o in bpy.data.objects if o.type == 'MESH']:
    for corner in [obj.matrix_world @ Vector(c) for c in obj.bound_box]:
        min_z = min(min_z, corner.z)
        max_z = max(max_z, corner.z)

current_height = max_z - min_z
target_height = 2.4384
scale_factor = target_height / current_height

for obj in bpy.data.objects:
    if obj.type in ['MESH', 'ARMATURE']:
        obj.location.x *= scale_factor
        obj.location.y *= scale_factor
        obj.location.z = (obj.location.z - min_z) * scale_factor
        obj.scale *= scale_factor

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)

f_min_z = float('inf')
f_max_z = float('-inf')
for obj in [o for o in bpy.data.objects if o.type == 'MESH']:
    for corner in [obj.matrix_world @ Vector(c) for c in obj.bound_box]:
        f_min_z = min(f_min_z, corner.z)
        f_max_z = max(f_max_z, corner.z)

f_height = f_max_z - f_min_z
print(f"VERIFIED SPEC: Ground Contact = {f_min_z:.6f}m, Top Rim = {f_max_z:.6f}m, Overall Height = {f_height:.6f}m")

bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"SUCCESS: Subsystem Rigging Pass applied to {blend_path}")
