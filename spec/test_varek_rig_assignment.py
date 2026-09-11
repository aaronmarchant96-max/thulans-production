#!/usr/bin/env python3
"""Focused regression tests for Varek moving-module assignment."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from varek_rig_assignment import bone_for_name, side_of, validate_assignment


class VarekRigAssignmentTests(unittest.TestCase):
    def test_side_tokens_are_recognized_inside_names(self):
        self.assertEqual(side_of("Forearm_R_OUTER"), "R")
        self.assertEqual(side_of("LegRail_L_INNER"), "L")
        self.assertEqual(side_of("Finger_R_02"), "R")

    def test_representative_moving_modules_resolve_laterally(self):
        expected = {
            "Forearm_R_OUTER": "forearm.R",
            "UpperArm_L_INNER": "upper_arm.L",
            "LegRail_L_INNER": "thigh.L",
            "Finger_R_02": "hand.R",
            "Manipulator_Digit_L_3": "hand.L",
            "Toe_Pad_R_0": "foot.R",
            "Femur_Ram_L_1": "thigh.L",
            "Shin_R_DORSAL": "shin.R",
            "Gren_Skildus": "upper_arm.L",
        }
        for name, bone in expected.items():
            with self.subTest(name=name):
                self.assertEqual(bone_for_name(name), bone)
                validate_assignment(name, bone)

    def test_lateral_limb_module_cannot_resolve_to_spine(self):
        with self.assertRaisesRegex(ValueError, "resolved centrally"):
            validate_assignment("Forearm_R_OUTER", "spine")

    def test_wrong_lateral_bone_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "misassigned"):
            validate_assignment("Finger_R_02", "hand.L")

    def test_explicit_central_whitelist_is_supported(self):
        validate_assignment("Forearm_R_OUTER", "spine", {"Forearm_R_OUTER"})


if __name__ == "__main__":
    unittest.main()
