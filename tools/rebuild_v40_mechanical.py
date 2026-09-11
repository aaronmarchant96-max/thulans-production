import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler
from pathlib import Path

blend_path = '/home/aaron/animation/thulans-production/blender/candidates/varek-v40-osint-juggernaut.blend'
bpy.ops.wm.open_mainfile(filepath=blend_path)
scene = bpy.context.scene
arm = bpy.data.objects.get('Varek_Original_Rig') or bpy.data.objects.get('Armature')

# Collections
def get_col(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        scene.collection.children.link(c)
    return c

col_hull = get_col('02_OPERATOR_HULL')
col_frame = get_col('03_LOAD_FRAME')
col_legs = get_col('05_LOWER_CHASSIS')
col_tools = get_col('06_MANIPULATORS')
col_mantle = get_col('08_REGALIA')

# Clean materials
mat_clay = bpy.data.materials.get('QA_Workbench_Clay')
mat_bronze = bpy.data.materials.get('QA_Bronze_Trim')
mat_dark_iron = bpy.data.materials.get('QA_Dark_Iron')

def tag_obj(obj, name, col, mat=mat_clay, driver='spine'):
    obj.name = name
    obj['production_geometry'] = True
    obj['form_importance'] = 'PRIMARY'
    obj['rigid_driver_bone'] = driver
    if mat:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    if obj.name not in col.objects:
        col.objects.link(obj)
    if obj.name in scene.collection.objects:
        scene.collection.objects.unlink(obj)
    for p in obj.data.polygons:
        p.use_smooth = True
    if arm and 'Rigid_Armature' not in obj.modifiers:
        mod = obj.modifiers.new(name='Rigid_Armature', type='ARMATURE')
        mod.object = arm
    return obj

# -----------------------------------------------------------------------------
# 1. MECHANICAL CLEVIS / PIVOT KNUCKLES FOR KNEES & ELBOWS
# -----------------------------------------------------------------------------
# Purge floating bellows
purge_bellows = [o for o in bpy.data.objects if 'Bellows' in o.name]
for o in purge_bellows:
    bpy.data.objects.remove(o, do_unlink=True)

# 1A. KNEE CLEVIS HINGES (Interlocking Cast Clevis Housings)
for side, x_kn in [('L', -0.30), ('R', 0.30)]:
    shin_drv = f'shin.{side}'
    thigh_drv = f'thigh.{side}'

    # Upper Clevis Fork (Anchored to Thigh, extends down over knee pivot)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.155, depth=0.14,
        location=(x_kn, 0.01, 0.62),
        rotation=(0, math.radians(90), 0)
    )
    obj_u_fork = bpy.context.active_object
    mod_uf = obj_u_fork.modifiers.new(name='Bevel', type='BEVEL')
    mod_uf.width = 0.015
    tag_obj(obj_u_fork, f'Mech_Knee_Clevis_UpperFork_{side}', col_legs, mat_clay, driver=thigh_drv)

    # Lower Clevis Tongue (Anchored to Shin, nests inside Upper Fork)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.140, depth=0.18,
        location=(x_kn, 0.01, 0.62),
        rotation=(0, math.radians(90), 0)
    )
    obj_l_tongue = bpy.context.active_object
    mod_lt = obj_l_tongue.modifiers.new(name='Bevel', type='BEVEL')
    mod_lt.width = 0.012
    tag_obj(obj_l_tongue, f'Mech_Knee_Clevis_LowerTongue_{side}', col_legs, mat_clay, driver=shin_drv)

    # Heavy Through-Axle Pivot Pin & Bronze Retention Endcaps
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.042, depth=0.34,
        location=(x_kn, 0.01, 0.62),
        rotation=(0, math.radians(90), 0)
    )
    tag_obj(bpy.context.active_object, f'Mech_Knee_Pivot_Axle_{side}', col_legs, mat_bronze, driver=shin_drv)

    for cap_side, cap_x in [('Out', x_kn + (-0.17 if side=='L' else 0.17)), ('In', x_kn + (0.17 if side=='L' else -0.17))]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.062, depth=0.025,
            location=(cap_x, 0.01, 0.62),
            rotation=(0, math.radians(90), 0)
        )
        tag_obj(bpy.context.active_object, f'Mech_Knee_Axle_Cap_{side}_{cap_side}', col_legs, mat_bronze, driver=shin_drv)

