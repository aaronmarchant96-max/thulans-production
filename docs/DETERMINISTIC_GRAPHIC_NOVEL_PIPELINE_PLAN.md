---
status: PROPOSED_IMPLEMENTATION_PLAN
authority: AGENTS.md; docs/CARDO_REI_CLAIM_KERNEL.md; docs/BLENDER_RENDER_PIPELINE.md
scope: Varek cinematic stills and graphic-novel pages only; not Deephearth game production
---

# Deterministic 3D-to-Graphic-Novel Pipeline Plan

## 1. Outcome and claim boundary

Create reproducible graphic-novel pages from frozen Blender scenes. A panel
must be regenerable from a declared scene, camera, frame, render profile, and
panel manifest. The pipeline produces page-ready visual assets; it does not
authorize mechanical function, game implementation, real-world engineering, or
human art approval.

The first production deliverable is **one three-panel proof page**. It is not a
full issue, a complete chapter, or a new Varek asset build.

## 2. Ground truth and constraints

### Implemented foundation

- The repository contains a CARDO Claim Kernel, canonical evidence validation,
  hash-bound candidate patterns, and headless Blender command guidance.
- Existing Varek render scripts are largely Workbench or Cycles diagnostics.
- The Varek hand/tool physics gate remains blocked. Its visual material may be
  used as an explicitly non-physical scene subject, never as a functioning-grip
  claim.

### Not established

- No panel manifest format, page assembler, vector line-art exporter, comic
  compositor, print profile, or Krita template is currently implemented.
- No checked-in `.blend` candidate is available in this repository checkout.
- The mutation and finite-force physics work remain separate critical work;
  this plan does not bypass them.

### Render authority

EEVEE is the final panel master for this scoped graphic-novel pipeline. Its
Grease Pencil Line Art, Shader-to-RGB, fast repeatable rendering, and
compositor-oriented pass workflow are a better fit for print-style panels than
Cycles path tracing. Cycles remains the diagnostic reference for material and
lighting comparison, not the default page-production engine.

No external Blender add-on is part of the first build. Lightning Boy Shader,
Malt, BEER, and Clip Studio Paint may be evaluated later, but they are not
dependencies of the deterministic baseline.

## 3. Architecture

```text
frozen .blend + panel manifest
        |
        v
headless Blender panel renderer
        |-- EEVEE panel master (PNG or EXR)
        |-- EEVEE tone-ID derivative
        |-- Grease Pencil Line Art (SVG + PNG)
        |-- normal/depth/mask passes (multilayer EXR)
        v
CARDO panel evidence record
        |
        v
deterministic compositor
        |-- halftone derivative
        |-- panel preview PNG
        v
SVG page assembler
        |-- print-preview PDF
        |-- raster review PNG
        v
Krita human finishing copy
```

The frozen Blender input and programmatic page output are authoritative. Krita
edits are editorial derivatives: they must be exported with a sidecar note of
manual changes and may never overwrite the generated master.

## 4. Canonical artifact contract

Each panel lives in `evidence/graphic-novel/<page_id>/<panel_id>/` and contains:

```text
panel-manifest.json          declared inputs and artistic scope
claim.json                   CARDO authorization record
panel-master.exr             EEVEE final panel master
panel-master.png             review derivative
tone-id.png                  three-band EEVEE tonal classification
lineart.svg                  editable vector linework
lineart.png                  raster preview of the same linework
masks.exr                    depth, normal, object/material Cryptomatte passes
halftone.png                 deterministic compositor result
panel.png                    final generated panel derivative
```

`panel-manifest.json` must declare:

- Stable page and panel IDs.
- Input `.blend` path and SHA-256.
- Source commit SHA, Blender version, command, camera, and frame.
- Resolution, color management, render engine, samples, seed, and pass list.
- Line-art source collection and enabled categories.
- Tonal thresholds, halftone frequency, angle, and deterministic seed.
- Mechanical claim references, visual claim references, exclusions, and script
  dialogue reference.

Any changed input invalidates the generated panel and its page placement.

## 5. Pass rules

