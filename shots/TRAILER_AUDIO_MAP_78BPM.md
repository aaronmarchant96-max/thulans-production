# TEASER TRAILER SPEC: THE WEIGHT OF A LIE (CANONICAL V2.2 LOCKED)
**Track:** `Familiar_Stone_Take3_Master.wav` (78.000 BPM | 4/4 Time | 24 FPS Sync | 90.00s / F2160)  
**Governing Rule:** RULING 001 (The Intimacy Rule) — *"Never let the Mountain become bigger than the people crushed beneath it."*
_V2.2 adds the Dual-Domain Hand-off & Production Contract (Blender/REAPER/NLE sync). V2.1 struck the title-card tagline under RULING 005._

---

## ⏱️ Master Audio-Visual Grid (78.000 BPM | 1 Bar = 3.0769s | 24 FPS)

```
BAR / BEAT    TIME (s)    FRAME (24fps)    VISUAL STATE                                        AUDIO / VO / FOLEY CUE
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
[M01.1]       00:00.00    F0000            Behind Varek: Mountain chasm in total collapse      Solitary Felt Piano opens (Haunting motif)
[M03.1]       00:06.15    F0148            Macro: cracked iron visor, single weary human eye   Respirator hiss, deep hydraulic groan
[M05.1]       00:12.31    F0295            Reverse begins: falling slabs rise, flames retreat  Reverse rubble whoosh, low tectonic groan
[M07.3]       00:20.00    F0480            Hydraulic struts snap back to rigid Anchor State    Metallic latch `CLANG` in reverse reverb
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
[M09.1]       00:24.62    F0591            Wide Reverse: 2,000m chasm reconstructing backward  VO 1: "They told us the Mountain provided."
[M11.1]       00:30.77    F0738            Panic rewinds; cut to individual terrified faces    Cello enters (mournful legato drone)
[M13.1]       00:36.92    F0886            Lift cables reconnect, burned depots re-assemble    Electrical reverse-arc sizzle, gas hiss
[M15.1]       00:43.08    F1034            Depot doors close; smoke sucked into pipes          VO 2: "They told us sacrifice made it answer."
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
[M17.1]       00:49.23    F1182            The spectacle shrinks: Gold valve reverses shut     Piano dynamic lift; low string ostinato
[M19.1]       00:55.38    F1329            Water rushes backward; district cistern empties     Brass gear clicks; rushing water in reverse
[M21.1]       01:01.54    F1477            Two ledgers: Survey Date vs. Tithe Order Date       VAREK (diegetic): "When was it surveyed?"
[M23.1]       01:07.69    F1625            Dates align in silence; paperwork condemns itself   TOTAL SILENCE from bureaucrats; ink stamp reverse
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
[M25.1]       01:13.85    F1772            Continuous downward tracking shot through levels    CHORUS SWELL: Cello + Piano crescendo
[M26.3]       01:18.46    F1883            Wulfila steps backward off Tithe platform (NO CHAINS) Cord untwists in reverse; tear retreats
[M27.3]       01:21.54    F1957            Sister Haila's hand presses hammer-ring into palm   VO 3 (exhausted certainty): "Wulfila volunteered to a lie."
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
[M29.1]       01:26.15    F2068            INT. Ash-Hearth: TIME MOVES FORWARD (Normal motion) TOTAL SILENCE (Music cuts to domestic room tone)
[M29.3]       01:27.69    F2105            Haila playfully wipes soot off Wulfila; he smiles   Stove crackle; soft fabric; off-screen: "Wulfila."
[M30.2]       01:30.00    F2160            SMASH TO BLACK                                      Single low stone strike: THUM (Faírguni-Hamars)
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
```

---

## ⏱️ Dual-Domain Hand-off & Production Contract

**Domain 1 — Tempo-Slaved (`M01.1`–`M29.1`, 0:00.00–1:26.15):** while the score is
active, cuts, reverse foley swells, and Varek's voiceover lock to the 78 BPM grid
(1 bar = 3.076923s; 1 beat = 0.769231s). When the music dies on `M29.1`, the timeline
stops obeying bar downbeats.

**Domain 2 — Frame-Governed (F2068–F2160, exactly 92 frames of forward-time domestic):**
the score and reverse motion are dead; natural forward 24 FPS motion only. Wulfila at the
stove; Haila wipes the coal soot; off-screen voice *"Wulfila."*; he looks up alive and
whole.

| Event | Time | Frame | Source |
| --- | ---: | ---: | --- |
| Score dies to room tone (`M29.1`) | 01:26.154 | F2068 | 28 bars × 3.076923s |
| `M30.1` (room tone continues) | 01:29.231 | F2142 | 29 bars × 3.076923s |
| SMASH TO BLACK + `THUM` (`M30.2`) | 01:30.000 | F2160 | 29 bars + 1 beat |
| `THUM` acoustic decay tail (`M31.1`) | 01:32.308 | F2215 | 30 bars × 3.076923s |

**Contract:**
1. **Blender:** render range **Frame 1 → Frame 2160** (90.00s).
2. **Cut to black:** **Frame 2160**.
3. **REAPER:** marker `[08_SMASH_BLACK]` at **M30.2** (01:30.000 / F2160); place the
   *Faírguni-Hamars* `THUM` sample there. Its ~2.3s resonance decays F2160–F2215 under
   the title card. **M30.1 is not the cut** — exactly one beat separates it from the smash.
4. **Title card:** `THE THULANS` only, no tagline (RULING 005 trailer ban).

