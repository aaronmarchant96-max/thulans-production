import bpy,json
from pathlib import Path
P=Path('/home/aaron/animation/thulans-production')
bpy.ops.wm.open_mainfile(filepath=str(P/'blender/candidates/varek-hammer-study-v5.blend'))
o=bpy.data.objects['Donor rescue hand R'];m=o.data
adj={v.index:set() for v in m.vertices}
for e in m.edges:
    a,b=e.vertices;adj[a].add(b);adj[b].add(a)
seen=set();rows=[]
for i in adj:
    if i in seen:continue
    stack=[i];used=[];seen.add(i)
    while stack:
        j=stack.pop();used.append(j)
        for k in adj[j]-seen:seen.add(k);stack.append(k)
    pts=[m.vertices[j].co for j in used]
    rows.append({'indices':used,'verts':len(used),'lo':[min(v[k] for v in pts) for k in range(3)],'hi':[max(v[k] for v in pts) for k in range(3)]})
(P/'evidence/varek-hammer-study-v5/hand-components.json').write_text(json.dumps(rows,indent=2))
print('HAND',o.matrix_world[:],o.get('source_groups'),flush=True)
print(json.dumps([{k:v for k,v in row.items() if k!='indices'} for row in rows]),flush=True)
