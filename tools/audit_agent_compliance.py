#!/usr/bin/env python3
"""Fail-closed enforcement for the machine-readable contract in AGENTS.md."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence


CONTRACT_BEGIN = "<!-- AGENT_CONTRACT_V1_BEGIN -->"
CONTRACT_END = "<!-- AGENT_CONTRACT_V1_END -->"


class ContractError(RuntimeError):
    """The executable agent contract is absent or malformed."""


@dataclass(frozen=True)
class AddedLine:
    path: str
    line: int
    text: str


@dataclass(frozen=True)
class ChangedPath:
    status: str
    path: str


@dataclass(frozen=True)
class Violation:
    rule_id: str
    message: str
    weight: int
    path: str | None = None
    line: int | None = None


def load_contract(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    start = text.find(CONTRACT_BEGIN)
    end = text.find(CONTRACT_END)
    if start < 0 or end < 0 or end <= start:
        raise ContractError("AGENT_CONTRACT_V1 markers are missing or reversed")

    payload = text[start + len(CONTRACT_BEGIN) : end].strip()
    fenced = re.fullmatch(r"```json\s*(\{.*\})\s*```", payload, flags=re.DOTALL)
    if not fenced:
        raise ContractError("contract payload must be one fenced JSON object")

    try:
        contract = json.loads(fenced.group(1))
    except json.JSONDecodeError as exc:
        raise ContractError(f"contract JSON is invalid: {exc}") from exc

    required = {
        "schema",
        "fail_closed",
        "writable_exact",
        "writable_roots",
        "frozen_paths",
        "override_root",
        "override_required_fields",
        "allowed_verdicts",
        "scanner_excludes",
        "banned_patterns",
        "error_gap_patterns",
        "error_gap_marker_regex",
        "task_record_root",
        "task_record_required_for_roots",
        "task_record_required_fields",
        "placation_index",
    }
    missing = sorted(required - contract.keys())
    if missing:
        raise ContractError(f"contract fields missing: {', '.join(missing)}")
    if contract["schema"] != "thulans-agent-contract-1.0":
        raise ContractError(f"unsupported schema: {contract['schema']!r}")
    if contract["fail_closed"] is not True:
        raise ContractError("fail_closed must be true")

    for pattern in contract["banned_patterns"]:
        if not {"id", "regex", "weight"} <= pattern.keys():
            raise ContractError("each banned pattern requires id, regex, and weight")
        try:
            re.compile(pattern["regex"])
        except re.error as exc:
            raise ContractError(f"invalid banned regex {pattern['id']}: {exc}") from exc

    try:
        re.compile(contract["error_gap_marker_regex"])
        for pattern in contract["error_gap_patterns"]:
            re.compile(pattern)
    except re.error as exc:
        raise ContractError(f"invalid error-gap regex: {exc}") from exc

    thresholds = contract["placation_index"]
    if thresholds.get("diff_only_threshold", 0) <= 0:
        raise ContractError("diff_only_threshold must be positive")
    if thresholds.get("blocked_threshold", 0) < thresholds["diff_only_threshold"]:
        raise ContractError("blocked_threshold must be >= diff_only_threshold")
    return contract


def compile_runtime_invariants(contract: Mapping[str, object]) -> str:
    """Compile the JSON contract into a compact prompt/harness invariant block."""

    exact = ", ".join(contract["writable_exact"])
    roots = ", ".join(contract["writable_roots"])
    frozen = ", ".join(contract["frozen_paths"])
    verdicts = ", ".join(contract["allowed_verdicts"])
    banned = ", ".join(item["id"] for item in contract["banned_patterns"])
    required = ", ".join(contract["task_record_required_fields"])
    pi = contract["placation_index"]
    return "\n".join(
        (
            "THULANS AGENT RUNTIME CONTRACT v1",
            "FAIL CLOSED: output or changes violating these invariants must be rejected.",
            f"WRITE EXACT: {exact}",
            f"WRITE ROOTS: {roots}",
            f"FROZEN WITHOUT HUMAN OVERRIDE: {frozen}",
            f"VERDICTS: {verdicts}",
            f"BANNED RULE IDS: {banned}",
            f"TASK RECORD FIELDS: {required}",
            "PASS_SCOPED requires counterevidence, zero unexecuted checks, and a reproduction command.",
            "Missing telemetry is UNAVAILABLE; it is never zero and never PASS.",
            (
                "PLACATION AUTHORITY: PI >= "
                f"{pi['diff_only_threshold']} => DIFF_ONLY; PI >= {pi['blocked_threshold']} => BLOCKED."
            ),
        )
    )


def _run_git(repo_root: Path, args: Sequence[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ContractError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def collect_git_change(repo_root: Path, base: str, head: str) -> tuple[str, str]:
    if head == "WORKTREE":
        diff = _run_git(repo_root, ["diff", "--unified=0", "--no-ext-diff", base, "--"])
        names = _run_git(repo_root, ["diff", "--name-status", "--no-ext-diff", base, "--"])
    else:
        diff = _run_git(repo_root, ["diff", "--unified=0", "--no-ext-diff", base, head, "--"])
        names = _run_git(repo_root, ["diff", "--name-status", "--no-ext-diff", base, head, "--"])
    return diff, names


def parse_name_status(text: str) -> list[ChangedPath]:
    changes: list[ChangedPath] = []
    for raw in text.splitlines():
        if not raw.strip():
            continue
        parts = raw.split("\t")
        status = parts[0]
        if status.startswith(("R", "C")) and len(parts) >= 3:
            changes.append(ChangedPath(status=status, path=parts[2]))
        elif len(parts) >= 2:
            changes.append(ChangedPath(status=status, path=parts[1]))
        else:
            raise ContractError(f"unparseable git name-status line: {raw!r}")
    return changes


def parse_added_lines(diff: str) -> list[AddedLine]:
    additions: list[AddedLine] = []
    current_path: str | None = None
    next_line: int | None = None

    for raw in diff.splitlines():
        if raw.startswith("+++ b/"):
            current_path = raw[6:]
            continue
        if raw.startswith("+++ /dev/null"):
            current_path = None
            continue
        if raw.startswith("@@"):
            match = re.search(r"\+(\d+)(?:,(\d+))?", raw)
            next_line = int(match.group(1)) if match else None
            continue
        if current_path is None or next_line is None:
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            additions.append(AddedLine(current_path, next_line, raw[1:]))
            next_line += 1
        elif raw.startswith("-") and not raw.startswith("---"):
            continue
        else:
            next_line += 1
    return additions


def _matches_any(path: str, patterns: Iterable[str]) -> bool:
    return any(path == pattern or fnmatch.fnmatch(path, pattern) for pattern in patterns)


def _is_writable(path: str, contract: Mapping[str, object]) -> bool:
    if path in contract["writable_exact"]:
        return True
    return any(path.startswith(root) for root in contract["writable_roots"])


def _is_runtime_source(path: str) -> bool:
    return Path(path).suffix.lower() in {
        ".gd",
        ".js",
        ".json",
        ".jsx",
        ".mjs",
        ".py",
        ".ts",
        ".tsx",
        ".yaml",
        ".yml",
    }


def _load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON object required: {path}")
    return value


def _valid_override(
    repo_root: Path,
    contract: Mapping[str, object],
    frozen_path: str,
) -> bool:
    root = repo_root / str(contract["override_root"])
    if not root.exists():
        return False
    required = set(contract["override_required_fields"])
    for candidate in sorted(root.glob("*.json")):
        try:
            record = _load_json(candidate)
        except ContractError:
            continue
        if required - record.keys():
            continue
        if record.get("schema") != "thulans-agent-override-1.0":
            continue
        if record.get("approved_by") != "Aaron Marchant":
            continue
        if frozen_path not in record.get("paths", []):
            continue
        if not str(record.get("reason", "")).strip():
            continue
        return True
    return False


def _validate_task_record(
    record: Mapping[str, object],
    path: str,
    contract: Mapping[str, object],
    required_coverage: set[str],
) -> list[Violation]:
    violations: list[Violation] = []
    missing = sorted(set(contract["task_record_required_fields"]) - record.keys())
    if missing:
        violations.append(
            Violation(
                "task_record_missing_fields",
                f"task record is missing: {', '.join(missing)}",
                3,
                path,
            )
        )
        return violations

    verdict = record["verdict"]
    if record["schema"] != "thulans-agent-task-1.0":
        violations.append(
            Violation(
                "invalid_task_record_schema",
                f"unsupported task record schema: {record['schema']!r}",
                3,
                path,
            )
        )
    if verdict not in contract["allowed_verdicts"]:
        violations.append(
            Violation("invalid_verdict", f"unsupported verdict: {verdict!r}", 3, path)
        )

    for field in ("counterevidence_checked", "known_exclusions", "unexecuted_checks", "covered_paths"):
        if not isinstance(record[field], list):
            violations.append(
                Violation("task_record_field_type", f"{field} must be a list", 2, path)
            )

    if violations:
        return violations

    covered = set(record["covered_paths"])
    uncovered = sorted(required_coverage - covered)
    if uncovered:
        violations.append(
            Violation(
                "task_record_incomplete_coverage",
                f"task record does not cover: {', '.join(uncovered)}",
                3,
                path,
            )
        )

    if not str(record["claim"]).strip():
        violations.append(Violation("task_record_empty_claim", "claim is empty", 2, path))
    if not str(record["source_revision"]).strip():
        violations.append(
            Violation("task_record_missing_revision", "source_revision is empty", 2, path)
        )

    if verdict == "PASS_SCOPED":
        if not record["counterevidence_checked"]:
            violations.append(
                Violation(
                    "pass_without_counterevidence",
                    "PASS_SCOPED requires counterevidence_checked",
                    4,
                    path,
                )
            )
        if record["unexecuted_checks"]:
            violations.append(
                Violation(
                    "pass_with_unexecuted_checks",
                    "PASS_SCOPED cannot contain unexecuted checks",
                    4,
                    path,
                )
            )
        if not str(record["reproduction_command"]).strip():
            violations.append(
                Violation(
                    "pass_without_reproduction",
                    "PASS_SCOPED requires reproduction_command",
                    4,
                    path,
                )
            )
    return violations


def audit_change(
    *,
    contract: Mapping[str, object],
    additions: Sequence[AddedLine],
    changes: Sequence[ChangedPath],
    repo_root: Path,
    json_loader: Callable[[Path], dict] = _load_json,
) -> list[Violation]:
    violations: list[Violation] = []
    changed_paths = {change.path for change in changes}

    for change in changes:
        if not _is_writable(change.path, contract):
            violations.append(
                Violation(
                    "path_outside_write_boundary",
                    "path is outside writable_exact and writable_roots",
                    3,
                    change.path,
                )
            )
        if change.path in contract["frozen_paths"] and not _valid_override(
            repo_root, contract, change.path
        ):
            violations.append(
                Violation(
                    "frozen_path_modified",
                    "frozen path changed without an Aaron-approved override record",
                    5,
                    change.path,
                )
            )

    excluded = contract["scanner_excludes"]
    gap_marker = re.compile(contract["error_gap_marker_regex"])
    gap_patterns = [re.compile(pattern) for pattern in contract["error_gap_patterns"]]

    for added in additions:
        if _matches_any(added.path, excluded):
            continue
        for rule in contract["banned_patterns"]:
            if re.search(rule["regex"], added.text):
                marker = rule.get("allow_marker")
                if marker and marker in added.text:
                    continue
                violations.append(
                    Violation(
                        rule["id"],
                        f"banned added-line pattern matched: {rule['regex']}",
                        int(rule["weight"]),
                        added.path,
                        added.line,
                    )
                )
        is_evidence_metadata = added.path.startswith(contract["task_record_root"]) or added.path.startswith(
            contract["override_root"]
        )
        if _is_runtime_source(added.path) and not is_evidence_metadata and any(
            pattern.search(added.text) for pattern in gap_patterns
        ):
            if not gap_marker.search(added.text):
                violations.append(
                    Violation(
                        "untracked_error_gap",
                        "new error-gap logic requires AGENT_ERROR_GAP[ID] on the added line",
                        2,
                        added.path,
                        added.line,
                    )
                )

    required_coverage = {
        path
        for path in changed_paths
        if any(path.startswith(root) for root in contract["task_record_required_for_roots"])
        and not path.startswith(contract["task_record_root"])
    }
    if required_coverage:
        task_records = sorted(
            path
            for path in changed_paths
            if path.startswith(contract["task_record_root"]) and path.endswith(".json")
        )
        if not task_records:
            violations.append(
                Violation(
                    "missing_task_evidence_envelope",
                    "executable changes require a changed JSON task record",
                    4,
                )
            )
        else:
            valid_records = 0
            record_violations: list[Violation] = []
            for path in task_records:
                try:
                    record = json_loader(repo_root / path)
                except ContractError as exc:
                    record_violations.append(
                        Violation("invalid_task_record_json", str(exc), 3, path)
                    )
                    continue
                found = _validate_task_record(record, path, contract, required_coverage)
                if found:
                    record_violations.extend(found)
                else:
                    valid_records += 1
            if valid_records == 0:
                violations.extend(record_violations)
    return violations


def build_report(
    contract: Mapping[str, object],
    violations: Sequence[Violation],
    base: str,
    head: str,
) -> dict:
    pi = sum(item.weight for item in violations)
    thresholds = contract["placation_index"]
    if pi >= thresholds["blocked_threshold"]:
        authority = "BLOCKED"
    elif pi >= thresholds["diff_only_threshold"]:
        authority = "DIFF_ONLY"
    else:
        authority = "WRITE"
    return {
        "schema": "thulans-agent-compliance-report-1.0",
        "base": base,
        "head": head,
        "verdict": "FAIL" if violations else "PASS_SCOPED",
        "placation_index_delta": pi,
        "recommended_authority": authority,
        "violations": [asdict(item) for item in violations],
    }


def _default_base(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD^"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "HEAD"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default="AGENTS.md")
    parser.add_argument("--base")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--compile-only", action="store_true")
    parser.add_argument("--json-output")
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]
    try:
        contract = load_contract(repo_root / args.contract)
        if args.compile_only:
            print(compile_runtime_invariants(contract))
            return 0

        base = args.base or _default_base(repo_root)
        diff, names = collect_git_change(repo_root, base, args.head)
        violations = audit_change(
            contract=contract,
            additions=parse_added_lines(diff),
            changes=parse_name_status(names),
            repo_root=repo_root,
        )
        report = build_report(contract, violations, base, args.head)
    except ContractError as exc:
        print(f"AGENT CONTRACT ERROR: {exc}", file=sys.stderr)
        return 2

    output = json.dumps(report, indent=2, sort_keys=True)
    print(output)
    if args.json_output:
        (repo_root / args.json_output).write_text(output + "\n", encoding="utf-8")
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
