import bpy
from pathlib import Path
R = Path('/home/aaron/animation/thulans-production')
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/candidates/varek-carry-v15.blend'))
pelvis = bpy.data.objects['Pelvic cradle']
print('verts', len(pelvis.data.vertices), 'faces', len(pelvis.data.polygons), 'edges', len(pelvis.data.edges))
rig = bpy.data.objects['Varek simple articulation']
print('pose_position', rig.data.pose_position)
# bounds
print('bounds x', min(v.co.x for v in pelvis.data.vertices), max(v.co.x for v in pelvis.data.vertices))
print('bounds z', min(v.co.z for v in pelvis.data.vertices), max(v.co.z for v in pelvis.data.vertices))
