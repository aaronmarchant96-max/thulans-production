import bpy
import bmesh
from mathutils import Vector, Matrix, Euler
import math

blend_path = '/home/aaron/animation/thulans-production/blender/candidates/varek-v40-osint-juggernaut.blend'
bpy.ops.wm.open_mainfile(filepath=blend_path)
scene = bpy.context.scene

def clean_mesh(obj):
    if not obj or obj.type != 'MESH':
        return
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    # Ensure smooth shading
    for poly in obj.data.polygons:
        poly.use_smooth = True
    # Add weighted normal modifier if not present
    wn = next((m for m in obj.modifiers if m.type == 'WEIGHTED_NORMAL'), None)
    if not wn:
        wn = obj.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
        wn.keep_sharp = True

# =============================================================================
# 1. RE-MODEL PELVIC CODPLATE & HIP FAULDS (CLEAN CAST GEOMETRY & NORMALS)
# =============================================================================

# Pelvic Codplate
codplate = bpy.data.objects.get('Sculpt_Pelvic_Codplate')
if codplate:
    bm = bmesh.new()
    verts = [
        Vector((0.0, 0.22, 1.14)),       # 0: Top Front Apex
        Vector((-0.18, 0.16, 1.14)),     # 1: Top Left
        Vector((0.18, 0.16, 1.14)),      # 2: Top Right
        Vector((-0.20, 0.02, 1.14)),     # 3: Top Back Left
        Vector((0.20, 0.02, 1.14)),      # 4: Top Back Right
        
        Vector((0.0, 0.24, 0.98)),       # 5: Mid Front Keel
        Vector((-0.16, 0.18, 0.98)),     # 6: Mid Left Outer
        Vector((0.16, 0.18, 0.98)),      # 7: Mid Right Outer
        Vector((-0.15, 0.05, 0.98)),     # 8: Mid Back Left
        Vector((0.15, 0.05, 0.98)),      # 9: Mid Back Right
        
        Vector((0.0, 0.18, 0.82)),       # 10: Lower Keel
        Vector((-0.11, 0.12, 0.82)),     # 11: Lower Left
        Vector((0.11, 0.12, 0.82)),      # 12: Lower Right
        Vector((-0.09, 0.04, 0.82)),     # 13: Lower Back Left
        Vector((0.09, 0.04, 0.82)),      # 14: Lower Back Right
        
        Vector((0.0, 0.08, 0.72)),       # 15: Bottom Tip Front
        Vector((-0.06, 0.04, 0.72)),     # 16: Bottom Tip Left
        Vector((0.06, 0.04, 0.72)),      # 17: Bottom Tip Right
    ]
    bm_verts = [bm.verts.new(v) for v in verts]
    
    faces = [
        [bm_verts[1], bm_verts[0], bm_verts[2], bm_verts[4], bm_verts[3]],
        [bm_verts[0], bm_verts[1], bm_verts[6], bm_verts[5]],
        [bm_verts[0], bm_verts[5], bm_verts[7], bm_verts[2]],
        [bm_verts[1], bm_verts[3], bm_verts[8], bm_verts[6]],
        [bm_verts[2], bm_verts[7], bm_verts[9], bm_verts[4]],
        [bm_verts[5], bm_verts[6], bm_verts[11], bm_verts[10]],
        [bm_verts[5], bm_verts[10], bm_verts[12], bm_verts[7]],
        [bm_verts[6], bm_verts[8], bm_verts[13], bm_verts[11]],
        [bm_verts[7], bm_verts[12], bm_verts[14], bm_verts[9]],
        [bm_verts[10], bm_verts[11], bm_verts[16], bm_verts[15]],
        [bm_verts[10], bm_verts[15], bm_verts[17], bm_verts[12]],
        [bm_verts[11], bm_verts[13], bm_verts[16]],
        [bm_verts[12], bm_verts[17], bm_verts[14]],
    ]
    for f in faces:
        try:
            bm.faces.new(f)
        except Exception:
            pass
            
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(codplate.data)
    bm.free()
    codplate.data.update()
    
    codplate.modifiers.clear()
    bev = codplate.modifiers.new(name="Bevel", type='BEVEL')
    bev.width = 0.015
    bev.segments = 3
    bev.limit_method = 'ANGLE'
    sub = codplate.modifiers.new(name="Subdivision", type='SUBSURF')
    sub.levels = 1
    sub.render_levels = 2
    clean_mesh(codplate)

