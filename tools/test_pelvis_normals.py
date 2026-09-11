import bpy, bmesh
from pathlib import Path
R = Path('/home/aaron/animation/thulans-production')
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/candidates/varek-carry-v14.blend'))
pelvis=bpy.data.objects['Pelvic cradle']
bm=bmesh.new(); bm.from_mesh(pelvis.data)
vol=bm.calc_volume(signed=True)
print('signed volume',vol,'abs',abs(vol))
# count normals pointing toward origin vs away
import mathutils
inward=0; outward=0
for f in bm.faces:
    c=f.calc_center_median(); n=f.normal
    if n.dot(c-mathutils.Vector((0,0,1)))<0: inward+=1
    else: outward+=1
print('inward',inward,'outward',outward)
