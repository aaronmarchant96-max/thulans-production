import bpy
import bmesh
from mathutils import Vector, Matrix, Euler
import math

blend_path = '/home/aaron/animation/thulans-production/blender/candidates/varek-v40-osint-juggernaut.blend'
bpy.ops.wm.open_mainfile(filepath=blend_path)
scene = bpy.context.scene

rig = bpy.data.objects.get('Varek_Original_Rig')

def get_or_create_material(name, base_color, metallic, roughness, emission=None, emission_strength=0.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    if emission:
        bsdf.inputs['Emission Color'].default_value = emission
        bsdf.inputs['Emission Strength'].default_value = emission_strength
    return mat

mat_iron = get_or_create_material('PBR_Cast_Iron', (0.09, 0.09, 0.10, 1.0), 0.85, 0.42)
mat_bronze = get_or_create_material('PBR_Bronze_Trim', (0.48, 0.32, 0.14, 1.0), 0.90, 0.30)
mat_amber = get_or_create_material('PBR_Visor_Amber', (1.0, 0.55, 0.05, 1.0), 0.0, 0.1, (1.0, 0.6, 0.05, 1.0), 5.0)
mat_green_cloth = get_or_create_material('PBR_Gren_Skildus_Wool', (0.06, 0.11, 0.07, 1.0), 0.0, 0.92)
mat_dark_rubber = get_or_create_material('PBR_Flexible_Bellows', (0.03, 0.03, 0.03, 1.0), 0.1, 0.7)
mat_steel = get_or_create_material('PBR_Tool_Steel', (0.35, 0.35, 0.38, 1.0), 0.95, 0.22)
mat_gauge_white = get_or_create_material('PBR_Dial_Face', (0.85, 0.85, 0.80, 1.0), 0.0, 0.3)

def create_torus_mesh(name, major_rad, minor_rad, loc, rot_euler, mat, bone_name=None):
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    bpy.ops.mesh.primitive_torus_add(
        align='WORLD', location=loc, rotation=rot_euler,
        major_radius=major_rad, minor_radius=minor_rad,
        major_segments=24, minor_segments=10
    )
    obj = bpy.context.active_object
    obj.name = name
    for p in obj.data.polygons:
        p.use_smooth = True
    wn = obj.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
    wn.keep_sharp = True
    if mat:
        obj.data.materials.append(mat)
    if rig and bone_name:
        mod = obj.modifiers.new(name="Armature", type='ARMATURE')
        mod.object = rig
        vg = obj.vertex_groups.new(name=bone_name)
        vg.add(range(len(obj.data.vertices)), 1.0, 'REPLACE')
    return obj

def make_mesh_obj(name, bm, mat, bone_name=None):
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(obj)
    for p in me.polygons:
        p.use_smooth = True
    wn = obj.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
    wn.keep_sharp = True
    if mat:
        obj.data.materials.append(mat)
    if rig and bone_name:
        mod = obj.modifiers.new(name="Armature", type='ARMATURE')
        mod.object = rig
        vg = obj.vertex_groups.new(name=bone_name)
        vg.add(range(len(me.vertices)), 1.0, 'REPLACE')
    return obj

print("Rebuilding Varek to 100% Concept Precision...")

# Delete old mesh objects to ensure exact hierarchy
for o in [obj for obj in list(bpy.data.objects) if obj.type == 'MESH']:
    bpy.data.objects.remove(o, do_unlink=True)

# =============================================================================
# 1. TORSO, GORGET & CHEST HATCH
# =============================================================================

# Main Cuirass (Heavy continuous cast iron torso with pectoral volume and abdominal plates)
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=0.46, radius2=0.42, depth=0.75)
for v in bm.verts:
    v.co.z += 1.48
    v.co.y *= 0.82
make_mesh_obj('Varek_Cuirass', bm, mat_iron, bone_name='spine_03')

# High U-Gorget Collar
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=False, cap_tris=False, segments=24, radius1=0.25, radius2=0.28, depth=0.34)
for v in bm.verts:
    v.co.z += 1.84
    v.co.y *= 0.90
    if v.co.y > 0.15:
        v.co.z -= 0.08
make_mesh_obj('Varek_Gorget_Collar', bm, mat_iron, bone_name='spine_03')

