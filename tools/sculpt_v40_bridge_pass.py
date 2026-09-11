import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler
from pathlib import Path

blend_path = '/home/aaron/animation/thulans-production/blender/candidates/varek-v40-osint-juggernaut.blend'
bpy.ops.wm.open_mainfile(filepath=blend_path)
scene = bpy.context.scene

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
# 1. SCULPTED PELVIC FAULD / INGUINAL CODPLATE & HIP GUARDS
# -----------------------------------------------------------------------------
# Triangular reinforced cast plate covering the groin / pelvic junction
bm_cod = bmesh.new()
cod_verts = [
    # Top waist rim
    (-0.16, -0.22, 1.22), (-0.08, -0.26, 1.23), (0.00, -0.27, 1.23), (0.08, -0.26, 1.23), (0.16, -0.22, 1.22),
    # Mid shield
    (-0.14, -0.21, 1.08), (-0.07, -0.25, 1.10), (0.00, -0.26, 1.10), (0.07, -0.25, 1.10), (0.14, -0.21, 1.08),
    # Inguinal wedge apex
    (-0.08, -0.16, 0.94), (-0.04, -0.20, 0.95), (0.00, -0.21, 0.95), (0.04, -0.20, 0.95), (0.08, -0.16, 0.94)
]
v_grid = [bm_cod.verts.new(pt) for pt in cod_verts]
for r in range(2):
    for c in range(4):
        i0 = r * 5 + c
        bm_cod.faces.new((v_grid[i0], v_grid[i0+1], v_grid[i0+6], v_grid[i0+5]))

bmesh.ops.solidify(bm_cod, geom=list(bm_cod.faces), thickness=0.035)
bmesh.ops.bevel(bm_cod, geom=list(bm_cod.edges), offset=0.008, segments=2, affect='EDGES')
me_cod = bpy.data.meshes.new('Sculpt_Pelvic_Codplate_Mesh')
bm_cod.to_mesh(me_cod)
bm_cod.free()
obj_cod = bpy.data.objects.new('Sculpt_Pelvic_Codplate', me_cod)
scene.collection.objects.link(obj_cod)
mod = obj_cod.modifiers.new(name='Subsurf', type='SUBSURF')
mod.levels = 2
tag_obj(obj_cod, 'Sculpt_Pelvic_Codplate', col_hull, mat_clay, driver='pelvis')

# Bronze Trim on Codplate Ridge
bpy.ops.mesh.primitive_cube_add(
    size=1.0, location=(0.0, -0.26, 1.08),
    scale=(0.02, 0.02, 0.26),
    rotation=(math.radians(12), 0, 0)
)
tag_obj(bpy.context.active_object, 'Sculpt_Codplate_Bronze_Ridge', col_hull, mat_bronze, driver='pelvis')

# Left / Right Lateral Hip Fauld Plates
for side, x_fauld, rot_y in [('L', -0.28, -15), ('R', 0.28, 15)]:
    bpy.ops.mesh.primitive_cube_add(
        size=1.0, location=(x_fauld, -0.12, 1.10),
        scale=(0.12, 0.26, 0.18),
        rotation=(0, math.radians(rot_y), 0)
    )
    obj_fauld = bpy.context.active_object
    mod_f = obj_fauld.modifiers.new(name='Bevel', type='BEVEL')
    mod_f.width = 0.02
    tag_obj(obj_fauld, f'Sculpt_Hip_Fauld_{side}', col_hull, mat_clay, driver='pelvis')

# -----------------------------------------------------------------------------
# 2. JOINT ARTICULATION BELLOWS (BRIDGING ELBOWS & KNEES)
# -----------------------------------------------------------------------------
# Corrugated Rubber Accordion Bellows on Elbows
for side, x_elb, rot_y in [('L', -0.68, 6), ('R', 0.68, -6)]:
    for r_idx, z_ring in enumerate([1.34, 1.30, 1.26]):
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.118, minor_radius=0.016,
            location=(x_elb, -0.01, z_ring),
            rotation=(0, math.radians(rot_y), 0)
        )
        tag_obj(bpy.context.active_object, f'Sculpt_Elbow_Bellows_{side}_{r_idx+1}', col_tools, mat_dark_iron, driver=f'upper_arm.{side}')

