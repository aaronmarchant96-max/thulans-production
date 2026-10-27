# The Thulans: Salvation - motion production

**Story status:** canonical companion story, confirmed by the author on 27 October 2026.

**Production status:** planning package. No finished film, measured runtime, approved panel artwork, or audio master is supplied here.

Eleven Bells was a prototype made before the story was written. Its existing folder is preserved. Its plates, music, timing, and production approval claims do not transfer to Salvation.

## Read first

- [The canonical story direction](../../docs/SALVATION_STORY_DIRECTION.md)
- [The 16-page pilot, revision 3](../../docs/SALVATION_PILOT_16_PAGES.md)
- [Plan for pilot revision 4](../../docs/SALVATION_REVISION_PLAN.md)
- [The episode specification](EPISODE_SPEC.md)
- [The motion and audio brief](MOTION_AUDIO_BRIEF.md)
- [The violence doctrine](../../docs/THULAN_VIOLENCE_DOCTRINE.md)

The pilot predates the latest relationship/pacing brief. This package maps the existing 66 panels; it does not silently claim that a new script pass has been written.

## Production files

| File | Purpose |
| --- | --- |
| [EPISODE_MANIFEST.json](EPISODE_MANIFEST.json) | Canon and production statuses, source hash, proposed delivery settings, open work. |
| [SHOT_LEDGER.csv](SHOT_LEDGER.csv) | One row per source panel, from P01_01 to P16_03; source lines, dialogue, motion/audio guidance, and blank timing fields. |
| [storyboard_beats.json](storyboard_beats.json) | The same source-linked beats for production tools. |
| [ASSET_REGISTER.json](ASSET_REGISTER.json) | Required art and audio, explicitly marked missing. Proposed filenames are not supplied assets. |

## Working order

1. Review the relationship/pacing brief and explicitly revise the script if needed. Keep its source identity and panel mapping synchronized.
2. Resolve the route after Ansen's established Chapter Ten/Eleven presence and block Frame 9's controls, loaded connection, grip, and shutoff.
3. Create and approve panel compositions and required motion layers. Do not silently reuse prototype plates or treat title-page experiments as locked designs.
4. Record a scratch read and original audio, then measure the edit. Keep voice playback natural at 1.0.
5. Enter measured timing in the ledger and use an episode-neutral render path to assemble a review animatic.

The proposed delivery is 1920x1080 at 24 fps. Neither setting establishes runtime. Timing fields remain empty until measured; no fixed duration is derived from sixteen printed pages.

## Exporter limitation

The existing [exporter](../../tools/export_animatic.py) has Eleven Bells-specific shot mappings, fallback images, bell-triggered motion, audio defaults, and segment-cache behaviour. Even its dry run requires audio and does not establish that all plates exist. This package is not claimed compatible with it. No exporter or frozen physics file was changed by this planning work.

## Source changes

The manifest and storyboard store the pilot's SHA-256. If the source changes, review the mapping, dialogue, and brief rather than treating old cached media as current. Keep Eleven Bells and the novella mirrors outside this episode's generated outputs.
