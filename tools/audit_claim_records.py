"""Validate canonical CARDO claim records and inventory legacy PASS language."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

try:
    from tools.cardo_claims import SCHEMA_VERSION, validate_record
except ModuleNotFoundError:  # Direct execution from tools/
    from cardo_claims import SCHEMA_VERSION, validate_record


PASS_TOKENS = {"PASS", "PASSED", "PASS_SCOPED", "MACHINE_PASS"}
VERDICT_KEYS = {"result", "overall", "verdict", "status", "machine_result"}
NON_CLAIM_SCHEMAS = {
    "thulans-agent-task-1.0",
    "thulans-agent-override-1.0",
    "thulans-agent-compliance-report-1.0",
}


def audit(root: Path) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    legacy: list[str] = []
    for path in sorted((root / "evidence").rglob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"{path.relative_to(root)}: unreadable JSON: {exc}")
            continue
        if not isinstance(record, dict):
            continue
        if record.get("schema") in NON_CLAIM_SCHEMAS:
            continue
        if record.get("schema_version") == SCHEMA_VERSION:
            failures.extend(
                f"{path.relative_to(root)}: {reason}" for reason in validate_record(record)
            )
            continue
        for key in VERDICT_KEYS:
            value = str(record.get(key, "")).upper()
            if any(token in value for token in PASS_TOKENS):
                legacy.append(f"{path.relative_to(root)}:{key}={record.get(key)}")
                break
    return failures, legacy


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--legacy-inventory", type=Path)
    args = parser.parse_args()
    failures, legacy = audit(args.root.resolve())
    if args.legacy_inventory:
        args.legacy_inventory.parent.mkdir(parents=True, exist_ok=True)
        args.legacy_inventory.write_text("\n".join(legacy) + ("\n" if legacy else ""), encoding="utf-8")
    print(f"canonical_failures={len(failures)} legacy_pass_records={len(legacy)}")
    for failure in failures:
        print(f"FAIL {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
