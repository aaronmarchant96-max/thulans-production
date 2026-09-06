"""
THULAN IP — PRODUCTION TOOL
Script: build_shot01_greybox.py
Target: Blender 4.2+ (EEVEE Next / Cycles / Workbench)
Purpose: Procedurally generate the complete Shot 01 (Megalithic Cavern & Varek Silhouette)
         greybox scene to validate scale, vertical anxiety, dieselpunk brutalism,
         and character silhouette prior to asset detailing.

Usage:
  1. Inside Blender: Open Scripting workspace -> Open this file -> Run Script.
  2. From Terminal: blender --python tools/build_shot01_greybox.py
"""

import bpy
import math
from mathutils import Vector, Euler

def clear_scene():
    """Clear default objects from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Remove orphan data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in bpy.data.lights:
        if block.users == 0:
            bpy.data.lights.remove(block)
    for block in bpy.data.cameras:
        if block.users == 0:
            bpy.data.cameras.remove(block)

def get_or_create_collection(name, parent_collection=None):
    """Retrieve or create a scene collection."""
    if name in bpy.data.collections:
        col = bpy.data.collections[name]
    else:
        col = bpy.data.collections.new(name)
        if parent_collection:
            parent_collection.children.link(col)
        else:
            bpy.context.scene.collection.children.link(col)
    return col

def create_clay_material(name, color=(0.55, 0.55, 0.58, 1.0), roughness=0.85):
    """Create a neutral greybox clay material for visual consistency."""
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = color
            bsdf.inputs["Roughness"].default_value = roughness
    return mat

def create_emissive_material(name, color=(1.0, 0.8, 0.5, 1.0), strength=15.0):
    """Create a high-contrast emissive indicator material."""
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        node_out = nodes.new(type='ShaderNodeOutputMaterial')
        node_emit = nodes.new(type='ShaderNodeEmission')
        node_emit.inputs['Color'].default_value = color
        node_emit.inputs['Strength'].default_value = strength
        mat.node_tree.links.new(node_emit.outputs['Emission'], node_out.inputs['Surface'])
    return mat

# ==============================================================================
# 1. ENVIRONMENT: MEGALITHIC CAVERN & CYCLOPEAN ROCK WALLS
# ==============================================================================
def build_megalithic_cavern(collection):
    """Construct the continent-scale hollow mountain chamber (2,000m vertical)."""
    clay_rock = create_clay_material("Mat_Rock_Clay", color=(0.18, 0.18, 0.20, 1.0), roughness=0.95)
    clay_iron = create_clay_material("Mat_Structural_Iron", color=(0.28, 0.28, 0.30, 1.0), roughness=0.7)

    # Cavern Back Wall / Terraced Strata (Stepped cyclopean excavation)
    for tier in range(-2, 10):
        z_pos = tier * 180.0
        depth_offset = tier * 35.0
        width = 1200.0 + (tier * 40.0)
        
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(0.0, 350.0 + depth_offset, z_pos),
            scale=(width, 120.0, 160.0)
        )
        wall = bpy.context.active_object
        wall.name = f"Cavern_Strata_Tier_{tier:02d}"
        wall.data.materials.append(clay_rock)
        collection.objects.link(wall)
        bpy.context.scene.collection.objects.unlink(wall)

    # Massive Load-Bearing Mountain Ribs (Vertical Cyclopean Struts)
    for x_offset in [-450.0, -180.0, 180.0, 450.0]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=45.0,
            depth=2200.0,
            vertices=12,
            location=(x_offset, 280.0, 800.0)
        )
        pillar = bpy.context.active_object
        pillar.name = f"Megalithic_Rib_X{int(x_offset)}"
        pillar.data.materials.append(clay_rock)
        collection.objects.link(pillar)
        bpy.context.scene.collection.objects.unlink(pillar)

    # Overhead Cyclopean Arches (Tectonic Ceiling Trusses)
    for arch_idx in range(4):
        z_arch = 600.0 + (arch_idx * 300.0)
        y_arch = 150.0 + (arch_idx * 60.0)
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(0.0, y_arch, z_arch),
            scale=(900.0, 60.0, 50.0)
        )
        arch = bpy.context.active_object
        arch.name = f"Tectonic_Ceiling_Truss_{arch_idx:02d}"
        arch.data.materials.append(clay_iron)
        collection.objects.link(arch)
        bpy.context.scene.collection.objects.unlink(arch)

# ==============================================================================
# 2. INFRASTRUCTURE: LIGHT TOWERS, LIFTS & FOREGROUND GANTRY
# ==============================================================================
def build_infrastructure(collection):
    """Build vertical light towers, hanging pipes, and the observation gantry."""
    clay_iron = create_clay_material("Mat_Structural_Iron")
    emit_sodium = create_emissive_material("Mat_Sodium_Light", color=(0.95, 0.98, 1.0, 1.0), strength=25.0)
    emit_orange = create_emissive_material("Mat_Furnace_Emissive", color=(1.0, 0.35, 0.05, 1.0), strength=12.0)

    # Modular Light Towers (Ascending up the cavern walls)
    tower_positions = [
        (-280.0, 220.0), (-90.0, 260.0), (120.0, 240.0), (320.0, 210.0),
        (-180.0, 160.0), (220.0, 170.0)
    ]
    
    for t_idx, (tx, ty) in enumerate(tower_positions):
        # Vertical Truss Tower
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(tx, ty, 600.0),
            scale=(18.0, 18.0, 1600.0)
        )
        tower = bpy.context.active_object
        tower.name = f"Light_Tower_Truss_{t_idx:02d}"
        tower.data.materials.append(clay_iron)
        collection.objects.link(tower)
        bpy.context.scene.collection.objects.unlink(tower)

        # Light Pod Platforms along the tower height
        for z_level in range(-100, 1500, 120):
            bpy.ops.mesh.primitive_cube_add(
                size=1.0,
                location=(tx, ty - 12.0, z_level),
                scale=(26.0, 10.0, 6.0)
            )
            platform = bpy.context.active_object
            platform.name = f"Tower_{t_idx:02d}_Pod_Z{z_level}"
            platform.data.materials.append(clay_iron)
            collection.objects.link(platform)
            bpy.context.scene.collection.objects.unlink(platform)

            # Emissive Floodlight Lens
            bpy.ops.mesh.primitive_cylinder_add(
                radius=4.5,
                depth=3.0,
                vertices=8,
                location=(tx, ty - 18.0, z_level),
                rotation=(math.radians(90), 0, 0)
            )
            lens = bpy.context.active_object
            lens.name = f"Tower_{t_idx:02d}_Lens_Z{z_level}"
            lens.data.materials.append(emit_sodium)
            collection.objects.link(lens)
            bpy.context.scene.collection.objects.unlink(lens)

    # Heavy Hanging Conduits & Ventilation Shafts
    for pipe_x in [-220.0, -140.0, 160.0, 280.0]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=12.0,
            depth=1800.0,
            vertices=12,
            location=(pipe_x, 180.0, 500.0)
        )
        pipe = bpy.context.active_object
        pipe.name = f"Ventilation_Conduit_X{int(pipe_x)}"
        pipe.data.materials.append(clay_iron)
        collection.objects.link(pipe)
        bpy.context.scene.collection.objects.unlink(pipe)

    # --------------------------------------------------------------------------
    # Foreground Cantilever Observation Gantry (Where Varek & Worker stand)
    # --------------------------------------------------------------------------
    # Main Deck Platform (Z = 0.0m)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0.0, 0.0, -0.6),
        scale=(45.0, 24.0, 1.2)
    )
    gantry_deck = bpy.context.active_object
    gantry_deck.name = "Gantry_Main_Deck"
    gantry_deck.data.materials.append(clay_iron)
    collection.objects.link(gantry_deck)
    bpy.context.scene.collection.objects.unlink(gantry_deck)

    # Gantry Edge Safety Railing & Toe-Board
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0.0, 11.5, 0.6),
        scale=(45.0, 0.3, 1.2)
    )
    rail = bpy.context.active_object
    rail.name = "Gantry_Safety_Railing"
    rail.data.materials.append(clay_iron)
    collection.objects.link(rail)
    bpy.context.scene.collection.objects.unlink(rail)

    # Massive Under-Deck Cantilever Truss & Hydraulic Anchor Dampers
    for damper_x in [-18.0, 0.0, 18.0]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=1.8,
            depth=35.0,
            vertices=12,
            location=(damper_x, -5.0, -14.0),
            rotation=(math.radians(35), 0, 0)
        )
        damper = bpy.context.active_object
        damper.name = f"Gantry_Hydraulic_Damper_X{int(damper_x)}"
        damper.data.materials.append(clay_iron)
        collection.objects.link(damper)
        bpy.context.scene.collection.objects.unlink(damper)

    # Worker Console & Diagnostic Terminal (Midground Left: X = -3.8m, Y = 3.2m)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(-3.8, 3.2, 0.6),
        scale=(1.8, 0.9, 1.2)
    )
    console = bpy.context.active_object
    console.name = "Worker_Diagnostic_Console"
    console.data.materials.append(clay_iron)
    collection.objects.link(console)
    bpy.context.scene.collection.objects.unlink(console)

    # Small console screen glow
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(-3.8, 3.2, 1.25),
        scale=(1.4, 0.4, 0.15)
    )
    screen = bpy.context.active_object
    screen.name = "Console_CRT_Screen"
    screen.data.materials.append(emit_orange)
    collection.objects.link(screen)
    bpy.context.scene.collection.objects.unlink(screen)

# ==============================================================================
# 3. CHARACTERS: VAREK BLOCKOUT (3.0m) & HUMAN MINER (1.75m)
# ==============================================================================
def build_varek_blockout(collection):
    """
    Construct Varek in the Tectonic Anchor Rig (~3.0m tall).
    Key features: Overhead load-bearing yoke, broad asymmetric Gren-Skildus pauldron,
    heavy hydraulic leg pistons, locked magnetic heelspikes, rear exhaust pack.
    """
    mat_varek = create_clay_material("Mat_Varek_Rig", color=(0.35, 0.36, 0.38, 1.0), roughness=0.6)
    mat_pauldron = create_clay_material("Mat_Gren_Skildus_Clay", color=(0.22, 0.35, 0.26, 1.0), roughness=0.55)
    
    varek_root_loc = Vector((2.8, 4.5, 0.0))  # Right-third placement on gantry
    
    # 1. Base / Boots with Locked Heelspikes (Z = 0.0 to 0.4m)
    for leg_side in [-0.55, 0.55]:
        # Heavy Boot
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(varek_root_loc.x + leg_side, varek_root_loc.y + 0.1, 0.25),
            scale=(0.55, 0.95, 0.5)
        )
        boot = bpy.context.active_object
        boot.name = f"Varek_Boot_{'L' if leg_side > 0 else 'R'}"
        boot.data.materials.append(mat_varek)
        collection.objects.link(boot)
        bpy.context.scene.collection.objects.unlink(boot)

        # Deployed Rear Heelspike Claws (Anchoring to iron deck)
        bpy.ops.mesh.primitive_cone_add(
            radius1=0.18,
            depth=0.5,
            vertices=8,
            location=(varek_root_loc.x + leg_side, varek_root_loc.y - 0.45, 0.15),
            rotation=(math.radians(-35), 0, 0)
        )
        spike = bpy.context.active_object
        spike.name = f"Varek_Heelspike_{'L' if leg_side > 0 else 'R'}"
        spike.data.materials.append(mat_varek)
        collection.objects.link(spike)
        bpy.context.scene.collection.objects.unlink(spike)

        # Hydraulic Shins & Knee Armor (Z = 0.5 to 1.3m)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.26,
            depth=0.85,
            vertices=10,
            location=(varek_root_loc.x + leg_side, varek_root_loc.y, 0.85)
        )
        shin = bpy.context.active_object
        shin.name = f"Varek_Shin_{'L' if leg_side > 0 else 'R'}"
        shin.data.materials.append(mat_varek)
        collection.objects.link(shin)
        bpy.context.scene.collection.objects.unlink(shin)

        # Heavy Thigh & External Hydraulic Cylinder (Z = 1.3 to 1.9m)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.28,
            depth=0.7,
            vertices=10,
            location=(varek_root_loc.x + leg_side, varek_root_loc.y, 1.6)
        )
        thigh = bpy.context.active_object
        thigh.name = f"Varek_Thigh_{'L' if leg_side > 0 else 'R'}"
        thigh.data.materials.append(mat_varek)
        collection.objects.link(thigh)
        bpy.context.scene.collection.objects.unlink(thigh)

    # 2. Pelvis & Tectonic Girdle (Z = 1.85m to 2.1m)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(varek_root_loc.x, varek_root_loc.y, 1.95),
        scale=(1.35, 0.85, 0.45)
    )
    pelvis = bpy.context.active_object
    pelvis.name = "Varek_Pelvis_Girdle"
    pelvis.data.materials.append(mat_varek)
    collection.objects.link(pelvis)
    bpy.context.scene.collection.objects.unlink(pelvis)

    # 3. Heavy Torso & Respirator Intake Core (Z = 2.1 to 2.8m)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(varek_root_loc.x, varek_root_loc.y + 0.05, 2.45),
        scale=(1.45, 1.0, 0.8)
    )
    torso = bpy.context.active_object
    torso.name = "Varek_Torso_Core"
    torso.data.materials.append(mat_varek)
    collection.objects.link(torso)
    bpy.context.scene.collection.objects.unlink(torso)

    # 4. Helm & Rebreather Housing (Z = 2.7m to 3.0m)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(varek_root_loc.x, varek_root_loc.y + 0.12, 2.82),
        scale=(0.45, 0.5, 0.45)
    )
    helm = bpy.context.active_object
    helm.name = "Varek_Helm_Visor"
    helm.data.materials.append(mat_varek)
    collection.objects.link(helm)
    bpy.context.scene.collection.objects.unlink(helm)

    # 5. Overhead Structural Yoke / Roll-Cage (Key Thulan Silhouette)
    # Struts framing the shoulders and head to bear overhead cave-in loads
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.95,
        minor_radius=0.14,
        location=(varek_root_loc.x, varek_root_loc.y, 2.95),
        rotation=(math.radians(90), 0, 0)
    )
    yoke = bpy.context.active_object
    yoke.name = "Varek_Overhead_Structural_Yoke"
    yoke.scale = (1.1, 0.7, 0.9)
    yoke.data.materials.append(mat_varek)
    collection.objects.link(yoke)
    bpy.context.scene.collection.objects.unlink(yoke)

    # 6. Ancestral Left Shoulder — The Gren-Skildus (Massive Curved Pauldron)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.62,
        depth=0.75,
        vertices=12,
        location=(varek_root_loc.x + 0.95, varek_root_loc.y, 2.72),
        rotation=(0, math.radians(25), math.radians(15))
    )
    pauldron_l = bpy.context.active_object
    pauldron_l.name = "Varek_Gren_Skildus_Pauldron"
    pauldron_l.data.materials.append(mat_pauldron)
    collection.objects.link(pauldron_l)
    bpy.context.scene.collection.objects.unlink(pauldron_l)

    # 7. Right Shoulder — Industrial Hydraulic Lift Articulation
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(varek_root_loc.x - 0.92, varek_root_loc.y, 2.68),
        scale=(0.55, 0.65, 0.65)
    )
    pauldron_r = bpy.context.active_object
    pauldron_r.name = "Varek_Right_Hydraulic_Joint"
    pauldron_r.data.materials.append(mat_varek)
    collection.objects.link(pauldron_r)
    bpy.context.scene.collection.objects.unlink(pauldron_r)

    # 8. Arms & Massive Gauntlets (Holding railing / braced at side)
    for arm_side, arm_x in [("L", 0.95), ("R", -0.95)]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.22,
            depth=1.1,
            vertices=10,
            location=(varek_root_loc.x + arm_x, varek_root_loc.y + 0.15, 2.05),
            rotation=(math.radians(15), 0, 0)
        )
        arm = bpy.context.active_object
        arm.name = f"Varek_Arm_{arm_side}"
        arm.data.materials.append(mat_varek)
        collection.objects.link(arm)
        bpy.context.scene.collection.objects.unlink(arm)

    # 9. Rear Thermal Unit & Diesel/Pneumatic Exhaust Chimneys
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(varek_root_loc.x, varek_root_loc.y - 0.55, 2.5),
        scale=(1.1, 0.5, 0.9)
    )
    backpack = bpy.context.active_object
    backpack.name = "Varek_Backpack_Power_Unit"
    backpack.data.materials.append(mat_varek)
    collection.objects.link(backpack)
    bpy.context.scene.collection.objects.unlink(backpack)

    for ex_x in [-0.35, 0.35]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.12,
            depth=0.8,
            vertices=8,
            location=(varek_root_loc.x + ex_x, varek_root_loc.y - 0.75, 2.95),
            rotation=(math.radians(-15), 0, 0)
        )
        exhaust = bpy.context.active_object
        exhaust.name = f"Varek_Exhaust_Chimney_{'L' if ex_x > 0 else 'R'}"
        exhaust.data.materials.append(mat_varek)
        collection.objects.link(exhaust)
        bpy.context.scene.collection.objects.unlink(exhaust)

def build_human_miner_blockout(collection):
    """
    Construct the baseline mortal human worker (~1.75m tall).
    Placed midground left (X = -3.8m, Y = 2.6m) at the diagnostic console.
    This anchors the human-to-Thulan-to-mountain scale chain.
    """
    mat_worker = create_clay_material("Mat_Worker_Clay", color=(0.45, 0.42, 0.38, 1.0), roughness=0.9)
    
    worker_loc = Vector((-3.8, 2.6, 0.0))
    
    # Boots & Legs (Z = 0.0 to 0.9m)
    for leg_x in [-0.15, 0.15]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.10,
            depth=0.9,
            vertices=8,
            location=(worker_loc.x + leg_x, worker_loc.y, 0.45)
        )
        leg = bpy.context.active_object
        leg.name = f"Worker_Leg_{'L' if leg_x > 0 else 'R'}"
        leg.data.materials.append(mat_worker)
        collection.objects.link(leg)
        bpy.context.scene.collection.objects.unlink(leg)

    # Torso with Heavy Work Vest (Z = 0.9m to 1.45m)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(worker_loc.x, worker_loc.y, 1.18),
        scale=(0.48, 0.30, 0.55)
    )
    torso = bpy.context.active_object
    torso.name = "Worker_Torso"
    torso.data.materials.append(mat_worker)
    collection.objects.link(torso)
    bpy.context.scene.collection.objects.unlink(torso)

    # Head with Miner's Hardhat & Respirator Mask (Z = 1.45m to 1.75m)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(worker_loc.x, worker_loc.y + 0.05, 1.62),
        scale=(0.22, 0.26, 0.24)
    )
    head = bpy.context.active_object
    head.name = "Worker_Head_Helmet"
    head.data.materials.append(mat_worker)
    collection.objects.link(head)
    bpy.context.scene.collection.objects.unlink(head)

    # Arms leaning forward onto console (Z = 1.0m to 1.35m)
    for arm_x in [-0.28, 0.28]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.07,
            depth=0.55,
            vertices=8,
            location=(worker_loc.x + arm_x, worker_loc.y + 0.25, 1.15),
            rotation=(math.radians(45), 0, 0)
        )
        arm = bpy.context.active_object
        arm.name = f"Worker_Arm_{'L' if arm_x > 0 else 'R'}"
        arm.data.materials.append(mat_worker)
        collection.objects.link(arm)
        bpy.context.scene.collection.objects.unlink(arm)

# ==============================================================================
# 4. CINEMATOGRAPHY: CAMERA SETUP (SHOT 01 SPEC)
# ==============================================================================
def build_cinematic_camera(collection):
    """
    Set up the 24mm wide cinematic camera positioned low on the gantry (Z = 1.2m),
    pitched upward +14 deg to emphasize the endless vertical rise of the light towers.
    """
    cam_data = bpy.data.cameras.new("Cam_Shot01_Est_Data")
    cam_data.lens = 24.0  # 24mm wide angle for vertical scale drama
    cam_data.sensor_width = 36.0  # Full frame 35mm sensor
    cam_data.sensor_height = 20.25  # 16:9 aspect ratio
    cam_data.clip_start = 0.1
    cam_data.clip_end = 5000.0  # Ensure deep cavern visibility

    cam_obj = bpy.data.objects.new("Camera_Shot01_Est", cam_data)
    # Position: slightly to the left, pulled back, lower than human eye-level
    cam_obj.location = Vector((-2.2, -9.5, 1.25))
    cam_obj.rotation_euler = Euler((math.radians(78.5), 0.0, math.radians(-12.0)), 'XYZ')

    collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    
    # Set scene resolution to 4K cinematic (3840 x 2160) at 24fps
    bpy.context.scene.render.resolution_x = 3840
    bpy.context.scene.render.resolution_y = 2160
    bpy.context.scene.render.fps = 24

# ==============================================================================
# 5. LIGHTING & ATMOSPHERIC DEPTH HIERARCHY
# ==============================================================================
def build_lighting_and_atmosphere(collection):
    """Create the 4-layer lighting hierarchy specified in SHOT_01_SPEC.md."""
    # Layer 1: Deep Abyss Furnace Glow (Low Key, Amber from Z = -250m)
    abyss_light_data = bpy.data.lights.new("Light_Abyss_Furnace", type='SUN')
    abyss_light_data.color = (1.0, 0.35, 0.08)  # Smoldering Amber
    abyss_light_data.energy = 3.5
    abyss_light_obj = bpy.data.objects.new("Light_Abyss_Furnace", abyss_light_data)
    abyss_light_obj.rotation_euler = Euler((math.radians(-75.0), math.radians(20.0), 0.0), 'XYZ')
    collection.objects.link(abyss_light_obj)

    # Layer 2: Overhead Gantry Industrial Floodlight (Console Key Light)
    console_light_data = bpy.data.lights.new("Light_Console_Flood", type='SPOT')
    console_light_data.color = (1.0, 0.92, 0.80)
    console_light_data.energy = 850.0
    console_light_data.spot_size = math.radians(45.0)
    console_light_data.spot_blend = 0.35
    console_light_obj = bpy.data.objects.new("Light_Console_Flood", console_light_data)
    console_light_obj.location = Vector((-3.8, 2.8, 6.5))
    console_light_obj.rotation_euler = Euler((math.radians(15.0), 0.0, 0.0), 'XYZ')
    collection.objects.link(console_light_obj)

    # Layer 3: High-Contrast Rim Light on Varek's Left Pauldron (Gren-Skildus Edge)
    rim_light_data = bpy.data.lights.new("Light_Varek_Rim", type='SPOT')
    rim_light_data.color = (0.75, 0.88, 1.0)  # Cold Pale Steel
    rim_light_data.energy = 3500.0
    rim_light_data.spot_size = math.radians(30.0)
    rim_light_data.spot_blend = 0.2
    rim_light_obj = bpy.data.objects.new("Light_Varek_Rim", rim_light_data)
    rim_light_obj.location = Vector((18.0, 32.0, 14.0))
    rim_light_obj.rotation_euler = Euler((math.radians(-155.0), math.radians(-35.0), math.radians(-25.0)), 'XYZ')
    collection.objects.link(rim_light_obj)

    # Layer 4: Volumetric Atmospheric Bounding Box
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0.0, 150.0, 400.0),
        scale=(1600.0, 600.0, 1200.0)
    )
    fog_box = bpy.context.active_object
    fog_box.name = "Atmospheric_Volume_Scatter"
    
    # Create Volume Scatter Material
    mat_fog = bpy.data.materials.new(name="Mat_Volume_Fog")
    mat_fog.use_nodes = True
    nodes = mat_fog.node_tree.nodes
    nodes.clear()
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_vol = nodes.new(type='ShaderNodeVolumeScatter')
    node_vol.inputs['Color'].default_value = (0.7, 0.75, 0.82, 1.0)
    node_vol.inputs['Density'].default_value = 0.0015
    node_vol.inputs['Anisotropy'].default_value = 0.65  # Strong forward god rays
    mat_fog.node_tree.links.new(node_vol.outputs['Volume'], node_out.inputs['Volume'])
    
    fog_box.data.materials.append(mat_fog)
    collection.objects.link(fog_box)
    bpy.context.scene.collection.objects.unlink(fog_box)

# ==============================================================================
# MAIN SCENE BUILDER
# ==============================================================================
def main():
    print("==================================================================")
    print("THULAN PRODUCTION PIPELINE: GENERATING SHOT 01 GREYBOX")
    print("==================================================================")
    
    clear_scene()
    
    # Hierarchy Collections
    col_env = get_or_create_collection("01_ENVIRONMENT")
    col_infra = get_or_create_collection("02_INFRASTRUCTURE")
    col_chars = get_or_create_collection("03_CHARACTERS")
    col_cams = get_or_create_collection("04_CAMERAS")
    col_lights = get_or_create_collection("05_LIGHTS_ATMOSPHERE")
    
    # Build components
    print("-> Building Megalithic Cavern geometry...")
    build_megalithic_cavern(col_env)
    
    print("-> Building Light Towers & Gantry Infrastructure...")
    build_infrastructure(col_infra)
    
    print("-> Building Varek Tectonic Anchor Rig Blockout (3.0m)...")
    build_varek_blockout(col_chars)
    
    print("-> Building Human Miner Scale Anchor (1.75m)...")
    build_human_miner_blockout(col_chars)
    
    print("-> Setting up 24mm Cinematic Camera (Shot 01)...")
    build_cinematic_camera(col_cams)
    
    print("-> Configuring Atmospheric Scattering & Lighting Hierarchy...")
    build_lighting_and_atmosphere(col_lights)
    
    # Viewport Display Settings (Clay QA Mode)
    bpy.context.scene.display.shading.light = 'MATCAP'
    bpy.context.scene.display.shading.studio_light = 'clay.exr'
    bpy.context.scene.display.shading.show_cavity = True
    bpy.context.scene.display.shading.cavity_type = 'BOTH'
    
    print("==================================================================")
    print("SHOT 01 GREYBOX GENERATION COMPLETE.")
    print("Camera: 'Camera_Shot01_Est' (24mm, Z=1.25m, Pitch=+14 deg)")
    print("Varek Pos: (2.8, 4.5, 0.0) | Worker Pos: (-3.8, 2.6, 0.0)")
    print("Scale Chain: Worker (1.75m) -> Varek (3.0m) -> Cavern (2,000m)")
    print("==================================================================")

if __name__ == "__main__":
    main()
