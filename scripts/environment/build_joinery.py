"""Original V03 architectural joinery. Run: blender -b -t 2 -P scripts/environment/build_joinery.py

Blender authors bevelled mouldings, glazed arch profiles, rebated timber panels,
turned hinges and swept brass handles. Runtime only rotates exported hinge nodes.
Coordinates accepted by helpers are +Y up, +Z outdoors; glTF exports that contract.
"""
from pathlib import Path
import bpy, math, json, sys, struct
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'public/assets/environment/joinery';OUT.mkdir(parents=True,exist_ok=True)
LAYOUT=json.loads((ROOT/'scripts/environment/layout.json').read_text())
TEX=ROOT/'public/assets/textures'
bpy.ops.wm.read_factory_settings(use_empty=True)

def V(p):return (p[0],-p[2],p[1])
def mat(name,color,rough=.65,metal=0,tex=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
 if tex:
  for suffix,inp in [('color','Base Color'),('roughness','Roughness'),('normal','Normal')]:
   f=TEX/f'{tex}-{suffix}.jpg'
   if not f.exists():continue
   node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(f),check_existing=True)
   if suffix!='color':node.image.colorspace_settings.name='Non-Color'
   if suffix=='normal':
    normal=m.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.12;m.node_tree.links.new(node.outputs['Color'],normal.inputs['Color']);m.node_tree.links.new(normal.outputs['Normal'],bs.inputs[inp])
   elif suffix=='color':
    mul=m.node_tree.nodes.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;mul.inputs[2].default_value=(*color,1);m.node_tree.links.new(node.outputs['Color'],mul.inputs[1]);m.node_tree.links.new(mul.outputs[0],bs.inputs[inp])
   else:m.node_tree.links.new(node.outputs['Color'],bs.inputs[inp])
 return m
WOOD=mat('Joinery_warm_walnut',(.30,.17,.081),.72,tex='oak')
OAK=mat('Joinery_honey_oak',(.56,.37,.17),.72,tex='oak')
GREEN=mat('Joinery_forest_green',(.09,.16,.105),.65,tex='oak')
SAGE=mat('Joinery_sage_cream',(.72,.67,.51),.76,tex='oak')
BRONZE=mat('Joinery_sunroom_bronze',(.30,.25,.13),.4,.65)
BRASS=mat('Joinery_brass_fittings',(.63,.45,.19),.31,.78)
DARK=mat('Joinery_recessed_walnut',(.15,.085,.035),.83,tex='oak')
GLASS=mat('Joinery_clear_glass',(.72,.85,.82),.14,.04)
bs=GLASS.node_tree.nodes.get('Principled BSDF');bs.inputs['Alpha'].default_value=.13;GLASS.surface_render_method='DITHERED'
GLASS.use_transparency_overlap=False
BLADE=mat('Joinery_screw_slots',(.08,.065,.035),.5,.6)


def empty(name,location=(0,0,0),parent=None):
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.location=V(location);o.parent=parent;return o

def finish(o,material,bevel=0,parent=None):
 o.data.materials.append(material)
 if bevel:
  b=o.modifiers.new('Soft handcrafted edge','BEVEL');b.width=bevel;b.segments=3;b.affect='EDGES'
  b.limit_method='ANGLE';b.angle_limit=.25
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=b.name)
 for p in o.data.polygons:p.use_smooth=True
 n=o.modifiers.new('Controlled face normals','WEIGHTED_NORMAL');n.keep_sharp=True;n.weight=50
 bpy.context.view_layer.objects.active=o
 try:bpy.ops.object.modifier_apply(modifier=n.name)
 except RuntimeError:pass
 # Cubic projection supplies consistent metre-scale UVs across bespoke extrusions.
 uv=o.data.uv_layers.new(name='UVMap') if not o.data.uv_layers else o.data.uv_layers.active
 for p in o.data.polygons:
  normal=p.normal;axis=max(range(3),key=lambda i:abs(normal[i]))
  for li in p.loop_indices:
   co=o.data.vertices[o.data.loops[li].vertex_index].co
   coords=(co.y,co.z) if axis==0 else (co.x,co.z) if axis==1 else (co.x,co.y)
   uv.data[li].uv=coords
 if parent:o.parent=parent
 return o

