# Thulans Production: Agent Operating Charter & Physical Mechanism Handoff Protocol

> **Read first:** `handoff/PREFIX.md` — the frozen resumption prefix (canonical
> artifacts, gate state, tooling, open rulings). It is the single handoff anchor and
> must be updated in the same commit as any state change.

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

For the current twelve-chapter novella, the [live Google Doc](https://docs.google.com/document/d/1UioMeG59Kw7xE6XvxoLRXy0SbkTXwg-6ktSO5QL2cpY) is authoritative. Chapter One in `novella/THE_THULANS_MANUSCRIPT_COMPLETE.md` and `novella/chapter_01.md` matches the accepted live text as of 24 October, including the three restrained readability edits. Chapters Two–Twelve retain their 21 October snapshot; consult `handoff/PREFIX.md` for later live edits. Do not overwrite the live draft with a stale mirror. The current `docs/NOVELLA_BLUEPRINT.md` describes the written novella. For the approved literary continuation, read `docs/REBELLION_SAGA_DIRECTION.md` and RULINGS 034/036: the rebellion rises through working communities toward the Spire; book count, detailed geography, sequel dates, and the final outcome remain open. *Salvation* is the author-confirmed canonical companion story; *Eleven Bells* is an earlier pre-story prototype preserved separately. For the Welded and *Salvation*, read RULING 035 and `docs/SALVATION_STORY_DIRECTION.md`: Ansen and Nessa are siblings; the later search must preserve his Chapter Ten/Eleven presence. The new bronze monument, reused empty frame, and working nursery pump are distinct. Varek remains dead. Broader literary, cinematic, and game documents below retain their own scope; do not import an incompatible scene or timeline into the novella.

For all story, script, character motivation, dialogue, and cinematic beats, consult:
- `docs/THE_DISMANTLING_OF_VAREK.md`: **Canonical Literary Foundation & Master Living Story.**
- `docs/VAREK_ACTS_ONE_AND_TWO.md` & `docs/VAREK_ACT_THREE.md`: Screenplay & prose master chapters.
- `RULINGS.md`: Authoritative design rulings (RULING 001 through RULING 036).
- `docs/AUDIENCE_PRIMER.md` & `docs/AUDIENCE_NAMES.md`: **Audience gate** — the first-contact
  primer and the naming gate (which names/terms may surface in marketing, trailers, and
  first-act screenplay, and the six-name ceiling). Consult before writing or approving any
  audience-facing material.

---

## 3. Token Policy (all agents)

The model is cheap; context is what costs. Obey:
1. Never read a whole large file — grep the symbol, then read ~20 lines at the offset.
2. Delegate broad search to the `explore` subagent; it returns one paragraph, not raw files.
3. Cap every command's output (`--porcelain`, `| head`, `-q`); never dump large results.
4. Reuse `handoff/PREFIX.md` instead of re-deriving state; keep the prefix byte-stable so prompt caching hits.
5. One task per session; when work closes, let compaction run — do not sprawl.
6. Use the cheapest model that can do the job; reserve reasoning for planning only.
7. Batch independent tool calls into a single turn.
8. Never paste or re-read content already pinned in context.

---

## 4. The Thulans Novel Manuscript & CARDO Method Invariants

When the author opens OpenCode to write or edit the novel, the agent is immediately locked into this exact creative framework:

- **Active Work**: *The Thulans: The Weight of a Lie (or The Dismantling of Varek)*.
- **Narrative Architecture**: Twelve chapters across four acts. The repository currently contains 22,424 words of chapter and act text after the 24 October Chapter One synchronization; Chapters Two–Twelve remain the 21 October snapshot. This is not a current live-Doc total. The former ~40,000-word target is historical, not a missing-text requirement.
- **Current Manuscript State**:
  - All twelve chapters are complete in the live Google Doc. Chapter One in both repository manuscript files was synchronized on 24 October. Later live updates to Chapters Two–Twelve, including the separately approved Chapter Twelve rebellion seed, are recorded in `handoff/PREFIX.md` and have not been synchronized. The larger Chapters One–Four readability trial remains a comparison proposal, not an adopted replacement.
  - Character and rhythm revisions are incorporated. Do not restore older passages merely to match an earlier count.
  - Remaining editorial questions: Chapter Six threat dialogue, geological timescale across the six-year epilogue, and selective rhythmic variation. These are review items, not authorization to invent lore or require a quota of new interior passages.
- **The CARDO Method (`docs/CARDO_STORY_METHOD.md`)**:
  1. **Locate the Hinge First**: Every scene pivots on a structural turning point where a character's assumption breaks and their trajectory irreversibly shifts.
  2. **Phase 0 Character Driver**: Identify what the character wants, what they fear, and what concrete physical event forces the turn.
  3. **Show, Do Not Summarize**: Zero abstract emotion tags ("he felt despair"). Deliver the scene entirely through physical labor, cold grease, broken seals, tactile tools, and sharp subtextual dialogue.
  4. **Never Announce the Twist**: No narrative hand-waving or editorial telegraphing. Consequences land through concrete physical events.
  5. **Conclusion Discipline**: Never close on a moralizing or summarizing wrap-up. End with a hard, tangible physical action, image, or line of dialogue.
- **The Voice Contract (`docs/THULAN_NOVELLA_VOICE_CONTRACT.md`)**:
  - **Zero AI Slop**: Strict ban on *tapestry, delve, palpable, symphony, dance, crescendo, ethereal, eerie*.
  - **McCarthy/Abercrombie Cadence**: Short, heavy, monosyllabic verbs landing like an eight-pound sledge.
  - **Character Speech Registers**:
    - *Bram (13; turns 14 on 30 October)*: Literal, naive, cold shins, dropped hex nuts.
    - *Kaelen (58)*: Shop-floor curt, missing a fingertip, tallow candle clamped in teeth, cynical loyalty.
    - *Varek (300+)*: Heavy manganese steel, steam-driven oil hydraulics, acoustic resonance, words burn auxiliary air.
    - *Sanna (18)*: Domestic triage, boiling leek roots on red coal clinkers, unflinching.
    - *Theodemir (70)*: Exhausted administrative clerk with slate and chalk, calculating 1-in-7 casualty budgets.
- **The Violence Doctrine (`docs/THULAN_VIOLENCE_DOCTRINE.md`)**:
  - *"The violence is fast. Understanding what happened is slow."*
  - **The Three Beats**: [1. Impact] instantaneous kinetic trauma $\rightarrow$ [2. Recognition] mechanical comprehension $\rightarrow$ [3. Residue] permanent physical evidence and constraints.
  - Zero torture spectacle, zero action-movie quips, zero physically impossible survival.
- **GDR Anti-Slop & Prose Discipline (`docs/GDR_SLOP.md`)**:
  - Strict ban on generic fantasy compounds and self-important adjective inflation (*unyielding, monumental, profound, relentless, seamless*).
  - RULING 001: If a word exists only to make the setting or proposal sound larger, cut it.

