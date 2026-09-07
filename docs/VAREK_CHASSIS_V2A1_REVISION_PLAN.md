---
plan_id: varek-chassis-v2a1-primary-massing-salvage
plan_valid_as_of: 2026-09-06T22:38:41-06:00
git_commit: cfdf1bb7b02343f6e68ca0f00b7c85eade8e33c8
files_affected: 4 tracked implementation files plus one ignored blend and six review renders
reversible: yes
blast_radius: new V2A.1 derivative only; approved concept, rejected V1/V2A fixtures, lore, rigging, materials, and Shot 01 remain unchanged
stop_conditions:
  - approved_concept_or_v2a_hash_mismatch
  - output_collision
  - scope_drift_beyond_six_primary_form_corrections
  - torso_remains_box_dominant
  - yoke_remains_hoop_or_roll_cage_like
  - load_path_not_visually_continuous
  - limbs_remain_sparse_or_generic
  - feet_remain_humanoid_boots
  - pilot_not_visibly_buried_and_protected
  - tertiary_detail_used_to_camouflage_primary_form
  - height_or_ground_gate_failure
  - frozen_candidate_hash_changes_during_review
---

# Varek Chassis V2A.1 — Primary-Massing Salvage

## Claim boundary

This increment may establish only that the rejected V2A design has been salvaged into
a stronger static Thulan silhouette by correcting six primary forms. It does not claim
final topology, articulation, rigging, deformation, materials, engineering capacity,
animation, or Shot 01 readiness.

V2A is a machine-valid but human-rejected negative fixture. It must remain byte-exact:

- V2A blend: `blender/candidates/varek-chassis-v2a-static.blend`
- V2A SHA-256: `0449a7d6386f9d495cc29e87e35b79a611c98b5bd280c07b850f76e8ae570071`
- Visual verdict: `evidence/varek-chassis-v2a/visual-verdict.json`
- Approved concept SHA-256:
  `26161f565b3f64e3f9f13d6ed9f78b22fde4a004e0beadc1d9daa9264cf51561`

V2A.1 is built from factory startup with revised procedural definitions. V2A supplies
measurements and observed failure causes, not imported geometry.

## Authorized revision scope

Only these six primary-form corrections are allowed:

1. **Torso taper and segmentation**
   - Replace the single flat rectangular thoracic read with three interlocked,
     tapered/faceted survival-hull masses.
   - Narrow the central mass and leave visible lateral structure so the hull reads as
     protection around a person, not a robot chest or muscular breastplate.
2. **Yoke depth and attachment**
   - Replace the tube-hoop read with paired deep-section, curved/faceted load members.
   - Use a flatter crown, meaningful front-to-rear depth, and primary gusset masses at
     the physical junctions with the dorsal rails.
3. **Dorsal-rail continuity**
   - Make the load route visually traceable from yoke through paired dorsal/thoracic
     rails into the pelvic clevis.
   - Junction gaps may not be hidden with trim or tertiary parts.
4. **Leg-member density**
   - Each leg receives multiple primary load members, paired hydraulic rams, and
     guarded hip/knee/ankle junction masses.
   - Human limb space and machine load paths remain separately legible.
5. **Manipulator structure**
   - Each arm receives paired upper/forearm load members, visible joint housings, a
     rotary wrist bearing, palm carriage, and four functional rescue digits.
   - Linear bars ending in blocks, mittens, or conventional armored gloves fail.
6. **Anchor-foot massing**
   - Widen and deepen the ground interface; emphasize the heel drive, folded anchor
     outriggers, structural sole, and split mechanical toe pads.
   - The silhouette must read as ground-engagement machinery rather than a large boot.

The protected operator cell is repositioned only as required by these corrections:
lower/recess it into the machine, deepen the brow/yoke protection, and add primary
lateral containment masses. Normal exterior views must not expose debug pilot-envelope
limbs through empty chassis gaps. The cutaway must still prove a plausible human fits.

## Explicit prohibitions

