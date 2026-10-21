# The Thulans Production

> 📖 **The Thulans: The Weight of a Lie (Complete 12-Chapter Novella)**  
> **Read the Master Manuscript**: [**`novella/THE_THULANS_MANUSCRIPT_COMPLETE.md`**](novella/THE_THULANS_MANUSCRIPT_COMPLETE.md)  
> *Author: Aaron Marchant · Acts I–IV Complete · 23,233 Words · 100% Canon-Locked & Quality Audited*

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
