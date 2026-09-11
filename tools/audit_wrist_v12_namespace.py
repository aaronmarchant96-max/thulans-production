"""STAGE -1A(a) — read-only V12 wrist namespace inventory (no writes).

Lists the pose-bone armature chain from upperarm/forearm through hand.R and the
wrist-adjacent mesh objects, so the intended wrist hardware can be measured by
name instead of guessed.
"""
import json
import sys
from pathlib import Path
import bpy

R = Path('/home/aaron/animation/thulans-production')
P = R / 'blender/candidates/varek-articulated-grip-v12.blend'
assert P.exists()

bpy.ops.wm.open_mainfile(filepath=str(P))
scene = bpy.context.scene
rig = bpy.data.objects.get('Varek simple articulation')
hand = bpy.data.objects.get('Donor rescue hand R')
assert rig is not None and hand is not None, 'expected rig/hand by bound names'

# Armature chain of interest: find hand.R and walk parents to the forearm/arm.
pose = rig.pose.bones
bone_chain = []
def parent_walk(name):
    cur = pose.get(name)
    chain = []
    while cur is not None:
        chain.append(cur.name)
        cur = cur.parent
    return chain

# Build a small id map incl. pose channels (rotation constraints/locks).
all_pose = pose.keys()

# Get bone rest info for hand.R and its immediate chain ancestor bones.
def bone_info(nm):
    b = rig.data.bones.get(nm)
    if b is None:
        return None
    ch = pose.get(nm)
    return {
        'name': nm,
        'parent': b.parent.name if b.parent else None,
        'head': [round(v, 6) for v in b.head_local],
        'tail': [round(v, 6) for v in b.tail_local],
        'length_m': round(b.length, 6),
        'lock_rot': [bool(x) for x in ch.lock_rotation],
        'lock_rot_w': ch.lock_rotation_w,
        'use_custom_order': ch.rotation_mode != 'QUATERNION',
    }

# Figure which chain owns the right wrist. hand.R + a couple parents.
anc = parent_walk('hand.R')

# Collect wrist-candidate meshes: any object whose name contains 'wrist','coupler','coupling'.
ALL_MESHES = [o.name for o in bpy.data.objects if o.type == 'MESH']
wrist_objs = [o for o in ALL_MESHES
              if any(k in o.lower() for k in ('wrist', 'coupl', 'bearing', 'gaunt'))]

# Also nearby in a likely Varek_Editable_Parts collection.
collections = [c.name for c in bpy.data.collections]
part_col = bpy.data.collections.get('Varek_Editable_Parts')

report = {
    'claim_class': 'OBSERVED',
    'candidate': str(P),
    'candidate_basename': P.name,
    'blender_version': bpy.app.version_string,
    'rig_name': rig.name,
    'hand_mesh_name': hand.name,
    'hand_to_root_chain': anc,
    'full_pose_bone_count': len(all_pose),
    'hand_bone_info': bone_info('hand.R'),
    'chain_bone_info': {nm: bone_info(nm) for nm in anc},
    'wrist_adjacent_mesh_objects': wrist_objs,
    'editable_parts_collection_exists': part_col is not None,
    'editable_parts_member_count': len(part_col.objects) if part_col else None,
}

# Pose constraint listing for the direct chain bones of interest.
constraints = {}
for nm in anc:
    ch = pose.get(nm)
    constraints[nm] = [
        {'name': c.name, 'type': c.type, 'mute': bool(c.mute),
         'influence': round(c.influence, 4)}
        for c in ch.constraints
    ]
report['chain_pose_constraints'] = constraints

print(json.dumps(report, indent=2, default=str))
sys.stdout.flush()