# Left & Right Hip Faulds
for side, sign in [('L', 1), ('R', -1)]:
    fauld = bpy.data.objects.get(f'Sculpt_Hip_Fauld_{side}')
    if fauld:
        bm = bmesh.new()
        y_center = 0.05
        z_top = 1.16
        z_bot = 0.90
        x_in = 0.22 * sign
        x_out = 0.38 * sign
        
        verts = [
            Vector((x_in, y_center + 0.12, z_top)),
            Vector((x_out, y_center + 0.10, z_top - 0.04)),
            Vector((x_out, y_center - 0.12, z_top - 0.04)),
            Vector((x_in, y_center - 0.12, z_top)),
            
            Vector((x_in + 0.02*sign, y_center + 0.14, z_bot + 0.08)),
            Vector((x_out + 0.05*sign, y_center + 0.11, z_bot + 0.03)),
            Vector((x_out + 0.05*sign, y_center - 0.13, z_bot + 0.03)),
            Vector((x_in + 0.02*sign, y_center - 0.13, z_bot + 0.08)),
            
            Vector((x_in + 0.04*sign, y_center + 0.11, z_bot)),
            Vector((x_out + 0.03*sign, y_center + 0.08, z_bot - 0.02)),
            Vector((x_out + 0.03*sign, y_center - 0.10, z_bot - 0.02)),
            Vector((x_in + 0.04*sign, y_center - 0.10, z_bot)),
        ]
        bm_verts = [bm.verts.new(v) for v in verts]
        if sign > 0:
            bm.faces.new([bm_verts[0], bm_verts[1], bm_verts[2], bm_verts[3]])
            bm.faces.new([bm_verts[0], bm_verts[4], bm_verts[5], bm_verts[1]])
            bm.faces.new([bm_verts[1], bm_verts[5], bm_verts[6], bm_verts[2]])
            bm.faces.new([bm_verts[2], bm_verts[6], bm_verts[7], bm_verts[3]])
            bm.faces.new([bm_verts[4], bm_verts[8], bm_verts[9], bm_verts[5]])
            bm.faces.new([bm_verts[5], bm_verts[9], bm_verts[10], bm_verts[6]])
            bm.faces.new([bm_verts[6], bm_verts[10], bm_verts[11], bm_verts[7]])
        else:
            bm.faces.new([bm_verts[3], bm_verts[2], bm_verts[1], bm_verts[0]])
            bm.faces.new([bm_verts[1], bm_verts[5], bm_verts[4], bm_verts[0]])
            bm.faces.new([bm_verts[2], bm_verts[6], bm_verts[5], bm_verts[1]])
            bm.faces.new([bm_verts[3], bm_verts[7], bm_verts[6], bm_verts[2]])
            bm.faces.new([bm_verts[5], bm_verts[9], bm_verts[8], bm_verts[4]])
            bm.faces.new([bm_verts[6], bm_verts[10], bm_verts[9], bm_verts[5]])
            bm.faces.new([bm_verts[7], bm_verts[11], bm_verts[10], bm_verts[6]])
            
        bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.025)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(fauld.data)
        bm.free()
        fauld.data.update()
        
        fauld.modifiers.clear()
        bev = fauld.modifiers.new(name="Bevel", type='BEVEL')
        bev.width = 0.008
        bev.segments = 2
        clean_mesh(fauld)

# =============================================================================
# 2. RE-MODEL HOLMATRO RESCUE SHEAR BLADES (PRECISION HARDENED STEEL)
# =============================================================================

for blade_name, rot_sign in [('Mech_Shear_Blade_Upper', 1), ('Mech_Shear_Blade_Lower', -1)]:
    blade = bpy.data.objects.get(blade_name)
    if blade:
        bm = bmesh.new()
        p_x = 0.68
        p_z = 1.00 + 0.05 * rot_sign
        
        spine_pts = [
            Vector((p_x, 0.0, p_z)),
            Vector((p_x, 0.12, p_z + 0.06 * rot_sign)),
            Vector((p_x, 0.28, p_z + 0.12 * rot_sign)),
            Vector((p_x, 0.46, p_z + 0.14 * rot_sign)),
            Vector((p_x, 0.62, p_z + 0.04 * rot_sign)),
        ]
        
        edge_pts = [
            Vector((p_x, 0.0, p_z)),
            Vector((p_x, 0.14, p_z - 0.02 * rot_sign)),
            Vector((p_x, 0.30, p_z - 0.01 * rot_sign)),
            Vector((p_x, 0.48, p_z - 0.03 * rot_sign)),
            Vector((p_x, 0.62, p_z + 0.04 * rot_sign)),
        ]
        
        thick_half = 0.035
        v_spine_left = [bm.verts.new(p + Vector((-thick_half, 0, 0))) for p in spine_pts]
        v_spine_right = [bm.verts.new(p + Vector((thick_half, 0, 0))) for p in spine_pts]
        v_edge = [bm.verts.new(p) for p in edge_pts]
        
        for i in range(len(spine_pts) - 1):
            bm.faces.new([v_spine_left[i], v_spine_right[i], v_spine_right[i+1], v_spine_left[i+1]])
            bm.faces.new([v_spine_left[i], v_spine_left[i+1], v_edge[i+1], v_edge[i]])
            bm.faces.new([v_spine_right[i], v_edge[i], v_edge[i+1], v_spine_right[i+1]])
            
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(blade.data)
        bm.free()
        blade.data.update()
        
        blade.modifiers.clear()
        bev = blade.modifiers.new(name="Bevel", type='BEVEL')
        bev.width = 0.005
        bev.segments = 2
        clean_mesh(blade)