---

## 🎬 Granular Shot-by-Shot Director's Breakdown

### Phase 1: The Consequence (`00:00.00` – `00:24.61` | M01.1 – M08.4)
* **Camera:** Opens from behind Varek—a hulking, scarred bulkhead silhouette framed against the vast burning expanse of a multi-level mining chasm in total collapse. Cuts to macro extreme close-up on his cracked iron visor. Through the aperture, a single human eye blinks. Blood streaks down pitted armor.
* **Music & Audio:** Felt upright piano plays the mournful opening motif. Deep, rhythmic mechanical respirator breathing inside the helmet.
* **Reverse Action:** The reverse motion begins almost imperceptibly. Dust gets pulled back into hairline fractures. Floating fire embers retreat into ruptured pipes. The sheared hydraulic legs un-buckle, rising back into rigid Anchor State on `M07.3` (`00:20.00`).
* **Dialogue:** **None.** We let the audience ask: *What happened to this world?*

---

### Phase 2: Civilization Rewinds (`00:24.62` – `00:49.22` | M09.1 – M16.4)
* **Camera:** Wide cavern pull-back, but repeatedly cutting in to **individual human faces** in the crowd to maintain RULING 001.
* **Reverse Action:** Panicking miners run backward out of elevator gates. Provision depots re-assemble from ash. Severed gantry cables whip upward and reconnect to iron pylons.
* **Varek Voiceover (Weary, quiet, steady):**
  > `00:24.62` ➔ *"They told us the Mountain provided."*  
  > `00:43.08` ➔ *"They told us sacrifice made it answer."*
* **Music & Audio:** Solo cello enters with a low, mournful pedal drone. Rushing air and reverse fire whooshes.

---

### Phase 3: The Bureaucratic Crime (`00:49.23` – `01:13.84` | M17.1 – M24.4)
* **Camera:** The spectacle shrinks from planetary disaster down to cold interior infrastructure.
* **Reverse Action:**
  - A heavy gold-trimmed valve wheel spins backward, shutting off flow.
  - Water in a communal cistern surges backward into ceiling conduits.
  - The scene cuts to a mundane desk in the upper administrative quarter: **two physical paper ledgers** are being pulled apart in reverse.
    - **Document A (Survey Ledger):** `NORTH AQUIFER — Surveyed & Verified: [Date X]`
    - **Document B (Faith / Provision Order):** `Reveal Rite / Life Tithe — Authorized: [Date Y (Weeks Later)]`
  - A surveyor's trembling hand briefly aligns the two dates before the reverse motion slides them into separate folders.
* **Varek Voice (Diegetic, quiet, in-scene radio tone):**
  > `01:01.54` ➔ **“When was it surveyed?”**
* **The Response:** **NO VERBAL ANSWER.** No dialogue from the bureaucrat. The silence and the two visible dates answer him. The cold sound of an ink stamp lifting off paper in reverse.

---

### Phase 4: The Consent of Wulfila (`01:13.85` – `01:26.14` | M25.1 – M28.4)
* **Camera Transition:** A continuous, heavy downward tracking shot descending through the groaning iron girders, freight cages, and soot-stained work tiers of the Mountain, arriving at the public square of Azg-Haíms.
* **Visual Action:**
  - Wulfila (19 years old, soot-stained, terrified but resolute) **steps backward off the Life Tithe platform**.
  - **NO SHACKLES. NO GUARDS. NO GALLOWS.** His hands are completely free. He volunteered to save his starving hearth.
  - The ceremonial shroud slips backward off his shoulders into the priest's hands.
  - **Hammer-Ring Continuity (Forward-defined, inverted):** In life, Haila tied the crude cord around his neck and pressed the iron ring into his hand; in reverse, the braided cord untwists from his collar, lifting back into Haila’s trembling fingers as she presses the ring into his open palm. A tear on her cheek flows upward into her eye.
* **Varek Voiceover (Delivered with flat, exhausted certainty — not dramatic, not angry):**
  > `01:21.54` ➔ **“Wulfila volunteered to a lie.”**
* **Music:** Full orchestral crescendo (Piano + Cello + Chamber Strings) reaches peak dynamic pressure.

---

### Phase 5: The Forward Reversal (`01:26.15` – `01:30.00` | M29.1 – M30.2)
* **The Masterstroke:** **THE SCORE DIES ON M29.1.** Complete cut to dry, domestic room tone.
* **THE REVERSE MOTION STOPS:** For the first time in the entire trailer, **time moves FORWARD in normal 24 FPS motion.**
* **Visual:**
  - Inside a modest, soot-warmed stone hearth. A kettle murmurs on an ordinary coal stove.
  - Wulfila sits at a wooden table in an ordinary coarse tunic.
  - Haila playfully wipes a smudge of coal soot off his nose with her thumb; Wulfila rolls his eyes and smiles an ordinary, nineteen-year-old boy's smile.
  - From off-screen, a woman's gentle voice calls:
    > *“Wulfila.”*
  - Wulfila looks up toward the doorway, alive and whole.

---

### Phase 6: The Black & The Tool (`01:30.00` | M30.2 / Frame 2160)
* **`01:30.00` (F2160):** **SMASH TO BLACK.**
* **Sound Effect:** One single, low, physical strike of *Faírguni-Hamars* against solid bedrock:  
  *`THUM.`* (Long acoustic geological decay).
* **Title Card:**

```
                   T H E   T H U L A N S
```
