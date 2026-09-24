import json
import tempfile
import unittest
from pathlib import Path

from tools.audit_agent_compliance import (
    AddedLine,
    ChangedPath,
    ContractError,
    Violation,
    audit_change,
    build_report,
    compile_runtime_invariants,
    load_contract,
    parse_added_lines,
    parse_name_status,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AgentContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = load_contract(REPO_ROOT / "AGENTS.md")

    def test_contract_compiles_to_runtime_invariants(self):
        compiled = compile_runtime_invariants(self.contract)
        self.assertIn("FAIL CLOSED", compiled)
        self.assertIn("PASS_SCOPED", compiled)
        self.assertIn("DIFF_ONLY", compiled)
        self.assertNotIn("## 1. Physical", compiled)

    def test_missing_contract_markers_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "AGENTS.md"
            path.write_text("# prose only\n", encoding="utf-8")
            with self.assertRaises(ContractError):
                load_contract(path)

    def test_git_parsers_capture_added_line_and_rename_destination(self):
        diff = """diff --git a/tools/a.py b/tools/a.py
--- a/tools/a.py
+++ b/tools/a.py
@@ -1,0 +2,2 @@
+safe = 1
+assert True
"""
        additions = parse_added_lines(diff)
        self.assertEqual(additions[0], AddedLine("tools/a.py", 2, "safe = 1"))
        self.assertEqual(additions[1], AddedLine("tools/a.py", 3, "assert True"))
        changes = parse_name_status("R100\told.py\ttools/new.py\n")
        self.assertEqual(changes, [ChangedPath("R100", "tools/new.py")])

    def test_synthetic_pass_and_absolute_path_are_rejected(self):
        additions = [
            AddedLine("tools/new_gate.py", 2, "assert True"),
            AddedLine("tools/new_gate.py", 3, 'verdict = "PASS"'),
            AddedLine("tools/new_gate.py", 4, 'source = "/home/aaron/candidate.blend"'),
        ]
        with tempfile.TemporaryDirectory() as directory:
            violations = audit_change(
                contract=self.contract,
                additions=additions,
                changes=[ChangedPath("M", "tools/new_gate.py")],
                repo_root=Path(directory),
            )
        ids = {item.rule_id for item in violations}
        self.assertIn("synthetic_assert_true", ids)
        self.assertIn("unscoped_pass_verdict", ids)
        self.assertIn("workstation_absolute_path", ids)
        self.assertIn("missing_task_evidence_envelope", ids)

    def test_mock_true_requires_justification_marker(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bad = audit_change(
                contract=self.contract,
                additions=[AddedLine("tools/a.py", 1, "mock.return_value = True")],
                changes=[ChangedPath("M", "tools/a.py")],
                repo_root=root,
            )
            good = audit_change(
                contract=self.contract,
                additions=[
                    AddedLine(
                        "tools/a.py",
                        1,
                        "mock.return_value = True  # AGENT_TEST_DOUBLE_JUSTIFICATION: negative fixture",
                    )
                ],
                changes=[ChangedPath("M", "tools/a.py")],
                repo_root=root,
            )
        self.assertIn("unjustified_true_mock", {item.rule_id for item in bad})
        self.assertNotIn("unjustified_true_mock", {item.rule_id for item in good})

    def test_scoped_pass_is_not_bare_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            violations = audit_change(
                contract=self.contract,
                additions=[
                    AddedLine(
                        "evidence/agent-tasks/TASK.json",
                        1,
                        '"verdict": "PASS_SCOPED",',
                    )
                ],
                changes=[ChangedPath("A", "evidence/agent-tasks/TASK.json")],
                repo_root=Path(directory),
            )
        self.assertNotIn("unscoped_pass_verdict", {item.rule_id for item in violations})

    def test_evidence_metadata_may_name_an_error_gap_fixture(self):
        with tempfile.TemporaryDirectory() as directory:
            violations = audit_change(
                contract=self.contract,
                additions=[
                    AddedLine(
                        "evidence/agent-tasks/TASK.json",
                        1,
                        '"counterevidence_checked": ["untagged NotImplementedError fixture"]',
                    )
                ],
                changes=[ChangedPath("A", "evidence/agent-tasks/TASK.json")],
                repo_root=Path(directory),
            )
        self.assertNotIn("untracked_error_gap", {item.rule_id for item in violations})

    def test_error_gap_requires_machine_readable_marker(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bad = audit_change(
                contract=self.contract,
                additions=[AddedLine("tools/a.py", 1, "raise NotImplementedError")],
                changes=[ChangedPath("M", "tools/a.py")],
                repo_root=root,
            )
            good = audit_change(
                contract=self.contract,
                additions=[
                    AddedLine(
                        "tools/a.py",
                        1,
                        "raise NotImplementedError  # AGENT_ERROR_GAP[RENDER-001]",
                    )
                ],
                changes=[ChangedPath("M", "tools/a.py")],
                repo_root=root,
            )
        self.assertIn("untracked_error_gap", {item.rule_id for item in bad})
        self.assertNotIn("untracked_error_gap", {item.rule_id for item in good})

    def test_path_boundary_and_frozen_file_are_enforced(self):
        with tempfile.TemporaryDirectory() as directory:
            violations = audit_change(
                contract=self.contract,
                additions=[],
                changes=[
                    ChangedPath("A", "outside.txt"),
                    ChangedPath("M", "tools/build_varek_physics_gate_v1.py"),
                ],
                repo_root=Path(directory),
            )
        ids = {item.rule_id for item in violations}
        self.assertIn("path_outside_write_boundary", ids)
        self.assertIn("frozen_path_modified", ids)

    def test_human_override_unlocks_only_named_frozen_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            override_root = root / self.contract["override_root"]
            override_root.mkdir(parents=True)
            record = {
                "schema": "thulans-agent-override-1.0",
                "override_id": "OVERRIDE-001",
                "approved_by": "Aaron Marchant",
                "approved_at": "2026-09-24T00:00:00Z",
                "reason": "Explicit repair authorization",
                "paths": ["tools/build_varek_physics_gate_v1.py"],
                "source_revision": "abc123",
            }
            (override_root / "OVERRIDE-001.json").write_text(
                json.dumps(record), encoding="utf-8"
            )
            violations = audit_change(
                contract=self.contract,
                additions=[],
                changes=[ChangedPath("M", "tools/build_varek_physics_gate_v1.py")],
                repo_root=root,
            )
        self.assertNotIn("frozen_path_modified", {item.rule_id for item in violations})

    def test_valid_task_record_covers_executable_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task_path = Path(self.contract["task_record_root"]) / "TASK-001.json"
            absolute = root / task_path
            absolute.parent.mkdir(parents=True)
            record = {
                "schema": "thulans-agent-task-1.0",
                "task_id": "TASK-001",
                "agent_id": "test-agent",
                "claim": "The scoped compliance check executed.",
                "verdict": "PASS_SCOPED",
                "counterevidence_checked": ["fraudulent fixture rejected"],
                "known_exclusions": [],
                "unexecuted_checks": [],
                "reproduction_command": "python -m unittest spec.test_agent_compliance",
                "covered_paths": ["tools/new_gate.py"],
                "source_revision": "abc123",
            }
            absolute.write_text(json.dumps(record), encoding="utf-8")
            violations = audit_change(
                contract=self.contract,
                additions=[],
                changes=[
                    ChangedPath("A", "tools/new_gate.py"),
                    ChangedPath("A", task_path.as_posix()),
                ],
                repo_root=root,
            )
        self.assertEqual(violations, [])

    def test_pass_record_fails_without_counterevidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task_path = Path(self.contract["task_record_root"]) / "TASK-002.json"
            absolute = root / task_path
            absolute.parent.mkdir(parents=True)
            record = {
                "schema": "thulans-agent-task-1.0",
                "task_id": "TASK-002",
                "agent_id": "test-agent",
                "claim": "Unsupported pass",
                "verdict": "PASS_SCOPED",
                "counterevidence_checked": [],
                "known_exclusions": [],
                "unexecuted_checks": ["mutation test"],
                "reproduction_command": "",
                "covered_paths": ["tools/new_gate.py"],
                "source_revision": "abc123",
            }
            absolute.write_text(json.dumps(record), encoding="utf-8")
            violations = audit_change(
                contract=self.contract,
                additions=[],
                changes=[
                    ChangedPath("A", "tools/new_gate.py"),
                    ChangedPath("A", task_path.as_posix()),
                ],
                repo_root=root,
            )
        ids = {item.rule_id for item in violations}
        self.assertIn("pass_without_counterevidence", ids)
        self.assertIn("pass_with_unexecuted_checks", ids)
        self.assertIn("pass_without_reproduction", ids)

    def test_placation_index_degrades_authority(self):
        report = build_report(
            self.contract,
            [
                # Synthetic pass alone reaches the contract's DIFF_ONLY threshold.
                Violation("synthetic_assert_true", "fixture", 3),
            ],
            "base",
            "head",
        )
        self.assertEqual(report["recommended_authority"], "DIFF_ONLY")


if __name__ == "__main__":
    unittest.main()
