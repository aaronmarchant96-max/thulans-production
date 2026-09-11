"""Independent saved-file checks; no build or render and no visual verdict."""
import bpy,hashlib,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
R=Path('/home/aaron/animation/thulans-production');E=R/'evidence/varek-hand-v10';P=R/'blender/candidates/varek-hand-v10.blend';S=R/'blender/candidates/varek-hand-v9.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((E/'measurements.json').read_text());assert sha(P)==report['candidate_sha256'] and sha(S)==report['source_sha256']
allowed=set(report['changed_meshes'])
def invariants():
    rig=bpy.data.objects['Varek simple articulation']
    meshes=sorted((o.name,tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons),tuple(m.name if m else None for m in o.data.materials)) for o in bpy.data.collections['Varek_Editable_Parts'].objects if o.type=='MESH' and o.name not in allowed)
    bones=[(b.name,b.parent.name if b.parent else None,tuple(b.head_local),tuple(b.tail_local),tuple(tuple(row) for row in b.matrix_local)) for b in rig.data.bones]
    return hashlib.sha256(repr((meshes,bones)).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(S));baseline=invariants()
bpy.ops.wm.open_mainfile(filepath=str(P));assert invariants()==baseline
def surface(o):
    e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();tree=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[list(p.vertices) for p in m.polygons]);e.to_mesh_clear();return tree
parts=bpy.data.collections['Varek_Editable_Parts'].objects;tools=[o for o in parts if o.type=='MESH' and o.get('rigid_driver_bone')=='tool'];results=[]
for name in allowed:
    o=bpy.data.objects[name];driver='forearm.R' if name=='Donor forearm R' else 'hand.R';index=o.vertex_groups[driver].index
    assert all(len(v.groups)==1 and v.groups[0].group==index and abs(v.groups[0].weight-1)<1e-6 for v in o.data.vertices)
for frame in [1,36,64]:
    bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();hits={}
    for name in allowed:
        a=surface(bpy.data.objects[name])
        for o in tools:
            n=len(a.overlap(surface(o)))
            if n:hits[name+' / '+o.name]=n
    results.append({'frame':frame,'tool_surface_crossings':hits});assert not hits
assert sha(P)==report['candidate_sha256'] and sha(S)==report['source_sha256']
(E/'saved-readback.json').write_text(json.dumps({'claim_class':'OBSERVED','candidate_sha256':sha(P),'unchanged_out_of_scope_geometry_and_rest_bones':True,'single_bone_weights_valid':True,'samples':results,'result':'SAVED_CHECKS_PASS','human_review':'PENDING'},indent=2))
print('SAVED_CHECKS_PASS',flush=True)
