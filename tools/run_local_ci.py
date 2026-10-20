#!/usr/bin/env python3
"""Run the repository checks used by the GitHub Actions integrity workflow."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Sequence


@dataclass(frozen=True)
class CheckSpec:
    check_id: str
    description: str
    command: tuple[str, ...]


@dataclass(frozen=True)
class CheckResult:
    check_id: str
    description: str
    command: tuple[str, ...]
    returncode: int


Runner = Callable[..., subprocess.CompletedProcess]


def build_checks(python: str, base: str, head: str) -> tuple[CheckSpec, ...]:
    """Return the local equivalents of the workflow's executable steps."""

    return (
        CheckSpec(
            "contract",
            "Compile executable agent contract",
            (python, "tools/audit_agent_compliance.py", "--compile-only"),
        ),
        CheckSpec(
            "compliance",
            "Audit agent compliance for the selected revision range",
            (
                python,
                "tools/audit_agent_compliance.py",
                "--base",
                base,
                "--head",
                head,
            ),
        ),
        CheckSpec(
            "tests",
            "Run repository unit tests",
            (python, "-m", "unittest", "discover", "-s", "spec", "-v"),
        ),
        CheckSpec(
            "claims",
            "Audit canonical claim records",
            (python, "tools/audit_claim_records.py"),
        ),
    )


def execute_checks(
    repo_root: Path,
    checks: Sequence[CheckSpec],
    runner: Runner = subprocess.run,
) -> list[CheckResult]:
    """Execute every check so one failure does not hide later diagnostics."""

    results: list[CheckResult] = []
    for index, check in enumerate(checks, start=1):
        print(
            f"\n[{index}/{len(checks)}] {check.description}",
            file=sys.stderr,
            flush=True,
        )
        completed = runner(list(check.command), cwd=repo_root, check=False)
        results.append(
            CheckResult(
                check_id=check.check_id,
                description=check.description,
                command=check.command,
                returncode=completed.returncode,
            )
        )
    return results


def build_report(base: str, head: str, results: Sequence[CheckResult]) -> dict:
    """Build a machine-readable summary without broadening the evidence scope."""

    failures = [result.check_id for result in results if result.returncode != 0]
    return {
        "schema": "thulans-local-ci-report-1.0",
        "base": base,
        "head": head,
        "verdict": "FAIL" if failures else "PASS_SCOPED",
        "failed_checks": failures,
        "checks": [asdict(result) for result in results],
        "known_exclusions": [
            "GitHub-hosted runner allocation and workflow integration",
            "Blender execution, renders, physics simulation, and visual approval",
            "Unimplemented physical-gate assertions",
        ],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base",
        default="HEAD^",
        help="Base Git revision for the compliance diff (default: HEAD^)",
    )
    parser.add_argument(
        "--head",
        default="HEAD",
        help="Head Git revision for the compliance diff (default: HEAD)",
    )
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]
    checks = build_checks(sys.executable, args.base, args.head)
    results = execute_checks(repo_root, checks)
    report = build_report(args.base, args.head, results)
    print("\n" + json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["failed_checks"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
