import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler
from pathlib import Path

# Initialize new Blender file
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# Create collections
main_col = bpy.data.collections.new('VAREK_JUGGERNAUT')
scene.collection.children.link(main_col)

# Materials setup
mat_iron = bpy.data.materials.new('Cast_Iron_Dark')
mat_iron.use_nodes = True
b_iron = mat_iron.node_tree.nodes.get('Principled BSDF')
b_iron.inputs['Base Color'].default_value = (0.12, 0.12, 0.13, 1.0)
b_iron.inputs['Metallic'].default_value = 0.85
b_iron.inputs['Roughness'].default_value = 0.38

mat_bronze = bpy.data.materials.new('Cast_Bronze_Trim')
mat_bronze.use_nodes = True
b_br = mat_bronze.node_tree.nodes.get('Principled BSDF')
b_br.inputs['Base Color'].default_value = (0.45, 0.28, 0.12, 1.0)
b_br.inputs['Metallic'].default_value = 0.9
b_br.inputs['Roughness'].default_value = 0.32

mat_amber = bpy.data.materials.new('Amber_Visor_Slit')
mat_amber.use_nodes = True
b_amb = mat_amber.node_tree.nodes.get('Principled BSDF')
b_amb.inputs['Base Color'].default_value = (1.0, 0.5, 0.05, 1.0)
b_amb.inputs['Emission Color'].default_value = (1.0, 0.5, 0.05, 1.0)
b_amb.inputs['Emission Strength'].default_value = 5.0

mat_cloth = bpy.data.materials.new('Gren_Skildus_Green')
mat_cloth.use_nodes = True
b_cloth = mat_cloth.node_tree.nodes.get('Principled BSDF')
b_cloth.inputs['Base Color'].default_value = (0.04, 0.12, 0.06, 1.0)
b_cloth.inputs['Roughness'].default_value = 0.85

def add_part(name, mesh_data, mat=mat_iron):
    obj = bpy.data.objects.new(name, mesh_data)
    obj.data.materials.append(mat)
    main_col.objects.link(obj)
    # Add smooth shading and subdivision
    for poly in obj.data.polygons:
        poly.use_smooth = True
    sub = obj.modifiers.new('Subdiv', 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 2
    return obj

# -----------------------------------------------------------------------------
# 1. TORSO & HIGH-WALLED GORGET (Continuous cast cuirass)
# -----------------------------------------------------------------------------
# Torso cross-sections from pelvis (Z=1.1) to high gorget lip (Z=2.08)
bm = bmesh.new()
layers = [
    # (z, rx, ry_front, ry_back)
    (1.10, 0.28, -0.16, 0.18), # Pelvis belt line
    (1.28, 0.32, -0.22, 0.22), # Abdomen swell
    (1.50, 0.38, -0.26, 0.25), # Mid-chest / pectoral breadth
    (1.72, 0.42, -0.28, 0.26), # Upper chest / shoulder line
    (1.86, 0.34, -0.26, 0.24), # Base of neck / collar flange
    (1.98, 0.28, -0.24, 0.26), # Mid-gorget defensive wall
    (2.08, 0.26, -0.20, 0.28), # High curved rear cowl / gorget rim
]

rings = []
for z, rx, ry_f, ry_b in layers:
    ring = []
    # 16-point smooth elliptical profile
    for i in range(16):
        theta = 2.0 * math.pi * i / 16.0
        x = rx * math.sin(theta)
        # Asymmetric front/back depth
        y_rad = ry_f if math.cos(theta) < 0 else ry_b
        y = y_rad * math.cos(theta)
        v = bm.verts.new((x, y, z))
        ring.append(v)
    rings.append(ring)

for i in range(len(rings) - 1):
    r1, r2 = rings[i], rings[i+1]
    for j in range(16):
        bm.faces.new((r1[j], r1[(j+1)%16], r2[(j+1)%16], r2[j]))

bm.faces.new(reversed(rings[0]))
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.012, segments=2, affect='EDGES')
me_torso = bpy.data.meshes.new('Torso_Cuirass_Mesh')
bm.to_mesh(me_torso)
bm.free()
torso_obj = add_part('Torso_Cuirass', me_torso)

