# SPECIFICATION: VAREK HAND DYNAMIC PHYSICS TEST ENVELOPE

**Document ID:** `docs/VAREK_HAND_PHYSICS_TEST_ENVELOPE.md`  
**Authority:** `docs/HAND_PHYSICS_GATE.md`, `RULINGS.md` (RULING 010, RULING 023, RULING 024)  
**Status:** FROZEN TEST ENVELOPE  
**Target Candidate:** `blender/candidates/varek-v55-mechanical-grip.blend`  
**Test Derivative:** `blender/candidates/varek-v55-hand-physics.blend`  

---

## 1. PURPOSE & CLAIM BOUNDARY

Per `docs/HAND_PHYSICS_GATE.md`:
> *"Inputs that must exist before simulation: Declare units and scale; hammer mass, centre of mass and inertia with provenance; material/contact friction range; finite grip/actuator limits; joint travel and supports; gravity; movement duration and disturbance; permitted slip, angular drift, penetration and closure gaps; numerical settings and repeatability bands. These are currently UNSET, not measured facts. Choose and freeze a conservative test envelope before running; never tune it after seeing a failure."*

This document defines and freezes the explicit physical parameters, collision proxies, and acceptance criteria for validating that the Left Hand mechanical rig can retain the *Faírguni-Hamars* maul under gravity purely through physical contact, and release it cleanly upon opening.

---

## 2. DECLARED PHYSICAL INPUTS & PROVENANCE

### 2.1 Units & Coordinate System
- **Units:** SI metric (meters, kilograms, seconds).
- **Scale:** $1.0\text{ Blender unit} = 1.0\text{ meter}$.
- **Gravity Vector:** $\vec{g} = (0.0, 0.0, -9.810)\text{ m/s}^2$ (standard terrestrial gravity).

### 2.2 Maul (*Faírguni-Hamars*) Physical Properties
- **Total Mass:** $30.0\text{ kg}$ (canonical specification for pneumatic fault maul).
- **Haft Diameter:** $48.0\text{ mm}$ across flats (hexagonal forged alloy steel), $52.0\text{ mm}$ across ribs.
- **Center of Mass:** Located $0.320\text{ m}$ above the lower grip collar toward the striking shoe.
- **Collision Type:** Compound / Convex Hull rigid body proxy encompassing the haft, grip ribs, impact cylinder, and head.
- **Dynamic Freedom:** Unparented, zero animation data, zero armature modifiers, zero kinematic constraints, `rigid_driver_bone = 'tool'`.

### 2.3 Hand & Arm Mechanical Boundary
- **Stationary Support:** The left forearm (`forearm.L`) and wrist cuff (`Wrist coupling L`) are pinned / kinematic anchors.
- **Wrist Articulation:** 2-DOF universal gimbal with physical limits:
  - Pitch (`wrist_pitch.L`): $-20.0^\circ$ to $+45.0^\circ$.
  - Yaw (`wrist_yaw.L`): $-15.0^\circ$ to $+25.0^\circ$.
- **Digit Segments:** 14 rigid forged segments:
  - 1 Palm plate chassis (`Palm_Plate_L`).
  - 9 Finger phalanx segments (`Digit[1-3]_Phalanx[1-3]_L`).
  - 2 Thumb phalanx segments (`Thumb_Phalanx[1-2]_L`).
  - 2 Gimbal yoke rings (`Gimbal_Yoke_Outer_L`, `Gimbal_Yoke_Inner_L`).
- **Collision Proxies:** Distinct convex hull colliders for each individual phalanx and the palm plate. **No single convex hull covers the palm cavity**, preserving open clearance for haft entry.
- **Friction & Restitution:**
  - Steel-on-steel friction coefficient: $\mu = 0.55$.
  - Restitution (elastic bounce): $\epsilon = 0.05$ (near-inelastic hard contact).
  - Collision margin: $0.001\text{ m}$ ($1.0\text{ mm}$).

---

## 3. SIMULATION SOLVER SETTINGS

- **Physics Engine:** Bullet Physics (Blender 5.2.0 LTS internal).
- **Substeps Per Frame:** $60$ (minimum for high-stiffness hard-surface contact).
- **Solver Iterations:** $50$.
- **Time Step:** Fixed $1 / 60\text{ s}$ per frame.

---

## 4. TEST PROTOCOLS & ACCEPTANCE CRITERIA

| Test Case | Hand Pose / State | Expected Result | Pass Criteria |
| :--- | :--- | :--- | :--- |
| **Test 1: Preflight Verification** | Scene configuration | `PREREQUISITES_ONLY_PASS` | 0 failures in `check_hand_physics_preflight.py` |
| **Test 2: Dynamic Hold (Gravity)** | Digits closed in canonical grip | Maul retained under $-9.81\text{ m/s}^2$ | Vertical slip $\Delta z < 5.0\text{ mm}$ over 60 frames; angular drift $< 2.0^\circ$ |
| **Test 3: Negative Control A (Open Hand)** | Digits at rest pose (open) | Maul drops freely | Maul falls $\ge 0.5\text{ m}$ under gravity within 30 frames |
| **Test 4: Negative Control B (Disabled Contact)** | Digits in grip, collision disabled | Maul drops freely | Maul falls $\ge 0.5\text{ m}$ through hand |

---

## 5. EVIDENCE BINDING

All simulation runs must produce:
1. Frozen `.blend` candidate: `blender/candidates/varek-v55-hand-physics.blend`.
2. SHA-256 hash log.
3. Diagnostic frame captures and trajectories.
4. JSON measurement log recording position $(x, y, z)$, linear velocity, and angular deviation at frames 1, 15, 30, 45, 60.
