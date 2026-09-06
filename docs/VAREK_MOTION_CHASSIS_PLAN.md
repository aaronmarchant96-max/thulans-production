---
plan_id: thulan-varek-motion-chassis-v1
plan_valid_as_of: 2026-09-06T17:46:59-06:00
git_commit: 29b9e4d911831a38ddc2bc7e5f87c84814bec085
files_affected: 1 tracked plan checkpoint; future execution creates a builder, validator, candidate blend, and review evidence
reversible: yes
blast_radius: new Varek greybox candidate only; no existing blend or Shot 01 scene may be opened or changed
stop_conditions:
  - approved_concept_hash_mismatch
  - baseline_commit_changed_without_revalidation
  - existing_output_collision
  - overall_height_gate_failure
  - human_envelope_does_not_fit
  - load_path_not_visually_continuous
  - rigid_structure_deforms
  - joint_clearance_failure
  - trailer_pose_gate_failure
  - conventional_power_armor_drift
  - scope_drift_into_detail_materials_or_shot_01
---

# Varek Motion Chassis V1

## Claim

This increment may establish only that a 2.4384 m greybox machine can contain a
plausible full-limbed human envelope, preserve the approved industrial silhouette,
articulate through the required rescue poses, and route the dominant visible load from
yoke to ground without gross intersection or rigid-part deformation.

It does not claim final engineering dimensions, structural capacity, production
topology, final rigging, materials, animation quality, or Shot 01 readiness.

## Hash-bound input

- Approved concept: `assets/concepts/varek-v4-four-view-approved.png`
- Required SHA-256:
  `26161f565b3f64e3f9f13d6ed9f78b22fde4a004e0beadc1d9daa9264cf51561`
- Blender entry point: `flatpak run org.blender.Blender`
- Measured installed version at plan time: `Blender 5.2.0 LTS`

Any mismatch stops execution before Blender starts.

## Scope

### Build

- Neutral full-limbed pilot envelope, explicitly marked `PROVISIONAL` and never treated
  as a locked biological height.
- Sealed protective human hull surrounding that envelope.
- Overhead yoke, thoracic rails, dorsal/spinal powerplant volume, pelvic load junction,
  femur/shin columns, articulated rescue manipulators, and broad anchor boots.
- Three simplified, mutually exclusive ground-interface states: rock pin, structural
  clamp, and debris outrigger.
- Simplified Gren-Skildus volume on character-left and industrial tool station on
  character-right for silhouette clearance only.
- Minimal articulated chassis controls sufficient for the test poses. Rigid modules
  use rigid parenting or single-driver weights; no plate receives blended rubber-like
  deformation.

### Do not build

- Fault Maul production mesh
- thermal-shear production mesh
- engine internals or decorative greebles
- UVs, textures, shaders, weathering, gore, cloth simulation, hair, or final materials
- production walk cycle, combat motion, camera choreography, lighting, environment, or
  Shot 01
- any exact load, pressure, impact-energy, temperature, eye-line, shoulder-span, mass-
  breakdown, or cylinder-diameter claim

## Safe execution architecture

The future builder must:

1. Run only with Blender's `--factory-startup --background` flags.
2. Create a new versioned candidate; never open or clear an existing production blend.
3. Refuse an existing output path rather than overwrite it.
4. Use deterministic named collections:
   `00_REFERENCE`, `01_PILOT_ENVELOPE`, `02_HUMAN_HULL`, `03_LOAD_FRAME`,
   `04_POWERPLANT`, `05_GROUND_INTERFACE`, `06_CONTROLS`, `07_QA_CAMERAS`.
5. Save before rendering, hash the candidate, render from those exact bytes without
   saving review-only camera or display changes back into it, then re-hash.
6. Exit non-zero and write a failure record on every contracted gate failure.

## Dimensional gates

- Overall ground-contact-to-yoke-apex height: `2.4384 m +/- 0.0005 m`.
- Neutral ground-contact surfaces: `Z = 0.0 m +/- 0.00025 m`.
- Scene units: metric, unit scale `1.0`.
- Object scale applied before measurement; no negative or non-uniform scale on rigid
  modules in the frozen candidate.
- Pilot height and joint locations are recorded as `PROVISIONAL_MEASURED`, not canon.
- Pilot head, shoulders, elbows, pelvis, knees, and feet must remain inside their
  corresponding hull/frame envelopes in neutral and test poses.
