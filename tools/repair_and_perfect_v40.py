import bpy
import bmesh
from mathutils import Vector, Matrix, Euler
import math

# 1. Load the good base snapshot
src_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v40-osint-juggernaut.blend1'
target_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v40-osint-juggernaut.blend'
bpy.ops.wm.open_mainfile(filepath=src_blend)
scene = bpy.context.scene
rig = bpy.data.objects.get('Varek_Original_Rig')

print("Starting Surgical Repair of V40 Base...")

# Clean helper
def clean_mesh(obj):
    if not obj or obj.type != 'MESH':
        return
    for poly in obj.data.polygons:
        poly.use_smooth = True
    wn = next((m for m in obj.modifiers if m.type == 'WEIGHTED_NORMAL'), None)
    if not wn:
        wn = obj.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
        wn.keep_sharp = True

# Materials
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

mat_iron = get_or_create_material('QA_PBR_Weathered_CastIron', (0.08, 0.08, 0.09, 1.0), 0.88, 0.45)
mat_bronze = get_or_create_material('QA_PBR_Weathered_Bronze', (0.48, 0.32, 0.14, 1.0), 0.90, 0.30)
mat_amber = get_or_create_material('QA_Amber_Visor', (1.0, 0.55, 0.05, 1.0), 0.0, 0.1, (1.0, 0.6, 0.05, 1.0), 8.0)
mat_cloth = get_or_create_material('QA_PBR_Gren_Skildus_Wool', (0.05, 0.10, 0.06, 1.0), 0.0, 0.92)
mat_rubber = get_or_create_material('QA_PBR_Flexible_Rubber', (0.03, 0.03, 0.03, 1.0), 0.1, 0.70)
mat_steel = get_or_create_material('QA_PBR_Hardened_ToolSteel', (0.38, 0.38, 0.40, 1.0), 0.95, 0.20)

# =============================================================================
# 1. REMOVE MISPLACED / FLOATING OBJECTS
# =============================================================================
# Remove floating struts and front-placed accumulators
for o in list(bpy.data.objects):
    if o.name.startswith(('Dorsal_Accumulator', 'Mech_Thigh_Bracing', 'Collar_Conduit')):
        # Check if it was placed on the front (Y > 0)
        if o.location.y > 0 or o.name.startswith('Mech_Thigh_Bracing'):
            bpy.data.objects.remove(o, do_unlink=True)

# Also remove any duplicate toruses on right shoulder
for o in list(bpy.data.objects):
    if 'Puldron' in o.name and '_R' in o.name and 'Trim' in o.name:
        bpy.data.objects.remove(o, do_unlink=True)

# =============================================================================
# 2. ADD SOLID HELMET DOME, VISOR & REBREATHER CHEEK CANISTERS
# =============================================================================
# Helmet Dome
old_h = bpy.data.objects.get('Sculpt_Helmet_Dome')
if old_h:
    bpy.data.objects.remove(old_h, do_unlink=True)

bm = bmesh.new()
bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=16, radius=0.17)
for v in bm.verts:
    v.co.z = v.co.z * 1.08 + 1.88
    v.co.y = v.co.y * 1.05 + 0.02
me = bpy.data.meshes.new('Sculpt_Helmet_Dome')
bm.to_mesh(me)
bm.free()
helm_obj = bpy.data.objects.new('Sculpt_Helmet_Dome', me)
bpy.context.collection.objects.link(helm_obj)
clean_mesh(helm_obj)
helm_obj.data.materials.append(mat_iron)
if rig:
    mod = helm_obj.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = rig
    vg = helm_obj.vertex_groups.new(name='head')
    vg.add(range(len(me.vertices)), 1.0, 'REPLACE')

# Glowing Amber Visor
old_v = bpy.data.objects.get('Sculpt_Helmet_Visor')
if old_v:
    bpy.data.objects.remove(old_v, do_unlink=True)

bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts:
    v.co.x *= 0.10
    v.co.y *= 0.025
    v.co.z *= 0.022
    v.co.y += 0.175
    v.co.z += 1.91
me = bpy.data.meshes.new('Sculpt_Helmet_Visor')
bm.to_mesh(me)
bm.free()
visor_obj = bpy.data.objects.new('Sculpt_Helmet_Visor', me)
bpy.context.collection.objects.link(visor_obj)
clean_mesh(visor_obj)
visor_obj.data.materials.append(mat_amber)
if rig:
    mod = visor_obj.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = rig
    vg = visor_obj.vertex_groups.new(name='head')
    vg.add(range(len(me.vertices)), 1.0, 'REPLACE')

# Dual Rebreather Cheek Canisters (Left & Right)
for side, sign in [('L', 1), ('R', -1)]:
    old_c = bpy.data.objects.get(f'Sculpt_Rebreather_Canister_{side}')
    if old_c:
        bpy.data.objects.remove(old_c, do_unlink=True)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=0.042, radius2=0.042, depth=0.055)
    rot = Euler((math.radians(35), math.radians(20 * sign), math.radians(-25 * sign))).to_matrix()
    for v in bm.verts:
        v.co = rot @ v.co
        v.co.x += 0.09 * sign
        v.co.y += 0.14
        v.co.z += 1.82
    me = bpy.data.meshes.new(f'Sculpt_Rebreather_Canister_{side}')
    bm.to_mesh(me)
    bm.free()
    can_obj = bpy.data.objects.new(f'Sculpt_Rebreather_Canister_{side}', me)
    bpy.context.collection.objects.link(can_obj)
    clean_mesh(can_obj)
    can_obj.data.materials.append(mat_bronze)
    if rig:
        mod = can_obj.modifiers.new(name="Armature", type='ARMATURE')
        mod.object = rig
        vg = can_obj.vertex_groups.new(name='head')
        vg.add(range(len(me.vertices)), 1.0, 'REPLACE')

