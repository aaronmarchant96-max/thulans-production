---
status: draft
authority_scope: anti-slop-and-prose-discipline
owner: Aaron Marchant
applies_to: all-agents-and-human-facing-output
---

# GDR-SLOP: ANTI-SLOP & PROSE DISCIPLINE (DRAFT)

## 1. Scope
Applies universally to:
- Player-facing names, titles, and UI text.
- Agent proposals, plans, reviews, and bus messages.
- Code documentation and commit logs.

---

## 2. The Rule

### A. Player-Facing Naming (No Fantasy Compounds & No Texture Titles)
- All player-facing titles, places, factions, and rituals must clear the **T1–T4 linguistic ladder** (`THULAN_LANGUAGE_NOTE.md`).
- **Prohibited:** Generic English fantasy compounds (*Ashwake, Blackstone, Ironborn, Emberfall*).
- **Exception:** "Deephearth" — Aaron-approved override (2026-09-18). Gothic compound, lore-consistent, Tier A load-bearing title for the game.
- **Prohibited:** Promoting Tier B texture names (*the Wahlja, Azg-Haíms, blôþ-stáin*) to primary game titles. Per `AUDIENCE_PRIMER.md`, texture names must never be introduced on first contact.
- **Enforcement:** Primary titles must be Tier A load-bearing or plain documentary English (*Thulan*, *Fairguni*, *The Soul-Tenth*). If a name does not clear this filter, it is rejected.

### B. Agent Prose Discipline (No Metaphor Inflation)
- **Prohibited:** 
  - Self-important adjectives (*"unyielding," "monumental," "profound," "relentless," "seamless"*).
  - Doctrine voice (*"The sacred duty of the system is..."*).
  - Cosmetic emoji ladders, ASCII trophy shelves, and rhetorical padding.
  - Invented honorifics (*"the Meier Gate," "the Intimacy Doctrine"* when referring to standard unit tests).
- **Required:** 
  - Terse, declarative imperatives: state what will be executed, which file is touched, which ruling is cited, and what the assertion tests.
  - Deliver verification receipts: exact command, exit code, and stdout numbers.

### C. Cut Scale-Only Words (RULING 001)
If a word exists only to make the proposal or setting sound larger, cut it.
