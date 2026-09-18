# Deephearth — Milestone 2: Godot Live UI Integration

Status: IMPLEMENTATION SPECIFICATION / NOT YET VERIFIED IN GODOT. Recorded 2026-09-18.

## Goal and authority

Bind the approved Deephearth cross-section visual direction to the actual Event Forge colony state, not hardcoded interface labels. This document records the author's Day 43 integration specification; Milestone 1 performance and tests were supplied as local evidence and have not been independently reproduced from this repository. The 2D pixel-art colony management view is the intended game, not a separate avatar-controlled mode.

The **simulation owns all resources, residents, relationships, event proposals, resolved effects and ledger entries**. Godot presents snapshots and sends commands. UI widgets must never directly mutate authoritative data or infer outcomes from a choice label. Use a versioned adapter between the Python prototype and Godot; choose and document either a faithful GDScript port or a local bridge only after inspecting the actual prototype. An optional local bridge must not silently become a cloud or paid API dependency.

## Day 43 fixture: expected UI bindings

| Element | Source | Expected fixture display |
| --- | --- | --- |
| Header resources | `ColonyState.resources` and capacity/presentation fields | Water 62% (124 L / 200 L); steam 58 PSI; rations 14 days; marks 27; dwellers 24/32 |
| Selected resident profile | Selected `Dweller` object | Bram; age 34; miner; health 42%; morale 68%; fatigue 76%; traits Diligent, Loyal, Chronic Cough, Family Man |
| Relationship | Selected `Dweller.bonds[target_id]` | Sanna +62, Close Friend |
| Active event | Current `EventProposal` | P01 Survival Through Concealment; dilemma and consequence previews supplied by the engine |
| Event options | Proposal's actual available choices | Hide Condition, Report to Overseer, Find Middle Path **only if each has an executable choice ID** |
| History | `ColonyState.consequence_ledger` | Historical entries on days 33, 35, 37, 40 and 42; day 43 entry appears only AFTER an actual commitment |

These are a test fixture's values, not global canon: Bram and Sanna are not required residents in every colony. Display a resource only in its actual measurement unit; distinguish water quantity from percentage and PSI from percentage. `24/32` is a fixture population/capacity display, whereas a proposed smaller first playable hearth can use fewer inhabitants. Do not imply the first playable simulation already supports 24 independently simulated residents unless measured.

## Read-only projection and command contract

Create a narrow adapter with these operations (logical contracts, not claims of existing Python method names):

- `load_snapshot() -> { schema_version, state_version, day, bell, resources, dwellers, selected_dweller_id?, active_events, consequence_ledger }`.
- `get_dweller(id) -> resident projection` containing ID, health, morale, fatigue, traits and relationships; UI selects by stable ID, not display name.
- `get_event(id) -> event projection` containing proposal ID, pattern ID, state version, validated choice IDs, preview descriptions and expiry, with no fabricated guaranteed outcomes.
- `resolve_event(proposal_id, choice_id, expected_state_version) -> { accepted, reason?, new_snapshot? }`. The authoritative executor revalidates immediately before committing; on stale state, death, failed prerequisites or another rejection, do not apply any UI-only deltas; reload snapshot and show the reason.
- `save_game(path) / load_game(path)` operate on authoritative versioned colony state, not rendered labels or panels. Save and reload the event lifecycle, RNG seed/state as needed, character knowledge, bonds, event cooldowns and committed ledger facts.

For Godot, separate `ColonyAdapter` (state access/commands), `ColonyScreen` (view and selections), `DwellerProfile`, `EventPanel`, `ResourceHeader`, and `EventLedger`. Use state-change signals or an equivalent explicit refresh to update every dependent widget from the accepted **new snapshot**. No per-frame polling of a Python service is needed to keep labels in sync.

## Visual reference acceptance

The September 18 user-approved concept image is a **target for live gameplay**: layered cross-section rooms, visible workers and lift, stone Gothic architecture, brass/steam/dieselpunk machinery, warm amber furnaces, cold blue-grey stone and water infrastructure, legible panels. Use reusable sprites, tile layers, animations and UI components; a static concept image used as a background with clickable rectangles does **not** satisfy the visual-production gate. Test at the actual window size with legible text and resident selection. Art/look acceptance is separate from functional data-binding acceptance.

## Required end-to-end acceptance tests

1. Launch the actual Godot project and show a living colony cross-section; select Bram by ID and verify Day 43 header, profile and +62 Sanna bond against the authoritative snapshot.
2. Present the active P01 proposal and render **only executable** choices. If Find Middle Path lacks an implemented command, hide or label it unavailable rather than simulating a fake effect. Consequence previews must be sourced from the proposal and must not claim guaranteed outcomes where probabilities or future discoveries exist.
3. Select Hide Condition in one fresh Day 43 fixture and Report to Overseer in a separately reset fixture. Verify each command reaches the authoritative executor, passes fresh pre-resolution validation and returns a committed snapshot. Only values with specified actual deltas must change; unaffected gauges must stay the same. Exactly one appropriate event-resolution ledger record is appended per successful choice.
4. Reopen an offered proposal after killing/moving its actor or otherwise invalidating its prerequisites. Verify rejection, no partial resource or ledger mutation, and an accurate UI refresh/error.
5. Save an accepted result, restart the game process, load it and compare canonical serialized state (or a stable canonical-state hash) against the pre-save result. Assert the same displayed gauges, traits, relationships, event states, ledger order and RNG continuity. Do not demand GPU screenshot bytes match bit-for-bit across devices; visual equivalence is a separate screenshot/layout test.
6. Produce an evidence record: Godot and adapter versions, code revision, command output, pass/fail assertions, screenshots or capture, and any unimplemented features. Benchmark frame time separately from Event Forge proposal generation latency.

## Exit criterion

Milestone 2 is complete **only** after a launched Godot UI is shown reading authoritative state, both supported P01 branches work end to end and save/reload passes. A fixture JSON file, mocked choice handler, scripted screenshot, or passing standalone Python tests alone do not complete this gate.