# 1B. ELBOW CLEVIS HINGES (Interlocking Arm Pivot Housings)
for side, x_elb in [('L', -0.68), ('R', 0.68)]:
    uarm_drv = f'upper_arm.{side}'
    farm_drv = f'forearm.{side}'

    # Upper Arm Elbow Hinge Lug
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.125, depth=0.12,
        location=(x_elb, -0.01, 1.30),
        rotation=(0, math.radians(90), 0)
    )
    obj_eh = bpy.context.active_object
    mod_eh = obj_eh.modifiers.new(name='Bevel', type='BEVEL')
    mod_eh.width = 0.012
    tag_obj(obj_eh, f'Mech_Elbow_Hinge_Upper_{side}', col_tools, mat_clay, driver=uarm_drv)

    # Forearm Elbow Clevis Bracket
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.115, depth=0.16,
        location=(x_elb, -0.01, 1.30),
        rotation=(0, math.radians(90), 0)
    )
    obj_ef = bpy.context.active_object
    mod_ef = obj_ef.modifiers.new(name='Bevel', type='BEVEL')
    mod_ef.width = 0.010
    tag_obj(obj_ef, f'Mech_Elbow_Clevis_Lower_{side}', col_tools, mat_clay, driver=farm_drv)

    # Pivot Bolt & Hex Nut
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.035, depth=0.28,
        location=(x_elb, -0.01, 1.30),
        rotation=(0, math.radians(90), 0)
    )
    tag_obj(bpy.context.active_object, f'Mech_Elbow_Pivot_Pin_{side}', col_tools, mat_bronze, driver=farm_drv)

# -----------------------------------------------------------------------------
# 2. FUNCTIONAL MECHANICAL FOREARM TOOLS
# -----------------------------------------------------------------------------
# 2A. ROTARY DRILL: Functional Motor Chassis, Thrust Rails, Chip Flutes, Carbide Teeth
x_drill = 0.71
# Purge old primitive drill bit & flange
purge_drill = [o for o in bpy.data.objects if 'Drill_Bit' in o.name or 'Chucking' in o.name]
for o in purge_drill:
    bpy.data.objects.remove(o, do_unlink=True)

# Heavy Multi-Stage Chucking Hub & Bolted Flange Ring
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.135, depth=0.08,
    location=(x_drill, -0.02, 0.90),
    rotation=(0, 0, 0)
)
obj_c_hub = bpy.context.active_object
mod_ch = obj_c_hub.modifiers.new(name='Bevel', type='BEVEL')
mod_ch.width = 0.012
tag_obj(obj_c_hub, 'Mech_Drill_Chucking_Collar_Master', col_tools, mat_bronze, driver='forearm.R')

# Flange Perimeter Bolt Circle (8 Heavy Hex Bolts)
for b_idx in range(8):
    th = 2.0 * math.pi * b_idx / 8.0
    bx = x_drill + 0.118 * math.cos(th)
    by = -0.02 + 0.118 * math.sin(th)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.010, depth=0.025,
        location=(bx, by, 0.86),
        rotation=(0, 0, 0)
    )
    tag_obj(bpy.context.active_object, f'Mech_Drill_Collar_Bolt_{b_idx+1}', col_tools, mat_dark_iron, driver='forearm.R')

# Multi-Tier Stepped Rotary Boring Head (Authentic OSINT Mining Jumbo Geometry)
# Stage 1: Cylindrical reamer body with spiral chip exhaust flutes
# Stage 2: Conical pilot boring head with tungsten carbide chisel buttons
bm_d = bmesh.new()
# Construct continuous fluted drill bit
d_profile = [
    (0.86, 0.112, 4),  # Base sleeve
    (0.74, 0.108, 4),  # Reamer flutes
    (0.60, 0.088, 3),  # Tapered core
    (0.46, 0.052, 2),  # Pilot cone
    (0.36, 0.012, 1),  # Chisel tip
]
d_rings = []
for z, r, n_flutes in d_profile:
    ring = []
    for i in range(32):
        th = 2.0 * math.pi * i / 32.0
        ang = (0.86 - z) * 8.0 + th
        # Deep spiral flutes for debris clearing
        flute_depth = 0.18 * math.cos(ang * 3.0)
        curr_r = r * (1.0 + flute_depth)
        x = x_drill + curr_r * math.cos(ang)
        y = -0.02 + curr_r * math.sin(ang)
        ring.append(bm_d.verts.new((x, y, z)))
    d_rings.append(ring)

for i in range(len(d_rings) - 1):
    r1, r2 = d_rings[i], d_rings[i+1]
    for j in range(32):
        bm_d.faces.new((r1[j], r1[(j+1)%32], r2[(j+1)%32], r2[j]))

bm_d.faces.new(reversed(d_rings[0]))
bmesh.ops.bevel(bm_d, geom=list(bm_d.edges), offset=0.006, segments=2, affect='EDGES')
me_d = bpy.data.meshes.new('Mech_Drill_MultiFlute_Bit_Mesh')
bm_d.to_mesh(me_d)
bm_d.free()
obj_d = bpy.data.objects.new('Mech_Drill_MultiFlute_Bit', me_d)
scene.collection.objects.link(obj_d)
mod_ds = obj_d.modifiers.new(name='Subsurf', type='SUBSURF')
mod_ds.levels = 1
tag_obj(obj_d, 'Mech_Drill_MultiFlute_Bit', col_tools, mat_dark_iron, driver='forearm.R')

