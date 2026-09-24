"""Independent Oracle for Single-Joint 4-Part Evidence Suite.

Consumes evidence/varek-v55-mechanical-grip/single-joint-evidence.json.
Evaluates:
1. Zero-load motor arc completion.
2. Limit enforcement (-10° to +90°).
3. Loaded response change under 10 kg mass.
4. Disabled motor negative control (motion stops).
5. Axis alignment audit (|dot(Hinge_Z, Motor_X)| >= 0.999).
"""

from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_JSON = ROOT / "evidence/varek-v55-mechanical-grip/single-joint-evidence.json"
READBACK_JSON = ROOT / "evidence/varek-v55-mechanical-grip/single-joint-readback.json"

def main() -> int:
    if not EVIDENCE_JSON.exists() or not READBACK_JSON.exists():
        print("Oracle Fail: Required evidence or readback JSON missing.")
        return 1

    ev = json.loads(EVIDENCE_JSON.read_text())
    rb = json.loads(READBACK_JSON.read_text())

    print("ORACLE STATUS: FAIL_UNIMPLEMENTED")
    print("The declared loaded-response and disabled-motor causality checks are not implemented.")

    # These diagnostics are retained because they expose useful measurements,
    # but they are not the complete five-part oracle declared above.
    # In particular, loaded response and motor-disable causality are not yet
    # validated. Partial diagnostics must never authorize a PASS.

    # 1. Axis Alignment Audit
    dot = rb.get("constraint_alignment_dot", 0.0)
    print(f"1. Axis Alignment Audit: |dot(Hinge_Z, Motor_X)| = {dot:.6f}")
    if dot < 0.999:
        print("DIAGNOSTIC RESULT: FAIL (Axis misalignment)")
        return 1

    # 2. Unloaded Arc & Limits Check
    p1_frames = ev.get("part1_unloaded_arc", [])
    angles = [f["relative_angle_deg"] for f in p1_frames]
    min_ang, max_ang = min(angles), max(angles)
    print(f"2. Unloaded Arc: [{min_ang:.2f}°, {max_ang:.2f}°] (Limits: [-10°, 90°])")
    if min_ang < -10.5 or max_ang > 90.5:
        print("DIAGNOSTIC RESULT: FAIL (Joint limit exceeded)")
        return 1

    # 3. Disabled Motor Negative Control Check
    p4_frames = ev.get("part4_disabled_motor_control", [])
    p4_motion = max([f["relative_angle_deg"] for f in p4_frames]) - min([f["relative_angle_deg"] for f in p4_frames])
    print(f"3. Disabled Motor Motion Range: {p4_motion:.2f}° (Required: ~0.00°)")

    print("ORACLE RESULT: FAIL_UNIMPLEMENTED")
    print("Missing checks: loaded response and disabled-motor causality.")
    return 1

if __name__ == '__main__':
    sys.exit(main())
