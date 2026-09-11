# SPECIFICATION: VAREK LEFT HAND & RIGHT ARM MECHANICAL RIG

**Document ID:** `docs/VAREK_HAND_RIG_SPEC_v1.md`  
**Status:** DRAFT — awaiting measurement from approved V51/V52 chassis  
**Authority:** RULING 010, RULING 011, RULING 023, RULING 024  
**Gate:** `docs/HAND_PHYSICS_GATE.md`  
**Baselines:**
- `blender/candidates/varek-v51-functional.blend` — sha256 `dbb66690d4a902df38db4433e9a5bf1d79deff4f5ce7afb189a91ec7e5af44e9`
- `blender/candidates/varek-v52-graviton.blend` — sha256 `611516896fbc937af983c816f85a0420c9d4bc57de4d7f49d772bbbdbd43e2e2`

---

## 1. PURPOSE & SCOPE

This document specifies the mechanical degrees of freedom, pivot locations, ranges of motion, constraint limits, and collision mesh requirements for:

1. **Left hand assembly** — the maul grip interface, including wrist gimbal, palm plate, three digits, and opposable thumb.
2. **Right arm assembly** — the graviton manipulator, including three hydraulic talons and the central induction ring mount.

It is the input specification for the procedural Blender script that will assemble the rig. It is not the script. It is not the model. It is the contract the script must satisfy.

**What this document does not specify:**

- Absolute dimensions (marked TBD — must be measured from V51/V52 chassis).
- Materials, shaders, or textures.
- Animation keyframes or poses.
- The maul mesh itself (separate object, driven by `tool` bone).

---

## 2. REFERENCES & AUTHORITY

| Document | Authority |
| :--- | :--- |
| `RULINGS.md` RULING 010 | V4 Visual Gate & Engineering-Evidence Boundary |
| `RULINGS.md` RULING 011 | V4 Four-View Silhouette Approval |
| `RULINGS.md` RULING 023 | Freeze v51 Functional Baseline & Authorize Graviton Manipulator |
| `RULINGS.md` RULING 024 | Tectonic Load-Coupler — Physics, Architecture, Burden Law |
| `docs/HAND_PHYSICS_GATE.md` | 7-step validation sequence; inputs must exist before simulation |
| `tools/check_hand_physics_preflight.py` | Read-only fail-closed preflight |
| `spec/test_hand_physics_preflight.py` | Regression test |
| Session handoff (2026-09-10) | Decisive audit finding: V12 wrist does not articulate |

---

## 3. GENERAL PRINCIPLES FOR HARD-SURFACE RIGGING

### 3.1 Rigid Parenting

Every mesh segment is parented **100% rigidly** to a single bone. No smooth skinning. No weight blending. The steel does not deform; it pivots.

**Rationale:** Varek is a three-tonne assembly of boiler plate, hydraulic cylinders, and clevis pins. If an auto-rigger applies smooth skinning, iron plates bend like rubber, rams stretch like dough, and rivets shear across vertices. Rigid parenting is the only correct approach.

### 3.2 Pivot at Physical Center

Every bone origin is placed at the **exact geometric center** of its physical pivot — the center of the clevis pin, the intersection of gimbal axes, the center of the ball joint.

**Rationale:** If the bone origin is offset from the physical pivot, the segment will rotate around the wrong point. The hinge will appear to translate, not rotate. The constraint will bind at the wrong angle.

### 3.3 Mechanical Stops

Every joint has a **Limit Rotation** constraint (or bone rotation limits) that prevents motion beyond the physical stop. The steel cannot rotate through itself.

**Rationale:** Without limits, the fingers can curl past their own hinges. This is physically impossible for a rigid mech.

### 3.4 Rest Pose

The rig is modeled in a **neutral rest pose**: wrist straight, fingers extended, thumb extended, talons open.

**Rationale:** If the rig is modeled in the grip pose, the fingers cannot open. If modeled in a fist, the hand cannot reach. The grip is a *pose*, not a geometry.

### 3.5 No Camera-Driven Fixes

The wrist orientation is not adjusted to suit the camera. The camera is adjusted to suit the wrist.

**Rationale:** RULING: "Do not fix wrist orientation by rotating the hand to suit the camera." A rig that only works from one angle is not a rig.

