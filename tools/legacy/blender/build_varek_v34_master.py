import bpy
import math
import os
from mathutils import Vector, Euler, Quaternion

SRC_BLEND = "/home/aaron/animation/thulans-production/blender/candidates/varek-v33-canonical.blend"
DST_BLEND = "/home/aaron/animation/thulans-production/blender/candidates/varek-v34-canonical.blend"
ART_DIR = "/home/aaron/animation/thulans-production/assets/art"
FRONT34 = os.path.join(ART_DIR, "varek_v34_front34_frame_001.png")
SIDE = os.path.join(ART_DIR, "varek_v34_side_profile_frame_001.png")

bpy.ops.wm.open_mainfile(filepath=SRC_BLEND)
scene = bpy.context.scene
arm = bpy.data.objects.get('Varek simple articulation')

# ---------------------------------------------------------------------------
# 1. HARD-SURFACE SMOOTHING, AUTO-SMOOTH & CINEMATIC BEVELS
# ---------------------------------------------------------------------------
def is_cloth_or_insignia(obj):
    n = obj.name.lower()
    return any(k in n for k in ("gren", "skildus", "cloth", "cross", "insignia"))

for obj in scene.objects:
    if obj.type != 'MESH':
        continue
    
    # Shade smooth all faces
    for poly in obj.data.polygons:
        poly.use_smooth = True
        
    if not is_cloth_or_insignia(obj):
        # Auto-smooth via Weighted Normal modifier
        wn_mod = obj.modifiers.get('WeightedNormal')
        if not wn_mod:
            wn_mod = obj.modifiers.new(name='WeightedNormal', type='WEIGHTED_NORMAL')
            wn_mod.keep_sharp = True
            
        # Non-destructive Bevel modifier for rounded specular highlights
        bev = obj.modifiers.get('Bevel')
        if not bev:
            bev = obj.modifiers.new(name='Bevel', type='BEVEL')
            bev.limit_method = 'ANGLE'
            bev.angle_limit = math.radians(32)
            bev.profile = 0.7
        bev.width = 0.012
        bev.segments = 4

# ---------------------------------------------------------------------------
# 2. MATERIAL METALLURGY OVERHAUL (REMOVE PLASTIC/TOY LOOK)
# ---------------------------------------------------------------------------
# A. Warm charcoal cast iron -> Deep forged anthracite steel
mat_iron = bpy.data.materials.get('Warm charcoal cast iron')
if mat_iron and mat_iron.use_nodes:
    bsdf = next((n for n in mat_iron.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.045, 0.045, 0.05, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.96
        bsdf.inputs['Roughness'].default_value = 0.38
        if 'Specular IOR Level' in bsdf.inputs:
            bsdf.inputs['Specular IOR Level'].default_value = 0.6
        elif 'Specular' in bsdf.inputs:
            bsdf.inputs['Specular'].default_value = 0.6

# B. Aged brass -> Dark tarnished machinery bronze
mat_brass = bpy.data.materials.get('Aged brass')
if mat_brass and mat_brass.use_nodes:
    bsdf = next((n for n in mat_brass.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.24, 0.16, 0.065, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.92
        bsdf.inputs['Roughness'].default_value = 0.36

# C. Cinderback jade paint -> Deep muted slate green canvas
mat_cloth = bpy.data.materials.get('Cinderback jade paint')
if mat_cloth and mat_cloth.use_nodes:
    bsdf = next((n for n in mat_cloth.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.07, 0.12, 0.09, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.0
        bsdf.inputs['Roughness'].default_value = 0.88
        if 'Sheen Weight' in bsdf.inputs:
            bsdf.inputs['Sheen Weight'].default_value = 0.0

# ---------------------------------------------------------------------------
# 3. GREN-SKILDUS ORGANIC CANVAS CLOAK REFINEMENT
# ---------------------------------------------------------------------------
cloth_obj = bpy.data.objects.get("Gren Skildus")
if cloth_obj:
    sub = cloth_obj.modifiers.get('Subdivision')
    if sub:
        sub.levels = 3
        sub.render_levels = 3
    sol = cloth_obj.modifiers.get('Thickness')
    if sol:
        sol.thickness = 0.016

# ---------------------------------------------------------------------------
# 4. SAVE BLEND
# ---------------------------------------------------------------------------
bpy.ops.wm.save_as_mainfile(filepath=DST_BLEND)
print(f"V34 Saved: {DST_BLEND}")

# ---------------------------------------------------------------------------
# 5. CYCLES 128 SAMPLES DIAGNOSTIC RENDERS
# ---------------------------------------------------------------------------
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.render.resolution_x = 960
scene.render.resolution_y = 1280
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

# Render Front 3/4
cam_front = bpy.data.objects.get("V32_Cam_Front34") or scene.camera
scene.camera = cam_front
scene.render.filepath = FRONT34
bpy.ops.render.render(write_still=True)

# Render Side Profile
cam_side = bpy.data.objects.get("Side_Profile_Camera_V33") or bpy.data.objects.get("Side_Profile_Camera_V31")
if cam_side:
    scene.camera = cam_side
scene.render.filepath = SIDE
bpy.ops.render.render(write_still=True)

print("V34 Beauty Renders Completed!")