# =============================================================================
# 3. RE-SCULPT GREN-SKILDUS MANTLE (ORGANIC HEAVY WOOL DRAPE)
# =============================================================================

mantle = bpy.data.objects.get('Sculpt_Gren_Skildus_Mantle')
if mantle:
    bm = bmesh.new()
    rows = 14
    cols = 9
    torc_center = Vector((-0.28, 0.16, 1.82))
    grid = []
    for r in range(rows):
        row_verts = []
        u = r / (rows - 1)
        for c in range(cols):
            v_frac = c / (cols - 1)
            angle = (v_frac - 0.2) * math.pi * 0.9
            radius = 0.30 + 0.14 * u + 0.02 * math.sin(u * 12.0 + c * 3.0)
            
            x = -0.32 - radius * math.cos(angle) * (0.8 + 0.3 * u)
            y = 0.08 + radius * math.sin(angle) * (0.9 + 0.2 * u)
            z = 1.84 - u * 0.95 - 0.04 * math.sin(v_frac * math.pi * 3.0) * (1.0 - u * 0.5)
            
            if u < 0.15:
                blend = u / 0.15
                pos = torc_center.lerp(Vector((x, y, z)), blend)
            else:
                pos = Vector((x, y, z))
                
            fold_wave = 0.022 * math.sin(v_frac * math.pi * 5.0 + u * 4.0)
            pos.x += fold_wave * math.sin(angle)
            pos.y += fold_wave * math.cos(angle)
            row_verts.append(bm.verts.new(pos))
        grid.append(row_verts)
        
    for r in range(rows - 1):
        for c in range(cols - 1):
            bm.faces.new([grid[r][c], grid[r+1][c], grid[r+1][c+1], grid[r][c+1]])
            
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.016)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mantle.data)
    bm.free()
    mantle.data.update()
    
    mantle.modifiers.clear()
    sub = mantle.modifiers.new(name="Subdivision", type='SUBSURF')
    sub.levels = 1
    sub.render_levels = 2
    clean_mesh(mantle)

# =============================================================================
# 4. HIGH-PRESSURE BRAIDED HYDRAULIC HOSES & BRASS COMPRESSION FITTINGS
# =============================================================================

def create_braided_hose(name, start_pt, mid_pts, end_pt, radius=0.018):
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = radius
    curve_data.bevel_resolution = 6
    curve_data.use_fill_caps = True
    
    spline = curve_data.splines.new(type='BEZIER')
    all_pts = [start_pt] + mid_pts + [end_pt]
    spline.bezier_points.add(len(all_pts) - 1)
    
    for i, pt in enumerate(all_pts):
        bp = spline.bezier_points[i]
        bp.co = pt
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
        
    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)
    return obj

def create_compression_fitting(name, loc, rot_euler, radius=0.032, length=0.045):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=6, radius1=radius, radius2=radius, depth=length)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = loc
    obj.rotation_euler = rot_euler
    bpy.context.collection.objects.link(obj)
    clean_mesh(obj)
    return obj

for o in [obj for obj in bpy.data.objects if 'Hose_' in obj.name or 'Fitting_' in obj.name]:
    bpy.data.objects.remove(o, do_unlink=True)

hose_drill_1 = create_braided_hose(
    'Hose_Drill_Main_Feed',
    Vector((-0.35, -0.32, 1.60)),
    [
        Vector((-0.52, -0.22, 1.45)),
        Vector((-0.68, -0.05, 1.30)),
        Vector((-0.72, 0.05, 1.15))
    ],
    Vector((-0.70, 0.12, 1.05)),
    radius=0.020
)

