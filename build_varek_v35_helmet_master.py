import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix, Euler

# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------
BASE_DIR = "/home/aaron/animation/thulans-production"
BLEND_DIR = os.path.join(BASE_DIR, "blender", "candidates")
ART_DIR = os.path.join(BASE_DIR, "assets", "art")
os.makedirs(BLEND_DIR, exist_ok=True)
os.makedirs(ART_DIR, exist_ok=True)

CANDIDATES = [
    os.path.join(BLEND_DIR, "varek-v34-canonical.blend"),
    os.path.join(BLEND_DIR, "varek-v33-canonical.blend"),
]
OUT_BLEND = os.path.join(BLEND_DIR, "varek-v35-canonical.blend")
RENDER_HEAD = os.path.join(ART_DIR, "varek_v35_head_closeup_frame_001.png")
RENDER_FRONT = os.path.join(ART_DIR, "varek_v35_front34_frame_001.png")

ARMATURE_NAME = "Varek simple articulation"
HEAD_BONE = "head"

# -----------------------------------------------------------------------------
# LOAD BASE FILE
# -----------------------------------------------------------------------------
loaded = False
for path in CANDIDATES:
    if os.path.exists(path):
        bpy.ops.wm.open_mainfile(filepath=path)
        print(f"[v35] Loaded base: {path}")
        loaded = True
        break
if not loaded:
    print("[v35] No base file found, starting from empty scene.")
    bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
arm = bpy.data.objects.get(ARMATURE_NAME)

# -----------------------------------------------------------------------------
# PURGE OLD HEAD OBJECTS
# -----------------------------------------------------------------------------
def purge_old_head_objects():
    keywords = ["head", "visor", "chin", "neck", "helmet", "cranium",
                "brow", "jaw", "respirator", "gimbal", "throat"]
    to_remove = []
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        name_l = obj.name.lower()
        if any(k in name_l for k in keywords):
            if "body" in name_l or "torso" in name_l or "arm" in name_l or "leg" in name_l:
                continue
            to_remove.append(obj)
    for obj in to_remove:
        print(f"[v35] Purging old head object: {obj.name}")
        bpy.data.objects.remove(obj, do_unlink=True)

purge_old_head_objects()

# -----------------------------------------------------------------------------
# MATERIALS
# -----------------------------------------------------------------------------
MAT_IRON = bpy.data.materials.get("Warm charcoal cast iron")
MAT_BRASS = bpy.data.materials.get("Aged brass")
MAT_AMBER = bpy.data.materials.get("Amber visor")
MAT_STEEL = bpy.data.materials.get("Oily joint steel")

def bind_to_bone(obj, bone_name):
    if not obj or not arm:
        return
    vg = obj.vertex_groups.get(bone_name)
    if not vg:
        vg = obj.vertex_groups.new(name=bone_name)
    vg.add([v.index for v in obj.data.vertices], 1.0, 'REPLACE')
    
    arm_mod = None
    for m in obj.modifiers:
        if m.type == 'ARMATURE':
            arm_mod = m
            break
    if not arm_mod:
        arm_mod = obj.modifiers.new(name='Rigid single bone', type='ARMATURE')
    arm_mod.object = arm

def new_mesh_obj(name, bm, material):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    scene.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    bind_to_bone(obj, HEAD_BONE)
    return obj

def add_bevel_subsurf(obj, bevel_width=0.008, bevel_segments=4, subsurf_levels=1):
    bev = obj.modifiers.new("Bevel", 'BEVEL')
    bev.width = bevel_width
    bev.segments = bevel_segments
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(35)
    if subsurf_levels > 0:
        sub = obj.modifiers.new("Subdivision", 'SUBSURF')
        sub.levels = subsurf_levels
        sub.render_levels = subsurf_levels

def shade_smooth(obj):
    for p in obj.data.polygons:
        p.use_smooth = True

# -----------------------------------------------------------------------------
# A. MAIN CRANIAL DOME & BROW GUARD
# -----------------------------------------------------------------------------
def build_cranial_dome():
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.16
        v.co.y *= 0.16
        v.co.z *= 0.13
        v.co.z += 2.05
    bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges), offset=0.045, segments=3, profile=0.5, affect='EDGES')
    for v in bm.verts:
        if v.co.z > 2.10 and v.co.y < 0.0:
            v.co.y -= 0.02
            v.co.z += 0.02
        if v.co.z < 2.00:
            v.co.x *= 0.85
            v.co.y *= 0.9
    obj = new_mesh_obj("Varek_Helmet_Cranium", bm, MAT_IRON)
    add_bevel_subsurf(obj, bevel_width=0.008, bevel_segments=4, subsurf_levels=1)
    shade_smooth(obj)
    return obj

def build_brow_guard():
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.17
        v.co.y *= 0.045
        v.co.z *= 0.035
        v.co.y += -0.155
        v.co.z += 2.10
    for v in bm.verts:
        if v.co.y < -0.16:
            v.co.z -= 0.015
    bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges), offset=0.012, segments=3, affect='EDGES')
    obj = new_mesh_obj("Varek_Helmet_BrowGuard", bm, MAT_IRON)
    add_bevel_subsurf(obj, bevel_width=0.006, bevel_segments=3, subsurf_levels=1)
    shade_smooth(obj)
    return obj

