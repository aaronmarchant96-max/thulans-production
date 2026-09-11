"""Local articulated-hand/acquisition study, NOT a free-tool physics certificate.

The palm extends distally from the wrist. Three three-link fingers oppose a
two-link thumb. The old fixed rings are not used. Source and unrelated parts
are preserved. Animation is explicitly kinematic; physical handoff stays blocked.
"""
import ast
import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

R = Path('/home/aaron/animation/thulans-production')
S = R / 'blender/candidates/varek-hand-v10.blend'
P = R / 'blender/candidates/varek-articulated-grip-v12.blend'
E = R / 'evidence/varek-articulated-grip-v12'
EXPECTED = '9bf78724a82a0573e0c816597ed278e7214975e3aebdb027de63aa7084df810d'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(S) == EXPECTED and not P.exists()
assert not E.exists() or not any(E.iterdir()), 'Preserve existing evidence'
E.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S))
scene = bpy.context.scene
rig = bpy.data.objects['Varek simple articulation']
collection = bpy.data.collections['Varek_Editable_Parts']
allowed = {'Donor rescue hand R', 'Wrist coupling R',
           'Gauntlet dorsal guard R', 'Gauntlet knuckle bar R'}

def signature():
    return hashlib.sha256(repr(sorted((o.name,
        tuple(tuple(v.co) for v in o.data.vertices),
        tuple(tuple(p.vertices) for p in o.data.polygons),
        tuple(m.name if m else None for m in o.data.materials))
        for o in collection.objects if o.type == 'MESH' and o.name not in allowed)).encode()).hexdigest()

baseline = signature()
rest_before = {b.name: tuple(tuple(row) for row in b.matrix_local) for b in rig.data.bones}
F = json.loads((R / 'evidence/varek-simplified-donor-v2/build.json').read_text())['normalization_factor']
V = lambda v: Vector(v) * F
scene.frame_set(1)
for o in [rig] + [o for o in collection.objects if o.name.startswith('Calf ram ')]:
    o.animation_data_clear()
for b in rig.pose.bones:
    b.matrix_basis = Matrix.Identity(4)
    b.rotation_mode = 'QUATERNION'
bpy.context.view_layer.update()
for file, names in [('rig_varek_salvage_v4.py', {'set_segment', 'solve', 'evaluated_vertices'}),
                    ('fit_varek_grip_v7.py', {'surface'})]:
    tree = ast.parse((R / 'tools' / file).read_text())
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)
        and n.name in names], type_ignores=[]), file + '-helpers', 'exec'), globals())

# Anatomical rest frame: X distal, Y radial/thumb side, Z palm-facing normal.
wr = rig.data.bones['hand.R'].head_local.copy()
hand_rest = rig.data.bones['hand.R'].matrix_local.copy()
X0 = (rig.data.bones['hand.R'].tail_local - wr).normalized()
Y0 = Vector((1, 0, 0))
# Distal / radial / PALMAR is a left-handed anatomical basis on a RIGHT hand.
# Using distal cross radial here silently builds a left hand on the right arm.
Z0 = Y0.cross(X0).normalized()
H0 = Matrix((X0, Y0, Z0)).transposed()
rest_point = lambda p: wr + H0 @ V(p)

# Open-rest finger chains. Closing follows outside tangents to the existing
# 37 mm grip ribs. Joint pins connect every phalange; no concentric ring mesh.
radius = .037 + .009
vertex_radius = radius / math.cos(math.radians(35))
finger_length = 2 * vertex_radius * math.sin(math.radians(35))
root_x = .115 + vertex_radius * math.cos(math.radians(-80))
root_z = .055 + vertex_radius * math.sin(math.radians(-80))
bone_specs = []
for i, y in enumerate([-.05, 0, .05]):
    for j in range(3):
        name = f'finger.R.{i}.{j}'
        a = Vector((root_x + finger_length*j, y, root_z))
        b = a + Vector((finger_length, 0, 0))
        bone_specs.append((name, a, b, 'hand.R' if j == 0 else f'finger.R.{i}.{j-1}'))
