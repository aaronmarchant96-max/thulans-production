#!/usr/bin/env python3
"""Build the static Varek V2A.1 primary-massing salvage candidate."""

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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_varek_chassis_v2a as base


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "VAREK_CHASSIS_V2A1_REVISION_PLAN.md"
CONTRACT_PATH = ROOT / "spec" / "varek_chassis_v2a1_contract.json"
VALIDATOR = ROOT / "tools" / "validate_varek_chassis_v2a1.py"
DEFAULT_OUTPUT = ROOT / "blender" / "candidates" / "varek-chassis-v2a1-dense-static.blend"
EVIDENCE_DIR = ROOT / "evidence" / "varek-chassis-v2a1"
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
                "gate": "VAREK_CHASSIS_V2A1",
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


def arguments():
    values = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--source-git-commit", required=True)
    parser.add_argument("--source-repo-state", choices=("CLEAN",), required=True)
    parser.add_argument("--plan-git-commit", required=True)
    return parser.parse_args(values)


def structural_beam(name, start, end, thickness, collection, mat, importance="PRIMARY", cutaway=False):
    obj = base.beam(name, start, end, thickness, collection, mat, importance, cutaway)
    obj["structural_start"] = list(start)
    obj["structural_end"] = list(end)
    return obj


def build_pilot(human, pilot):
    base.sphere("Pilot_Head", (0.0, -0.015, 1.80), (0.105, 0.09, 0.125), human, pilot)
    base.prism("Pilot_Torso", (0.0, 0.0, 1.45), 0.54, 0.27, 0.34, 0.18, 0.22, human, pilot, 0.035, "SECONDARY")
    base.prism("Pilot_Pelvis", (0.0, 0.0, 1.13), 0.19, 0.24, 0.29, 0.17, 0.19, human, pilot, 0.03, "SECONDARY")
    for side, sign in (("L", -1), ("R", 1)):
        structural_beam(f"Pilot_UpperArm_{side}", (sign * 0.17, 0.0, 1.62), (sign * 0.23, 0.0, 1.29), 0.052, human, pilot, "SECONDARY")
        structural_beam(f"Pilot_Forearm_{side}", (sign * 0.23, 0.0, 1.29), (sign * 0.25, -0.01, 0.98), 0.047, human, pilot, "SECONDARY")
        structural_beam(f"Pilot_Thigh_{side}", (sign * 0.10, 0.0, 1.05), (sign * 0.13, 0.0, 0.67), 0.07, human, pilot, "SECONDARY")
        structural_beam(f"Pilot_Shin_{side}", (sign * 0.13, 0.0, 0.67), (sign * 0.16, -0.01, 0.29), 0.06, human, pilot, "SECONDARY")
        base.box(f"Pilot_Foot_{side}", (sign * 0.16, -0.07, 0.19), (0.12, 0.24, 0.085), human, pilot, edge=0.02)


