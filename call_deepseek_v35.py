#!/usr/bin/env python3
"""
DeepSeek V35 Blast-Helmet Cinematic Redesign:
Replaces the blocky stepped primitives with a cast-iron industrial blast helmet:
- Heavy forged dome with beveled brow crest and reinforced cheek bulwarks
- Recessed narrow armored quartz visor slit (glowing amber with internal glass refraction)
- Twin heavy sulfur respirator filter canisters with intake grilles and ribbed intake hoses
- Mechanical neck articulation pivot and collar seals
- Cast iron texture with micro-beveled chamfers catching rim lighting
"""
import json
import urllib.request

API_KEY = "sk-a870d707436547509e7beb65c09cc73b"
API_URL = "https://api.deepseek.com/v1/chat/completions"

SYSTEM_PROMPT = """You are a senior 3D Hard-Surface Model & LookDev artist writing Blender Python (bpy) scripts for 'The Thulans' production.
Output ONLY executable Python code in a single ```python block.
The goal is to replace Varek's current blocky/Roblox-like stepped cube head with a high-detail cinematic Cast Iron Blast Helmet.
Lore specs:
- Narrow armored quartz slit with amber illumination.
- Heavy dual sulfur respirators on jaw flanks with intake grilles.
- Forged cast iron brow guard, angled cheek plates, and neck gimbal joint.
- Bound to armature 'Varek simple articulation' -> bone 'head'.
- Materials: 'Warm charcoal cast iron', 'Aged brass', 'Amber visor', 'Oily joint steel'."""

USER_PROMPT = """Write build_varek_v35_blast_helmet.py to load varek-v34-canonical.blend (or varek-v33-canonical.blend), overhaul the head, save to varek-v35-canonical.blend, and render:

1. PURGE OLD HEAD PRIMITIVES:
   - Identify and remove all old head/helmet sub-objects (e.g., Head, Visor, Chin, Neck blocks).

2. CONSTRUCT CANONICAL BLAST HELMET:
   - A. Main Cranial Dome & Brow Guard:
     - Forged faceted dome (pydata or beveled cylinder/cube) with sloped forehead (Z=1.92 to 2.18, Y=-0.16 to 0.16, X=-0.16 to 0.16).
     - Overhanging armored brow visor crest protecting the viewport.
     - Chamfered cheek cowl plates tapering down toward the jaw.
     - Add Bevel (4 segments, 0.008 width) and Subdivision modifiers.
     - Material: 'Warm charcoal cast iron'.
   - B. Armored Quartz Visor Slit:
     - Deeply recessed horizontal slit (width=0.18, height=0.035, depth=0.04) positioned at (0, -0.15, 2.02).
     - Material: 'Amber visor' with high emission and internal depth.
   - C. Dual Sulfur Respirator Filter Pods:
     - Cylindrical ribbed canister filter pods on left and right jaw flanks (at X=±0.13, Y=-0.10, Z=1.94, angled 35° outward).
     - Brass intake mesh caps and grooved pressure valves.
     - Materials: Canister body = 'Warm charcoal cast iron', Intake rings/caps = 'Aged brass'.
   - D. Reinforced Throat & Neck Gimbal:
     - Heavy segmented steel neck ring (radius 0.11, depth 0.10, Z=1.86).
     - Material: 'Oily joint steel'.

3. RIGGING / ARMATURE BINDING:
   - All helmet components must be bound cleanly to bone 'head' on armature 'Varek simple articulation'.

4. DIAGNOSTIC RENDERING:
   - Cycles 128 samples, Denoising enabled.
   - Close-up Front 3/4 beauty shot of the helmet & torso.
   - Save render to /home/aaron/animation/thulans-production/assets/art/varek_v35_head_closeup_frame_001.png
   - Save full front to /home/aaron/animation/thulans-production/assets/art/varek_v35_front34_frame_001.png
   - Save blend to /home/aaron/animation/thulans-production/blender/candidates/varek-v35-canonical.blend
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

out_path = "/home/aaron/animation/thulans-production/build_varek_v35_helmet_master.py"
with open(out_path, "w") as f:
    f.write(code)

print(f"DeepSeek V35 Helmet Script written to {out_path}")
