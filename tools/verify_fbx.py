"""Blender-only FBX round-trip geometry report. Does not validate UE import/runtime.
Run: blender -b --python tools/verify_fbx.py -- /path/to/assets/resonance
"""
import bpy,bmesh,json,math,sys
from pathlib import Path
root=Path(sys.argv[sys.argv.index('--') + 1]).resolve()
manifest=json.loads((root/'asset_manifest.json').read_text())
report={}
for name,expected in manifest['assets'].items():
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=.01
 bpy.ops.import_scene.fbx(filepath=str(root/expected['fbx']),use_custom_normals=True)
 meshes=[o for o in bpy.data.objects if o.type=='MESH' and not o.name.startswith('UCX_')]
 assert len(meshes)==1,(name,[o.name for o in meshes])
 o=meshes[0];m=o.data;m.calc_loop_triangles()
 bm=bmesh.new();bm.from_mesh(m)
 bad=sum(1 for e in bm.edges if not e.is_manifold)
 coords=[o.matrix_world@v.co for v in m.vertices]
 lo=[min(v[i] for v in coords) for i in range(3)];hi=[max(v[i] for v in coords) for i in range(3)]
 dims=[hi[i]-lo[i] for i in range(3)]
 report[name]={'object':o.name,'world_dimensions_cm':dims,'expected_dimensions_cm':expected['dimensions_cm'],'world_bounds_min_cm':lo,'world_bounds_max_cm':hi,'origin_cm':list(o.location),'scale':list(o.scale),'triangles':len(m.loop_triangles),'vertices':len(m.vertices),'non_manifold_edges':bad,'zero_area_faces':sum(1 for p in m.polygons if p.area<1e-9),'uv_layers':[u.name for u in m.uv_layers],'material_slots':[s.name for s in o.material_slots],'material_indices':sorted({p.material_index for p in m.polygons}),'collision_objects':[x.name for x in bpy.data.objects if x.name.startswith('UCX_')]}
 remaining=set(bm.faces);volumes=[]
 while remaining:
  component=set();stack=[next(iter(remaining))]
  while stack:
   f=stack.pop()
   if f in component:continue
   component.add(f)
   stack.extend(n for e in f.edges for n in e.link_faces if n not in component)
  remaining-=component
  volume=0
  for f in component:
   verts=[v.co for v in f.verts]
   for i in range(1,len(verts)-1):volume+=verts[0].dot(verts[i].cross(verts[i+1]))/6
  volumes.append(volume)
 report[name]['connected_component_signed_volumes_cm3']=volumes
 bm.free()
(root/'independent_mesh_review.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
