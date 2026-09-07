---
status: LOCKED
authority: RULINGS.md#ruling-012-blender-shading-and-render-authority
applies_to: thulans-production
---

# Blender Render Pipeline

## Tier 1 — Workbench MatCap Clay

Use for fast geometry decisions:

- silhouette and proportion;
- surface continuity and manufactured form;
- articulation and rigid-part clearance;
- pose readability and load-path visibility.

Workbench evidence cannot approve materials, reflections, volumetrics, or final
lighting.

## Tier 2 — Cycles Diagnostic

Use one frame at 128 samples for material and lighting approval:

- true contact and self-shadowing between mechanical assemblies;
- cast iron, steel, grease, paint, rubber, and Gren-Skildus separation;
- roughness falloff and reflected-light behavior;
- smoke, dust, furnace bounce, and volumetric shafts.

The evidence record must capture render engine, sample count, denoising state, device,
Blender version, scene hash, camera, frame, color management, resolution, and output
hash. Device and denoising are measured settings, not assumed defaults.

## Tier 3 — Cycles Final

Render approved sequences as numbered lossless PNG frames. Preserve the frames as the
render master. Encode H.264 MP4 files only as review or delivery derivatives through
FFmpeg, with the exact input frame range, frame rate, command, and output hash recorded.

Final sample count, bounce limits, denoising, and render device remain shot-specific
until measured quality/time tests establish them. Diagnostic `128 samples` must not be
silently promoted into a universal final-pass setting.

## Headless command shape

```bash
flatpak run org.blender.Blender \
  --background /absolute/path/to/scene.blend \
  --python-exit-code 1 \
  --python /absolute/path/to/render_script.py
```

Always use absolute host-visible paths with Flatpak. A command exit code and the output
artifact hash must both pass before a render is reported successful.

## Prohibited evidence shortcuts

- EEVEE renders presented as final visual evidence;
- MP4-only masters;
- material approval from Workbench clay;
- geometry approval hidden beneath final materials;
- claims about Cycles settings that were not read from the rendered scene;
- successful-render claims based only on Blender launching or exiting `0` without the
  required artifact.
