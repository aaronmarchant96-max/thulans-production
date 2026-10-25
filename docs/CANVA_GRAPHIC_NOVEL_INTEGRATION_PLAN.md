---
status: PROPOSED_CANVA_INTEGRATION
authority: AGENTS.md; docs/DETERMINISTIC_GRAPHIC_NOVEL_PIPELINE_PLAN.md; docs/GRAPHIC_NOVEL_STYLE_CONTRACT.md; docs/CARDO_REI_CLAIM_KERNEL.md
scope: Thulans graphic-novel layout, lettering, and proof-page finishing only; not mechanical physics, game production, or Blender scene approval
implementation: NOT_IMPLEMENTED
---

# Canva-Assisted Graphic-Novel Finishing Plan

## Decision and boundaries

**Proposal:** use Canva as a human-editable **page design and lettering derivative**. Preserve frozen Blender/EEVEE panel production, CARDO evidence, and the deterministic SVG/PDF page assembler as separate authoritative processes. This is a layout workflow proposal, not an assertion that Canva exports are byte-for-byte reproducible, scriptable through the installed connector, or approved.

The first target remains **one three-panel proof page**, not an issue or a full chapter. No scene, camera, model, or graphic-novel page is approved by this plan. A missing checked-in `.blend` keeps the verified 3D production path **BLOCKED** until source discovery succeeds. It is permitted to sketch an explicitly noncanonical layout in Canva before then, but such a sketch cannot become an authorized Blender panel or satisfy any CARDO proof obligation.

The Thulan graphic-novel visual thesis remains **administrative dread, industrial tenderness, consequences that remain**. Preserve the six-unit grid, human-first hierarchy, silent-read test, palette and restrained lighting, and the approved EEVEE final-panel tier in the existing style contract.

## Revised architecture

```text
FROZEN SOURCE OF TRUTH                         EDITABLE HUMAN FINISHING
frozen .blend + panel manifest
    -> discovery preflight + source hash
    -> EEVEE master + line SVG/PNG + tone/masks
    -> deterministic halftone + panel PNG
    -> independent CARDO panel evidence
    -> deterministic SVG page assembler ----------> approved panel exports
           |                                             |
           v                                             v
    baseline page.svg/pdf/png                CANVA fixed-size page design
           |                                 - gutters, frames/crops, captions
           |                                 - speech balloons, typography
           |                                 - human review and manual edits
           |                                             |
           |                                             v
           |                                 Canva review PDF/PNG export
           |                                             |
           +---------------------------> Canva derivative validator
                                                 |
                                                 v
                                     author visual and lettering approval
```

**Only the baseline assembler may claim** `PAGE.REPRODUCIBLE_FROM_LEDGER`. Canva outputs are **editable editorial derivatives** and are never substitutes for the frozen panel masters, canonical page geometry, or CARDO mechanical validation. A Canva design cannot certify physics, load transfer, hand/tool grip, continuity of unrendered views, or an unapproved model.

Krita remains an optional local paintover tool, not a required first-stage dependency. Record any Krita-to-Canva changes in the same editorial ledger.

## Source-of-truth and responsibility table

| Deliverable | Authoritative producer | Canva responsibility | Acceptance |
|---|---|---|---|
| Character and machinery identity | Approved scene/model + character bible + human visual decision | Cannot revise canon | Exact approved reference and scene scope required |
| Panel imagery | Blender EEVEE + deterministic compositor | Place an unchanged authorized panel image | Panel source hash and crop binding recorded |
| Panel borders, order, and gutters | Baseline SVG layout manifest | Editable finishing presentation | Layout comparison against source manifest |
| Balloons, captions, lettering | Approved script + layout manifest | Editable design application | Human lettering approval and complete transcript |
| Print master baseline | Deterministic SVG/PDF assembler | None | Verified baseline hashes |
| Canva review/print candidate | Canva exported PDF/PNG | Visual production derivative | Export readback, print checks, human approval |
| Physics validation | Separate physics gate, if ever passed | No role | Never inferred from a page |

## Canva capabilities and limits to verify before integration

