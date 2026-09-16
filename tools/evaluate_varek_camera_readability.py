from __future__ import annotations
import math
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path("/home/aaron/animation/thulans-production")
ANIM_BLEND = ROOT / "blender/renders/varek_load_struggle_blocking.blend"
OUT_DIR = Path("/home/aaron/.gemini/antigravity/brain/c8d29359-41cb-4a73-aa95-01cade4cb5b7")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Explicit 9-landmark set specifying exact bone head positions
LANDMARKS = [
    "head", "hand.L", "upper_arm.L", "upper_arm.R",
    "pelvis", "thigh.L", "thigh.R", "foot.L", "foot.R"
]

CRITICAL_SAFE_LANDMARKS = ["head", "hand.L", "pelvis", "foot.L", "foot.R"]

FOCAL_LENGTHS = [40.0, 46.0, 52.0]
TARGET_FRAMES = [1, 32, 40, 50, 65, 76, 90, 120]
EPS = 1e-6

def get_bone_world_head_pos(arm_obj, bone_name):
    """Calculates exact world-space position of bone head landmark."""
    pbone = arm_obj.pose.bones.get(bone_name)
    if not pbone:
        return Vector((0, 0, 0))
    chain = []
    curr = pbone
    while curr:
        chain.append(curr)
        curr = curr.parent
    chain.reverse()
    
    mat = arm_obj.matrix_world.copy()
    for b in chain:
        rest_mat = arm_obj.data.bones[b.name].matrix_local
        if b.parent:
            parent_rest = arm_obj.data.bones[b.parent.name].matrix_local
            rest_mat = parent_rest.inverted() @ rest_mat
        mat = mat @ rest_mat @ b.matrix_basis
    return mat.to_translation()

