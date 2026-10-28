"""Independent Decoupling Oracle for Empty-Hand Scenarios A1 (Digit Closure) & A2 (Wrist Gimbal).

Consumes evidence/varek-v55-mechanical-grip/full-hand-diagnostic.json.
Evaluates:
1. Cryptographic Hash & Provenance Match against full-hand-readback.json.
2. Strict Cardinality & Non-NaN/Inf Finiteness Assertions.
3. Scenario A1 Aperture Directionality (Open -> Close -> Reopen).
4. Scenario A1 Exact Per-Joint Kinematic Limit Contracts.
5. Scenario A2-PITCH & A2-YAW Independent Gimbal Travel & Cross-Coupling Isolation.
"""

from __future__ import annotations
import json
import math
from pathlib import Path
import sys

ROOT = Path("/home/aaron/animation/thulans-production")
EVIDENCE_JSON = ROOT / "evidence/varek-v55-mechanical-grip/full-hand-diagnostic.json"
READBACK_JSON = ROOT / "evidence/varek-v55-mechanical-grip/full-hand-readback.json"

EXACT_JOINT_CONTRACTS = {
    "Palm_Plate_L->Digit1_Phalanx1_L": (-10.0, 90.0),
    "Digit1_Phalanx1_L->Digit1_Phalanx2_L": (0.0, 80.0),
    "Digit1_Phalanx2_L->Digit1_Phalanx3_L": (0.0, 80.0),
    "Palm_Plate_L->Digit2_Phalanx1_L": (-10.0, 90.0),
    "Digit2_Phalanx1_L->Digit2_Phalanx2_L": (0.0, 80.0),
    "Digit2_Phalanx2_L->Digit2_Phalanx3_L": (0.0, 80.0),
    "Palm_Plate_L->Digit3_Phalanx1_L": (-10.0, 90.0),
    "Digit3_Phalanx1_L->Digit3_Phalanx2_L": (0.0, 80.0),
    "Digit3_Phalanx2_L->Digit3_Phalanx3_L": (0.0, 80.0),
    "Palm_Plate_L->Thumb_Phalanx1_L": (-15.0, 90.0),
    "Thumb_Phalanx1_L->Thumb_Phalanx2_L": (0.0, 80.0)
}

WRIST_PITCH_KEY = "Palm_Plate_L->Gimbal_Yoke_Outer_L"
WRIST_YAW_KEY = "Gimbal_Yoke_Outer_L->Gimbal_Yoke_Inner_L"
WRIST_CONTRACTS = {
    WRIST_PITCH_KEY: (-45.0, 45.0),
    WRIST_YAW_KEY: (-30.0, 30.0)
}

EXPECTED_FINGERTIPS = {
    "Digit1_Phalanx3_L", "Digit2_Phalanx3_L", "Digit3_Phalanx3_L", "Thumb_Phalanx2_L"
}

def check_finite(val: float, name: str) -> bool:
    if not isinstance(val, (int, float)) or math.isnan(val) or math.isinf(val):
        print(f"   - FINITENESS ERROR: Non-finite value detected for {name}: {val}")
        return False
    return True