def build_hull(hull, frame, dark, iron):
    base.sphere("Operator_Cell", (0.0, 0.015, 1.82), (0.18, 0.15, 0.205), hull, dark, "PRIMARY", True)
    base.box("Operator_Brow", (0.0, -0.155, 1.90), (0.38, 0.12, 0.12), hull, iron, edge=0.025, importance="PRIMARY", cutaway=True)
    base.box("Operator_Visor_Guard", (0.0, -0.222, 1.82), (0.22, 0.025, 0.045), hull, iron, edge=0.006, importance="PRIMARY", cutaway=True)

    # Three interlocked protective masses replace the rejected flat box torso.
    base.prism("Thoracic_Center", (0.0, -0.02, 1.51), 0.55, 0.31, 0.39, 0.22, 0.29, hull, dark, 0.04, "PRIMARY", True)
    left = base.prism("Thoracic_Wing_L", (-0.29, 0.0, 1.53), 0.55, 0.18, 0.25, 0.24, 0.32, hull, dark, 0.035, "PRIMARY", True)
    right = base.prism("Thoracic_Wing_R", (0.29, 0.0, 1.53), 0.55, 0.18, 0.25, 0.24, 0.32, hull, dark, 0.035, "PRIMARY", True)
    left.rotation_euler.y = -0.10
    right.rotation_euler.y = 0.10
    base.prism("Abdominal_Cage", (0.0, 0.015, 1.22), 0.25, 0.35, 0.43, 0.25, 0.30, hull, dark, 0.03, "PRIMARY", True)

    # Deep front/rear faceted yoke: visibly load-bearing, not a round hoop.
    yoke = {
        "L": [(-0.48, 1.82), (-0.60, 2.10), (-0.47, 2.31), (-0.27, 2.40)],
        "R": [(0.48, 1.82), (0.60, 2.10), (0.47, 2.31), (0.27, 2.40)],
    }
    for side, points in yoke.items():
        for depth_name, y in (("Front", -0.14), ("Rear", 0.20)):
            for index, (a, b) in enumerate(zip(points, points[1:])):
                name = f"Yoke_Riser_{side}_{depth_name}" if index == 0 else f"Yoke_{side}_{depth_name}_{index}"
                structural_beam(name, (a[0], y, a[1]), (b[0], y, b[1]), 0.11, frame, iron)
        for index, (x, z) in enumerate(points[1:]):
            structural_beam(f"Yoke_Depth_{side}_{index}", (x, -0.14, z), (x, 0.20, z), 0.09, frame, iron)
    structural_beam("Yoke_Crown_Front", (-0.27, -0.14, 2.40), (0.27, -0.14, 2.40), 0.11, frame, iron)
    structural_beam("Yoke_Crown_Rear", (-0.27, 0.20, 2.40), (0.27, 0.20, 2.40), 0.11, frame, iron)
    for x in (-0.27, 0.0, 0.27):
        structural_beam(f"Yoke_Crown_Depth_{x:+.2f}", (x, -0.14, 2.40), (x, 0.20, 2.40), 0.09, frame, iron)

    # Primary gusset masses make the yoke/rail junction explicit.
    for side, sign in (("L", -1), ("R", 1)):
        base.prism(f"Yoke_Gusset_{side}", (sign * 0.48, 0.10, 1.90), 0.28, 0.18, 0.26, 0.22, 0.30, frame, iron, 0.025, "PRIMARY")


def build_load_frame(frame, power, dark, iron):
    for side, sign in (("L", -1), ("R", 1)):
        structural_beam(f"Thoracic_Rail_{side}", (sign * 0.48, -0.10, 1.88), (sign * 0.35, -0.07, 1.16), 0.095, frame, iron, cutaway=True)
        structural_beam(f"Dorsal_Rail_{side}", (sign * 0.48, 0.20, 1.88), (sign * 0.34, 0.19, 1.15), 0.105, frame, iron)
        structural_beam(f"Pelvic_Strut_{side}", (sign * 0.34, 0.19, 1.15), (sign * 0.25, 0.05, 1.05), 0.11, frame, iron)
        structural_beam(f"Hull_CrossBrace_{side}", (sign * 0.46, -0.07, 1.67), (sign * 0.18, -0.18, 1.42), 0.07, frame, iron, cutaway=True)

    base.cylinder("Pelvic_Clevis", (0.0, 0.04, 1.08), 0.17, 0.62, frame, iron, (0.0, math.pi / 2, 0.0), 20, "PRIMARY")
    for side, sign in (("L", -1), ("R", 1)):
        base.prism(f"Pelvic_Fork_{side}", (sign * 0.27, 0.04, 1.00), 0.34, 0.13, 0.17, 0.23, 0.27, frame, iron, 0.025, "PRIMARY")

    base.prism("Powerplant_Core", (0.0, 0.31, 1.55), 0.72, 0.34, 0.40, 0.24, 0.29, power, dark, 0.035, "PRIMARY")
    for side, sign in (("L", -1), ("R", 1)):
        base.cylinder(f"Power_Cylinder_{side}", (sign * 0.19, 0.36, 1.52), 0.07, 0.54, power, iron, importance="SECONDARY")
        base.cylinder(f"Pressure_Accumulator_{side}", (sign * 0.29, 0.31, 1.83), 0.075, 0.31, power, dark, importance="SECONDARY")
        base.cylinder(f"Exhaust_Stack_{side}", (sign * 0.31, 0.34, 2.08), 0.045, 0.38, power, dark, importance="SECONDARY")


