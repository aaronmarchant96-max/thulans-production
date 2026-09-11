#!/usr/bin/env python3
"""
Call DeepSeek API to generate bpy code for Varek V32 fixes, then write the result.
Addresses: side profile disconnections + Gren-Skildus cloth too small/blobby.
"""
import json
import urllib.request
import urllib.error
import sys

API_KEY = "sk-a870d707436547509e7beb65c09cc73b"
API_URL = "https://api.deepseek.com/v1/chat/completions"

SYSTEM_PROMPT = """You are an expert Blender Python (bpy) assistant for the Thulans animation production.
Output ONLY pure executable Python code inside a single ```python code block.
Always import bpy, math, and mathutils as needed.
The scene is Varek Fairgunjis — an 8-ft (2.4384m) heavy industrial rescue exoskeleton.
Armature name: 'Varek simple articulation'
Existing materials: 'Warm charcoal cast iron', 'Aged brass', 'Cinderback jade paint', 'M_Thulan_Insignia_BoneWhite', 'M_Dark_Winch_Cable', 'Amber visor', 'Oily joint steel'
The source blend is: /home/aaron/animation/thulans-production/blender/candidates/varek-v31-canonical.blend
Save output to: /home/aaron/animation/thulans-production/blender/candidates/varek-v32-canonical.blend
Write code that works in Blender 5.2 LTS."""

USER_PROMPT = """Load varek-v31-canonical.blend and produce varek-v32-canonical.blend with these specific fixes:

1. GREN-SKILDUS SHOULDER CLOAK (top priority):
   - The current 'Gren Skildus' object is too small — appears as a fist-sized blob.
   - Delete the existing 'Gren Skildus' object if it exists.
   - Create a large draped canvas cloak using pydata mesh (NOT a cylinder).
   - The cloak must: start at the left shoulder crest (X=+0.38, Z=1.85), drape down covering the entire left shoulder and upper arm, fall naturally to about hip level (Z=1.05) on the left side, have organic folds (use SubSurf modifier level 2 + Solidify thickness 0.03).
   - The canvas must be WIDE — at least 0.55 units across at the shoulder, flaring out at the bottom to 0.45 units.
   - Apply material 'Cinderback jade paint' to it.
   - Bind to 'upper_arm.L' bone of armature 'Varek simple articulation'.

2. SIDE PROFILE TORSO-PELVIS BRIDGE:
   - Add a thick structural spine column (cylinder, radius=0.055, depth=0.35) running from spine (Z=1.55) down to pelvis (Z=1.20), positioned at Y=-0.05 (rear-center).
   - Add two lateral flank panels (flat boxes, scale 0.18 x 0.04 x 0.28) on each side at X=±0.19, Z=1.35 bridging torso to pelvis.
   - Apply material 'Warm charcoal cast iron' to all.
   - Bind spine column to 'spine' bone, flank panels to 'pelvis' bone.

3. SIDE PROFILE SHOULDER-TORSO BRIDGE:
   - Add a yoke collar ring (torus, major_radius=0.22, minor_radius=0.035) centered at Z=1.82, connecting shoulder to upper torso.
   - Add a rear shoulder plate (box, scale 0.35 x 0.06 x 0.22) at Y=+0.08, Z=1.72 bridging the back of the shoulders.
   - Apply 'Warm charcoal cast iron' material.
   - Bind to 'spine' bone.

4. RENDER: After saving the blend, render two diagnostic frames (128 samples, Cycles):
   - Front 3/4 view: camera at (1.8, -2.2, 1.35), pointing at (0, 0, 1.2). Save to /home/aaron/animation/thulans-production/assets/art/varek_v32_front34_frame_001.png
   - Side profile view: camera at (2.8, 0.0, 1.25), pointing at (0, 0, 1.2). Save to /home/aaron/animation/thulans-production/assets/art/varek_v32_side_profile_frame_001.png
   - Resolution: 960x1280, PNG.

Use bind_to_bone helper:
def bind_to_bone(obj, bone_name):
    arm = bpy.data.objects.get('Varek simple articulation')
    if not arm: return
    vg = obj.vertex_groups.new(name=bone_name)
    vg.add(list(range(len(obj.data.vertices))), 1.0, 'REPLACE')
    mod = obj.modifiers.new('Armature', 'ARMATURE')
    mod.object = arm
"""

payload = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT}
    ],
    "temperature": 0.1,
    "max_tokens": 4096
}

print("Calling DeepSeek API for V32 bpy code...", flush=True)

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

try:
    with urllib.request.urlopen(req, timeout=60) as response:
        result = json.loads(response.read().decode('utf-8'))
        raw = result["choices"][0]["message"]["content"]
except Exception as e:
    print(f"API ERROR: {e}", file=sys.stderr)
    sys.exit(1)

# Extract python block
code = raw
if "```python" in code:
    code = code.split("```python")[1].split("```")[0].strip()
elif "```" in code:
    code = code.split("```")[1].split("```")[0].strip()

# Write the generated script
out_path = "/home/aaron/animation/thulans-production/build_varek_v32_deepseek.py"
with open(out_path, "w") as f:
    f.write(code)

print(f"DeepSeek generated script written to: {out_path}", flush=True)
print("--- PREVIEW (first 30 lines) ---", flush=True)
for i, line in enumerate(code.split("\n")[:30], 1):
    print(f"{i:3}: {line}", flush=True)
