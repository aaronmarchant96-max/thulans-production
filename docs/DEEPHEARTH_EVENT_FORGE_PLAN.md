# Deephearth Event Forge — Offline Narrative Engine

Status: **MILESTONE 1 LOCALLY REPORTED AS VERIFIED; REPOSITORY EVIDENCE NOT YET INSPECTED. MILESTONE 2 SPECIFIED / NOT VERIFIED.** Updated 2026-09-18. This is the game-specific adaptation of the user's Story Forge concept; it does not establish that Story Forge exposes an API or that Godot is already connected.

## Purpose

Generate grounded colony dilemmas from live simulation facts and curated narrative patterns without requiring cloud inference. Story Forge contributes the *source pressure* and story hinge; the colony simulation remains authoritative over physical state, resident identity, knowledge and outcomes. Historical source inspiration must remain distinguishable from fictional Thulan events.

## Pipeline and lifecycle

1. Detect a real trigger (resource threshold crossing, injury, expedition result, debt or unresolved consequence).
2. Select an eligible authored story pattern.
3. Assign existing residents and locations to required roles.
4. Validate actor status, reachability, prerequisite knowledge, exact numerical state and world-lore constraints. Also check duplicate/active-event collisions.
5. Offer a validated dilemma. Revalidate against current state before resolving the chosen action.
6. Commit physical changes and consequence-ledger facts atomically; otherwise reject without partial mutation.

Lifecycle: TRIGGERED -> PROPOSED -> VALIDATED -> OFFERED -> RESOLVED -> COMMITTED. Rejection and expiration are explicit alternative states. A proposal is not an event that already happened. Seeded randomness is reproducible only with the same seed, initial state and rules version.

## Ten authored pattern identifiers (locally reported implemented)

P01 Survival Through Concealment; P02 The Diverted Shipment; P03 Names Beneath the Stone; P04 The Unsealed Flue; P05 The Cold Tithe; P06 The Broken Gauge; P07 The Surface Rumor; P08 The Stolen Filter-Salt; P09 The Silent Sump; P10 The Returning Bell.

Thresholds, resource names, numeric values, role names and PSI figures from the draft are illustrative until checked against the implementation and approved lore. A low resource value does not prove theft; debt does not prove falsified records; a missing resident is not necessarily dead. Resident names from the concept short story are not hardcoded requirements.

## Proposal contract

Store event ID, pattern ID and version, seed, source-pattern provenance, trigger facts, referenced colony-state version, actor IDs, location IDs, eligibility and knowledge predicates, player options, preconditions, proposed effects, expiry, and cooldown/deduplication key. Separate immutable observed facts, character beliefs, suspicions and newly introduced fiction. Dialogue may only reference validated facts or explicitly attributed beliefs.

## Milestone 1: user-supplied local evidence, 2026-09-18

The author reports running `python3 -m unittest discover tests` against a **local** `prototype/` directory. The supplied output states:

- 11/11 tests passing, 100 seeded colony snapshots evaluated, 90 valid proposals and 10 incompatible proposals rejected, with no snapshots lacking a trigger.
- All ten patterns P01–P10 exercised; reported average generation latency 0.026 ms and maximum 0.050 ms for this benchmark.
- Tests reportedly reject deliberately corrupted proposals, reject stale proposals after an actor dies, roll back failed execution, and chain committed consequences into later dweller knowledge and events.
- `fixtures/generate_mockup_state.py` reportedly produces a Day 43 example with water 124/200 L (62%), pressure 58 PSI, marks 27, Bram's 45-mark debt, a +62 Sanna bond, and the P01 concealment proposal.

**Evidence boundary:** These are reported results, not an independently reproduced test run. The linked GitHub repository did not expose an accessible `prototype/` implementation or fixture at the time of this documentation update. 90% valid proposals is the benchmark's *proposal yield*, not a 90% validator correctness measurement. An 11-test PASS does not alone prove every possible corrupted state is rejected, zero bugs, Godot framerate, or universal offline performance. Record the exact code revision, Python version, test command, fixture contents, baseline snapshots and benchmark method once the code is available.

## Milestone 2: Godot live UI integration

The authoritative UI data bindings, Day 43 example, command contract, visual acceptance and end-to-end save/load tests are specified in [`DEEPHEARTH_MILESTONE_2_UI_CONTRACT.md`](DEEPHEARTH_MILESTONE_2_UI_CONTRACT.md). Milestone 2 requires a **launched Godot scene** reading actual engine state, selectable resident, real P01 choices and a persisted result; it is not complete when a fixture or mockup alone matches the concept art.

## Optional future capabilities

Local or hosted language models, a Python service, editor AI and reinforcement learning are exploratory enhancements, not requirements. The baseline game should function offline without per-event API calls.