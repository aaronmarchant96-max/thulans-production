# THULAN PRODUCTION — 3D & ANIMATIC TECHNICAL SPEC (TECH_SPEC.md)

---
status: active-production-standard
scope: Blender 4.2+ / EEVEE Next / Camera & FX Pipeline
owner: Aaron Marchant
date: 2026-09-06
---

## 1. Megalithic Cavern Instancing (The 35s Teaser Hook Shot)
* **Objective:** Render thousands of vertical residential/mining lights across the hollow mountain walls with near-zero viewport lag and instant render times.
* **Technique:**
  * **Geometry Nodes / Particle Instancing:** Model a single modular 3-tier "Scaffold & Filament Lamp" asset.
  * Scatter across the procedural cavern surface normals using Geometry Nodes with a random rotation seed and subtle flicker frequency.
  * **Volumetric Atmosphere:** Use a single scene-wide World Volume Scatter shader (`Density: 0.015–0.025`, `Anisotropy: 0.6–0.75`) to capture light cones from the lamps and orange blast-furnaces.
  * **Engine:** EEVEE Next (Blender 4.2+) with Raytracing enabled for instant ambient occlusion and volumetric lighting.

---

## 2. Transient Waveform Audio Sync Workflow
* **Objective:** Lock all camera cuts, focal zooms, and mechanical impacts directly to the musical rhythm.
* **Technique:**
  * Import `Green Metal Heelspikes.mp3` directly into the Blender Video Sequencer (VSE) and enable `Show Waveform`.
  * **Transient Snapping:** Align major keyframes to specific audio markers:
    * *Anvil Clangs:* Hard camera cuts or rapid focal length shifts.
    * *Heel-Spike Deploy (0:18):* Mechanical pneumatic piston drop and floor dust burst.
    * *Climax Vocal Roar (“SO ENDURE ME!”):* Frame freeze, screen-shake trigger, and shockwave displacement.

---

## 3. Anchor State Optimization (Strain vs. Heavy Simulation)
* **Objective:** Communicate millions of tons of tectonic collapse force without expensive rigid-body physics sims.
* **Technique:**
  * **Foreground Sim Only:** Rigid-body physics / fractured mesh simulation limited strictly to the 4–6 small debris chunks interacting directly with Varek's shoulders and gauntlets.
  * **Background Depth:** Static high-res displacement mountain geometry layered behind dense particle dust emitters.
  * **The Physical Strain:** Subtle 2-frame micro-jitter on Varek's torso bone (`Noise Modifier` on F-curve) to simulate hydraulic pistons fighting against overwhelming structural load.

---

## 4. The Climax "Impact Freeze" Trick
* **Objective:** Deliver maximum cinematic weight when Varek catches the falling ceiling.
* **Technique:**
  * **The Deceleration Illusion:** The overhead slab drops rapidly for 4 frames, then **abruptly freezes on contact** with Varek's raised hands.
  * **Camera Impulse:** 3-frame vertical camera kick (`Z-offset: -0.08m` to `+0.04m` with exponential decay).
  * **Shockwave FX:** Radial displacement ripple modifier on the foreground dust particles and an optical glow flare on the *Gren-Skildus* weld seams.
  * **Audio Payoff:** The visual freeze-frame perfectly lands on the anvil strike and the vocal explosion: ***“SO ENDURE ME!”***
