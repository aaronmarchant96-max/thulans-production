# Simplified Varek v4 — articulation study

Source: `varek-simplified-donor-v3.blend`, SHA-256
`22801e4e4195948b916be146d445c61ab3f55e14b0a3c7a88eda2fec56b4398a`.
Source remains unchanged.

Candidate: `varek-simplified-rig-v4.blend`, SHA-256
`775960dd420ca8832964ef1f3d624ef1516e596375e77740f95da5232c6073a7`.

Three discrete review poses: frame 1 neutral, frame 30 raised arms,
frame 60 planted work. Constant key interpolation deliberately avoids claiming
that the transitions are validated animation. Actual Cycles renders accompany
the candidate; their hashes and sampled measurements are in `measurements.json`.

Rigid module binding preserves source mesh coordinates. The calf piston upper
socket was lowered on the calf, without changing cylinder lengths, to retain rod
overlap and accommodate the working pose. `failure.json` preserves the earlier
pre-correction piston-stroke failure; it is not the final candidate result.

Final sampled grounding, elbow-chain and piston-stroke checks pass. No surface
crossings were detected in the declared arm/yoke/torso and shin/thigh pairs.
This is not a full collision/containment test, continuous walk validation,
load simulation, or human visual approval.

Faírguni-Hamars remains parked on its own tool bone. The near-hand placement in
the working render is not a validated grip or hammer-swing interaction.

Human review pending. No canonical promotion. Existing unrelated audio, lore,
README and older production work were left untouched.
