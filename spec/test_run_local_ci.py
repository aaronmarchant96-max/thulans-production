import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

from tools.run_local_ci import build_checks, build_report, execute_checks


class LocalCITests(unittest.TestCase):
    def test_build_checks_matches_workflow_order_and_revision_range(self):
        checks = build_checks("python-test", "base-sha", "head-sha")

        self.assertEqual(
            [check.check_id for check in checks],
            ["contract", "compliance", "tests", "claims"],
        )
        self.assertEqual(
            checks[1].command[-4:],
            ("--base", "base-sha", "--head", "head-sha"),
        )
        self.assertEqual(
            checks[2].command[1:],
            ("-m", "unittest", "discover", "-s", "spec", "-v"),
        )

    def test_execute_checks_continues_after_failure(self):
        checks = build_checks(sys.executable, "HEAD^", "HEAD")
        runner = Mock(
            side_effect=[
                subprocess.CompletedProcess([], 0),
                subprocess.CompletedProcess([], 7),
                subprocess.CompletedProcess([], 0),
                subprocess.CompletedProcess([], 0),
            ]
        )

        results = execute_checks(Path("/repo"), checks, runner=runner)

        self.assertEqual(runner.call_count, 4)
        self.assertEqual([result.returncode for result in results], [0, 7, 0, 0])

    def test_report_fails_closed_and_names_exclusions(self):
        checks = build_checks(sys.executable, "HEAD^", "HEAD")
        runner = Mock(
            side_effect=[
                subprocess.CompletedProcess([], 0),
                subprocess.CompletedProcess([], 0),
                subprocess.CompletedProcess([], 1),
                subprocess.CompletedProcess([], 0),
            ]
        )
        results = execute_checks(Path("/repo"), checks, runner=runner)

        report = build_report("HEAD^", "HEAD", results)

        self.assertEqual(report["verdict"], "FAIL")
        self.assertEqual(report["failed_checks"], ["tests"])
        self.assertIn(
            "Blender execution, renders, physics simulation, and visual approval",
            report["known_exclusions"],
        )


if __name__ == "__main__":
    unittest.main()
