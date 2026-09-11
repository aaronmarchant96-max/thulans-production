"""STAGE -1A(b) — read-only hand.R pose parameterization probe (no writes).

Determines how hand.R is actually rotated across the frozen V12 keyed motion:
which local axis is swept, whether it is a single-axis sweep, what the neutral
frame pose is, and whether any modal constraint / keying drives it. Also records
rest-frame transforms of hand.R / forearm.R / Wrist coupling R object.
"""
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector, Euler

R = Path('/home/aaron/animation/thulans-production')
P = R / 'blender/candidates/varek-articulated-grip-v12.blend'
bpy.ops.wm.open_mainfile(filepath=str(P))
scene = bpy.context.scene
rig = bpy.data.objects['Varek simple articulation']
pose = rig.pose.bones

def v3(v): return [round(float(c), 6) for c in v]

arm = rig.data
coupler = bpy.data.objects.get('Wrist coupling R')

# Bone rest transforms (head/tail in world) + 3x3 rest matrices.
def bone_rest(nm):
    b = arm.bones[nm]
    return {
        'bone': nm,
        'head_world': v3(rig.matrix_world @ b.head_local),
        'tail_world': v3(rig.matrix_world @ b.tail_local),
        'rest_rot_matrix': [[round(float(c), 5) for c in row]
                            for row in b.matrix_local.to_3x3().transposed()],
    }

fb = arm.bones['forearm.R']
hb_ = arm.bones['hand.R']
X_fore = (fb.tail_local - fb.head_local).normalized()
X_hand = (hb_.tail_local - hb_.head_local).normalized()
M_f = fb.matrix_local.to_3x3().normalized()
M_h = hb_.matrix_local.to_3x3().normalized()
rel = M_f.inverted() @ M_h
eul = rel.to_euler('XYZ')
print('REST_REL_EULER_DEG', [round(math.degrees(x), 4) for x in eul])

# Sweep: sample hand.R pose rotation over the frozen 168-frame motion.
frame_start = int(max(scene.frame_start, 1))
frame_end = int(min(scene.frame_end, 168))
rows = []
for fr in range(frame_start, frame_end + 1):
    scene.frame_set(fr)
    e = Euler(pose['hand.R'].rotation_euler).copy()
    rows.append({'frame': fr,
                 'euler_deg': [round(math.degrees(e.x), 5),
                               round(math.degrees(e.y), 5),
                               round(math.degrees(e.z), 5)]})

stats = {}
for i, ax in enumerate(['x', 'y', 'z']):
    vals = [r['euler_deg'][i] for r in rows]
    stats[ax] = {'min': round(min(vals), 5), 'max': round(max(vals), 5),
                 'span': round(max(vals) - min(vals), 5)}
dom = max(stats, key=lambda ax: stats[ax]['span'])

# Wrist coupling R object metadata.
c_info = None
if coupler is not None:
    bb = coupler.bound_box
    c_info = {
        'name': coupler.name,
        'type': coupler.type,
        'vertex_count': len(coupler.data.vertices) if coupler.type == 'MESH' else None,
        'vertex_polygon_count': len(coupler.data.polygons) if coupler.type == 'MESH' else None,
        'parent': coupler.parent.name if coupler.parent else None,
        'location': v3(coupler.location),
        'bound_local_min': [min(p[i] for p in bb) for i in range(3)],
        'bound_local_max': [max(p[i] for p in bb) for i in range(3)],
        'matrix_world': [[round(float(c), 4) for c in row] for row in coupler.matrix_world],
        'collection_labels': [c.name for c in coupler.users_collection],
    }
else:
    c_info = None

all_digits = [b.name for b in rig.data.bones
              if b.name.lower().startswith(('finger.', 'thumb.'))]

report = {
    'candidate': P.name,
    'blender': bpy.app.version_string,
    'forearm_rest': bone_rest('forearm.R'),
    'hand_rest': bone_rest('hand.R'),
    'rest_rel_euler_xyz_deg': [round(math.degrees(x), 4) for x in eul],
    'sweep_axis_stats': stats,
    'dominant_sweep_axis': dom,
    'sample_frame_count': len(rows),
    'frame_to_euler_first': rows[0] if rows else None,
    'frame_to_euler_last': rows[-1] if rows else None,
    'wrist_coupling': c_info,
    'digit_root_bone_count': len(all_digits),
    'digit_roots_sample': all_digits[:14],
}
print(json.dumps(report, indent=2, default=str))
sys.stdout.flush()
