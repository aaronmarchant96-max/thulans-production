import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler
from pathlib import Path

# Load baseline rig and scene
source_parent = '/home/aaron/animation/thulans-production/blender/candidates/varek-v2b7-anchor-grounded.blend'
target_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v40-osint-juggernaut.blend'
bpy.ops.wm.open_mainfile(filepath=source_parent)
scene = bpy.context.scene

# Clean old test meshes, retain rig
keep_exact = ['Varek_Original_Rig', 'Armature']
for obj in list(bpy.data.objects):
    if obj.name not in keep_exact and obj.type == 'MESH':
        bpy.data.objects.remove(obj, do_unlink=True)

arm = bpy.data.objects.get('Varek_Original_Rig') or bpy.data.objects.get('Armature')

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

# Clean neutral gray clay mat for pure topology & MatCap review (No shiny chrome hiding flaws)
mat_clay = bpy.data.materials.new('QA_Workbench_Clay')
mat_clay.use_nodes = True
bsdf = mat_clay.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value = (0.28, 0.28, 0.30, 1.0)
bsdf.inputs['Metallic'].default_value = 0.0
bsdf.inputs['Roughness'].default_value = 0.55

mat_bronze_trim = bpy.data.materials.new('QA_Bronze_Trim')
mat_bronze_trim.use_nodes = True
bsdf_b = mat_bronze_trim.node_tree.nodes.get('Principled BSDF')
bsdf_b.inputs['Base Color'].default_value = (0.45, 0.30, 0.14, 1.0)
bsdf_b.inputs['Metallic'].default_value = 0.8
bsdf_b.inputs['Roughness'].default_value = 0.35

def tag_sculpt_obj(obj, name, col, mat=mat_clay, driver='spine'):
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

# =============================================================================
# 1. SUBSYSTEM 1: SCULPTED TORSO CUIRASS & HIGH U-SHAPED GORGET COLLAR
# =============================================================================
# We build an authentic anatomical cast-iron breastplate with:
# - Deep U-shaped neck aperture surrounded by high gorget wall
# - Convex pectoral bulge tapering smoothly to pelvic girdle flange
# - Sub-D quad flow with creased perimeter flanges
bm_torso = bmesh.new()

# Define cross-sectional anatomical profile rings (Z, rx, ry_front, ry_back, center_y)
torso_layers = [
    (0.96, 0.26, -0.16, 0.16, 0.00),   # Crotch / Pelvic base
    (1.12, 0.34, -0.22, 0.20, 0.00),   # Lower pelvis / hip flare
    (1.24, 0.36, -0.25, 0.22, 0.00),   # Waist recess (tapered)
    (1.42, 0.42, -0.30, 0.25, -0.01),  # Lower ribs expansion
    (1.62, 0.48, -0.36, 0.28, -0.02),  # Full pectoral peak
    (1.80, 0.46, -0.34, 0.29, -0.01),  # Clavicle shelf
    (1.94, 0.38, -0.28, 0.27, 0.01),   # Gorget transition base
    (2.06, 0.30, -0.22, 0.30, 0.03),   # Mid gorget collar wall
    (2.20, 0.27, -0.17, 0.33, 0.05),   # High U-Collar top rim
]

rings = []
n_pts = 32
for z, rx, ry_f, ry_b, cy in torso_layers:
    ring = []
    for i in range(n_pts):
        th = 2.0 * math.pi * i / float(n_pts)
        x = rx * math.sin(th)
        # Add chest plate anatomical curvature
        y_r = ry_f if math.cos(th) < 0 else ry_b
        # Sculpt front pectoral ridge
        if math.cos(th) < -0.3 and 1.4 < z < 1.85:
            y_r *= (1.0 + 0.15 * math.cos(th * 2.0))
        y = cy + y_r * math.cos(th)
        ring.append(bm_torso.verts.new((x, y, z)))
    rings.append(ring)

for i in range(len(rings) - 1):
    r1, r2 = rings[i], rings[i+1]
    for j in range(n_pts):
        bm_torso.faces.new((r1[j], r1[(j+1)%n_pts], r2[(j+1)%n_pts], r2[j]))

