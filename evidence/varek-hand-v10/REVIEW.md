# Right-hand interface v10 — human review pending

Frozen candidate: `varek-hand-v10.blend`
SHA-256: `9bf78724a82a0573e0c816597ed278e7214975e3aebdb027de63aa7084df810d`.

Rebuilt only the right forearm housing, wrist coupling, hand, dorsal guard and
knuckle rail. Right-arm pose keys were adjusted to present the grip clearly;
hammer motion and geometry were retained. The old busy assembly remains in v9.

The three fingers, opposed thumb and curved palm now enclose the existing haft.
The forearm terminates before a compact wrist bearing. This is a fixed closed
grip, not a finger-opening rig or proof of physical load capacity.

Producer: `tools/rebuild_varek_hand_v10.py`.
Saved-file check: `tools/check_varek_hand_v10.py`.
The independent readback confirms unchanged out-of-scope mesh geometry/material
slots and rest bones, correct rigid weights, and no selected right-interface
surface crossings against the hammer at frames 1, 36 and 64.
The producer also checks reference grip alignment at 72 integer frames.
These checks do not constitute full suit or continuous collision certification.

Actual Cycles views: `full.png`, `grip-detail.png`, `wrist-side.png`.
The candidate was saved before review-camera edits; its bytes remain frozen.
No canonical promotion, visual approval, or unrelated worktree commit performed.
