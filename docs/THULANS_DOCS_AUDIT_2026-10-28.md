# Thulans documentation audit & cleanup — 28 October 2026

**Disposition:** Documentation-only audit and cleanup candidate in draft PR #4. **No approved canon, story script, image, model, code, API, safety gate or historical record was rewritten or deleted.** The author's REI / Image Engine master plan remains unapproved.

## Checked baseline and scope

- GitHub `main` snapshot: `2f87d21ad3a03872a48fe6b7621b2af6779d42b0`; draft documentation branch before this cleanup: `229c6866d1a4190028b852ba79e64084cbbde956`.
- Repository tree had **629 entries**; targeted source inspection included **17 core Markdown documents** plus the `.github/workflows/cardo-claims.yml` workflow and the agent-compliance audit script.
- Checked local relative links in those 17 documents against the repository tree. The apparent missing links to `THULANS_LOCKED_STATUS_2026-10-28.md` existed on draft PR #4, not on `main`; these were **branch-aware false positives**, not missing assets.
- This is a targeted governance/README/handoff audit, **not** a full 629-entry security, image-file, screenplay, 3D asset, or automated test audit.

## Corrected in this draft PR

| Finding | Change | Boundary |
| --- | --- | --- |
| README badge says **22,979 words**, but `AGENTS.md`, `handoff/PREFIX.md` and the chapter table give **22,424** for the dated repository chapter/act snapshot. | Correct badge to **22,424**. | This is **not** a measured live Google Doc total. |
| README said the entire novella/illustrations were synchronized directly from the live Doc, while the handoff confirms Chapter One is from 24 October and Chapters Two–Twelve are a 21 October snapshot. | Replace broad sync claim with explicit mixed-date mirror status and keep the live Doc as source of truth. | No manuscript content or actual illustration is changed. |
| `docs/STATE_OF_PRODUCTION.md` is dated **15 September** but proclaims old comprehensive locks and physical certification as if current. | Label as **historical**, preserve claims in place, and link current status sources. | No retroactive assertion that the old machinery or story branch was formally rescinded. |
| Eight `file:///home/aaron/...` Markdown links in the September state report only worked on one local machine. | Convert to equivalent repository-relative links. | Preserve cited assets; no local paths or media were modified. |
| `docs/SESSION_HANDOFF.md` (10 September) instructs future agents to “read this file first” and use machine-local paths. | Explicitly label archival and redirect to current agent/handoff docs, keeping the historical evidence. | Do not change operational path contracts elsewhere. |
| `handoff/PREFIX.md` began with an older update date, despite the new 28 October section. | Align its top-level date/scope to the latest status annotation; retain dated history. | No claim of new manuscript sync or code completion. |
| FORTIS reconciliation draft called unapproved future PRs “required,” risking mistaken execution; PR-B already has open PR #3. | Retitle as **proposed**, note existing PR #3, and reiterate the unapproved plan. | Does not merge PR #3 or approve REI implementation. |

## Locked decisions and work still intentionally **not** promoted

- **Ansen and Nessa** are approved **siblings**, with approved naming and RULING 035 penal-system premise/outcome.
- Established companion-story/repository title **The Thulans: Salvation** remains; **FORTIS** is an unapproved working cover/presentation title.
- `docs/SALVATION_PILOT_16_PAGES.md` revision 3 is the working script (16 story pages / 66 panels). Opening Revision 4 and its Pages 1–4 five-panel Page 2 production material are **candidates**.
- Art/character faces, lantern-free lighting realization, final cover, title treatment, canon dimensions, revised dialogue and design references are **not approved final assets**.
- REI routing, BFL provider, DeepSeek scene director, EchoForge asset approval, Arena QA and LoRA plans are **ideas requiring separate authorization**. No paid generation, API credentials or runtime edits were introduced.

## Unresolved / stop conditions

1. **GitHub Actions CARDO claim-integrity failure:** The current workflow compiles `AGENTS.md` through `tools/audit_agent_compliance.py --compile-only`. The script requires `<!-- AGENT_CONTRACT_V1_BEGIN -->` and `<!-- AGENT_CONTRACT_V1_END -->`, but `AGENTS.md` contains neither. GitHub Actions runs for draft PR #4 and implementation PR #3 were reported **failed** on this dated inspection; merely viewing their conclusions does not prove the only failing step without inspecting run logs. Previous evidence identified the compile step as a blocker. The missing markers must be reconciled to the intended actual contract by the designated implementer; **do not fabricate the rules, insert empty placeholder markers, or disable the gate**.
2. **PR #3** (Panel Studio multi-scene refactor) remains open/unmerged at its checked SHA `e6fa45090dedaf11b5c02742c6a2768327638c59`; its tests, style-reference approval claims and live submission boundary need independent review before promotion. Do not collide with AGY's work.
3. **Canonical script freeze, names/title change, lighting resolution, visual atlas and full cover** remain outstanding author choices. Do not infer final approval from attractive mockups or from this cleanup PR.
4. **Existing local build/physics/asset gates** were not executed in this session. No green test status or production certification is claimed.

## Read order for future agents

`AGENTS.md` → `handoff/PREFIX.md` → `RULINGS.md` / authoritative live novella → `docs/SALVATION_STORY_DIRECTION.md` → `docs/SALVATION_PILOT_16_PAGES.md` → [locked-status index](THULANS_LOCKED_STATUS_2026-10-28.md). Historical September production/handoff documents are background reference, not source authority.

**Approval boundary:** This record is an audit trail, **not an action list granting permission** to rewrite canon, ship a cover, or implement REI.
