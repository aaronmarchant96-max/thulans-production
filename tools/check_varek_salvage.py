"""Read-only Blender scene check; writes a small report outside the candidate."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector

root=Path('/home/aaron/animation/thulans-production')
candidate=root/'blender/candidates/varek-simplified-donor-v2.blend'
report=root/'evidence/varek-simplified-donor-v2/readback.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=sha(candidate)
assert Path(bpy.data.filepath)==candidate
collection=bpy.data.collections['Varek_Editable_Parts']
deps=bpy.context.evaluated_depsgraph_get()
points=[o.evaluated_get(deps).matrix_world@Vector(c) for o in collection.objects if o.type=='MESH' for c in o.evaluated_get(deps).bound_box]
height=max(v.z for v in points)-min(v.z for v in points)
floor=min(v.z for v in points)
donors=[o.name for o in collection.objects if 'donor' in o]
missing=[o.name for o in collection.objects if o.type=='MESH' and not o.data.materials]
checks={'height':abs(height-2.4384)<.0005,'ground_contact':abs(floor)<.00025,'donor_components':len(donors)==10,'materials_present':not missing,'cycles':bpy.context.scene.render.engine=='CYCLES','candidate_unchanged':sha(candidate)==before}
data={'claim_class':'OBSERVED','scope':'STATIC_SCENE_STRUCTURE_ONLY','candidate_sha256':before,'height_m':height,'floor_z':floor,'donor_objects':donors,'checks':checks,'result':'PASS' if all(checks.values()) else 'FAIL','visual_approval':False,'animation_validated':False}
report.write_text(json.dumps(data,indent=2))
print(json.dumps(data,indent=2))
if not all(checks.values()):raise RuntimeError('Static readback failed')
