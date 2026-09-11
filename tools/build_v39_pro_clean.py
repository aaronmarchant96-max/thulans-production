import bpy
import bmesh
import math
from mathutils import Vector, Matrix

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# Create collection
col = bpy.data.collections.new('VAREK_PRO_CHASSIS')
scene.collection.children.link(col)

# Materials
mat_dark = bpy.data.materials.new('Mat_Cast_Iron')
mat_dark.use_nodes = True
b = mat_dark.node_tree.nodes.get('Principled BSDF')
b.inputs['Base Color'].default_value = (0.08, 0.08, 0.09, 1.0)
b.inputs['Metallic'].default_value = 0.8
b.inputs['Roughness'].default_value = 0.4

mat_bronze = bpy.data.materials.new('Mat_Bronze')
mat_bronze.use_nodes = True
b_br = mat_bronze.node_tree.nodes.get('Principled BSDF')
b_br.inputs['Base Color'].default_value = (0.4, 0.25, 0.12, 1.0)
b_br.inputs['Metallic'].default_value = 0.85
b_br.inputs['Roughness'].default_value = 0.35

mat_amber = bpy.data.materials.new('Mat_Visor')
mat_amber.use_nodes = True
b_amb = mat_amber.node_tree.nodes.get('Principled BSDF')
b_amb.inputs['Base Color'].default_value = (1.0, 0.5, 0.05, 1.0)
b_amb.inputs['Emission Color'].default_value = (1.0, 0.5, 0.05, 1.0)
b_amb.inputs['Emission Strength'].default_value = 4.0

def make_obj(name, mesh, mat=mat_dark):
    o = bpy.data.objects.new(name, mesh)
    o.data.materials.append(mat)
    col.objects.link(o)
    for p in o.data.polygons:
        p.use_smooth = True
    return o

# 1. TORSO CUIRASS & HIGH GORGET
# Revolve/loft a solid armored chest plate
bm = bmesh.new()
# Cross section layers: (Z, Radius X, Radius Y, Center Y)
cuirass_layers = [
    (1.15, 0.26, 0.18, 0.00), # Waist/pelvis coupling
    (1.35, 0.32, 0.24, -0.02), # Abdomen swell
    (1.58, 0.38, 0.28, -0.04), # Mid chest
    (1.78, 0.40, 0.28, -0.02), # Clavicle line
    (1.92, 0.30, 0.24, 0.02),  # Base of neck gorget
    (2.08, 0.26, 0.26, 0.05),  # High curved gorget rim
]
rings = []
for z, rx, ry, cy in cuirass_layers:
    ring = []
    for i in range(24):
        th = 2.0 * math.pi * i / 24.0
        x = rx * math.sin(th)
        y = cy + ry * math.cos(th)
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
me = bpy.data.meshes.new('Cuirass_Mesh')
bm.to_mesh(me)
bm.free()
make_obj('Torso_Cuirass', me)

# Central Chest Reactor/Hatch
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=0.11, radius2=0.10, depth=0.05)
rot_x = Matrix.Rotation(math.radians(90.0), 4, 'X')
for v in bm.verts:
    v.co = rot_x @ v.co
    v.co.y += -0.31
    v.co.z += 1.58
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.005, segments=2, affect='EDGES')
me = bpy.data.meshes.new('Chest_Hatch_Mesh')
bm.to_mesh(me)
bm.free()
make_obj('Chest_Hatch', me, mat_bronze)

# 2. HELMET & OPTICAL SLIT
bm = bmesh.new()
bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=16, radius=0.17)
for v in bm.verts:
    v.co.x *= 1.05
    v.co.y *= 1.12
    v.co.z += 1.94
    v.co.y += 0.02
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.008, segments=2, affect='EDGES')
me = bpy.data.meshes.new('Helmet_Mesh')
bm.to_mesh(me)
bm.free()
make_obj('Operator_Helmet', me)

# Visor Slit
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts:
    v.co.x *= 0.08
    v.co.y *= 0.02
    v.co.z *= 0.012
    v.co.y += -0.17
    v.co.z += 1.94
me = bpy.data.meshes.new('Slit_Mesh')
bm.to_mesh(me)
bm.free()
make_obj('Visor_Slit', me, mat_amber)

# 3. HEAVY FLARED PAULDRONS (Overlapping curved shells)
for side, s_sign in [('L', -1), ('R', 1)]:
    bm = bmesh.new()
    # 24-point flared curved dome
    bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=0.28)
    for v in bm.verts:
        if v.co.z < -0.05:
            v.co.z = -0.05
        v.co.x *= 1.15
        v.co.y *= 1.05
        v.co.x += s_sign * 0.52
        v.co.y += -0.02
        v.co.z += 1.82
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.01, segments=2, affect='EDGES')
    me = bpy.data.meshes.new(f'Pauldron_{side}_Mesh')
    bm.to_mesh(me)
    bm.free()
    make_obj(f'Pauldron_{side}', me)