# Thumb is a genuine opposite chain: open away from the shaft, then raise
# proximal link before folding the distal pad over the handle's back quadrant.
thumb_root = Vector((.070, .080, 0))
thumb_joint = thumb_root + Vector((-.080, 0, 0))
bone_specs += [('thumb.R.0', thumb_root, thumb_joint, 'hand.R'),
               ('thumb.R.1', thumb_joint, thumb_joint + Vector((-.065, 0, 0)), 'thumb.R.0')]
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='EDIT')
for name, a, b, parent in bone_specs:
    eb = rig.data.edit_bones.new(name)
    eb.head, eb.tail = rest_point(a), rest_point(b)
    eb.parent = rig.data.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT')
assert all(tuple(tuple(row) for row in rig.data.bones[n].matrix_local) == m for n, m in rest_before.items())

verts, faces, weights = [], [], []
def add_box(center, size, driver):
    start = len(verts)
    for s in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
              (-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]:
        verts.append(Vector(center) + Vector(tuple(s[k]*size[k]/2 for k in range(3))))
        weights.append(driver)
    faces.extend(tuple(start+j for j in ids) for ids in
        [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])

def pin(center, radius, width, driver, n=16):
    start = len(verts)
    for y in [-width/2, width/2]:
        for i in range(n):
            a = 2*math.pi*i/n
            verts.append(Vector(center) + Vector((radius*math.cos(a), y, radius*math.sin(a))))
            weights.append(driver)
    faces.extend([tuple(start+i for i in reversed(range(n))), tuple(start+n+i for i in range(n))])
    for i in range(n):
        faces.append((start+i,start+(i+1)%n,start+n+(i+1)%n,start+n+i))

def bind(name):
    o = bpy.data.objects[name]
    mats = list(o.data.materials)
    inv = o.matrix_world.inverted()
    mesh = bpy.data.meshes.new(name + ' articulated v12')
    # The anatomical frame has negative determinant: preserve outward winding.
    mesh.from_pydata([inv @ rest_point(p) for p in verts], [], [tuple(reversed(f)) for f in faces])
    mesh.update()
    for m in mats: mesh.materials.append(m)
    o.data = mesh
    o.vertex_groups.clear()
    for driver in sorted(set(weights)):
        group = o.vertex_groups.new(name=driver)
        group.add([i for i,w in enumerate(weights) if w == driver], 1, 'REPLACE')
    for mod in o.modifiers:
        if mod.type == 'BEVEL':
            mod.width = .0007
            mod.segments = 2
    o['geometry_origin'] = 'Original hinged Thulan manipulator v12'
    if 'donor' in o: del o['donor']

# Palm starts at the wrist and projects DISTALLY. Flat seating pad touches the
# back tangent of the ribs; the wrist is not mounted on the finger side.
add_box((.083, 0, .001), (.112, .146, .034), 'hand.R')
add_box((.020, 0, -.003), (.048, .083, .040), 'hand.R')
add_box((.060, .078, -.002), (.042, .042, .036), 'hand.R')
for name, a, b, parent in bone_specs:
    width = .031 if name.startswith('finger') else .014
    thick = .018 if name.startswith('finger') else .022
    add_box((a+b)/2, (abs(b.x-a.x)-.004, width, thick), name)
    pin(a, .012 if name.startswith('finger') else .014, width+.006, name)
bind('Donor rescue hand R')
verts, faces, weights = [], [], []
pin((0, 0, 0), .031, .095, 'hand.R', 24)
bind('Wrist coupling R')
verts, faces, weights = [], [], []
for y in [-.051, .051]:
    add_box((.012, y, -.003), (.054, .018, .073), 'hand.R')
bind('Gauntlet dorsal guard R')
verts, faces, weights = [], [], []
add_box((.075, 0, -.024), (.086, .128, .014), 'hand.R')
bind('Gauntlet knuckle bar R')
assert signature() == baseline

X = Vector((-.494, -.869, 0)).normalized()
Y = Vector((0, 0, 1))
Z = Y.cross(X)
H = Matrix((X, Y, Z)).transposed()
D = H @ H0.inverted()
wr_grip = V((-.650, -.300, 1.250))
shaft_center = wr_grip + H @ V((.115, 0, .055))
tool_rest_contact = V((-.86, -.17, 1.250))
tools = [o for o in collection.objects if o.type == 'MESH' and o.get('rigid_driver_bone') == 'tool']
interface = [bpy.data.objects[n] for n in allowed | {'Donor forearm R'}]

def smooth(t):
    t = min(1., max(0., t))
    return t*t*(3-2*t)

def phase(f, a, b): return smooth((f-a)/(b-a))

