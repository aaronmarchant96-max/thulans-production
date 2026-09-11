#!/usr/bin/env python3
"""Deterministic object-name to Varek rig-bone assignment."""

from __future__ import annotations

import re


CENTRAL_BONES = frozenset({"root", "pelvis", "spine", "yoke"})
SIDE_TOKEN = re.compile(r"(?:^|[_.])(L|R)(?=[_.]|$)")


def side_of(name: str) -> str | None:
    """Return a token-delimited L/R marker anywhere in an object name."""
    matches = SIDE_TOKEN.findall(name)
    if not matches:
        return None
    if len(set(matches)) != 1:
        raise ValueError(f"ambiguous side tokens in {name!r}: {matches}")
    return matches[0]


def limb_region(name: str) -> str | None:
    """Return the intended moving limb region, if the name declares one."""
    if name.startswith("Pilot_"):
        if "Thigh" in name:
            return "thigh"
        if "Shin" in name:
            return "shin"
        if "Foot" in name:
            return "foot"
        if "UpperArm" in name:
            return "upper_arm"
        if "Forearm" in name:
            return "forearm"
    prefix_regions = (
        (("Foot_", "Heel_", "Toe_", "Folded_", "Front_Visible_", "Sole_", "Ankle_"), "foot"),
        (("Shin_", "Knee_Ankle_", "Rear_Hydraulic_Piston_Lower", "Knee_Pivot"), "shin"),
        (("Femur_", "LegRail_", "Pelvis_Knee_", "Rear_Hydraulic_Piston_Upper", "Hip_Pivot", "Knee_Guard"), "thigh"),
        (("Manipulator_", "Palm_", "Digit_", "Finger_", "Wrist_"), "hand"),
        (("Forearm_", "Arm_Ram", "Elbow_Pivot"), "forearm"),
        (("UpperArm_", "Shoulder_Pivot"), "upper_arm"),
    )
    for prefixes, region in prefix_regions:
        if name.startswith(prefixes):
            return region
    return None


def bone_for_name(name: str) -> str:
    if name == "Gren_Skildus":
        return "upper_arm.L"
    side = side_of(name)
    region = limb_region(name)
    if region is not None:
        if side is None:
            raise ValueError(f"limb-tagged object has no side token: {name}")
        return f"{region}.{side}"
    if name.startswith("Pilot_"):
        return "spine" if "Head" in name or "Torso" in name else "pelvis"
    if name.startswith(("Pelvic_", "Abdominal_")):
        return "pelvis"
    if name.startswith("Yoke_"):
        return "yoke"
    return "spine"


def validate_assignment(name: str, bone: str, central_whitelist=()) -> None:
    """Reject lateral limb modules assigned centrally or to the wrong side/region."""
    side = side_of(name)
    region = limb_region(name)
    if region is None or side is None or name in central_whitelist:
        return
    expected = f"{region}.{side}"
    if bone in CENTRAL_BONES:
        raise ValueError(f"lateral limb module resolved centrally: {name} -> {bone}")
    if bone != expected:
        raise ValueError(f"lateral limb module misassigned: {name} -> {bone}; expected {expected}")
