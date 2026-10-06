"""Original Resonance asset pack. Run blender -b --python build_models.py -- --render.
Coordinates are authored numerically in centimetres; scene scale_length = .01.
No proprietary meshes, textures or shaders are imported. Blender 4.3.2.
"""
import bpy, math, json, os, sys, random
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for p in ('exports','renders'): (ROOT/p).mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials): bpy.data.materials.remove(m)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=.01
PALETTE=[('M_Shell',(0.79,.84,.82,1)),('M_Seam',(.028,.052,.072,1)),('M_Signal',(.055,.64,.64,1)),('M_Control',(.97,.29,.065,1)),('M_Echo',(.29,.85,.71,1)),('M_Stone',(.115,.20,.23,1)),('M_StoneLight',(.21,.33,.35,1)),('M_EchoLight',(.67,.96,.82,1))]
M=[]
for n,c in PALETTE:
 m=bpy.data.materials.new(n); m.diffuse_color=c; m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=c; bs.inputs['Roughness'].default_value=.55; bs.inputs['Metallic'].default_value=.05
 M.append(m)
parts=[]
def use(o,mat):
 for m in M: o.data.materials.append(m)
 for p in o.data.polygons:p.material_index=mat
 parts.append(o);return o

def box(loc,dim,mat,bevel=0,rot=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dim;o.rotation_euler.z=rot
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  b=o.modifiers.new('Purposeful edge chamfer','BEVEL');b.width=bevel;b.segments=1
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=b.name)
 return use(o,mat)
def cyl(loc,r,depth,mat,vertices=12,axis='Z',r2=None):
 bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=r,radius2=r if r2 is None else r2,depth=depth,location=loc)
 o=bpy.context.object
 if axis=='Y':o.rotation_euler.x=math.pi/2
 if axis=='X':o.rotation_euler.y=math.pi/2
 return use(o,mat)
def mesh(name,verts,faces,mat):
 d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update();o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);return use(o,mat)
def ring(loc,outer,inner,depth,mat,n=16,axis='Z'):
 verts=[]
 for z,r in [(-depth/2,outer),(depth/2,outer),(-depth/2,inner),(depth/2,inner)]:
  for i in range(n):
   a=2*math.pi*i/n;v=(r*math.cos(a),r*math.sin(a),z)
   if axis=='Y':v=(v[0],v[2],v[1])
   verts.append(tuple(v[j]+loc[j] for j in range(3)))
 faces=[]
 for i in range(n):
  j=(i+1)%n
  faces += [(i,j,n+j,n+i),(2*n+j,2*n+i,3*n+i,3*n+j),(n+i,n+j,3*n+j,3*n+i),(j,i,2*n+i,2*n+j)]
 return mesh('Annular housing',verts,faces,mat)
def crystal(loc,r,h,mat,n=6,tilt=(0,0),seed=0):
 rng=random.Random(seed);vs=[]
 for z,scale in [(0,.65),(h*.23,1),(h*.77,.79)]:
  for i in range(n):
   a=2*math.pi*i/n;vs.append((loc[0]+math.cos(a)*r*scale+tilt[0]*z,loc[1]+math.sin(a)*r*scale+tilt[1]*z,loc[2]+z))
 vs.append((loc[0]+tilt[0]*h+.15*r,loc[1]+tilt[1]*h,loc[2]+h))
 fs=[tuple(reversed(range(n)))]
 for k in range(2):
  for i in range(n):fs.append((k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i))
 for i in range(n):fs.append((2*n+i,2*n+(i+1)%n,3*n))
 o=mesh('Faceted echo',vs,fs,mat)
 for p in o.data.polygons:
  if p.index%5==2:p.material_index=7 if mat==4 else mat
 return o