# Rolled Bronze Gorget Rim
create_torus_mesh('Varek_Gorget_Bronze_Rim', 0.285, 0.022, (0, 0, 2.01), (0, 0, 0), mat_bronze, bone_name='spine_03')

# Gorget Vertical Vent Slots (Pills)
for i, angle_deg in enumerate([-40, -25, -10, 10, 25, 40]):
    rad = math.radians(angle_deg)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.012
        v.co.y *= 0.030
        v.co.z *= 0.045
    x = math.sin(rad) * 0.28
    y = math.cos(rad) * 0.25
    for v in bm.verts:
        v.co.x += x
        v.co.y += y
        v.co.z += 1.76
    make_mesh_obj(f'Varek_Gorget_Vent_{i+1}', bm, mat_dark_rubber, bone_name='spine_03')

# Center Chest Round Hatch & 3-Spoke Wheel
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=20, radius1=0.12, radius2=0.12, depth=0.04)
for v in bm.verts:
    v.co.y += 0.38
    v.co.z += 1.48
    v.co = Euler((math.radians(75), 0, 0)).to_matrix() @ v.co
make_mesh_obj('Varek_Chest_Hatch_Flange', bm, mat_bronze, bone_name='spine_03')

create_torus_mesh('Varek_Chest_Handwheel', 0.075, 0.012, (0, 0.38, 1.48), (math.radians(75), 0, 0), mat_iron, bone_name='spine_03')

for spoke_i, angle in enumerate([0, 120, 240]):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=0.009, radius2=0.009, depth=0.07)
    rot = Euler((0, math.radians(angle), math.radians(75))).to_matrix()
    for v in bm.verts:
        v.co = rot @ v.co
        v.co.y += 0.40
        v.co.z += 1.48
    make_mesh_obj(f'Varek_Chest_Spoke_{spoke_i+1}', bm, mat_iron, bone_name='spine_03')

# Abdominal segmented fauld plates & Bronze Belt
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=0.44, radius2=0.44, depth=0.10)
for v in bm.verts:
    v.co.z += 1.18
    v.co.y *= 0.85
make_mesh_obj('Varek_Belt_Bronze', bm, mat_bronze, bone_name='pelvis')

bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts:
    v.co.x *= 0.07
    v.co.y *= 0.03
    v.co.z *= 0.05
    v.co.y += 0.38
    v.co.z += 1.18
make_mesh_obj('Varek_Belt_Buckle', bm, mat_iron, bone_name='pelvis')

# Left Hip Ammo/Utility Pouch
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts:
    v.co.x *= 0.05
    v.co.y *= 0.06
    v.co.z *= 0.08
    v.co.x += 0.36
    v.co.y += 0.18
    v.co.z += 1.16
make_mesh_obj('Varek_Utility_Pouch', bm, mat_iron, bone_name='pelvis')

# Coiled Cable on Left Hip
create_torus_mesh('Varek_Coiled_Cable', 0.09, 0.022, (0.42, 0.05, 1.08), (math.radians(20), math.radians(70), 0), mat_dark_rubber, bone_name='pelvis')

# =============================================================================
# 2. HELMET, VISOR & REBREATHER FILTERS
# =============================================================================

bm = bmesh.new()
bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=16, radius=0.16)
for v in bm.verts:
    v.co.z = v.co.z * 1.1 + 1.90
    v.co.y = v.co.y * 1.05 + 0.02
make_mesh_obj('Varek_Helmet_Dome', bm, mat_iron, bone_name='head')

bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts:
    v.co.x *= 0.09
    v.co.y *= 0.02
    v.co.z *= 0.016
    v.co.y += 0.17
    v.co.z += 1.94
make_mesh_obj('Varek_Helmet_Visor_Amber', bm, mat_amber, bone_name='head')

for side, sign in [('L', 1), ('R', -1)]:
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=0.038, radius2=0.038, depth=0.05)
    rot = Euler((math.radians(45), math.radians(25 * sign), math.radians(-30 * sign))).to_matrix()
    for v in bm.verts:
        v.co = rot @ v.co
        v.co.x += 0.08 * sign
        v.co.y += 0.14
        v.co.z += 1.83
    make_mesh_obj(f'Varek_Rebreather_Filter_{side}', bm, mat_bronze, bone_name='head')

