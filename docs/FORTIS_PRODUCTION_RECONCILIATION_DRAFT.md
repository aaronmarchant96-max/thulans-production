# FORTIS — Production Reconciliation Addendum (Draft)

**Status:** PROPOSED / NOT CANON / NOT PRODUCTION APPROVAL  
**Scope:** Proposed title and workflow for the Ansen/Nessa 16-page graphic-novel pilot currently known in the repository as *The Thulans: Salvation*.  
**Baseline reviewed:** `afb72829954b07f7bcdbc7859aa4022832d7c0b8` (28 October 2026).  
**Owner:** Author approval required. **Implementer:** AGY for code, canon and production changes.

## Why this addendum exists

The emerging working title **FORTIS**, the individual-panel generation workflow, and Canva lettering/motion workflow are newer proposals. They do not silently replace the approved *Salvation* story direction or the existing graphic-novel style contract.

This document captures **proposals and conflicts** for review. It must not be represented as a final title ruling, production-certified character sheet, approved page render, or successful automated test.

## Authority order and boundaries

1. `RULINGS.md` (especially RULING 035) and authoritative novella text control narrative/physical canon.
2. `docs/SALVATION_STORY_DIRECTION.md` governs approved relationship aims, open questions, and forthcoming editorial pass.
3. `docs/SALVATION_PILOT_16_PAGES.md` is **working revision 3**, not a frozen script; 16 story pages / 66 panels.
4. `docs/GRAPHIC_NOVEL_STYLE_CONTRACT.md` provides the established visual thesis, rejection gate and human approval process. Its metadata states its scope is Varek literary/graphic-novel continuity; extending its gates to the siblings needs explicit scoping, not an unannounced rewrite.
5. This FORTIS addendum describes **proposed pilot-specific production choices only** and cannot override items 1–4.

The live illustrated novella has authority over stale repository mirrors where `AGENTS.md` and `handoff/PREFIX.md` say so. Do not synchronize prose during this project.

## Decisions requested from the author

| ID | Proposed choice | Status / blocking consequence |
|---|---|---|
| DEC-01 | Change pilot presentation title from *Salvation* to **FORTIS**, with *THE THULANS* small above it | **OPEN**; do not batch-rename or edit RULING 035 before approval |
| DEC-02 | FORTIS has a near-monochrome, heavy-ink subprofile under the Thulans visual system; use cold charcoal foundation, limited locally motivated amber, restrained lead-blue audit light | **PROPOSED**; color conflict with the broader contract must be resolved by an explicit scope rule |
| DEC-03 | Approve two age-appropriate silhouette sheets for Ansen and Nessa before illustration | **OPEN**; exact ages and seniority unassigned |
| DEC-04 | Use Canva for editorial layout/animation while retaining reproducible, text-source-backed lettering exports | **PROPOSED**; resolve against contract §18's deterministic SVG lettering requirement |
| DEC-05 | Use a 6 × 9 in, 2:3 portrait print working master | **PROVISIONAL**; printer, binding, bleed and minimum-page constraints unknown |
| DEC-06 | Freeze script revision after sibling humor, active search, and mechanical blocking pass | **OPEN**; no bulk panels beforehand |

## Production workflow after decisions

