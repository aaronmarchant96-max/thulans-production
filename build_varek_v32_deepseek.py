import bpy
import math
import mathutils
from mathutils import Vector

# ---------------------------------------------------------------------------
# Load source blend
# ---------------------------------------------------------------------------
bpy.ops.wm.open_mainfile(filepath="/home/aaron/animation/thulans-production/blender/candidates/varek-v31-canonical.blend")

scene = bpy.context.scene
arm_name = 'Varek simple articulation'
arm = bpy.data.objects.get(arm_name)


def bind_to_bone(obj, bone_name):
    arm_obj = bpy.data.objects.get('Varek simple articulation')
    if not arm_obj:
        return
    vg = obj.vertex_groups.new(name=bone_name)
    vg.add(list(range(len(obj.data.vertices))), 1.0, 'REPLACE')
    mod = obj.modifiers.new('Armature', 'ARMATURE')
    mod.object = arm_obj


def get_mat(name):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    return m


def assign_mat(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


# ---------------------------------------------------------------------------
# 1. GREN-SKILDUS SHOULDER CLOAK
# ---------------------------------------------------------------------------
old = bpy.data.objects.get('Gren Skildus')
if old is not None:
    bpy.data.objects.remove(old, do_unlink=True)

# Build a draped canvas cloak from pydata.
# Grid: rows (vertical drape) x cols (horizontal width)
rows = 14
cols = 16

# Shoulder crest anchor
top_x = 0.38
top_z = 1.85
bottom_z = 1.05

# Widths: wide at shoulder, flaring at bottom
top_width = 0.55
bottom_width = 0.45

verts = []
faces = []

for i in range(rows + 1):
    t = i / rows  # 0 at top, 1 at bottom
    # vertical position with slight ease
    z = top_z + (bottom_z - top_z) * t
    # width interpolation
    w = top_width + (bottom_width - top_width) * t
    # drape outward in +X as it falls (over the shoulder/arm)
    x_center = top_x + 0.10 * t + 0.05 * math.sin(t * math.pi)
    # Y offset: cloak wraps slightly forward then back
    y_center = -0.02 + 0.06 * math.sin(t * math.pi * 1.2)

    for j in range(cols + 1):
        u = j / cols  # 0..1 across width
        # horizontal offset from center
        x = x_center + (u - 0.5) * w
        # organic fold displacement
        fold = 0.035 * math.sin(u * math.pi * 5.0 + t * 3.0)
        fold += 0.02 * math.sin(u * math.pi * 9.0 - t * 2.0)
        # slight curvature across width (drape over shoulder)
        curve = -0.06 * (u - 0.5) ** 2
        y = y_center + fold + curve
        # slight z sag at edges
        zz = z - 0.03 * (u - 0.5) ** 2
        verts.append((x, y, zz))

# faces
for i in range(rows):
    for j in range(cols):
        a = i * (cols + 1) + j
        b = a + 1
        c = a + (cols + 1) + 1
        d = a + (cols + 1)
        faces.append((a, b, c, d))

mesh = bpy.data.meshes.new('Gren Skildus')
mesh.from_pydata(verts, [], faces)
mesh.update()

cloak = bpy.data.objects.new('Gren Skildus', mesh)
scene.collection.objects.link(cloak)

# SubSurf level 2
subsurf = cloak.modifiers.new('Subdivision', 'SUBSURF')
subsurf.levels = 2
subsurf.render_levels = 2

# Solidify thickness 0.03
solid = cloak.modifiers.new('Solidify', 'SOLIDIFY')
solid.thickness = 0.03
solid.offset = 0.0

# Material
assign_mat(cloak, get_mat('Cinderback jade paint'))

# Bind to upper_arm.L
bind_to_bone(cloak, 'upper_arm.L')

# ---------------------------------------------------------------------------
# 2. SIDE PROFILE TORSO-PELVIS BRIDGE
# ---------------------------------------------------------------------------
charcoal = get_mat('Warm charcoal cast iron')

# Spine column
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.055,
    depth=0.35,
    location=(0.0, -0.05, 1.375),
    rotation=(0.0, 0.0, 0.0)
)
spine_col = bpy.context.active_object
spine_col.name = 'Torso_Pelvis_SpineColumn'
assign_mat(spine_col, charcoal)
bind_to_bone(spine_col, 'spine')

# Lateral flank panels
for side, sx in (('L', 0.19), ('R', -0.19)):
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(sx, 0.0, 1.35)
    )
    panel = bpy.context.active_object
    panel.name = f'Torso_Pelvis_Flank_{side}'
    panel.scale = (0.18, 0.04, 0.28)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign_mat(panel, charcoal)
    bind_to_bone(panel, 'pelvis')

# ---------------------------------------------------------------------------
# 3. SIDE PROFILE SHOULDER-TORSO BRIDGE
# ---------------------------------------------------------------------------
# Yoke collar ring
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.22,
    minor_radius=0.035,
    location=(0.0, 0.0, 1.82),
    major_segments=48,
    minor_segments=16
)
yoke = bpy.context.active_object
yoke.name = 'Shoulder_Torso_YokeCollar'
assign_mat(yoke, charcoal)
bind_to_bone(yoke, 'spine')

# Rear shoulder plate
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(0.0, 0.08, 1.72)
)
rear_plate = bpy.context.active_object
rear_plate.name = 'Shoulder_Torso_RearPlate'
rear_plate.scale = (0.35, 0.06, 0.22)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
assign_mat(rear_plate, charcoal)
bind_to_bone(rear_plate, 'spine')

# ---------------------------------------------------------------------------
# Save blend
# ---------------------------------------------------------------------------
bpy.ops.wm.save_as_mainfile(
    filepath="/home/aaron/animation/thulans-production/blender/candidates/varek-v32-canonical.blend"
)

# ---------------------------------------------------------------------------
# 4. RENDER DIAGNOSTIC FRAMES
# ---------------------------------------------------------------------------
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.render.resolution_x = 960
scene.render.resolution_y = 1280
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'


def make_camera(name, loc, target):
    cam_data = bpy.data.cameras.new(name)
    cam_obj = bpy.data.objects.new(name, cam_data)
    scene.collection.objects.link(cam_obj)
    cam_obj.location = Vector(loc)
    direction = Vector(target) - Vector(loc)
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    return cam_obj


# Front 3/4
cam_front = make_camera('V32_Cam_Front34', (1.8, -2.2, 1.35), (0.0, 0.0, 1.2))
scene.camera = cam_front
scene.render.filepath = "/home/aaron/animation/thulans-production/assets/art/varek_v32_front34_frame_001.png"
bpy.ops.render.render(write_still=True)

# Side profile
cam_side = make_camera('V32_Cam_SideProfile', (2.8, 0.0, 1.25), (0.0, 0.0, 1.2))
scene.camera = cam_side
scene.render.filepath = "/home/aaron/animation/thulans-production/assets/art/varek_v32_side_profile_frame_001.png"
bpy.ops.render.render(write_still=True)

# Re-save with cameras included
bpy.ops.wm.save_as_mainfile(
    filepath="/home/aaron/animation/thulans-production/blender/candidates/varek-v32-canonical.blend"
)