---

## 4. COORDINATE SYSTEM & CONVENTIONS

### 4.1 Hand-Local Coordinate System

All pivot locations are specified relative to the **wrist gimbal center**, which is the origin `(0, 0, 0)` of the hand assembly.

| Axis | Direction | Convention |
| :--- | :--- | :--- |
| **+Y** | Distal | Toward fingertips |
| **+Z** | Dorsal | Back of hand |
| **+X** | Radial | Thumb side (left hand) |

### 4.2 Normalized Units

Pivot locations are expressed as **fractions of hand length** (wrist center to fingertip). This makes the spec independent of absolute scale. Absolute dimensions will be substituted once measured from V51/V52.

| Landmark | Normalized Y | Description |
| :--- | :--- | :--- |
| Wrist gimbal center | 0.00 | Origin |
| Palm plate center | 0.15 | 15% toward fingertips |
| MCP joints (knuckles) | 0.35 | 35% toward fingertips |
| PIP joints (mid-finger) | 0.60 | 60% toward fingertips |
| DIP joints (tip-finger) | 0.80 | 80% toward fingertips |
| Fingertips | 1.00 | Full extension |

### 4.3 Bone Naming Convention

| Bone | Name | Parent |
| :--- | :--- | :--- |
| Hand root | `hand.L` | `forearm.L` |
| Wrist pitch | `wrist_pitch.L` | `hand.L` |
| Wrist yaw | `wrist_yaw.L` | `wrist_pitch.L` |
| Palm | `palm.L` | `wrist_yaw.L` |
| Digit 1 (index) seg 1 | `digit1_01.L` | `palm.L` |
| Digit 1 seg 2 | `digit1_02.L` | `digit1_01.L` |
| Digit 1 seg 3 | `digit1_03.L` | `digit1_02.L` |
| Digit 2 (middle) seg 1 | `digit2_01.L` | `palm.L` |
| Digit 2 seg 2 | `digit2_02.L` | `digit2_01.L` |
| Digit 2 seg 3 | `digit2_03.L` | `digit2_02.L` |
| Digit 3 (ring) seg 1 | `digit3_01.L` | `palm.L` |
| Digit 3 seg 2 | `digit3_02.L` | `digit3_01.L` |
| Digit 3 seg 3 | `digit3_03.L` | `digit3_02.L` |
| Thumb seg 1 | `thumb_01.L` | `palm.L` |
| Thumb seg 2 | `thumb_02.L` | `thumb_01.L` |

**Total bones in left hand:** 15 (1 root + 2 wrist + 1 palm + 9 digits + 2 thumb)

**Maul bone:** `tool` — separate object, parented to `digit1_01.L` through `digit3_01.L` and `thumb_01.L` via IK/contact verification, **not fused** to any hand mesh.

---

## 5. MECHANICAL PRIMITIVES

### 5.1 Clevis Hinge (1 DOF)

**Geometry:** Two parallel plates (the clevis) with a cylindrical pin passing through both. The child segment rotates around the pin axis.

**Pivot:** Center of the pin.

**Degrees of freedom:** 1 (rotation around pin axis).

**Constraint:** Limit Rotation — minimum and maximum angle per joint specification.

**Use:** Finger segments, thumb segments, talon segments.

### 5.2 Universal Gimbal Yoke (2 DOF)

**Geometry:** Two concentric rings at 90° to each other. The outer ring rotates around one axis; the inner ring rotates around the orthogonal axis.

**Pivot:** Intersection of the two axes.

**Degrees of freedom:** 2 (pitch and yaw).

**Constraint:** Two Limit Rotation constraints (one per axis).

**Use:** Wrist (pitch + yaw), induction ring mount (pitch + yaw).

### 5.3 Limited Ball-and-Socket (2–3 DOF)

**Geometry:** A spherical ball captured in a socket with mechanical stops.

**Pivot:** Center of the ball.

**Degrees of freedom:** 2–3 (depending on socket geometry).

**Constraint:** Limit Rotation with cone angle and twist angle.

**Use:** Thumb base (saddle joint), if a gimbal is insufficient.

---

## 6. LEFT HAND ASSEMBLY — MAUL GRIP