def build_legs(frame, ground, dark, iron):
    for side, sign in (("L", -1), ("R", 1)):
        hip = Vector((sign * 0.28, 0.03, 1.02))
        knee = Vector((sign * 0.33, 0.00, 0.61))
        ankle = Vector((sign * 0.35, -0.01, 0.24))
        base.cylinder(f"Hip_Pivot_{side}", hip, 0.12, 0.24, frame, dark, (math.pi / 2, 0.0, 0.0), 20, "PRIMARY")
        base.cylinder(f"Knee_Pivot_{side}", knee, 0.125, 0.25, frame, dark, (math.pi / 2, 0.0, 0.0), 20, "PRIMARY")
        base.cylinder(f"Ankle_Pivot_{side}", ankle, 0.09, 0.22, frame, dark, (math.pi / 2, 0.0, 0.0), 18, "PRIMARY")
        for lane, xoff, y in (("OUTER", sign * 0.07, -0.09), ("INNER", -sign * 0.055, -0.07), ("DORSAL", 0.0, 0.10)):
            structural_beam(f"Femur_{side}_{lane}", (hip.x + xoff, y, hip.z - 0.03), (knee.x + xoff * 0.65, y, knee.z + 0.05), 0.075, frame, iron)
            structural_beam(f"Shin_{side}_{lane}", (knee.x + xoff * 0.65, y, knee.z - 0.05), (ankle.x + xoff * 0.35, y, ankle.z + 0.05), 0.07, frame, iron)
        for ram_index, (xoff, y) in enumerate(((sign * -0.07, 0.02), (sign * 0.075, 0.04))):
            structural_beam(f"Femur_Ram_{side}_{ram_index}", (hip.x + xoff, y, 0.96), (knee.x + xoff, y, 0.67), 0.05, frame, dark, "SECONDARY")
            structural_beam(f"Shin_Ram_{side}_{ram_index}", (knee.x + xoff, y, 0.55), (ankle.x + xoff, y, 0.30), 0.047, frame, dark, "SECONDARY")
        base.prism(f"Knee_Guard_{side}", (knee.x, -0.13, knee.z), 0.25, 0.22, 0.27, 0.12, 0.15, frame, dark, 0.025, "PRIMARY")

        foot = base.box(f"Foot_Base_{side}", (sign * 0.35, -0.01, 0.095), (0.43, 0.51, 0.14), ground, iron, edge=0.025, importance="PRIMARY")
        foot["ground_reference"] = True
        base.box(f"Heel_Drive_{side}", (sign * 0.35, 0.23, 0.12), (0.35, 0.22, 0.20), ground, dark, edge=0.025, importance="PRIMARY")
        for toe, offset in enumerate((-0.11, 0.11)):
            base.box(f"Toe_Pad_{side}_{toe}", (sign * 0.35 + offset, -0.27, 0.08), (0.17, 0.23, 0.11), ground, dark, edge=0.022, importance="PRIMARY")
        base.box(f"Folded_Outrigger_Outer_{side}", (sign * 0.59, 0.04, 0.085), (0.22, 0.16, 0.10), ground, dark, edge=0.018, importance="PRIMARY")
        base.box(f"Folded_Outrigger_Rear_{side}", (sign * 0.35, 0.37, 0.085), (0.20, 0.20, 0.10), ground, dark, edge=0.018, importance="PRIMARY")


