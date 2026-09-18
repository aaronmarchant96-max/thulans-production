# Thulans Production: Agent Operating Charter & Physical Mechanism Handoff Protocol

## 1. Physical Mechanism Handoff & Evidence Governance

For Varek's hand/tool interface, inspect `docs/HAND_PHYSICS_GATE.md` and `docs/VAREK_HAND_PHYSICS_TEST_ENVELOPE.md` before building, validating, or presenting a candidate as ready for approval.

### Non-Negotiable Rules
1. **No Superficial PASS Claims:** No static render, reference-point alignment, infinite-mass kinematic collider clamping, or intersection-only check can authorize handoff as a functioning grip.
2. **Anti-Claim-Drift Rule:** **Documentation claims must be generated from implemented test capabilities, not written ahead of them.** Never claim a test harness enforces constraints or metrics that are not explicitly executed in code.
3. **Decoupled 4-Layer Architecture:**
   - `tools/build_hand_physics_harness.py`: Builder script **only** (scene, binding, colliders, constraints). Hard-fails on missing components.
   - `tools/run_hand_physics_simulation.py`: Execution runner **only** (steps simulation scenarios, exports raw trajectory & local palm-frame logs).
   - `tools/validate_hand_physics_results.py`: Independent Oracle **only** (consumes raw JSON logs; never manipulates Blender directly; evaluates local slip, drift, and drop metrics).
   - `tools/mutate_hand_physics_candidate.py`: Adversarial mutant suite generator & evaluator (generates corrupted derivatives to test gate sensitivity).
4. **Adversarial Mutation Score Gate:** A candidate cannot pass unless the gate engine reliably rejects deliberately broken or corrupted candidates (48/48 mutation score). If a fraudulent scene passes, the gate itself fails.
5. **Prerequisite Claim Graph DAG:** No downstream PASS claim (e.g. Physics Hold) can override an upstream failure (e.g. Handedness, Connected Mechanism, or Acquisition Trajectory).
6. **Canonical Denominator Integrity:** Maintain permanent test IDs across the 9 layers (1,000 assertions). Never silently rewrite or weaken failing tests; retire bad tests with explicit rationale and increment versioning.

---

## 2. Narrative & Lore Authority Protocol

### Original Varek literary/cinematic continuity

For story, script, character motivation, dialogue, and cinematic beats in the Varek production, consult:
- `docs/THE_DISMANTLING_OF_VAREK.md`: canonical literary foundation and living story **for that continuity**.
- `docs/VAREK_ACTS_ONE_AND_TWO.md` & `docs/VAREK_ACT_THREE.md`: screenplay and prose master chapters.
- `RULINGS.md`: historical authoritative design rulings (RULING 001 through RULING 031 as previously documented). Do not silently revise existing rulings.

### Thulans: Deephearth game

Consult `docs/DEEPHEARTH_GAME_DIRECTION.md` for approved gameplay, art direction, and boundaries, and `docs/DEEPHEARTH_EVENT_FORGE_PLAN.md` for the **proposed, unimplemented** offline narrative prototype. The Varek story is a tonal/literary reference, not a required protagonist, plot or ending for the colony sim. Shared world facts still require checking the lore bible and rulings; distinguish world canon from cinematic-specific plot and proposed game mechanics. The user-approved concept art is a visual target, not a playable screenshot or a set of production-ready assets.

Across both projects, label decisions as established world canon, approved project direction, proposed design or verified implementation. Never promote a design plan or test target into an implemented or passed claim.