# Corrugated Rubber Bellows on Knees
for side, x_kn in [('L', -0.30), ('R', 0.30)]:
    for r_idx, z_ring in enumerate([0.65, 0.61, 0.57]):
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.155, minor_radius=0.018,
            location=(x_kn, 0.01, z_ring),
            rotation=(0, 0, 0)
        )
        tag_obj(bpy.context.active_object, f'Sculpt_Knee_Bellows_{side}_{r_idx+1}', col_legs, mat_dark_iron, driver=f'shin.{side}')

# -----------------------------------------------------------------------------
# 3. MOUNTING FLANGES & HEAVY TOOL CUFFS
# -----------------------------------------------------------------------------
# Right Drill Mounting Collar Flange (Connecting cone to forearm sleeve)
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.128, depth=0.06,
    location=(0.71, -0.02, 0.90),
    rotation=(0, 0, 0)
)
tag_obj(bpy.context.active_object, 'Sculpt_Drill_Chucking_Flange', col_tools, mat_bronze, driver='forearm.R')

# Left Rescue Shear Mounting Hub & Heavy Blade Knuckle
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.128, depth=0.06,
    location=(-0.71, -0.02, 0.90),
    rotation=(0, 0, 0)
)
tag_obj(bpy.context.active_object, 'Sculpt_Shear_Mounting_Flange', col_tools, mat_bronze, driver='forearm.L')

# -----------------------------------------------------------------------------
# 4. GREN-SKILDUS TATTERED DRAPE RESCULPT
# -----------------------------------------------------------------------------
# Recreate with deep sculptural wave folds and frayed bottom hem
obj_old_m = bpy.data.objects.get('Sculpt_Gren_Skildus_Mantle')
if obj_old_m:
    bpy.data.objects.remove(obj_old_m, do_unlink=True)

bm_m2 = bmesh.new()
# Curving, layered S-wave folds
m_waves = [
    # Clasp bunching
    [(0.32, -0.22, 1.94), (0.42, -0.16, 1.97), (0.48, -0.04, 1.98), (0.46, 0.14, 1.94), (0.36, 0.24, 1.90)],
    # Shoulder roll
    [(0.30, -0.27, 1.74), (0.45, -0.20, 1.77), (0.54, -0.04, 1.75), (0.50, 0.16, 1.72), (0.34, 0.26, 1.68)],
    # Mid-chest heavy undulating folds
    [(0.27, -0.30, 1.48), (0.46, -0.18, 1.52), (0.56, -0.02, 1.50), (0.52, 0.18, 1.46), (0.31, 0.26, 1.42)],
    # Flank cascade
    [(0.25, -0.28, 1.18), (0.44, -0.15, 1.22), (0.54, -0.01, 1.19), (0.49, 0.18, 1.16), (0.29, 0.24, 1.12)],
    # Tattered jagged hem points
    [(0.23, -0.25, 0.82), (0.43, -0.10, 0.86), (0.52, 0.01, 0.78), (0.47, 0.19, 0.84), (0.27, 0.21, 0.76)]
]

v_rows = []
for row in m_waves:
    v_rows.append([bm_m2.verts.new(pt) for pt in row])

for r in range(len(v_rows) - 1):
    for c in range(4):
        bm_m2.faces.new((v_rows[r][c], v_rows[r][c+1], v_rows[r+1][c+1], v_rows[r+1][c]))

bmesh.ops.solidify(bm_m2, geom=list(bm_m2.faces), thickness=0.038)
me_m2 = bpy.data.meshes.new('Sculpt_Gren_Skildus_Mantle_Mesh')
bm_m2.to_mesh(me_m2)
bm_m2.free()
obj_m2 = bpy.data.objects.new('Sculpt_Gren_Skildus_Mantle', me_m2)
scene.collection.objects.link(obj_m2)
mod_m = obj_m2.modifiers.new(name='Subsurf', type='SUBSURF')
mod_m.levels = 2
tag_obj(obj_m2, 'Sculpt_Gren_Skildus_Mantle', col_mantle, mat_clay, driver='spine')

# Save updated candidate
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"SUCCESS: Bridged & Sculpted Varek V40 saved to {blend_path}")

