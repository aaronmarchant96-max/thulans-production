---
status: active-standard
authority_scope: visual-atmosphere-and-cinematic-evaluation
owner: Aaron Marchant
author: AGY (Antigravity)
auditor: OpenCode
applies_to: cinematic-poc-track
---

# VISUAL ATMOSPHERE GATE (VAG) (RECONCILED)

## Principle: The Two-Tier Evaluation Doctrine
**Atmosphere cannot be automated.** Automated test suites assert *sameness* and *mechanical invariants* (palette conformance, character hashes, naming tiers). They can never assert whether a scene "feels right." 

A passing automated checklist is an audit aid, **never proof that the art is good**. Final atmospheric approval is strictly reserved for human review by Aaron via live renders and screenshots.

---

## Tier A: The Human Visual Atmosphere Gate (Aaron Approves)
Evaluated directly by Aaron from live renders and uncompressed screenshots. Every scene must clear all eight criteria before entering production.

| # | Criterion | Pass Condition | Verification Method |
|---|---|---|---|
| 1 | **Tone** | Administrative horror: restraint, cold institutional inertia, no action/spectacle, no clean sci-fi gloss. Tactile industrial (iron, coal smoke, oil-sheen, wet wool). | Visual inspection of scene mood and props. |
| 2 | **Intimacy Rule (RULING 001 amended)** | Human-scale framing is the strict default; the Mountain is experienced through the people it crushes. **Awe Exception:** Establishing and transitional shots may render Gothic-industrial architecture at colossal scale (Great Rift, brass-and-iron foundries, vertical chasm) without a person in frame to convey institutional dread and insignificance. The juxtaposition between overwhelming scale and intimate human struggle is mandatory. | Framing hierarchy & juxtaposition audit. |
| 3 | **Approved Palette (VAG-003)** | Strictly derived from the established Thulan spectrum: `#12171a` (deep slate), `#1c2326` (iron shadow), `#d8d2c0` (parchment/skin), `#e8a13c` (kerosene amber), `#b04a3c` (rust red). Automated scan acts as a partial control; final render appearance under opacity, gradients, and filters must be visually approved. Zero off-palette neon. | Render inspection + color spot checks. |
| 4 | **Lighting Logic** | Source-consistent (single kerosene wick, distant flue flare). Light falloff obeys physical obstruction. Warm/cold contrast carries narrative meaning (kerosene = fragile warmth; blue-gray = cold mountain). | Shadow angles and light falloff check. |
| 5 | **Readability** | Hotspots, documents, and interactive text are immediately legible at 1x desktop and mobile scales without visual clutter. | Typographic contrast check. |
| 6 | **Originality** | Distinct visual identity rooted in Thulan Gothic-industrial reality — **never a stylistic copy of As Dusk Falls or generic visual novels**. | Art style verification. |
| 7 | **Lore-Faithful** | Zero unauthorized elements. No magic, no mythical monsters, no anachronistic digital technology, no fantasy compounds. | Lore Bible / RULINGS cross-check. |
| 8 | **Cinematic Continuity** | Transitions preserve spatial orientation, character identity, and understandable chronology. Changes in composition, lighting, and perspective serve the narrative rather than appearing arbitrary. | Aaron reviews the complete sequence (Steward &rarr; Wulfila &rarr; Steward) at normal playback speed. |

---

## Tier B: Automated Consistency Suite (CI-Verifiable)
Automated vitest suite (`visual.consistency.test.ts`) that guarantees zero regression across scenes and builds:

1. **Palette Conformance (VAG-003)**: Scans scene CSS/SVG assets for disallowed hex/rgb literal color tokens as a partial static control.
2. **Character Identity (VAG-002)**: Separates stable canonical identity attributes (skin tone, hair silhouette, facial architecture) from approved expression/lighting variants (`dour`, `grim`, `alert`). Asserts core identity remains invariant while allowing expressive performance across scenes.
3. **Naming Verification**: Every name and location string must resolve to an approved tier in `NAME_CANON.md` (T1–T4).
4. **Anti-Slop Text Scan**: Scans all dialogue and scene text against `GDR_SLOP.md` (flags banned compounds, doctrine voice, and scale-only adjectives).
5. **Hotspot Geometry & Accessibility (VAG-001)**:
   - Normalized coordinate bounds: $0.0 \le x \le 1.0$, $0.0 \le y \le 1.0$, $w > 0$, $h > 0$.
   - Fully contained: $x + w \le 1.0$ and $y + h \le 1.0$.
   - Layering: Overlapping hotspots are permitted only when deterministic z-index priority is explicitly declared.
   - Accessibility: Must support standard keyboard focus (`tabIndex={0}`, `Enter`/`Space` activation) and responsive viewport scaling.
6. **Branch & State Integrity (VAG-004)**:
   - Asserts all narrative branches resolve to valid, defined terminal consequence states with zero unhandled transitions.
   - Terminal states are recognized as intentional endings, not dead ends.
   - Re-start capability verified: resetting clears state cleanly without stale flags.
7. **Asset Hash Receipts**: Pinned SHA-256 digests for all approved SVG background plates, audio cues, and portrait manifests.

---

## Scene Approval Contract Template

Each scene deliverable produces an immutable approval record:

```markdown
### Scene Approval Record: [SCENE_ID]
- **Source Revision**: [Git commit hash]
- **Asset SHA-256 Receipts**:
  - Background Plate: `sha256:...`
  - Interactive Hotspot Spec: `sha256:...`
- **Viewport Dimensions Tested**: 1920x1080 (desktop), 1280x720 (laptop), 390x844 (mobile)
- **Tier B Automated Consistency**: PASS (exit 0)
- **Independent Audit (OpenCode)**: ACCEPTED (Receipt ID: `...`)
- **Tier A Atmosphere Review (Aaron)**: APPROVED / REVISION REQUESTED
- **Approved Exceptions**: None / [Documented exceptions]
```