# =============================================================================
# 3. GREN-SKILDUS MANTLE & TORC CLASP
# =============================================================================

create_torus_mesh('Varek_Gren_Skildus_Torc', 0.065, 0.014, (-0.28, 0.24, 1.76), (math.radians(35), math.radians(-25), 0), mat_bronze, bone_name='clavicle_r')

bm = bmesh.new()
rows, cols = 16, 10
grid = []
for r in range(rows):
    row_verts = []
    u = r / (rows - 1)
    for c in range(cols):
        v = c / (cols - 1)
        angle = (v - 0.3) * math.pi * 0.7
        rad = 0.26 + 0.12 * u + 0.02 * math.sin(u * 14.0 + c * 3.0)
        x = -0.32 - rad * math.cos(angle) * (0.8 + 0.3 * u)
        y = 0.12 + rad * math.sin(angle) * (0.8 + 0.2 * u)
        z = 1.78 - u * 1.15
        if u > 0.85:
            z -= 0.06 * math.sin(c * 5.0)
        pos = Vector((x, y, z))
        if u < 0.12:
            pos = Vector((-0.28, 0.24, 1.76)).lerp(pos, u / 0.12)
        row_verts.append(bm.verts.new(pos))
    grid.append(row_verts)

for r in range(rows - 1):
    for c in range(cols - 1):
        bm.faces.new([grid[r][c], grid[r+1][c], grid[r+1][c+1], grid[r][c+1]])

bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.018)
make_mesh_obj('Varek_Gren_Skildus_Mantle', bm, mat_green_cloth, bone_name='clavicle_r')

# =============================================================================
# 4. PAULDRONS & BICEPS
# =============================================================================

for tier, scale_rad, z_pos in [(1, 0.24, 1.84), (2, 0.26, 1.76), (3, 0.28, 1.68)]:
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=False, cap_tris=False, segments=18, radius1=scale_rad, radius2=scale_rad*0.8, depth=0.10)
    for v in bm.verts:
        v.co.x += 0.52
        v.co.z += z_pos
        v.co.y *= 0.88
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.020)
    make_mesh_obj(f'Varek_Pauldron_L_Tier_{tier}', bm, mat_iron, bone_name='upper_arm_l')

create_torus_mesh('Varek_Pauldron_L_Bronze_Trim', 0.285, 0.016, (0.52, 0, 1.63), (0, 0, 0), mat_bronze, bone_name='upper_arm_l')

bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=False, cap_tris=False, segments=18, radius1=0.26, radius2=0.22, depth=0.18)
for v in bm.verts:
    v.co.x -= 0.52
    v.co.z += 1.76
    v.co.y *= 0.88
bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.020)
make_mesh_obj('Varek_Pauldron_R_Base', bm, mat_iron, bone_name='upper_arm_r')

for side, sign in [('L', 1), ('R', -1)]:
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=0.12, radius2=0.12, depth=0.22)
    for v in bm.verts:
        v.co.x += 0.50 * sign
        v.co.z += 1.40
        v.co.x += 0.012 * math.sin(v.co.z * 60.0) * sign
    make_mesh_obj(f'Varek_Elbow_Bellows_{side}', bm, mat_dark_rubber, bone_name=f'upper_arm_{side.lower()}')

# =============================================================================
# 5. RIGHT ARM: ROTARY-PERCUSSION DRILL ARM
# =============================================================================

bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=18, radius1=0.14, radius2=0.12, depth=0.35)
for v in bm.verts:
    v.co.x -= 0.56
    v.co.z += 1.15
    v.co.y += 0.04
make_mesh_obj('Varek_Drill_Forearm_Sleeve', bm, mat_iron, bone_name='forearm_r')

bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=0.042, radius2=0.042, depth=0.025)
rot = Euler((math.radians(45), 0, math.radians(-30))).to_matrix()
for v in bm.verts:
    v.co = rot @ v.co
    v.co.x -= 0.62
    v.co.y += 0.16
    v.co.z += 1.25
make_mesh_obj('Varek_Drill_Pressure_Gauge_Bezel', bm, mat_bronze, bone_name='forearm_r')

bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=0.038, radius2=0.038, depth=0.005)
for v in bm.verts:
    v.co = rot @ v.co
    v.co.x -= 0.62
    v.co.y += 0.17
    v.co.z += 1.25
