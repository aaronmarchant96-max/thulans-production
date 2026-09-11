import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler
from pathlib import Path

R = Path('/home/aaron/animation/thulans-production')
TARGET_BLEND = R / 'blender/candidates/varek-v38-cloth-pass.blend'

bpy.ops.wm.open_mainfile(filepath=str(TARGET_BLEND))
scene = bpy.context.scene

load_col = bpy.data.collections.get('03_LOAD_FRAME')
assert load_col is not None, '03_LOAD_FRAME not found'

mat_dark = bpy.data.materials.get('QA_Dark_Clay') or bpy.data.materials.get('Warm charcoal cast iron')
mat_iron = bpy.data.materials.get('QA_Iron_Clay') or bpy.data.materials.get('Warm charcoal cast iron')
mat_cloth = bpy.data.materials.get('QA_Gren_Skildus_Clay') or bpy.data.materials.get('Gren-Skildus Cloth') or mat_dark

# 1. PURGE PREVIOUS GREN SKILDUS OBJECTS
purge_names = [
    'Gren_Skildus', 'Gren_Mount_Lower', 'Gren_Mount_Upper',
    'Gren_Skildus_Mantle', 'Gren_Skildus_Clasp_Ring', 'Gren_Skildus_Mount_Bracket'
]
for name in purge_names:
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

def tag_part(obj, name, mat, driver='upper_arm.L'):
    obj.name = name
    obj['production_geometry'] = True
    obj['form_importance'] = 'SECONDARY'
    obj['rigid_driver_bone'] = driver
    if mat:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    if obj.name not in load_col.objects:
        load_col.objects.link(obj)
    if obj.name in scene.collection.objects:
        scene.collection.objects.unlink(obj)
    arm = bpy.data.objects.get('Varek_Original_Rig') or bpy.data.objects.get('Rig_Armature') or bpy.data.objects.get('Armature')
    if arm and 'Rigid_Armature' not in obj.modifiers:
        mod = obj.modifiers.new(name='Rigid_Armature', type='ARMATURE')
        mod.object = arm
    return obj

# -----------------------------------------------------------------------------
# 2. GREN-SKILDUS BRONZE/IRON BROOCH CLASP (Rigid anchor on Shoulder)
# -----------------------------------------------------------------------------
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=0.045, radius2=0.040, depth=0.030)
rot = Matrix.Rotation(math.radians(90.0), 4, 'X')
for v in bm.verts:
    v.co = rot @ v.co
    v.co.x += -0.615
    v.co.y += -0.115
    v.co.z += 1.885
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.005, segments=2, affect='EDGES')
me_clasp = bpy.data.meshes.new('Gren_Skildus_Clasp_Ring_Mesh')
bm.to_mesh(me_clasp)
bm.free()
clasp_obj = bpy.data.objects.new('Gren_Skildus_Clasp_Ring', me_clasp)
tag_part(clasp_obj, 'Gren_Skildus_Clasp_Ring', mat_iron, driver='upper_arm.L')

# -----------------------------------------------------------------------------
# 3. GREN-SKILDUS CEREMONIAL MANTLE (Heavy, draped woven canvas across left pauldron)
# Outer flank of Left Shoulder: X: [-0.85, -0.52], Y: [-0.22, 0.12], Z: [1.38, 1.92]
# -----------------------------------------------------------------------------
bm = bmesh.new()

# Cross-section slices descending in Z over the shoulder down to mid-arm:
# (z, x_center, x_halfwidth, y_front, y_back, fold_depth)
drape_layers = [
    # Top gathered anchor under clasp
    (1.905, -0.615, 0.050, -0.110, 0.040, 0.015),
    # Swell over shoulder cap dome
    (1.840, -0.645, 0.115, -0.160, 0.095, 0.035),
    # Upper bicep primary drape (heavy forward fold wave)
    (1.720, -0.665, 0.130, -0.175, 0.100, 0.040),
    # Mid-arm taper (sloping down outer flank)
    (1.580, -0.655, 0.115, -0.155, 0.080, 0.030),
    # Asymmetric broken hem
    (1.420, -0.635, 0.090, -0.125, 0.050, 0.020),
]

rings = []
for z, xc, xh, yf, yb, fd in drape_layers:
    ring_verts = []
    # 8-point heavy fabric profile with deep front drape crease
    x_outer = xc - xh
    x_inner = xc + xh * 0.6
    y_mid = (yf + yb) * 0.5
    
    pts = [
        # Front outer fold crest
        (x_outer * 0.95, yf, z),
        # Front inner crease (folds back)
        (xc, yf + fd, z),
        # Front inner wrap
        (x_inner, yf * 0.6 + yb * 0.4, z),
        # Inner arm contact
        (x_inner, yb, z),
        # Rear inner
        (xc, yb + fd * 0.5, z),
        # Rear outer fold crest
        (x_outer * 0.92, yb, z),
        # Outer lateral ridge
        (x_outer, y_mid, z),
        # Outer front lead
        (x_outer * 0.98, yf * 0.75 + y_mid * 0.25, z),
    ]
    for px, py, pz in pts:
        v = bm.verts.new((px, py, pz))
        ring_verts.append(v)
    rings.append(ring_verts)

for i in range(len(rings) - 1):
    r1 = rings[i]
    r2 = rings[i+1]
    n = len(r1)
    for j in range(n):
        v1 = r1[j]
        v2 = r1[(j + 1) % n]
        v3 = r2[(j + 1) % n]
        v4 = r2[j]
        bm.faces.new((v1, v2, v3, v4))

bm.faces.new(reversed(rings[0])) # Cap top
bm.faces.new(rings[-1])          # Cap hem

bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()

bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.008, segments=2, affect='EDGES')

me_cloth = bpy.data.meshes.new('Gren_Skildus_Mantle_Mesh')
bm.to_mesh(me_cloth)
bm.free()

cloth_obj = bpy.data.objects.new('Gren_Skildus_Mantle', me_cloth)
tag_part(cloth_obj, 'Gren_Skildus_Mantle', mat_cloth, driver='upper_arm.L')

bpy.ops.wm.save_as_mainfile(filepath=str(TARGET_BLEND))
print(f'Saved correctly positioned Gren-Skildus in {TARGET_BLEND}')