### 6.1 Assembly Overview

The left hand grips the Fault Maul (*Faírguni-Hamars*). The maul is 30 kg of tool steel with a hexagonal haft. The hand must:

- Grip the haft securely under load (the maul drags, swings, strikes).
- Release the haft on command.
- Articulate gently enough to hold a human hand (the final touch scene).

The hand has **three digits + one opposable thumb**. Three digits wrap around three faces of the hexagonal haft. The thumb wraps around a fourth face. This is a stable grip.

### 6.2 Wrist Gimbal

| Parameter | Value | Notes |
| :--- | :--- | :--- |
| Type | Universal gimbal yoke | 2 DOF |
| Bone 1 | `wrist_pitch.L` | Flexion/extension |
| Bone 2 | `wrist_yaw.L` | Radial/ulnar deviation |
| Pivot | Intersection of gimbal axes | Normalized Y = 0.00 |
| Pitch range | −20° (extension) to +45° (flexion) | TBD — pending mechanical stop design |
| Yaw range | −15° (ulnar) to +20° (radial) | TBD — pending mechanical stop design |
| Constraint type | Limit Rotation | Per axis |

### 6.3 Palm Plate

| Parameter | Value | Notes |
| :--- | :--- | :--- |
| Type | Rigid plate | 0 DOF |
| Bone | `palm.L` | Parented to `wrist_yaw.L` |
| Pivot | Center of palm plate | Normalized Y = 0.15 |
| Dimensions | TBD | Measure from V51/V52 |

### 6.4 Digit Segments (Digits 1–3)

Each digit has **three segments**: proximal, middle, distal.

| Joint | Bone | Parent | Pivot (Y) | Range | Constraint |
| :--- | :--- | :--- | :--- | :--- | :--- |
| MCP | `digit{N}_01.L` | `palm.L` | 0.35 | 0° to +80° curl | Limit Rotation |
| PIP | `digit{N}_02.L` | `digit{N}_01.L` | 0.60 | 0° to +90° curl | Limit Rotation |
| DIP | `digit{N}_03.L` | `digit{N}_02.L` | 0.80 | 0° to +60° curl | Limit Rotation |

**Digit X positions (normalized, relative to palm center):**

| Digit | X offset | Description |
| :--- | :--- | :--- |
| Digit 1 | −0.15 | Index (radial side) |
| Digit 2 | 0.00 | Middle |
| Digit 3 | +0.15 | Ring (ulnar side) |

**Total DOF per digit:** 3 (MCP, PIP, DIP) × 3 digits = 9 DOF.

### 6.5 Thumb

The thumb has **two segments** and a **saddle base joint** for opposition.

| Joint | Bone | Parent | Pivot (Y) | Range | Constraint |
| :--- | :--- | :--- | :--- | :--- | :--- |
| CMC (base) | `thumb_01.L` | `palm.L` | 0.15 | −30° to +45° flexion; −20° to +30° abduction | Limit Rotation (2 axes) |
| MCP | `thumb_02.L` | `thumb_01.L` | 0.40 | 0° to +70° curl | Limit Rotation |

**Thumb X position:** +0.25 (radial side, opposite the digits).

**Total DOF for thumb:** 3 (CMC flexion, CMC abduction, MCP curl).

### 6.6 Constraint Summary — Left Hand

| Joint | DOF | Min | Max | Constraint Type |
| :--- | :--- | :--- | :--- | :--- |
| Wrist pitch | 1 | −20° | +45° | Limit Rotation |
| Wrist yaw | 1 | −15° | +20° | Limit Rotation |
| MCP (each digit) | 1 | 0° | +80° | Limit Rotation |
| PIP (each digit) | 1 | 0° | +90° | Limit Rotation |
| DIP (each digit) | 1 | 0° | +60° | Limit Rotation |
| Thumb CMC flex | 1 | −30° | +45° | Limit Rotation |
| Thumb CMC abd | 1 | −20° | +30° | Limit Rotation |
| Thumb MCP | 1 | 0° | +70° | Limit Rotation |
| **Total** | **14** | | | |

---

## 7. RIGHT ARM ASSEMBLY — GRAVITON MANIPULATOR