# 4. LEGS (Thighs, Shins, Boots)
for side, s_sign in [('L', -1), ('R', 1)]:
    # Thigh
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=20, radius1=0.18, radius2=0.15, depth=0.42)
    for v in bm.verts:
        v.co.x += s_sign * 0.22
        v.co.y += -0.02
        v.co.z += 0.90
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.008, segments=2, affect='EDGES')
    me = bpy.data.meshes.new(f'Thigh_{side}_Mesh')
    bm.to_mesh(me)
    bm.free()
    make_obj(f'Thigh_{side}', me)

    # Shin
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=20, radius1=0.16, radius2=0.14, depth=0.44)
    for v in bm.verts:
        v.co.x += s_sign * 0.22
        v.co.y += -0.04
        v.co.z += 0.46
        # Knee bulwark
        if v.co.z > 0.60 and v.co.y < -0.02:
            v.co.y -= 0.07
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.008, segments=2, affect='EDGES')
    me = bpy.data.meshes.new(f'Shin_{side}_Mesh')
    bm.to_mesh(me)
    bm.free()
    make_obj(f'Shin_{side}', me)

    # Boot
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.22
        v.co.y *= 0.36
        v.co.z *= 0.16
        v.co.x += s_sign * 0.23
        v.co.y += -0.08
        v.co.z += 0.10
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.012, segments=2, affect='EDGES')
    me = bpy.data.meshes.new(f'Boot_{side}_Mesh')
    bm.to_mesh(me)
    bm.free()
    make_obj(f'Boot_{side}', me)

# 5. RIGHT FOREARM: CONICAL BORE-DRILL
bm = bmesh.new()
# Forearm housing
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=0.14, radius2=0.13, depth=0.28)
rot_x = Matrix.Rotation(math.radians(90.0), 4, 'X')
for v in bm.verts:
    v.co = rot_x @ v.co
    v.co.x += 0.54
    v.co.y += -0.22
    v.co.z += 1.28
# Drill Cone
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=0.13, radius2=0.01, depth=0.48)
for v in bm.verts[-26:]:
    v.co = rot_x @ v.co
    v.co.x += 0.54
    v.co.y += -0.60
    v.co.z += 1.28
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.006, segments=2, affect='EDGES')
me = bpy.data.meshes.new('Forearm_Drill_Mesh')
bm.to_mesh(me)
bm.free()
make_obj('Forearm_Drill', me)

# 6. LEFT FOREARM: HYDRAULIC RESCUE CLAW
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=20, radius1=0.13, radius2=0.12, depth=0.32)
for v in bm.verts:
    v.co.x += -0.54
    v.co.y += -0.04
    v.co.z += 1.25
# Dual Jaws
for j_sign in [-1, 1]:
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts[-8:]:
        v.co.x *= 0.04
        v.co.y *= 0.16
        v.co.z *= 0.07
        v.co.x += -0.54 + (j_sign * 0.07)
        v.co.y += -0.26
        v.co.z += 1.02
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.006, segments=2, affect='EDGES')
me = bpy.data.meshes.new('Forearm_Claw_Mesh')
bm.to_mesh(me)
bm.free()
make_obj('Forearm_Claw', me)

# Save & Render in Cycles
target_blend = '/home/aaron/animation/thulans-production/blender/candidates/varek-v39-pro-clean.blend'
bpy.ops.wm.save_as_mainfile(filepath=target_blend)

scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.device = 'CPU'
scene.render.resolution_x = 1080
scene.render.resolution_y = 1350
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

# Lighting
world = bpy.data.worlds.new('World_Studio')
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value = (0.05, 0.05, 0.06, 1.0)
bg.inputs['Strength'].default_value = 1.0

key_data = bpy.data.lights.new('Key_Light', 'AREA')
key_data.energy = 900
key_data.size = 2.5
key_data.color = (1.0, 0.95, 0.9)
key = bpy.data.objects.new('Key_Light', key_data)
key.location = (2.5, -4.0, 3.2)
scene.collection.objects.link(key)

fill_data = bpy.data.lights.new('Fill_Light', 'AREA')
fill_data.energy = 350
fill_data.size = 3.5
fill_data.color = (0.75, 0.85, 1.0)
fill = bpy.data.objects.new('Fill_Light', fill_data)
fill.location = (-3.5, -2.5, 2.0)
scene.collection.objects.link(fill)

rim_data = bpy.data.lights.new('Rim_Light', 'AREA')
rim_data.energy = 1400
rim_data.size = 3.0
rim_data.color = (1.0, 0.9, 0.8)
rim = bpy.data.objects.new('Rim_Light', rim_data)
rim.location = (0.0, 4.0, 3.0)
scene.collection.objects.link(rim)

# Camera
cam_data = bpy.data.cameras.new('Camera')
cam = bpy.data.objects.new('Camera', cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

cam.location = Vector((2.2, -4.2, 1.6))
target = Vector((0.0, 0.0, 1.2))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 55.0

out_render = '/home/aaron/animation/thulans-production/evidence/varek-v39-pro-clean_fullbody.png'
scene.render.filepath = out_render
bpy.ops.render.render(write_still=True)
print(f'Rendered clean 3D chassis to {out_render}')
