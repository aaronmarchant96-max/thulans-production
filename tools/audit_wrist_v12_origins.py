"""STAGE -1A(c) — read-only probe of WHERE the V12 wrist deflection originates.

Measures each chain bone's world-space axis rotation (approx flexion angle about
the meaningful anatomical axis) across the 168 frozen frames, to determine
whether the reported 6.96-36.17 deg "wrist deflection" is actually produced by a
hand.R/local wrist DOF, by forearm rotation, or by upper-arm repositioning of
the whole arm (which would mean there is effectively no separately articulated
wrist joint observed in the keyed motion).
"""
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

R = Path('/home/aaron/animation/thulans-production')
P = R / 'blender/candidates/varek-articulated-grip-v12.blend'
bpy.ops.wm.open_mainfile(filepath=str(P))
scene = bpy.context.scene
rig = bpy.data.objects['Varek simple articulation']
pose = rig.pose.bones
arm = rig.data

def axis_world(name, fr):
    scene.frame_set(fr)
    b = arm.bones[name]
    h = pose[name].head
    t = pose[name].tail
    return (Vector(t) - Vector(h)).normalized()

# Reference: a steady vertical for comparison is not anatomical; we measure relative
# change vs frame 1 (neutral/open) per bone. Report per-bone total rotation angle
# from frame 1 pose, and the angulation between hand.R and its proximal forearm.
bones = ['hand.R', 'forearm.R', 'upper_arm.R']
origin = {nm: axis_world(nm, 1) for nm in bones}

# Rotational delta summary: for each bone, total angle its axis sweeps from frame 1.
def angle_between(a, b_):
    a = a.normalized(); b_ = b_.normalized()
    c = max(-1.0, min(1.0, a.dot(b_)))
    return round(math.degrees(math.acos(c)), 4)

rows = []
for fr in range(1, 169):
    cur = {nm: axis_world(nm, fr) for nm in bones}
    row = {'frame': fr}
    for nm in bones:
        row[nm + '_sweep_from_F1_deg'] = angle_between(origin[nm], cur[nm])
    # hand vs forearm angulation (carpal/flexion proxy) in this frame.
    row['hand_vs_forearm_deg'] = angle_between(cur['hand.R'], cur['forearm.R'])
    rows.append(row)

def span(key):
    vals = [r[key] for r in rows]
    return {'min': min(vals), 'max': max(vals), 'absmax': max(abs(v) for v in vals)}

summary = {f'{nm}_sweep': span(f'{nm}_sweep_from_F1_deg') for nm in bones}
summary['hand_vs_forearm'] = span('hand_vs_forearm_deg')

# Net: which parent bone carries the elbow/shoulder repositioning proxy.
report = {
    'candidate': P.name,
    'summary': summary,
}
print(json.dumps(report, indent=2, default=str))
sys.stdout.flush()