bm_torso.faces.new(reversed(rings[0]))
bmesh.ops.bevel(bm_torso, geom=list(bm_torso.edges), offset=0.010, segments=2, affect='EDGES')

me_torso = bpy.data.meshes.new('Sculpt_Torso_Cuirass_Mesh')
bm_torso.to_mesh(me_torso)
bm_torso.free()
obj_torso = bpy.data.objects.new('Sculpt_Torso_Cuirass', me_torso)
scene.collection.objects.link(obj_torso)
mod_sub_t = obj_torso.modifiers.new(name='Subsurf', type='SUBSURF')
mod_sub_t.levels = 2
mod_sub_t.render_levels = 2
tag_sculpt_obj(obj_torso, 'Sculpt_Torso_Cuirass', col_hull, mat_clay, driver='spine')

# Gorget Top Rim Rolled Bronze Flange
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.28, minor_radius=0.020,
    location=(0.0, 0.06, 2.20),
    rotation=(math.radians(12), 0, 0)
)
tag_sculpt_obj(bpy.context.active_object, 'Sculpt_Gorget_Rim_Bronze', col_hull, mat_bronze_trim, driver='spine')

# Gorget Vertical Ventilation Louvers
for idx, x_louver in enumerate([-0.10, -0.06, -0.02, 0.02, 0.06, 0.10]):
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(x_louver, -0.24, 1.98),
        scale=(0.015, 0.018, 0.045)
    )
    tag_sculpt_obj(bpy.context.active_object, f'Gorget_Vent_Louver_{idx+1}', col_hull, mat_clay, driver='spine')

# Central Pectoral Seal / 3-Spoke Relief Valve
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.115, depth=0.035,
    location=(0.0, -0.34, 1.62),
    rotation=(math.radians(86), 0, 0)
)
tag_sculpt_obj(bpy.context.active_object, 'Pectoral_Hatch_Flange', col_hull, mat_bronze_trim, driver='spine')

bpy.ops.mesh.primitive_torus_add(
    major_radius=0.075, minor_radius=0.014,
    location=(0.0, -0.36, 1.62),
    rotation=(math.radians(86), 0, 0)
)
tag_sculpt_obj(bpy.context.active_object, 'Pectoral_Hatch_Handwheel', col_hull, mat_clay, driver='spine')

for s_idx, rot in enumerate([0, 120, 240]):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.010, depth=0.13,
        location=(0.0, -0.36, 1.62),
        rotation=(math.radians(86), math.radians(rot), 0)
    )
    tag_sculpt_obj(bpy.context.active_object, f'Pectoral_Hatch_Spoke_{s_idx+1}', col_hull, mat_clay, driver='spine')