def evaluate_camera(lens_val):
    print(f"\n=======================================================")
    print(f"  EVALUATING CAMERA FOCAL LENGTH: {lens_val:.1f} mm")
    print(f"=======================================================")

    bpy.ops.wm.open_mainfile(filepath=str(ANIM_BLEND))
    scene = bpy.context.scene
    arm_obj = bpy.data.objects.get("Varek simple articulation")
    cam_obj = scene.camera

    if not arm_obj or not cam_obj:
        print("HARD FAIL: Armature or Camera missing.")
        return None

    # Set focal length candidate
    cam_obj.data.lens = lens_val

    # Store projected normalized camera coordinates (0.0 .. 1.0)
    frame_coords = {}
    safe_frame_pass = True
    min_safe = 0.03
    max_safe = 0.97

    for f in TARGET_FRAMES:
        scene.frame_set(f)
        coords = {}
        for bname in LANDMARKS:
            wpos = get_bone_world_head_pos(arm_obj, bname)
            cpos = world_to_camera_view(scene, cam_obj, wpos)
            coords[bname] = cpos

            # Camera Safe-Frame Bounds Assertion for critical landmarks
            if bname in CRITICAL_SAFE_LANDMARKS:
                if not (min_safe <= cpos.x <= max_safe and min_safe <= cpos.y <= max_safe):
                    safe_frame_pass = False
                    print(f"  [SAFE-FRAME WARN] Frame F{f:03d} landmark '{bname}' near edge: ({cpos.x:.3f}, {cpos.y:.3f})")
        frame_coords[f] = coords

    # --- METRIC 1: Initial Causal Propagation Ratio (F032 -> F040) ---
    hand_f32 = frame_coords[32]["hand.L"]
    hand_f40 = frame_coords[40]["hand.L"]
    pelvis_f32 = frame_coords[32]["pelvis"]
    pelvis_f40 = frame_coords[40]["pelvis"]

    hand_disp = (Vector((hand_f40.x, hand_f40.y)) - Vector((hand_f32.x, hand_f32.y))).length
    pelvis_disp = (Vector((pelvis_f40.x, pelvis_f40.y)) - Vector((pelvis_f32.x, pelvis_f32.y))).length
    
    # Denominator guard to avoid division by near-zero pelvis displacement
    prop_ratio = hand_disp / max(pelvis_disp, EPS)
    prop_pass = prop_ratio >= 1.50

    # --- METRIC 2: Boot Skid Screen Displacement (F040 -> F050) ---
    foot_f40 = frame_coords[40]["foot.L"]
    foot_f50 = frame_coords[50]["foot.L"]

    skid_disp_x = abs(foot_f50.x - foot_f40.x) # Screen width fraction
    skid_disp_y = abs(foot_f50.y - foot_f40.y) # Screen height contamination
    skid_ratio = skid_disp_x / max(skid_disp_y, EPS)
    skid_pass = skid_disp_x >= 0.025 and skid_ratio >= 1.50

    # --- METRIC 3: Landmark Pose Separation ---
    def calc_pose_sep(f_a, f_b):
        total_d = 0.0
        count = 0
        for b in LANDMARKS:
            ca = frame_coords[f_a][b]
            cb = frame_coords[f_b][b]
            d = (Vector((ca.x, ca.y)) - Vector((cb.x, cb.y))).length
            total_d += d
            count += 1
        return total_d / max(count, 1)

    sep_001_065 = calc_pose_sep(1, 65)
    sep_065_120 = calc_pose_sep(65, 120)
    sep_001_120 = calc_pose_sep(1, 120)
    sep_pass = sep_001_065 > 0.05 and sep_065_120 > 0.03 and sep_001_120 > 0.02

    print(f"1. Causal Propagation Ratio (F32->F40):     {prop_ratio:.2f} ({'PASS' if prop_pass else 'FAIL'})")
    print(f"   [Raw Displacements] Hand: {hand_disp:.4f} | Pelvis: {pelvis_disp:.4f}")
    print(f"2. Boot Skid Screen Width Fraction (F40->F50): {skid_disp_x*100:.2f}% ({'PASS' if skid_pass else 'FAIL'})")
    print(f"   Boot Skid Vertical Contamination:          {skid_disp_y*100:.2f}% (Horizontal/Vertical Ratio: {skid_ratio:.2f})")
    print(f"3. Pose Separation (F001 vs F065):           {sep_001_065:.3f} ({'PASS' if sep_pass else 'FAIL'})")
    print(f"   Pose Separation (F065 vs F120):           {sep_065_120:.3f}")
    print(f"   Pose Separation (F001 vs F120):           {sep_001_120:.3f}")
    print(f"4. Camera Safe-Frame Bounds (0.03-0.97):     {'PASS' if safe_frame_pass else 'WARN'}")

    # Render diagnostic candidate stills
    lens_tag = f"{int(lens_val)}mm"
    for f in TARGET_FRAMES:
        scene.frame_set(f)
        out_png = OUT_DIR / f"precheck_cam_{lens_tag}_f{f:03d}.png"
        scene.render.filepath = str(out_png)
        bpy.ops.render.render(write_still=True)

    res_data = {
        "lens_mm": lens_val,
        "raw_hand_displacement": round(hand_disp, 4),
        "raw_pelvis_displacement": round(pelvis_disp, 4),
        "absolute_causal_delta": round(hand_disp - pelvis_disp, 4),
        "prop_ratio": round(prop_ratio, 3),
        "skid_screen_x_pct": round(skid_disp_x * 100, 2),
        "skid_screen_y_pct": round(skid_disp_y * 100, 2),
        "skid_ratio_x_y": round(skid_ratio, 2),
        "sep_001_065": round(sep_001_065, 3),
        "sep_065_120": round(sep_065_120, 3),
        "sep_001_120": round(sep_001_120, 3),
        "safe_frame_pass": safe_frame_pass,
        "overall_pass": prop_pass and skid_pass and sep_pass and safe_frame_pass
    }
    return res_data

def main():
    results = {}
    for lens in FOCAL_LENGTHS:
        res = evaluate_camera(lens)
        if res:
            results[f"{int(lens)}mm"] = res

    # Save summary JSON report with raw metrics and safe-frame dispositions
    report_file = OUT_DIR / "camera_readability_precheck_summary.json"
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)

    print("\n=======================================================")
    print(f"  PRECHECK QA COMPLETE. SUMMARY SAVED TO: {report_file}")
    print("=======================================================\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