def build_arms(frame, hands, dark, iron):
    for side, sign in (("L", -1), ("R", 1)):
        shoulder = Vector((sign * 0.62, 0.00, 1.78))
        elbow = Vector((sign * 0.70, -0.01, 1.29))
        wrist = Vector((sign * 0.72, -0.03, 0.91))
        base.cylinder(f"Shoulder_Pivot_{side}", shoulder, 0.145, 0.25, frame, dark, (math.pi / 2, 0.0, 0.0), 20, "PRIMARY")
        base.cylinder(f"Elbow_Pivot_{side}", elbow, 0.115, 0.23, frame, dark, (math.pi / 2, 0.0, 0.0), 20, "PRIMARY")
        for lane, xoff, y in (("OUTER", sign * 0.055, -0.08), ("INNER", sign * -0.05, 0.075)):
            structural_beam(f"UpperArm_{side}_{lane}", (shoulder.x + xoff, y, shoulder.z - 0.04), (elbow.x + xoff, y, elbow.z + 0.04), 0.075, frame, iron)
            structural_beam(f"Forearm_{side}_{lane}", (elbow.x + xoff, y, elbow.z - 0.04), (wrist.x + xoff, y, wrist.z + 0.04), 0.068, frame, iron)
        structural_beam(f"Arm_Ram_{side}", (shoulder.x - sign * 0.08, 0.02, 1.69), (elbow.x - sign * 0.08, 0.02, 1.37), 0.052, frame, dark, "SECONDARY")
        base.cylinder(f"Wrist_Bearing_{side}", wrist, 0.095, 0.19, hands, iron, (math.pi / 2, 0.0, 0.0), 18, "PRIMARY")
        base.prism(f"Manipulator_Palm_{side}", (wrist.x, -0.02, 0.79), 0.22, 0.18, 0.21, 0.17, 0.19, hands, dark, 0.025, "PRIMARY")
        for digit, offset in enumerate((-0.075, -0.025, 0.025, 0.075)):
            x = wrist.x + offset
            structural_beam(f"Manipulator_Digit_{side}_{digit}", (x, -0.045, 0.70), (x + sign * 0.012, -0.07, 0.56), 0.032, hands, iron, "SECONDARY")
            base.cylinder(f"Manipulator_Tip_{side}_{digit}", (x + sign * 0.012, -0.075, 0.535), 0.022, 0.07, hands, dark, vertices=12, importance="SECONDARY")


def build_identity(frame, dark, iron, plate):
    gren = base.prism("Gren_Skildus", (-0.77, -0.015, 1.69), 0.54, 0.27, 0.34, 0.15, 0.18, frame, plate, 0.04, "PRIMARY")
    gren.rotation_euler = (0.0, -0.10, -0.025)
    structural_beam("Gren_Mount_Upper", (-0.61, 0.04, 1.87), (-0.71, 0.00, 1.85), 0.065, frame, iron)
    structural_beam("Gren_Mount_Lower", (-0.61, 0.04, 1.52), (-0.71, 0.00, 1.55), 0.065, frame, iron)
    base.cylinder("Tool_Interface_R", (0.78, 0.0, 1.68), 0.17, 0.24, frame, dark, (math.pi / 2, 0.0, 0.0), 20, "PRIMARY")


