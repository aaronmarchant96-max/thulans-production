# SHOT 01 PRODUCTION SPECIFICATION: MEGALITHIC CAVERN & SILHOUETTE GATE

---

## 1. Scene Intent & Dramatic Core
* **Shot Code:** `SHOT_01_EST_MEGALITH`
* **Sequence:** Intro Teaser / World Establishing Hook (0:00 – 0:08)
* **Audio Track Reference:** `Green Metal Heelspikes.mp3` (Bars 1–4, low rhythmic anvil clangs, mechanical sub-hum)
* **Core Dramatic Function:** First visual manifestation of the Thulan universe. It must prove the scale, vertical anxiety, dieselpunk brutalism, Varek's heavy silhouette, and the Intimacy Rule without relying on text, dialogue, or surface textures.

---

## 2. The 5 Proof Gates

```
+-------------------------------------------------------------------------+
|                                                                         |
|   [THE MOUNTAIN]  Endless vertical shafts, light towers ascending 2km+  |
|         |                                                               |
|   [CAVERN]        Cyclopean rock buttresses, hanging conduits, smog     |
|         |                                                               |
|   [MACHINERY]     Gantry cranes, hydraulic lifts, ventilation ducts     |
|         |                                                               |
|   [THULAN]        Varek (3.0m) - Overhead yoke, Gren-Skildus pauldron   |
|         |                                                               |
|   [HUMAN]         Ordinary Miner (1.75m) at gantry console rail         |
|                                                                         |
+-------------------------------------------------------------------------+
```

### Gate 1: The Scale Chain (Human -> Thulan -> Cavern -> Mountain)
- **Human (1.75m):** Positioned at the gantry maintenance terminal. Provides the baseline biological scale reference.
- **Thulan / Varek (3.0m):** Towering over the human by nearly double height and quadruple mass. Massive load-bearing stance.
- **Gantry / Machinery (12m - 40m):** Riveted structural steel, hydraulic stabilization pistons, crane rails.
- **Cavern & Mountain (500m - 2,500m):** Thousands of vertical light arrays fading into atmospheric smog above and furnace heat below.

### Gate 2: Vertical Anxiety
- **Camera Tilt & FOV:** 24mm wide angle, low-angle position (1.2m height), tilted upward +14°.
- **Psychological Effect:** The top of the frame is dominated by impossible weight; the bottom drops into an abyss. The viewer immediately understands this civilization is stacked vertically inside a hollowed-out continent.

### Gate 3: Dieselpunk Industrial Identity (De-40k Test)
- **What is NOT present:** No cathedral arches, no gothic spires, no flying buttresses, no skull motifs, no imperial eagles, no clean sci-fi glowing blue energy shields.
- **What IS present:** Heavy cast-iron cross-bracing, hydraulic pistons, exposed pneumatic lines, soot-stained exhaust towers, riveted box girders, analog floodlights, vertical freight lift counterweights.

### Gate 4: Varek Silhouette Read
- **Overhead Yoke:** Heavy roll-cage / tectonic load harness framing his head and traps.
- **Gren-Skildus (Left Shoulder):** Wide, handcrafted, curved ancestral plate.
- **Right Shoulder:** Functional industrial hydraulic linkage and mechanical hinge.
- **Lower Chassis:** Wide-stance legs, piston dampers, flared magnetic heelspikes locked to gantry deck.
- **Backpack:** Low-profile diesel/rebreather thermal unit with twin angled cooling exhausts.

### Gate 5: The Intimacy Rule
- Despite the 2km vertical cavern backdrop, the composition uses lighting contrast and perspective leading lines (gantry rail, light tower beam, gantry boom) to direct the viewer's eye straight to Varek's silhouette and the solitary human worker beside him.

---

## 3. Camera & Composition Setup

| Parameter | Value | Rationale |
| :--- | :--- | :--- |
| **Focal Length** | `24mm` (Full Frame 35mm equivalent) | Expands field of view, dramatizes vertical perspective |
| **Sensor Size** | `36mm x 20.25mm` (16:9 4K / UHD) | Standard cinematic wide sensor |
| **Camera Height** | `Z = 1.2m` (relative to gantry floor) | Lower than human eye-level; looks upward at Varek and ceiling |
| **Camera Angle** | Pitch `+14.0°`, Roll `0.0°` | Forces viewer gaze up the vertical light-tower shafts |
| **Framing Grid** | Rule of Thirds | Varek at right vertical third; Human worker at midground left third |
| **Depth of Field** | F/5.6, Focus locked on Varek | Sharp foreground-midground; atmospheric haze carries background depth |

---

## 4. Lighting Hierarchy & Volumetrics

1. **Layer 1: Deep Abyss Furnace Glow (Low Key)**
   - *Type:* Large Area / Ambient Bounce from lower shafts (`Z = -300m`).
   - *Color:* Deep Industrial Amber / Smoldering Orange (`#FF5500` / `2000K`).
   - *Intensity:* Low fill, illuminates underbellies of lower gantries and rising dust.

2. **Layer 2: Light-Tower Array (Mid-to-High Key Background)**
   - *Type:* Vertical column of instanced point/spot lights along cavern walls (`Z = +50m to +1500m`).
   - *Color:* Cold Industrial Sodium Vapor & Halogen White (`#E6F0FF` / `5500K`).
   - *Function:* Creates the "thousand vertical cities" look, punching volumetric rays through smog.

3. **Layer 3: Key Gantry Work Light**
   - *Type:* Overhead industrial floodlight mounted to gantry crane arm (`Z = +10m`).
   - *Color:* Harsh Warm White (`#FFF2DC` / `3800K`).
   - *Function:* Casts downward cone on the console area, defining the human worker's silhouette.

4. **Layer 4: Silhouette Rim Light**
   - *Type:* Distant high-intensity edge spot from across the cavern chasm.
   - *Color:* Cold Pale Steel (`#C8DCFF` / `6500K`).
   - *Function:* Catches the edge of Varek's left pauldron (*Gren-Skildus*), helmet visor rim, and overhead structural yoke.

---

## 5. Acceptance Criteria (QA Gate Checklist)

- [ ] **Clay Render Test (Workbench / Greybox):** With all textures disabled, does the frame immediately convey a gargantuan vertical mountain cavern with a massive armored protector?
- [ ] **Scale Ratio Verification:** Human head is ~1/3 the width of Varek's pauldron; gantry girder is 4x human height; cavern ceiling vanishes beyond camera frustum.
- [ ] **Silhouette Distinctiveness:** Can Varek's silhouette be instantly recognized purely by the overhead yoke, heavy pauldron, and hydraulic legs without looking like a generic space marine?
- [ ] **De-40K Confirmation:** Zero neo-gothic religious architecture; 100% brutalist tectonic mining and disaster-engineering infrastructure.
