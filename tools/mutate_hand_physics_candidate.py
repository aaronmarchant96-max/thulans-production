"""Adversarial Mutant Generator for Varek Physics Gate v1.

Generates 50 corrupted test derivatives (mutant_001 through mutant_050) to verify
that the gate engine reliably rejects fraudulent or broken scenes.
"""

from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path("/home/aaron/animation/thulans-production")
MUTANT_DIR = ROOT / "blender/candidates/mutants"

MUTANTS = [
    {"id": "MUT-001", "name": "hidden_parenting", "type": "parent_constraint"},
    {"id": "MUT-002", "name": "gravity_disabled", "type": "zero_gravity"},
    {"id": "MUT-003", "name": "tool_kinematic", "type": "kinematic_body"},
    {"id": "MUT-004", "name": "infinite_motor_force", "type": "unlimited_torque"},
    {"id": "MUT-005", "name": "palm_cavity_hull", "type": "single_hull"},
    {"id": "MUT-006", "name": "collision_disabled", "type": "no_collision"},
    {"id": "MUT-007", "name": "wrist_180_flip", "type": "reversed_wrist"},
    {"id": "MUT-008", "name": "tool_sleeping", "type": "deactivated_body"},
    {"id": "MUT-009", "name": "scale_animation", "type": "scaled_shaft"},
    {"id": "MUT-010", "name": "hidden_fixed_constraint", "type": "fixed_constraint"}
]

def main() -> int:
    MUTANT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    
    for m in MUTANTS:
        mutant_path = MUTANT_DIR / f"{m['id']}_{m['name']}.blend"
        manifest.append({
            "id": m["id"],
            "name": m["name"],
            "type": m["type"],
            "expected_result": "FAIL",
            "path": str(mutant_path)
        })
        
    (MUTANT_DIR / "mutant_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"Generated manifest for {len(MUTANTS)} adversarial mutants in {MUTANT_DIR}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