# Tungsten Carbide Button Teeth (Welded along spiral cutting ridges)
for b_idx in range(12):
    z_btn = 0.82 - b_idx * 0.038
    ang_btn = (0.86 - z_btn) * 8.0 + (b_idx % 3) * (2.0 * math.pi / 3.0)
    r_btn = 0.105 * (z_btn - 0.34) / 0.52
    bx = x_drill + r_btn * math.cos(ang_btn)
    by = -0.02 + r_btn * math.sin(ang_btn)
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.014,
        location=(bx, by, z_btn)
    )
    tag_obj(bpy.context.active_object, f'Mech_Drill_Carbide_Tooth_{b_idx+1}', col_tools, mat_bronze, driver='forearm.R')

# 2B. RESCUE SHEARS: Mechanical Pivot Knuckle, Dual Actuator Rams, Serrated Blades
x_shear = -0.71
# Purge old primitive shear blades
purge_shears = [o for o in bpy.data.objects if 'Shear_Blade' in o.name or 'Shear_Mounting' in o.name]
for o in purge_shears:
    bpy.data.objects.remove(o, do_unlink=True)

# Heavy Forged Clevis Hub (Houses central Grade-8 pivot bolt)
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.135, depth=0.10,
    location=(x_shear, -0.02, 0.90),
    rotation=(0, 0, 0)
)
tag_obj(bpy.context.active_object, 'Mech_Shear_Base_Flange', col_tools, mat_bronze, driver='forearm.L')

# Central Hardened Pivot Boss (Traverses horizontally through blade tangs)
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.085, depth=0.16,
    location=(x_shear, -0.02, 0.82),
    rotation=(math.radians(90), 0, 0)
)
tag_obj(bpy.context.active_object, 'Mech_Shear_Central_Pivot_Bolt', col_tools, mat_dark_iron, driver='forearm.L')

# Authentic Curved Bypass Demolition Blades with Serrated Crushing Notches
for jaw_name, dy_offset, rot_deg in [('Upper', 0.038, 14), ('Lower', -0.038, -16)]:
    bm_jaw = bmesh.new()
    # Profile: Base tang -> Pivot eye -> Curved shearing beak -> Serrated throat notch
    jaw_pts = [
        # Tang connection to hydraulic ram
        (x_shear - 0.08, -0.02 + dy_offset * 1.5, 0.92), (x_shear + 0.02, -0.02 + dy_offset * 1.5, 0.92),
        # Pivot hub envelope
        (x_shear - 0.06, -0.02 + dy_offset, 0.82),       (x_shear + 0.06, -0.02 + dy_offset, 0.82),
        # Mid cutting edge with stepped notch
        (x_shear - 0.04, -0.02 + dy_offset * 0.8, 0.68), (x_shear + 0.04, -0.02 + dy_offset * 0.8, 0.68),
        # Incurved piercing beak
        (x_shear - 0.02, -0.02 + (-0.04 if jaw_name=='Upper' else 0.04), 0.52),
        (x_shear + 0.02, -0.02 + (-0.04 if jaw_name=='Upper' else 0.04), 0.52)
    ]
    v_j = [bm_jaw.verts.new(pt) for pt in jaw_pts]
    for row in range(3):
        i0 = row * 2
        bm_jaw.faces.new((v_j[i0], v_j[i0+1], v_j[i0+3], v_j[i0+2]))

    bmesh.ops.solidify(bm_jaw, geom=list(bm_jaw.faces), thickness=0.045)
    bmesh.ops.bevel(bm_jaw, geom=list(bm_jaw.edges), offset=0.008, segments=2, affect='EDGES')
    me_jaw = bpy.data.meshes.new(f'Mech_Shear_Blade_{jaw_name}_Mesh')
    bm_jaw.to_mesh(me_jaw)
    bm_jaw.free()
    obj_jaw = bpy.data.objects.new(f'Mech_Shear_Blade_{jaw_name}', me_jaw)
    scene.collection.objects.link(obj_jaw)
    mod_js = obj_jaw.modifiers.new(name='Subsurf', type='SUBSURF')
    mod_js.levels = 1
    tag_obj(obj_jaw, f'Mech_Shear_Blade_{jaw_name}', col_tools, mat_clay, driver='forearm.L')

    # Dual Hydraulic Actuator Ram Pushrods (Connecting forearm cylinders to blade tangs)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.022, depth=0.24,
        location=(x_shear - 0.08, -0.02 + dy_offset * 1.5, 1.04),
        rotation=(0, 0, 0)
    )
    tag_obj(bpy.context.active_object, f'Mech_Shear_Actuator_Pushrod_{jaw_name}', col_tools, mat_bronze, driver='forearm.L')

# -----------------------------------------------------------------------------
# 3. SAVE PRODUCTION MECHANICAL MODEL
# -----------------------------------------------------------------------------
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"SUCCESS: Rebuilt Mechanical Interlocking Varek V40 saved to {blend_path}")

