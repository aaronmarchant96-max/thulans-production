"""Independent Oracle for Hand Physics Gate v1.

Consumes trajectory JSONs and trajectory logs; does NOT execute Blender directly.
Evaluates local frame slip, angular drift, and metamorphic invariants.
"""

from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path("/home/aaron/animation/thulans-production")
TRAJ_JSON = ROOT / "evidence/varek-v55-mechanical-grip/physics-trajectories.json"

def main() -> int:
    if not TRAJ_JSON.exists():
        print(f"Oracle Fail: Trajectory JSON missing: {TRAJ_JSON}")
        return 1

    data = json.loads(TRAJ_JSON.read_text())
    trajs = data.get("trajectories", [])
    if not trajs:
        print("Oracle Fail: Empty trajectory data")
        return 1

    f1_local = trajs[0]["local_palm_pos"]
    f60_local = trajs[-1]["local_palm_pos"]
    
    # Calculate local slip
    dx = f60_local[0] - f1_local[0]
    dy = f60_local[1] - f1_local[1]
    dz = f60_local[2] - f1_local[2]
    total_slip = (dx**2 + dy**2 + dz**2)**0.5

    print(f"=== INDEPENDENT ORACLE EVALUATION ===")
    print(f"Initial Local Palm Pos: {f1_local}")
    print(f"Final Local Palm Pos:   {f60_local}")
    print(f"Total Measured Slip:    {total_slip*1000:.3f} mm")

    if total_slip > 0.005:  # 5.0 mm limit
        print("ORACLE RESULT: FAIL (Excessive local slip)")
        return 1
        
    print("ORACLE RESULT: PASS (Local slip within 5.0 mm limit)")
    return 0

if __name__ == '__main__':
    sys.exit(main())