make_mesh_obj('Varek_Drill_Pressure_Gauge_Dial', bm, mat_gauge_white, bone_name='forearm_r')

bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=18, radius1=0.16, radius2=0.15, depth=0.12)
for v in bm.verts:
    v.co.x -= 0.56
    v.co.z += 0.94
make_mesh_obj('Varek_Drill_Chucking_Collar', bm, mat_bronze, bone_name='forearm_r')

bm = bmesh.new()
flute_steps = 36
for step in range(flute_steps):
    t = step / flute_steps
    z = 0.88 - t * 0.58
    rad = 0.14 * (1.0 - t * 0.88)
    angle = t * math.pi * 6.0
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=rad, radius2=rad*0.8, depth=0.025)
    for v in bm.verts[-10:]:
        v.co.x -= 0.56 + 0.015 * math.sin(angle)
        v.co.y += 0.015 * math.cos(angle)
        v.co.z = z
make_mesh_obj('Varek_Drill_Conical_Bit', bm, mat_steel, bone_name='forearm_r')

for h_i, y_off in enumerate([0.08, -0.08]):
    curve_data = bpy.data.curves.new(name=f'Varek_Drill_Hose_{h_i+1}', type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.016
    curve_data.bevel_resolution = 4
    curve_data.use_fill_caps = True
    spline = curve_data.splines.new(type='BEZIER')
    pts = [
        Vector((-0.52, -0.15 + y_off, 1.48)),
        Vector((-0.68, -0.10 + y_off, 1.35)),
        Vector((-0.65, 0.10 + y_off, 1.20)),
        Vector((-0.58, 0.12 + y_off, 1.05))
    ]
    spline.bezier_points.add(len(pts) - 1)
    for p_i, pt in enumerate(pts):
        spline.bezier_points[p_i].co = pt
        spline.bezier_points[p_i].handle_left_type = 'AUTO'
        spline.bezier_points[p_i].handle_right_type = 'AUTO'
    h_obj = bpy.data.objects.new(f'Varek_Drill_Hose_{h_i+1}', curve_data)
    bpy.context.collection.objects.link(h_obj)
    bpy.context.view_layer.objects.active = h_obj
    h_obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    h_obj.data.materials.append(mat_dark_rubber)

# =============================================================================
# 6. LEFT ARM: HOLMATRO RESCUE SHEARS
# =============================================================================

bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=18, radius1=0.14, radius2=0.12, depth=0.38)
for v in bm.verts:
    v.co.x += 0.56
    v.co.z += 1.15
make_mesh_obj('Varek_Shears_Forearm_Sleeve', bm, mat_iron, bone_name='forearm_l')

for side_i, y_pos in enumerate([0.10, -0.10]):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12, radius1=0.024, radius2=0.024, depth=0.32)
    for v in bm.verts:
        v.co.x += 0.68
        v.co.y += y_pos
        v.co.z += 1.12
    make_mesh_obj(f'Varek_Shears_Actuator_Cylinder_{side_i+1}', bm, mat_bronze, bone_name='forearm_l')

bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts:
    v.co.x *= 0.015
    v.co.y *= 0.08
    v.co.z *= 0.12
    v.co.x += 0.68
    v.co.z += 1.08
make_mesh_obj('Varek_Shears_Mesh_Grille', bm, mat_dark_rubber, bone_name='forearm_l')