ASSETS={};COLL={};REPORT={}
def finish(name,colliders=[]):
 global parts
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
 scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 # Correct face winding after procedural construction; preserve deliberate flat facets.
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False)
 bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.02)
 bpy.ops.object.mode_set(mode='OBJECT')
 tri=o.modifiers.new('Explicit triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=tri.name)
 ASSETS[name]=o;parts=[];cs=[]
 for i,(loc,dim) in enumerate(colliders):
  c=box(loc,dim,1);c.name=f'UCX_{name}_{i:02d}';c.hide_render=True;c.display_type='WIRE';cs.append(c)
 COLL[name]=cs;parts=[]
 bpy.context.view_layer.update()
 REPORT[name]={'fbx':f'exports/{name}.fbx','dimensions_cm':[round(x,3) for x in o.dimensions],'triangles':len(o.data.polygons),'vertices':len(o.data.vertices),'material_slots':[m.name for m in o.data.materials],'used_material_indices':sorted(set(p.material_index for p in o.data.polygons)),'uv_sets':[u.name for u in o.data.uv_layers],'collision_hulls':len(cs),'pivot_cm':[0,0,0]}
 return o
# 01: Tuning Lens. Low cylindrical heel seats on a receiving slot; two cheek guards
# protect a large octagonal optical head. Rear bridge gives an obvious hand grip.
cyl((0,0,1.5),7.6,3,1)
cyl((0,0,4),9.7,2,0)
box((0,0,9),(17,13,9),0,2)
box((0,0,16),(13,10,10),1,1)
for x in (-9.1,9.1):box((x,0,13),(3.3,12,15),0,1.3)
# Front optic (+Y); ring geometry has a real aperture.
ring((0,1.5,24),11.6,8.9,7,0,16,'Y')
ring((0,5.25,24),9.1,7.4,1.4,1,16,'Y')
cyl((0,5.2,24),7.2,1.2,4,12,'Y')
ring((0,6,24),6.7,6.15,.3,7,12,'Y')
# Three index tabs, deliberately asymmetrical orange calibration dial.
for a in (math.pi/2,math.pi*7/6,math.pi*11/6):
 x,z=10.15*math.cos(a),24+10.15*math.sin(a)
 box((x,5.35,z),(2.4,1.1,2),2,.25,0)
cyl((12.8,0,23),3.9,3.2,3,12,'X');cyl((14.5,0,23),2.8,.4,1,12,'X')
box((0,-6.5,27),(15,3.1,3.5),3,1.2)
for x in (-6,6):box((x,-6.1,23),(3,3,7),1,.8)
for z in (9,12,15):box((0,7,z),(7,.8,1.1),2,.25)
finish('SM_TuningLens',[((0,0,8.5),(19,15,17)),((0,1.5,25),(24,13,22))])
# 02: Echo Glass. A manufactured resonant nugget, grown in a hexagonal pressure shoe.
cyl((0,0,1.7),9,3.4,1,6);cyl((0,0,3),9.5,2,0,6)
crystal((0,0,3),7.2,20,4,6,seed=3)
crystal((6,2,3),3.4,12,4,5,tilt=(.09,.05),seed=2)
crystal((-5,-3,3),3,10.5,4,5,tilt=(-.1,-.06),seed=1)
for a in (0,math.pi*2/3,math.pi*4/3):
 box((7.5*math.cos(a),7.5*math.sin(a),5.4),(2.5,3.6,4.5),2,.5,a)
finish('SM_EchoGlass',[((0,0,10.5),(19,18,21))])
# 03: Site ground cradle. Geology is asymmetric, instrumentation has clear intent.
random.seed(28)
for i in range(8):
 a=2*math.pi*i/8;r=26+random.uniform(-4,5)
 o=cyl((r*math.cos(a),r*math.sin(a),5+random.uniform(-1,2)),random.uniform(16,24),13,5 if i%3 else 6,5,r2=random.uniform(11,16));o.rotation_euler.z=a
cyl((0,0,10),33,16,5,9,r2=29)
ring((0,0,17),27,17,5,6,12)
ring((0,0,20),23,17,2,1,12)
# Three ground-level interface pedestals echo the optical instrument without copying slots.
for a in (math.pi/2,7*math.pi/6,11*math.pi/6):
 x,y=31*math.cos(a),31*math.sin(a)
 box((x,y,15),(14,18,9),0,2,a-math.pi/2)
 cyl((x,y,20),5.5,1.5,1,12)
 ring((x,y,21),4.7,3.1,.8,3,12)
 # No gameplay socket represented here: instrument interaction target only.
finish('SM_ResonanceSite_Base',[((0,0,10),(71,71,20))])
# Petal prism is a shaped, closed radial slab, rather than a rectangular pillar.
def petal(angle,active):
 # side profile: bottom outside/inside to narrow oblique crown; x radial, y width
 profile=[(14,20),(23,20),(27 if active else 19,51),(40 if active else 13,67),(33 if active else 5,73),(20 if active else 7,47)]
 verts=[]
 for side in (-1,1):
  for r,z in profile:
   w=7 if z<55 else 4
   verts.append((r*math.cos(angle)-side*w*math.sin(angle),r*math.sin(angle)+side*w*math.cos(angle),z))
 n=len(profile);faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
 for i in range(n):faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
 o=mesh('Lithic shutter',verts,faces,5)
 for p in o.data.polygons:
  if p.index in (1,4,5):p.material_index=6
 # Distinct bright inserts only in the opened crown.
 if active:
  crystal((21*math.cos(angle),21*math.sin(angle),35),3.3,25,4,5,tilt=(.32*math.cos(angle),.32*math.sin(angle)))
for active in (False,True):
 cyl((0,0,23),16,8,1,9,r2=13)
 for a in (math.pi/2,7*math.pi/6,11*math.pi/6):petal(a,active)
 if active:
  crystal((0,0,24),9,38,4,6)
  ring((0,0,35),15,12,2,2,12)
  ring((0,0,48),12,10,2,7,12)
 else:
  cyl((0,0,29),9,4,6,6,r2=6)
  for a in (math.pi/2,7*math.pi/6,11*math.pi/6):
   cyl((12*math.cos(a),12*math.sin(a),47),2,3,3,6)
 finish('SM_ResonanceSite_'+('Active' if active else 'Dormant'))
# Export one render mesh + matching UCX hulls per FBX. No external textures.
for name,o in ASSETS.items():
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
 for c in COLL[name]:c.select_set(True)
 bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(ROOT/'exports'/f'{name}.fbx'),use_selection=True,object_types={'MESH'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Y',axis_up='Z',use_mesh_modifiers=True,mesh_smooth_type='FACE',use_triangles=True,bake_anim=False,add_leaf_bones=False,path_mode='AUTO')
# Authoritative machine-readable contract, cm bounds and actual mesh counts.
manifest={'version':1,'generator':'Blender 4.3.2','source_units':'centimetres','blender_unit_scale':.01,'export_forward':'-Y','export_up':'Z','authored_front':'+Y','import_uniform_scale':1.0,'scale_status':'provisional; actual Tier1 collision reference has not been measured','origin':'lens/nugget base contact center; site ground center with geology extending 2.107 cm below ground; all site pieces share origin','attachment_normal':'body -Z; receiver +Z; configure actual ChildSlotComponent in UE','materials':[{ 'name':n,'base_color_linear':c,'roughness':.55,'metallic':.05}for n,c in PALETTE],'assets':REPORT,'site_assembly':{'base':'SM_ResonanceSite_Base','dormant':'SM_ResonanceSite_Dormant','active':'SM_ResonanceSite_Active','transform':'all at 0,0,0; toggle state mesh visibility; active and dormant mutually exclusive'},'unreal_notes':['Import normals','Import collision for lens, nugget, base; state meshes have no collision','Set Has Navigation Data false on every mesh','Base collider is intentionally simplified; player interaction should use a dedicated component','Use opaque materials; active silhouette does not require emissive or translucency','Generate UV1 lightmap if static lighting is used; authored UV0 is smart projected','Disable automatic collision generation when authored UCX is used','Windows UE editor import, cooking, runtime and in-game fit UNTESTED']}
(ROOT/'asset_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Source model scene is clean, all objects retain assembly-space origins.
for cs in COLL.values():
 for c in cs:c.hide_set(True)
for o in ASSETS.values():o.hide_render=True
ASSETS['SM_TuningLens'].hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source'/'ResonanceAssets.blend'))
# Studio render scene. The delivered source stays at true shared pivots.
if '--render' in sys.argv:
 scene.render.engine='CYCLES';scene.cycles.samples=128;scene.cycles.use_denoising=False
 scene.render.resolution_x=1200;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
 scene.world.color=(.18,.18,.18)
 scene.view_settings.view_transform='AgX'
 world=scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.17,.20,1);world.node_tree.nodes['Background'].inputs[1].default_value=.5
 ground=box((0,0,-1.1),(2000,2000,2),1,0);parts=[]
 # ground uses neutral material, unrelated to export assets
 gm=bpy.data.materials.new('Studio only');gm.diffuse_color=(.085,.12,.15,1);gm.use_nodes=True;gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.085,.12,.15,1);gm.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8;ground.data.materials.clear();ground.data.materials.append(gm)
 for p in ground.data.polygons:p.material_index=0
 def light(loc,energy,size):
  bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=energy;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((0,0,25))-l.location).to_track_quat('-Z','Y').to_euler()
 light((50,65,110),180000,90);light((-65,20,60),110000,80);light((10,-65,100),220000,70)
 bpy.ops.object.camera_add(location=(70,100,65));cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.lens=50;cam.data.clip_end=5000
 def render(name,visible,target,scale,position):
  for key,o in ASSETS.items():o.hide_render=key not in visible
  cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
  scene.render.filepath=str(ROOT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
 render('01_TuningLens',['SM_TuningLens'],(0,0,18),53,(63,100,56))
 render('02_EchoGlass',['SM_EchoGlass'],(0,0,11),35,(60,85,55))
 render('03_SiteDormant',['SM_ResonanceSite_Base','SM_ResonanceSite_Dormant'],(0,0,33),110,(120,170,115))
 render('04_SiteActive',['SM_ResonanceSite_Base','SM_ResonanceSite_Active'],(0,0,33),110,(120,170,115))
 render('05_TuningLensRear',['SM_TuningLens'],(0,0,18),53,(-63,-100,50))
 print('MODELS_COMPLETE',str(ROOT))
