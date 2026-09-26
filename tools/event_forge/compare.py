"""Compare a recovered Event Forge output corpus with the clean-room oracle.

Both inputs are JSON arrays of proposal dictionaries. The comparison is
structural and deliberately reports differences instead of declaring either
implementation correct.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


KEYS = ("pattern_id", "seed", "actor_ids", "location_ids", "options", "proposed_effects")


def compare(reference: list[dict[str, Any]], candidate: list[dict[str, Any]]) -> dict[str, Any]:
    mismatches: list[dict[str, Any]] = []
    for index, (expected, actual) in enumerate(zip(reference, candidate)):
        for key in KEYS:
            if expected.get(key) != actual.get(key):
                mismatches.append({"index": index, "field": key, "reference": expected.get(key), "candidate": actual.get(key)})
    if len(reference) != len(candidate):
        mismatches.append({"field": "length", "reference": len(reference), "candidate": len(candidate)})
    return {"reference_count": len(reference), "candidate_count": len(candidate), "match": not mismatches, "mismatches": mismatches}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: python -m tools.event_forge.compare reference.json candidate.json")
    result = compare(json.loads(Path(sys.argv[1]).read_text()), json.loads(Path(sys.argv[2]).read_text()))
    print(json.dumps(result, indent=2, sort_keys=True))