def local_segment(name, a, b, wrist):
    # Preserve the declared shaft-parallel hinge axis, not just bone endpoints.
    theta = math.atan2((b-a).z, (b-a).x)
    rest_theta = math.pi if name.startswith('thumb') else 0
    orient = H @ Matrix.Rotation(rest_theta-theta, 3, 'Y') @ H0.inverted()
    poses[name] = (Matrix.Translation(wrist + H @ V(a))
        @ orient.to_4x4() @ rig.data.bones[name].matrix_local.to_3x3().to_4x4())

def arm_segment(name, a, b):
    rb=rig.data.bones[name]
    q=(rb.tail_local-rb.head_local).rotation_difference(b-a)
    poses[name]=Matrix.Translation(a)@q.to_matrix().to_4x4()@rb.matrix_local.to_3x3().to_4x4()

rows = []
for frame in range(1, 169):
    scene.frame_set(frame)
    poses={b.name:b.matrix_local.copy() for b in rig.data.bones}
    # Approach from the open palm side. Lift only after all pads are closed;
    # plant before release. The tool driver is explicitly kinematic in this study.
    retreat = .105 * (1-phase(frame, 1, 24) + phase(frame, 151, 168))
    lift = .12 * (phase(frame, 61, 84) - phase(frame, 97, 120))
    wrist = wr_grip - Z*retreat*F + Vector((0,0,lift*F))
    contact = shaft_center + Vector((0,0,lift*F))
    a = rig.data.bones['upper_arm.R'].head_local.copy()
    elbow = solve(a, wrist, rig.data.bones['upper_arm.R'].length,
                  rig.data.bones['forearm.R'].length, a + Vector((0,0,-1)))
    arm_segment('upper_arm.R', a, elbow)
    arm_segment('forearm.R', elbow, wrist)
    poses['hand.R'] = Matrix.Translation(wrist) @ D.to_4x4() @ hand_rest.to_3x3().to_4x4()
    # Yaw the parked head so its long dimension clears the right boot.
    poses['tool'] = Matrix.Translation(contact) @ Matrix.Rotation(math.pi/2,4,'Z') @ Matrix.Translation(-tool_rest_contact) @ rig.data.bones['tool'].matrix_local
    # Sequential closure, reverse sequential opening; shafts never need to
    # pass through a pre-closed cavity.
    q0 = phase(frame,25,36) * (1-phase(frame,139,150))
    q1 = phase(frame,37,48) * (1-phase(frame,130,139))
    q2 = phase(frame,49,60) * (1-phase(frame,121,130))
    for i,y in enumerate([-.05,0,.05]):
        p = Vector((root_x,y,root_z))
        for j, deg in enumerate([45*q0,45*q0+70*q1,45*q0+70*q1+70*q2]):
            theta = math.radians(deg)
            end = p + Vector((finger_length*math.cos(theta),0,finger_length*math.sin(theta)))
            local_segment(f'finger.R.{i}.{j}', p, end, wrist)
            p = end
    thumb_a = math.radians(180-90*phase(frame,25,44)*(1-phase(frame,134,150)))
    # Solve distal pad tangent from the actual 34 mm smooth grip and 11 mm
    # half-thickness; do not leave the former 1.3 mm thumb gap.
    thumb_closed = math.asin(.045/math.hypot(.045,.025))-math.atan2(.025,.045)
    thumb_b = thumb_a-(math.pi/2-thumb_closed)*phase(frame,45,60)*(1-phase(frame,121,134))
    ta = thumb_root.copy()
    tb = ta + Vector((.080*math.cos(thumb_a),0,.080*math.sin(thumb_a)))
    tc = tb + Vector((.065*math.cos(thumb_b),0,.065*math.sin(thumb_b)))
    local_segment('thumb.R.0',ta,tb,wrist)
    local_segment('thumb.R.1',tb,tc,wrist)
    # Explicit parent-space conversion avoids per-joint dependency-graph
    # evaluation and eliminates reliance on stale parent pose matrices.
    for pb in rig.pose.bones:
        rb=pb.bone
        if rb.parent:
            pb.matrix_basis=(rb.matrix_local.inverted() @ rb.parent.matrix_local
                @ poses[rb.parent.name].inverted() @ poses[pb.name])
        else: pb.matrix_basis=rb.matrix_local.inverted() @ poses[pb.name]
    bpy.context.view_layer.update()
    for name in ['hand.R']+[n for n,_,_,_ in bone_specs]:
        err=max(abs(rig.pose.bones[name].matrix[i][j]-poses[name][i][j]) for i in range(4) for j in range(4))
        assert err<.00001,(frame,name,'pose conversion',err)
    wrist_angle = math.degrees((wrist-elbow).angle(X))
    feet = {s:min(v.z for v in evaluated_vertices(bpy.data.objects['Anchor sole '+s])) for s in ['L','R']}
    tool_z = min(v.z for o in tools for v in evaluated_vertices(o))
    assert all(abs(z)<.00025 for z in feet.values()) and tool_z>=-.00025
    assert wrist_angle < 45, (frame, wrist_angle)
    # Mesh-to-tool surface intersections, evaluated at EVERY integer frame.
    tool_bvhs = [(o.name,surface(o)) for o in tools]
    hits = {}
    for o in interface:
        bvh = surface(o)
        for name,t in tool_bvhs:
            n = len(bvh.overlap(t))
            if n: hits[o.name+' / '+name] = n
    rows.append({'frame':frame,'wrist_deflection_deg':wrist_angle,
                 'sole_z':feet,'tool_min_z':tool_z,'surface_crossings':hits})
    if frame%24==0: print('CHECKED_FRAME',frame,'crossings',hits,flush=True)
    for pb in rig.pose.bones:
        for ch in ['location','rotation_quaternion','scale']: pb.keyframe_insert(ch)
