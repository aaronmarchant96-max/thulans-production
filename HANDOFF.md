# Production Handoff: Eleven Bells Motion Graphic Novel Track

**Date**: 2026-09-27  
**Status**: COMPLETE AUDIO MASTER & AUDIO-VISUAL DELIVERABLES READY  
**Playback Rate**: Locked at 1.066 (Tape-transport pitch & speed)

---

## 1. Verified Master Audio Assets & Measured Checksums

### A. The Canonical 03:33 Cinematic Trailer Master (10s Intro, 6–8s Dramatic Pauses)
* **Date**: 2026-09-28
* **Status**: **CANONICAL PRODUCTION AUTHORITY**
* **Runtime**: 03:32.95 (212.95s)
* **Playback Rate**: 1.000 (100% natural vocal timbre, unhurried gravitas)
* **Pacing Architecture**:
  * **0:00 – 0:10.00**: 10 full seconds of solo atmospheric music. Heavy cello motif and downbeat at 6.5s ring out before the first word is uttered.
  * **0:10.00 – 3:11.88**: 19 discrete vocal statements with generous **5.5s to 8.0s theatrical breath pauses** letting stone reverb, water drips, and bell tolls hang in the air.
  * **3:11.88 – 3:32.95**: Full 21-second mournful strings outro dissolving into silence.
* **DSP Processing**: Vocal HPF at 80 Hz, music carved at 320 Hz and 2.2 kHz (-2.5 dB), sidechain ducking (-2.5 dB), True Peak ceiling at -1.0 dBFS.

| File | Specs | Checksum (MD5) |
| :--- | :--- | :--- |
| `~/Downloads/THULANS_Eleven_Bells_Cinematic_3m30_Master.wav` | 03:32.95, 48kHz 24-bit broadcast WAV | `e1be3300538bc1deb6b48ecaf5d9980c` |
| `~/Downloads/THULANS_Eleven_Bells_Cinematic_3m30_Master.mp3` | 03:32.95, 320 kbps MP3 stereo | `4b333277b1ff00e0b624cf99606a1591` |

### B. Previous Shorter Reference Takes
| File | Specs | Checksum (MD5) |
| :--- | :--- | :--- |
| `~/Downloads/THULANS_Eleven_Bells_Master_EQ_Carved.mp3` | 02:52.95, 320 kbps MP3 (5s intro) | `4bc0c1b5ee933aa16f65b4e79c5ea528` |
| `~/Downloads/THULANS_Eleven_Bells_Teaser_Master.mp3` | 02:42.24, 320 kbps MP3 (1.066 speedup) | `4744952f5ceb1b13a40f61d5e76716b8` |
| `~/Downloads/THULANS_Eleven_Bells_Teaser_Master_48k24.wav` | 02:42.24, 48kHz, 24-bit stereo broadcast WAV | `de75db0e23baca8e41bf2d9687d7a80b` |
| `~/Downloads/THULANS_Eleven_Bells_Teaser_Video.mp4` | 02:42.24, 1080p H.264 / AAC 320k | `09bbcebeae8420709515ac9c21c377e7` |

---

## 2. REAPER Integration & Track Layout (`Eleven_Bells_Project.rpp`)

* **Project Playrate**: **1.000** (Restored to natural vocal delivery).
* **Track 1 (`01_Aaron_Dialogue_TAKE7_MASTER`)**: 19 discrete items with 40ms cosine crossfades, starting at 0:05.00 with expanded cinematic pauses. Active at 0.0 dB unity.
* **Track 2 (`02_SHAFT_STONE_REFLECTION_AUX`)**: 19 matching reflection items (-18 dB, 48ms pre-delay).
* **Track 3 (`03 AARON NEW INSTRUMENTAL`)**: Clean isolated instrumental stem at -5.5 dB, runs continuously 0:00 to 02:52.95.
* **Track 4 (`04 Prev Music Take`)**: Previous music take (Muted reference).
* **Timeline Markers**: 15 updated markers mapped to the new spacious timing spine.
* **Master Headroom**: -1.0 dBFS True Peak, zero master clipping.

---

## 3. Visual Director Desk & REI.ai Integration

* **Location**: Flagship web app `rei-ai` at `/home/aaron/repos/rei-ai` (`/#storyboard`).
* **Backend Bridge**: `rei-ai/api/storyboard.js` mounted at `/api/storyboard` in `server.js`.
* **Director Interface**: `src/modules/storyboard/GraphicNovelStudio.jsx`:
  * **16:9 Cinema Stage**: Live Dark Horse lettering overlay preview (Bebas Neue title, Share Tech Mono tactical sector, Barlow Condensed dialogue caption).
  * **Modular Prompt Chips**: Fooocus-style non-destructive state (`activeChips = new Set(...)`) covering Mignola Inking, Heavy Slate Shadows, Verdigris Patina, Boiler Anatomy, and Zero-Swords hard negative rules.
  * **Reference Conditioning**: AGY Native `ImagePaths` conditioning using canon plates (`plate_02_the_welded_profile_canon.jpg`).
  * **A/B Split-Screen**: Instant visual parity check between generated drafts and canon benchmarks.

