---
verified: true
last_reviewed: 2026-07-31
---

# Token Efficiency Handbook

## Core Thesis: The Caching & Compression Model

> **"The model is cheap; the context is what you pay for."**

This build (768 tests, 63 suites, ~22k lines) cost ~$22 because **97.7% of tokens were cache hits** (~120x cost reduction). Token efficiency isn't a complex prompt library—it's three habits and one systemic leverage point:

1. **Freeze the Prefix & Compress History:** Don't let conversation context grow infinitely. Compress closed work into dense summaries. Keep instructions and prefix frozen so they hit cache. Only new work pays fresh tokens.
2. **Read Small, Search Tight:** Grep for exact symbols, read 20 lines around them. Delegate discovery to subagents so it returns in one concise paragraph instead of paging through raw files.
3. **Machine Verification Over Conversational Re-explanation:** Run local tests and typecheckers (`npm test`, `tsc --noEmit`). Look at logs directly. Don't ask the LLM "is this right?" when the compiler/test suite already told you.
4. **Plan Before Execution:** Explore, map the plan, get human "go", then edit. Wasted build attempts are wasted fresh turns.

*Freeze the prefix, compress everything closed, and let the tests carry the memory. Then a big system is mostly one long cache hit.*

---

## The Numbers

| Interaction | Token Cost (typical) | With Tactic |
|-------------|---------------------|-------------|
| Codebase exploration (no guide) | ~100K | ~12K (read fortis-et-liber first) |
| AGY plan for complex refactor | ~12K | ~8K (pin exact line numbers, skip narrative) |
| EXEC implementation of plan | ~10K | ~5K (fast lane, skip AGY if mechanical) |
| Full AGY + EXEC loop | ~25K | ~18K (structured plan + efficient execution) |

---

## Tactic 1: The 12K Onboarding Path

Instead of exploring the codebase through trial-and-error:

1. Read `docs/fortis-et-liber.md` — the CLI reference map (4K tokens)
2. Read `docs/REI_CODE_PATTERNS.md` — the 8 standard patterns (3K tokens)
3. Read `AGENTS.md` — the workflow spec (2K tokens)

**Total: ~9K tokens to become productive vs ~100K through exploration.** That's 91% savings.

---

## Tactic 2: Fast Lane for Mechanical Tasks

If a task meets all 3 Fast Lane criteria (AGENTS.md triage gate):

- Skip AGY entirely — don't plan, just execute
- Single commit, single tool call pattern
- Savings: ~5–8K tokens per task skipped

**When in doubt:** If the task touches 3+ files but the change is a pure sed/replace, it's still Fast Lane. Don't over-plan.

---

## Tactic 3: Plan Format Discipline

AGY plans (CARDO REI format) should be:

- Under 4,000 tokens maximum
- Pin exact line numbers (`src/REI.jsx:334-340`)
- List files that will change and WHY (not how)
- Include the verification command (`npm test -- --runInBand`)

Bad (burns tokens):
```
We should consider modifying the routing logic to handle the new domain
by adding a new branch that checks the keyword matches and routes accordingly...
```

Good (saves tokens):
```
ADD nightShiftRouter.js:306 — legal routing branch (isLikelyLegalRequest guard)
RUN: npm test -- --runInBand src/lib/nightShiftRouter.test.js
```

---

## Tactic 4: Structured Error Reports

Instead of a narrative about what went wrong, use the template from AGENTS.md:

```
## Error Report
**Command:** <exact>
**Error:** <exact>
**Rollback:** clean
**Next:** escalate to AGY
```

This is ~200 tokens vs a 1,000-token freeform explanation.

---

## Tactic 5: Compress Aggressively

When a conversation section is closed (feature shipped, research concluded, dead end discarded):

- Compress that range into a dense summary
- Keep only the decisions made, files changed, and verification results
- Discard all intermediate exploration, failed attempts, and raw output

A good compress summary is 500–1,000 tokens replacing 5,000–10,000 of raw conversation.

