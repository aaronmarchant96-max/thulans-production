# CHARTER SCOPE AMENDMENT: CINEMATIC-001
*Interactive Cinematic Drama & Shifting Perspective Proof of Concept*

---

## 1. Track Authorization & Scope Reorientation
- **Track Designation**: `CINEMATIC-001` (retired track `HEARTH-001/002` remains archived).
- **Core Vision**: An **interactive cinematic drama with shifting perspectives** (*As Dusk Falls* model). The game delivers the moral weight of a dying mountain civilization through illustrated cinematography and dramatic irony, strictly obeying **RULING 001 (The Intimacy Rule)**.
- **Negative Scope (Out of Scope)**:
  - No 3D environments, no skeletal character rigs, no physics-based pathfinding, no per-pawn simulation.
  - No resource spreadsheet dashboards.
  - No speculative multi-scene branching.

---

## 2. The First Build: Cinematic Proof of Concept (CPoC)
A single dramatic arc testing one falsifiable hypothesis:
> *"Does experiencing the human reality through Wulfila's perspective make the Steward's administrative decision significantly more meaningful than experiencing the survey discovery alone?"*

### Structural Flow:
```
1. SCENE A: THE STEWARD (Records Cell 4) [Day +40: The Present]
   - Setting: 40 days post-Tithe, contemporaneous with the impending Shaft 44 collapse. Employs RULING 001 Awe Exception juxtaposition: intimate first-person desk in foreground overlooking the colossal subterranean chasm vista.
   - Inspects Ledger 884-W: Discovers the Watona aquifer sounding occurred 40 days before the sacrifice (Day -40).
   - Core revelation: The shortage is real. The reserve was known before the sacrifice. Its controlled release is fraudulently presented as a miracle. (Nuance: the Watona district shortage is staged via withheld water; the Mountain scarcity is real. Hold both.)

2. CINEMATIC CUT: PERSPECTIVE SHIFT
   - Atmospheric camera pan / lighting wipe from iron desk to cold rock.

3. SCENE B: WULFILA (Lower Four Drift Bunk) [Day 0: Flashback]
   - Wulfila in the tenement drift with Bram (14).
   - The summons docket arrives: Bram is drafted for the lethal deep copper shifts at Shaft 44.
   - Wulfila confronts the horror: volunteering for the Life Tithe platform to buy a family water exemption and spare his brother.
   - Dramatic Irony: Wulfila does not know the water already exists.

4. PERSPECTIVE SHIFT BACK: THE DECISION [Day +40: The Present]
   - Returns to the Steward holding the pen over Ledger 884-W as the Shaft 44 crisis crests.
   - Three distinct, consequential branches:
     - [EXPOSE TO DISTRICT]  (RULING 013 & DISMANTLING:41: Sounding date posted to timber flumes; triggers Azg-Haíms timber strike for 12h shifts; timber halts, pulling miners—including Bram—off shift before cave-in; Council reprisals follow)
     - [BURY IN THE LEDGER]  (RULING 004 & 029: The lie holds; timber flows at 16h; Bram enters Shaft 44 on schedule; canon roof shear crushes his leg; FEATURE_PITCH:52)
     - [LEVERAGE TO HALZA]   (RULING 008 "The Corruption of 'Endure'": Steward sells date to House Halza; uses grain payment to bribe clerk and pull Bram from roster; Halza hoards dry rights)
```

---

## 3. Authoritative Canon Rulings Attached

| Item | Ruling | Canonical Source |
| :--- | :--- | :--- |
| **Watona Sounding Date** | **40 days before the Tithe.** Capped holding 11 million gallons in reserve. | `THE_DISMANTLING_OF_VAREK.md:31` |
| **Bram's Status & Alternate Timelines** | **Prime Canon vs. Authorized Divergence (Ruling: Aaron Marchant, 2026-09-17).** Prime Canon (`BURY`) preserves the locked screenplay invariant: Bram's leg is crushed in Shaft 44 (`FEATURE_PITCH:52`). In authorized alternate branches (`EXPOSE`, `LEVERAGE`), player choices diverge from screenplay canon to pull Bram off the shift, testing systemic trade-offs. | `FEATURE_PITCH:52` & Aaron Ruling |
| **Interactive Framing Device** | The Hearth Steward in Records Cell 4 at [Day +40] is an interactive dramatic device contemporaneous with the Shaft 44 crisis (`VAREK_ACTS:82`). | Design Grounding |
| **Local Boundary** | The Steward's actions alter local district flumes, timber strikes, and Bram's immediate roster status, never preempting Varek's global ark revelation (`DISMANTLING:31-49`). | `DISMANTLING:31-49` |
| **Wulfila's Motive** | **Family water exemption & keeping Bram out of the deep drifts.** | `THE_DISMANTLING_OF_VAREK.md:35` |
| **Cast Ceiling** | Theodemir (Seat Two), Malakor (clerk), Wulfila, Sanna, Bram, Haila, Halza (factor). | `NAME_CANON.md` §T1–T4 |

---

## 4. Evaluation Gates (VAG & Consistency Suite)

### A. The Human Gate: Visual Atmosphere Gate (`docs/VISUAL_ATMOSPHERE_GATE.md`)
Subjective atmospheric quality is not automatable. Every scene must be reviewed and approved by Aaron based on 7 qualitative criteria:
1. Tone (Administrative horror, tactile industrial)
2. Intimacy Rule (RULING 001 amended, human scale default with the Awe Exception for establishing/chasm vistas)
3. Palette conformance (`#12171a`, `#1c2326`, `#d8d2c0`, `#e8a13c`, `#b04a3c`)
4. Lighting logic (physical source consistency)
5. Readability (high typographic contrast)
6. Originality (distinct Thulan Gothic identity, not a visual clone)
7. Lore fidelity (zero magic, zero fantasy compounds)

### B. The Automated Gate: Consistency Suite (`visual.consistency.test.ts`)
Automated Vitest suite verifying mechanical invariants:
1. Palette conformance scanner on all SVG/CSS styles.
2. Character spec determinism (`portraitSpec` hash matches across scenes).
3. Naming verification against `NAME_CANON.md`.
4. Text scan against `GDR_SLOP.md`.
5. Hotspot boundary validation (no overlap, normalized $0 \le x,y \le 1$).
6. State reachability and zero dead ends.
7. SHA-256 asset pinning.

---

## 5. Background Art Strategy
- **PoC Strategy**: CSS/SVG-layered architectural vector compositions (iron grates, kerosene falloff gradients, rock ceiling silhouettes).
- Zero external dependencies, zero license ambiguity, zero generation costs.
- External illustration/concept art pipelines remain gated until the PoC dramatic pacing is proven.

---

## 6. Measurable Proof-of-Concept Standard
1. **A/B Decision Distribution**: Comparing Arm A (Steward only) vs. Arm B (Steward $\rightarrow$ Wulfila $\rightarrow$ Steward). Arm B must demonstrate a measurable shift in branch selection and increased dwell time ($>15$ seconds).
2. **Qualitative Justification**: Playtesters must spontaneously cite Bram's impending draft or Wulfila's sacrifice as their decision rationale.
