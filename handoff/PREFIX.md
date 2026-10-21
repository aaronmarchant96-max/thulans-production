# Thulans project handoff

Updated 21 October 2026. Scope: novella production cleanup and synchronization.

## Authoritative artifacts

- Live illustrated reading draft: https://docs.google.com/document/d/1UioMeG59Kw7xE6XvxoLRXy0SbkTXwg-6ktSO5QL2cpY
- Text mirror: `novella/THE_THULANS_MANUSCRIPT_COMPLETE.md`
- Chapter mirrors: `novella/chapter_01.md` through `chapter_12.md`
- Written-story outline: `docs/NOVELLA_BLUEPRINT.md` version 2
- Current overview: `docs/ONEPAGER.md`
- Historical production notes: `docs/archive/READING_DRAFT_PRODUCTION_NOTES_2026-10-20.md`

## Current state

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
