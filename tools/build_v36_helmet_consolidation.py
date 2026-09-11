import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler
from pathlib import Path

R = Path('/home/aaron/animation/thulans-production')
TARGET_BLEND = R / 'blender/candidates/varek-v36-helmet-pass.blend'
RENDER_OUT = R / 'evidence/varek-v36-helmet-pass/helmet_consolidated_pass4_workbench.png'

bpy.ops.wm.open_mainfile(filepath=str(TARGET_BLEND))
scene = bpy.context.scene

hull_col = bpy.data.collections.get('02_OPERATOR_HULL')
assert hull_col is not None, "02_OPERATOR_HULL not found"

mat_dark = bpy.data.materials.get("QA_Dark_Clay") or bpy.data.materials.get("Warm charcoal cast iron")
mat_iron = bpy.data.materials.get("QA_Iron_Clay") or bpy.data.materials.get("Warm charcoal cast iron")
mat_amber = bpy.data.materials.get("Amber visor")

# -----------------------------------------------------------------------------
# 1. PURGE PREVIOUS HEAD ATTEMPTS
# -----------------------------------------------------------------------------
purge_names = [
    "Operator_Pressure_Helmet_Shell", "Operator_Cheek_Respirator_Boss_L",
    "Operator_Cheek_Respirator_Boss_R", "Operator_Visor_Optical_Slit",
    "Operator_Thoracic_Collar_Ring", "Operator_Pressure_Cranium",
    "Operator_Brow_Faceted", "Operator_Visor_Bunker_Cheek_L",
    "Operator_Visor_Bunker_Cheek_R", "Operator_Visor_Amber_Slit",
    "Operator_Blast_Jaw_Plate", "Operator_Respirator_Housing_L",
    "Operator_Respirator_Housing_R", "Operator_Respirator_Intake_L",
    "Operator_Respirator_Intake_R", "Operator_Thoracic_Locking_Collar",
    "Operator_Neck_Hinge_Knuckle", "Operator_Brow_Stepped",
    "Operator_Visor_Slit", "Operator_Visor_Cowl", "Operator_Cell",
    "Operator_Brow", "Operator_Visor_Guard", "Operator_Pressure_Helmet",
    "Operator_Respirator_Boss_L", "Operator_Respirator_Boss_R"
]
for name in purge_names:
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

def tag_part(obj, name, mat):
    obj.name = name
    obj["production_geometry"] = True
    obj["form_importance"] = "PRIMARY"
    obj["rigid_driver_bone"] = "spine"
    if mat:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    if obj.name not in hull_col.objects:
        hull_col.objects.link(obj)
    if obj.name in scene.collection.objects:
        scene.collection.objects.unlink(obj)
    return obj

# -----------------------------------------------------------------------------
# 2. MONOLITHIC INDUSTRIAL PRESSURE HELMET HOUSING (V37 SPECIFICATION)
# Head Envelope:
# X: [-0.180, 0.180] (Width 0.36m)
# Y: [-0.220, 0.165] (Depth ~0.38m)
# Z: [1.600, 2.010] (Height 0.41m)
# -----------------------------------------------------------------------------

bm = bmesh.new()

# Cross-section profiles (Z descending) creating distinct 3-tier read:
# Tier 1: Armored Cranium Dome & Heavy Overhanging Stepped Brow
# Tier 2: Deeply Recessed Chamfered Visor Aperture Shelf
# Tier 3: Mechanical Wedge Jaw & Flank Cheek Intake Shelves
layers = [
    # (z, x_rad, y_front, y_back, cx, cf)
    (2.010, 0.115, -0.055, 0.095, 0.68, 0.68), # Top skull plate
    (1.975, 0.165, -0.100, 0.145, 0.82, 0.82), # Upper cranium slope
    (1.930, 0.180, -0.210, 0.160, 0.92, 0.90), # Stepped brow upper tier (forward awning)
    (1.865, 0.185, -0.222, 0.165, 0.96, 0.96), # Brow overhang lower lip (heavy shadow awning)
    (1.835, 0.170, -0.150, 0.160, 0.88, 0.75), # Recessed optical shelf aperture (deep step-in)
    (1.795, 0.178, -0.175, 0.155, 0.94, 0.88), # Cheek wedge flank shelf
    (1.730, 0.165, -0.160, 0.140, 0.90, 0.85), # Squared pressurized blast-chin wedge
    (1.660, 0.150, -0.115, 0.125, 0.84, 0.82), # Throat taper into locking collar
    (1.600, 0.145, -0.075, 0.110, 0.78, 0.78), # Collar coupling base
]

rings = []
for z, xr, yf, yb, cx, cf in layers:
    ring_verts = []
    # 8-point faceted industrial section with lateral slope
    pts = [
        (0.0, yf),
        (xr * cx, (yf * 0.72 + yb * 0.0)),
        (xr, (yf * 0.18 + yb * 0.52)),
        (xr * cx, yb * 0.92),
        (0.0, yb),
        (-xr * cx, yb * 0.92),
        (-xr, (yf * 0.18 + yb * 0.52)),
        (-xr * cx, (yf * 0.72 + yb * 0.0)),
    ]
    for px, py in pts:
        v = bm.verts.new((px, py, z))
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

