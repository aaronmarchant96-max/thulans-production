# Thulans project handoff

Updated 24 October 2026. Scope: rebellion-series direction, proposed six-year chronology model, Chapter Twelve seed, and literary lore authority reconciliation.
The production and synchronization notes below retain their explicitly dated historical scope.

## Authoritative artifacts

- Live illustrated reading draft: https://docs.google.com/document/d/1UioMeG59Kw7xE6XvxoLRXy0SbkTXwg-6ktSO5QL2cpY
- Text mirror: `novella/THE_THULANS_MANUSCRIPT_COMPLETE.md`
- Chapter mirrors: `novella/chapter_01.md` through `chapter_12.md`
- Written-story outline: `docs/NOVELLA_BLUEPRINT.md` version 3
- Current overview: `docs/ONEPAGER.md`
- Literary continuation: `docs/REBELLION_SAGA_DIRECTION.md` and RULING 034
- Editorial constitution and decision log: https://docs.google.com/document/d/1v-J0KnzXkittERcHcRgbhEiiG9VRV514yMJ6Pmwim4M
- Historical production notes: `docs/archive/READING_DRAFT_PRODUCTION_NOTES_2026-10-20.md`

## Current literary direction — 24 October 2026

The author approved successive rebellion novellas following how working communities at
higher levels handle and transform resistance from below, reaching the Spire for the
final climax. Exact count, titles, numbered geography, detailed order, next-book date,
and final macro outcome remain open. The older numbered strata conflict with the
written office on Tier Nine; do not turn “Lower Four” into Tier Four or renumber prose.

In the live Chapter Twelve dedication, six years after Varek's death, a foundry worker
asks Bram for a copy of the order for his shift. Bram invites him to Lower Four after
the bell to read it together. This exact candidate (67138) was author-approved,
applied, and verified in the live Doc. The final line, “No. It was our iron anyway,”
remains unchanged. The statue is a separate bronze casting; the refitted iron frame
is empty; the working nursery pump is a third object. Varek remains dead.

Live source checked on 24 October:
`AHj4eMRgG5ONwara6YlP5CmNzMaPAD1rdBRvEUdR2atGWqUFYVFA7ltOeLhL3DtY5whPhPW2Dx_N1FuRj6k5oRthzi9I0VA88vlzum5nals`.
Twelve chapter headings and twelve inline images were observed; Chapter Eleven
intentionally has no chapter plate. The repository's 21 October prose mirrors and
word-count tables were not synchronized by this update. Do not restore them over
the newer live draft or treat their counts as a current measurement.

RULING 034 and the series-direction document separate the current literary chronology
from older plans that kept Varek alive during an immediate public collapse. The old
sequences remain scoped planning history, not automatic sequel events. The final
rebellion outcome and a fresh eruption/launch timetable have not been selected.

The proposed Varek recovery-arc dialogue plan remains unapplied. The current editorial
pass is Chapter Five; this separately approved Chapter Twelve seed does not authorize
a general ending rewrite. No manuscript, cover, chapter plate, engineering model,
music, game, or REI code was changed in this documentation commit.

## Chronology working model — 24 October 2026

Recorded `docs/REBELLION_CHRONOLOGY_WORKING_MODEL.md` and linked it from the series
direction. The model preserves the established six-year gap and proposes a costly
managed retreat, continued ark preparation, and a first ark approaching readiness
at the dedication. Departure preparations would create the next immediate clock;
the geological threat explains why escape matters. These are distinct from the
first novella's feeder-closure and ram deadlines.

Theodemir remaining head of Continuity and transferring maintenance crews from
occupied districts to final ark preparations are proposed sequel choices, not
newly locked events. Before drafting, prepare a compact six-year chronology,
surviving-district dependency map, ark readiness record, and character/evidence
chronology. Compare explicit manuscript threat statements before adopting the
model; geological coherence has not yet been verified.

Only this handoff, the series direction, and the new working-model document are
changed in this documentation update. No manuscript, prose mirror, illustration,
ruling, engineering model, or REI implementation is changed.

## Age reconciliation — 23 October 2026

The author confirmed that the accepted story governs conflicting older lore. RULING 029
and the Lore Bible now identify Bram as thirteen during the main action on 22 October,
turning fourteen on 30 October; the epilogue is six years later. This corrects reference
labels and does not change the manuscript, artwork, or broader adaptation events.
Other older lore discrepancies require their own comparison with the accepted story.
No prose-mirror or illustration synchronization was performed in this age-only update.

## Current state (21 October synchronization snapshot)

Twelve chapters and four acts are complete. Chapter/act text contains 22,577 words by whitespace count; cover and repository front matter are excluded. Five images remain in the live Doc: the approved cover and Chapters One–Four plates.

Character revisions establish Varek’s trust in the recorded allowance, his expectation that the sounding will compel correction, and his recognition that he never asked whose names filled the berths. The family pass adds Bram–Sanna friction and Haila’s scarf memory. The rhythm pass intentionally removes about 530 words from Chapters Seven–Ten. Do not restore those passages to match an older total.

Production cleanup standardizes typographic quotes/apostrophes and chapter-heading styles, supplies the first-act heading, and keeps illustration openings with their headings. Repository mirrors derive from the live document and contain no production appendix.

## Open editorial questions

- Chapter Six’s overt threat dialogue compared with the later restrained confrontation.
- Geological timescale and reader orientation across the six-year epilogue.
- Remaining repetitive pauses and scene ornaments.
- External cold-reader feedback is still needed; internal ratings are editorial opinions.

These questions do not authorize inventing new lore or rewriting the ending.

## Other project scopes

Existing engineering acceptance rules, model approvals, music remediation, cinematic history, and game continuity retain their own governing documents. This manuscript synchronization makes no new claim that those gates pass. Consult `AGENTS.md` and the relevant domain gate before working on them.

## Synchronization verification

The complete repository manuscript and all twelve chapter mirrors were compared paragraph by paragraph with the live Doc (1,797 narrative and scene-break paragraphs). Headings and typographic punctuation were checked separately. Agent instructions contain one current manuscript-status block.

## README reconciliation — 21 October 2026

Restored the authoritative illustrated Doc link, redirected the removed appendix link to the archived production notes, corrected the chit/slate locations and Chapter Eight closure order, and recomputed chapter counts from the text mirror. Described the book as a revised reading draft rather than a finalized or universally clean manuscript. Manuscript prose and artwork were not changed.

## Root script organization — 21 October 2026

Moved 33 root Python scripts into `tools/legacy/blender/`, `tools/legacy/llm/`, and `tools/blender_setup/`. The V35 preflight JSON moved with the historical Blender scripts. Updated the four generation helpers so their outputs target the relocated builder directory. No tracked external references to the old root script paths were found; documentation and directory navigation now show the new locations. Manuscript files and assets are unchanged.

Relocation checks: all 33 Python scripts compile; the four generator output paths resolve to the moved builders; the other 30 relocated files are byte-identical to their originals. Repository CI was run before and after the move and retained the same missing agent-contract markers plus three physics-test failures and one related contract-test setup error (35 tests). Blender execution was not part of this directory cleanup.