- Canva supports fixed-size designs with frames, image placement, text and speech bubbles, multipage layouts, and PDF Print export. Use a **fixed-dimension design**, not Canva Docs, for book pages and bleed review.
- The connected Canva actions currently expose creation, page metadata, asset upload, editing transactions, and import workflows. **An automated export action is not surfaced by the currently connected Canva tool set**. Manual editor export is the baseline; an external API connector may be evaluated only after an authenticated capability probe.
- Canva supports PDF Print and optional bleed/crop marks, but page dimensions, printer-specific bleed, trim, safe area, PDF profile, and colour management **must be measured from exported files**. Do not assume Canva’s fixed bleed matches a future publisher’s requirements.
- Canva's editable object layout is not a deterministic scene description. Do not claim the same output bytes after reopening, copying, re-exporting, changing fonts, or changing Canva’s rendering implementation. Preserve export hashes, not imagined determinism.
- Do not upload unapproved generated-image substitutes as if they are frozen Blender output. Layout mockups are clearly watermarked or titled **NONCANON LAYOUT STUDY** and remain separate from evidence.

## Canonical file additions (PROPOSED, not implemented)

Create `evidence/graphic-novel/<page_id>/canva/` **only after** a valid page ID exists:

```text
canva-page-manifest.json     declared Canva design ID, page number, source panel hashes
canva-editorial-edits.json   manual change log for crops, borders, balloons, captions
canva-review.pdf            exported snapshot, not the deterministic master
canva-review.png            raster review derivative
canva-validation.json       independent readback and comparison results
canva-human-approval.json   decision bound to exact exported artifact hash
```

No API credential, access token, signed/temporary download URL, or private viewer link is committed as source material. Store a stable design ID, plus a link only if its sharing/access scope is deliberately authorized.

Suggested future files:

- `spec/canva_page_manifest_schema.json` — structure, types, and strict source IDs;
- `tools/validate_canva_page_derivative.py` — independent PDF/image/manifest validator;
- `spec/test_canva_page_derivative_contract.py` — rejection cases for missing or stale proof;
- `spec/page_layouts/proof-page-001.json` — still owned by the deterministic SVG assembler.

None of these files exists merely because this document names them.

### Manifest requirements

Record `page_id`, approved `panel_id` order, each panel's `panel.png` SHA-256, source `panel-manifest.json` SHA-256, approved script revision and spoken text, source page-layout hash, Canva design ID, Canva page index, intended width/height/units, panel bounding boxes and crops, gutters, balloon/caption text and positions, font family/license declaration, approved palette, editorial change list, export file hashes, author approval state, and known exceptions. Do not invent a scene or camera ID; copy only observed identifiers from prior authorized records.

Any replaced image, changed crop, lettering, font, or page geometry **invalidates the Canva derivative's previous review approval**. It does not silently change the frozen scene or invalidate an unchanged underlying panel master.

## Two explicit working modes

**A. Visual layout rehearsal (available before Blender readiness):**
- Make one Canva fixed-size prototype using empty panels, graphic frames, and proposed text areas.
- Label every proof-page image substitute and draft balloon as noncanonical; never claim panel hash, 3D continuity, geometry, or validation.
- Human-review reading order, gutters, focal hierarchy, typography, text density, and thumbnail clarity. This produces only a visual layout decision.

**B. Evidence-backed Canva page (blocked until panels exist):**
- Require three validated and author-accepted panel-image candidates and one baseline SVG/PDF page.
- Import *those exact panel assets* into a dedicated Canva design; record each source hash and intended crop in the manifest.
- Letter only from an approved script revision. No new character dialogue or story beats invented in Canva.
- Export a dated PDF and PNG review. Validate their content, image dimensions, page geometry, text extraction, fonts, bleed/safe-area fit, and source-panel correspondence. Assess visual differences manually where exact pixel comparison is not meaningful.
- Author approves the exact exported revision and the declared manual-edit ledger. Further edits reopen review.

## Proof-page specification

Keep the existing first proof page and use a three-panel page on a six-unit grid:

1. **Records:** steward at an iron desk under a single amber lamp. A stamped ledger or seal supplies the concrete evidence token. Enough negative space for a short caption.
2. **Obstruction:** Varek enters as weight and limitation, fully framed from lifting eyes to boots where scene evidence permits. No hero pose, no implied functioning grip from the blocked hand gate.
3. **Human cost:** close view of a scarred hand, lead band, or physically constrained tool interface. Caption refers to a concrete observed object, not an abstract moral.

