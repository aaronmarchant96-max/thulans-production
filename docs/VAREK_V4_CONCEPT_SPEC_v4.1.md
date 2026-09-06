# BROTHAR VAREK FAIRGUNJIS — V4.1 VISUAL CONCEPT CONTRACT

**Status:** HUMAN APPROVED — SILHOUETTE LOCKED  
**Blender:** PLANNING AUTHORIZED; EXECUTION BLOCKED PENDING PLAN QA  
**Shot 01:** BLOCKED

## Design claim

Varek must read as a purpose-built industrial rescue and load-bearing machine
containing a mortal person—not as conventional power armor carrying mining props.

Visual hierarchy:

> Rescue engine first. Human prison second. Ancient guardian third. Warrior last.

Target read: approximately 90% industrial machine / 10% protective power equipment.

## Dimensional authority

The assembled rig height is locked at exactly **2.4384 m (8 ft)** from ground contact
to the apex of the overhead yoke. Varek has an approximately **three-tonne presence**.

All other pre-chassis dimensions are visual targets only. Eye height, shoulder span,
yoke clearance, cylinder diameter, frame thickness, pilot envelope, mass breakdown,
joint locations, pressure, stroke, thermal output, impact energy, and load rating must
be measured or calculated from the approved visual chassis. They are not canon yet.

## Four-view sheet

The required sheet contains matching neutral-pose front, rear, character-left, and
character-right orthographic views plus a neutral human-envelope inset.

- **Front:** pilot centerline, thoracic load cage, asymmetric Gren-Skildus, pelvic
  load junction, leg columns, and broad ground interface.
- **Rear:** integrated powerplant acting as the structural spine; powerplant must not
  read as removable luggage.
- **Character-left:** Gren-Skildus depth, yoke clearance, head protection, and pilot
  placement.
- **Character-right:** exposed industrial tool station, guarded Thermal Vein Cutter,
  and working hydraulics.
- **Human envelope:** head, shoulders, pelvis, elbows, knees, and feet aligned inside
  the machinery without anatomical impossibility.

Only the overall **2.4384 m** height may be numerically labeled. Relationship labels
may identify `PRIMARY LOAD PATH`, `PILOT ENVELOPE`, `POWERPLANT / SPINAL STRUCTURE`,
`ANCESTRAL LOAD PLATE`, `TOOL INTERFACE`, and `ANCHOR ASSEMBLY`.

## Dominant structural load path

The dominant structural load bypasses the pilot through the external frame:

```text
overhead yoke
  -> shoulder and thoracic rails
  -> integrated dorsal powerplant/spinal structure
  -> pelvic load junction
  -> femur and shin struts
  -> configurable anchor assemblies
  -> substrate
```

The pilot remains exposed to vibration, acceleration, heat, pressure change, and
residual structural loading. The machine can remain operational after his body begins
to fail.

## Required primary forms

- Open, braced thoracic load cage around a sealed protective human hull.
- Heavy vertical members visibly joining yoke, pelvis, legs, and ground.
- Integrated low-revving diesel-hydraulic powerplant forming part of the dorsal frame:
  opposed-piston visual language, hydraulic pump, accumulators, governor, radiators,
  service access, emergency pressure reserve, and soot-controlled exhaust.
- Character-left Gren-Skildus ancestral load plate: battered Cinderback jade, mortal-
  made, repaired, and visually distinct from the machine.
- Character-right industrial tool station with guarded electric thermal shear.
- Fault Maul as a variable-output structural driver/pile-driver, never a firearm.
- Hydraulic rescue hands that remain capable of careful human extraction.

## Anchor State architecture

- **Rock — Driven Pin Mode:** retractable drilling/pinning assemblies engage fractured
  stone or prepared anchor points.
- **Structural Metal — Clamp Mode:** magnetic assistance plus mechanical cleats or jaws
  grip compatible plates, rails, grating, or flanges.
- **Debris / Unknown — Outrigger Mode:** widened feet, friction teeth, and splayed
  stabilizers increase area and resist sliding.

No single mechanism is claimed to penetrate every substrate.

## Vocabulary contract

| Retire | Use |
| --- | --- |
| pauldron | Gren-Skildus ancestral load plate |
| backpack | integrated diesel-hydraulic powerplant |
| armor frame | external structural frame |
| armor plating | protective hull / protective plate |
| weapon mount | industrial tool station |
| armored torso | thoracic load cage / protective human hull |

## Visual rejection rules

Reject the sheet if any of these are true:

- silhouette reads primarily as a soldier, Space Marine, fantasy dwarf, or cockpit mech;
- torso resembles muscular breastplate anatomy;
- powerplant reads as a strapped-on box;
- load path cannot be traced visually from yoke to ground;
- pilot anatomy cannot fit inside the machine;
- industrial tool reads as a gun;
- heel anchors read as fantasy claws;
- decorative components enter the silhouette without load, rescue, survival, or
  service function.

## Gate state

```yaml
overall_height_2_4384_m: LOCKED
approximate_three_tonne_presence: LOCKED
load_path_architecture: APPROVED_IN_PRINCIPLE
four_view_visual_sheet: APPROVED
human_placement: VISUALLY_ESTABLISHED_NOT_MEASURED
silhouette: LOCKED
engineering_dimensions: UNMEASURED
blender_chassis: PLANNING_AUTHORIZED_EXECUTION_BLOCKED
shot_01: REJECTED_DO_NOT_RUN
git_provenance: NOT_ESTABLISHED
```

Aaron approved the bounded-refinement sheet on 2026-09-06 with the explicit response
“1000%.” Approval is bound to the exact image hash in
`evidence/concepts/varek-v4-silhouette-approval.json`. This authorizes provenance setup
and motion-chassis planning, but not Blender execution.

## Bounded refinement before silhouette lock

The approved architecture must not be redesigned. One visual refinement may change
only these areas:

1. Replace humanoid/mecha gloves with precision industrial manipulators capable of
   both heavy gripping and careful casualty extraction.
2. Reframe the small human head as a protected mining-rescue operator cell nested
   beneath the load yoke, without enlarging it or introducing warrior-helmet anatomy.
3. Preserve the Gren-Skildus shape, location, and Cinderback jade identity while
   removing unapproved pseudo-script and adding handmade irregularity, old welds,
   mismatched repair rivets, layered paint, heat discoloration, and one repaired crack.

All other primary forms, load paths, powerplant architecture, anchors, tools, height,
palette, views, and human-envelope logic are frozen for this refinement.