create_compression_fitting('Fitting_Drill_Gen_Outlet', Vector((-0.35, -0.32, 1.60)), (0, math.radians(45), math.radians(-30)))
create_compression_fitting('Fitting_Drill_Housing_Inlet', Vector((-0.70, 0.12, 1.05)), (math.radians(-45), 0, 0))

hose_shear_1 = create_braided_hose(
    'Hose_Shear_Pressure_Line',
    Vector((0.35, -0.32, 1.60)),
    [
        Vector((0.52, -0.22, 1.45)),
        Vector((0.66, -0.05, 1.30)),
        Vector((0.70, 0.05, 1.15))
    ],
    Vector((0.68, 0.12, 1.05)),
    radius=0.020
)

create_compression_fitting('Fitting_Shear_Gen_Outlet', Vector((0.35, -0.32, 1.60)), (0, math.radians(-45), math.radians(30)))
create_compression_fitting('Fitting_Shear_Housing_Inlet', Vector((0.68, 0.12, 1.05)), (math.radians(-45), 0, 0))

for hose_obj in [hose_drill_1, hose_shear_1]:
    bpy.context.view_layer.objects.active = hose_obj
    hose_obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    clean_mesh(hose_obj)

# =============================================================================
# 5. ASSIGN MATERIALS TO ALL COMPONENTS
# =============================================================================

mat_iron = bpy.data.materials.get('QA_PBR_Weathered_CastIron')
mat_bronze = bpy.data.materials.get('QA_PBR_Weathered_Bronze')
mat_cloth = bpy.data.materials.get('QA_PBR_Gren_Skildus_Wool')

mat_hose = bpy.data.materials.get('QA_PBR_Braided_HydraulicHose')
if not mat_hose:
    mat_hose = bpy.data.materials.new('QA_PBR_Braided_HydraulicHose')
    mat_hose.use_nodes = True
    nodes = mat_hose.node_tree.nodes
    links = mat_hose.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = (0.04, 0.04, 0.045, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.35
    bsdf.inputs['Roughness'].default_value = 0.55

mat_tool_steel = bpy.data.materials.get('QA_PBR_Hardened_ToolSteel')
if not mat_tool_steel:
    mat_tool_steel = bpy.data.materials.new('QA_PBR_Hardened_ToolSteel')
    mat_tool_steel.use_nodes = True
    t_nodes = mat_tool_steel.node_tree.nodes
    t_links = mat_tool_steel.node_tree.links
    t_nodes.clear()
    t_out = t_nodes.new('ShaderNodeOutputMaterial')
    t_bsdf = t_nodes.new('ShaderNodeBsdfPrincipled')
    t_links.new(t_bsdf.outputs['BSDF'], t_out.inputs['Surface'])
    t_bsdf.inputs['Base Color'].default_value = (0.38, 0.38, 0.40, 1.0)
    t_bsdf.inputs['Metallic'].default_value = 0.95
    t_bsdf.inputs['Roughness'].default_value = 0.18

for obj in bpy.data.objects:
    if obj.type == 'MESH':
        if 'Mantle' in obj.name:
            obj.data.materials.clear()
            obj.data.materials.append(mat_cloth)
        elif 'Hose' in obj.name:
            obj.data.materials.clear()
            obj.data.materials.append(mat_hose)
        elif 'Fitting' in obj.name or 'Bronze' in obj.name or 'Trim' in obj.name or 'Cap' in obj.name or 'Pin' in obj.name or 'Boss' in obj.name or 'Flange' in obj.name or 'Torc' in obj.name or 'Gauge' in obj.name or 'Tooth' in obj.name:
            obj.data.materials.clear()
            obj.data.materials.append(mat_bronze)
        elif 'Blade' in obj.name or 'Flute' in obj.name:
            obj.data.materials.clear()
            obj.data.materials.append(mat_tool_steel)
        elif 'Visor' in obj.name or 'Slit' in obj.name:
            mat_amber = bpy.data.materials.get('QA_Amber_Visor')
            obj.data.materials.clear()
            obj.data.materials.append(mat_amber)
        else:
            obj.data.materials.clear()
            obj.data.materials.append(mat_iron)

# =============================================================================
# 6. ENFORCE EXACT KINEMATIC DATUMS (8'0" / 2.4384m Height, 0.0000m Ground)
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

bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"SUCCESS: Production Perfection Pass applied to {blend_path}")