| Pass | Tool | Required role | Prohibited claim |
|---|---|---|---|
| Panel master | EEVEE | final graphic-novel image | mechanical correctness |
| Line art | Grease Pencil Line Art | character, machinery, contour and selected crease lines | collision/physics proof |
| Background edge | compositor depth/normal | distant rock and dense industrial detail | vector-quality foreground ink |
| Tone ID | EEVEE Shader-to-RGB | discrete lit/mid/shadow classification | mechanical correctness |
| Halftone | compositor | screen-space dots, hatch, soot texture | independent lighting model |
| Cryptomatte | multilayer EXR | post-selection masks | permanent named-object authority |
| Page | SVG/PDF | panels, gutters, balloons, captions | final human lettering approval |

Intersection line art is optional and default-off. It is a visual effect only;
it cannot imply valid floor contact, collision clearance, or force transfer.

## 6. Deterministic controls

1. **Frozen input.** Compute scene SHA-256 before and after rendering. The
   renderer never saves the source scene.
2. **Declared camera.** Every panel names one camera object; no active-camera
   fallback is permitted.
3. **Fixed render profile.** Resolution, engine, samples, color transform,
   compositor settings, and random seeds live in the manifest.
4. **Dual line output.** Store both SVG and raster preview. Never call a PNG
   “resolution independent.”
5. **Screen-space tone texture.** Halftone coordinates are panel-space and
   seeded. They are generated after tonal classification, not separately in
   every material.
6. **Named masks.** Cryptomatte selection maps to a frozen object/material
   registry in the manifest; arbitrary renames invalidate the mask contract.
7. **No silent manual fix.** Krita edits are described in an edit ledger and
   never replace the deterministic source assets.
8. **Independent readback.** The panel validator consumes files and manifests
   written to disk; it never authorizes from the renderer's in-memory state.

## 7. CARDO claim model

Use `tools/cardo_claims.py` for each panel and page.

### Panel proof obligations

- `PANEL.INPUT_HASH_BOUND`
- `PANEL.CAMERA_EXISTS`
- `PANEL.FRAME_RENDERED`
- `PANEL.REQUIRED_PASSES_EXIST`
- `PANEL.LINEART_VECTOR_AND_PREVIEW_MATCH`
- `PANEL.TONE_PROFILE_BOUND`
- `PANEL.HALFTONE_SEED_BOUND`
- `PANEL.PROVENANCE_REPRODUCIBLE`

### Page proof obligations

- `PAGE.PANEL_MANIFESTS_AUTHORIZED`
- `PAGE.PANEL_CROPS_MATCH_LAYOUT`
- `PAGE.GUTTERS_AND_BLEED_VALID`
- `PAGE.FONT_LICENSES_DECLARED`
- `PAGE.PDF_AND_PREVIEW_EXIST`
- `PAGE.REPRODUCIBLE_FROM_LEDGER`

Every page and panel remains `PASS_SCOPED`; human readability, staging, tone,
and lettering remain separate review decisions.

## 8. Anti-hallucination protocol

The pipeline must derive runtime facts from files and Blender readback. Prompts,
plans, prior messages, filenames in prose, and agent confidence are not runtime
evidence.

### Source-of-truth order

1. Frozen saved `.blend` opened by the declared Blender version.
2. Checked-in manifest bound to that file's SHA-256.
3. Independent readback written after the operation.
4. Generated artifact inspected from disk and hash-verified.
5. Human approval bound to an exact artifact hash.

Lower-ranked sources cannot override a contradiction from a higher-ranked
source.

### Prohibited fabrication

- Guessing an object, collection, camera, material, view layer, node, socket,
  or render-pass name.
- Claiming that a Blender API or exporter exists without a capability probe
  against the declared installed version.
- Substituting a placeholder render, empty file, previous candidate, generated
  image, or differently framed camera when the requested input is absent.
- Treating Blender process exit `0` as proof that the required artifacts were
  created correctly.
- Reporting a visual or mechanical PASS from configuration values without
  executing and independently reading back the result.
- Reusing an old hash, measurement, or human approval after any bound input
  changes.
