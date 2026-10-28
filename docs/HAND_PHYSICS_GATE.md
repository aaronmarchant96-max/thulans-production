# Varek hand/tool physical-plausibility gate

Authority: Aaron requested a functioning real-world-style mechanism before handoff (retaining v10's right-hand wrist-reversal as historical rejection evidence; RULING 023/024 canonicalized the maul grip to the left hand and the Faírg-Tygil to the right arm).
Scope: Left hand, wrist gimbal interface, Faírguni-Hamars grasp. No new suit redesign.

## Claim boundary

Required claim: under explicit physical assumptions, a connected, actuated hand
can admit the existing handle, close, retain the free hammer under gravity and
the declared movement, and release it without impossible geometry or hidden
support. This is **modeled physical plausibility**, not real-world certification.
Actual buildability, material fatigue and safe load ratings require engineering
review and physical tests beyond Blender. A pretty render is not this proof.

## Current disposition

`varek-hand-v10.blend`, SHA-256
`9bf78724a82a0573e0c816597ed278e7214975e3aebdb027de63aa7084df810d`:
**REJECTED FOR PHYSICAL HANDOFF**. Aaron rejected wrist orientation; fingers are
a fixed closed shape, and the hammer follows a keyed tool bone. Earlier narrow
kinematic/intersection passes remain historical measurements, not grip proof.

## Required sequence (stop at the first failed prerequisite)

1. **Anatomy and mechanism.** Declare the left-hand coordinate frame: proximal
   forearm, wrist centre, distal palm, palm normal, radial/thumb side. Show these
   on a neutral/open hand, not inferred from a flattering camera. Confirm correct
   handedness and palm attachment with Aaron. State wrist/finger/thumb axes,
   joint centres, travel limits and mechanical connections. The palm must extend
   from the wrist correctly; bending back through the forearm or flipping 180
   degrees for camera readability is not a correction. Every moving segment
   needs a supported joint and plausible actuation path; no disconnected rings.
2. **Acquisition and release path.** Begin genuinely open with the shaft outside
   the hand. Move through approach, seating, closure, opening and withdrawal.
   No assembling fingers around an already trapped shaft, teleportation, passing
   through the guard/collar, or scaling geometry to gain clearance. Check swept
   motion, not just selected endpoint poses. Track allowable joint travel.
3. **Contact and load path.** Show actual finger/palm/thumb contact surfaces and
   force direction. Distinguish friction grip from geometric support under a
   collar. Trace hammer -> contact -> digits/palm -> wrist -> forearm. An
   unconnected visual hinge, or a reference point coinciding with another point,
   supplies no load path. Reject penetration, unexplained gaps or unlimited
   joint force. Metal should not be visibly squashed to fake compression.
4. **Free-tool gravity test.** In a separate diagnostic copy, remove the tool's
   animation, parenting, bone deformation and hidden constraints that dictate
   its motion. Use a dynamic hammer with declared mass/inertia/centre of mass.
   It must stay held by finite-force finger contact, not a fixed hand/tool joint,
   disabled collisions, gravity cancellation or sleeping-body trick. A stationary
   supported forearm is allowed and must be declared. Kinematically driven
   fingers alone cannot prove a finite-force load capacity.
5. **Loaded motion and release.** Run the intended slow lift/hold/plant and a
   declared bounded disturbance. Measure slip, rotation, joint travel, contact
   penetration and actuator demand. Open the hand: the unsupported hammer must
   fall. Run a control with contact removed: it must also fall. A tool that stays
   suspended fails the test even if its beauty render looks correct.
6. **Numerical robustness.** Repeat with increased solver accuracy, conservative
   friction/load variants and checked collision proxies. No single convex hull
   may fill the open cavity of the hand. Record collision margin and its relation
   to real clearances. Show proxy/mesh comparison. A pass that disappears under
   reasonable solver changes is inconclusive, not a production pass.
7. **Frozen evidence, then human review.** Bind the exact design candidate,
   physics-test derivative, collision proxies, assumptions, simulator/version,
   scripts, logs and diagnostic video by hash. Recompute the measurements from
   the frozen test, not only the producer's in-memory state. Aaron judges the
   visible mechanism only after the tests pass. Visual rejection still blocks.

## Inputs that must exist before simulation

Declare units and scale; hammer mass, centre of mass and inertia with provenance;
material/contact friction range; finite grip/actuator limits; joint travel and
supports; gravity; movement duration and disturbance; permitted slip, angular
drift, penetration and closure gaps; numerical settings and repeatability bands.
These are currently **UNSET**, not measured facts. Choose and freeze a conservative
test envelope before running; never tune it after seeing a failure. Estimated
inputs must be labeled assumptions, not canon or real-world measured ratings.

## Enforcement and implementation status

`tools/check_hand_physics_preflight.py` is implemented and read-only. It inspects
the saved scene for independent digit motion, wrist limits, a physics world and
a free dynamic tool, and retains Aaron's v10 rejection. It exits nonzero on a
failed prerequisite. Passing it never authorizes handoff by itself.

The full acquisition/load/release simulation and an independent oracle for loaded
contact, slip, drift, and drop metrics are **not yet implemented**. The current
`tools/validate_hand_physics_results.py` checks only empty-hand diagnostic
telemetry; its results cannot establish a functioning grip or authorize handoff.
The legacy `tools/build_varek_physics_gate_v1.py` executes none of its advertised
assertions and now reports every layer as `UNIMPLEMENTED`, exits nonzero, and
keeps physical handoff blocked. Diagnostic evidence is allowed.

Technical references: Blender's [collision properties](https://docs.blender.org/manual/en/dev/physics/rigid_body/properties/collisions.html)
and [rigid-body constraints](https://docs.blender.org/manual/en/5.0/physics/rigid_body/constraints/introduction.html).