- No restart from a new visual architecture.
- No tertiary-density increase. V2A.1 should use fewer tertiary objects than V2A;
  it may never exceed the V2A count recorded in its evidence.
- No hoses, loose cables, bolts, rivet fields, gauges, vents, decals, inscriptions, or
  greebles used to improve the read.
- No material/lookdev work, Cycles rendering, lighting polish, weathering, or color.
- No rig, armature, weights, constraints, animation, A-pose, or T-pose work.
- No external assets or donor geometry.
- No weapon, Fault Maul, cutter, mantle, belt, or Shot 01 additions.

V2A.1 remains in a static service stance. A wide A-pose becomes the V2B production
rest-pose decision only after this silhouette passes.

## Measured construction gates

- Overall ground-contact-to-yoke height: `2.4384 m +/- 0.0005 m`.
- Ground contact: `Z = 0.0 m +/- 0.00025 m`.
- Metric scene, unit scale `1.0`, and applied object scales.
- Workbench MatCap clay only; six views and camera roles remain unchanged.
- External asset count is exactly zero.
- Required collections, primary modules, and object roles are enumerated in the V2A.1
  JSON contract before the builder runs.
- Structural connector endpoints for yoke-to-dorsal and dorsal-to-pelvis junctions must
  be declared by objects/metadata and measure no more than `0.01 m` apart.
- The candidate is frozen before rendering. Review-only visibility changes may not be
  saved; pre-render and post-render SHA-256 values must match.

## Provisional comparison measurements

The validator records V2A and V2A.1 side by side without inventing aesthetic pass
targets:

- widest yoke/shoulder silhouette width;
- protected operator-cell width;
- pelvis width;
- stance width at ground contact;
- Gren-Skildus front-view projected bounding area;
- machine depth in side view;
- pilot-envelope bounding dimensions;
- primary, secondary, and tertiary object counts.

The prior V2A `head_to_yoke_clearance_m` value is invalid as a physical-clearance
measurement because it used the yoke's global lowest side point. V2A.1 corrects the
method: within the operator-cell lateral X band plus a declared margin, find the lowest
yoke surface strictly above the pilot-head top and subtract the pilot-head top Z. The
record must include the band, margin, sampled geometry, and method. It remains
`PROVISIONAL_MEASURED_FOR_VISUAL_COMPARISON`, not a canon dimension.

## Review evidence

The builder produces a new candidate only:

`blender/candidates/varek-chassis-v2a1-dense-static.blend`

Required renders:

1. front orthographic;
2. rear orthographic;
3. character-left orthographic;
4. character-right orthographic;
5. three-quarter perspective;
6. non-destructive human-envelope cutaway.

The exterior views show primary and secondary forms with tertiary forms disabled. The
cutaway uses temporary visibility or ephemeral review objects only. No saved candidate
geometry or visibility state may differ between views.

## Human visual gate

Aaron alone decides whether the revision:

- reads as the approved Thulan load machine rather than a simplified robot;
- presents a dense, interlocked primary silhouette without greeble camouflage;
- makes the operator feel buried and protected while remaining recognizably human;
- communicates `yoke -> dorsal rails -> pelvis -> legs -> anchors -> ground`;
- makes limbs read as rescue/load machinery rather than mechanical stick limbs;
- preserves the promising asymmetry and rear/right powerplant volume from V2A.

A machine PASS cannot satisfy this gate.

## QA and execution sequence

```text
preserve V2A machine PASS + human FAIL_REVISE fixture
  -> commit this V2A.1 plan
  -> external CARDO plan audit
  -> implement V2A.1 contract + builder + independent validator
  -> commit implementation checkpoint without running Blender
  -> external CARDO checkpoint audit
  -> run exactly one V2A.1 build
  -> independent validation and six frozen-byte Workbench renders
  -> show the three-quarter view on Aaron's desktop and verify the viewer window
  -> Aaron visual verdict
  -> STOP
```

Any new failure cause requires a measured plan amendment. Repeating the same build or
adding detail to conceal unresolved massing is prohibited.
