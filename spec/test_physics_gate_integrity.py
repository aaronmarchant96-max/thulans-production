from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_gate_module():
    path = ROOT / "tools/build_varek_physics_gate_v1.py"
    spec = importlib.util.spec_from_file_location("physics_gate", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PhysicsGateIntegrityTests(unittest.TestCase):
    def test_declared_battery_cannot_report_unexecuted_passes(self):
        gate = load_gate_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = root / "candidate.blend"
            report_path = root / "report.json"
            candidate.write_bytes(b"test candidate")

            exit_code = gate.run_gate(candidate, report_path)
            report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 1)
        self.assertEqual(report["result"], "FAIL_UNIMPLEMENTED")
        self.assertFalse(any(report["claim_graph"].values()))
        self.assertEqual(sum(layer["passed"] for layer in report["assertions"].values()), 0)
        self.assertTrue(all(layer["status"] == "UNIMPLEMENTED" for layer in report["assertions"].values()))

    def test_partial_single_joint_oracle_exits_nonzero(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/validate_hand_physics_results.py")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL_UNIMPLEMENTED", result.stdout)
        self.assertNotIn("ORACLE RESULT: PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
