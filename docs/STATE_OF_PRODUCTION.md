# State of the Production
*The Thulans — Ground Truth, Asset Status & Critical Path*  
*Path: `docs/STATE_OF_PRODUCTION.md` | Date: 2026-09-11 (Updated under RULINGS 023-031)*

---

### Executive Summary
The narrative, thematic, demographic, economic, and philosophical foundation is 100% locked, unified, and de-slopped. RULING 031 establishes the definitive canon for Varek's absolute human death, the reconstructed Council machine, the unpurged residual control lattice, and the final quiet load transfer in the abandoned drift.

On the 3D technical production side, the mechanical Left Hand rig (`varek-v55-mechanical-grip.blend`) is fully assembled and visually certified: 2-DOF universal gimbal yoke nested in `Wrist coupling L`, heavy 136mm cast-iron palm plate, 3 articulated 34mm forged box digits with clevis ears and 14mm pins, opposable lateral thumb, zero mesh intersection (0 surface polygon crossings), and canonical `tool` bone binding under RULING 024.

---

### 1. What Is Built & Working

* **Narrative, Canon & World Architecture (100% Locked & De-Slopped):**
  * **Master Novella & Prose:** [`THE_DISMANTLING_OF_VAREK.md`](file:///home/aaron/animation/thulans-production/docs/THE_DISMANTLING_OF_VAREK.md) and [`VAREK_ACTS_ONE_AND_TWO.md`](file:///home/aaron/animation/thulans-production/docs/VAREK_ACTS_ONE_AND_TWO.md). Granular, tactile human prose; zero AI boilerplate or melodrama.
  * **Unified Spine (RULING 029):** Wulfila (19), Haila, Bram (14), and Sanna (18) are a single family core across a 40-day tragedy. Varek's complicity in Wulfila's sacrifice drives his rescue of Bram and his voluntary dismantling in Lower Four.
  * **Demographic Scale & Historical Decay (RULING 030):**
    * **Peak Population:** ~42 million (historical engineered capacity at zenith 3,000y ago).
    * **Present Population:** ~4.2 million (10:1 demographic collapse after centuries of aquifer failure and abandoned tiers; ten people living in infrastructure built for a hundred).
    * **Ark Triage:** Six atmospheric arks $\times$ 100,000 = 600,000 capacity (~14.3% of the population, 1 in 7). 3.6 million people cannot leave. Theodemir's slate scene mathematically anchored to this triage.
    * **Timbermen Union:** ~40,000 timbermen (~1% of the entire polity, dominant industrial force).
  * **The Varek-Machine & The Residual Pattern (RULING 031):**
    * **Absolute Human Death:** Varek dies as a man in Lower Four when his hand closes in Sanna's. No digital soul, no uploaded brain.
    * **Dual Systems:** Council Varek (command queue, quotas, propaganda) vs. Residual Varek (kinesthetic reflexes accumulated over 300 years of mechanical compensation: approaching unstable stone, checking the second survivor first, knocking twice).
    * **Subtle Cruelty:** The machine genuinely saves lives; the regime uses authentic goodness as its most potent lie: *"Varek still serves."*
    * **The Epilogue:** Decades later, an unmonitored machine knocks twice at a rusted blast door in an empty drift, seals an unneeded vent, assumes the load-bearing stance, and makes a 4mm actuator correction transferring load away from an empty gallery. Pointless—unless you are Varek.
    * **Thematic Maxim:** *"A society can preserve the pattern of a good man while destroying the man who made it."*
  * **Grounded Physics & Iron-True Geology (RULING 024, RULING 030):**
    * *Faírg-Tygil* operates strictly via high-flux pulsed electromagnetism and hydraulic reaction transfer into the chassis and anchored boots. No gravity negation. *"Graviton"* is strictly drift miner slang.
    * Shaft 44 rock is explicitly **banded magnetite-ironstone** (*blôþ-stáin* / hematite skarn) and forged iron shoring pins, not non-magnetic basalt.
  * **Screenplay Treatment:** [`THE_THULANS_FEATURE_PITCH.md`](file:///home/aaron/animation/thulans-production/docs/THE_THULANS_FEATURE_PITCH.md). 90-minute feature layout with 19-day physical proof and Theodemir's arithmetic locked.
  * **Core Governance:** 3,000-year deep civilization vs. 300-year Varek caisson lifespan (RULING 027). Council of Three with Archon Theodemir as executive arithmetic authority (RULING 028).
  * **Tightened Reference Documents:** [`THULAN_POLITICAL_ECONOMY.md`](file:///home/aaron/animation/thulans-production/docs/THULAN_POLITICAL_ECONOMY.md) and [`THULAN_CULINARY_READER.md`](file:///home/aaron/animation/thulans-production/docs/THULAN_CULINARY_READER.md) condensed into production briefs.
  * **Trailer Audio Grid:** [`shots/TRAILER_AUDIO_MAP_78BPM.md`](file:///home/aaron/animation/thulans-production/shots/TRAILER_AUDIO_MAP_78BPM.md). Locked 78 BPM tempo grid to `Familiar_Stone_Take3_Master.wav`.

* **3D Mechanical & Geometric Assets:**
  * **Right Arm Manipulator (v54 Baseline):** Copper induction ring (open torus), cast-iron docking collar, 3 articulated talons arranged in a 120° chuck, braided forearm conduits (`varek-v54-graviton.blend`, sha256 `fd8e1bec...`).
  * **Left Wrist Universal Gimbal (v55 Baseline):** 2-DOF nested yoke (outer pitch ring -20° to +45°, inner yaw ring -15° to +20°, 4 clevis pins) nested inside `Wrist coupling L` (`varek-v55-mechanical-grip.blend`).
  * **Left Hand Digit Architecture (v55.1):** 136mm cast-iron palm plate chassis, 3 articulated 34mm forged box digits with clevis ears and 14mm pins, opposable lateral thumb.
  * **Zero-Penetration Interlocking Grip:** Maul offset by 24mm along palmar normal, achieving exact 0 surface polygon crossings in both rest and grip poses.
  * **Tool Binding:** 30 kg *Faírguni-Hamars* maul driven canonically by `tool` bone parented to `hand.L` (RULING 024 Part 3).
  * **Visual Verifications:** Rendered and inspected via `view_file`:
    * `evidence/varek-v55-mechanical-grip/left_hand_grip_closeup.png` (frame 48, Cycles)
    * `evidence/varek-v55-mechanical-grip/left_hand_rest_closeup.png` (frame 1, Cycles)
    * `evidence/varek-v55-mechanical-grip/left_hand_wrist_gimbal.png` (frame 1, Cycles)
    * `evidence/varek-v55-mechanical-grip/v55_full_character_q34.png` (Cycles full body showcase)
  * **Engineering Specifications:**
    * [`docs/VAREK_HAND_RIG_SPEC_v1.md`](file:///home/aaron/animation/thulans-production/docs/VAREK_HAND_RIG_SPEC_v1.md)
    * [`docs/VAREK_HAND_PHYSICS_TEST_ENVELOPE.md`](file:///home/aaron/animation/thulans-production/docs/VAREK_HAND_PHYSICS_TEST_ENVELOPE.md)

---

### 2. Active Technical Steps (Hand Physics Gate)

* **Preflight Script Updated (`tools/check_hand_physics_preflight.py`):**
  * Updated to support canonical Left Hand rig (RULING 023) and multi-part hand assemblies.
  * Evaluates independent digit motion, wrist travel limits, physics world, free dynamic tool, and gravity.
  * Baseline check on character rig correctly fails closed (`failures: ["physics_world_missing", "free_dynamic_tool_missing"]`) with evidence frozen in `evidence/varek-v55-mechanical-grip/preflight-baseline.json`.
* **Physics Test Scene Build (`varek-v55-hand-physics.blend`):**
  * Separate diagnostic derivative with active rigid body world and unparented 30 kg dynamic maul to execute finite-force retention and negative controls under gravity.

---

### 3. The Critical Path

```
[LOCKED: Narrative / Screenplay / RULINGS 001-031 / Audio Map]
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│ COMPLETED: Left Hand Mechanical Rig (v55.1)            │
│ • 2-DOF universal wrist gimbal nested in coupling L    │
│ • 136mm cast palm plate + 34mm forged box digits       │
│ • Zero-penetration interlocking grip around maul haft  │
│ • Canonical tool bone binding & verified visual renders│
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ STEP 1: Hand Physics Simulation & Certification        │
│ • Build blender/candidates/varek-v55-hand-physics.blend│
│ • Pass tools/check_hand_physics_preflight.py           │
│ • Run finite-force retention & negative controls (drop)│
│ • Render and inspect diagnostic physics trajectory     │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ STEP 2: Trailer Shot Production                        │
│ • Frame 1 -> Frame 2160 camera layout in Blender       │
│ • Sync cuts to 78 BPM grid per shots/TRAILER_AUDIO_MAP │
└────────────────────────────────────────────────────────┘
```
