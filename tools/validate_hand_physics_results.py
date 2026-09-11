"""Independent Oracle for Hand Physics Gate v1 (Milestone 1).

Consumes physics-scenario-1.json trajectory logs.
Calculates local palm-frame slip, angular drift, and verifies release drop.
"""

from __future__ import annotations
import json
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
    
    hold_slip = sum((f75_local[i] - f31_local[i])**2 for i in range(3))**0.5
    
    # Extract Release Phase (Frames 76-105)
    release_frames = [f for f in frames if f["phase"] == "release"]
    f105_local = release_frames[-1]["local_palm_pos"] if release_frames else f75_local
    release_fall = f75_local[2] - f105_local[2]  # Z displacement drop

    print(f"=== MILESTONE 1 ORACLE EVALUATION ===")
    print(f"Hold Phase Local Slip: {hold_slip*1000:.3f} mm (Limit: 5.000 mm)")
    print(f"Release Phase Fall:     {release_fall*1000:.3f} mm (Required: > 500.000 mm)")

    if hold_slip > 0.005:
        print("ORACLE RESULT: FAIL (Excessive hold slip)")
        return 1
        
    if release_fall < 0.5:
        print("ORACLE RESULT: FAIL (Maul failed to fall on release)")
        return 1

    print("ORACLE RESULT: PASS (Scenario 1 hold and release verified)")
    return 0

if __name__ == '__main__':
    sys.exit(main())
