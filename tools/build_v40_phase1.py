import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler
from pathlib import Path

# -----------------------------------------------------------------------------
# 1. INITIALIZE PRODUCTION ENVIRONMENT & BASELINE KINEMATICS
# -----------------------------------------------------------------------------
source_parent = '/home/aaron/animation/thulans-production/blender/candidates/varek-v2b7-anchor-grounded.blend'
target_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v40-osint-juggernaut.blend'

bpy.ops.wm.open_mainfile(filepath=source_parent)
scene = bpy.context.scene

# Create or retrieve production collections
def get_or_create_col(name):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        scene.collection.children.link(col)
    return col

col_hull = get_or_create_col('02_OPERATOR_HULL')
col_frame = get_or_create_col('03_LOAD_FRAME')
col_tools = get_or_create_col('06_MANIPULATORS')

# Materials
def get_or_create_mat(name, color, metallic=0.0, roughness=0.5, emit=0.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
        if emit > 0:
            bsdf.inputs['Emission Color'].default_value = color
            bsdf.inputs['Emission Strength'].default_value = emit
    return mat

mat_iron = get_or_create_mat('QA_Cast_Iron', (0.10, 0.10, 0.11, 1.0), metallic=0.85, roughness=0.42)
mat_bronze = get_or_create_mat('QA_Cast_Bronze', (0.45, 0.28, 0.12, 1.0), metallic=0.90, roughness=0.35)
mat_amber = get_or_create_mat('QA_Amber_Visor', (1.0, 0.50, 0.04, 1.0), emit=5.0)
mat_rubber = get_or_create_mat('QA_Joint_Rubber', (0.04, 0.04, 0.05, 1.0), metallic=0.1, roughness=0.85)

def tag_obj(obj, name, col, mat=mat_iron, driver='spine'):
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
    # Ensure smooth shading
    for poly in obj.data.polygons:
        poly.use_smooth = True
    # Add Rig modifier
    arm = bpy.data.objects.get('Varek_Original_Rig') or bpy.data.objects.get('Armature')
    if arm and 'Rigid_Armature' not in obj.modifiers:
        mod = obj.modifiers.new(name='Rigid_Armature', type='ARMATURE')
        mod.object = arm
    return obj

# Purge prototype operator objects
purge_names = [
    'Operator_Pressure_Helmet', 'Operator_Respirator_Boss_L', 'Operator_Respirator_Boss_R',
    'Operator_Visor_Aperture_Frame', 'Operator_Visor_Optical_Slit', 'Operator_Thoracic_Collar_Ring',
    'Thoracic_Center', 'Thoracic_Wing_L', 'Thoracic_Wing_R', 'Abdominal_Cage', 'Operator_Cell',
    'Operator_Brow', 'Operator_Visor_Guard'
]
for n in purge_names:
    o = bpy.data.objects.get(n)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)

# -----------------------------------------------------------------------------
# 2. PHASE 1: CONTINUOUS CAST CUIRASS & HIGH-WALLED GORGET RAMPART
# -----------------------------------------------------------------------------
# Contoured heavy cast-iron torso cuirass with continuous draft angles
bm = bmesh.new()
# Cross section layers: (Z, rx, ry_front, ry_back, center_y)
cuirass_profile = [
    (1.18, 0.28, -0.16, 0.18, 0.00), # Lower waist / pelvic girdle flange
    (1.36, 0.34, -0.23, 0.22, -0.01), # Abdominal expansion
    (1.58, 0.40, -0.27, 0.25, -0.02), # Mid pectoral / rib cage
    (1.78, 0.42, -0.28, 0.26, -0.01), # Upper chest / clavicle shelf
    (1.92, 0.32, -0.26, 0.25, 0.02),  # Base of protective gorget collar
    (2.04, 0.28, -0.24, 0.28, 0.05),  # High curved gorget defensive lip
]

rings = []
for z, rx, ry_f, ry_b, cy in cuirass_profile:
    ring = []
    for i in range(24):
        theta = 2.0 * math.pi * i / 24.0
        x = rx * math.sin(theta)
        y_r = ry_f if math.cos(theta) < 0 else ry_b
        y = cy + y_r * math.cos(theta)
        ring.append(bm.verts.new((x, y, z)))
    rings.append(ring)

for i in range(len(rings) - 1):
    r1, r2 = rings[i], rings[i+1]
    for j in range(24):
        bm.faces.new((r1[j], r1[(j+1)%24], r2[(j+1)%24], r2[j]))

bm.faces.new(reversed(rings[0]))
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.012, segments=2, affect='EDGES')
me_torso = bpy.data.meshes.new('Operator_Cuirass_Gorget_Mesh')
bm.to_mesh(me_torso)
bm.free()
torso_obj = bpy.data.objects.new('Operator_Cuirass_Gorget', me_torso)
tag_obj(torso_obj, 'Operator_Cuirass_Gorget', col_hull, mat_iron, driver='spine')

