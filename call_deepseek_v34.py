#!/usr/bin/env python3
"""
DeepSeek V34: High-End Industrial Bevel, Subdivision & Surface Curvature Overhaul.
Transforms Varek from boxy primitive look to heavy, authentic cinematic cast iron:
1. Adds automated weighted bevels (width=0.012 to 0.024, 4 segments) & Auto-Smooth (35°) to all rigid chassis components.
2. Fixes the brass materials (too shiny/plastic toy-like) -> deep aged bronze/tarnished industrial brass with proper micro-roughness.
3. Fixes charcoal iron -> deep forged manganese/anthracite steel with authentic edge highlight falloff.
4. Redesigns the Gren-Skildus canvas with multi-layered high-density drape cloth simulation/pydata folds instead of a flat extruded plane.
5. Softens harsh silhouette joints with mechanical fillets and cast welding beads.
"""
import json
import urllib.request

API_KEY = "sk-a870d707436547509e7beb65c09cc73b"
API_URL = "https://api.deepseek.com/v1/chat/completions"

SYSTEM_PROMPT = """You are a master 3D LookDev and Hard-Surface Modeler writing Blender Python (bpy) scripts for 'The Thulans' feature production.
Output ONLY executable Python code in a single ```python block.
The current model looks like a low-poly toy/Roblox asset because:
- Primitives have sharp un-beveled 90-degree polygonal edges.
- Flat shading or missing Weighted Normal / Bevel modifiers on hard surfaces.
- Materials lack proper metal micro-roughness (Aged brass looks like shiny toy gold, Iron looks like plastic matte black).
- Cloth (Gren-Skildus) is too rigid and blocky.

Your task is to write build_varek_v34_cinematic_polish.py to load varek-v33-canonical.blend, overhaul every object into high-end film-grade assets, and save as varek-v34-canonical.blend."""

USER_PROMPT = """Write build_varek_v34_cinematic_polish.py to execute the following comprehensive quality overhaul:

1. HARD-SURFACE SMOOTHING & CINEMATIC BEVELS:
   - Iterate over ALL mesh objects in the scene:
     - Set mesh shade smooth on all polygons (`poly.use_smooth = True` or `obj.data.shade_smooth()`).
     - Enable Auto Smooth (in Blender 4/5: add 'Weighted Normal' modifier with `keep_sharp=True` or `obj.data.use_auto_smooth = True` with angle 35-40 degrees).
     - Add a clean non-destructive 'Bevel' modifier to every hard-surface object (width=0.008 to 0.016, segments=3 or 4, limit_method='ANGLE', angle_limit=math.radians(30), profile=0.7). If a bevel modifier already exists, upgrade its segments to 4 and tune width so edges catch natural rim highlights.

2. MATERIAL LOOKDEV OVERHAUL (PHYSICAL METALLURGY):
   - 'Warm charcoal cast iron':
     - Base Color: Deep anthracite (0.04, 0.04, 0.045, 1.0)
     - Metallic: 0.95
     - Roughness: 0.38
     - Add subtle procedural Noise bump (scale 120, strength 0.04) for cast iron sand-cast pitting.
   - 'Aged brass' (currently looks like shiny toy gold, needs to look like oily heavy machinery brass):
     - Base Color: Dark tarnished bronze/brass (0.28, 0.19, 0.08, 1.0)
     - Metallic: 0.92
     - Roughness: 0.32 (not mirror-like)
     - Clearcoat/Specular tuned for greasy industrial sheen.
   - 'Cinderback jade paint' (Gren-Skildus):
     - Base Color: Deep desaturated moss/slate green (0.08, 0.14, 0.10, 1.0)
     - Metallic: 0.0
     - Roughness: 0.85
     - Sheen: 0.0 (no washed out velvet glow)

3. GREN-SKILDUS ORGANIC FABRIC RECONSTRUCTION:
   - High density organic cowl mesh with realistic natural fabric sag, multiple ripple folds, and weighted downward stretch.
   - 10 rows x 12 columns quad grid with procedural harmonic wave displacement (`sin(u*pi*4)*0.03 + sin(v*pi*3)*0.02 + cos((u+v)*pi*5)*0.015`).
   - Add Subdivision Surface (Level 2) and Solidify (0.016 thickness) for heavy canvas weight.

4. LIGHTING & CYCLES RENDER:
   - 128 samples Cycles render with denoising enabled.
   - Render Front 3/4 to `/home/aaron/animation/thulans-production/assets/art/varek_v34_front34_frame_001.png`
   - Render Side Profile to `/home/aaron/animation/thulans-production/assets/art/varek_v34_side_profile_frame_001.png`
   - Save to `/home/aaron/animation/thulans-production/blender/candidates/varek-v34-canonical.blend`
"""

payload = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT}
    ],
    "temperature": 0.15,
    "max_tokens": 4096
}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(
    API_URL,
    data=data,
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "User-Agent": "Blender-DeepSeek-Addon/1.0"
    }
)

with urllib.request.urlopen(req, timeout=60) as response:
    result = json.loads(response.read().decode('utf-8'))
    raw = result["choices"][0]["message"]["content"]

code = raw
if "```python" in code:
    code = code.split("```python")[1].split("```")[0].strip()
elif "```" in code:
    code = code.split("```")[1].split("```")[0].strip()

out_path = "/home/aaron/animation/thulans-production/build_varek_v34_master.py"
with open(out_path, "w") as f:
    f.write(code)

print(f"DeepSeek V34 script written to {out_path}")