- Silently changing engine, compositor, page size, font, color profile,
  threshold, seed, or fallback path to make a run complete.

### Mandatory discovery preflight

Before rendering a panel, the runner writes a discovery record containing:

- Blender version and build hash.
- Scene file SHA-256 and source revision.
- Exact scene, camera, collection, object, material, view-layer, and node names
  required by the manifest.
- Supported render engines and required node/pass capabilities.
- Resolved output paths and whether any target already exists.
- Every mismatch, missing dependency, and ambiguous identifier.

The renderer exits nonzero before mutation or rendering when discovery is
incomplete. Approximate name matching is permitted only as a diagnostic list;
it may never select an input automatically.

### Allowed epistemic states

| State | Meaning |
|---|---|
| `DECLARED` | specified in a manifest but not yet observed |
| `OBSERVED` | read directly from the frozen input or output |
| `DERIVED` | computed from recorded observed values |
| `HUMAN_APPROVED` | approved by Aaron against an exact artifact hash |
| `BLOCKED` | required input or prerequisite is absent or ambiguous |
| `UNIMPLEMENTED` | required executable capability does not exist |
| `FAIL` | executed evidence contradicts the predicate |
| `PASS_SCOPED` | all bounded proof obligations were executed and satisfied |

`ASSUMED`, `LIKELY`, `SHOULD_EXIST`, and `LOOKS_RIGHT` are not valid machine
verdicts.

### Independent artifact readback

After rendering, a separate validator must reopen or inspect the written files
and verify format, dimensions, channel/pass presence, non-empty payload, hashes,
manifest binding, and source-scene immutability. The renderer's in-memory report
cannot authorize its own output.

## 9. Implementation phases

### Phase 0 — Reconcile source truth

**Purpose:** prevent the graphic-novel pipeline from inheriting stale claims.

- Audit `docs/STATE_OF_PRODUCTION.md` against current evidence and current
  physics-gate status; preserve historical information but correct unsupported
  “working/certified” language.
- Create `docs/GRAPHIC_NOVEL_STYLE_CONTRACT.md` with the mineral palette,
  line-weight hierarchy, tonal bands, halftone ranges, and prohibited visual
  language: neon crystal, glossy sci-fi, clean manga softness, generic fantasy.
- Create a frozen object/material naming registry for the proof-page scene.

**Exit gate:** one candidate scene and one visual scene scope are named and
hash-bound. If the scene is unavailable, the phase is `BLOCKED`, not simulated.

### Phase 1 — Manifest and render preflight

**Build:**

- `tools/render_graphic_novel_panel.py`
- `tools/validate_graphic_novel_panel.py`
- `spec/graphic_novel_panel_schema.json`
- `spec/test_graphic_novel_panel_contract.py`

The renderer initially validates the manifest and produces only the required
artifacts. The validator checks hashes, output dimensions, pass presence, and
the exact scene/camera/frame binding.

**Exit gate:** a deliberately bad manifest (wrong scene hash, missing camera,
missing line SVG, changed seed) is rejected by automated tests.

### Phase 2 — Ink and tone proof

**Build:**

- Grease Pencil Line Art collection targeting for Varek foreground assets.
- EEVEE three-band tonal derivative using Shader-to-RGB.
- A compositor group that converts the tone ID into deterministic halftone and
  cross-hatch variants.
- SVG export/readback and pixel preview comparison.

**Art rules:**

- Stable heavy silhouette on Varek, tools, load frames, and major architecture.
- Fine creases on armor, respirators, rivets, and hydraulic joints.
- Broken internal lines for stone, soot, cloth, and damaged timber.
- Solid charcoal reserved for unreachable shafts and institutional darkness.
- Amber only for fire, lamps, furnace mouths, and important physical evidence.

**Exit gate:** one static Varek panel produces a correctly paired `lineart.svg`
and `lineart.png`, three readable tonal bands, and a repeatable halftone image.
No claim is made about physical hand function.

### Phase 3 — Page assembler proof

**Build:**

- `tools/assemble_graphic_novel_page.py`
- `spec/page_layouts/proof-page-001.json`
- `tools/validate_graphic_novel_page.py`