# =============================================================================
# 3. POSITION ACCUMULATOR CYLINDERS ON THE BACK (DORSAL)
# =============================================================================
for name in ['Dorsal_Accumulator_Upper', 'Dorsal_Accumulator_Lower', 'Dorsal_Exhaust_L', 'Dorsal_Exhaust_R']:
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)

# Horizontal Surge Accumulators on BACK (Y = -0.34)
for acc_name, z_pos in [('Upper', 1.48), ('Lower', 1.32)]:
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=0.065, radius2=0.065, depth=0.48)
    rot = Euler((0, math.radians(90), 0)).to_matrix()
    for v in bm.verts:
        v.co = rot @ v.co
        v.co.y -= 0.32 # Strictly on BACK
        v.co.z += z_pos
    me = bpy.data.meshes.new(f'Dorsal_Accumulator_{acc_name}')
    bm.to_mesh(me)
    bm.free()
    acc_obj = bpy.data.objects.new(f'Dorsal_Accumulator_{acc_name}', me)
    bpy.context.collection.objects.link(acc_obj)
    clean_mesh(acc_obj)
    acc_obj.data.materials.append(mat_iron)
    if rig:
        mod = acc_obj.modifiers.new(name="Armature", type='ARMATURE')
        mod.object = rig
        vg = acc_obj.vertex_groups.new(name='spine_03')
        vg.add(range(len(me.vertices)), 1.0, 'REPLACE')

# =============================================================================
# 4. SOLIDIFY CUISSES & GROIN CODPLATE (NO HOLLOW VOIDS)
# =============================================================================
for side, sign in [('L', 1), ('R', -1)]:
    cuisse = bpy.data.objects.get(f'Sculpt_Cuisse_{side}')
    if cuisse:
        # Ensure cuisse has top cap and solid volume
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=20, radius1=0.21, radius2=0.17, depth=0.36)
        for v in bm.verts:
            v.co.x += 0.24 * sign
            v.co.z += 0.94
            v.co.y *= 0.90
        bm.to_mesh(cuisse.data)
        bm.free()
        cuisse.data.update()
        clean_mesh(cuisse)

# Center Groin Codplate
codplate = bpy.data.objects.get('Sculpt_Pelvic_Codplate')
if codplate:
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=0.15, radius2=0.08, depth=0.28)
    for v in bm.verts:
        v.co.y += 0.12
        v.co.z += 1.02
        if v.co.y > 0.05:
            v.co.y += 0.04 # Keel ridge
    bm.to_mesh(codplate.data)
    bm.free()
    codplate.data.update()
    clean_mesh(codplate)

# =============================================================================
# 5. RE-SCULPT GREN-SKILDUS MANTLE ON RIGHT SHOULDER (VIEWER'S LEFT)
# =============================================================================
# Torc Clasp
old_t = bpy.data.objects.get('Sculpt_Gren_Skildus_Torc_Clasp')
if old_t:
    bpy.data.objects.remove(old_t, do_unlink=True)

bpy.ops.mesh.primitive_torus_add(
    align='WORLD', location=(-0.28, 0.22, 1.76),
    rotation=(math.radians(35), math.radians(-25), 0),
    major_radius=0.065, minor_radius=0.015,
    major_segments=20, minor_segments=10
)
torc = bpy.context.active_object
torc.name = 'Sculpt_Gren_Skildus_Torc_Clasp'
clean_mesh(torc)
torc.data.materials.append(mat_bronze)
if rig:
    mod = torc.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = rig
    vg = torc.vertex_groups.new(name='clavicle_r')
    vg.add(range(len(torc.data.vertices)), 1.0, 'REPLACE')

# Mantle Cloth Mesh
mantle = bpy.data.objects.get('Sculpt_Gren_Skildus_Mantle')
if mantle:
    bm = bmesh.new()
    rows, cols = 18, 10
    grid = []
    for r in range(rows):
        row_verts = []
        u = r / (rows - 1)
        for c in range(cols):
            v = c / (cols - 1)
            angle = (v - 0.25) * math.pi * 0.75
            rad = 0.28 + 0.14 * u + 0.02 * math.sin(u * 12.0 + c * 3.0)
            x = -0.32 - rad * math.cos(angle) * (0.8 + 0.3 * u)
            y = 0.10 + rad * math.sin(angle) * (0.85 + 0.2 * u)
            z = 1.78 - u * 1.18
            if u > 0.85:
                z -= 0.05 * math.sin(c * 5.0)
            pos = Vector((x, y, z))
            if u < 0.12:
                pos = Vector((-0.28, 0.22, 1.76)).lerp(pos, u / 0.12)
            row_verts.append(bm.verts.new(pos))
        grid.append(row_verts)

    for r in range(rows - 1):
        for c in range(cols - 1):
            bm.faces.new([grid[r][c], grid[r+1][c], grid[r+1][c+1], grid[r][c+1]])

    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.018)
    bm.to_mesh(mantle.data)
    bm.free()
    mantle.data.update()
    clean_mesh(mantle)
    mantle.data.materials.clear()
    mantle.data.materials.append(mat_cloth)

# =============================================================================
# 6. ENFORCE EXACT KINEMATIC SCALE & GROUNDING (2.4384m Height, 0.0000m Ground)
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

# Save target blend
bpy.ops.wm.save_as_mainfile(filepath=target_blend)
print(f"SUCCESS: Surgical repair applied to {target_blend}")