def setup_scene(contract):
    base.clear_scene()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.render.fps = 24
    scene.frame_start = scene.frame_end = 1
    cols = base.collections(contract["required_collections"])
    iron = base.material("QA_Primary_Iron_Clay", (0.35, 0.37, 0.38))
    dark = base.material("QA_Protected_Hull_Clay", (0.18, 0.20, 0.21))
    pilot = base.material("QA_Pilot_Envelope", (0.48, 0.25, 0.20))
    plate = base.material("QA_Gren_Skildus_Clay", (0.29, 0.32, 0.30))
    ref, human, hull, frame, power, ground, hands, _, cameras = (cols[name] for name in contract["required_collections"])

    build_pilot(human, pilot)
    build_hull(hull, frame, dark, iron)
    build_load_frame(frame, power, dark, iron)
    build_legs(frame, ground, dark, iron)
    build_arms(frame, hands, dark, iron)
    build_identity(frame, dark, iron, plate)

    production = [obj for obj in scene.objects if obj.type == "MESH" and obj.get("production_geometry")]
    factor = base.normalize_height(production, contract["dimensions_m"]["overall_height_target"])
    for obj in production:
        obj["normalization_factor"] = factor
    floor = base.box("QA_Floor", (0.0, 0.0, -0.035), (4.0, 4.0, 0.07), ref, dark, edge=0, importance="REFERENCE")
    floor["production_geometry"] = False
    floor["source_kind"] = "PROCEDURAL_QA"

    camera_specs = {
        "Cam_Front": ((0.0, -6.0, 1.25), (0.0, 0.0, 1.22), "ORTHO"),
        "Cam_Rear": ((0.0, 6.0, 1.25), (0.0, 0.0, 1.22), "ORTHO"),
        "Cam_CharacterLeft": ((-5.5, 0.0, 1.25), (0.0, 0.0, 1.22), "ORTHO"),
        "Cam_CharacterRight": ((5.5, 0.0, 1.25), (0.0, 0.0, 1.22), "ORTHO"),
        "Cam_ThreeQuarter": ((4.4, -5.0, 1.45), (0.0, 0.0, 1.20), "PERSP"),
        "Cam_Cutaway": ((3.8, -5.2, 1.36), (0.0, 0.0, 1.28), "PERSP"),
    }
    for name, (location, target, kind) in camera_specs.items():
        data = bpy.data.cameras.new(name)
        data.type = kind
        data.ortho_scale = 2.85
        data.lens = 70
        camera = bpy.data.objects.new(name, data)
        camera.location = location
        base.look_at(camera, target)
        cameras.objects.link(camera)

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


def aabb_gap(first, second):
    a0, a1 = base.bounds(first)
    b0, b1 = base.bounds(second)
    delta = Vector((max(a0.x - b1.x, b0.x - a1.x, 0.0), max(a0.y - b1.y, b0.y - a1.y, 0.0), max(a0.z - b1.z, b0.z - a1.z, 0.0)))
    return delta.length


