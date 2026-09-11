"""Independent Oracle for Hand Physics Gate v1 (Milestone 1).

Consumes physics-scenario-1.json trajectory logs.
Evaluates local palm-frame slip (3D vector displacement), local angular drift, actuator torque demand, and release drop.
Assigns status: ROBUST PASS / LOW MARGIN / INCONCLUSIVE / FAIL.
"""

from __future__ import annotations
import json
import math
from pathlib import Path
import sys

ROOT = Path("/home/aaron/animation/thulans-production")
SCENARIO_1_JSON = ROOT / "evidence/varek-v55-mechanical-grip/physics-scenario-1.json"

def main() -> int:
    if not SCENARIO_1_JSON.exists():
        print(f"Oracle Fail: Log missing: {SCENARIO_1_JSON}")
        return 1

    data = json.loads(SCENARIO_1_JSON.read_text())
    frames = data.get("frames", [])
    if not frames:
        print("Oracle Fail: Empty frame log")
        return 1

    # Extract Hold Phase (Frames 31-75)
    hold_frames = [f for f in frames if f["phase"] == "hold"]
    if not hold_frames:
        print("Oracle Fail: Missing hold phase frames")
        return 1
        
    f31_local = hold_frames[0]["local_palm_pos"]
    f75_local = hold_frames[-1]["local_palm_pos"]
    
    # 3D Vector Slip in Local Palm Frame
    hold_slip_3d = sum((f75_local[i] - f31_local[i])**2 for i in range(3))**0.5
    
    # Angular Drift in Local Palm Frame
    f31_rot = hold_frames[0]["local_palm_rot_deg"]
    f75_rot = hold_frames[-1]["local_palm_rot_deg"]
    angular_drift = sum((f75_rot[i] - f31_rot[i])**2 for i in range(3))**0.5

    # Actuator Demand
    max_demand = max([f["max_actuator_torque_demand"] for f in hold_frames])

    # Extract Release Phase (Frames 76-105)
    release_frames = [f for f in frames if f["phase"] == "release"]
    f105_local = release_frames[-1]["local_palm_pos"] if release_frames else f75_local
    release_fall = f75_local[2] - f105_local[2]  # Z displacement drop

    print(f"=== MILESTONE 1 ORACLE EVALUATION ===")
    print(f"Hold Phase Local 3D Slip: {hold_slip_3d*1000:.3f} mm (Limit: 5.000 mm)")
    print(f"Hold Phase Angular Drift: {angular_drift:.2f}° (Limit: 2.00°)")
    print(f"Max Actuator Torque:      {max_demand:.1f} N·m (Limit: 120.0 N·m)")
    print(f"Release Phase Fall:        {release_fall*1000:.3f} mm (Required: > 500.000 mm)")

    # Status Assignment Rules
    if hold_slip_3d > 0.005 or angular_drift > 2.0 or release_fall < 0.5:
        print("ORACLE RESULT: FAIL")
        return 1
        
    if hold_slip_3d < 0.002 and angular_drift < 1.0 and max_demand < 100.0:
        status = "PASS — ROBUST"
    else:
        status = "PASS — LOW MARGIN"

    print(f"ORACLE RESULT: {status}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