def poly(name,loop,z0,z1,material,bevel=.008,parent=None):
 n=len(loop);verts=[V((x,y,z)) for z in [z0,z1] for x,y in loop]
 faces=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 tri=tessellate_polygon([[Vector((x,y,0)) for x,y in loop]])
 def idx(v):return v if isinstance(v,int) else min(range(n),key=lambda i:(loop[i][0]-v.x)**2+(loop[i][1]-v.y)**2)
 for t in tri:
  ids=tuple(idx(v) for v in t);faces.extend([tuple(reversed(ids)),tuple(i+n for i in ids)])
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);return finish(o,material,bevel,parent)

def ring(name,outer,inner,z0,z1,material,bevel=.006,parent=None):
 n=len(outer);assert n==len(inner)
 verts=[V((x,y,z)) for z in [z0,z1] for arr in [outer,inner] for x,y in arr]
 faces=[]
 for i in range(n):
  j=(i+1)%n
  faces.extend([(i,j,j+2*n,i+2*n),(i+n,i+3*n,j+3*n,j+n),(i,i+n,j+n,j),(i+2*n,j+2*n,j+3*n,i+3*n)])
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);return finish(o,material,bevel,parent)

def arch(w,h,rise,inset=0,segments=64):
 r=w/2-inset;ry=rise-inset;spring=h/2-rise;bottom=-h/2+inset
 return [(-r,bottom),(r,bottom)]+[(r*math.cos(a),spring+ry*math.sin(a)) for a in [i*math.pi/segments for i in range(segments+1)]]

def half(w,h,rise,side,inset=0,segments=48):
 r=w/2-inset;ry=rise-inset;spring=h/2-rise;bottom=-h/2+inset;c=.012+inset
 if side<0:
  a=math.acos(-c/r)
  return [(-r,bottom),(-c,bottom)]+[(r*math.cos(t),spring+ry*math.sin(t)) for t in [a+(math.pi-a)*i/segments for i in range(segments+1)]]
 a=math.acos(c/r)
 return [(c,bottom),(r,bottom)]+[(r*math.cos(t),spring+ry*math.sin(t)) for t in [a*i/segments for i in range(segments+1)]]

def box(name,size,loc,material,bevel=.008,parent=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=V(loc));o=bpy.context.object;o.name=name;o.dimensions=(size[0],size[2],size[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,material,bevel,parent)

def turned(name,profile,loc,material,parent=None,segments=24):
 verts=[]
 for y,r in profile:
  for i in range(segments):
   a=i*2*math.pi/segments;verts.append(V((loc[0]+math.cos(a)*r,loc[1]+y,loc[2]+math.sin(a)*r)))
 faces=[]
 for k in range(len(profile)-1):
  for i in range(segments):faces.append((k*segments+i,k*segments+(i+1)%segments,(k+1)*segments+(i+1)%segments,(k+1)*segments+i))
 faces.extend([tuple(reversed(range(segments))),tuple((len(profile)-1)*segments+i for i in range(segments))])
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);return finish(o,material,0,parent)

def tube(name,points,r,material,parent=None):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=8;c.bevel_depth=r;c.bevel_resolution=4
 s=c.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
 for p,co in zip(s.bezier_points,points):p.co=V(co);p.handle_left_type=p.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.data.materials.append(material);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o=bpy.context.object;o.select_set(False)
 for p in o.data.polygons:p.use_smooth=True
 if parent:o.parent=parent
 return o

def escutcheon(name,x,y,z,sign,parent,facing=1):
 # Three-dimensional backplate, swept loop pull, turned ends, visible fasteners.
 box(name+'_plate',(.07,.26,.018),(x,y,z),BRASS,.025,parent)
 tube(name+'_pull',[(x,y-.08,z+facing*.016),(x+sign*.015,y-.06,z+facing*.07),(x+sign*.024,y+.06,z+facing*.07),(x,y+.08,z+facing*.016)],.016,BRASS,parent)
 for dy in [-.106,.106]:
  bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1,location=V((x,y+dy,z+facing*.014)))
  o=bpy.context.object;o.name=name+'_screw';o.scale=(.012,.006,.012);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,BRASS,0,parent)
  box(name+'_slot',(.014,.003,.002),(x,y+dy,z+facing*.021),BLADE,.0008,parent)

def panel(name,w,h,center,material,parent):
 x,y,z=center
 box(name+'_rebate',(w,h,.036),(x,y,z),DARK,.025,parent)
 box(name+'_field',(w-.075,h-.075,.033),(x,y,z+.028),material,.04,parent)
 for dz,ww,hh,th in [(0,w,h,.022),(.021,w-.048,h-.048,.014)]:
  outer=[(x-ww/2,y-hh/2),(x+ww/2,y-hh/2),(x+ww/2,y+hh/2),(x-ww/2,y+hh/2)]
  inner=[(x-ww/2+th,y-hh/2+th),(x+ww/2-th,y-hh/2+th),(x+ww/2-th,y+hh/2-th),(x-ww/2+th,y+hh/2-th)]
  ring(name+'_raised_moulding',outer,inner,z+dz,z+.025+dz,material,.005,parent)

