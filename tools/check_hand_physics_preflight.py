"""Fail-closed prerequisites only. This does not execute or certify physics."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

REJECTED_WRIST_SHA = '9bf78724a82a0573e0c816597ed278e7214975e3aebdb027de63aa7084df810d'

def evaluate(snapshot):
    failures = []
    checks = {
        'independent_digit_motion_missing': snapshot.get('independent_digit_motion') is True,
        'wrist_travel_limits_missing': snapshot.get('wrist_travel_limits') is True,
        'physics_world_missing': snapshot.get('physics_world') is True,
        'free_dynamic_tool_missing': snapshot.get('free_dynamic_tool') is True,
        'gravity_disabled': snapshot.get('gravity_enabled') is True,
    }
    failures.extend(name for name, passed in checks.items() if not passed)
    if snapshot.get('candidate_sha256') == REJECTED_WRIST_SHA:
        failures.append('human_rejected_wrong_side_of_wrist')
    return {
        'gate': 'HAND_PHYSICS_PREFLIGHT',
        'claim_class': 'OBSERVED',
        'candidate_sha256': snapshot.get('candidate_sha256'),
        'result': 'FAIL' if failures else 'PREREQUISITES_ONLY_PASS',
        'failures': failures,
        'observations': snapshot,
        'physics_simulation_executed': False,
        'handoff_authorized': False,
        'remaining_gates': ['anatomy_and_mechanism_review', 'acquisition_and_release_path',
                            'finite_force_load_test', 'negative_controls',
                            'numerical_robustness', 'frozen_evidence_readback', 'human_approval'],
    }

def inspect_scene(bpy, digest):
    rig = bpy.data.objects.get('Varek simple articulation')
    if rig is None:
        raise RuntimeError('Expected Varek simple articulation rig missing')

    hand_objs = [
        o for o in bpy.data.objects
        if o.type == 'MESH' and any(
            k in o.name.lower() for k in ('hand', 'palm', 'digit', 'thumb', 'gimbal_yoke')
        )
    ]
    if not hand_objs:
        raise RuntimeError('Expected hand mesh components missing')

    used = sorted({
        o.vertex_groups[g.group].name
        for o in hand_objs
        for v in o.data.vertices
        for g in v.groups
        if g.weight > 0 and g.group < len(o.vertex_groups)
    })

    digit_bones = [
        b.name for b in rig.pose.bones
        if any(t in b.name.lower() for t in ('finger', 'thumb', 'digit'))
    ]

    digit_constraints = [
        o.name for o in bpy.data.objects
        if o.rigid_body_constraint
        and any(t in o.name.lower() for t in ('finger', 'thumb', 'digit'))
    ]

    wrist_limit_candidates = [
        'wrist_pitch.L', 'wrist_yaw.L', 'hand.L',
        'wrist_pitch.R', 'wrist_yaw.R', 'hand.R',
    ]
    wrist_limits = []
    for bname in wrist_limit_candidates:
        pb = rig.pose.bones.get(bname)
        if pb:
            for c in pb.constraints:
                if c.type == 'LIMIT_ROTATION' and not c.mute and (c.use_limit_x or c.use_limit_y or c.use_limit_z):
                    wrist_limits.append(f"{bname}:{c.name}")

    tool_parts = [
        o for o in bpy.data.objects
        if o.get('rigid_driver_bone') == 'tool' or ('maul' in o.name.lower() and o.type == 'MESH')
    ]

    dynamic = [
        o.name for o in tool_parts
        if o.rigid_body and o.rigid_body.type == 'ACTIVE'
        and not o.rigid_body.kinematic and not o.parent and not o.constraints
        and not o.animation_data and not any(m.type == 'ARMATURE' for m in o.modifiers)
    ]

    return {
        'candidate_sha256': digest, 'blender_version': bpy.app.version_string,
        'hand_weight_drivers': used, 'digit_bones': digit_bones,
        'digit_constraint_objects': digit_constraints, 'wrist_limit_constraints': wrist_limits,
        'tool_part_names': [o.name for o in tool_parts], 'free_dynamic_tool_parts': dynamic,
        # Conservative prerequisites, not a general mechanism detector/certificate.
        'independent_digit_motion': bool(digit_constraints or (digit_bones and len(used) > 1)),
        'wrist_travel_limits': bool(wrist_limits),
        'physics_world': bpy.context.scene.rigidbody_world is not None,
        'free_dynamic_tool': bool(dynamic),
        'gravity_enabled': bool(bpy.context.scene.use_gravity and bpy.context.scene.gravity.length > 0),
    }

def main():
    args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    a = parser.parse_args(args)
    if a.output.exists():
        raise RuntimeError('Preserve prior evidence: output already exists')
    digest = hashlib.sha256(a.candidate.read_bytes()).hexdigest()
    import bpy
    bpy.ops.wm.open_mainfile(filepath=str(a.candidate))
    report = evaluate(inspect_scene(bpy, digest))
    assert hashlib.sha256(a.candidate.read_bytes()).hexdigest() == digest
    report['candidate_unchanged'] = True
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'gate': report['gate'], 'result': report['result'],
                      'failures': report['failures'], 'handoff_authorized': False}), flush=True)
    if report['failures']:
        raise RuntimeError('HAND_PHYSICS_PREFLIGHT_FAIL — preserved candidate; handoff blocked')

if __name__ == '__main__':
    main()