### 7.1 Assembly Overview

The right arm terminates in **three hydraulic talons** around the **copper induction ring** (*Faírg-Tygil*). It has no conventional hand. The talons grip and stabilize loads; the induction ring generates the gravimetric coupling field.

Per RULING 024, the right arm has eight structural stages:

1. Shoulder Load Yoke
2. Upper-Arm Structural Housing
3. Heavy Elbow Bearing
4. Forearm Field Generator
5. Concentric Coupling Rings
6. Segmented Field Vanes
7. Compact Manipulator Palm
8. Backpack Power / Conduit Path

This specification covers **stages 5–7**: the coupling rings, field vanes, and manipulator palm (talons + induction ring mount).

### 7.2 Talon Segments (Talons A, B, C)

Each talon has **three segments**: base, mid, tip.

| Joint | Bone | Parent | Pivot (Y) | Range | Constraint |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Base | `talon{A}_01.R` | `manip_palm.R` | 0.00 | 0° to +60° curl | Limit Rotation |
| Mid | `talon{A}_02.R` | `talon{A}_01.R` | 0.35 | 0° to +80° curl | Limit Rotation |
| Tip | `talon{A}_03.R` | `talon{A}_02.R` | 0.65 | 0° to +50° curl | Limit Rotation |

**Talon angular positions (radial, relative to palm center):**

| Talon | Angle | Description |
| :--- | :--- | :--- |
| Talon A | 0° | Top |
| Talon B | 120° | Bottom-right |
| Talon C | 240° | Bottom-left |

**Total DOF per talon:** 3 × 3 talons = 9 DOF.

### 7.3 Induction Ring Mount

The copper induction ring (*Faírg-Tygil*) is mounted on a **universal gimbal yoke** at the center of the three talons.

| Parameter | Value | Notes |
| :--- | :--- | :--- |
| Type | Universal gimbal yoke | 2 DOF |
| Bone 1 | `ring_pitch.R` | Pitch |
| Bone 2 | `ring_yaw.R` | Yaw |
| Pivot | Center of ring | Normalized Y = 0.50 (center of talon span) |
| Pitch range | −30° to +30° | TBD — pending field geometry |
| Yaw range | −30° to +30° | TBD — pending field geometry |
| Constraint type | Limit Rotation | Per axis |

**Ring dimensions:** TBD — measure from V52 graviton model.

### 7.4 Constraint Summary — Right Arm

| Joint | DOF | Min | Max | Constraint Type |
| :--- | :--- | :--- | :--- | :--- |
| Talon base (each) | 1 | 0° | +60° | Limit Rotation |
| Talon mid (each) | 1 | 0° | +80° | Limit Rotation |
| Talon tip (each) | 1 | 0° | +50° | Limit Rotation |
| Ring pitch | 1 | −30° | +30° | Limit Rotation |
| Ring yaw | 1 | −30° | +30° | Limit Rotation |
| **Total** | **11** | | | |

---

## 8. RIGID PARENTING & BONE HIERARCHY

### 8.1 Left Hand Hierarchy

```
forearm.L
└── hand.L
    └── wrist_pitch.L
        └── wrist_yaw.L
            └── palm.L
                ├── digit1_01.L
                │   └── digit1_02.L
                │       └── digit1_03.L
                ├── digit2_01.L
                │   └── digit2_02.L
                │       └── digit2_03.L
                ├── digit3_01.L
                │   └── digit3_02.L
                │       └── digit3_03.L
                └── thumb_01.L
                    └── thumb_02.L
```

### 8.2 Right Arm Hierarchy

```
forearm.R
└── manip_palm.R
    ├── ring_pitch.R
    │   └── ring_yaw.R
    │       └── induction_ring.R
    ├── talonA_01.R
    │   └── talonA_02.R
    │       └── talonA_03.R
    ├── talonB_01.R
    │   └── talonB_02.R
    │       └── talonB_03.R
    └── talonC_01.R
        └── talonC_02.R
            └── talonC_03.R
```

### 8.3 Vertex Group Assignment

Every vertex of every mesh segment is assigned **100% weight** to its corresponding bone. No vertex is assigned to more than one bone. No weight blending. No smooth deformation.