- Human shoulder, elbow, hip, knee, and ankle centers must remain within documented
  provisional offsets from the corresponding chassis articulation centers in every
  test pose. V1 measures and reports those offsets; it does not invent an acceptance
  number. Any pose requiring anatomical dislocation, limb-length change, or impossible
  human joint rotation fails human review.
- The `2.4384 m` value is a production chassis normalization target, not a claim of
  biological precision.

## Required poses at 24 fps

These are clearance tests, not final animation:

| Frame | State | Required observation |
| ---: | --- | --- |
| 1 | neutral service stance | human placement and complete silhouette |
| 24 | mid-stride | leg clearance and visible weight shift |
| 48 | planted stance | both ground contacts established |
| 60 | Anchor State deployed | debris outriggers opened and pelvis lowered |
| 72 | overhead catch | hands/yoke aligned beneath a proxy load |
| 96 | sustained brace | frame remains planted and visually continuous |

## Trailer Pose Gate

Machine PASS requires:

- no primary foot-chassis reference-point translation greater than `0.002 m` from
  frames 48–96; deployment parts may articulate relative to the stationary feet;
- no ground-contact penetration or floating greater than `0.002 m`;
- no rigid module non-uniform scaling or blended bending;
- no bounding-volume or mesh penetration above a provisional, predeclared collision
  threshold for enumerated interface pairs: helmet/yoke, shoulder/rail, pelvis/hip,
  knee, ankle, hand/tool-proxy, powerplant/load-frame, and Gren-Skildus/torso;
- hands can meet the overhead proxy without shoulder disassembly;
- debris-outrigger geometry visibly contacts the substrate at frame 60;
- rock-pin and structural-clamp modes pass isolated neutral deployment checks and are
  excluded from the frame 48–96 planted-foot metric.

The collision threshold and the collision representation used for each pair must be
declared in the builder contract before execution. They remain provisional test values,
not anatomical or engineering canon.

Human review PASS requires:

- no visually unacceptable collision, clipping, implausible clearance, or silhouette
  collapse;
- front, rear, side, and three-quarter clay views preserve the approved industrial
  silhouette and show a continuous yoke-to-ground load path;
- the human envelope remains legible and plausible inside the machine;
- the design reads as Thulan rescue infrastructure rather than conventional power
  armor.

Machine PASS does not equal chassis approval. Only Aaron may approve silhouette, human
plausibility, industrial identity, Thulan continuity, and absence of conventional
power-armor drift.

## Diagnostic support check

At frames 48, 60, 72, and 96, report the projected chassis reference center relative
to the measured ground-contact support polygon. This is diagnostic only. It establishes
neither physical stability nor structural/load capacity, and does not justify a physics
simulation in V1.

## Evidence outputs

Generated, non-promoted outputs:

- `blender/candidates/varek-motion-chassis-v1.blend`
- `evidence/varek-motion-chassis-v1/measurements.json`
- `evidence/varek-motion-chassis-v1/front-clay.png`
- `evidence/varek-motion-chassis-v1/rear-clay.png`
- `evidence/varek-motion-chassis-v1/side-clay.png`
- `evidence/varek-motion-chassis-v1/three-quarter-clay.png`
- `evidence/varek-motion-chassis-v1/trailer-pose-clay.png`

The measurement record must bind:

- source concept hash and candidate blend hash;
- `plan_id`, plan Git commit, and plan-file SHA-256;
- source Git commit and clean/dirty repository state;
- builder-script and validator-script SHA-256;
- OS/platform, resolved Blender executable, Blender version, embedded Python version,
  and UTC build timestamp;
- scene units, overall height, ground contacts, provisional pilot measurements and
  pilot-to-chassis joint offsets;
- object-scale inventory, rigid-driver inventory, enumerated collision-pair results,
  pose-frame contacts, diagnostic support-center results, and every PASS/FAIL result.

## Gate sequence

```text
plan audit
  -> deterministic builder implementation
  -> builder audit without execution
  -> one background build
  -> machine gates
  -> frozen candidate hash
  -> clay review renders
  -> independent evidence audit
  -> Aaron human chassis decision
```

Pre-build failures create only a failure record. Post-build failures preserve the
generated candidate and all evidence produced up to the failure point, but do not
promote it. There is no automatic second build. A repeat requires a new measured cause
and a revised plan.