def main() -> int:
    if not EVIDENCE_JSON.exists() or not READBACK_JSON.exists():
        print("ORACLE RESULT: FAIL_UNIMPLEMENTED (required full-grip evidence is missing)")
        return 1

    ev = json.loads(EVIDENCE_JSON.read_text())
    rb = json.loads(READBACK_JSON.read_text())
    print(
        "FULL GRIP GATE: FAIL_UNIMPLEMENTED "
        "(empty-hand diagnostics do not test loaded acquisition, retention, or release)"
    )

    # Dynamically extract exact joint contracts from canonical readback
    exact_joint_contracts = {}
    for j_spec in rb.get("serialized_joints", []):
        j_key = f"{j_spec['parent']}->{j_spec['child']}"
        exact_joint_contracts[j_key] = tuple(j_spec["hinge_limits_deg"])

    wrist_pitch_contract = exact_joint_contracts.get(WRIST_PITCH_KEY, (-20.0, 45.0))
    wrist_yaw_contract = exact_joint_contracts.get(WRIST_YAW_KEY, (-15.0, 25.0))

    # =========================================================================
    # 1. Cryptographic Hash Binding Audit
    # =========================================================================
    ev_hash = ev.get("derivative_sha256")
    rb_hash = rb.get("derivative_sha256")
    print(f"1. Cryptographic Hash Audit: {ev_hash[:12] if ev_hash else 'None'} == {rb_hash[:12] if rb_hash else 'None'}")
    if not ev_hash or ev_hash != rb_hash:
        print("ORACLE RESULT: FAIL (Derivative hash mismatch between diagnostic and readback)")
        return 1

    # =========================================================================
    # 2. Strict Cardinality & Finiteness Assertions
    # =========================================================================
    a1_frames = ev.get("scenario_a1_digit_closure_frames", [])
    a2_pitch_frames = ev.get("scenario_a2_pitch_wrist_frames", [])
    a2_yaw_frames = ev.get("scenario_a2_yaw_wrist_frames", [])

    print("2. Telemetry Cardinality & Finiteness Assertions:")
    if len(a1_frames) != 60:
        print(f"ORACLE RESULT: FAIL (A1 frame count = {len(a1_frames)}, expected 60)")
        return 1
    if len(a2_pitch_frames) != 60:
        print(f"ORACLE RESULT: FAIL (A2 Pitch frame count = {len(a2_pitch_frames)}, expected 60)")
        return 1
    if len(a2_yaw_frames) != 60:
        print(f"ORACLE RESULT: FAIL (A2 Yaw frame count = {len(a2_yaw_frames)}, expected 60)")
        return 1

    # Finiteness check across all telemetry
    all_finite = True
    for frame_idx, f_data in enumerate(a1_frames):
        for j_name, angle in f_data.get("relative_signed_twist_deg", {}).items():
            all_finite = all_finite and check_finite(angle, f"A1 frame {frame_idx} {j_name}")
        for ft_name, dist in f_data.get("fingertip_radial_aperture_distances_m", f_data.get("fingertip_aperture_distances_m", {})).items():
            all_finite = all_finite and check_finite(dist, f"A1 frame {frame_idx} {ft_name}")

    for sub_name, frames in [("A2-Pitch", a2_pitch_frames), ("A2-Yaw", a2_yaw_frames)]:
        for frame_idx, f_data in enumerate(frames):
            for j_name, angle in f_data.get("signed_twist_deg", {}).items():
                all_finite = all_finite and check_finite(angle, f"{sub_name} frame {frame_idx} {j_name}")

    if not all_finite:
        print("ORACLE RESULT: FAIL (Telemetry contained NaN or Inf values)")
        return 1

    digit_joint_keys = [k for k in exact_joint_contracts if k not in (WRIST_PITCH_KEY, WRIST_YAW_KEY)]
    if set(a1_frames[0].get("relative_signed_twist_deg", {}).keys()) != set(digit_joint_keys):
        print("ORACLE RESULT: FAIL (A1 telemetry digit joint keys missing or mismatched)")
        return 1

    print("   - All frame counts (60/60/60), key sets, and numeric values strictly valid & finite.")

    # =========================================================================
    # 3. Scenario A1 Grasp Envelope Aperture Trajectory Audit (Radial Shaft Axis Distance)
    # =========================================================================
    print("3. Grasp Envelope Radial Aperture Trajectory Audit (Fingertip -> Shaft Axis Distance):")
    open_aperture = a1_frames[14].get("fingertip_radial_aperture_distances_m", a1_frames[14].get("fingertip_aperture_distances_m", {}))   # Frame 15 end of opening
    close_aperture = a1_frames[39].get("fingertip_radial_aperture_distances_m", a1_frames[39].get("fingertip_aperture_distances_m", {}))  # Frame 40 end of closing
    reopen_aperture = a1_frames[59].get("fingertip_radial_aperture_distances_m", a1_frames[59].get("fingertip_aperture_distances_m", {})) # Frame 60 end of reopening

    aperture_valid = True
    for ft_name in EXPECTED_FINGERTIPS:
        d_open = open_aperture[ft_name]
        d_close = close_aperture[ft_name]
        d_reopen = reopen_aperture[ft_name]
        
        close_delta_mm = (d_open - d_close) * 1000.0
        reopen_delta_mm = (d_reopen - d_close) * 1000.0
        
        print(f"   - {ft_name}: Open(f15)={d_open*1000:.1f}mm -> Close(f40)={d_close*1000:.1f}mm (Inward: {close_delta_mm:+.1f}mm) -> Reopen(f60)={d_reopen*1000:.1f}mm (Outward: {reopen_delta_mm:+.1f}mm)")
        
        if close_delta_mm < 5.0:
            print(f"   - ERROR: [A1-GRIP-TRAJECTORY] {ft_name} failed to contract by >= 5.0mm toward shaft axis during closure phase.")
            aperture_valid = False
        if reopen_delta_mm < 5.0:
            print(f"   - ERROR: [A1-D2-REOPEN-DIR] {ft_name} failed to expand by >= 5.0mm away from shaft axis during reopening phase.")
            aperture_valid = False

    if not aperture_valid:
        print("ORACLE RESULT: FAIL (Grasp envelope radial aperture failed open->close->reopen trajectory assertion)")
        return 1

    # =========================================================================
    # 4. Scenario A1 Exact Per-Joint Kinematic Limit Contract Audit
    # =========================================================================
    print("4. Exact Per-Joint Kinematic Limit Contract Audit (Synchronized with Readback):")
    limit_violations = 0
    for j_name in digit_joint_keys:
        contract_min, contract_max = exact_joint_contracts[j_name]
        angles = [f["relative_signed_twist_deg"][j_name] for f in a1_frames]
        min_ang, max_ang = min(angles), max(angles)
        print(f"   - {j_name}: Observed [{min_ang:+.2f}°, {max_ang:+.2f}°] | Allowed [{contract_min:+.1f}°, {contract_max:+.1f}°]")
        if min_ang < (contract_min - 0.5) or max_ang > (contract_max + 0.5):
            print(f"   - CONTRACT VIOLATION: {j_name} exceeded limit contract [{contract_min}°, {contract_max}°]")
            limit_violations += 1

    if limit_violations > 0:
        print(f"ORACLE RESULT: FAIL ({limit_violations} per-joint limit contract violations in Scenario A1)")
        return 1

    # =========================================================================
    # 5. Scenario A2 Wrist Pitch & Yaw Independent Travel & Isolation Audit
    # =========================================================================
    print("5. Scenario A2 Independent Gimbal Travel & Cross-Coupling Audit:")
    
    # Audit A2-PITCH
    pitch_angles = [f["signed_twist_deg"][WRIST_PITCH_KEY] for f in a2_pitch_frames]
    pitch_yaw_coupled = [f["signed_twist_deg"][WRIST_YAW_KEY] for f in a2_pitch_frames]
    p_min, p_max = min(pitch_angles), max(pitch_angles)
    py_coupled_range = max(pitch_yaw_coupled) - min(pitch_yaw_coupled)
    
    # Check neutral digits in A2-PITCH
    max_digit_pitch_travel = 0.0
    for j_name in digit_joint_keys:
        d_angles = [f["signed_twist_deg"][j_name] for f in a2_pitch_frames]
        d_range = max(d_angles) - min(d_angles)
        if d_range > max_digit_pitch_travel:
            max_digit_pitch_travel = d_range

    print(f"   - A2-PITCH Run: Pitch Travel = [{p_min:+.2f}°, {p_max:+.2f}°] (Span: {p_max-p_min:.2f}°) | Contract [{wrist_pitch_contract[0]:+.1f}°, {wrist_pitch_contract[1]:+.1f}°]")
    print(f"   - A2-PITCH Run: Yaw Cross-Coupling = {py_coupled_range:.2f}° | Max Digit Motion = {max_digit_pitch_travel:.2f}°")

    if (p_max - p_min) < 5.0:
        print("ORACLE RESULT: FAIL (A2-PITCH failed to produce >= 5.0° pitch travel)")
        return 1
    if p_min < (wrist_pitch_contract[0] - 0.5) or p_max > (wrist_pitch_contract[1] + 0.5):
        print("ORACLE RESULT: FAIL (A2-PITCH exceeded physical wrist pitch contract limits)")
        return 1
    if py_coupled_range > 1.0:
        print(f"ORACLE RESULT: FAIL (A2-PITCH excessive yaw coupling: {py_coupled_range:.2f}° > 1.0°)")
        return 1
    if max_digit_pitch_travel > 1.0:
        print(f"ORACLE RESULT: FAIL (A2-PITCH digits not neutralized: max digit travel {max_digit_pitch_travel:.2f}° > 1.0°)")
        return 1

    # Audit A2-YAW
    yaw_angles = [f["signed_twist_deg"][WRIST_YAW_KEY] for f in a2_yaw_frames]
    yaw_pitch_coupled = [f["signed_twist_deg"][WRIST_PITCH_KEY] for f in a2_yaw_frames]
    y_min, y_max = min(yaw_angles), max(yaw_angles)
    yp_coupled_range = max(yaw_pitch_coupled) - min(yaw_pitch_coupled)

    # Check neutral digits in A2-YAW
    max_digit_yaw_travel = 0.0
    for j_name in digit_joint_keys:
        d_angles = [f["signed_twist_deg"][j_name] for f in a2_yaw_frames]
        d_range = max(d_angles) - min(d_angles)
        if d_range > max_digit_yaw_travel:
            max_digit_yaw_travel = d_range

    print(f"   - A2-YAW Run: Yaw Travel = [{y_min:+.2f}°, {y_max:+.2f}°] (Span: {y_max-y_min:.2f}°) | Contract [{wrist_yaw_contract[0]:+.1f}°, {wrist_yaw_contract[1]:+.1f}°]")
    print(f"   - A2-YAW Run: Pitch Cross-Coupling = {yp_coupled_range:.2f}° | Max Digit Motion = {max_digit_yaw_travel:.2f}°")

    if (y_max - y_min) < 5.0:
        print("ORACLE RESULT: FAIL (A2-YAW failed to produce >= 5.0° yaw travel)")
        return 1
    if y_min < (wrist_yaw_contract[0] - 0.5) or y_max > (wrist_yaw_contract[1] + 0.5):
        print("ORACLE RESULT: FAIL (A2-YAW exceeded physical wrist yaw contract limits)")
        return 1
    if yp_coupled_range > 1.0:
        print(f"ORACLE RESULT: FAIL (A2-YAW excessive pitch coupling: {yp_coupled_range:.2f}° > 1.0°)")
        return 1
    if max_digit_yaw_travel > 1.0:
        print(f"ORACLE RESULT: FAIL (A2-YAW digits not neutralized: max digit travel {max_digit_yaw_travel:.2f}° > 1.0°)")
        return 1

    print("\nDIAGNOSTIC RESULT: PASS — EMPTY-HAND SCENARIOS A1, A2-PITCH & A2-YAW VERIFIED")
    print(
        "ORACLE RESULT: FAIL_UNIMPLEMENTED "
        "(loaded grip, disturbance, and release scenarios are not implemented)"
    )
    return 1

if __name__ == '__main__':
    sys.exit(main())