**Example:** All vertices of the distal phalanx of digit 1 are weighted 100% to `digit1_03.L`. The bone rotates; the mesh follows rigidly.

### 8.4 The `tool` Bone

The Fault Maul is a **separate object**, not fused to any hand mesh. It is driven by the `tool` bone, which is parented to `palm.L` (or to `hand.L`). The maul's position is verified via IK/contact against `digit1_01.L`, `digit2_01.L`, `digit3_01.L`, and `thumb_01.L`.

**Rule:** The maul is never fused to the hand or forearm mesh. It is a separate object with its own bone.

---

## 9. COLLISION MESH REQUIREMENTS

### 9.1 Purpose

Collision meshes detect when the hand penetrates the maul haft, when fingers penetrate themselves, and when the talons penetrate the induction ring.

### 9.2 Requirements

| Mesh | Type | Purpose |
| :--- | :--- | :--- |
| `col_digit1_01.L` | Convex hull | Digit 1 proximal collision |
| `col_digit1_02.L` | Convex hull | Digit 1 middle collision |
| `col_digit1_03.L` | Convex hull | Digit 1 distal collision |
| `col_digit2_01.L` | Convex hull | Digit 2 proximal collision |
| `col_digit2_02.L` | Convex hull | Digit 2 middle collision |
| `col_digit2_03.L` | Convex hull | Digit 2 distal collision |
| `col_digit3_01.L` | Convex hull | Digit 3 proximal collision |
| `col_digit3_02.L` | Convex hull | Digit 3 middle collision |
| `col_digit3_03.L` | Convex hull | Digit 3 distal collision |
| `col_thumb_01.L` | Convex hull | Thumb proximal collision |
| `col_thumb_02.L` | Convex hull | Thumb distal collision |
| `col_maul_haft` | Convex hull | Maul haft collision |
| `col_talon{A}_01.R` | Convex hull | Talon base collision |
| `col_talon{A}_02.R` | Convex hull | Talon mid collision |
| `col_talon{A}_03.R` | Convex hull | Talon tip collision |
| `col_ring.R` | Cylinder | Induction ring collision |

### 9.3 Collision Rules

1. Digits cannot penetrate each other.
2. Digits cannot penetrate the palm plate.
3. Digits cannot penetrate the maul haft.
4. Talons cannot penetrate each other.
5. Talons cannot penetrate the induction ring.
6. The maul haft cannot penetrate the palm plate.

**Validation:** The preflight tool checks these rules. If any collision is detected, the preflight fails.

---

## 10. VALIDATION SEQUENCE

### 10.1 Preflight (Prerequisite Only)

1. Run `tools/check_hand_physics_preflight.py` on the candidate.
2. Verify PASS: REST envelope canonical, 0 prohibited intersections, 0 self-intersections, 0 unbound meshes, 0 floating geometry.
3. Verify all bones exist and are parented correctly.
4. Verify all constraints are set with correct limits.
5. Verify all collision meshes exist and are bound.

**PASS is prerequisite-only, not a simulation certificate.**

### 10.2 Finite-Force Rigid-Body Simulation

1. Place the maul in the hand grip.
2. Apply gravity (9.81 m/s² downward).
3. Apply load forces: maul weight (30 kg × 9.81 = 294.3 N), swing forces (TBD), impact forces (TBD).
4. Simulate for 300 frames (at 24 FPS = 12.5 seconds).
5. Check:
   - Maul stays seated in grip (no slip).
   - No finger penetration of maul haft.
   - No constraint violation.
   - No pivot drift.
   - No mesh deformation.
6. Record results. If any check fails, the grip is not valid.

### 10.3 Visual Diagnostic

1. Render a Cycles diagnostic frame (128 samples) at a three-quarter angle.
2. Verify contact shadows, mechanical mass, material separation.
3. Verify the grip reads correctly to the eye.
4. **The visual check is not a substitute for the simulation. It is a supplement.**

### 10.4 Handoff Gate

Handoff requires:
- Preflight PASS (prerequisite).
- Finite-force simulation PASS (physical-plausibility gate).
- Aaron's visual approval.

**No static render, reference-point alignment, or intersection-only PASS authorizes handoff.**

---

## 11. OPEN ITEMS (TBD)

