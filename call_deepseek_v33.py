#!/usr/bin/env python3
"""
DeepSeek V33 Model Architecture & Feel Script
Calls DeepSeek API to construct V33 addressing:
1. Gren-Skildus authentic drape: wrapping across shoulder, front chest fold, natural thickness, Thulan cross insignia properly positioned on front face.
2. Complete side-profile torso-pelvis structural bridges (rib cage, hydraulic spine, flank gussets).
3. Armature bone binding & clean render diagnostics.
"""
import json
import urllib.request
import sys

API_KEY = "sk-a870d707436547509e7beb65c09cc73b"
API_URL = "https://api.deepseek.com/v1/chat/completions"

SYSTEM_PROMPT = """You are an expert Blender Python (bpy) assistant for 'The Thulans' production.
Output ONLY pure executable Python code inside a single ```python code block.
Import bpy, math, mathutils (Euler, Vector, Quaternion).
The model is Brothar Varek Fairgunjis (2.4384m tall industrial rescue frame).
Armature: 'Varek simple articulation'.
Key materials in scene: 'Warm charcoal cast iron', 'Aged brass', 'Cinderback jade paint', 'M_Thulan_Insignia_BoneWhite', 'Amber visor'.
Source blend: /home/aaron/animation/thulans-production/blender/candidates/varek-v31-canonical.blend
Target blend: /home/aaron/animation/thulans-production/blender/candidates/varek-v33-canonical.blend
Ensure compatibility with Blender 5.2 LTS."""

USER_PROMPT = """Create build_varek_v33_master.py that loads varek-v31-canonical.blend, implements the canonical fixes, and outputs varek-v33-canonical.blend:

1. PURGE & RECONSTRUCT GREN-SKILDUS CLOAK:
   - Remove existing 'Gren Skildus' and any loose 'Thulan_Cross_' objects.
   - Build a 3D curved wrap-around shoulder canvas mesh from pydata.
   - The cloak must wrap over the top shoulder (X: 0.40 to 0.65, Y: -0.22 to +0.22, Z: 1.88 down to 1.30).
   - In front view (Y < 0), it extends from chest (X: 0.38) outward past shoulder (X: 0.64) down to mid-arm (Z: 1.30).
   - In side view, it wraps around the shoulder joint smoothly with a convex front curve and draping back fold.
   - Mesh: define a quad grid (approx 5x4 quads) with natural folds, add Solidify modifier (thickness=0.018), and Subsurf modifier (levels=2).
   - Material: 'Cinderback jade paint'.
   - Bind to 'upper_arm.L' bone.
   - Add the Thulan Double-Cross insignia on the front-facing lower section of the cloak (mesh object 'Thulan_Cross_Insignia', material 'M_Thulan_Insignia_BoneWhite', bind to 'upper_arm.L').
   - Keep or position the Bronze Brooch pin at the shoulder crest (X=0.52, Y=-0.02, Z=1.86).

2. SIDE PROFILE SOLID CONNECTIONS (Torso to Pelvis & Spine):
   - Add heavy Thoracic Rib Cage Gussets on left and right flanks bridging Torso (Z=1.60) to Pelvis (Z=1.20).
   - Add Dual Heavy Hydraulic Spine Actuators along the rear back column (radius 0.04, length 0.38, running from upper back Z=1.65 down to pelvic clevis Z=1.25 at Y=-0.12).
   - Add Pelvic-to-Torso Structural Locking Plates (thick beveled box geometry) filling the hollow gap between upper hull and pelvis.
   - Material for structural frame: 'Warm charcoal cast iron'.
   - Hydraulic rods/fittings: 'Aged brass'.
   - Correctly bind torso parts to 'spine' bone and lower parts to 'pelvis' bone.

3. RENDER DIAGNOSTICS:
   - Setup Cycles render (128 samples).
   - Render Front 3/4 view to /home/aaron/animation/thulans-production/assets/art/varek_v33_front34_frame_001.png
   - Render Side profile view to /home/aaron/animation/thulans-production/assets/art/varek_v33_side_profile_frame_001.png
   - Save blend file to /home/aaron/animation/thulans-production/blender/candidates/varek-v33-canonical.blend
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

out_path = "/home/aaron/animation/thulans-production/build_varek_v33_master.py"
with open(out_path, "w") as f:
    f.write(code)

print(f"DeepSeek V33 script written to {out_path}")