def consolidate(root):
 # Keep each pivot's subtree separate. Meshes share one draw per material in each subtree.
 def visit(parent):
  children=list(parent.children)
  for child in children:
   if child.type=='EMPTY':visit(child)
  groups={}
  for child in list(parent.children):
   if child.type=='MESH':groups.setdefault(child.data.materials[0].name if child.data.materials else 'none',[]).append(child)
  for material,objects in groups.items():
   bpy.ops.object.select_all(action='DESELECT')
   for o in objects:o.select_set(True)
   bpy.context.view_layer.objects.active=objects[0]
   if len(objects)>1:bpy.ops.object.join()
   o=bpy.context.object;o.name=parent.name+'__'+material;o.select_set(False)
 visit(root)

def export(root,path):
 consolidate(root);bpy.ops.object.select_all(action='DESELECT')
 root.select_set(True)
 for o in root.children_recursive:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_image_format='JPEG',export_jpeg_quality=88,export_normals=True,export_texcoords=True,export_cameras=False,export_lights=False)
 # The Blender exporter does not retain a MixRGB tint multiplier. Keep the authored
 # paint/wood factor in the glTF PBR field; texture data and UVs remain unchanged.
 raw=path.read_bytes();json_size=struct.unpack_from('<I',raw,12)[0]
 document=json.loads(raw[20:20+json_size]);binary_chunks=raw[20+json_size:]
 for material in document.get('materials',[]):
  source=bpy.data.materials.get(material['name'])
  if source:
   factor=list(source.diffuse_color)
   factor[3]=source.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value
   material.setdefault('pbrMetallicRoughness',{})['baseColorFactor']=factor
 data=json.dumps(document,separators=(',',':')).encode();data+=b' '*((-len(data))%4)
 path.write_bytes(struct.pack('<4sII',b'glTF',2,20+len(data)+len(binary_chunks))+struct.pack('<I4s',len(data),b'JSON')+data+binary_chunks)
 # Delete only this asset hierarchy, preserve materials and images for subsequent files.
 for o in list(root.children_recursive):bpy.data.objects.remove(o,do_unlink=True)
 bpy.data.objects.remove(root,do_unlink=True)

def window(room):
 w,h,rise=room['width'],room['height'],room['arch'];kind=room['kind']
 timber=BRONZE if kind=='sunroom' else GREEN if kind in ['library','music'] else SAGE if kind=='bedroom' else OAK if kind=='art' else WOOD
 root=empty(room['id']);static=empty('frame',parent=root)
 # Three continuous moulding stages, rather than pasted rectangular stiles.
 ring('arch_frame_rebate',arch(w,h,rise,.018),arch(w,h,rise,.102),-.14,.075,timber,.01,static)
 ring('arch_frame_bead',arch(w,h,rise,.027),arch(w,h,rise,.052),.064,.118,timber,.006,static)
 ring('arch_frame_inner_stop',arch(w,h,rise,.089),arch(w,h,rise,.112),-.12,-.075,DARK,.006,static)
 box('sill_rounded_timber',(w-.02,.07,.31),(0,-h/2+.025,-.005),timber,.018,static)
 # Leaves are offset from aperture by the frame thickness, with a true central closing gap.
 sw,sh,sr=w-.205,h-.205,rise-.1025;inward=room['hinge']=='inward';hz=-.13 if inward else .17
 for side,label in [(-1,'left'),(1,'right')]:
  px=side*sw/2
  hinge=empty('hinge_'+label,(px,0,hz),root)
  local=lambda arr:[(x-px,y) for x,y in arr]
  outer=half(sw,sh,sr,side);inner=half(sw,sh,sr,side,.063)
  ring('arched_sash_stiles',local(outer),local(inner),-.05,.046,timber,.008,hinge)
  ring('glazing_bead',local(half(sw,sh,sr,side,.05)),local(half(sw,sh,sr,side,.073)),.038,.064,timber,.004,hinge)
  glass=poly('clear_glazing',local(half(sw,sh,sr,side,.077)),-.015,-.007,GLASS,0,hinge)
  # Each pane retains narrow profile bars without overwhelming the interior view.
  mid=-side*sw/4;leafW=sw/2-.09;bottom=-sh/2;spring=sh/2-sr
  railY=bottom+(.48 if kind=='sunroom' else .66)
  box('meeting_rail',(leafW,.045,.075),(mid,railY,.016),timber,.006,hinge)
  if kind not in ['living','bedroom']:
   muntin_top=spring+(sr-.08)*math.sqrt(max(0,1-((px+mid)/(sw/2-.08))**2))
   box('slender_vertical_muntin',(.028,max(.2,muntin_top-railY),.055),(mid,(muntin_top+railY)/2,.014),timber,.004,hinge)
  if kind in ['kitchen','workshop','sunroom']:
   box('cross_muntin',(leafW,.028,.055),(mid,(railY+spring)/2,.014),timber,.004,hinge)
  if kind!='sunroom':panel('fielded_lower_panel',leafW-.04,.48,(mid,bottom+.32,.025),timber,hinge)
  # Weather strip and shaped meeting stile increase close-up construction detail.
  meeting=-px-side*.025
  box('meeting_astragal',(.035,sh-.1,.075),(meeting,-.01,.028),timber,.009,hinge)
  escutcheon('handle',meeting-side*.095,bottom+.91,.073,-side,hinge)
  # Back handle is useful from inside the balcony opening.
  if inward:escutcheon('inside_handle',meeting-side*.095,bottom+.91,-.075,side,hinge,-1)
  ys=[bottom+.22,min(spring-.13,bottom+1.25)]
  for j,y in enumerate(ys):
   # Barrel follows parent pivot; turned end caps and knuckles remain rigid to the sash.
   turned('barrel_hinge',[(0,.024),(.014,.03),(.032,.024),(.062,.027),(.095,.024),(.125,.03),(.139,.024)],(0,y,0),BRASS,hinge)
   box('hinge_leaf',(.09,.105,.012),(-side*.048,y+.07,.005),BRASS,.007,hinge)
   box('fixed_hinge_leaf',(.075,.1,.014),(px+side*.035,y+.07,hz-.012),BRASS,.006,static)
 export(root,OUT/f"{room['id']}.glb")