# =============================================================================
# 2. SUBSYSTEM 2: ORGANICALLY SCULPTED THIGHS & SHINS (CUISSE & GREAVES)
# =============================================================================
# Thigh bone: (-0.30, 0.01, 1.02) to (-0.35, 0.0, 0.61)
# Shin bone: (-0.35, 0.0, 0.61) to (-0.35, -0.01, 0.24)
for side, x_leg in [('L', -0.30), ('R', 0.30)]:
    thigh_drv = f'thigh.{side}'
    shin_drv = f'shin.{side}'
    foot_drv = f'foot.{side}'

    # 2A. SCULPTED CUISSE (Thigh Armor Plate): Contoured barrel with muscle swell
    bm_thigh = bmesh.new()
    thigh_layers = [
        (0.66, 0.17, 0.16),  # Above knee taper
        (0.76, 0.21, 0.19),  # Mid thigh outward expansion
        (0.88, 0.22, 0.20),  # Upper thigh swell
        (1.02, 0.19, 0.17),  # Inguinal crest taper
    ]
    t_rings = []
    for z, rx, ry in thigh_layers:
        ring = []
        for i in range(24):
            th = 2.0 * math.pi * i / 24.0
            x = x_leg + rx * math.sin(th)
            y = 0.01 + ry * math.cos(th)
            ring.append(bm_thigh.verts.new((x, y, z)))
        t_rings.append(ring)
    for i in range(len(t_rings) - 1):
        r1, r2 = t_rings[i], t_rings[i+1]
        for j in range(24):
            bm_thigh.faces.new((r1[j], r1[(j+1)%24], r2[(j+1)%24], r2[j]))
    bmesh.ops.bevel(bm_thigh, geom=list(bm_thigh.edges), offset=0.008, segments=2, affect='EDGES')
    me_thigh = bpy.data.meshes.new(f'Sculpt_Cuisse_{side}_Mesh')
    bm_thigh.to_mesh(me_thigh)
    bm_thigh.free()
    obj_thigh = bpy.data.objects.new(f'Sculpt_Cuisse_{side}', me_thigh)
    scene.collection.objects.link(obj_thigh)
    mod = obj_thigh.modifiers.new(name='Subsurf', type='SUBSURF')
    mod.levels = 2
    tag_sculpt_obj(obj_thigh, f'Sculpt_Cuisse_{side}', col_legs, mat_clay, driver=thigh_drv)

    # Bronze Cuisse Bottom Flange Trim
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.175, minor_radius=0.016,
        location=(x_leg, 0.01, 0.66),
        rotation=(0, 0, 0)
    )
    tag_sculpt_obj(bpy.context.active_object, f'Sculpt_Cuisse_Trim_{side}', col_legs, mat_bronze_trim, driver=thigh_drv)

    # 2B. SPHERICAL DOMED KNEE COP & PIVOT BOSS
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.138,
        location=(x_leg, -0.06, 0.61)
    )
    obj_knee = bpy.context.active_object
    mod_k = obj_knee.modifiers.new(name='Subsurf', type='SUBSURF')
    mod_k.levels = 1
    tag_sculpt_obj(obj_knee, f'Sculpt_Knee_Cop_{side}', col_legs, mat_clay, driver=shin_drv)

    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.048, depth=0.035,
        location=(x_leg + (-0.14 if side=='L' else 0.14), -0.06, 0.61),
        rotation=(0, math.radians(90), 0)
    )
    tag_sculpt_obj(bpy.context.active_object, f'Sculpt_Knee_Boss_{side}', col_legs, mat_bronze_trim, driver=shin_drv)

    # 2C. SCULPTED GREAVE (Shin Armor Guard): Heavy flared cast guard with anterior ridge
    bm_shin = bmesh.new()
    shin_layers = [
        (0.18, 0.17, 0.16),  # Ankle collar taper
        (0.32, 0.20, 0.19),  # Mid calf bulge
        (0.48, 0.21, 0.20),  # Upper calf flare
        (0.58, 0.18, 0.17),  # Sub-knee transition
    ]
    s_rings = []
    for z, rx, ry in shin_layers:
        ring = []
        for i in range(24):
            th = 2.0 * math.pi * i / 24.0
            x = x_leg + rx * math.sin(th)
            # Anterior shin ridge on front
            y_r = ry * (1.12 if math.cos(th) < -0.5 else 1.0)
            y = -0.01 + y_r * math.cos(th)
            ring.append(bm_shin.verts.new((x, y, z)))
        s_rings.append(ring)
    for i in range(len(s_rings) - 1):
        r1, r2 = s_rings[i], s_rings[i+1]
        for j in range(24):
            bm_shin.faces.new((r1[j], r1[(j+1)%24], r2[(j+1)%24], r2[j]))
    bmesh.ops.bevel(bm_shin, geom=list(bm_shin.edges), offset=0.008, segments=2, affect='EDGES')
    me_shin = bpy.data.meshes.new(f'Sculpt_Greave_{side}_Mesh')
    bm_shin.to_mesh(me_shin)
    bm_shin.free()
    obj_shin = bpy.data.objects.new(f'Sculpt_Greave_{side}', me_shin)
    scene.collection.objects.link(obj_shin)
    mod = obj_shin.modifiers.new(name='Subsurf', type='SUBSURF')
    mod.levels = 2
    tag_sculpt_obj(obj_shin, f'Sculpt_Greave_{side}', col_legs, mat_clay, driver=shin_drv)

    # Bronze Ankle Flange Trim
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.172, minor_radius=0.016,
        location=(x_leg, -0.01, 0.18),
        rotation=(0, 0, 0)
    )
    tag_sculpt_obj(bpy.context.active_object, f'Sculpt_Greave_Ankle_Trim_{side}', col_legs, mat_bronze_trim, driver=shin_drv)

    # Rear Hydraulic Calf Stabilizer Ram
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.030, depth=0.28,
        location=(x_leg, 0.17, 0.38),
        rotation=(math.radians(-10), 0, 0)
    )
    tag_sculpt_obj(bpy.context.active_object, f'Sculpt_Calf_Stabilizer_Ram_{side}', col_legs, mat_bronze_trim, driver=shin_drv)

    # 2D. MULTI-SEGMENT TECTONIC ANCHOR BOOT CHASSIS
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(x_leg, -0.06, 0.08),
        scale=(0.28, 0.46, 0.14)
    )
    obj_b_base = bpy.context.active_object
    mod_b = obj_b_base.modifiers.new(name='Bevel', type='BEVEL')
    mod_b.width = 0.02
    tag_sculpt_obj(obj_b_base, f'Sculpt_Boot_Chassis_{side}', col_legs, mat_clay, driver=foot_drv)

    # 4-Segment Articulated Excavator Toe Claws
    for t_idx, x_toe_off in enumerate([-0.10, -0.035, 0.035, 0.10]):
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(x_leg + x_toe_off, -0.29, 0.05),
            scale=(0.055, 0.13, 0.08),
            rotation=(math.radians(18), 0, 0)
        )
        obj_t = bpy.context.active_object
        mod_t = obj_t.modifiers.new(name='Bevel', type='BEVEL')
        mod_t.width = 0.01
        tag_sculpt_obj(obj_t, f'Sculpt_Toe_Segment_{side}_{t_idx+1}', col_legs, mat_clay, driver=foot_drv)