# Central pressure hatch medallion
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=0.12, radius2=0.11, depth=0.04)
rot = Matrix.Rotation(math.radians(90.0), 4, 'X')
for v in bm.verts:
    v.co = rot @ v.co
    v.co.z += 1.52
    v.co.y += -0.27
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.006, segments=2, affect='EDGES')
me_hatch = bpy.data.meshes.new('Chest_Hatch_Mesh')
bm.to_mesh(me_hatch)
bm.free()
add_part('Chest_Hatch', me_hatch, mat_bronze)

# -----------------------------------------------------------------------------
# 2. LOW-SEATED RECESSED DOME HELMET & OPTICAL SLIT
# -----------------------------------------------------------------------------
bm = bmesh.new()
# Hemispherical dome nested deep inside the gorget collar at Z=1.86 to 2.06
bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=16, radius=0.17)
for v in bm.verts:
    v.co.x *= 1.05
    v.co.y *= 1.10
    v.co.z *= 0.95
    v.co.z += 1.95
    v.co.y += -0.02
    # Flatten brow and face slope
    if v.co.z < 1.98 and v.co.y < -0.08:
        v.co.y -= 0.03
me_head = bpy.data.meshes.new('Operator_Helmet_Mesh')
bm.to_mesh(me_head)
bm.free()
add_part('Operator_Helmet', me_head)

# Amber Optical Slit
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts:
    v.co.x *= 0.08
    v.co.y *= 0.015
    v.co.z *= 0.012
    v.co.y += -0.190
    v.co.z += 1.940
me_slit = bpy.data.meshes.new('Visor_Amber_Slit_Mesh')
bm.to_mesh(me_slit)
bm.free()
add_part('Visor_Amber_Slit', me_slit, mat_amber)

# Dual cheek respirators
for side, sign in [('L', -1), ('R', 1)]:
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=0.038, radius2=0.034, depth=0.045)
    rot = Matrix.Rotation(math.radians(sign * 28.0), 4, 'Z') @ Matrix.Rotation(math.radians(20.0), 4, 'X')
    base_p = Vector((sign * 0.115, -0.175, 1.880))
    for v in bm.verts:
        v.co = rot @ v.co + base_p
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.004, segments=2, affect='EDGES')
    me_resp = bpy.data.meshes.new(f'Respirator_{side}_Mesh')
    bm.to_mesh(me_resp)
    bm.free()
    add_part(f'Respirator_{side}', me_resp, mat_bronze)

# -----------------------------------------------------------------------------
# 3. MASSIVE FLARED SHOULDER PAULDRONS
# -----------------------------------------------------------------------------
for side, sign in [('L', -1), ('R', 1)]:
    bm = bmesh.new()
    # 3-tier curved pauldron shell
    bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=0.28)
    for v in bm.verts:
        # Cut lower/inner hemisphere
        if v.co.z < 0.0 or (sign * v.co.x < -0.05):
            v.co.z *= 0.2
        v.co.x *= 1.15
        v.co.y *= 0.95
        v.co.z *= 0.85
        # Position over shoulder
        v.co.x += sign * 0.54
        v.co.y += -0.02
        v.co.z += 1.78
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.008, segments=2, affect='EDGES')
    me_p = bpy.data.meshes.new(f'Pauldron_{side}_Mesh')
    bm.to_mesh(me_p)
    bm.free()
    add_part(f'Pauldron_{side}', me_p, mat_iron)

# -----------------------------------------------------------------------------
# 4. FOREARM TOOL STATIONS (Right: Conical Drill, Left: Hydraulic Shear)
# -----------------------------------------------------------------------------
# Right Forearm: Pneumatic Conical Tectonic Bore-Drill
bm = bmesh.new()
# Arm collar housing
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=0.15, radius2=0.14, depth=0.28)
rot = Matrix.Rotation(math.radians(90.0), 4, 'X')
for v in bm.verts:
    v.co = rot @ v.co
    v.co.x += 0.58
    v.co.y += -0.28
    v.co.z += 1.25

