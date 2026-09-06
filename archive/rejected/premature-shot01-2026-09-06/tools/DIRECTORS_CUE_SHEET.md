# THE THULANS: DIRECTOR'S AUDIO-VISUAL CUE SHEET & SHOT MAPPING

---
status: production-authoritative
scope: Audio-to-Animation Synchronization (Blender VSE / Camera FX)
track: Green Metal Heelspikes x varek_soundtrack_master (Mashup).mp3 (5:32.5) / Green Metal Heelspikes.mp3 (0:59.8)
---

## 1. The 35s Teaser: Core Visual-Lore Synchronization

| Time / Marker | Audio Element | Visual Direction & Lore Beat | Key Technique |
| :--- | :--- | :--- | :--- |
| **0:00 – 0:08** | Sub-bass *THOOM* + Anvil *CLANG* | Low-angle camera dolly across the basalt floor moving with the bass pulse. Foreground foundry hammers strike anvils on the beat. Extreme wide shot of thousands of flickering filament lamps up the cavern. | **Geometry Nodes instancing**; 1–2px micro-shake on bass hits. |
| **0:08 – 0:17** | Rhythmic Work Chant + Distant Sirens | Zoom into a row of soot-covered miners singing in unison; cut to a temple mural depicting the *Life Tithe* (a child lowered into a shaft). Ceiling cracks spiderweb; dust rains down. | Camera tilts Up-Mountain toward the distant unreachable summit, then plunges Down-Mountain. |
| **0:17 – 0:24** | Heavy Pneumatic *HISSSS* | Low-angle shot of Varek's iron boots slamming into bedrock. Pneumatic heel-spikes punch into stone. Camera tilts up over scarred boiler-plate to reveal the green *Gren-Skildus* and stitched clan runes. | Particle burst on heel impact; amber glow on narrow quartz visor slit. |
| **0:24 – 0:30** | Choral Explosion: *"SO ENDURE ME!"* | The cavern ceiling drops for 4 frames and **abruptly freezes on contact with Varek's raised hands**. Static camera locked in place; background shockwave ripple. | **Impact Freeze Technique**; radial displacement modifier on dust particles. |
| **0:30 – 0:35** | Hard Cut to Black; Steam Exhale | Screen is completely black. Slow *chug-chug* of the idling rear diesel engine. Varek speaks softly through the sulfur filter: *"I had a mother."* | Faint single anvil ring fades into absolute silence. |

---

## 2. The 330s Master Short Film: Extended Lore Synchronization

### Act I: The Daily Reality & The Staged Miracle (0:00 – 1:30)
* **Visual Hierarchy:** Clean grain crates and water tanks hoisted Up-Mountain on heavy cable cars; slag, dust, and sulfur exhaust venting downward into residential sectors.
* **The Mother's Tragedy:** A background shot of a weeping mother receiving a clean water cup after a *Life Tithe*, while the camera pans past a copper conduit stamped with an old inspection date: `Survey Approval: 4 Weeks Prior`.
* **Sound-to-Action:** Miners' shovels and pickaxes strike stone in sync with the transient rhythm.

### Act II: The Witness & The Acceleration (1:30 – 2:45)
* **The Semantic Challenge:** Varek enters the temple where a *Life Tithe* is prepared under a corrupted Thulan symbol. On the line *"When was it surveyed?"*, the camera cuts to the priest’s stunned, terrified expression.
* **The Tremor Sirens:** Deep subterranean fault lines shift. The elite patricians lock the blast doors and board the silver-hulled atmospheric arks at the True Summit.

### Act III: The Anchor State & The Somatic Sacrifice (2:45 – 5:10)
* **The Physical Collapse:** Central basalt pillars buckle. Millions of tons of mountain fall toward fleeing civilian families.
* **The Anchor State Deployment:** Varek steps into the breach, locking his heel-spikes into the floor and pushing his hydraulic spine past 300% load.
* **Visualizing the Interstice / Void:**
  * No cartoon monsters or tentacles.
  * **Visual Distortion:** The sulfur fog dims; the narrow quartz visor reflects hyper-spatial geometric light that does not exist in the room.
  * **The Internal Reflection:** Micro-shot inside the helmet looking out through the slit; the Void's cold, contractual words appear as faint phosphor text on the inside glass.
  * **The Double-Breath:** The audio layers a subtle second mechanical breath into Varek's respirator, signifying the somatic entry.

### The Climax: Reclaiming the Ancient Truth (5:10 – 5:32)
* **The Static Anchor:** The camera locks into a completely motionless wide shot of Varek holding up the mountain.
* **The Roar:** On the climactic roar ***“SO ENDURE ME!”***, the frame experiences a 2-frame shockwave kick, the green pauldron (*Gren-Skildus*) hairline-cracks under the load, and the scene smash-cuts to black.

---

## 3. Blender Animation Workflow: Baking Waveforms to F-Curves

To automatically drive camera shake, hydraulic strain, and lighting flicker from the master audio:

```python
# Blender Automation: Bake Audio to Camera F-Curve
# 1. Select Camera in 3D Viewport.
# 2. In Graph Editor: Key -> Bake Sound to F-Curves.
# 3. Select 'thulans-production/assets/audio/Green Metal Heelspikes.mp3'.
# 4. Set Low Freq = 20Hz, High Freq = 120Hz (for Bass/Anvil impact shake).
```

* **Frame 048:** Anvil strike → Foundry hammer hits stone.
* **Frame 120:** Pneumatic hiss → Helmet vent particle emitter bursts.
* **Frame 240:** Heel-spike deploy → Bedrock fracture modifier activates.
* **Frame 480:** Vocal Climax → Camera kick + shockwave displace.