# =============================================================================
# 3. SUBSYSTEM 3: 3-TIER FLARED PAULDRONS (SHOULDER COVERS)
# =============================================================================
for side, x_sh in [('L', -0.58), ('R', 0.58)]:
    sh_drv = f'upper_arm.{side}'
    for tier, (z_p, sc_r, sc_d, rot_y) in enumerate([
        (1.94, 0.32, 0.12, -26 if side=='L' else 26),
        (1.84, 0.30, 0.10, -18 if side=='L' else 18),
        (1.74, 0.28, 0.09, -10 if side=='L' else 10)
    ]):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=1.0, depth=1.0,
            location=(x_sh, 0.00, z_p),
            rotation=(0, math.radians(rot_y), 0)
        )
        obj_p = bpy.context.active_object
        obj_p.scale = (sc_r, sc_r * 1.15, sc_d)
        mod_p = obj_p.modifiers.new(name='Bevel', type='BEVEL')
        mod_p.width = 0.02
        mod_sub = obj_p.modifiers.new(name='Subsurf', type='SUBSURF')
        mod_sub.levels = 1
        tag_sculpt_obj(obj_p, f'Sculpt_Puldron_Tier_{tier+1}_{side}', col_frame, mat_clay, driver=sh_drv)

        if tier == 0:
            bpy.ops.mesh.primitive_torus_add(
                major_radius=0.33, minor_radius=0.016,
                location=(x_sh, 0.00, z_p + 0.05),
                rotation=(0, math.radians(rot_y), 0)
            )
            tag_sculpt_obj(bpy.context.active_object, f'Sculpt_Puldron_Trim_{side}', col_frame, mat_bronze_trim, driver=sh_drv)