The assembler uses SVG for panel clipping, borders, speech balloons, captions,
and typography placement. It emits PDF and review PNG. Pillow may generate
contact sheets, but it does not own the print-page master.

**Exit gate:** a three-panel page is rebuilt byte-consistently from its panel
ledger. A changed panel hash invalidates the page claim.

### Phase 4 — Human finishing and controlled exceptions

**Build:**

- Krita template matching the generated page geometry.
- `editorial-edits.json` sidecar schema for balloons, dialogue placement,
  paintover, and manual line corrections.
- Font and licensing manifest.

**Exit gate:** opening the generated page in Krita does not change the source
panel evidence; any approved manual change is declared and linked to a page
revision.

### Phase 5 — EEVEE production calibration

Render the approved test panel through the fixed EEVEE panel profile and a
Cycles diagnostic reference. Compare readability, silhouette, material
separation, smoke, print response, render time, and rerun consistency. The
comparison tunes the EEVEE profile; it does not decide whether EEVEE is allowed.

**Exit gate:** EEVEE panel output meets the defined readability and rerun gates.
Cycles discrepancies become a documented look-development issue, not a reason
to silently change the production engine.

### Phase 6 — Sequence production

Only after the proof page passes:

- Add shot-to-panel ledger entries from the approved script.
- Use the same manifest and page contracts for every page.
- Build batch rendering with resume-safe artifact checks.
- Produce issue-level contact sheets, an evidence index, and print PDFs.

## 10. First proof-page content

Use an intimate, legible sequence—not combat spectacle:

1. **Panel 1:** a records steward at an iron desk under one amber lamp; soot,
   ledger pressure, and a sealed audit mark establish the institutional world.
2. **Panel 2:** Varek, full silhouette and grounded, enters the frame as weight
   and obstruction rather than a heroic pose.
3. **Panel 3:** close view of a lead band, a scarred hand, or a mechanically
   constrained tool interface; caption binds the human cost to a physical fact.

This tests environment edges, full-body readability, close mechanical ink, warm
against cold tones, lettering space, and continuity without inventing a new
action scene or claiming an unresolved mechanism works.

## 11. Risks and stop conditions

| Risk | Control | Stop condition |
|---|---|---|
| Line Art overload on dense scenes | foreground collection + background edge pass | render time/line density exceeds declared budget |
| EEVEE/Cycles visual mismatch | comparative proof page | no silent replacement of current render authority |
| Halftone shimmer or moiré | panel-space seed + print-scale test | dot pattern changes on rerun or destroys focal read |
| Mask drift after object rename | naming registry + hash-bound manifest | object/material registry mismatch |
| Manual edits erase provenance | sidecar editorial ledger | edited page lacks declared change record |
| Stale Varek physics language leaks into panels | visual/mechanical claim separation | panel implies functional grip without authorized proof |
| Missing candidate `.blend` | explicit preflight | phase marked `BLOCKED`; no substitute scene invented |

## 12. Acceptance checklist for the first page

- [ ] Frozen source scene exists and hashes before/after render match.
- [ ] All three panel manifests validate.
- [ ] EEVEE panel master, line SVG, line PNG, tone ID, masks EXR, halftone, and panel PNG
      exist with recorded hashes.
- [ ] Every panel CARDO claim has no unauthorized PASS request.
- [ ] Discovery preflight contains no missing or ambiguous runtime identifiers.
- [ ] Independent artifact readback verifies every declared output from disk.
- [ ] Page SVG, PDF, and review PNG reproduce from the ledger.
- [ ] Full-body Varek panel passes the head-and-ground framing requirement.
- [ ] No panel claims unverified mechanical function.
- [ ] Human review explicitly approves or rejects readability, staging, and
      Thulan visual identity.

## 13. Deferred decisions

- Print size, bleed, CMYK profile, and publisher requirements.
- Final letterer/font family and commercial license status.
- Whether Clip Studio Paint is ever worth a paid exception.
- Whether external NPR add-ons are reproducible enough to admit.
- Full issue length, release format, and distribution.
