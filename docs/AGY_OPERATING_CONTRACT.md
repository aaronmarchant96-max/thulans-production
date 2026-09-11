# AGY Operating Contract — thulans-production

Binding on any agent building in `thulans-production`. Aaron is the sole
authority for canon and scope. This contract overrides convenience.

## 1. Preserve — never delete or modify (RULINGS 010/011)

`Operator cell`, anchor boots (`Anchor sole *`, `Folded heel anchor *`,
`Foot_Toe_Cleat *`), `Gren Skildus` + brooch, load frames/yoke, helmet,
existing rig/animation, and any other agent's candidate blends.

Locked architecture is not an obstacle to prune for a camera view.

## 2. One pinned candidate

Exactly one working candidate at a time, with its SHA-256 recomputed from the
file on disk. All other variants are quarantined to
`evidence/failed-attempts/`. Never cite a hash from memory — recompute it.

## 3. Gate before claim

Run `tools/check_hand_physics_preflight.py` (read-only; prerequisite-only) and
the real clearance auditor **before** any PASS claim. No render, reference
alignment, or intersection-only result authorizes handoff.

## 4. Real auditor requirements

- Pose-activity assertion: `pose_position=POSE`; `pelvis`, `thigh.L`, `thigh.R`
  must actually move across the action. Hard-fail before collision analysis.
- All-pairs overlap plus per-mesh self-intersection.
- Writes a hash-bound JSON to the candidate's **own** evidence path. Never write
  to another candidate's evidence path.
- Exits nonzero on any prohibited intersection.

## 5. No PASS without evidence

A claim is valid only if a hash-bound evidence file exists in the repo and
reproduces on re-run. An asserted PASS is a violation.

## 6. Framing

Every geometry/visual claim uses a full-body render with **head and ground
contact both visible**. Close-ups are supplementary only.

## 7. Stop-and-ask

On the first gate failure, stop and report. Do not hack geometry — no bone
scaling, hardcoded world coordinates, or part deletion — to force a pass.

## 8. Boolean cutters

Must be winding-verified with `bmesh.ops.recalc_face_normals`. `normal_update()`
alone is insufficient. Verify with an in-memory winding test before use.

## 9. Scope freeze (AGENTS.md)

No new armor/materials/scenery/animation while the hand/tool interface is
unresolved. The graviton manipulator requires an explicit RULING 022 (Aaron) and
is treated as interface work; the hand/tool gate applies to the left-hand maul
grip.

## 10. Claim boundary

"Modeled kinematic/physical plausibility" only — never real-world safety or
manufacturability certification.

## 11. Attribution

CC0 donors (Quaternius) recorded in provenance. No imported fictional-mech
geometry.