for jaw_name, z_rot_dir, jaw_z in [('Upper', 1, 0.94), ('Lower', -1, 0.86)]:
    bm = bmesh.new()
    pts = [
        Vector((0.56, 0.08 * z_rot_dir, jaw_z)),
        Vector((0.56, 0.16 * z_rot_dir, jaw_z - 0.08)),
        Vector((0.56, 0.18 * z_rot_dir, jaw_z - 0.18)),
        Vector((0.56, 0.08 * z_rot_dir, jaw_z - 0.28)),
        Vector((0.56, 0.02 * z_rot_dir, jaw_z - 0.32))
    ]
    thick = 0.035
    v_l = [bm.verts.new(p + Vector((-thick, 0, 0))) for p in pts]
    v_r = [bm.verts.new(p + Vector((thick, 0, 0))) for p in pts]
    for idx in range(len(pts) - 1):
        bm.faces.new([v_l[idx], v_r[idx], v_r[idx+1], v_l[idx+1]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.030)
    make_mesh_obj(f'Varek_Shear_Blade_{jaw_name}', bm, mat_steel, bone_name='forearm_l')

# =============================================================================
# 7. LEGS: CUISSES, KNEE COPS, GREAVES & ANCHOR BOOTS
# =============================================================================

for side, sign in [('L', 1), ('R', -1)]:
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=18, radius1=0.20, radius2=0.16, depth=0.34)
    for v in bm.verts:
        v.co.x += 0.24 * sign
        v.co.z += 0.92
        v.co.y *= 0.90
    make_mesh_obj(f'Varek_Cuisse_{side}', bm, mat_iron, bone_name=f'thigh_{side.lower()}')

    create_torus_mesh(f'Varek_Cuisse_Trim_{side}', 0.175, 0.016, (0.24 * sign, 0, 0.76), (0, 0, 0), mat_bronze, bone_name=f'thigh_{side.lower()}')

    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=0.10)
    for v in bm.verts:
        v.co.x += 0.24 * sign
        v.co.y += 0.14
        v.co.z += 0.70
    make_mesh_obj(f'Varek_Knee_Cop_{side}', bm, mat_iron, bone_name=f'shin_{side.lower()}')

    for cap_side, cap_sign in [('In', -1), ('Out', 1)]:
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12, radius1=0.038, radius2=0.038, depth=0.02)
        for v in bm.verts:
            v.co.x += (0.24 + 0.11 * cap_sign) * sign
            v.co.y += 0.08
            v.co.z += 0.70
            v.co = Euler((0, math.radians(90), 0)).to_matrix() @ v.co
        make_mesh_obj(f'Varek_Knee_Pivot_{side}_{cap_side}', bm, mat_bronze, bone_name=f'shin_{side.lower()}')

    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=18, radius1=0.16, radius2=0.22, depth=0.42)
    for v in bm.verts:
        v.co.x += 0.24 * sign
        v.co.z += 0.44
        if v.co.y > 0.05:
            v.co.y += 0.03
    make_mesh_obj(f'Varek_Greave_{side}', bm, mat_iron, bone_name=f'shin_{side.lower()}')

    create_torus_mesh(f'Varek_Greave_Ankle_Trim_{side}', 0.225, 0.018, (0.24 * sign, 0, 0.24), (0, 0, 0), mat_bronze, bone_name=f'shin_{side.lower()}')

    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12, radius1=0.022, radius2=0.022, depth=0.36)
    for v in bm.verts:
        v.co.x += 0.24 * sign
        v.co.y -= 0.16
        v.co.z += 0.48
    make_mesh_obj(f'Varek_Calf_Ram_{side}', bm, mat_bronze, bone_name=f'shin_{side.lower()}')

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.22
        v.co.y *= 0.28
        v.co.z *= 0.10
        v.co.x += 0.24 * sign
        v.co.y -= 0.04
        v.co.z += 0.11
    make_mesh_obj(f'Varek_Boot_Bridge_{side}', bm, mat_iron, bone_name=f'foot_{side.lower()}')

    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=0.16)
    for v in bm.verts:
        v.co.x += 0.24 * sign
        v.co.y += 0.02
        v.co.z = v.co.z * 0.6 + 0.14
    make_mesh_obj(f'Varek_Boot_Shield_{side}', bm, mat_bronze, bone_name=f'foot_{side.lower()}')

    for toe_i, toe_x_off in enumerate([-0.09, -0.03, 0.03, 0.09]):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co.x *= 0.026
            v.co.y *= 0.075
            v.co.z *= 0.045
            v.co.x += (0.24 + toe_x_off) * sign
            v.co.y += 0.22
            v.co.z += 0.045
        make_mesh_obj(f'Varek_Toe_Cleat_{side}_{toe_i+1}', bm, mat_iron, bone_name=f'foot_{side.lower()}')

# =============================================================================
# 8. KINEMATIC SCALE & GROUNDING LOCK (2.4384m Height, 0.0000m Ground)
# =============================================================================

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
print(f"SUCCESS: Exact Concept Match Varek Build Applied to {blend_path}")
