#!/usr/bin/env python3
"""Read-only triangle-intersection census for overhead arm/yoke clearance."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy
from mathutils.bvhtree import BVHTree


ROOT = Path("/home/aaron/animation/thulans-production")
CANDIDATE = ROOT / "blender/candidates/varek-v2b7-anchor-grounded.blend"
CANDIDATE_SHA = "ccc8cd8fb3083f5c1298f3e2d046fb054752208597e7641c3051fe12d3cf6c40"
OUTPUT = ROOT / "evidence/varek-v2b7-clearance-final/overhead-arm-yoke-intersections.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main() -> None:
    if Path(bpy.data.filepath).resolve() != CANDIDATE.resolve() or digest(CANDIDATE) != CANDIDATE_SHA:
        raise RuntimeError("V2B7 candidate identity mismatch")
    if OUTPUT.exists():
        raise RuntimeError("overhead clearance diagnostic output collision")

    scene = bpy.context.scene
    scene.frame_set(60)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    arm_bones = {f"{region}.{side}" for region in ("upper_arm", "forearm", "hand") for side in ("L", "R")}
    arms = [
        obj for obj in scene.objects
        if obj.type == "MESH"
        and obj.get("production_geometry")
        and obj.get("rigid_driver_bone") in arm_bones
        and not obj.name.startswith("Pilot_")
    ]
    yoke = [
        obj for obj in scene.objects
        if obj.type == "MESH"
        and obj.get("production_geometry")
        and obj.get("rigid_driver_bone") == "yoke"
    ]
    trees = {obj.name: BVHTree.FromObject(obj, depsgraph) for obj in arms + yoke}
    intersections = []
    for arm in sorted(arms, key=lambda obj: obj.name):
        for fixed in sorted(yoke, key=lambda obj: obj.name):
            overlap = trees[arm.name].overlap(trees[fixed.name])
            if overlap:
                intersections.append({
                    "arm_object": arm.name,
                    "arm_bone": arm.get("rigid_driver_bone"),
                    "yoke_object": fixed.name,
                    "triangle_pair_count": len(overlap),
                })
    record = {
        "schema_version": "1.0",
        "claim_class": "OBSERVED",
        "candidate_sha256": CANDIDATE_SHA,
        "frame": 60,
        "arm_objects_checked": len(arms),
        "yoke_objects_checked": len(yoke),
        "intersections": intersections,
        "intersection_pair_count": len(intersections),
        "candidate_unchanged": digest(CANDIDATE) == CANDIDATE_SHA,
    }
    OUTPUT.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