def measure(contract):
    scene = bpy.context.scene
    production = [obj for obj in scene.objects if obj.type == "MESH" and obj.get("production_geometry")]
    low, high = base.union_bounds(production)
    dims = contract["dimensions_m"]
    tertiary = [obj for obj in production if obj.get("form_importance") == "TERTIARY"]
    external = [obj.name for obj in production if obj.get("source_kind") != "PROCEDURAL_ORIGINAL"]
    invalid_scales = {obj.name: list(obj.scale) for obj in production if any(abs(value - 1.0) > 1e-6 for value in obj.scale)}
    missing_objects = [name for name in contract["required_primary_objects"] if name not in scene.objects]
    missing_collections = [name for name in contract["required_collections"] if name not in bpy.data.collections]
    junctions = []
    for first_name, second_name in contract["structural_junctions"]:
        gap = aabb_gap(scene.objects[first_name], scene.objects[second_name])
        junctions.append({"objects": [first_name, second_name], "aabb_gap_m": gap, "pass": gap <= contract["structural_junction_max_gap_m"]})
    gates = {
        "overall_height": {"pass": abs((high.z - low.z) - dims["overall_height_target"]) <= dims["overall_height_tolerance"], "measured_m": high.z - low.z, "target_m": dims["overall_height_target"], "tolerance_m": dims["overall_height_tolerance"]},
        "ground_contact": {"pass": abs(low.z - dims["ground_z_target"]) <= dims["ground_z_tolerance"], "measured_m": low.z, "target_m": dims["ground_z_target"], "tolerance_m": dims["ground_z_tolerance"]},
        "required_objects": {"pass": not missing_objects, "missing": missing_objects},
        "required_collections": {"pass": not missing_collections, "missing": missing_collections},
        "rigid_scales_applied": {"pass": not invalid_scales, "invalid": invalid_scales},
        "external_assets": {"pass": len(external) == contract["external_asset_count"], "objects": external, "expected_count": contract["external_asset_count"]},
        "tertiary_ceiling": {"pass": len(tertiary) <= contract["tertiary_object_max"], "count": len(tertiary), "maximum": contract["tertiary_object_max"]},
        "structural_junctions": {"pass": all(item["pass"] for item in junctions), "measurements": junctions, "maximum_gap_m": contract["structural_junction_max_gap_m"]},
        "render_engine": {"pass": scene.render.engine == contract["render"]["engine"], "observed": scene.render.engine, "expected": contract["render"]["engine"]},
    }

    operator_low, operator_high = base.bounds(scene.objects["Operator_Cell"])
    pelvis_low, pelvis_high = base.bounds(scene.objects["Pelvic_Clevis"])
    gren_low, gren_high = base.bounds(scene.objects["Gren_Skildus"])
    pilot_objects = list(bpy.data.collections["01_PILOT_ENVELOPE"].objects)
    pilot_low, pilot_high = base.union_bounds(pilot_objects)
    left_foot = scene.objects["Foot_Base_L"].matrix_world.translation
    right_foot = scene.objects["Foot_Base_R"].matrix_world.translation
    margin = contract["head_clearance"]["operator_lateral_margin_m"]
    lateral_limit = max(abs(operator_low.x), abs(operator_high.x)) + margin
    yoke_objects = [obj for obj in production if obj.name.startswith("Yoke_")]
    overhead_samples = []
    for obj in yoke_objects:
        for vertex in obj.data.vertices:
            point = obj.matrix_world @ vertex.co
            if abs(point.x) <= lateral_limit and point.z > pilot_high.z:
                overhead_samples.append((point.z, obj.name))
    clearance_z, clearance_object = min(overhead_samples) if overhead_samples else (None, None)
    clearance = clearance_z - pilot_high.z if clearance_z is not None else None
    counts = {key: sum(1 for obj in production if obj.get("form_importance") == key) for key in ("PRIMARY", "SECONDARY", "TERTIARY")}
    provisional = {
        "measurement_class": contract["head_clearance"]["measurement_class"],
        "total_silhouette_width_m": high.x - low.x,
        "operator_cell_width_m": operator_high.x - operator_low.x,
        "pelvis_width_m": pelvis_high.x - pelvis_low.x,
        "stance_reference_width_m": abs(right_foot.x - left_foot.x),
        "head_to_yoke_local_overhead_clearance_m": clearance,
        "gren_skildus_front_projected_bbox_area_m2": (gren_high.x - gren_low.x) * (gren_high.z - gren_low.z),
        "machine_depth_m": high.y - low.y,
        "pilot_envelope_dimensions_m": list(pilot_high - pilot_low),
        "form_object_counts": counts,
        "methods": {
            "silhouette_width": "world-space production-geometry union AABB X span",
            "head_clearance": "lowest yoke mesh vertex strictly above pilot envelope top within operator-cell world-X half-width plus declared margin",
            "head_clearance_lateral_limit_m": lateral_limit,
            "head_clearance_sample_count": len(overhead_samples),
            "head_clearance_lowest_object": clearance_object,
            "gren_area": "front-view world XZ bounding-box proxy; not pixel segmentation",
            "machine_depth": "world-space production-geometry union AABB Y span",
        },
    }
    inventory = {obj.name: obj.get("form_importance") for obj in production}
    return gates, provisional, inventory