# Conical spiral drill bit
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=0.14, radius2=0.01, depth=0.48)
for v in bm.verts[-26:]: # Bit vertices
    v.co = rot @ v.co
    v.co.x += 0.58
    v.co.y += -0.66
    v.co.z += 1.25

bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.006, segments=2, affect='EDGES')
me_drill = bpy.data.meshes.new('Forearm_Drill_Mesh')
bm.to_mesh(me_drill)
bm.free()
add_part('Forearm_Drill', me_drill, mat_iron)

# Left Forearm: Heavy Hydraulic Rescue Clamp / Pincer
bm = bmesh.new()
# Forearm sleeve
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=20, radius1=0.14, radius2=0.13, depth=0.32)
rot_z = Matrix.Rotation(math.radians(0.0), 4, 'X')
for v in bm.verts:
    v.co.x += -0.58
    v.co.y += -0.05
    v.co.z += 1.22

# Dual pincer jaws
for j_sign in [-1, 1]:
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts[-8:]:
        v.co.x *= 0.04
        v.co.y *= 0.16
        v.co.z *= 0.08
        # Taper jaw tip
        if v.co.y < 0:
            v.co.z *= 0.5
        v.co.x += -0.58 + (j_sign * 0.08)
        v.co.y += -0.26
        v.co.z += 0.98 + (j_sign * 0.06)

bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.006, segments=2, affect='EDGES')
me_clamp = bpy.data.meshes.new('Forearm_Rescue_Clamp_Mesh')
bm.to_mesh(me_clamp)
bm.free()
add_part('Forearm_Rescue_Clamp', me_clamp, mat_iron)

# -----------------------------------------------------------------------------
# 5. LOWER CHASSIS (Thick armored thighs, knees & tectonic anchor boots)
# -----------------------------------------------------------------------------
for side, sign in [('L', -1), ('R', 1)]:
    # Thigh Bulkwark
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=18, radius1=0.19, radius2=0.16, depth=0.42)
    for v in bm.verts:
        v.co.x += sign * 0.22
        v.co.y += -0.02
        v.co.z += 0.88
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.008, segments=2, affect='EDGES')
    me_thigh = bpy.data.meshes.new(f'Thigh_{side}_Mesh')
    bm.to_mesh(me_thigh)
    bm.free()
    add_part(f'Thigh_{side}', me_thigh)

    # Shin Greave & Knee Cap
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=18, radius1=0.17, radius2=0.15, depth=0.46)
    for v in bm.verts:
        v.co.x += sign * 0.23
        v.co.y += -0.04
        v.co.z += 0.44
        # Protruding knee shield
        if v.co.z > 0.58 and v.co.y < -0.02:
            v.co.y -= 0.08
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.008, segments=2, affect='EDGES')
    me_shin = bpy.data.meshes.new(f'Shin_{side}_Mesh')
    bm.to_mesh(me_shin)
    bm.free()
    add_part(f'Shin_{side}', me_shin)

    # Tectonic Anchor Boot
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.22
        v.co.y *= 0.36
        v.co.z *= 0.16
        v.co.x += sign * 0.24
        v.co.y += -0.08
        v.co.z += 0.10
        # Forward claw toe taper
        if v.co.y < -0.08:
            v.co.z *= 0.7
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.010, segments=2, affect='EDGES')
    me_boot = bpy.data.meshes.new(f'Anchor_Boot_{side}_Mesh')
    bm.to_mesh(me_boot)
    bm.free()
    add_part(f'Anchor_Boot_{side}', me_boot)