# =============================================================================
# 4. SUBSYSTEM 4: GREN-SKILDUS HEAVY WOOL MANTLE WITH ORGANIC GATHERED DRAPING
# =============================================================================
# Drapes over figure's right shoulder (X > 0 / viewer's right) through ancient bronze ring
bm_m = bmesh.new()
# Grid of vertices creating authentic gathered folds cascading over chest and flank
m_pts = [
    # Shoulder bunching around ring clasp
    [(0.32, -0.22, 1.94), (0.42, -0.16, 1.97), (0.48, -0.04, 1.98), (0.46, 0.14, 1.94), (0.36, 0.24, 1.90)],
    # Clavicle gather
    [(0.30, -0.26, 1.76), (0.44, -0.18, 1.78), (0.52, -0.04, 1.76), (0.48, 0.16, 1.74), (0.34, 0.26, 1.70)],
    # Mid-chest cascade
    [(0.28, -0.28, 1.50), (0.46, -0.16, 1.52), (0.54, -0.02, 1.50), (0.50, 0.18, 1.48), (0.32, 0.26, 1.44)],
    # Waist drape
    [(0.26, -0.26, 1.20), (0.44, -0.14, 1.22), (0.52, -0.02, 1.20), (0.48, 0.18, 1.18), (0.30, 0.24, 1.15)],
    # Tattered hem
    [(0.24, -0.24, 0.88), (0.42, -0.12, 0.86), (0.50, -0.02, 0.84), (0.46, 0.16, 0.82), (0.28, 0.22, 0.80)]
]

v_grid = []
for row in m_pts:
    v_grid.append([bm_m.verts.new(pt) for pt in row])

for r in range(len(v_grid) - 1):
    for c in range(4):
        bm_m.faces.new((v_grid[r][c], v_grid[r][c+1], v_grid[r+1][c+1], v_grid[r+1][c]))

bmesh.ops.solidify(bm_m, geom=list(bm_m.faces), thickness=0.035)
me_m = bpy.data.meshes.new('Sculpt_Gren_Skildus_Mesh')
bm_m.to_mesh(me_m)
bm_m.free()
obj_m = bpy.data.objects.new('Sculpt_Gren_Skildus_Mantle', me_m)
scene.collection.objects.link(obj_m)
mod_m_sub = obj_m.modifiers.new(name='Subsurf', type='SUBSURF')
mod_m_sub.levels = 2
tag_sculpt_obj(obj_m, 'Sculpt_Gren_Skildus_Mantle', col_mantle, mat_clay, driver='spine')

# Ancient Circular Bronze Ring Brooch Torc Clasp
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.090, minor_radius=0.018,
    location=(0.36, -0.24, 1.88),
    rotation=(math.radians(45), math.radians(-25), 0)
)
tag_sculpt_obj(bpy.context.active_object, 'Sculpt_Gren_Skildus_Torc_Clasp', col_mantle, mat_bronze_trim, driver='spine')

# =============================================================================
# 5. SUBSYSTEM 5: FOREARM TOOL STATIONS (DRILL & SHEARS)
# =============================================================================
# 5A. RIGHT FOREARM: ROTARY-PERCUSSION DRILL ARM
x_drill = 0.71
# Bicep sleeve
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.13, depth=0.36,
    location=(0.66, -0.01, 1.54),
    rotation=(0, 0, 0)
)
tag_sculpt_obj(bpy.context.active_object, 'Sculpt_Armor_Bicep_R', col_tools, mat_clay, driver='upper_arm.R')

# Armored Forearm Sleeve
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.12, depth=0.42,
    location=(x_drill, -0.02, 1.10),
    rotation=(0, 0, 0)
)
tag_sculpt_obj(bpy.context.active_object, 'Sculpt_Tool_Drill_Housing', col_tools, mat_clay, driver='forearm.R')

# Bronze Reinforcing Rib Rings
for z_rib in [1.25, 1.10, 0.94]:
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.124, minor_radius=0.014,
        location=(x_drill, -0.02, z_rib),
        rotation=(0, 0, 0)
    )
    tag_sculpt_obj(bpy.context.active_object, f'Sculpt_Drill_Rib_{z_rib}', col_tools, mat_bronze_trim, driver='forearm.R')

# Analog Pressure Gauge
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.036, depth=0.022,
    location=(x_drill + 0.09, -0.10, 1.20),
    rotation=(math.radians(35), math.radians(45), 0)
)
tag_sculpt_obj(bpy.context.active_object, 'Sculpt_Drill_Pressure_Gauge', col_tools, mat_bronze_trim, driver='forearm.R')

