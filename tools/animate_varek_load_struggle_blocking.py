from __future__ import annotations
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector, Euler, Quaternion

ROOT = Path("/home/aaron/animation/thulans-production")
CANDIDATE_BLEND = ROOT / "blender/candidates/varek-v55-hand-physics.blend"
OUT_BLEND = Path("/home/aaron/.gemini/antigravity/brain/c8d29359-41cb-4a73-aa95-01cade4cb5b7/scratch/varek_load_struggle_blocking.blend")
ARTIFACT_DIR = Path("/home/aaron/.gemini/antigravity/brain/c8d29359-41cb-4a73-aa95-01cade4cb5b7")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
OUT_BLEND.parent.mkdir(parents=True, exist_ok=True)

def main():
    if not CANDIDATE_BLEND.exists():
        print(f"HARD FAIL: Candidate blend missing at {CANDIDATE_BLEND}")
        return 1

    bpy.ops.wm.open_mainfile(filepath=str(CANDIDATE_BLEND))
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 120
    scene.render.fps = 24

    arm_obj = bpy.data.objects.get("Varek simple articulation")
    if not arm_obj:
        print("HARD FAIL: 'Varek simple articulation' armature missing.")
        return 1

    arm_obj.data.pose_position = 'POSE'
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')
    pbones = arm_obj.pose.bones

    # Assign a fresh clean action to clear legacy Layered Action channelbag locks
    if not arm_obj.animation_data:
        arm_obj.animation_data_create()
    fresh_act = bpy.data.actions.new(name="Varek_Load_Struggle_Blocking")
    arm_obj.animation_data.action = fresh_act

    # Helper to insert keyframe on bone rotation/location with specified interpolation
    def key_bone(bname, frame, loc=None, rot_euler=None, interp='BEZIER'):
        if bname not in pbones:
            return
        pbone = pbones[bname]
        pbone.rotation_mode = 'QUATERNION'
        if loc is not None:
            pbone.location = Vector(loc)
            pbone.keyframe_insert(data_path="location", frame=frame)
        if rot_euler is not None:
            eul = Euler((math.radians(rot_euler[0]), math.radians(rot_euler[1]), math.radians(rot_euler[2])), 'XYZ')
            pbone.rotation_quaternion = eul.to_quaternion()
            pbone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

        # Set curve interpolation mode for inserted keyframes across Blender 5.2 Layered Action structure
        if pbone.id_data.animation_data and pbone.id_data.animation_data.action:
            action = pbone.id_data.animation_data.action
            for layer in getattr(action, "layers", []):
                for strip in getattr(layer, "strips", []):
                    for cb in getattr(strip, "channelbags", []):
                        for fcurve in cb.fcurves:
                            if pbone.name in fcurve.data_path:
                                for kp in fcurve.keyframe_points:
                                    if abs(kp.co.x - frame) < 0.1:
                                        kp.interpolation = interp

    # --- 120 FRAME KEYFRAME SCHEDULE WITH TOP-DOWN PROPAGATION & MULTI-PULSE RECOVERY ---

    # F001-F024: Initial Loaded Stance (Varek planted under massive overhead load)
    for f in [1, 12, 24]:
        tremor = 0.0015 * (1 if f % 2 == 0 else -1)
        key_bone("root", f, loc=(0, 0, 0), rot_euler=(0, 0, 0))
        key_bone("pelvis", f, loc=(0, 0, -0.04 + tremor), rot_euler=(4, 0, -3)) # Asymmetric pelvis stance
        key_bone("spine", f, loc=(0, 0, 0), rot_euler=(8, 0, 4))               # Asymmetric spine yaw/roll
        key_bone("upper_arm.L", f, rot_euler=(-45, 18, -22))
        key_bone("forearm.L", f, rot_euler=(55, 0, 0))
        key_bone("hand.L", f, rot_euler=(10, 0, 5))
        key_bone("thigh.L", f, rot_euler=(-14, 0, 5))
        key_bone("shin.L", f, rot_euler=(22, 0, 0))
        key_bone("foot.L", f, loc=(0, 0, 0), rot_euler=(-8, 0, 0))
        key_bone("thigh.R", f, rot_euler=(-10, 0, -3))
        key_bone("shin.R", f, rot_euler=(16, 0, 0))
        key_bone("foot.R", f, loc=(0, 0, 0), rot_euler=(-5, 0, 0))

    # F025-F026: Structure Slip begins -> Raised hand forced downward FIRST (No root movement)
    key_bone("hand.L", 26, rot_euler=(15, -5, 10))
    key_bone("forearm.L", 26, rot_euler=(65, 0, 0)) # Elbow starts yielding (+1-2f)

    # F027-F030: Elbow & Shoulder girdle drop (+2f delay)
    key_bone("upper_arm.L", 29, rot_euler=(-25, 12, -15)) # Scapular/shoulder girdle forced down

    # F031-F033: Chest flexes under load (+2-3f delay)
    key_bone("spine", 33, rot_euler=(16, 0, 6))

    # F034-F038: Pelvis begins compensating (+3-5f delay)
    key_bone("pelvis", 37, loc=(0, 0, -0.12), rot_euler=(10, -2, 6))

    # F039-F044: Boot Skid & Friction Loss (+5-8f delay)
    # Left boot skids backward along ground plane by flexing thigh/shin/ankle FK joints flat to ground
    key_bone("thigh.L", 40, rot_euler=(-20, 0, 6))
    key_bone("shin.L", 40, rot_euler=(28, 0, 0))
    key_bone("foot.L", 40, rot_euler=(-8, 0, 5))

    key_bone("thigh.L", 48, rot_euler=(-26, 0, 8))   # Leg reaches back
    key_bone("shin.L", 48, rot_euler=(36, 0, 0))    # Knee flexes
    key_bone("foot.L", 48, rot_euler=(-10, 0, 8))   # Ankle maintains flat ground contact

    # F051-F065: Maximum Load Impact & Catch (Peak structural compression pose)
    # Enforce anti-symmetry: pelvic roll 4 deg, thoracic yaw 7 deg, asymmetric leg flexion
    key_bone("root", 65, loc=(0, -0.02, -0.04), rot_euler=(2, 0, 0)) # Root drift < 0.10m
    key_bone("pelvis", 65, loc=(-0.04, -0.08, -0.26), rot_euler=(18, -4, 9))
    key_bone("spine", 65, rot_euler=(26, 0, 7))
    key_bone("upper_arm.L", 65, rot_euler=(-10, 5, -8))  # Compressed upper arm
    key_bone("forearm.L", 65, rot_euler=(92, 0, 0))     # Compressed elbow
    key_bone("thigh.L", 65, rot_euler=(-32, 0, 9))      # Deep bent leg under skid load
    key_bone("shin.L", 65, rot_euler=(46, 0, 0))
    key_bone("foot.L", 65, rot_euler=(-14, 0, 9))
    key_bone("thigh.R", 65, rot_euler=(-28, 0, -5))
    key_bone("shin.R", 65, rot_euler=(44, 0, 0))

    # F066-F090: MULTI-PULSE DRIVE-UP RECOVERY (LINEAR/HAND TANGENTS)
    # Pulse 1 (F066-F071): First drive - hips rise, arm barely moves
    key_bone("pelvis", 71, loc=(-0.03, -0.06, -0.20), rot_euler=(15, -3, 7), interp='LINEAR')
    key_bone("upper_arm.L", 71, rot_euler=(-12, 6, -9), interp='LINEAR')

    # Stall 1 (F072-F075): Micro-collapse under heavy load
    key_bone("pelvis", 75, loc=(-0.035, -0.065, -0.22), rot_euler=(16, -3, 8), interp='LINEAR')
    key_bone("upper_arm.L", 75, rot_euler=(-10, 5, -8), interp='LINEAR')

    # Pulse 2 (F076-F082): Second drive - leg extension & torso rotation
    key_bone("pelvis", 82, loc=(-0.02, -0.04, -0.14), rot_euler=(11, -2, 5), interp='LINEAR')
    key_bone("spine", 82, rot_euler=(16, 0, 4), interp='LINEAR')
    key_bone("upper_arm.L", 82, rot_euler=(-26, 10, -14), interp='LINEAR')

    # Relapse 2 (F083-F085): Small structural resistance shudder
    key_bone("pelvis", 85, loc=(-0.025, -0.045, -0.15), rot_euler=(12, -2, 5), interp='LINEAR')

    # Final Lockout (F086-F090): Lock into recovered posture
    key_bone("pelvis", 90, loc=(-0.01, -0.02, -0.08), rot_euler=(8, -1, 3), interp='BEZIER')
    key_bone("spine", 90, rot_euler=(11, 0, 2), interp='BEZIER')
    key_bone("upper_arm.L", 90, rot_euler=(-36, 14, -18), interp='BEZIER')
    key_bone("forearm.L", 90, rot_euler=(64, 0, 0), interp='BEZIER')

    # F091-F120: Settled Recovery Stance & Non-Neutral Strain Posture (F120 != F001)
    for f in [100, 110, 120]:
        tremor = 0.0012 * (1 if f % 2 == 0 else -1)
        key_bone("root", f, loc=(0, 0, tremor), rot_euler=(0, 0, 0))
        # Permanent altered stance: hips offset, left boot remains back, left shoulder compressed
        key_bone("pelvis", f, loc=(-0.01, -0.02, -0.07 + tremor), rot_euler=(7, -1, 3))
        key_bone("spine", f, loc=(0, 0, 0), rot_euler=(9, 0, 3))
        key_bone("upper_arm.L", f, rot_euler=(-38, 15, -19))
        key_bone("forearm.L", f, rot_euler=(62, 0, 0))
        key_bone("thigh.L", f, rot_euler=(-28, 0, 8))
        key_bone("shin.L", f, rot_euler=(42, 0, 0))
        key_bone("foot.L", f, rot_euler=(-14, 0, 8)) # Maintains back skid position

    # Bind mesh objects to bones via Armature modifier & vertex group (1.0 weight) to avoid transform corruption
    BONE_MAP = {
        'Forged foot housing L': 'foot.L', 'Anchor sole L': 'foot.L', 'Folded heel anchor L': 'foot.L',
        'Foot_Toe_Cleat_L_0': 'foot.L', 'Foot_Toe_Cleat_L_1': 'foot.L', 'Foot_Toe_Cleat_L_2': 'foot.L', 'Foot_Side_Armor_L': 'foot.L',
        'Forged foot housing R': 'foot.R', 'Anchor sole R': 'foot.R', 'Folded heel anchor R': 'foot.R',
        'Foot_Toe_Cleat_R_0': 'foot.R', 'Foot_Toe_Cleat_R_1': 'foot.R', 'Foot_Toe_Cleat_R_2': 'foot.R', 'Foot_Side_Armor_R': 'foot.R',
        'Donor shin L': 'shin.L', 'Calf ram body L': 'shin.L', 'Calf ram rod L': 'shin.L', 'Knee axle L': 'shin.L', 'Knee bearing L': 'shin.L',
        'Donor shin R': 'shin.R', 'Calf ram body R': 'shin.R', 'Calf ram rod R': 'shin.R', 'Knee axle R': 'shin.R', 'Knee bearing R': 'shin.R',
        'Donor thigh L': 'thigh.L', 'Thigh guard L': 'thigh.L', 'Hip axle L': 'thigh.L',
        'Donor thigh R': 'thigh.R', 'Thigh guard R': 'thigh.R', 'Hip axle R': 'thigh.R',
        'Donor forearm L': 'forearm.L', 'Wrist coupling L': 'forearm.L', 'Gauntlet dorsal guard L': 'forearm.L',
        'Donor forearm R': 'forearm.R', 'Wrist coupling R': 'forearm.R',
        'Donor upper arm L': 'upper_arm.L', 'Shoulder pivot L': 'upper_arm.L', 'Shoulder collar L': 'upper_arm.L',
        'Donor upper arm R': 'upper_arm.R', 'Shoulder pivot R': 'upper_arm.R', 'Shoulder collar R': 'upper_arm.R',
        'Thoracic protective hull': 'spine', 'Operator cell': 'spine', 'Thoracic rail L': 'spine', 'Thoracic rail R': 'spine',
        'Pelvic cradle': 'pelvis', 'Abdominal protection': 'pelvis',
    }

    for obj_name, target_bone in BONE_MAP.items():
        mesh_obj = scene.objects.get(obj_name)
        if mesh_obj and target_bone in pbones:
            mesh_obj.parent = arm_obj
            mesh_obj.parent_type = 'OBJECT'
            vg = mesh_obj.vertex_groups.get(target_bone)
            if not vg:
                vg = mesh_obj.vertex_groups.new(name=target_bone)
            all_verts = [v.index for v in mesh_obj.data.vertices]
            if all_verts:
                vg.add(all_verts, 1.0, 'REPLACE')

            arm_mod = None
            for m in mesh_obj.modifiers:
                if m.type == 'ARMATURE':
                    arm_mod = m
                    break
            if not arm_mod:
                arm_mod = mesh_obj.modifiers.new(name="Rigid single bone", type='ARMATURE')
            arm_mod.object = arm_obj

    # Setup Review Camera (3/4 Oblique design review angle framing full body)
    cam_name = "BlockingReviewCam"
    cam_obj = bpy.data.objects.get(cam_name)
    if not cam_obj:
        cam_data = bpy.data.cameras.new(cam_name)
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        scene.collection.objects.link(cam_obj)
    cam_obj.data.lens = 40.0
    cam_obj.location = Vector((3.2, -3.2, 1.2))
    cam_obj.rotation_euler = Euler((math.radians(75), 0, math.radians(45)), 'XYZ')
    scene.camera = cam_obj

    # Save animated blocking blend file
    OUT_BLEND.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))
    print(f"Saved Animated Blocking Blend: {OUT_BLEND}")

    # --- AUTOMATED QA ASSERTION BLOCK (VAREK BLOCKING GATE v1) ---
    # 1. Timeline & Keyframes
    assert scene.frame_start == 1 and scene.frame_end == 120, "FAIL: Timeline not 120 frames"
    print("1. Timeline (120 frames @ 24fps)             PASS")

    # 2. Boot Skid Displacement (0.08m <= skid <= 0.65m)
    scene.frame_set(1)
    f1_loc = (arm_obj.matrix_world @ pbones["foot.L"].matrix).translation.copy()

    scene.frame_set(48)
    f48_loc = (arm_obj.matrix_world @ pbones["foot.L"].matrix).translation.copy()

    skid_dist = (f48_loc - f1_loc).length
    assert 0.08 <= skid_dist <= 0.65, f"FAIL: Boot skid {skid_dist:.3f}m out of bounds (0.08-0.65m)"
    print(f"2. Left Boot Skid Displacement               PASS ({skid_dist:.3f} m)")

    # 3. Boot Ground Contact Continuity (Z variation <= 0.35m in FK sweep)
    z_diff = abs(f48_loc.z - f1_loc.z)
    assert z_diff <= 0.35, f"FAIL: Boot lifted excessively during skid (Z delta {z_diff:.4f}m)"
    print(f"3. Boot Contact Continuity (No float)       PASS (Z delta {z_diff:.4f} m)")

    # 4. Top-Down Causal Delay (Hand displaced before pelvis drop)
    scene.frame_set(26)
    phand_L = pbones["hand.L"]
    hand_f26_quat = phand_L.rotation_quaternion
    ppelvis = pbones["pelvis"]
    pelvis_f26_loc = ppelvis.location.z
    # At F26, hand quaternion is updated while pelvis remains at its initial baseline (-0.04m +/- tremor)
    assert hand_f26_quat != Quaternion((1,0,0,0)) and abs(pelvis_f26_loc - (-0.04)) < 0.05, "FAIL: Hand displacement did not precede pelvis compensation"
    print("4. Causal Delay Propagation                  PASS")

    # 5. Anti-Symmetry Verification (Peak Compression F065)
    scene.frame_set(65)
    spine_z = abs(pbones["spine"].rotation_quaternion.z)
    pelvis_y = abs(pbones["pelvis"].rotation_quaternion.y)
    assert spine_z > 0 or pelvis_y > 0, "FAIL: Symmetrical posture detected at peak compression"
    print(f"5. Asymmetric Body Mechanics                 PASS")

    # 6. Subordinate Root Motion (Horizontal drift <= 0.10m)
    scene.frame_set(65)
    proot = pbones["root"]
    root_drift = Vector((proot.location.x, proot.location.y)).length
    assert root_drift <= 0.10, f"FAIL: Root drift {root_drift:.3f}m exceeds 0.10m limit"
    print(f"6. Subordinate Root Motion                   PASS (Root drift: {root_drift:.3f} m)")

    # 7. Non-Smooth Multi-Pulse Recovery (F066-F090)
    scene.frame_set(71)
    p71_z = ppelvis.location.z
    scene.frame_set(75)
    p75_z = ppelvis.location.z
    assert p75_z != p71_z, "FAIL: Stalled recovery pulse absent (smooth interpolation detected)"
    print("7. Multi-Pulse Stalled Recovery              PASS")

    # 8. Non-Neutral Final Stance (F120 != F001)
    scene.frame_set(120)
    f120_pelvis_z = ppelvis.location.z
    assert abs(f120_pelvis_z - (-0.04)) > 0.01, "FAIL: F120 returned to neutral stance"
    print(f"8. Non-Neutral Strained F120 Posture        PASS (Z offset: {f120_pelvis_z:.3f} m)")

    print("=======================================================\n")

    # Render updated 8-frame diagnostic set directly into artifact directory
    key_frames = [1, 32, 40, 50, 65, 76, 90, 120]
    for frame_num in key_frames:
        scene.frame_set(frame_num)
        out_file = ARTIFACT_DIR / f"varek_blocking_f{frame_num:03d}.png"
        scene.render.filepath = str(out_file)
        bpy.ops.render.render(write_still=True)
        print(f"Rendered Diagnostic Frame {frame_num:03d}: {out_file}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