The following parameters must be measured from the approved V51/V52 chassis before the script can be finalized:

| Item | Source | Value (Measured / Specified) |
| :--- | :--- | :--- |
| Hand length (wrist center to fingertip) | V51 / V52 | **0.3430 m** (0.151m hand + 0.192m digits) |
| Forearm cuff diameter (outer / inner) | V51 / V52 | **0.1814 m / 0.1426 m** (`Wrist coupling L`) |
| Palm plate width | V51 / V52 | **0.1500 m** (spanned across digit origins) |
| Palm plate thickness | V51 / V52 | **0.0350 m** |
| Clevis pin diameter | Design Spec | **0.0160 m** (16mm tool-steel pin) |
| Gimbal ring diameter | Design Spec | **0.1200 m** (nested inside 0.181m cuff) |
| Maul haft diameter (flats / ribs) | V52 Maul | **0.0520 m / 0.0682 m** (`Maul lower grip rib`) |
| Maul haft length (grip section) | V52 Maul | **0.2774 m** (`Maul grip`) |
| Talon length (3 segments combined) | V52 Graviton | **0.2200 m** |
| Induction ring diameter | V52 Graviton | **0.2207 m** (`Varek_Neck_GimbalRing` / core) |
| Induction ring thickness | V52 Graviton | **0.1076 m** |

---

## 12. APPENDIX: BONE NAMING CONVENTION

### 12.1 Left Hand

| Bone | Full Name | Description |
| :--- | :--- | :--- |
| `hand.L` | Hand root | Root of hand assembly |
| `wrist_pitch.L` | Wrist pitch | Flexion/extension |
| `wrist_yaw.L` | Wrist yaw | Radial/ulnar deviation |
| `palm.L` | Palm | Rigid palm plate |
| `digit1_01.L` | Digit 1 proximal | Index proximal phalanx |
| `digit1_02.L` | Digit 1 middle | Index middle phalanx |
| `digit1_03.L` | Digit 1 distal | Index distal phalanx |
| `digit2_01.L` | Digit 2 proximal | Middle proximal phalanx |
| `digit2_02.L` | Digit 2 middle | Middle middle phalanx |
| `digit2_03.L` | Digit 2 distal | Middle distal phalanx |
| `digit3_01.L` | Digit 3 proximal | Ring proximal phalanx |
| `digit3_02.L` | Digit 3 middle | Ring middle phalanx |
| `digit3_03.L` | Digit 3 distal | Ring distal phalanx |
| `thumb_01.L` | Thumb proximal | Thumb proximal segment |
| `thumb_02.L` | Thumb distal | Thumb distal segment |

### 12.2 Right Arm

| Bone | Full Name | Description |
| :--- | :--- | :--- |
| `manip_palm.R` | Manipulator palm | Talon root |
| `ring_pitch.R` | Ring pitch | Induction ring pitch |
| `ring_yaw.R` | Ring yaw | Induction ring yaw |
| `induction_ring.R` | Induction ring | The copper ring |
| `talonA_01.R` | Talon A base | Top talon base |
| `talonA_02.R` | Talon A mid | Top talon mid |
| `talonA_03.R` | Talon A tip | Top talon tip |
| `talonB_01.R` | Talon B base | Bottom-right talon base |
| `talonB_02.R` | Talon B mid | Bottom-right talon mid |
| `talonB_03.R` | Talon B tip | Bottom-right talon tip |
| `talonC_01.R` | Talon C base | Bottom-left talon base |
| `talonC_02.R` | Talon C mid | Bottom-left talon mid |
| `talonC_03.R` | Talon C tip | Bottom-left talon tip |

---

## 13. NEXT STEP

This specification is the input for the procedural Blender script. The script will:

1. Create the bone hierarchy with correct parenting.
2. Create the bone origins at the specified pivot locations.
3. Add Limit Rotation constraints with the specified limits.
4. Create collision meshes (convex hulls) for each segment.
5. Assign vertices 100% rigidly to their bones.
6. Save as `varek-hand-rig-v1.blend`.

After the script runs, run the preflight. Then run the finite-force simulation. Then render a diagnostic. Then present to Aaron for visual approval.

---

**End of specification.**