# Fluted Spiral Boring Head
bm_bit = bmesh.new()
bmesh.ops.create_cone(
    bm_bit, segments=32, radius1=0.105, radius2=0.008, depth=0.50
)
for v in bm_bit.verts:
    ang = (v.co.z + 0.25) * 11.0
    x0, y0 = v.co.x, v.co.y
    v.co.x = (x0 * math.cos(ang) - y0 * math.sin(ang)) * (1.0 + 0.15 * math.cos(ang * 2))
    v.co.y = (x0 * math.sin(ang) + y0 * math.cos(ang)) * (1.0 + 0.15 * math.cos(ang * 2))
    v.co.z = 0.88 - (v.co.z + 0.25)
    v.co.x += x_drill
    v.co.y -= 0.02

me_bit = bpy.data.meshes.new('Sculpt_Tool_Drill_Bit_Mesh')
bm_bit.to_mesh(me_bit)
bm_bit.free()
obj_bit = bpy.data.objects.new('Sculpt_Tool_Drill_Bit', me_bit)
scene.collection.objects.link(obj_bit)
mod_b_sub = obj_bit.modifiers.new(name='Subsurf', type='SUBSURF')
mod_b_sub.levels = 1
tag_sculpt_obj(obj_bit, 'Sculpt_Tool_Drill_Bit', col_tools, mat_clay, driver='forearm.R')

# 5B. LEFT FOREARM: RESCUE SHEARS / DEMOLITION SPREADER
x_shear = -0.71
# Bicep sleeve
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.13, depth=0.36,
    location=(-0.66, -0.01, 1.54),
    rotation=(0, 0, 0)
)
tag_sculpt_obj(bpy.context.active_object, 'Sculpt_Armor_Bicep_L', col_tools, mat_clay, driver='upper_arm.L')

# Forearm Cuff
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.12, depth=0.42,
    location=(x_shear, -0.02, 1.10),
    rotation=(0, 0, 0)
)
tag_sculpt_obj(bpy.context.active_object, 'Sculpt_Tool_Shear_Housing', col_tools, mat_clay, driver='forearm.L')

# Dual Actuator Piston Rams
for dy in [-0.06, 0.06]:
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.035, depth=0.34,
        location=(x_shear - 0.13, dy - 0.02, 1.10),
        rotation=(0, 0, 0)
    )
    tag_sculpt_obj(bpy.context.active_object, f'Sculpt_Shear_Ram_{dy}', col_tools, mat_bronze_trim, driver='forearm.L')

# Pivot Boss
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.08, depth=0.15,
    location=(x_shear, -0.03, 0.88),
    rotation=(math.radians(90), 0, 0)
)
tag_sculpt_obj(bpy.context.active_object, 'Sculpt_Shear_Pivot_Boss', col_tools, mat_bronze_trim, driver='forearm.L')

# Curved Stepped Demolition Cutting Blades
for j_idx, (j_name, dy_off, r_z) in enumerate([('Upper', 0.045, 18), ('Lower', -0.045, -22)]):
    bm_blade = bmesh.new()
    bmesh.ops.create_cube(bm_blade, size=1.0)
    for v in bm_blade.verts:
        v.co.x = v.co.x * 0.040 - 0.71
        v.co.y = v.co.y * 0.080 + dy_off - 0.03
        v.co.z = v.co.z * 0.24 + 0.72
        if v.co.z < 0.70:
            v.co.y += (-0.06 if j_name=='Upper' else 0.06)
    bmesh.ops.bevel(bm_blade, geom=list(bm_blade.edges), offset=0.010, segments=2, affect='EDGES')
    me_blade = bpy.data.meshes.new(f'Sculpt_Shear_Blade_{j_name}_Mesh')
    bm_blade.to_mesh(me_blade)
    bm_blade.free()
    obj_blade = bpy.data.objects.new(f'Sculpt_Shear_Blade_{j_name}', me_blade)
    scene.collection.objects.link(obj_blade)
    mod_bl_sub = obj_blade.modifiers.new(name='Subsurf', type='SUBSURF')
    mod_bl_sub.levels = 1
    tag_sculpt_obj(obj_blade, f'Sculpt_Shear_Blade_{j_name}', col_tools, mat_clay, driver='forearm.L')

# =============================================================================
# 6. SAVE PRODUCTION MESH
# =============================================================================
bpy.ops.wm.save_as_mainfile(filepath=target_blend)
print(f"SUCCESS: Sub-D Sculpted Varek V40 saved to {target_blend}")