bm.faces.new(reversed(rings[0]))
bm.faces.new(rings[-1])

bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()

# Crisp beveled mechanical edges
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.010, segments=2, affect='EDGES')

me_helmet = bpy.data.meshes.new("Operator_Pressure_Helmet_Mesh")
bm.to_mesh(me_helmet)
bm.free()

helmet_obj = bpy.data.objects.new("Operator_Pressure_Helmet", me_helmet)
tag_part(helmet_obj, "Operator_Pressure_Helmet", mat_dark)

# -----------------------------------------------------------------------------
# 3. PROMINENT INTEGRATED DUAL CHEEK RESPIRATORS
# Seated directly into cheek facet shelves at 26 deg yaw / 18 deg pitch
# -----------------------------------------------------------------------------
for side, sign in [('L', -1), ('R', 1)]:
    bm = bmesh.new()
    # Flanged two-stage intake canister
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12, radius1=0.042, radius2=0.035, depth=0.052)
    rot = Matrix.Rotation(math.radians(sign * 26.0), 4, 'Z') @ Matrix.Rotation(math.radians(18.0), 4, 'X')
    base_p = Vector((sign * 0.145, -0.142, 1.765))
    for v in bm.verts:
        v.co = rot @ v.co + base_p
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.005, segments=2, affect='EDGES')
    me_resp = bpy.data.meshes.new(f"Operator_Respirator_Boss_{side}_Mesh")
    bm.to_mesh(me_resp)
    bm.free()
    resp_obj = bpy.data.objects.new(f"Operator_Respirator_Boss_{side}", me_resp)
    tag_part(resp_obj, f"Operator_Respirator_Boss_{side}", mat_iron)

# -----------------------------------------------------------------------------
# 4. FRAMED AMBER OPTICAL SLIT (Buried 62mm behind brow awning)
# -----------------------------------------------------------------------------
# A. Internal Visor Frame Inset
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts:
    v.co.x *= 0.115  # Width 0.23m
    v.co.y *= 0.018  # Depth 0.036m
    v.co.z *= 0.018  # Height 0.036m
    v.co.y += -0.158 # Recessed behind brow at Y=-0.222
    v.co.z += 1.835
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.004, segments=2, affect='EDGES')
me_frame = bpy.data.meshes.new("Operator_Visor_Aperture_Frame_Mesh")
bm.to_mesh(me_frame)
bm.free()
frame_obj = bpy.data.objects.new("Operator_Visor_Aperture_Frame", me_frame)
tag_part(frame_obj, "Operator_Visor_Aperture_Frame", mat_iron)

# B. Amber Slit Core
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts:
    v.co.x *= 0.100  # Width 0.20m
    v.co.y *= 0.008  # Depth 0.016m
    v.co.z *= 0.009  # Height 0.018m
    v.co.y += -0.160
    v.co.z += 1.835
me_slit = bpy.data.meshes.new("Operator_Visor_Optical_Slit_Mesh")
bm.to_mesh(me_slit)
bm.free()
slit_obj = bpy.data.objects.new("Operator_Visor_Optical_Slit", me_slit)
tag_part(slit_obj, "Operator_Visor_Optical_Slit", mat_amber or mat_iron)

# -----------------------------------------------------------------------------
# 5. HEAVY STEPPED THORACIC DOCKING COLLAR
# Anchors the base at Z=1.60m into the thoracic plate with compression rings
# -----------------------------------------------------------------------------
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=0.172, radius2=0.190, depth=0.065)
for v in bm.verts:
    v.co.z += 1.605
    v.co.y += 0.015
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.008, segments=2, affect='EDGES')
me_col = bpy.data.meshes.new("Operator_Thoracic_Collar_Ring_Mesh")
bm.to_mesh(me_col)
bm.free()
col_obj = bpy.data.objects.new("Operator_Thoracic_Collar_Ring", me_col)
tag_part(col_obj, "Operator_Thoracic_Collar_Ring", mat_iron)

# -----------------------------------------------------------------------------
# 6. SAVE REFINED BLEND & RENDER DIAGNOSTIC WORKBENCH PORTRAIT
# -----------------------------------------------------------------------------
bpy.ops.wm.save_as_mainfile(filepath=str(TARGET_BLEND))
print(f"Saved refined V37 consolidated helmet to {TARGET_BLEND}")

s = bpy.context.scene
s.frame_set(1)
s.render.engine = 'BLENDER_WORKBENCH'
s.display.shading.light = 'MATCAP'
s.display.shading.studio_light = 'check_normal+y.exr'
s.render.resolution_x = 1080
s.render.resolution_y = 1350
s.render.resolution_percentage = 100
s.render.image_settings.file_format = 'PNG'
s.render.filepath = str(RENDER_OUT)

cam = s.objects.get('Camera')
if cam is None:
    cam_data = bpy.data.cameras.new('Camera')
    cam = bpy.data.objects.new('Camera', cam_data)
    s.collection.objects.link(cam)

cam.location = Vector((1.2, -2.4, 2.05))
target = Vector((0.0, 0.0, 1.85))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 65.0
s.camera = cam

bpy.ops.render.render(write_still=True)
print(f"Rendered V37 helmet portrait to {RENDER_OUT}")
