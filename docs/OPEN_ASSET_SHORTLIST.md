# Open Asset Shortlist

Checked on 2026-09-06 for parts that may accelerate later Varek and environment
look-development. Nothing listed here is imported into Motion Chassis V1; the greybox
must prove silhouette and articulation without inheriting another model's design.

## Cleared sources

| Source | Candidate use | License | Import state |
| --- | --- | --- | --- |
| [Poly Haven: Modular Industrial Pipes 01](https://polyhaven.com/a/modular_industrial_pipes_01) | hydraulic lines, flanges, valve and gauge forms | CC0 | not downloaded |
| [Poly Haven: Modular Pipes](https://polyhaven.com/a/modular_pipes) | later powerplant and environment pipe kit | CC0 | not downloaded |
| [Poly Haven: Modular Airduct Circular 01](https://polyhaven.com/a/modular_airduct_circular_01) | radiator and ventilation vocabulary | CC0 | not downloaded |
| [Kenney: Factory Kit](https://kenney.nl/assets/factory-kit) | low-detail factory fixtures and conveyor/environment blockout | CC0 | not downloaded |
| [Kenney: City Kit (Industrial)](https://kenney.nl/assets/city-kit-industrial) | distant industrial city and infrastructure blockout | CC0 | not downloaded |
| [ambientCG](https://ambientcg.com/) | later iron, painted metal, rubber, grime and floor materials | CC0 | not downloaded |

Poly Haven's site-wide asset terms explicitly place its HDRIs, textures, and models
under CC0. The two Kenney asset pages explicitly identify their downloads as CC0.
ambientCG publishes its assets under CC0. Each eventual download still requires its own
source URL, asset name/version, license snapshot, file hash, and import manifest entry.

## Usage ruling

- Prefer CC0 assets for redistributable production files.
- Do not import marketplace, Sketchfab, BlenderKit, GrabCAD, generated-model, or
  unknown-source files merely because they are downloadable.
- CC-BY assets require a deliberate attribution record before import.
- Reference images are not model-import authorization.
- Reusable parts may supply hoses, valves, fasteners, vents, gauges, and environment
  fixtures. They may not determine Varek's primary silhouette, operator cell, load
  path, Gren-Skildus, manipulator design, or anchor architecture.
- Every imported asset must be copied into a controlled source-assets directory and
  bound by SHA-256 before it enters a candidate blend.

## V1 decision

Motion Chassis V1 uses only deterministic Blender primitives. This keeps the silhouette
test original, light, reproducible, and independent of external downloads. The cleared
shortlist becomes useful after the chassis and articulation gates pass.