# Central Circular Mechanical Pressure Hatch
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=0.12, radius2=0.11, depth=0.05)
rot_x = Matrix.Rotation(math.radians(90.0), 4, 'X')
for v in bm.verts:
    v.co = rot_x @ v.co
    v.co.y += -0.30
    v.co.z += 1.58
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.005, segments=2, affect='EDGES')
me_hatch = bpy.data.meshes.new('Operator_Chest_Hatch_Mesh')
bm.to_mesh(me_hatch)
bm.free()
hatch_obj = bpy.data.objects.new('Operator_Chest_Hatch', me_hatch)
tag_obj(hatch_obj, 'Operator_Chest_Hatch', col_hull, mat_bronze, driver='spine')

# -----------------------------------------------------------------------------
# 3. OPERATOR HELMET & OPTICAL VIEWPORT (Nested inside gorget)
# -----------------------------------------------------------------------------
# Cast iron pressure dome seated low inside the neck rampart
bm = bmesh.new()
bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=16, radius=0.175)
for v in bm.verts:
    v.co.x *= 1.04
    v.co.y *= 1.10
    v.co.z *= 0.96
    v.co.z += 1.945
    v.co.y += 0.015
    # Stepped brow projection
    if 1.95 <= v.co.z <= 2.04 and v.co.y < -0.08:
        v.co.y -= 0.035
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.008, segments=2, affect='EDGES')
me_helm = bpy.data.meshes.new('Operator_Pressure_Helmet_Mesh')
bm.to_mesh(me_helm)
bm.free()
helm_obj = bpy.data.objects.new('Operator_Pressure_Helmet', me_helm)
tag_obj(helm_obj, 'Operator_Pressure_Helmet', col_hull, mat_iron, driver='spine')

# Deeply Recessed Amber Optical Slit
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts:
    v.co.x *= 0.090 # Width 0.18m
    v.co.y *= 0.015
    v.co.z *= 0.012 # Height 0.024m
    v.co.y += -0.175 # Recessed behind brow
    v.co.z += 1.940
me_slit = bpy.data.meshes.new('Operator_Visor_Slit_Mesh')
bm.to_mesh(me_slit)
bm.free()
slit_obj = bpy.data.objects.new('Operator_Visor_Slit', me_slit)
tag_obj(slit_obj, 'Operator_Visor_Slit', col_hull, mat_amber, driver='spine')

# Dual Cheek Respirator Housings
for side, s_sign in [('L', -1), ('R', 1)]:
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=0.040, radius2=0.034, depth=0.048)
    rot = Matrix.Rotation(math.radians(s_sign * 28.0), 4, 'Z') @ Matrix.Rotation(math.radians(18.0), 4, 'X')
    base_p = Vector((s_sign * 0.125, -0.165, 1.875))
    for v in bm.verts:
        v.co = rot @ v.co + base_p
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.004, segments=2, affect='EDGES')
    me_resp = bpy.data.meshes.new(f'Operator_Respirator_{side}_Mesh')
    bm.to_mesh(me_resp)
    bm.free()
    resp_obj = bpy.data.objects.new(f'Operator_Respirator_{side}', me_resp)
    tag_obj(resp_obj, f'Operator_Respirator_{side}', col_hull, mat_bronze, driver='spine')

# -----------------------------------------------------------------------------
# 4. SAVE V40 BLEND & RENDER TIER 1 WORKBENCH DIAGNOSTIC
# -----------------------------------------------------------------------------
bpy.ops.wm.save_as_mainfile(filepath=target_blend)
print(f'Successfully built Phase 1 Core Chassis in {target_blend}')

# Render Workbench MatCap Front & 3/4 Portrait
out_dir = Path('/home/aaron/animation/thulans-production/evidence/varek-v40-osint-juggernaut/phase1')
out_dir.mkdir(parents=True, exist_ok=True)

scene.frame_set(1)
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'MATCAP'
scene.display.shading.studio_light = 'check_normal+y.exr'
scene.render.resolution_x = 1080
scene.render.resolution_y = 1350
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

cam = scene.objects.get('Camera')
if cam is None:
    cam_data = bpy.data.cameras.new('Camera')
    cam = bpy.data.objects.new('Camera', cam_data)
    scene.collection.objects.link(cam)
scene.camera = cam

# View 1: Front Portrait
cam.location = Vector((0.0, -2.8, 1.85))
target = Vector((0.0, 0.0, 1.75))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 65.0
p1_front = str(out_dir / 'v40_phase1_front_workbench.png')
scene.render.filepath = p1_front
bpy.ops.render.render(write_still=True)
print(f'Rendered {p1_front}')

# View 2: Three-Quarter Portrait
cam.location = Vector((1.4, -2.4, 1.95))
target = Vector((0.0, 0.0, 1.75))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
p1_threequarter = str(out_dir / 'v40_phase1_threequarter_workbench.png')
scene.render.filepath = p1_threequarter
bpy.ops.render.render(write_still=True)
print(f'Rendered {p1_threequarter}')