def about(door,index):
 w,h,rise=door['width'],door['height'],door['arch'];root=empty('about-'+('back' if door['back'] else 'front'));static=empty('frame',parent=root)
 ring('arched_oak_lining',arch(w,h,rise,.015),arch(w,h,rise,.075),-.14,.1,WOOD,.012,static)
 ring('fine_architrave_bead',arch(w,h,rise,.02),arch(w,h,rise,.04),.09,.13,OAK,.006,static)
 sw,sh,sr=w-.16,h-.16,rise-.08;px=-sw/2;hinge=empty('hinge_left',(px,0,.17),root)
 poly('arched_walnut_door',[(x-px,y) for x,y in arch(sw,sh,sr)],-.055,.055,WOOD,.012,hinge)
 for y,hh in [(-.64,.59),(.03,.56)]:panel('raised_door_panel',sw-.16,hh,(-px,y,.06),OAK,hinge)
 # Arched transom relief contains actual glazing and slender radial bars.
 fanY=sh/2-sr+.02;fanW=sw-.18
 loop=[(-fanW/2+(-px),fanY),(fanW/2+(-px),fanY)]+[(fanW/2*math.cos(a)-px,fanY+(sr-.11)*math.sin(a)) for a in [i*math.pi/48 for i in range(49)]]
 poly('transom_dark_recess',loop,.06,.074,DARK,.004,hinge)
 poly('transom_glazing',loop,.075,.082,GLASS,0,hinge)
 for a in [math.pi*.25,math.pi*.5,math.pi*.75]:
  tube('fanlight_muntin',[(-px,fanY,.095),(math.cos(a)*fanW/2-px,fanY+math.sin(a)*(sr-.11),.095)],.013,BRASS,hinge)
 escutcheon('entrance_handle',sw-.105,-.15,.08,-1,hinge)
 panel('letter_slot_plate',.29,.075,(-px,.34,.08),BRASS,hinge)
 box('letter_slot_shadow',(.22,.018,.006),(-px,.34,.119),DARK,.006,hinge)
 for y in [-.87,-.08,.65]:turned('entrance_barrel',[(0,.026),(.014,.033),(.06,.028),(.13,.033),(.148,.026)],(0,y,0),BRASS,hinge)
 export(root,OUT/(('about-back' if door['back'] else 'about-front')+'.glb'))

for room in LAYOUT['rooms']:window(room)
for index,door in enumerate(LAYOUT['aboutDoors']):about(door,index)
print('EXPORTED',len(list(OUT.glob('*.glb'))),'joinery assets')
