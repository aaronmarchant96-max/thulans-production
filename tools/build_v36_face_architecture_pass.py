import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler
from pathlib import Path

R = Path('/home/aaron/animation/thulans-production')
TARGET_BLEND = R / 'blender/candidates/varek-v36-helmet-pass.blend'
RENDER_OUT = R / 'evidence/varek-v36-helmet-pass/helmet_face_architecture_workbench.png'

bpy.ops.wm.open_mainfile(filepath=str(TARGET_BLEND))
scene = bpy.context.scene

hull_col = bpy.data.collections.get('02_OPERATOR_HULL')
assert hull_col is not None, "02_OPERATOR_HULL not found"

mat_dark = bpy.data.materials.get("QA_Dark_Clay") or bpy.data.materials.get("Warm charcoal cast iron")
mat_iron = bpy.data.materials.get("QA_Iron_Clay") or bpy.data.materials.get("Warm charcoal cast iron")
mat_amber = bpy.data.materials.get("Amber visor")

# -----------------------------------------------------------------------------
# 1. PURGE PREVIOUS FACE/HELMET PROTOTYPE OBJECTS
# -----------------------------------------------------------------------------
purge_names = [
    "Operator_Brow_Stepped", "Operator_Visor_Slit", "Operator_Visor_Cowl",
    "Operator_Respirator_Canister_L", "Operator_Respirator_Canister_R",
    "Operator_Heat_Baffle_0", "Operator_Heat_Baffle_1", "Operator_Heat_Baffle_2",
    "Operator_Neck_Seal_Collar", "Operator_Cell"
]
for name in purge_names:
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

def tag_helmet_part(obj, name, mat):
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
# 2. RECONSTRUCT INDUSTRIAL PRESSURE HOUSING (CRANIUM)
# Octagonal cast-iron pressure hull with angled planar facets, eliminating the conventional round sphere
# -----------------------------------------------------------------------------
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts:
    v.co.x *= 0.170  # Width: 0.34m
    v.co.y *= 0.150  # Depth: 0.30m
    v.co.z *= 0.140  # Height: 0.28m
    v.co.y += 0.010  # Centered over spine axis
    v.co.z += 1.940
    # Slope forehead backward and taper top cranium
    if v.co.z > 1.98:
        v.co.x *= 0.88
        if v.co.y < 0:
            v.co.y *= 0.75
    # Taper lower jaw
    if v.co.z < 1.88:
        v.co.x *= 0.82
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.035, segments=3, affect='EDGES')
me = bpy.data.meshes.new("Operator_Pressure_Cranium_Mesh")
bm.to_mesh(me)
bm.free()
cranium_obj = bpy.data.objects.new("Operator_Pressure_Cranium", me)
tag_helmet_part(cranium_obj, "Operator_Pressure_Cranium", mat_dark)

# -----------------------------------------------------------------------------
# 3. STEPPED ARMORED BROW (SLOPED & FACETED)
# Replaces the flat shelf with a 3-facet angled brow roof that slopes down laterally
# -----------------------------------------------------------------------------
bm = bmesh.new()
# Left, Center, Right angled roof sections
bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts:
    v.co.x *= 0.165  # 0.33m wide
    v.co.y *= 0.055  # 0.11m deep
    v.co.z *= 0.030  # 0.06m thick
    v.co.y += -0.145
    v.co.z += 1.950
    # Central peak with lateral downward slope (angles down toward ears)
    lateral_dist = abs(v.co.x) / 0.165
    v.co.z -= 0.022 * (lateral_dist ** 1.5)
    # Forward overhang angle
    if v.co.y < -0.15:
        v.co.z -= 0.012
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.008, segments=2, affect='EDGES')
me = bpy.data.meshes.new("Operator_Brow_Faceted_Mesh")
bm.to_mesh(me)
bm.free()
brow_obj = bpy.data.objects.new("Operator_Brow_Faceted", me)
tag_helmet_part(brow_obj, "Operator_Brow_Faceted", mat_iron)

# -----------------------------------------------------------------------------
# 4. DEEPLY RECESSED QUARTZ VISOR SLIT & CAVITY CASING
# Visor is buried ~65mm behind the brow/cheek armor, readable only as a deep amber slit
# -----------------------------------------------------------------------------
# Outer protective armor bunker cheek plates (flanking visor)
for side, sign in [('L', -1), ('R', 1)]:
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.035
        v.co.y *= 0.060
        v.co.z *= 0.055
        v.co.x += sign * 0.125
        v.co.y += -0.145
        v.co.z += 1.885
        # Forward chamfer
        if v.co.y < -0.15:
            v.co.x *= 0.85
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.006, segments=2, affect='EDGES')
    me = bpy.data.meshes.new(f"Operator_Visor_Bunker_Cheek_{side}_Mesh")
    bm.to_mesh(me)
    bm.free()
    cheek_bunker = bpy.data.objects.new(f"Operator_Visor_Bunker_Cheek_{side}", me)
    tag_helmet_part(cheek_bunker, f"Operator_Visor_Bunker_Cheek_{side}", mat_iron)