# -----------------------------------------------------------------------------
# 6. GREN-SKILDUS MANTLE (Draped over left pauldron with bronze brooch)
# -----------------------------------------------------------------------------
bm = bmesh.new()
# Sculpted cloth flow descending from left pauldron
drape_layers = [
    (1.88, -0.42, 0.06, -0.16, 0.02),
    (1.76, -0.46, 0.12, -0.22, 0.06),
    (1.58, -0.48, 0.16, -0.24, 0.08),
    (1.36, -0.46, 0.18, -0.22, 0.06),
    (1.10, -0.42, 0.14, -0.18, 0.04),
]
rings = []
for z, xc, xw, yf, yb in drape_layers:
    ring = []
    pts = [
        (xc - xw, yf, z),
        (xc, yf + 0.02, z),
        (xc + xw, yf, z),
        (xc + xw, yb, z),
        (xc, yb - 0.01, z),
        (xc - xw, yb, z),
    ]
    for px, py, pz in pts:
        ring.append(bm.verts.new((px, py, pz)))
    rings.append(ring)

for i in range(len(rings) - 1):
    r1, r2 = rings[i], rings[i+1]
    for j in range(6):
        bm.faces.new((r1[j], r1[(j+1)%6], r2[(j+1)%6], r2[j]))

bm.faces.new(reversed(rings[0]))
bm.faces.new(rings[-1])
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.008, segments=2, affect='EDGES')
me_cloth = bpy.data.meshes.new('Gren_Skildus_Mantle_Mesh')
bm.to_mesh(me_cloth)
bm.free()
add_part('Gren_Skildus_Mantle', me_cloth, mat_cloth)

# Brooch Ring
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=20, radius1=0.055, radius2=0.055, depth=0.025)
rot = Matrix.Rotation(math.radians(90.0), 4, 'X')
for v in bm.verts:
    v.co = rot @ v.co
    v.co.x += -0.40
    v.co.y += -0.22
    v.co.z += 1.82
me_brooch = bpy.data.meshes.new('Gren_Brooch_Mesh')
bm.to_mesh(me_brooch)
bm.free()
add_part('Gren_Brooch', me_brooch, mat_bronze)

# -----------------------------------------------------------------------------
# 7. SAVE BLEND & RENDER DIAGNOSTIC PORTRAIT & FULL BODY
# -----------------------------------------------------------------------------
target_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v39-juggernaut-chassis.blend'
bpy.ops.wm.save_as_mainfile(filepath=target_blend)
print(f'Successfully saved 3D Juggernaut model to {target_blend}')

# Setup Cycles Render
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.device = 'CPU'
scene.render.resolution_x = 1080
scene.render.resolution_y = 1350
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

# Studio Environment Lighting
world = bpy.data.worlds.new('World_Studio')
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value = (0.05, 0.05, 0.06, 1.0)
bg.inputs['Strength'].default_value = 1.0

# Key Light
key_data = bpy.data.lights.new('Key_Light', 'AREA')
key_data.energy = 900
key_data.size = 2.5
key_data.color = (1.0, 0.95, 0.9)
key = bpy.data.objects.new('Key_Light', key_data)
key.location = (2.5, -4.0, 3.2)
scene.collection.objects.link(key)

# Fill Light
fill_data = bpy.data.lights.new('Fill_Light', 'AREA')
fill_data.energy = 350
fill_data.size = 3.5
fill_data.color = (0.75, 0.85, 1.0)
fill = bpy.data.objects.new('Fill_Light', fill_data)
fill.location = (-3.5, -2.5, 2.0)
scene.collection.objects.link(fill)

# Rim Light
rim_data = bpy.data.lights.new('Rim_Light', 'AREA')
rim_data.energy = 1400
rim_data.size = 3.0
rim_data.color = (1.0, 0.9, 0.8)
rim = bpy.data.objects.new('Rim_Light', rim_data)
rim.location = (0.0, 4.0, 3.0)
scene.collection.objects.link(rim)

# Setup Camera
cam_data = bpy.data.cameras.new('Camera')
cam = bpy.data.objects.new('Camera', cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

# View 1: 3/4 Hero Full Body View
cam.location = Vector((2.2, -4.2, 1.6))
target = Vector((0.0, 0.0, 1.2))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 55.0

out_render = '/home/aaron/animation/thulans-production/evidence/varek-v39-juggernaut-chassis_fullbody.png'
scene.render.filepath = out_render
bpy.ops.render.render(write_still=True)
print(f'Rendered full body to {out_render}')