---

## Tactic 6: Verification Minimalism

Don't run `npm test` unnecessarily. Instead:

- Run `npm test -- --runInBand <specific-test-file>` for targeted feedback
- Only run the full suite as a pre-commit/push gate
- Skip build check during exploration — it's a commit gate, not an exploration gate

---

## Tactic 7: Pin, Don't Wander

When AGY needs to inspect a file, it should:

- Open the file at the exact line range known to be relevant (use the file map)
- Not do a full-file read of 1,476-line components
- Use grep for targeted search, not `find` + manual scan

---

## Anti-Patterns (Token Wasters)

| Anti-pattern | Cost | Fix |
|-------------|------|-----|
| "Let me explore the codebase first" (no guide) | ~30K tokens | Read fortis-et-liber first |
| AGY plan for a 1-line comment change | ~6K | Fast Lane |
| Narrative error description instead of template | +800 tokens per error | Use Error Report template |
| Full test suite during every exploration step | ~20s × N runs | Targeted `--testPathPattern` |
| AGY reads entire 500-line file for one function | ~3K | Read at line offset |

---

## Quick Check: Is This Token-Efficient?

Before any tool call or output, ask:

- [ ] Does the user need this detail or is it for my own reasoning?
- [ ] Can I compress earlier context before adding more?
- [ ] Would this task qualify for Fast Lane?
- [ ] Am I reading more lines than necessary?

---

## Tactic 8: Budget Is the Compress Trigger, Not Size

Compression must be driven by the **token budget** in AGENTS.md (Fast <5K, plan <12K, AGY+EXEC <25K), not by how large the conversation *looks*. When a task reaches its budget and work remains:

- `compress` the closed ranges into dense summaries, drop a handoff note
- then continue — do NOT "power through" past the cap hoping it fits

A budget overrun that is just absorbed costs fresh tokens with zero signal. The rule: **hit budget → compress → continue**, never hit budget → keep going.

## Tactic 9: Write the Acceptance Tests First

The expensive pattern is *implement → review → re-plan → re-implement* (doubles the burn). Kill the loop up front: before writing code for any non-trivial (5+ file / reasoning) change, write the **experimental-isolation contract** as executable assertions — the same assertions a reviewer would demand:

- Which cases must be *controls* (unchanged: e.g. `cacheModeledEntries === 0`, null cache fields)
- Which case carries the *effect* (`cacheModeledEntries > 0`, savings non-null)
- What must stay *frozen* (identical routing/escalation/exclusion between control and effect)

Pin these in the test file *before* implementing. Then the first pass is the final pass, and the review is a confirmation, not a correction.

## Tactic 10: Full Suite + gen-claims Are Commit-Time Only

- `npm test -- --runInBand` without a path is a **commit/push gate only** — never an iteration tool.
- Iterate with `npm test -- --runInBand src/lib/<module>.test.ts` or `npm run test:changed`.
- `node scripts/gen-claims.mjs` re-runs the whole suite every time — run it **once**, immediately before commit, not during exploration.
- Extract gate numbers cheaply: `npm test -- --runInBand 2>&1 | rg "Tests:|Test Suites:"` — don't dump the whole chatty output.

## Tactic 11: The ~1,000 Test Ceiling & Consolidation Policy

- **Cap Test Count at ~1,000 (Current: 1366 tests / 121 suites):** Adding endless individual tests creates diminishing returns and bloats full-suite verification from ~15s to >100s.
- **1-In, 1-Out Policy:** Never add net-new tests past ~1,000 without pruning or consolidating redundant checks.
- **Table Parameterization (`test.each`):** When adding coverage for new edge cases, consolidate individual `it(...)` blocks into a single parameterized `test.each` matrix to eliminate suite setup/teardown latency.
- **Fast Lane Execution:** Run only the affected test file during development (<3s feedback loop).

---

*Compress early. Compress often. Stay under budget.*