def build_cheek_cowl(side):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.045
        v.co.y *= 0.10
        v.co.z *= 0.09
        v.co.x += side * 0.135
        v.co.y += -0.06
        v.co.z += 1.98
    for v in bm.verts:
        if v.co.z < 1.95:
            v.co.x *= 0.7
            v.co.y *= 0.85
    bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges), offset=0.010, segments=3, affect='EDGES')
    name = f"Varek_Helmet_CheekCowl_{'R' if side > 0 else 'L'}"
    obj = new_mesh_obj(name, bm, MAT_IRON)
    add_bevel_subsurf(obj, bevel_width=0.006, bevel_segments=3, subsurf_levels=1)
    shade_smooth(obj)
    return obj

# -----------------------------------------------------------------------------
# B. ARMORED QUARTZ VISOR SLIT
# -----------------------------------------------------------------------------
def build_visor_slit():
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.09
        v.co.y *= 0.02
        v.co.z *= 0.0175
        v.co.y += -0.15
        v.co.z += 2.02
    obj = new_mesh_obj("Varek_Helmet_VisorSlit", bm, MAT_AMBER)
    shade_smooth(obj)
    return obj

def build_visor_recess():
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.105
        v.co.y *= 0.025
        v.co.z *= 0.028
        v.co.y += -0.145
        v.co.z += 2.02
    obj = new_mesh_obj("Varek_Helmet_VisorRecess", bm, MAT_IRON)
    shade_smooth(obj)
    return obj

# -----------------------------------------------------------------------------
# C. DUAL SULFUR RESPIRATOR FILTER PODS
# -----------------------------------------------------------------------------
def build_respirator_pod(side):
    parts = []
    angle = math.radians(35.0) * side
    base_pos = Vector((side * 0.13, -0.10, 1.94))
    rot = Matrix.Rotation(angle, 4, 'Y')

    # Canister body
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=0.032, radius2=0.032, depth=0.075)
    for v in bm.verts:
        v.co = rot @ v.co + base_pos
    obj = new_mesh_obj(f"Varek_Respirator_Canister_{'R' if side > 0 else 'L'}", bm, MAT_IRON)
    add_bevel_subsurf(obj, bevel_width=0.004, bevel_segments=3, subsurf_levels=1)
    shade_smooth(obj)
    parts.append(obj)

    # Brass intake ring
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=0.036, radius2=0.036, depth=0.012)
    for v in bm.verts:
        v.co = rot @ (v.co + Vector((0, 0, 0.042))) + base_pos
    obj = new_mesh_obj(f"Varek_Respirator_IntakeRing_{'R' if side > 0 else 'L'}", bm, MAT_BRASS)
    add_bevel_subsurf(obj, bevel_width=0.003, bevel_segments=3, subsurf_levels=1)
    shade_smooth(obj)
    parts.append(obj)

    return parts

# -----------------------------------------------------------------------------
# D. REINFORCED THROAT & NECK GIMBAL
# -----------------------------------------------------------------------------
def build_neck_gimbal():
    parts = []
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=0.11, radius2=0.11, depth=0.10)
    for v in bm.verts:
        v.co.z += 1.86
    obj = new_mesh_obj("Varek_Neck_GimbalRing", bm, MAT_STEEL)
    add_bevel_subsurf(obj, bevel_width=0.005, bevel_segments=3, subsurf_levels=1)
    shade_smooth(obj)
    parts.append(obj)
    return parts

# -----------------------------------------------------------------------------
# EXECUTE BUILD
# -----------------------------------------------------------------------------
build_cranial_dome()
build_brow_guard()
build_cheek_cowl(+1)
build_cheek_cowl(-1)
build_visor_recess()
build_visor_slit()
build_respirator_pod(+1)
build_respirator_pod(-1)
build_neck_gimbal()

# Save canonical V35
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print(f"[v35] Saved candidate blend: {OUT_BLEND}")

# -----------------------------------------------------------------------------
# RENDER CLOSEUP & FRONT BEAUTY SHOTS
# -----------------------------------------------------------------------------
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.render.resolution_x = 960
scene.render.resolution_y = 1280
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

# 1. Close-up Helmet Portrait Camera
cam_head_data = bpy.data.cameras.new("V35_Cam_Head_Portrait")
cam_head_obj = bpy.data.objects.new("V35_Cam_Head_Portrait", cam_head_data)
scene.collection.objects.link(cam_head_obj)
cam_head_obj.location = (0.75, -1.10, 2.05)
dir_v = Vector((0.0, 0.0, 2.02)) - cam_head_obj.location
cam_head_obj.rotation_euler = dir_v.to_track_quat('-Z', 'Y').to_euler()
cam_head_data.lens = 85.0

scene.camera = cam_head_obj
scene.render.filepath = RENDER_HEAD
bpy.ops.render.render(write_still=True)

# 2. Full Body Front 3/4
cam_front = bpy.data.objects.get("V32_Cam_Front34")
if cam_front:
    scene.camera = cam_front
scene.render.filepath = RENDER_FRONT
bpy.ops.render.render(write_still=True)

print("[v35] Render complete!")