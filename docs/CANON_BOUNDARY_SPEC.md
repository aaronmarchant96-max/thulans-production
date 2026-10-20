# Thulan Repository Canon Boundary Specification

## Purpose

To prevent drift, protect finished assets, and maintain clear separation between foundational world rules, active production files, and generative experiments.

---

## The Three Tiers of Authority

```
┌─────────────────────────────────────────────────────────────┐
│ TIER 1: LOCKED CANON (Immutable Foundations)                │
│ RULINGS.md, NAME_CANON.md, STORY_BIBLE.md, VIOLENCE_DOCTRINE│
└──────────────────────────────┬──────────────────────────────┘
                               │ Governs & Constrains
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ TIER 2: PRODUCTION TRACK (Active Production Assets)         │
│ episodes/, Blender rigs, locked audio, shot ledgers         │
└──────────────────────────────┬──────────────────────────────┘
                               │ Informs & Tests
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ TIER 3: EXPERIMENTAL / PROMPTS (Exploration & Scratch)       │
│ REI raw outputs, Suno dumps, exploratory scripts, donor mesh│
└─────────────────────────────────────────────────────────────┘
```

### Tier 1: Locked Canon (Immutable)
* **Definition**: Ground truth of the Deephearth universe. Any contradiction is an error.
* **Key Files**:
  * `RULINGS.md`: Precedents, physical world limits, and historical boundaries.
  * `docs/NAME_CANON.md`: Approved naming syntax and linguistics.
  * `docs/THULAN_VIOLENCE_DOCTRINE.md`: Rules of physical consequence and martial pride.
  * `docs/THE_THULANS_LORE_BIBLE_v3.md`: Macro social structure and political economy.
* **Rule**: No automated script or subagent may alter Tier 1 files without explicit user review.

### Tier 2: Production Track (Active Implementation)
* **Definition**: Concrete production artifacts created to release episodes, trailers, and playable prototypes.
* **Key Directories**:
  * `episodes/00X_*/`: Script specs, locked audio files, shot ledgers, rendering passes.
  * `build_varek_v*.py`: Validated Blender mesh builders and material pipelines.
  * `assets/audio/`: Mastered takes and clean stems.
* **Rule**: Production assets must conform 100% to Tier 1 constraints before being marked as locked.

### Tier 3: Experimental / Story Generation (Sandboxed)
* **Definition**: REI brainstorming outputs, AI image-to-video trials, unvetted Suno tracks, and concept sketches.
* **Key Directories**:
  * `archive/`, `scratch/`, `handoff/`
* **Rule**: Material in Tier 3 has zero canon authority until formally audited, refined, and promoted into Tier 2 or Tier 1.
