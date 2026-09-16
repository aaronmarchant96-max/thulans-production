import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / 'tools/check_hand_physics_preflight.py'
spec = importlib.util.spec_from_file_location('hand_preflight', path)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

class PreflightTests(unittest.TestCase):
    def ready(self):
        return dict(candidate_sha256='other', independent_digit_motion=True,
                    wrist_travel_limits=True, physics_world=True,
                    free_dynamic_tool=True, gravity_enabled=True)

    def test_missing_evidence_fails_closed(self):
        result = gate.evaluate({})
        self.assertEqual(result['result'], 'FAIL')
        self.assertFalse(result['handoff_authorized'])

    def test_fixed_closed_fingers_fail(self):
        data = self.ready(); data['independent_digit_motion'] = False
        self.assertIn('independent_digit_motion_missing', gate.evaluate(data)['failures'])

    def test_driven_tool_fails(self):
        data = self.ready(); data['free_dynamic_tool'] = False
        self.assertIn('free_dynamic_tool_missing', gate.evaluate(data)['failures'])

    def test_wrong_wrist_human_rejection_cannot_be_overridden(self):
        data = self.ready(); data['candidate_sha256'] = gate.REJECTED_WRIST_SHA
        self.assertIn('human_rejected_wrong_side_of_wrist', gate.evaluate(data)['failures'])

    def test_truthy_strings_are_not_evidence(self):
        data = self.ready(); data['physics_world'] = 'PASS'
        self.assertEqual(gate.evaluate(data)['result'], 'FAIL')

    def test_prerequisites_never_authorize_physics_or_handoff(self):
        result = gate.evaluate(self.ready())
        self.assertEqual(result['result'], 'PREREQUISITES_ONLY_PASS')
        self.assertFalse(result['physics_simulation_executed'])
        self.assertFalse(result['handoff_authorized'])

class OracleMutationTests(unittest.TestCase):
    def test_oracle_catches_invalid_aperture_trajectory(self):
        # Verify that validate_hand_physics_results.py returns non-zero on current/corrupted trajectory
        import subprocess, sys
        val_script = Path(__file__).resolve().parents[1] / 'tools/validate_hand_physics_results.py'
        res = subprocess.run([sys.executable, str(val_script)], capture_output=True, text=True)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("ORACLE RESULT: FAIL", res.stdout)

    def test_oracle_rejects_cal_bad_001(self):
        # Verify that CAL-BAD-001 specimen is permanently rejected by the oracle
        import shutil, subprocess, sys
        root = Path(__file__).resolve().parents[1]
        val_script = root / 'tools/validate_hand_physics_results.py'
        cal_dir = root / 'evidence/calibration/CAL-BAD-001'
        target_dir = root / 'evidence/varek-v55-mechanical-grip'

        diag_bak = target_dir / 'full-hand-diagnostic.json.bak'
        read_bak = target_dir / 'full-hand-readback.json.bak'

        if (target_dir / 'full-hand-diagnostic.json').exists():
            shutil.copy(target_dir / 'full-hand-diagnostic.json', diag_bak)
        if (target_dir / 'full-hand-readback.json').exists():
            shutil.copy(target_dir / 'full-hand-readback.json', read_bak)

        try:
            shutil.copy(cal_dir / 'full-hand-diagnostic.json', target_dir / 'full-hand-diagnostic.json')
            shutil.copy(cal_dir / 'full-hand-readback.json', target_dir / 'full-hand-readback.json')
            
            res = subprocess.run([sys.executable, str(val_script)], capture_output=True, text=True)
            self.assertNotEqual(res.returncode, 0)
            self.assertIn("A1-D2-REOPEN-DIR", res.stdout)
            self.assertIn("A1-GRIP-TRAJECTORY", res.stdout)
            self.assertIn("ORACLE RESULT: FAIL", res.stdout)
        finally:
            if diag_bak.exists():
                shutil.copy(diag_bak, target_dir / 'full-hand-diagnostic.json')
                diag_bak.unlink()
            if read_bak.exists():
                shutil.copy(read_bak, target_dir / 'full-hand-readback.json')
                read_bak.unlink()

if __name__ == '__main__':
    unittest.main()
