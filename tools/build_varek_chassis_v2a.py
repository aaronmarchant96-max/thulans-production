#!/usr/bin/env python3
"""Build the static, concept-faithful Varek V2A chassis in Blender 5.2."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "VAREK_CHASSIS_V2_BUILD_PLAN.md"
CONTRACT_PATH = ROOT / "spec" / "varek_chassis_v2a_contract.json"
VALIDATOR = ROOT / "tools" / "validate_varek_chassis_v2a.py"
DEFAULT_OUTPUT = ROOT / "blender" / "candidates" / "varek-chassis-v2a-static.blend"
EVIDENCE_DIR = ROOT / "evidence" / "varek-chassis-v2a"
FAILURE_PATH = EVIDENCE_DIR / "failure.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def fail(phase: str, message: str, details=None) -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    FAILURE_PATH.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "claim_class": "OBSERVED",
                "gate": "VAREK_CHASSIS_V2A",
                "overall": "FAIL",
                "phase": phase,
                "message": message,
                "details": details or {},
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    raise RuntimeError(f"{phase}: {message}")


def args_from_cli():
    values = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--source-git-commit", required=True)
    parser.add_argument("--source-repo-state", choices=("CLEAN",), required=True)
    parser.add_argument("--plan-git-commit", required=True)
    return parser.parse_args(values)


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for data in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras):
        for block in list(data):
            if block.users == 0:
                data.remove(block)


def collections(names):
    result = {}
    for name in names:
        item = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(item)
        result[name] = item
    return result


def material(name, color):
    item = bpy.data.materials.new(name)
    item.diffuse_color = (*color, 1.0)
    return item


def relink(obj, collection):
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    collection.objects.link(obj)


def tag(obj, importance="SECONDARY", cutaway=False):
    obj["source_kind"] = "PROCEDURAL_ORIGINAL"
    obj["form_importance"] = importance
    obj["production_geometry"] = True
    obj["review_hide_cutaway"] = bool(cutaway)
    return obj


def apply_scale(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.select_set(False)


def bevel(obj, width=0.012, segments=2):
    if width <= 0:
        return obj
    modifier = obj.modifiers.new("Manufactured_Edge", "BEVEL")
    modifier.width = width
    modifier.segments = segments
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    return obj


def box(name, location, dimensions, collection, mat, rotation=(0.0, 0.0, 0.0), edge=0.012, importance="SECONDARY", cutaway=False):
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    apply_scale(obj)
    bevel(obj, min(edge, min(dimensions) * 0.18))
    obj.data.materials.append(mat)
    relink(obj, collection)
    return tag(obj, importance, cutaway)


def prism(name, location, height, width_bottom, width_top, depth_bottom, depth_top, collection, mat, edge=0.012, importance="PRIMARY", cutaway=False):
    z0, z1 = -height / 2, height / 2
    vertices = []
    for z, width, depth in ((z0, width_bottom, depth_bottom), (z1, width_top, depth_top)):
        vertices.extend(((-width / 2, -depth / 2, z), (width / 2, -depth / 2, z), (width / 2, depth / 2, z), (-width / 2, depth / 2, z)))
    faces = ((0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (4, 0, 3, 7))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bevel(obj, edge)
    return tag(obj, importance, cutaway)


def cylinder(name, location, radius, depth, collection, mat, rotation=(0.0, 0.0, 0.0), vertices=16, importance="SECONDARY", cutaway=False):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    apply_scale(obj)
    bevel(obj, min(0.008, radius * 0.2), 2)
    obj.data.materials.append(mat)
    relink(obj, collection)
    return tag(obj, importance, cutaway)


def sphere(name, location, scale, collection, mat, importance="SECONDARY", cutaway=False):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    apply_scale(obj)
    obj.data.materials.append(mat)
    relink(obj, collection)
    return tag(obj, importance, cutaway)


def beam(name, start, end, thickness, collection, mat, importance="PRIMARY", cutaway=False):
    start, end = Vector(start), Vector(end)
    delta = end - start
    obj = box(name, (start + end) / 2, (thickness, thickness, delta.length), collection, mat, edge=thickness * 0.18, importance=importance, cutaway=cutaway)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = delta.to_track_quat("Z", "Y")
    obj.rotation_mode = "XYZ"
    return obj


def arch(name, points, radius, collection, mat, importance="PRIMARY"):
    curve = bpy.data.curves.new(name + "_Curve", "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 2
    curve.bevel_depth = radius
    curve.bevel_resolution = 2
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, coordinate in zip(spline.bezier_points, points):
        point.co = coordinate
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.name = name
    obj.select_set(False)
    return tag(obj, importance)


def bounds(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points))), Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))


def union_bounds(objects):
    pairs = [bounds(obj) for obj in objects]
    return Vector((min(a.x for a, _ in pairs), min(a.y for a, _ in pairs), min(a.z for a, _ in pairs))), Vector((max(b.x for _, b in pairs), max(b.y for _, b in pairs), max(b.z for _, b in pairs)))


def normalize_height(objects, target):
    low, high = union_bounds(objects)
    factor = target / (high.z - low.z)
    for obj in objects:
        inverse = obj.matrix_world.inverted()
        for vertex in obj.data.vertices:
            world = obj.matrix_world @ vertex.co
            normalized = Vector((world.x * factor, world.y * factor, (world.z - low.z) * factor))
            vertex.co = inverse @ normalized
        obj.data.update()
    return factor


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def build(contract):
    clear_scene()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.render.fps = 24
    scene.frame_start = scene.frame_end = 1
    cols = collections(contract["required_collections"])
    iron = material("QA_Iron_Clay", (0.34, 0.36, 0.37))
    dark = material("QA_Dark_Clay", (0.16, 0.18, 0.19))
    pilot = material("QA_Pilot_Clay", (0.46, 0.27, 0.22))
    plate = material("QA_Ancestral_Plate_Clay", (0.27, 0.31, 0.29))

    ref, human, hull, frame, power, ground, hands, tertiary, cameras = (cols[name] for name in contract["required_collections"])

    # Full-limbed provisional human envelope, authored before the machine.
    sphere("Pilot_Head", (0.0, -0.035, 1.91), (0.105, 0.09, 0.125), human, pilot, cutaway=False)
    prism("Pilot_Torso", (0.0, 0.0, 1.52), 0.56, 0.28, 0.35, 0.18, 0.22, human, pilot, 0.04, "SECONDARY")
    prism("Pilot_Pelvis", (0.0, 0.0, 1.18), 0.20, 0.25, 0.30, 0.17, 0.19, human, pilot, 0.035, "SECONDARY")
    for side, sign in (("L", -1), ("R", 1)):
        beam(f"Pilot_UpperArm_{side}", (sign * 0.18, 0.0, 1.70), (sign * 0.24, 0.0, 1.34), 0.055, human, pilot, "SECONDARY")
        beam(f"Pilot_Forearm_{side}", (sign * 0.24, 0.0, 1.34), (sign * 0.25, -0.01, 1.02), 0.05, human, pilot, "SECONDARY")
        beam(f"Pilot_Thigh_{side}", (sign * 0.105, 0.0, 1.10), (sign * 0.13, 0.0, 0.70), 0.075, human, pilot, "SECONDARY")
        beam(f"Pilot_Shin_{side}", (sign * 0.13, 0.0, 0.70), (sign * 0.15, -0.015, 0.29), 0.065, human, pilot, "SECONDARY")
        box(f"Pilot_Foot_{side}", (sign * 0.15, -0.065, 0.19), (0.12, 0.25, 0.09), human, pilot, edge=0.025)

    # Recessed operator cell and tapered survival hull.
    sphere("Operator_Cell", (0.0, -0.075, 1.94), (0.175, 0.145, 0.19), hull, dark, "PRIMARY", True)
    box("Operator_Visor_Guard", (0.0, -0.207, 1.96), (0.23, 0.035, 0.055), hull, iron, edge=0.008, importance="PRIMARY", cutaway=True)
    prism("Thoracic_Hull", (0.0, 0.0, 1.58), 0.64, 0.47, 0.58, 0.31, 0.39, hull, dark, 0.045, "PRIMARY", True)
    prism("Abdominal_Hull", (0.0, 0.005, 1.26), 0.24, 0.38, 0.44, 0.26, 0.30, hull, dark, 0.035, "PRIMARY", True)

    # Two deep, curved yokes and their cross-load bridges.
    profile = [(-0.54, 0.0, 1.93), (-0.62, 0.0, 2.12), (-0.52, 0.0, 2.30), (-0.26, 0.0, 2.395), (0.0, 0.0, 2.415), (0.26, 0.0, 2.395), (0.52, 0.0, 2.30), (0.62, 0.0, 2.12), (0.54, 0.0, 1.93)]
    arch("Yoke_Arch_Front", [(x, -0.12, z) for x, _, z in profile], 0.045, frame, iron)
    arch("Yoke_Arch_Rear", [(x, 0.18, z) for x, _, z in profile], 0.045, frame, iron)
    for x in (-0.50, 0.0, 0.50):
        beam(f"Yoke_Depth_Bridge_{x:+.2f}", (x, -0.12, 2.31 if x else 2.415), (x, 0.18, 2.31 if x else 2.415), 0.055, frame, iron)

    # Visible primary load paths, separated from the hull.
    for side, sign in (("L", -1), ("R", 1)):
        beam(f"Thoracic_Rail_{side}", (sign * 0.47, -0.10, 2.04), (sign * 0.35, -0.08, 1.23), 0.075, frame, iron, "PRIMARY", True)
        beam(f"Dorsal_Rail_{side}", (sign * 0.43, 0.21, 2.08), (sign * 0.32, 0.22, 1.20), 0.085, frame, iron, "PRIMARY")
        beam(f"Thoracic_Brace_{side}", (sign * 0.48, -0.10, 1.85), (sign * 0.25, -0.18, 1.45), 0.052, frame, iron, "SECONDARY", True)

    cylinder("Pelvic_Clevis", (0.0, 0.03, 1.13), 0.16, 0.58, frame, iron, (0.0, math.pi / 2, 0.0), 20, "PRIMARY")
    box("Pelvic_Fork_L", (-0.25, 0.03, 1.05), (0.11, 0.22, 0.31), frame, iron, edge=0.025, importance="PRIMARY")
    box("Pelvic_Fork_R", (0.25, 0.03, 1.05), (0.11, 0.22, 0.31), frame, iron, edge=0.025, importance="PRIMARY")

    # Structural powerplant between the dorsal rails.
    prism("Powerplant_Core", (0.0, 0.29, 1.62), 0.69, 0.31, 0.37, 0.22, 0.25, power, dark, 0.035, "PRIMARY")
    for side, sign in (("L", -1), ("R", 1)):
        cylinder(f"Power_Cylinder_{side}_A", (sign * 0.18, 0.33, 1.60), 0.058, 0.52, power, iron)
        cylinder(f"Power_Cylinder_{side}_B", (sign * 0.29, 0.31, 1.58), 0.048, 0.44, power, iron)
        cylinder(f"Pressure_Accumulator_{side}", (sign * 0.25, 0.27, 1.93), 0.07, 0.28, power, dark)
        cylinder(f"Exhaust_Stack_{side}", (sign * 0.30, 0.31, 2.16), 0.04, 0.36, power, dark)
    for index in range(7):
        box(f"Radiator_Fin_{index:02d}", (0.0, 0.435, 1.43 + index * 0.045), (0.30, 0.02, 0.018), power, iron, edge=0.003)

    # Multi-member legs and guarded mechanical joints.
    for side, sign in (("L", -1), ("R", 1)):
        hip = Vector((sign * 0.27, 0.02, 1.08))
        knee = Vector((sign * 0.30, -0.005, 0.65))
        ankle = Vector((sign * 0.31, -0.02, 0.25))
        cylinder(f"Hip_Pivot_{side}", hip, 0.105, 0.20, frame, dark, (math.pi / 2, 0.0, 0.0), 20, "PRIMARY")
        cylinder(f"Knee_Pivot_{side}", knee, 0.11, 0.22, frame, dark, (math.pi / 2, 0.0, 0.0), 20, "PRIMARY")
        cylinder(f"Ankle_Pivot_{side}", ankle, 0.075, 0.18, frame, dark, (math.pi / 2, 0.0, 0.0), 18, "PRIMARY")
        for lane, y in (("FRONT", -0.085), ("REAR", 0.09)):
            beam(f"Femur_{side}_{lane}", (hip.x, y, hip.z - 0.05), (knee.x, y, knee.z + 0.06), 0.07, frame, iron)
            beam(f"Shin_{side}_{lane}", (knee.x, y, knee.z - 0.06), (ankle.x, y, ankle.z + 0.05), 0.065, frame, iron)
        cylinder(f"Femur_Ram_{side}", (sign * 0.22, 0.0, 0.86), 0.042, 0.40, frame, dark, importance="SECONDARY")
        cylinder(f"Shin_Ram_{side}", (sign * 0.23, 0.0, 0.45), 0.038, 0.33, frame, dark, importance="SECONDARY")

        base = box(f"Foot_Base_{side}", (sign * 0.31, -0.02, 0.105), (0.34, 0.40, 0.14), ground, iron, edge=0.025, importance="PRIMARY")
        base["ground_reference"] = True
        box(f"Heel_Block_{side}", (sign * 0.31, 0.17, 0.09), (0.30, 0.16, 0.14), ground, dark, edge=0.02, importance="PRIMARY")
        for toe in range(3):
            box(f"Toe_{side}_{toe}", (sign * (0.22 + toe * 0.09), -0.22, 0.075), (0.075, 0.18, 0.10), ground, dark, edge=0.018, importance="PRIMARY")
        box(f"Folded_Outrigger_{side}", (sign * 0.49, 0.06, 0.08), (0.20, 0.12, 0.09), ground, dark, edge=0.018, importance="SECONDARY")

    # Rescue arms with paired rails and precision manipulators.
    for side, sign in (("L", -1), ("R", 1)):
        shoulder = Vector((sign * 0.64, 0.0, 1.88))
        elbow = Vector((sign * 0.70, 0.0, 1.35))
        wrist = Vector((sign * 0.72, -0.02, 0.93))
        cylinder(f"Shoulder_Pivot_{side}", shoulder, 0.13, 0.22, frame, dark, (math.pi / 2, 0.0, 0.0), 20, "PRIMARY")
        cylinder(f"Elbow_Pivot_{side}", elbow, 0.10, 0.20, frame, dark, (math.pi / 2, 0.0, 0.0), 20, "PRIMARY")
        for lane, y in (("FRONT", -0.075), ("REAR", 0.08)):
            beam(f"UpperArm_{side}_{lane}", (shoulder.x, y, shoulder.z - 0.04), (elbow.x, y, elbow.z + 0.04), 0.065, frame, iron)
            beam(f"Forearm_{side}_{lane}", (elbow.x, y, elbow.z - 0.04), (wrist.x, y, wrist.z + 0.04), 0.055, frame, iron)
        palm = box(f"Manipulator_Palm_{side}", (wrist.x, -0.02, 0.82), (0.16, 0.16, 0.19), hands, dark, edge=0.035, importance="PRIMARY")
        for digit in range(3):
            finger_x = wrist.x + sign * (digit - 1) * 0.045
            cylinder(f"Manipulator_Digit_{side}_{digit}", (finger_x, -0.045, 0.68), 0.018, 0.22, hands, iron, vertices=12, importance="SECONDARY")
            cylinder(f"Manipulator_Tip_{side}_{digit}", (finger_x, -0.07, 0.57), 0.021, 0.08, hands, dark, vertices=12, importance="SECONDARY")

    # Ancestral plate and replaceable industrial interface.
    plate_obj = prism("Gren_Skildus", (-0.76, -0.015, 1.75), 0.50, 0.25, 0.31, 0.13, 0.16, frame, plate, 0.035, "PRIMARY")
    plate_obj.rotation_euler = (0.0, -0.10, -0.03)
    beam("Gren_Mount_Upper", (-0.65, 0.03, 1.92), (-0.73, 0.01, 1.90), 0.055, frame, iron)
    beam("Gren_Mount_Lower", (-0.66, 0.03, 1.57), (-0.73, 0.01, 1.59), 0.055, frame, iron)
    cylinder("Tool_Interface_R", (0.77, 0.0, 1.75), 0.15, 0.20, frame, dark, (math.pi / 2, 0.0, 0.0), 20, "PRIMARY")
    cylinder("Tool_Interface_R_Collar", (0.82, -0.01, 1.55), 0.08, 0.26, frame, iron, (0.0, 0.0, 0.0), 18, "SECONDARY")

    # Restrained tertiary service markers; never silhouette-bearing.
    for index, (x, z) in enumerate(((-0.13, 1.42), (0.13, 1.42), (-0.15, 1.58), (0.15, 1.58), (-0.14, 1.74), (0.14, 1.74))):
        cylinder(f"Service_Port_{index:02d}", (x, -0.205, z), 0.018, 0.025, tertiary, iron, (math.pi / 2, 0.0, 0.0), 12, "TERTIARY", True)
    for index in range(8):
        z = 1.54 + index * 0.045
        cylinder(f"Gren_Rivet_{index:02d}", (-0.89 if index % 2 == 0 else -0.65, -0.09, z), 0.014, 0.025, tertiary, iron, (math.pi / 2, 0.0, 0.0), 10, "TERTIARY")

    production = [obj for obj in bpy.context.scene.objects if obj.type == "MESH" and obj.get("production_geometry")]
    scale_factor = normalize_height(production, contract["dimensions_m"]["overall_height_target"])
    for obj in production:
        obj["normalization_factor"] = scale_factor

    floor = box("QA_Floor", (0.0, 0.0, -0.035), (4.0, 4.0, 0.07), ref, dark, edge=0, importance="REFERENCE")
    floor["production_geometry"] = False
    floor["source_kind"] = "PROCEDURAL_QA"

    camera_specs = {
        "Cam_Front": ((0.0, -6.0, 1.25), (0.0, 0.0, 1.24), "ORTHO"),
        "Cam_Rear": ((0.0, 6.0, 1.25), (0.0, 0.0, 1.24), "ORTHO"),
        "Cam_CharacterLeft": ((-5.5, 0.0, 1.25), (0.0, 0.0, 1.24), "ORTHO"),
        "Cam_CharacterRight": ((5.5, 0.0, 1.25), (0.0, 0.0, 1.24), "ORTHO"),
        "Cam_ThreeQuarter": ((4.4, -5.0, 1.45), (0.0, 0.0, 1.22), "PERSP"),
        "Cam_Cutaway": ((3.8, -5.2, 1.36), (0.0, 0.0, 1.30), "PERSP"),
    }
    for name, (location, target, kind) in camera_specs.items():
        data = bpy.data.cameras.new(name)
        data.type = kind
        data.ortho_scale = 2.85
        data.lens = 70
        cam = bpy.data.objects.new(name, data)
        cam.location = location
        look_at(cam, target)
        cameras.objects.link(cam)

    world = bpy.data.worlds.new("QA_Workbench_World")
    world.color = (0.025, 0.03, 0.035)
    scene.world = world
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "MATCAP"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "BOTH"
    scene.render.resolution_x = contract["render"]["resolution_x"]
    scene.render.resolution_y = contract["render"]["resolution_y"]
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    return cols


def measure(contract):
    scene = bpy.context.scene
    production = [obj for obj in scene.objects if obj.type == "MESH" and obj.get("production_geometry")]
    low, high = union_bounds(production)
    height = high.z - low.z
    tertiary = [obj for obj in production if obj.get("form_importance") == "TERTIARY"]
    external = [obj.name for obj in production if obj.get("source_kind") != "PROCEDURAL_ORIGINAL"]
    invalid_scales = {obj.name: list(obj.scale) for obj in production if any(abs(value - 1.0) > 1e-6 for value in obj.scale)}
    required_missing = [name for name in contract["required_primary_objects"] if name not in scene.objects]
    required_collections_missing = [name for name in contract["required_collections"] if name not in bpy.data.collections]
    dims = contract["dimensions_m"]
    gates = {
        "overall_height": {"pass": abs(height - dims["overall_height_target"]) <= dims["overall_height_tolerance"], "measured_m": height, "target_m": dims["overall_height_target"], "tolerance_m": dims["overall_height_tolerance"]},
        "ground_contact": {"pass": abs(low.z - dims["ground_z_target"]) <= dims["ground_z_tolerance"], "measured_m": low.z, "target_m": dims["ground_z_target"], "tolerance_m": dims["ground_z_tolerance"]},
        "required_objects": {"pass": not required_missing, "missing": required_missing},
        "required_collections": {"pass": not required_collections_missing, "missing": required_collections_missing},
        "rigid_scales_applied": {"pass": not invalid_scales, "invalid": invalid_scales},
        "external_assets": {"pass": len(external) == contract["external_asset_count"], "objects": external, "expected_count": contract["external_asset_count"]},
        "tertiary_ceiling": {"pass": len(tertiary) <= contract["tertiary_object_max"], "count": len(tertiary), "maximum": contract["tertiary_object_max"]},
        "render_engine": {"pass": scene.render.engine == contract["render"]["engine"], "observed": scene.render.engine, "expected": contract["render"]["engine"]},
    }
    operator_low, operator_high = bounds(scene.objects["Operator_Cell"])
    pelvis_low, pelvis_high = bounds(scene.objects["Pelvic_Clevis"])
    yoke_low = min(bounds(scene.objects[name])[0].z for name in ("Yoke_Arch_Front", "Yoke_Arch_Rear"))
    gren_low, gren_high = bounds(scene.objects["Gren_Skildus"])
    pilot_objects = list(bpy.data.collections["01_PILOT_ENVELOPE"].objects)
    pilot_low, pilot_high = union_bounds(pilot_objects)
    left_foot = scene.objects["Foot_Base_L"].matrix_world.translation
    right_foot = scene.objects["Foot_Base_R"].matrix_world.translation
    provisional = {
        "measurement_class": "PROVISIONAL_MEASURED_FOR_VISUAL_COMPARISON",
        "total_silhouette_width_m": high.x - low.x,
        "operator_cell_width_m": operator_high.x - operator_low.x,
        "pelvis_width_m": pelvis_high.x - pelvis_low.x,
        "stance_reference_width_m": abs(right_foot.x - left_foot.x),
        "head_to_yoke_clearance_m": yoke_low - operator_high.z,
        "gren_skildus_front_projected_bbox_area_m2": (gren_high.x - gren_low.x) * (gren_high.z - gren_low.z),
        "machine_depth_m": high.y - low.y,
        "pilot_envelope_dimensions_m": list(pilot_high - pilot_low),
        "methods": {
            "silhouette_width": "world-space production-geometry union AABB X span",
            "gren_area": "front-view world XZ bounding-box proxy; not pixel segmentation",
            "machine_depth": "world-space production-geometry union AABB Y span"
        },
    }
    return gates, provisional, {obj.name: obj.get("form_importance") for obj in production}


def render_views(contract, candidate_sha):
    scene = bpy.context.scene
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    result = {}
    cutaway_objects = [obj for obj in scene.objects if obj.get("review_hide_cutaway")]
    for filename, camera_name in contract["render"]["views"]:
        cutaway = filename == "human-cutaway-clay.png"
        for obj in cutaway_objects:
            obj.hide_render = cutaway
        scene.camera = scene.objects[camera_name]
        path = EVIDENCE_DIR / filename
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        result[filename] = {"camera": camera_name, "cutaway_review_only": cutaway, "sha256": digest(path), "candidate_sha256": candidate_sha}
    for obj in cutaway_objects:
        obj.hide_render = False
    return result


def main():
    args = args_from_cli()
    output = args.output.resolve()
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    if output.exists():
        fail("PRE_BUILD", "V2A output already exists", {"path": str(output)})
    concept = ROOT / contract["approved_concept"]["path"]
    if digest(concept) != contract["approved_concept"]["sha256"]:
        fail("PRE_BUILD", "approved concept hash mismatch")
    negative = ROOT / contract["negative_fixture"]["path"]
    if digest(negative) != contract["negative_fixture"]["sha256"]:
        fail("PRE_BUILD", "V1 negative fixture hash mismatch")
    if args.source_repo_state != "CLEAN":
        fail("PRE_BUILD", "host repository state is not clean")
    if bpy.data.filepath:
        fail("PRE_BUILD", "builder must start from factory startup")

    build(contract)
    gates, proportions, inventory = measure(contract)
    failed = [name for name, result in gates.items() if not result["pass"]]
    if failed:
        fail("MACHINE_GATE", "V2A internal gate failure", {"failed": failed, "gates": gates})

    scene = bpy.context.scene
    scene["plan_id"] = contract["plan_id"]
    scene["approved_concept_sha256"] = contract["approved_concept"]["sha256"]
    scene["human_approval"] = "REQUIRED"
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output), check_existing=False)
    candidate_sha = digest(output)
    record = {
        "schema_version": "1.0",
        "claim_class": "OBSERVED",
        "gate": "VAREK_CHASSIS_V2A_MACHINE",
        "overall": "PASS",
        "human_approval": "REQUIRED",
        "plan_id": contract["plan_id"],
        "plan_git_commit": args.plan_git_commit,
        "plan_file_sha256": digest(PLAN),
        "contract_file_sha256": digest(CONTRACT_PATH),
        "builder_script_sha256": digest(Path(__file__).resolve()),
        "validator_script_sha256": digest(VALIDATOR),
        "source_git_commit": args.source_git_commit,
        "source_repository_state": args.source_repo_state,
        "approved_concept_sha256": contract["approved_concept"]["sha256"],
        "negative_fixture_sha256": contract["negative_fixture"]["sha256"],
        "candidate": {"path": str(output), "sha256": candidate_sha},
        "environment": {"platform": platform.platform(), "blender_executable": str(Path(bpy.app.binary_path).resolve()), "blender_version": bpy.app.version_string, "embedded_python": sys.version, "build_timestamp_utc": datetime.now(timezone.utc).isoformat()},
        "gates": gates,
        "provisional_proportion_readback": proportions,
        "component_inventory": inventory,
    }
    measurement_path = EVIDENCE_DIR / "measurements.json"
    measurement_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    record["review_renders"] = render_views(contract, candidate_sha)
    post_render_sha = digest(output)
    if post_render_sha != candidate_sha:
        fail("POST_RENDER", "frozen candidate changed during review", {"before": candidate_sha, "after": post_render_sha})
    record["candidate"]["post_render_sha256"] = post_render_sha
    measurement_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    if FAILURE_PATH.exists():
        FAILURE_PATH.unlink()
    print(f"VAREK_CHASSIS_V2A_PASS={candidate_sha}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        print(f"VAREK_CHASSIS_V2A_FAIL={exc}", file=sys.stderr)
        raise SystemExit(1)
    except Exception as exc:
        if not FAILURE_PATH.exists():
            EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
            FAILURE_PATH.write_text(json.dumps({"schema_version": "1.0", "claim_class": "OBSERVED", "gate": "VAREK_CHASSIS_V2A", "overall": "FAIL", "phase": "UNEXPECTED_EXCEPTION", "message": f"{type(exc).__name__}: {exc}", "timestamp_utc": datetime.now(timezone.utc).isoformat()}, indent=2) + "\n", encoding="utf-8")
        print(f"VAREK_CHASSIS_V2A_ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
