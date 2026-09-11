import bpy, bmesh
from pathlib import Path
R = Path('/home/aaron/animation/thulans-production')
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/candidates/varek-carry-v14.blend'))
pelvis = bpy.data.objects['Pelvic cradle']
bm = bmesh.new(); bm.from_mesh(pelvis.data)
print('verts', len(bm.verts), 'faces', len(bm.faces), 'edges', len(bm.edges))
print('signed volume', bm.calc_volume(signed=True))
# duplicate faces
face_sets = {}
dup = 0
for f in bm.faces:
    key = frozenset(v.index for v in f.verts)
    face_sets[key] = face_sets.get(key, 0) + 1
    if face_sets[key] == 2:
        dup += 1
print('duplicate_faces', dup)
# zero area
zero = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
print('zero_area_faces', zero)
# degenerate edges
zero_edges = sum(1 for e in bm.edges if e.calc_length() < 1e-8)
print('zero_length_edges', zero_edges)
# normals vs center direction
import mathutils
inward = 0; outward = 0
for f in bm.faces:
    c = f.calc_center_median()
    if f.normal.dot(c) < 0:
        inward += 1
    else:
        outward += 1
print('normals_inward', inward, 'outward', outward)
