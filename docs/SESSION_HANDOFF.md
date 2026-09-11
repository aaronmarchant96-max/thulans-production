# Session Handoff — Workspace Confusion & Next-Session State


> Written 2026-09-10 to capture ground truth for the next agent session.
> **Switch to opencode is in progress. Read this file first.**


## CRITICAL: Two separate git repos were conflated


The file-tooling and the shell resolved paths against **different roots**,
which caused the majority of confusion and wasted tokens this session.


| Repo | Git root (verify with `git rev-parse --show-toplevel`) | Purpose |
|------|------|---------|
| **Animation** (real Blender work) | `/home/aaron/animation/thulans-production` | Varek / Fault Maul Blender candidates, evidence, hand-physics gate. **This is the authoritative repo for the 3D work.** |
| **REI** (app) | `/home/aaron/repos/rei-ai` | REI AI router web app. NOT the Blender repo. The terminal shell started here by default this session. |


**Do NOT assume `pwd` matches the repo you must edit.** Verify the target repo's
git root before creating/editing files; then use **absolute paths** beginning
`/home/aaron/animation/thulans-production/` for any 3D work.


## Authority files (read before building/validating/presenting)

- `/home/aaron/animation/thulans-production/docs/STATE_OF_PRODUCTION.md` — **EXECUTIVE PRODUCTION SUMMARY:** Single-page master audit of what is built, what works, what is broken (the wrist/hand physics bottleneck), and the critical path forward.
- `/home/aaron/animation/thulans-production/docs/VAREK_HAND_RIG_SPEC_v1.md` — **MECHANICAL SPECIFICATION:** The engineering contract for left-hand wrist gimbal, 3 digits + opposable thumb, and right-arm 3-talon graviton mount, with measured chassis dimensions.
- `/home/aaron/animation/thulans-production/docs/THE_DISMANTLING_OF_VAREK.md` — **CANONICAL STORY & THEMATIC SOUL:** The definitive story of Varek's voluntary industrial deconstruction, his physical touch, and the state's post-mortem mythmaking. Read before writing any lore, dialogue, or script beats.
- `/home/aaron/animation/thulans-production/docs/VAREK_ACTS_ONE_AND_TWO.md` — Acts One and Two master prose text.
- `/home/aaron/animation/thulans-production/docs/VAREK_ACT_THREE.md` — Act Three master prose novella (Chapters 11–15: The Spanners, The Severing, The Unmasking, The Touch, and The Monument/Malakor resolution).
- `/home/aaron/animation/thulans-production/docs/THE_THULANS_FEATURE_PITCH.md` — 90-minute two-act screenplay treatment (with Malakor resolution & 19-day physical proof).
- `/home/aaron/animation/thulans-production/docs/THULAN_POLITICAL_ECONOMY.md` — The Dual Grindstones: Totalitarian planning + extractive monopoly ("Everything belongs to everyone. Everything has a price. And somehow, you own nothing.").
- `/home/aaron/animation/thulans-production/docs/THULAN_CULINARY_TRADITIONS.md` — Canonical food and cultural philosophy ("Impoverished pantry, aristocratic technique").
- `/home/aaron/animation/thulans-production/docs/THULAN_CULINARY_READER.md` — Condensed Reader's Edition & Production Matrix (condenses the 10 arts & 6 regions into reference tables).
- `/home/aaron/animation/thulans-production/docs/THULAN_CANONICAL_FRAGMENTS.md` — Primary in-world source texts: Tier Two school primer, merchant charter, written-out Hearth Black recipe with raw origins, and the conspiracy of silence scene.
- `/home/aaron/animation/thulans-production/docs/THULAN_LITERARY_INSPIRATIONS.md` — The 30 dystopian short story studies defining the dual grinding stones (anti-capitalism vs anti-collectivism).
- `/home/aaron/animation/thulans-production/RULINGS.md` — Canonical design rulings (RULING 001 to RULING 026). Note RULING 024 for *Faírg-Tygil*, RULING 025 for culinary philosophy, RULING 026 for political economy.
- `/home/aaron/animation/thulans-production/AGENTS.md` — short rule: read
  `docs/HAND_PHYSICS_GATE.md` before building. No static render/reference/intersection
  PASS authorizes handoff. Preflight pass is prerequisite-only.
  Do NOT expand scope (armor/materials/scenery/animation) while interface unresolved.
  Do NOT rotate the hand to fix the camera.
- `/home/aaron/animation/thulans-production/docs/HAND_PHYSICS_GATE.md` — the 7-step
  sequence and the "Inputs that must exist before simulation" (currently UNSET).


## Current ground truth (verified this session)


- Blender GUI is open with `varek-carry-v15.blend` loaded (absolute path). That is
  the newest carry-lineage whole-character model (hip-clearance work v13→v15).
- No geometry was modified anywhere this session. Nothing was committed.
- Source candidate hashes (read-only, verified):
  - `blender/candidates/varek-articulated-grip-v12.blend`
    SHA-256 `c420feaa0d01d0604ce466cc8fca8f7d032fe01f3c761083471484702fdc81ad`
  - `blender/candidates/varek-hand-v10.blend`
    SHA-256 `9bf78724a82a0573e0c816597ed278e7214975e3aebdb027de63aa7084df810d`
- Preflight tool: `tools/check_hand_physics_preflight.py` (fail-closed, read-only).
  Rejects v10 for wrong-side wrist + fixed fingers + missing physics world.
- Spec regression test: `spec/test_hand_physics_preflight.py`.


## Decisive audit finding (verified against the 3 read-only probes)


The three completed STAGE -1A probes (namespace, poseparam, origins — all in
`tools/audit_wrist_v12_*.py`) show V12 (`varek-articulated-grip-v12`) does **not**
articulate a real wrist joint. `hand.R` swings only 0–0.022° across 168 frames;
the 6.96–36.17° "wrist deflection" is forearm (~30°) + upper-arm (~9°) lever swing.
`hand.R` is effectively rigidly carried. So no physics harness can pass V12 until a
genuine, correct-side rotational wrist mechanism exists.


## Agreed next-step sequence (from prior session, awaiting reconfirmation)


The user confirmed sequencing (rebuild wrist mechanism **first**, then the
finite-force rigid-body validator against it). Decision still open: whether to also
broaden the gate to full-body carry (footing/balance/swing clearance) — recommended
to keep separate/secondary.


## Known broken items to fix at session start


1. **Workspace root:** confirm and pin to `/home/aaron/animation/thulans-production`.
   Use absolute paths for file ops. Do not trust `pwd`.
2. The binding-audit write (`tools/audit_wrist_v12_binding.py`, STAGE -1A(d)) was
   never reliably persisted in the animation repo. Re-confirm its presence/location;
   if missing, recreate and run read-only before any geometry change.
3. The file-tool absolute-path writes DID reach `/home/aaron/animation/thulans-production`,
   so that is likely correct; but verify with a hash after any create/edit.


## Anti-fabrication reminder


Never claim a fix/render/PASS without: (a) files actually in the animation repo,
(b) real Blender stdout, (c) hash-pinned candidate. If the tool paths disagree, STOP.