1. **Source inventory:** Record HEAD SHA; inspect `AGENTS.md`, `handoff/PREFIX.md`, RULING 035, story direction, revision 3 script, style contract, approved Varek views, Welded reference and actual Panel Studio validator files.
2. **Script pass:** Write continuous scene action; apply relationship/pursuit brief while preserving chapter 6, 10 and 11 continuity. Seek author approval; only then freeze page/panel count and script revision.
3. **Thumbnails:** Thumbnail *all* pages at the locked page ratio. Reserve caption/balloon zones and test left-to-right, top-to-bottom reads and page turns. Pages 11–12 must rhyme in geometry; page 15 repeats page 1's exact report; page 16 retains its backward coat reveal.
4. **Character and set bibles:** Create approved front/profile/three-quarter/silhouette references for teenage Ansen and Nessa, adult Ansen, the shelter, frame, handler control, and escape-gallery layout. Childhood oversized coat and later borrowed worker coat are different objects.
5. **Prompt packets:** Generate each panel in a fresh request with exact, versioned approved reference images attached; include panel ID, visible action, camera, lighting source, exclusions, lettering-safe zone and adjacent continuity reference. Do not rely on chat memory or named-artist style prompts.
6. **Artwork generation:** Use individual **art-only** images, not whole pages or baked-in dialogue. Page 1 is **three scripted panels but only two artwork panels**; panel 1 is the text-only equipment record.
7. **QA:** Run applicable questions from `docs/GRAPHIC_NOVEL_STYLE_CONTRACT.md` §19 before the human scorecard §20. Non-applicable Varek-only questions must be recorded as N/A with reasoning, never silently altered or counted as a PASS. Human final approval remains mandatory; machine checks may reject, never approve.
8. **Static master:** Assemble approved art into fixed page grid with editable typography; preserve a deterministic text manifest or SVG/PDF export as agreed in DEC-04.
9. **Motion branch:** Duplicate approved image/caption sources into a separate timeline; animate restrained pans and text reveals; test against static story order. Do not compromise static composition to enable motion.
10. **Proof/release:** Check at final physical size and mobile view, verify spelling and captions, panel sequence, character/prop continuity, and export settings. Record exact artifact hashes and author sign-off.

## Non-negotiable regression assertions

- **CANON:** Ansen is the first broken-wrist miner freed; Nessa is not the second freed man. Chapter 10/11 appearances remain. Varek's approved machine form and left maul/right copper-ring arm remain intact.
- **SCRIPT:** No invented beat, dialogue, extra character, new mechanism, or fixed unapproved lyric. Revision 3 is not marked FINAL.
- **P01:** Three scripted panels, two artwork panels, one text panel; `FRAME 9. NO FAULT FOUND.` exactly.
- **P11–P12:** Same four-panel framing; the first removable restraint releases, the second load-bearing coupling does not.
- **P14–P15:** Nessa's forced grip has no consent; control line, action envelope, coupling and shutoff positions agree; no claim of verified mechanics without actual test.
- **P16:** Borrowed adult coat was prepared earlier; its visual rhyme to the childhood coat does not imply they are the same garment.
- **VISUAL:** Human action first, thumbnail/squint test, motivated light, legible hands and subject separation; no ambient amber wash or glamorized machinery. The §19 rejection gate and §20 scorecard retain authority.
- **LETTERING:** Text remains independently editable and reproducible; final report text exactly matches both occurrences.
- **TRACE:** Each candidate records the script revision, reference-version IDs, prompt, panel ID, output SHA/hash, review decision and reviewer.

## Engineering / Panel Studio investigation (not a fix claim)

Prior audit reported a `loreGuard` rule requiring unrelated Varek terms (such as “sloped bronze” and “hydraulic”) even for sibling/bread panels, as well as a named-artist prompt chip. **The actual validator file path and executable behavior have not been independently confirmed in this addendum**. AGY must:

1. Locate the real validator and prompt-chip source in the checked-out tree.
2. Run baseline tests and save their command/output; identify which tests actually exist.
3. Add scene-appropriate categories without weakening Varek-specific locked checks. Negative tests must prove invalid Varek prompts still fail.
4. Remove/replace named-artist prompt chips with functional visual-language descriptors, subject to the style contract §4.
5. Report test evidence and changed files in a separate implementation PR.

## Required next PRs (separate from this draft)

- **PR-A:** Author-approved title/style reconciliation with `RULINGS.md`, story direction, script header, README and `handoff/PREFIX.md` updated together. Do **not** apply until DEC-01/02 approved.
- **PR-B:** Panel Studio validator and prompt-chip repair, with negative regression tests.
- **PR-C:** Script revision, character/silhouette approvals and thumbnail sign-off.
- **PR-D:** Page 1 static/motion proof and measured calibration report.

## Stop conditions

No main-branch merge, title canonization, validator weakening, full-page generated artwork or bulk panel production is authorized by this draft alone. Author approval is required for title, story, design and final-art changes. Avoid concurrent work with AGY by assigning implementation PRs explicitly.