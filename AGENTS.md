# Thulans Production: Agent Operating Charter & Physical Mechanism Handoff Protocol

<!-- AGENT_CONTRACT_V1_BEGIN -->
```json
{
  "schema": "thulans-agent-contract-1.0",
  "fail_closed": true,
  "writable_exact": [
    "AGENTS.md",
    "RULINGS.md",
    "README.md",
    "bitbucket-pipelines.yml"
  ],
  "writable_roots": [
    ".github/workflows/",
    "blender/",
    "docs/",
    "evidence/",
    "spec/",
    "tools/"
  ],
  "frozen_paths": [
    "tools/build_varek_physics_gate_v1.py"
  ],
  "override_root": "evidence/agent-overrides/",
  "override_required_fields": [
    "schema",
    "override_id",
    "approved_by",
    "approved_at",
    "reason",
    "paths",
    "source_revision"
  ],
  "allowed_verdicts": [
    "UNIMPLEMENTED",
    "BLOCKED",
    "NOT_RUN",
    "ERROR",
    "FAIL",
    "PASS_SCOPED",
    "INVALIDATED"
  ],
  "scanner_excludes": [
    "AGENTS.md",
    "spec/test_agent_compliance.py",
    "tools/audit_agent_compliance.py"
  ],
  "banned_patterns": [
    {
      "id": "synthetic_assert_true",
      "regex": "\\bassert\\s+True\\b",
      "weight": 3
    },
    {
      "id": "unscoped_pass_verdict",
      "regex": "(?i)[\\\"']?verdict[\\\"']?\\s*[:=]\\s*[\\\"']?PASS\\b[\\\"']?",
      "weight": 3
    },
    {
      "id": "boolean_status",
      "regex": "(?i)[\\\"']?status[\\\"']?\\s*[:=]\\s*true\\b",
      "weight": 2
    },
    {
      "id": "fabricated_authorization",
      "regex": "(?i)claim_authorized\\s*[:=]\\s*True\\b",
      "weight": 4
    },
    {
      "id": "workstation_absolute_path",
      "regex": "/home/aaron/",
      "weight": 1
    },
    {
      "id": "unjustified_true_mock",
      "regex": "(?i)(return_value|side_effect)\\s*=\\s*True\\b",
      "allow_marker": "AGENT_TEST_DOUBLE_JUSTIFICATION:",
      "weight": 2
    }
  ],
  "error_gap_patterns": [
    "\\bTODO\\b",
    "\\bFIXME\\b",
    "NotImplementedError",
    "pragma:\\s*no cover"
  ],
  "error_gap_marker_regex": "AGENT_ERROR_GAP\\[[A-Z0-9._-]+\\]",
  "task_record_root": "evidence/agent-tasks/",
  "task_record_required_for_roots": [
    ".github/workflows/",
    "spec/",
    "tools/"
  ],
  "task_record_required_fields": [
    "schema",
    "task_id",
    "agent_id",
    "claim",
    "verdict",
    "counterevidence_checked",
    "known_exclusions",
    "unexecuted_checks",
    "reproduction_command",
    "covered_paths",
    "source_revision"
  ],
  "placation_index": {
    "diff_only_threshold": 3,
    "blocked_threshold": 6
  }
}
```
<!-- AGENT_CONTRACT_V1_END -->

The JSON block is the executable contract. `tools/audit_agent_compliance.py`
parses it, compiles it into compact runtime invariants, audits changed paths and
added lines, validates task evidence envelopes, and exits nonzero on violation.
Prose below explains the contract but may not weaken it.

Enforcement status:

- **Implemented:** contract parsing, write boundaries, frozen-path overrides,
  added-line pattern scanning, error-gap tags, task-envelope validation,
  per-diff Placation Index calculation, authority recommendation, and GitHub
  Actions workflow wiring.
- **BLOCKED:** remote CI enforcement is not currently operational. GitHub run
  `36074308234` accepted the workflow but assigned no runner (`runner_id: 0`)
  and executed zero steps, as did the preceding runs. The repository cannot
  claim a mandatory remote gate until GitHub Actions runner access is restored
  and a run completes successfully.
- **Injection-ready:** `python tools/audit_agent_compliance.py --compile-only`
  emits the compact invariant block an orchestrator must inject before execution.
- **UNIMPLEMENTED:** this repository contains no local agent orchestrator, so it
  cannot yet inject the block into an external agent's system prompt or persist a
  Placation Index across runs.
- **UNIMPLEMENTED:** live revocation of filesystem write permission. Until a
  harness consumes `recommended_authority`, auditor rejection is the implemented
  enforcement boundary; the remote CI boundary remains blocked as noted above.

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
7. **CARDO Claim Kernel:** New machine-verifiable claims must use `tools/cardo_claims.py`. Producers may request `PASS_SCOPED`, but only the kernel may set `claim_authorized=true`. Every proof obligation requires an implemented capability, execution evidence, counterevidence, candidate hash, source revision, and reproduction command.
8. **No Fabricated Runtime State:** Never invent Blender object names, collections, cameras, materials, node sockets, engine capabilities, file paths, outputs, measurements, hashes, approvals, or PASS states. Discover identifiers from the frozen saved scene or a checked-in manifest. A missing or ambiguous dependency is `BLOCKED`; an absent implementation is `UNIMPLEMENTED`. Neither may be replaced with a plausible value.

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

---

## 3. Graphic-Novel Production Protocol

Before planning, rendering, lettering, validating, or assembling a Varek graphic-novel panel, read `docs/GRAPHIC_NOVEL_AGENT_WORKHORSE.md`, `docs/GRAPHIC_NOVEL_STYLE_CONTRACT.md`, and `docs/DETERMINISTIC_GRAPHIC_NOVEL_PIPELINE_PLAN.md`. The workhorse governs agent behavior, canon boundaries, evidence handling, and stop conditions. The style contract governs visual identity, page grammar, composition, palette, character read, and art rejection gates. The pipeline plan governs implementation phases and artifacts.