# Deep horizontal optical slit (recessed at Y=-0.115, far behind Y=-0.18 brow)
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts:
    v.co.x *= 0.090  # 0.18m wide
    v.co.y *= 0.015  # 0.03m deep
    v.co.z *= 0.010  # 0.020m thin human slit
    v.co.y += -0.120 # Deeply buried
    v.co.z += 1.890
me = bpy.data.meshes.new("Operator_Visor_Amber_Slit_Mesh")
bm.to_mesh(me)
bm.free()
slit_obj = bpy.data.objects.new("Operator_Visor_Amber_Slit", me)
tag_helmet_part(slit_obj, "Operator_Visor_Amber_Slit", mat_amber or mat_dark)

# Lower blast jaw shield (beneath slit)
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts:
    v.co.x *= 0.110
    v.co.y *= 0.045
    v.co.z *= 0.028
    v.co.y += -0.150
    v.co.z += 1.845
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.006, segments=2, affect='EDGES')
me = bpy.data.meshes.new("Operator_Blast_Jaw_Plate_Mesh")
bm.to_mesh(me)
bm.free()
jaw_obj = bpy.data.objects.new("Operator_Blast_Jaw_Plate", me)
tag_helmet_part(jaw_obj, "Operator_Blast_Jaw_Plate", mat_iron)

# -----------------------------------------------------------------------------
# 5. INTEGRATED CHEEK INTAKE / SULFUR RESPIRATOR ARCHITECTURE
# Distinct dual industrial respirator housings nested directly into the jaw flank recesses
# -----------------------------------------------------------------------------
for side, sign in [('L', -1), ('R', 1)]:
    # A. Respirator main filter housing (heavy bevel box block)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.040
        v.co.y *= 0.055
        v.co.z *= 0.042
        v.co.x += sign * 0.135
        v.co.y += -0.090
        v.co.z += 1.810
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.005, segments=2, affect='EDGES')
    me = bpy.data.meshes.new(f"Operator_Respirator_Housing_{side}_Mesh")
    bm.to_mesh(me)
    bm.free()
    resp_house = bpy.data.objects.new(f"Operator_Respirator_Housing_{side}", me)
    tag_helmet_part(resp_house, f"Operator_Respirator_Housing_{side}", mat_iron)

    # B. Angled forward intake grill snout
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=0.024, radius2=0.020, depth=0.040)
    rot = Matrix.Rotation(math.radians(sign * 22.0), 4, 'Z') @ Matrix.Rotation(math.radians(20.0), 4, 'X')
    base_p = Vector((sign * 0.140, -0.135, 1.800))
    for v in bm.verts:
        v.co = rot @ v.co + base_p
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.003, segments=2, affect='EDGES')
    me = bpy.data.meshes.new(f"Operator_Respirator_Intake_{side}_Mesh")
    bm.to_mesh(me)
    bm.free()
    resp_intake = bpy.data.objects.new(f"Operator_Respirator_Intake_{side}", me)
    tag_helmet_part(resp_intake, f"Operator_Respirator_Intake_{side}", mat_dark)

# -----------------------------------------------------------------------------
# 6. HEAVY MECHANICAL NECK COLLAR & THORACIC LOCKING SEAL
# Heavy beveled octagonal locking ring firmly seating helmet into thoracic hull
# -----------------------------------------------------------------------------
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=0.155, radius2=0.165, depth=0.065)
for v in bm.verts:
    v.co.z += 1.730
    v.co.y += 0.010
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.008, segments=2, affect='EDGES')
me = bpy.data.meshes.new("Operator_Thoracic_Locking_Collar_Mesh")
bm.to_mesh(me)
bm.free()
collar_obj = bpy.data.objects.new("Operator_Thoracic_Locking_Collar", me)
tag_helmet_part(collar_obj, "Operator_Thoracic_Locking_Collar", mat_iron)

# Rear heavy neck hinge knuckle
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts:
    v.co.x *= 0.090
    v.co.y *= 0.045
    v.co.z *= 0.040
    v.co.y += 0.140
    v.co.z += 1.765
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.006, segments=2, affect='EDGES')
me = bpy.data.meshes.new("Operator_Neck_Hinge_Knuckle_Mesh")
bm.to_mesh(me)
bm.free()
hinge_obj = bpy.data.objects.new("Operator_Neck_Hinge_Knuckle", me)
tag_helmet_part(hinge_obj, "Operator_Neck_Hinge_Knuckle", mat_dark)

# -----------------------------------------------------------------------------
# 7. SAVE CANDIDATE BLEND & RENDER DIAGNOSTIC PORTRAIT
# -----------------------------------------------------------------------------
bpy.ops.wm.save_as_mainfile(filepath=str(TARGET_BLEND))
print(f"Saved refined face architecture to {TARGET_BLEND}")

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
target = Vector((0.0, 0.0, 1.95))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 65.0
s.camera = cam

bpy.ops.render.render(write_still=True)
print(f"Rendered diagnostic face portrait to {RENDER_OUT}")
