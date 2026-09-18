# Deephearth Event Forge — Offline Narrative Prototype Plan

Status: PROPOSED / NOT IMPLEMENTED. Updated 2026-09-18. This is the game-specific adaptation of the user's Story Forge concept, not a claim that Story Forge already exposes an API or that the game engine exists.

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

## Initial authored pattern candidates (not locked quests)

P01 Survival Through Concealment; P02 The Diverted Shipment; P03 Names Beneath the Stone; P04 The Unsealed Flue; P05 The Cold Tithe; P06 The Broken Gauge; P07 The Surface Rumor; P08 The Stolen Filter-Salt; P09 The Silent Sump; P10 The Returning Bell.

Thresholds, resource names, numeric values, role names and PSI figures from the draft are illustrative and require simulation/lore approval. A low resource value does not prove theft; debt does not prove falsified records; a missing resident is not necessarily dead. Resident names from the concept short story are not hardcoded requirements.

## Proposal contract (design target)

Store event ID, pattern ID and version, seed, source-pattern provenance, trigger facts, referenced colony-state version, actor IDs, location IDs, eligibility and knowledge predicates, player options, preconditions, proposed effects, expiry, and cooldown/deduplication key. Separate immutable observed facts, character beliefs, suspicions and newly introduced fiction. Dialogue may only reference validated facts or explicitly attributed beliefs.

## First prototype and tests

A Python-only test harness is a proposed rapid experiment; production Godot integration and Python-to-GDScript parity are not verified. Prefer portable data schemas, not assumptions of 1:1 class portability. Suggested modules: colony_state, story_patterns, role_matcher, event_validator, event_forge, event_executor, event_ledger, plus fixtures and tests.

Acceptance target: ten authored patterns, 100 seeded colony snapshots, rejection of deliberately corrupted proposals, acceptance of valid proposals, atomic and persistent consequence updates, replay with matching initial state and seed, and a later event demonstrably responding to a prior committed fact. Report rejection reasons, false rejections, repetition/collision frequency and measured execution timings. Do not claim zero bugs, infinite variety, 100% lore accuracy, or benchmark speeds before evidence exists.

## Optional future capabilities

Local or hosted language models, a Python service, editor AI and reinforcement learning are exploratory enhancements, not requirements. The baseline game should function offline without per-event API calls.