---

## 4. 24fps Motion Comic Animatic Compiler (`tools/export_animatic.py`)

* **Timeline Engine**: 14 distinct shots parsed from `SHOT_LEDGER.csv` synced to the 212.95s Take 7 Cinematic Master (`0.000s` sync variance).
* **Render Cadence**: 24fps libx264 with high-precision subpixel panning (`scale=2048:1152` into `1920:1080` dynamic crop).
* **Impulse Bell Tremor**:
  * **Bell 1**: 71.28s (01:11.28)
  * **Bell 3**: 84.66s (01:24.66)
  * **Bell 5**: 104.58s (01:44.58)
  * **Bell 7**: 127.66s (02:07.66)
  * **Door Slam**: 156.32s (02:36.32)
  * **Bell 11**: 161.82s (02:41.82)
  * **Filter Math**: `(between(t,rel_t,rel_t+0.4)*sin(2*PI*15*(t-rel_t))*exp(-6*(t-rel_t))*18)` damped harmonic tremor.
* **Output Deliverable**: `episodes/001_eleven_bells/eleven_bells_animatic.mp4`
  * **Duration**: 212.95s (03:32.95)
  * **Video**: 1920x1080 24fps H.264
  * **Audio**: AAC 320 kbps (Uncut Take 7 Cinematic Master)
  * **Filesize**: 26,287,995 bytes (25.1 MB)
  * **MD5 Checksum**: `25532d99f5e61feb7900dee0e730ab44`





---

## 5. Novella Prose Line-Editing Contract & Anti-Slop Directive
* **Document**: `docs/THULAN_NOVELLA_VOICE_CONTRACT.md`
* **Authority**: Aaron Marchant
* **Core Transition**: Shift from prompt generation to forensic line-editing.
* **Banned Vocabulary**: Zero tolerance for LLM crutches (*tapestry, testament, delve, palpable, hummed, danced, symphony, beacon*).
* **Character Registers**: Distinct linguistic separation between Bram (innocent apprentice), Kaelen (cynical frontier smith), Varek (monosyllabic dying acoustic engine), and Sanna (clinical domestic triage).
* **Pacing Contract**: Anti-nihilism rule ("Hope + Cost = Meaning") enforced through tactile labor, dark gallows humor, and sudden kinetic mechanical violence.

---

