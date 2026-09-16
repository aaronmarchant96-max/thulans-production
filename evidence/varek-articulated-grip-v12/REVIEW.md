# V12 — articulated hand / hammer motion diagnostic

Candidate SHA-256: `c420feaa0d01d0604ce466cc8fca8f7d032fe01f3c761083471484702fdc81ad`

Source v10 remains unchanged. Only the right hand, wrist coupling and two hand
guards were rebuilt; eleven digit bones were added. Original bone rest matrices,
other mesh geometry and material slots were preserved. No accepted source was
overwritten or promoted.

The right-hand anatomical frame is explicit: distal direction from wrist into
palm, radial/thumb side, and palmar normal. These form a left-handed coordinate
basis for the right hand. The earlier cross-product choice mirrored the hand;
that construction was stopped before saving a candidate. Finger orientations
also retain their shaft-parallel hinge axes rather than matching endpoints only.

Three independently articulated three-segment fingers oppose a two-segment
thumb. The animation approaches open, seats the palm, closes proximal-to-distal,
lifts, plants, opens in reverse order and withdraws. The hammer's geometry is
unchanged; its floor pose is yawed to clear the boot.

## Observed checks

- Producer: 168 integer frames; zero reported interface/tool surface-crossing
  frames. Soles remain at the floor and the hammer does not cross below it.
- Separate saved-file readback: joint continuity checked across 168 frames.
  Maximum sampled closed-pad/handle gap: 0.21243859373498708 mm, within the
  declared 0.75 mm diagnostic contact tolerance.
- Separate digit check: 55 nonadjacent group pairs over 168 frames; zero
  surface-crossing frames. Adjacent hinge/root seating is explicitly excluded.
  This uses conservative pre-bevel surfaces and is not a volume/force proof.
- Measured wrist/forearm deflection spans 6.962269233748342–36.170646448014864°.
- Aaron responded “yes great” after the closed-contact still was opened.
  This is positive feedback on that image, not approval of unshown motion or
  a completed physical-plausibility gate.

## Still blocked

`physics-preflight.json` correctly reports missing enforced wrist travel limits,
physics world and free dynamic tool. The hammer is controlled by a keyed tool
bone. No finite-force retention, disturbance, negative-control or numerical
robustness test has passed. **Physical handoff is not authorized.**

The Cycles animation previews sample the frozen 24-fps action at 8 fps. Encoding
to 24 fps repeats frames; it does not generate or validate extra motion samples.
The original reverse camera was obstructed by the torso; retain that failed
diagnostic, and use `wrist-outboard.png` / `open-outboard.png` for the readable
second angle. No geometry was hidden or saved differently for these stills.