for layer in rig.animation_data.action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for curve in bag.fcurves:
                for key in curve.keyframe_points: key.interpolation='LINEAR'
scene.frame_start, scene.frame_end, scene.render.fps = 1,168,24
scene.timeline_markers.clear()
for frame,label in [(1,'OPEN'),(24,'PALM SEATED'),(60,'CLOSED'),(84,'LIFT'),(96,'HOLD'),(120,'PLANT'),(150,'RELEASE'),(168,'WITHDRAW')]:
    scene.timeline_markers.new(label,frame=frame)
scene['status'] = 'ARTICULATED_GRIP_KINEMATIC_DIAGNOSTIC'
scene['physical_handoff_authorized'] = False
scene['tool_motion'] = 'KEYED TOOL BONE — NOT FREE DYNAMICS'
scene['grip_finger_rows'] = [-.05,0,.05]
scene.camera = bpy.data.objects['Front threequarter']
scene.render.engine = 'CYCLES'
scene.render.resolution_x, scene.render.resolution_y = 640,800
scene.render.resolution_percentage=100
scene.cycles.samples=16
scene.frame_set(60)
assert baseline == signature() and sha(S) == EXPECTED
bpy.ops.wm.save_as_mainfile(filepath=str(P))
digest = sha(P)
report = {'candidate_sha256':digest,'source_sha256':EXPECTED,
          'claim_class':'OBSERVED','result':'KINEMATIC_DIAGNOSTIC_ONLY',
          'changed_meshes':sorted(allowed),'unrelated_geometry_and_materials_unchanged':baseline==signature(),
          'existing_bone_rest_matrices_unchanged':True,
          'new_digit_bones':[n for n,_,_,_ in bone_specs],
          'hand_frame':{'X':'wrist toward palm/fingers','Y':'radial/thumb side, up during grip','Z':'palm contact normal'},
          'tool_control':'ANIMATED, NOT FREE DYNAMICS','physical_handoff_authorized':False,
          'remaining':['human anatomy review','independent saved readback','self-collision sweep',
                       'finite-force load simulation, negative controls, solver robustness'],
          'frames':rows}
(E/'measurements.json').write_text(json.dumps(report,indent=2))
print('FROZEN_DIAGNOSTIC',digest,'crossing_frames',sum(bool(r['surface_crossings']) for r in rows),flush=True)
scene.render.filepath=str(E/'full.png')
bpy.ops.render.render(write_still=True)
cam=scene.camera
target = shaft_center
scene.render.resolution_x=scene.render.resolution_y=640
cam.data.ortho_scale=.57
for name,delta,frame in [('closed-front',(-1.2,-1.8,.35),60),('closed-reverse',(1.2,1.3,.3),60),('open',(-1.2,-1.8,.35),24)]:
    scene.frame_set(frame)
    cam.location=target+Vector(delta)
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(E/(name+'.png'))
    bpy.ops.render.render(write_still=True)
assert sha(P)==digest and sha(S)==EXPECTED
print('V12_DIAGNOSTIC_STILLS_READY',flush=True)