Place panel numbers and text only in design metadata, not on source artwork. Keep three-band tonal clarity, restrained amber sources, charcoal void, and mineral-only Gren-Skildus green. After hiding all Canva text, the physical scene still must make sense. If any shot requires an absent/ambiguous `.blend`, the evidence-backed proof remains **BLOCKED**.

## Acceptance gates and stop conditions

### Proposed Canva derivative checks (do not report as implemented)

- `CANVA.SOURCE_PANEL_HASHES_BOUND` — panel IDs and SHA-256 match authorized panel records.
- `CANVA.DESIGN_ID_AND_PAGE_OBSERVED` — actual Canva design and page are independently resolved.
- `CANVA.PANEL_ORDER_AND_CROPS_REVIEWED` — crop, orientation, border, and gutters match declared layout or carry approved deviation.
- `CANVA.DIALOGUE_MATCHES_SCRIPT` — extracted text compared with the approved lettering script; reading order also human reviewed.
- `CANVA.FONT_LICENSE_AND_PRINT_PROFILE_DECLARED` — font rights and printer requirements documented.
- `CANVA.EXPORTS_READ_BACK` — PDF/PNG exports exist, parse, have sensible geometry, and are hash-bound.
- `CANVA.EDIT_LEDGER_COMPLETE` — editor-originated changes are enumerated.
- `CANVA.HUMAN_VISUAL_APPROVAL` — final readability, staging, Thulan identity, and lettering receive explicit author approval for exact export hash.

Use the repository's existing status vocabulary. Above checks are **DECLARED / UNIMPLEMENTED** until actual schemas, validators, tests, export capability and independent readback exist. Never report `PASS_SCOPED` for Canva from a creator's self-reported status.

**Stop** if any panel hash differs, visual asset is substituted, required view is absent, text does not match the script, unlicensed font is used, exported sizes/bleed cannot be measured, or a human approval refers to a prior export revision. Record the reason rather than silently adjusting inputs.

## Execution phases

**C0 — Canva layout rehearsal:** choose target trim and print-provider provisional settings; create a fixed-dimension three-panel layout; review human-first storytelling with blank/clearly unapproved mockup imagery. Exit: visual layout feedback only.

**C1 — Evidence handoff:** keep the original Phase 0–2 Blender preflight, manifests, and independent proof. Exit: three authorized panel assets or `BLOCKED`.

**C2 — Deterministic baseline page:** finish the original SVG/PDF assembler and verify exact page ledger. Exit: `PAGE.REPRODUCIBLE_FROM_LEDGER` is actually demonstrated, not inferred.

**C3 — Canva finishing copy:** place authorized panels, apply editable typography, capture stable design/page IDs and editorial edits. Exit: author can inspect one complete Canva page.

**C4 — Export and audit:** manual PDF Print and PNG export until a real automation route is proved. Independent readback and source hash audit. Exit: derivative review candidate, not canon approval.

**C5 — Author gate:** human verifies page meaning, staging, ink, character continuity, subtitle/lettering, print fit. Exit: exact exported revision approved or rejected.

**C6 — Sequence production:** start only after the three-panel proof succeeds; duplicate the workflow with independent hashes and approval records for every subsequent page.

## Non-goals

- No changes to hand-physics gate, CARDO claim kernel, novel text, or continuity.
- No Canva-generated Varek panels accepted as model/physics evidence.
- No claim of byte-identical Canva export regeneration.
- No replacement of the approved EEVEE panel tier or the original deterministic assembler.
- No automatic final publication, CMYK signoff, or print-master certification until external printer requirements and export readback are observed.

## Source notes

- Internal: `docs/DETERMINISTIC_GRAPHIC_NOVEL_PIPELINE_PLAN.md`, `docs/GRAPHIC_NOVEL_STYLE_CONTRACT.md`, `AGENTS.md`.
- Canva official guidance: https://www.canva.com/comic-strips/templates/ , https://www.canva.com/help/download-file-types/ , https://www.canva.com/help/margins-bleed-crop-marks/ .
- Canva API export documentation (a capability reference, not evidence that this connector exposes the action): https://www.canva.dev/docs/apps/rest-apis/reference/exports/create-design-export-job/ .
