#!/usr/bin/env python3
"""Independent read-only validation for the frozen Varek Chassis V2A blend."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "spec" / "varek_chassis_v2a_contract.json"
PLAN_PATH = ROOT / "docs" / "VAREK_CHASSIS_V2_BUILD_PLAN.md"
BUILDER_PATH = ROOT / "tools" / "build_varek_chassis_v2a.py"
DEFAULT_MEASUREMENTS = ROOT / "evidence" / "varek-chassis-v2a" / "measurements.json"
DEFAULT_OUTPUT = ROOT / "evidence" / "varek-chassis-v2a" / "validation.json"


def digest(path: Path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def arguments():
    values = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--measurements", type=Path, default=DEFAULT_MEASUREMENTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args(values)


def bounds(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points))), Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))


def union_bounds(objects):
    pairs = [bounds(obj) for obj in objects]
    return Vector((min(a.x for a, _ in pairs), min(a.y for a, _ in pairs), min(a.z for a, _ in pairs))), Vector((max(b.x for _, b in pairs), max(b.y for _, b in pairs), max(b.z for _, b in pairs)))


def item(rule, passed, observed, expected):
    return {"rule": rule, "pass": bool(passed), "observed": observed, "expected": expected}


def main():
    args = arguments()
    if not bpy.data.filepath:
        raise RuntimeError("validator requires an opened V2A candidate")
    blend = Path(bpy.data.filepath).resolve()
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    measurements = json.loads(args.measurements.read_text(encoding="utf-8"))
    before_sha = digest(blend)
    scene = bpy.context.scene
    checks = []
    checks.append(item("candidate.sha256", before_sha == measurements["candidate"]["sha256"], before_sha, measurements["candidate"]["sha256"]))
    checks.append(item("scene.plan_id", scene.get("plan_id") == contract["plan_id"], scene.get("plan_id"), contract["plan_id"]))
    checks.append(item("scene.human_approval", scene.get("human_approval") == "REQUIRED", scene.get("human_approval"), "REQUIRED"))
    checks.append(item("concept.sha256", digest(ROOT / contract["approved_concept"]["path"]) == contract["approved_concept"]["sha256"], digest(ROOT / contract["approved_concept"]["path"]), contract["approved_concept"]["sha256"]))
    checks.append(item("negative_fixture.sha256", digest(ROOT / contract["negative_fixture"]["path"]) == contract["negative_fixture"]["sha256"], digest(ROOT / contract["negative_fixture"]["path"]), contract["negative_fixture"]["sha256"]))
    checks.append(item("plan.sha256", digest(PLAN_PATH) == measurements["plan_file_sha256"], digest(PLAN_PATH), measurements["plan_file_sha256"]))
    checks.append(item("contract.sha256", digest(CONTRACT_PATH) == measurements["contract_file_sha256"], digest(CONTRACT_PATH), measurements["contract_file_sha256"]))
    checks.append(item("builder.sha256", digest(BUILDER_PATH) == measurements["builder_script_sha256"], digest(BUILDER_PATH), measurements["builder_script_sha256"]))
    checks.append(item("validator.sha256", digest(Path(__file__).resolve()) == measurements["validator_script_sha256"], digest(Path(__file__).resolve()), measurements["validator_script_sha256"]))

    missing_collections = sorted(set(contract["required_collections"]) - {collection.name for collection in bpy.data.collections})
    missing_objects = sorted(set(contract["required_primary_objects"]) - set(scene.objects.keys()))
    checks.append(item("collections.required", not missing_collections, missing_collections, []))
    checks.append(item("objects.required", not missing_objects, missing_objects, []))
    checks.append(item("render.engine", scene.render.engine == contract["render"]["engine"], scene.render.engine, contract["render"]["engine"]))
    checks.append(item("render.workbench_light", scene.display.shading.light == contract["render"]["light"], scene.display.shading.light, contract["render"]["light"]))

    production = [obj for obj in scene.objects if obj.type == "MESH" and obj.get("production_geometry")]
    low, high = union_bounds(production)
    dims = contract["dimensions_m"]
    height = high.z - low.z
    checks.append(item("dimensions.height", abs(height - dims["overall_height_target"]) <= dims["overall_height_tolerance"], height, {"target": dims["overall_height_target"], "tolerance": dims["overall_height_tolerance"]}))
    checks.append(item("dimensions.ground", abs(low.z - dims["ground_z_target"]) <= dims["ground_z_tolerance"], low.z, {"target": dims["ground_z_target"], "tolerance": dims["ground_z_tolerance"]}))
    invalid_scales = {obj.name: list(obj.scale) for obj in production if any(abs(value - 1.0) > 1e-6 for value in obj.scale)}
    checks.append(item("rigid.applied_scales", not invalid_scales, invalid_scales, {}))
    external = [obj.name for obj in production if obj.get("source_kind") != "PROCEDURAL_ORIGINAL"]
    checks.append(item("assets.external_count", len(external) == contract["external_asset_count"], external, []))
    tertiary = [obj.name for obj in production if obj.get("form_importance") == "TERTIARY"]
    checks.append(item("forms.tertiary_ceiling", len(tertiary) <= contract["tertiary_object_max"], len(tertiary), contract["tertiary_object_max"]))
    hidden_production = [obj.name for obj in production if obj.hide_render or obj.hide_viewport]
    checks.append(item("cutaway.not_saved", not hidden_production, hidden_production, []))

    render_failures = []
    for filename, camera in contract["render"]["views"]:
        record = measurements.get("review_renders", {}).get(filename)
        path = args.measurements.parent / filename
        if not record or not path.exists() or digest(path) != record.get("sha256") or record.get("candidate_sha256") != before_sha or record.get("camera") != camera:
            render_failures.append(filename)
    checks.append(item("renders.bound", not render_failures, render_failures, []))
    after_sha = digest(blend)
    checks.append(item("validator.read_only", before_sha == after_sha, after_sha, before_sha))
    failures = [check["rule"] for check in checks if not check["pass"]]
    output = {
        "schema_version": "1.0",
        "claim_class": "OBSERVED",
        "gate": "VAREK_CHASSIS_V2A_INDEPENDENT_VALIDATION",
        "overall": "PASS" if not failures else "FAIL",
        "candidate_sha256": before_sha,
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "failures": failures,
        "readback": {
            "height_m": height,
            "ground_min_z_m": low.z,
            "tertiary_object_count": len(tertiary),
            "external_asset_count": len(external),
            "proportion_measurement_class": measurements["provisional_proportion_readback"]["measurement_class"],
            "claim_boundary": "MACHINE_PASS_DOES_NOT_EQUAL_VISUAL_APPROVAL"
        },
        "human_approval": "REQUIRED"
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    if failures:
        print("VAREK_CHASSIS_V2A_VALIDATION_FAIL=" + ",".join(failures), file=sys.stderr)
        raise SystemExit(1)
    print(f"VAREK_CHASSIS_V2A_VALIDATION_PASS={before_sha}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        print(f"VAREK_CHASSIS_V2A_VALIDATION_ERROR={exc}", file=sys.stderr)
        raise SystemExit(1)
