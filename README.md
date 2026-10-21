# The Thulans Production

> 📖 **The Thulans: The Weight of a Lie — revised twelve-chapter novella**  
> **Authoritative illustrated reading draft:** [Google Doc](https://docs.google.com/document/d/1UioMeG59Kw7xE6XvxoLRXy0SbkTXwg-6ktSO5QL2cpY)  
> **Repository text mirror:** [Complete manuscript](novella/THE_THULANS_MANUSCRIPT_COMPLETE.md)  
> *Aaron Marchant · Acts I–IV complete · 22,577 words of chapter and act text · Synchronized 21 October 2026*

The live Google Doc governs the current novella. The complete manuscript, partial-act compilations, and twelve chapter files below mirror its prose; the illustrated edition remains in Google Docs. The word count uses whitespace-separated chapter and act text, including headings, and excludes the cover and repository front matter. Recent reductions in Chapters Seven–Ten are intentional editorial cuts.

- [Current novella blueprint](docs/NOVELLA_BLUEPRINT.md)
- [Project handoff and outstanding work](handoff/PREFIX.md)
- [Current novella overview](docs/ONEPAGER.md)

A complete draft is not a claim of publication readiness or universal canon verification. Earlier production notes are retained in [the archive](docs/archive/READING_DRAFT_PRODUCTION_NOTES_2026-10-20.md).

This repository contains the complete novella manuscript, canonical assets, and production pipeline for **The Thulans** and the proposed colony-simulation game **Thulans: Deephearth**. These are related projects, not interchangeable narrative continuities.

## Deephearth game direction (September 18, 2026)

- Narrative spine: LOCKED v3.2 Empty Mountain arc, reconciled to RULINGS 022–031 (see
  `docs/THE_THULANS_LORE_BIBLE_v3.md`); Void/Interstice removed — non-canon (RULING 005);
  naming standard locked (RULING 014); Varek's absolute death + residual-machine epilogue
  (RULING 031)
- Varek V4 silhouette: human approved and hash-bound
- Exact engineering dimensions beyond 2.4384 m: unmeasured
- Static chassis: V2A.1 silhouette human-approved (gate `V2A1_STATIC_SILHOUETTE`);
  V2B rig/articulation underway
- Motion chassis: Blender execution no longer blocked (see RULING 011)
- Shot 01: rejected premature draft archived; rebuild blocked
- Soundtrack: source tracks preserved; mashup requires two lyric remediations before
  original-IP-clean release

## Original cinematic production status (historical project-specific gates)

Original cinematic-production workspace for **The Thulans** and Brothar Varek Fairgunjis, Thulan of the Old Hearths.

- Narrative spine: LOCKED v3.1 Empty Mountain arc **for the Varek literary/cinematic continuity** (see `docs/THE_THULANS_LORE_BIBLE_v3.md`); Void/Interstice removed — non-canon (RULING 005); naming standard locked (RULING 014).
- Varek V4 silhouette: human approved and hash-bound.
- Exact engineering dimensions beyond 2.4384 m: unmeasured.
- Static chassis: V2A.1 silhouette human-approved (gate `V2A1_STATIC_SILHOUETTE`); V2B rig/articulation underway.
- Motion chassis: Blender execution no longer blocked (see RULING 011).
- Shot 01: rejected premature draft archived; rebuild blocked.
- Soundtrack: source tracks preserved; mashup requires two lyric remediations before original-IP-clean release.

The production rule is claim -> measurement -> acceptance gate -> implementation -> verification -> human approval. Do not present historical gate statements as a fresh verification of the current working tree.

## Local integrity checks

Run the executable repository gates locally when GitHub Actions is unavailable:

```bash
python tools/run_local_ci.py
```

The command compiles the agent contract, audits the `HEAD^..HEAD` compliance
diff, runs the Python unit suite, and audits canonical claim records. Its
`PASS_SCOPED` result does not cover GitHub runner allocation, Blender execution,
physics simulation, renders, visual approval, or unimplemented assertions.
