---
plan_id: varek-chassis-v2-concept-faithful-static
plan_valid_as_of: 2026-09-06T22:12:05-06:00
git_commit: 2de408c2ee4ce835946a98a82ab4fbebeb61f138
files_affected: 4 tracked implementation files plus one ignored blend and six review renders
reversible: yes
blast_radius: new V2 static chassis candidate only; V1 diagnostic, approved concept, lore, and Shot 01 remain unchanged
stop_conditions:
  - approved_concept_hash_mismatch
  - v2_output_collision
  - primary_silhouette_reads_as_robot_or_power_armor
  - operator_cannot_fit_inside_machine
  - load_path_not_visually_continuous
  - rectangular_scaffold_or_box_torso_dominates
  - external_asset_enters_primary_silhouette
  - height_gate_failure
  - workbench_evidence_failure
  - scope_drift_into_rigging_materials_or_shot_01
---

# Varek Chassis V2 — Static Silhouette Build

## Claim

This increment may establish only that a static, concept-faithful Varek chassis exists
at the production normalization height and visibly contains a plausible human while
reading as a purpose-built Thulan rescue/load machine.

It does not claim working articulation, deformation, engineering capacity, final
topology, materials, animation, or Shot 01 readiness.

## Bound inputs

- Approved concept:
  `assets/concepts/varek-v4-four-view-approved.png`
- Concept SHA-256:
  `26161f565b3f64e3f9f13d6ed9f78b22fde4a004e0beadc1d9daa9264cf51561`
- Negative diagnostic candidate:
  `blender/candidates/varek-motion-chassis-v1.blend`
- Negative diagnostic SHA-256:
  `6566fdbac4dc50e9f7adc120795c95c1795ff4fefafd13548b71375c0669269e`
- Render authority: `RULING 012` and `docs/BLENDER_RENDER_PIPELINE.md`.

V1's machine checks passed, but human visual approval was not granted. It is retained
only to preserve working scale/contact measurements and the rejected visual failure:
box torso, rectangular yoke, generic robot limbs, weak mechanical density, and escaped
pilot-envelope forms in the brace view.

## Gate split

```text
V2A static Workbench chassis
  -> machine measurements
  -> six Workbench clay views
  -> Aaron silhouette decision
  -> STOP

Only after V2A approval:
  V2B original human rig + rigid machine controls
  -> clearance poses
  -> Workbench motion gate
  -> STOP
```

No rigging code enters V2A. This is a form gate.

## V2A construction contract

### Operator and human plausibility

- Build a neutral, full-limbed, provisional human envelope first.
- Recess the small protected operator cell below the overhead yoke.
- The pilot's head, shoulders, elbows, pelvis, knees, and feet remain visibly plausible
  inside the machine in the dedicated cutaway view.
- The external machine joint centers may be offset from the human joints, but the
  offset and mechanical linkage volume must be visible and measured—not hidden by solid
  blocks.

### Primary structural language

- Curved or faceted overhead load yoke with substantial section depth; no rectangular
  scaffold silhouette.
- Paired thoracic and dorsal rails visibly continue into the pelvic clevis.
- Protective human hull is tapered and segmented around the operator; it may not read
  as a muscular breastplate or a single cuboid torso.
- Integrated powerplant occupies the dorsal load structure between the rails. It must
  read as part of the chassis, never luggage.
- Pelvis is a mechanical load junction with clevis/pivot language, not humanoid briefs.
- Each leg uses multiple visible load members, cylinders, joint housings, and guarded
  linkages. Solid rectangular thigh/shin columns are prohibited.
- Feet use articulated heel, sole, and toe blocks with folded outrigger volumes. They
  must read as ground equipment, not boots.
- Manipulators use a palm carriage and articulated precision digits; no mitten blocks
  or conventional armored gloves.

### Asymmetry and identity

- Gren-Skildus remains character-left, broad, battered in shape, and structurally
  mounted through visible pins/brackets.
- Character-right remains an exposed industrial tool interface with guarded clearance.
- Gren-Skildus is represented by shape only during Workbench review; no jade material
  is used to rescue a weak silhouette.

### Form-density hierarchy

Detail density must be structural and concentrated:

```text
primary: yoke -> dorsal/thoracic rails -> pelvis -> leg members -> ground
secondary: powerplant cylinders, accumulators, radiator, joint housings
tertiary: hose placeholders, fastener markers, service brackets
```

Tertiary forms may not enter the silhouette or disguise unresolved primary structure.

## Reuse and provenance

- Do not import any Space Marine mesh, armor, skeleton, proportion set, or donor part.
- V1 procedural geometry may be consulted for scene scale only; it is not a shape
  donor.
- A future original human rig may retarget animation curves only when those curves are
  confirmed Aaron-owned and recorded by source hash.
- V2A primary geometry is authored from deterministic Blender primitives, curves, and
  original mesh profiles.
- The CC0 shortlist in `docs/OPEN_ASSET_SHORTLIST.md` is approved only for later
  secondary hoses, valves, gauges, fasteners, vents, materials, and environments.
- No external asset enters V2A. This eliminates license ambiguity from the silhouette
  gate.

## Dimensional and scene gates

- Ground-contact-to-yoke-apex: `2.4384 m +/- 0.0005 m`.
- Neutral ground contact: `Z = 0.0 m +/- 0.00025 m`.
- Metric scene; unit scale `1.0`; applied rigid-object scales.
- Character-left/right naming and Gren-Skildus placement are machine checked.
- Required primary modules and collections are enumerated in a separate JSON contract.
- Candidate is created from `--factory-startup --background`, never by opening V1.
- Output path is new and versioned:
  `blender/candidates/varek-chassis-v2a-static.blend`.
- Existing output means stop; no overwrite and no automatic retry.

## Workbench-only review gate

V2A saves and freezes the candidate before review. It renders with Workbench MatCap
clay from the frozen bytes without saving review-only mutations.

Required views:

1. front orthographic;
2. rear orthographic;
3. character-left orthographic;
4. character-right orthographic;
5. three-quarter perspective;
6. human-envelope cutaway/overlay.

Cycles is deliberately blocked during V2A. Materials, contact-shadow realism, and
volumetrics cannot compensate for a wrong chassis.

## Human visual acceptance

Aaron alone decides whether:

- the result resembles the approved concept rather than V1;
- the load path can be traced at a glance;
- the operator looks contained rather than replaced by a robot;
- the torso, yoke, pelvis, legs, feet, and hands feel purpose-built for rescue/load
  bearing;
- the silhouette reads approximately 90% industrial machine and 10% protective power
  equipment;
- the design avoids conventional power armor, generic robot, fantasy dwarf, and
  cockpit-mech drift.

A machine PASS cannot approve those claims.

## Evidence and failure behavior

The measurement record binds the concept, plan, contract, builder, validator, candidate,
Blender environment, scene dimensions, component inventory, render settings, and all
six output hashes.

Pre-build failure creates only a failure record. Post-build failure preserves the
diagnostic candidate and evidence. A visual failure is retained as a negative fixture.
There is no automatic V2A second attempt; another build requires a specific observed
cause and bounded plan amendment.

## Execution sequence

```text
commit this plan
  -> QA audit
  -> write V2A contract, builder, and validator
  -> static audit without execution
  -> run one V2A build
  -> independent readback
  -> show six views to Aaron
  -> STOP
```