def render_views(contract, candidate_sha):
    scene = bpy.context.scene
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    pilot_objects = list(bpy.data.collections["01_PILOT_ENVELOPE"].objects)
    cutaway_objects = [obj for obj in scene.objects if obj.get("review_hide_cutaway")]
    result = {}
    for filename, camera_name in contract["render"]["views"]:
        is_cutaway = filename == "human-cutaway-clay.png"
        for obj in pilot_objects:
            obj.hide_render = not is_cutaway
        for obj in cutaway_objects:
            obj.hide_render = is_cutaway
        scene.camera = scene.objects[camera_name]
        path = EVIDENCE_DIR / filename
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        result[filename] = {"camera": camera_name, "cutaway_review_only": is_cutaway, "sha256": digest(path), "candidate_sha256": candidate_sha}
    for obj in pilot_objects + cutaway_objects:
        obj.hide_render = False
    return result


def main():
    args = arguments()
    output = args.output.resolve()
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    if output.exists():
        fail("PRE_BUILD", "V2A.1 output already exists", {"path": str(output)})
    for item_name in ("approved_concept", "negative_fixture"):
        item = contract[item_name]
        if digest(ROOT / item["path"]) != item["sha256"]:
            fail("PRE_BUILD", f"{item_name} hash mismatch")
    if digest(ROOT / contract["negative_fixture"]["visual_verdict_path"]) != contract["negative_fixture"]["visual_verdict_sha256"]:
        fail("PRE_BUILD", "V2A visual verdict hash mismatch")
    if digest(ROOT / contract["procedural_helper"]["path"]) != contract["procedural_helper"]["sha256"]:
        fail("PRE_BUILD", "procedural helper hash mismatch")
    if args.source_repo_state != "CLEAN":
        fail("PRE_BUILD", "host repository state is not clean")
    if bpy.data.filepath:
        fail("PRE_BUILD", "builder must start from factory startup")

    setup_scene(contract)
    gates, proportions, inventory = measure(contract)
    failed = [name for name, result in gates.items() if not result["pass"]]
    if failed:
        fail("MACHINE_GATE", "V2A.1 internal gate failure", {"failed": failed, "gates": gates})

    scene = bpy.context.scene
    scene["plan_id"] = contract["plan_id"]
    scene["approved_concept_sha256"] = contract["approved_concept"]["sha256"]
    scene["negative_fixture_sha256"] = contract["negative_fixture"]["sha256"]
    scene["human_approval"] = "REQUIRED"
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output), check_existing=False)
    candidate_sha = digest(output)
    record = {
        "schema_version": "1.0",
        "claim_class": "OBSERVED",
        "gate": "VAREK_CHASSIS_V2A1_MACHINE",
        "overall": "PASS",
        "human_approval": "REQUIRED",
        "plan_id": contract["plan_id"],
        "plan_git_commit": args.plan_git_commit,
        "plan_file_sha256": digest(PLAN),
        "contract_file_sha256": digest(CONTRACT_PATH),
        "builder_script_sha256": digest(Path(__file__).resolve()),
        "validator_script_sha256": digest(VALIDATOR),
        "procedural_helper_sha256": digest(ROOT / contract["procedural_helper"]["path"]),
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
    print(f"VAREK_CHASSIS_V2A1_PASS={candidate_sha}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        print(f"VAREK_CHASSIS_V2A1_FAIL={exc}", file=sys.stderr)
        raise SystemExit(1)
    except Exception as exc:
        if not FAILURE_PATH.exists():
            EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
            FAILURE_PATH.write_text(json.dumps({"schema_version": "1.0", "claim_class": "OBSERVED", "gate": "VAREK_CHASSIS_V2A1", "overall": "FAIL", "phase": "UNEXPECTED_EXCEPTION", "message": f"{type(exc).__name__}: {exc}", "timestamp_utc": datetime.now(timezone.utc).isoformat()}, indent=2) + "\n", encoding="utf-8")
        print(f"VAREK_CHASSIS_V2A1_ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
