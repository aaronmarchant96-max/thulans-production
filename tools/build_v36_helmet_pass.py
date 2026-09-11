import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler
from pathlib import Path

R = Path('/home/aaron/animation/thulans-production')
TARGET_BLEND = R / 'blender/candidates/varek-v36-helmet-pass.blend'
RENDER_OUT = R / 'evidence/varek-v36-helmet-pass/helmet_pass_workbench.png'

bpy.ops.wm.open_mainfile(filepath=str(TARGET_BLEND))
scene = bpy.context.scene

hull_col = bpy.data.collections.get('02_OPERATOR_HULL')
assert hull_col is not None, "02_OPERATOR_HULL not found"

# -----------------------------------------------------------------------------
# 1. READ CANONICAL MATS & BONES
# -----------------------------------------------------------------------------
mat_dark = bpy.data.materials.get("QA_Dark_Clay") or bpy.data.materials.get("Warm charcoal cast iron")
mat_iron = bpy.data.materials.get("QA_Iron_Clay") or bpy.data.materials.get("Warm charcoal cast iron")
mat_brass = bpy.data.materials.get("Aged brass")
mat_amber = bpy.data.materials.get("Amber visor")

# -----------------------------------------------------------------------------
# 2. PURGE OLD LOOSE VISOR / BROW
# -----------------------------------------------------------------------------
for name in ["Operator_Brow", "Operator_Visor_Guard"]:
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

# -----------------------------------------------------------------------------
# 3. CONSTRUCT CANONICAL HELMET WITHIN BOUNDS
# Bounded to: X in [-0.17, 0.17], Y in [-0.235, 0.05], Z in [1.74, 2.06]
# -----------------------------------------------------------------------------
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

# A. Stepped Forged Brow Visor Shield
# Slopes over the visor slit, protecting from overhead mine impacts
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts:
    v.co.x *= 0.175  # width 0.35m
    v.co.y *= 0.065  # depth
    v.co.z *= 0.038  # height
    v.co.y += -0.165
    v.co.z += 1.935
    # Forward overhang taper
    if v.co.y < -0.17:
        v.co.z -= 0.012
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.008, segments=3, affect='EDGES')
me = bpy.data.meshes.new("Operator_Brow_Stepped_Mesh")
bm.to_mesh(me)
bm.free()
brow_obj = bpy.data.objects.new("Operator_Brow_Stepped", me)
tag_helmet_part(brow_obj, "Operator_Brow_Stepped", mat_iron)

# B. Deeply Recessed Armored Visor Housing & Slit
# Recessed inside the brow overhang at Y=-0.175
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts:
    v.co.x *= 0.115  # width 0.23m
    v.co.y *= 0.025  # depth
    v.co.z *= 0.018  # narrow optical slit 0.036m
    v.co.y += -0.180
    v.co.z += 1.885
me = bpy.data.meshes.new("Operator_Visor_Slit_Mesh")
bm.to_mesh(me)
bm.free()
visor_obj = bpy.data.objects.new("Operator_Visor_Slit", me)
tag_helmet_part(visor_obj, "Operator_Visor_Slit", mat_amber or mat_dark)

# Visor armor surround cowl
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts:
    v.co.x *= 0.145
    v.co.y *= 0.030
    v.co.z *= 0.032
    v.co.y += -0.170
    v.co.z += 1.885
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.006, segments=2, affect='EDGES')
me = bpy.data.meshes.new("Operator_Visor_Cowl_Mesh")
bm.to_mesh(me)
bm.free()
cowl_obj = bpy.data.objects.new("Operator_Visor_Cowl", me)
tag_helmet_part(cowl_obj, "Operator_Visor_Cowl", mat_dark)

# C. Dual Sulfur Respirator Filter Pods (Jaw Flanks)
# Angled 28° outward at X=±0.125, Y=-0.12, Z=1.80
for side, sign in [('L', -1), ('R', 1)]:
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=0.030, radius2=0.030, depth=0.065)
    rot = Matrix.Rotation(math.radians(sign * 28.0), 4, 'Z') @ Matrix.Rotation(math.radians(15.0), 4, 'X')
    base_p = Vector((sign * 0.130, -0.135, 1.805))
    for v in bm.verts:
        v.co = rot @ v.co + base_p
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.004, segments=2, affect='EDGES')
    me = bpy.data.meshes.new(f"Operator_Respirator_Canister_{side}_Mesh")
    bm.to_mesh(me)
    bm.free()
    resp_obj = bpy.data.objects.new(f"Operator_Respirator_Canister_{side}", me)
    tag_helmet_part(resp_obj, f"Operator_Respirator_Canister_{side}", mat_dark)

# D. Heat Baffle Slats on Upper Forehead
# 3 low-profile cooling louvres above brow
for idx in range(3):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.08
        v.co.y *= 0.012
        v.co.z *= 0.005
        v.co.y += -0.135 + idx * 0.022
        v.co.z += 1.980 + idx * 0.018
    me = bpy.data.meshes.new(f"Operator_Heat_Baffle_{idx}_Mesh")
    bm.to_mesh(me)
    bm.free()
    baffle_obj = bpy.data.objects.new(f"Operator_Heat_Baffle_{idx}", me)
    tag_helmet_part(baffle_obj, f"Operator_Heat_Baffle_{idx}", mat_iron)

# E. Heavy Neck Seal Collar Segment
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=0.135, radius2=0.145, depth=0.055)
for v in bm.verts:
    v.co.z += 1.745
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.005, segments=2, affect='EDGES')
me = bpy.data.meshes.new("Operator_Neck_Seal_Collar_Mesh")
bm.to_mesh(me)
bm.free()
neck_obj = bpy.data.objects.new("Operator_Neck_Seal_Collar", me)
tag_helmet_part(neck_obj, "Operator_Neck_Seal_Collar", mat_iron)

# -----------------------------------------------------------------------------
# 4. SAVE CANONICAL V36 CANDIDATE BLEND
# -----------------------------------------------------------------------------
bpy.ops.wm.save_as_mainfile(filepath=str(TARGET_BLEND))
print(f"Saved refined candidate to {TARGET_BLEND}")

# -----------------------------------------------------------------------------
# 5. RENDER DIAGNOSTIC WORKBENCH PORTRAIT
# -----------------------------------------------------------------------------
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
print(f"Rendered diagnostic portrait to {RENDER_OUT}")