## 6. Novella Production Status (Acts I, II, & III Locked, Proof-Reconciled, and Omnibus Synced)
* **Chapter 1 ("The Flange & The Pine Sprig")**: Locked. Bram (13) conceals Wulfila's brass chit behind his apron bib; Kaelen spots the yellow reflection in the wet rail web and shifts his knee to quietly shield him. 30mm bolt seizure / tallow grease-pocket verified.
* **Chapter 2 ("The Nursery in Lower Four")**: Locked. Standardized 40-day interval (*"Wulfila gave his name to the Wahlja forty days ago"*); domestic warmth (toddler Elin rolling the wooden bearing-ball, Sanna sharing hot leek broth from the *Kald-Katil*); Sanna is 18; bilge pump pine stave patch (4-hour gamble) and Odo's ration reduction to 6 pints.
* **Chapter 3 ("The Memory of the Leap")**: Locked. Calendar lock verified: North Cistern sounded on 10 September (+18 FT OVERFLOW WEIR); Wulfila gives Bram the dried pine sprig on 11 September; Wulfila leaps on 12 September; present day is 22 October (exactly 40 days later). Bram remembers Wulfila as an imperfect, real brother (stealing barley crusts, wrestling on the straw tick).
* **Chapter 4 ("The Acoustic Trace")**: Locked. Bram wraps the survey slate in flour sacking and slips it into his apron bib before leaving the nursery; Caisson Seven connected to Drift 14 via Shaft 44 ore-incline; Fault Maul mass standardized to 30 kg total tool mass per Page 41 brief. Varek breaches the 4-course brick stop-wall.
* **Chapter 5 ("The Shoring of Drift 14")**: Locked. Bram unwraps the survey slate from his apron and lays it on the dry timber sill for Kaelen and Varek; contrary 66-lb head labels removed; 4-way realization intact; 40 yards/year magma math verified; Lower Four feeder diverted.
* **Chapter 6 ("The Welded Advance")**: Locked. Bram snuffs the nitro fuse with the track dog; Varek disables the Welded frames and releases living occupants; lethal force strictly confined to the guard taking aim at Bram; ends cleanly on Odo's retreat into the dark.
* **Chapter 7 ("The Ascent")**: Locked. Bram and Kaelen hook emergency steam bypass to clutch dog by temporarily idling the Lower Four bilge pump; Kaelen spots grandfather Edrik's Foundry Three punch marks on Varek's hip plate; 40-tonne counterweight gravity car hauls Varek up through the counterweight trunk; meeting stores fitter Tomas; the running washroom tap; Varek knocks on Continuity door.
* **Chapter 8 ("The Office on Tier Nine")**: Locked. Theodemir confrontation; 10 September sounding verified; Master Triage Ledger shows Hearth 12-9 `SURRENDER VALUE: NIL`; Theodemir writes Wulfila's name beside the number; 600,000-berth Ark triage reality; Theodemir signs written order confirming the sounding and ordering restoration of the sealed main.
* **Chapter 9 ("The Hammer Falls")**: Locked. Outside office, Varek learns order stands even if Theodemir is killed (Deputy Gero takes the desk); drops 30 kg maul flat on stone, leaving Archon alive; Tomas unloads lower stone cage allowing gravity descent; Bram and Kaelen wheel Varek on machinery trolley; return ends beside stopped bilge pump in Lower Four as baby Harn cries.
* **Quality Gates**: All 9 chapters scanned: **0 occurrences of 24 banned words**. 100% canon-verified (Wulfila 19, Bram 13 turning 14 on 30 Oct, Sanna 18, 41 winters, Varek 8ft / 300 years, 4.2M / 600k / 3.6M demographics). Complete omnibus compiled into `novella/THE_THULANS_MANUSCRIPT_ACTS_I_TO_III.md` (**123,501 bytes, 2,420 lines**).
* **Master Cover Deliverable**: Aaron Marchant's definitive master cover art **[thulans_cover_master_pine_sprig.jpg](file:///home/aaron/.gemini/antigravity/brain/3c9d0d7b-f1b8-451f-a6eb-40dda09da369/thulans_cover_master_pine_sprig.jpg)** (The Offering: human hand offering green spruce sprig into the open scoop of the *Faírg-Tygil* hydraulic talon) locked as Front Cover. Companion plate **[thulans_cover_master_contact_timber.jpg](file:///home/aaron/.gemini/antigravity/brain/3c9d0d7b-f1b8-451f-a6eb-40dda09da369/thulans_cover_master_contact_timber.jpg)** (The Contact on Shoring Timber) preserved for back cover / Act IV spread.
* **Chapter Illustration Brief**: Integrated from Page 41–42 proof schedule (`FIG. 1a` through `FIG. 9a` technical salvage and service record plates on clean cream grounds with `NOT TO SCALE` record stamps).

---

## 7. Act IV Production Milestone: The Dismantling (Chapters 10–12) — COMPLETE & VERIFIED
* **Chapter 10 ("Bring the Wrenches")**: Locked (2,540 words). Varek parked beside the stopped bilge pump in Lower Four; orders his own people to strip him for parts. Bram steps forward with the spanner to loosen the first collar bolt; miners systematically disassemble the frame into structural cribbing, valves, and pump parts.
* **Chapter 11 ("Skin Against Skin")**: Locked (1,976 words). The human biological remnant exposed: seventy pounds of scarred tissue, fused vertebrae, corneas stitched with silver wire. Sanna cleans his wounds; Varek touches human skin and clean air before dying.
* **Chapter 12 ("Our Iron Anyway")**: Locked (1,959 words). Epilogue. The contrast between the 24-foot bronze heroic monument erected above on Tier Six and the working-class reality below where Junior Surveyor Malakor records "RECOVERABLE ASSETS: NONE" as the salvaged bronze pump barrel keeps Lower Four dry. Sanna wipes the kettle rim: *"No. It was our iron anyway."*
* **Complete Novella Quality Gates**: All 12 chapters scanned: **0 occurrences of 24 banned words**. 100% canon-verified (Wulfila 19, Bram 13 turning 14 on 30 Oct, Sanna 18, 41 winters, Varek 8ft / 300 years, 4.2M / 600k / 3.6M demographics). Complete master omnibus compiled into `novella/THE_THULANS_MANUSCRIPT_COMPLETE.md` and `novella/THE_THULANS_MANUSCRIPT_ACTS_I_TO_IV.md` (**144,236 bytes, 2,755 lines, 24,604 words total / 23,002 chapter prose words**).
* **The Two-Tellings Strategic Fork**:
  * *Telling A (Novella)*: Water-breach / Drift 14 / Bram & Sanna flues rescue.
  * *Telling B (Lore Bible / Pitch)*: Shaft-shear / deep stope rescue of Malakor (reconciled in Ch. 12 as the state propaganda myth).
  * *Status*: Open dual-mythos architectural fork preserved intentionally.
