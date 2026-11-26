"""Original V03 fitted interiors. Run: blender -b --python scripts/environment/build_interiors_east.py
Coordinates exposed by helpers are runtime X / Y-up / Z-front. GLBs are floor-centred,
with an entrance plane at Z=0 and no exterior facade or animated entrance leaves.
Third-party component sources are documented in ASSET_CREDITS.md.
"""
import bpy, math, json, random, sys, os
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'public/assets/interiors';OUT.mkdir(parents=True,exist_ok=True)
REVIEW=ROOT.parent/'v03-review/east';REVIEW.mkdir(parents=True,exist_ok=True)
TEXTURES=ROOT/'public/assets/textures'
ASSETS=ROOT/'public/assets/models/v03'
LAYOUT=json.loads((ROOT/'scripts/environment/layout.json').read_text())
M={}; DYNAMIC=[]
def xyz(p): return Vector((p[0],-p[2],p[1]))
def rgba(h):
 h=h.lstrip('#');return tuple(((int(h[i:i+2],16)/255+.055)/1.055)**2.4 if int(h[i:i+2],16)/255>.04045 else int(h[i:i+2],16)/255/12.92 for i in (0,2,4))+(1,)
def material(name,color,rough=.65,metal=0,texture=None,emission=0):
 if name in M:return M[name]
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;links=m.node_tree.links;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=rgba(color);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if texture:
  for role,slot in [('color','Base Color'),('roughness','Roughness'),('normal','Normal')]:
   path=TEXTURES/(texture+'-'+role+'.jpg')
   if not path.exists():continue
   tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(path),check_existing=True)
   if role!='color':tex.image.colorspace_settings.name='Non-Color'
   if role=='color':
    mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=rgba(color);links.new(tex.outputs['Color'],mix.inputs[1]);links.new(mix.outputs[0],p.inputs[slot])
   elif role=='normal':
    nm=n.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.18;links.new(tex.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],p.inputs['Normal'])
   else:links.new(tex.outputs['Color'],p.inputs[slot])
 if emission:
  p.inputs['Emission Color'].default_value=rgba(color);p.inputs['Emission Strength'].default_value=emission
 M[name]=m;return m

def matinit():
 global M;M={}
 material('Ivory linen plaster','#e5ddc9',.95,texture='plaster');material('Warm oak','#b18a58',.8,texture='oak');material('Walnut joinery','#6b4931',.7,texture='oak');material('Dark oiled walnut','#342b26',.52,texture='oak');material('Muted brass','#ad915a',.34,.75);material('Bronze hardware','#705338',.42,.75);material('Limestone','#d8ccb3',.85,texture='stone');material('Warm paper','#f3e7cb',.9);material('Charcoal enamel','#292d2b',.32,.15);material('Ink','#1f2a28',.6);material('Linen','#c7baa0',.95,texture='bookcloth');material('Sage painted wood','#65745e',.7,texture='oak');material('Dusty blue paint','#56736f',.72,texture='oak');material('Claret fabric','#695052',.95,texture='bookcloth');material('Cream ceramic','#f4e7cc',.18);material('Copper','#b57849',.36,.7);material('Steel','#9ba7a4',.3,.85);material('Cobalt glaze','#355965',.21);material('Ochre paint','#b29354',.75);material('Rust paint','#a86c4b',.8);material('Olive paint','#728267',.82);material('emissive_warm','#ffcb8a',.5,emission=2.8);material('emissive_neutral','#ffebcb',.5,emission=1.6)

def assign(o,mat):o.data.materials.append(M[mat] if isinstance(mat,str) else mat)
def bevel(o,width=.015,segments=3):
 if width:
  m=o.modifiers.new('Crafted edge radii','BEVEL');m.width=width;m.segments=segments
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name)
 for f in o.data.polygons:f.use_smooth=True
 n=o.modifiers.new('Controlled corner normals','WEIGHTED_NORMAL');n.keep_sharp=True;n.weight=45;bpy.ops.object.modifier_apply(modifier=n.name)
 return o

def box(name,loc,size,mat='Warm oak',radius=.012,rot=(0,0,0)):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(loc));o=bpy.context.object;o.name=name;o.dimensions=(size[0],size[2],size[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);assign(o,mat);bevel(o,min(radius,min(size)*.43),3);o.rotation_euler=(rot[0],-rot[2],rot[1]);return o

def cyl(name,loc,radius,height,mat='Warm oak',vertices=32,top=None,rot=(0,0,0)):
 bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=radius,radius2=radius if top is None else top,depth=height,location=xyz(loc));o=bpy.context.object;o.name=name;assign(o,mat);bevel(o,min(.008,height*.18),2);o.rotation_euler=(rot[0],-rot[2],rot[1]);return o

def ellipsoid(name,loc,scale,mat='Linen',segments=32,rings=20):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=1,location=xyz(loc));o=bpy.context.object;o.name=name;o.scale=(scale[0],scale[2],scale[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);assign(o,mat)
 for f in o.data.polygons:f.use_smooth=True
 return o

def beam(name,a,b,r=.02,mat='Warm oak',round=True):
 va,vb=xyz(a),xyz(b);v=vb-va
 if round:o=cyl(name,tuple((Vector(a)+Vector(b))*.5),r,v.length,mat,24)
 else:o=box(name,tuple((Vector(a)+Vector(b))*.5),(r*2,v.length,r*2),mat,r*.18)
 o.rotation_euler=v.to_track_quat('Z','Y').to_euler();return o

def curve(name,points,r,mat='Muted brass'):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=12;c.bevel_depth=r;c.bevel_resolution=3
 s=c.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
 for p,co in zip(s.bezier_points,points):p.co=xyz(co);p.handle_left_type=p.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);assign(o,mat);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);return o

def lathe(name,loc,profile,mat='Cream ceramic',segments=40):
 verts=[];faces=[]
 for r,y in profile:
  for i in range(segments):
   a=2*math.pi*i/segments;verts.append(tuple(xyz((loc[0]+r*math.cos(a),loc[1]+y,loc[2]+r*math.sin(a)))))
 for j in range(len(profile)-1):
  for i in range(segments):a=j*segments+i;b=j*segments+(i+1)%segments;faces.append((a,b,b+segments,a+segments))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);assign(o,mat)
 for p in mesh.polygons:p.use_smooth=True
 # Cylindrical UV preserves meaningful textile / wood grain orientation when reused.
 uv=mesh.uv_layers.new()
 for poly in mesh.polygons:
  for li in poly.loop_indices:
   v=mesh.loops[li].vertex_index;uv.data[li].uv=((v%segments)/segments,(v//segments)/max(1,len(profile)-1))
 return o

def torus(name,loc,major,minor,mat='Muted brass',rot=(0,0,0)):
 bpy.ops.mesh.primitive_torus_add(major_segments=40,minor_segments=8,location=xyz(loc),major_radius=major,minor_radius=minor);o=bpy.context.object;o.name=name;assign(o,mat);o.rotation_euler=(rot[0],-rot[2],rot[1])
 for f in o.data.polygons:f.use_smooth=True
 return o

def frame(name,center,w,h,mat='Walnut joinery',depth=.06,border=.045):
 x,y,z=center
 box(name+' backing',(x,y,z),(w,h,.025),'Linen',.005)
 for s in [-1,1]:box(name+' vertical',(x+s*(w/2-border/2),y,z+.035),(border,h,depth),mat,.009);box(name+' horizontal',(x,y+s*(h/2-border/2),z+.035),(w-2*border,border,depth),mat,.009)

def handle(name,x,y,z,w=.12):
 for s in [-1,1]:beam(name+' bracket',(x+s*w*.5,y,z),(x+s*w*.5,y,z+.035),.012,'Muted brass')
 beam(name+' pull',(x-w*.5,y,z+.04),(x+w*.5,y,z+.04),.013,'Muted brass')

def drawer(name,x,y,z,w,h,mat='Warm oak'):
 box(name+' face',(x,y,z),(w,h,.055),mat,.013)
 box(name+' recessed panel',(x,y,z+.032),(w-.06,h-.055,.012),mat,.008)
 handle(name,x,y,z+.05,min(.13,w*.35))

def cup(name,loc,mat='Cream ceramic'):
 x,y,z=loc
 lathe(name+' saucer',(x,y,z),[(0,0),(.095,0),(.105,.009),(.092,.017),(0,.013)],mat)
 lathe(name,(x,y+.018,z),[(.035,0),(.055,.015),(.065,.1),(.061,.112),(.053,.105),(.045,.025)],mat)
 torus(name+' handle',(x+.073,y+.078,z),.031,.008,mat,(math.pi/2,0,0))
 cyl(name+' tea',(x,y+.113,z),.052,.004,'Walnut joinery',32)

def book(name,loc,size,mat='Sage painted wood',yaw=0):
 x,y,z=loc;w,h,d=size
 box(name+' cover',(x,y,z),(w,h,d),mat,.006,rot=(0,yaw,0));box(name+' pages',(x,y,z+.007),(w-.025,h-.024,d-.02),'Warm paper',.003,rot=(0,yaw,0))

def import_asset(name,loc,height,yaw=0):
 path=ASSETS/(name+'.glb')
 if not path.exists():print('MISSING_OPTIONAL_ASSET',path,flush=True);return []
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(path));obs=[o for o in bpy.context.scene.objects if o not in before]
 roots=[o for o in obs if o.parent not in obs]
 parent=bpy.data.objects.new('Imported '+name,None);bpy.context.collection.objects.link(parent);parent.location=xyz(loc);parent.scale=(height,height,height);parent.rotation_euler[2]=yaw
 for o in roots:o.parent=parent
 return obs

def shell(kind,w,d,h):
 accent={'art':'Linen','kitchen':'Sage painted wood','music':'Claret fabric','workshop':'Dusty blue paint'}[kind]
 # Planked boards with bevelled seams and varied single-family grain.
 count=math.ceil(w/.18)
 for i in range(count):
  x=-w/2+(i+.5)*w/count
  box('Oak floorboard %02d'%i,(x,-.025,-d/2),(w/count-.006,.05,d),'Warm oak',.004)
 box('Back plaster',(0,h/2,-d-.035),(w+.08,h,.07),'Ivory linen plaster',.012)
 for side in [-1,1]:
  box('Side plaster',(side*(w/2+.035),h/2,-d/2),(.07,h,d),'Ivory linen plaster',.01)
  box('Side skirting',(side*(w/2-.023),.1,-(d+.03)/2),(.055,.19,d-.03),'Walnut joinery',.006)
  box('Side cornice',(side*(w/2-.028),h-.065,-(d+.03)/2),(.08,.08,d-.03),'Limestone',.012)
  box('Side wainscot',(side*(w/2-.012),.47,-(d+.03)/2),(.04,.64,d-.03),accent,.005)
  box('Side chair rail',(side*(w/2-.04),.81,-(d+.03)/2),(.065,.045,d-.03),'Warm oak',.008)
 box('Back wainscot',(0,.47,-d+.012),(w,.64,.045),accent,.005)
 box('Back skirting',(0,.1,-d+.028),(w,.19,.065),'Walnut joinery',.005)
 box('Back chair rail',(0,.81,-d+.04),(w,.045,.07),'Warm oak',.008)
 box('Plaster ceiling',(0,h+.035,-d/2),(w+.14,.07,d),'Ivory linen plaster',.008)
 box('Back crown cornice',(0,h-.065,-d+.04),(w,.09,.1),'Limestone',.015)
 # Visible coffered ceiling joinery, no floating ornament.
 beam_front=1.72 if kind=='art' else 0
 for x in [-w*.32,w*.32]:box('Ceiling timber',(x,h-.09,-(d+beam_front)/2),(.065,.1,d-beam_front),'Warm oak',.012)


def pendant(name,loc,shade='Cream ceramic',neutral=False):
 x,y,z=loc
 cyl(name+' ceiling rose',(x,2.63,z),.065,.035,'Muted brass')
 beam(name+' suspension',(x,2.61,z),(x,y+.18,z),.009,'Bronze hardware')
 lathe(name+' curved shade',(x,y,z),[(.045,.16),(.065,.13),(.11,.075),(.19,.005),(.2,-.015),(.18,-.032),(.16,-.005)],shade)
 ellipsoid(name+' luminous bulb',(x,y-.015,z),(.06,.06,.06),'emissive_neutral' if neutral else 'emissive_warm',24,12)


def art_room(w,d,h):
 shell('art',w,d,h)
 # Built-in flat-file cabinet: deep drawers, label holders and carved plinth.
 cx=-1.13;cz=-2.18
 box('Flat file carcass',(cx,.5,cz),(.82,1.0,.59),'Walnut joinery',.024)
 box('Flat file crown',(cx,1.02,cz),(.88,.08,.66),'Warm oak',.022)
 for i in range(6):
  y=.17+i*.145;drawer('Paper drawer %d'%i,cx,y,cz+.325,.74,.126,'Warm oak')
  box('Drawer label holder',(cx,y,cz+.369),(.15,.035,.009),'Muted brass',.003)
  box('Handwritten label',(cx,y,cz+.375),(.125,.021,.003),'Warm paper',.001)
 # Slanted drawing desk, H-frame construction and broad white sheet.
 x=-.08;z=-1.89
 for sx in [-1,1]:
  beam('Drawing desk trestle front',(x+sx*.49,.04,z+.26),(x+sx*.45,.91,z+.16),.032,'Walnut joinery',False)
  beam('Drawing desk trestle rear',(x+sx*.49,.04,z-.23),(x+sx*.45,.91,z-.12),.032,'Walnut joinery',False)
  beam('Trestle foot',(x+sx*.49,.055,z-.31),(x+sx*.49,.055,z+.33),.045,'Walnut joinery',False)
 beam('Desk low stretcher',(x-.49,.2,z),(x+.49,.2,z),.028,'Walnut joinery',False)
 box('Tilted drawing board',(x,.97,z),(1.18,.065,.7),'Warm oak',.018,rot=(.20,0,0))
 box('Drawing paper',(x-.06,1.014,z),( .78,.009,.49),'Warm paper',.008,rot=(.20,0,0))
 for off in [-.18,0,.18]:beam('Pencil architectural marks',(x-.32+off,1.038,z-.18),(x-.12+off,1.002,z+.13),.0028,'Dusty blue paint')
 beam('Drawing pencil',(x+.43,1.03,z-.13),(x+.43,1.0,z+.14),.006,'Ochre paint')
 # A-frame easel with a painting of abstract countryside, not a duplicate desk graphic.
 ex=.93;ez=-1.94
 for side in [-1,1]:beam('Easel front leg',(ex+side*.3,.02,ez+.18),(ex+side*.14,1.85,ez-.03),.025,'Warm oak',False)
 beam('Easel rear leg',(ex,.02,ez-.34),(ex,1.72,ez-.03),.025,'Walnut joinery',False)
 box('Easel tray',(ex,.83,ez+.11),(.8,.055,.16),'Warm oak',.01)
 frame('Stretched canvas',(ex,1.28,ez+.04),.68,.85,'Warm oak',.045,.035)
 box('Canvas ground',(ex,1.28,ez+.083),(.59,.76,.009),'Linen',.003)
 # Crafted torn-paper style geometric pigment shapes, shallow but genuine canvas relief.
 box('Landscape sky',(ex,1.43,ez+.092),(.53,.36,.005),'Cobalt glaze',.002)
 ellipsoid('Painted sun',(ex+.13,1.48,ez+.1),(.07,.07,.003),'Ochre paint',24,12)
 box('Landscape meadow',(ex,1.13,ez+.095),(.53,.23,.006),'Olive paint',.002)
 beam('Painted stem',(ex-.1,1.12,ez+.103),(ex-.04,1.48,ez+.103),.01,'Rust paint',False)
 # A painter's kidney palette and small pigment daubs sit at the desk edge.
 palette=ellipsoid('Maple paint palette',(.33,1.035,-1.98),(.135,.009,.19),'Warm oak',32,12);palette.rotation_euler[0]=.2
 for px,pz,col in [(.27,-2.06,'Rust paint'),(.35,-2.1,'Ochre paint'),(.42,-2.05,'Cobalt glaze'),(.43,-1.94,'Olive paint')]:
  ellipsoid('Paint daub',(px,1.047+.2*(-1.98-pz),pz),(.024,.005,.022),col,16,8)
 # Hanging works and material swatches occupy only the rear wall, leaving the inward door sweep sectors clear.
 for i,(xx,yy,ww,hh) in enumerate([(-.96,1.77,.57,.61),(-.34,1.92,.4,.47),(.14,2.04,.42,.43)]):
  frame('Pinned studio work %d'%i,(xx,yy,-d+.07),ww,hh,'Warm oak',.04,.026)
  box('Studio print %d'%i,(xx,yy,-d+.102),(ww-.09,hh-.09,.004),['Linen','Dusty blue paint','Rust paint'][i],.001)
 # Original botanical studies: slender stems and textured leaves drawn in relief.
 for xx,yy,sc in [(-.96,1.77,1),(-.34,1.92,.68)]:
  zz=-d+.116
  curve('Botanical ink stem',[(xx-.02,yy-.21*sc,zz),(xx-.035,yy,zz),(xx+.035,yy+.2*sc,zz)],.003,'Walnut joinery')
  for k in range(5):
   side=-1 if k%2 else 1;ly=yy+(-.13+k*.065)*sc;lx=xx+side*.065*sc
   leaf=ellipsoid('Pressed botanical leaf',(lx,ly,zz+.004),(.065*sc,.018*sc,.0035),'Olive paint',24,12);leaf.rotation_euler[1]=side*.55
  ellipsoid('Botanical flower',(xx+.035,yy+.18*sc,zz+.007),(.025*sc,.025*sc,.003),'Ochre paint',20,12)
 for i,mat in enumerate(['Rust paint','Cobalt glaze','Olive paint','Ochre paint']):
  cyl('Pigment jar',(cx-.31+i*.2,1.12,cz+.06),.055,.15,mat,24)
  cyl('Jar lid',(cx-.31+i*.2,1.205,cz+.06),.058,.025,'Muted brass',24)
 lathe('Brush pot',(cx+.18,1.06,cz-.17),[(.07,0),(.085,.18),(.08,.19),(.066,.18),(.055,.02)],'Cream ceramic')
 for i in range(5):beam('Brush handle',(cx+.18+i*.018-.04,1.1,cz-.17),(cx+.17+i*.024-.04,1.49,cz-.17+.015*math.sin(i)),.006,'Walnut joinery')
 import_asset('articulated-desk-lamp',(-1.14,1.01725,-2.24),.57,.2)
 pendant('Studio enamel pendant',(.15,2.2,-1.5),'Cream ceramic',True)
 return [{'position':[.15,2.17,-1.5],'color':'#ffe6c3','intensity':3.0,'distance':4.8},{'position':[-1.15565,1.51764,-2.35869],'color':'#ffedce','intensity':.8,'distance':2.3}]


def shaker_door(name,x,y,z,w,h,mat='Sage painted wood'):
 box(name+' panel',(x,y,z),(w,h,.065),mat,.014)
 for side in [-1,1]:
  box(name+' stile',(x+side*(w/2-.035),y,z+.04),(.06,h,.03),mat,.008)
  box(name+' rail',(x,y+side*(h/2-.035),z+.04),(w-.13,.06,.03),mat,.008)
 cyl(name+' knob',(x+w*.31,y+h*.2,z+.092),.023,.04,'Muted brass',24,rot=(math.pi/2,0,0))

def bowl(name,loc,r=.14,mat='Cream ceramic'):
 return lathe(name,loc,[(.055,0),(r*.75,.035),(r,.11),(r,.125),(r-.015,.125),(r-.02,.11),(.06,.015)],mat)


def kitchen_room(w,d,h):
 shell('kitchen',w,d,h)
 # Cream-and-olive checker limestone floor, restrained material variation.
 tile=.24
 for ix in range(12):
  for iz in range(11):
   x=-w/2+(ix+.5)*w/12;z=-(iz+.5)*d/11
   box('Honed floor tile',(x,.006,z),(w/12-.007,.012,d/11-.007),'Limestone' if (ix+iz)%2 else 'Linen',.003)
 # Fitted rear cabinetry with a genuine sink bowl and appliance void.
 for x in [-1.02,-.42,.18]:
  box('Kitchen base carcass',(x,.45,-2.3),(.58,.86,.63),'Sage painted wood',.019)
  shaker_door('Kitchen base door',x,.43,-1.957,.53,.72)
  box('Cabinet toe plinth',(x,.065,-2.14),(.57,.12,.36),'Walnut joinery',.01)
 box('Sink countertop left',(-1.12,.915,-2.28),(.4,.075,.7),'Limestone',.018)
 box('Countertop middle',(-.36,.915,-2.28),(.42,.075,.7),'Limestone',.018)
 box('Countertop end',(.2,.915,-2.28),(.62,.075,.7),'Limestone',.018)
 # Sink opening as a tapered inset basin rather than a solid rectangle.
 sx=-.78;sz=-2.27
 box('Apron ceramic sink front',(sx,.82,sz+.29),(.6,.22,.075),'Cream ceramic',.025)
 box('Sink bottom',(sx,.77,sz),(.46,.035,.4),'Cream ceramic',.025)
 for side in [-1,1]:
  box('Sink side',(sx+side*.27,.845,sz),(.05,.17,.51),'Cream ceramic',.02)
  box('Sink rim front rear',(sx,.92,sz+side*.26),(.59,.045,.055),'Cream ceramic',.017)
 box('Sink rear',(sx,.845,sz-.245),(.51,.17,.04),'Cream ceramic',.015)
 cyl('Sink drain',(sx,.792,sz),.038,.007,'Steel',32)
 curve('Gooseneck brass faucet',[(sx, .95,sz-.27),(sx,1.18,sz-.27),(sx,1.31,sz-.17),(sx,1.26,sz-.03)],.018,'Muted brass')
 for x in [sx-.14,sx+.14]:cyl('Tap control',(x,.98,sz-.27),.027,.06,'Muted brass',24)
 # Professional imported stove fills the right appliance bay.
 imported=import_asset('electric-stove',(.94,.02,-2.25),.89,0)
 if not imported:
  box('Cooker enamel chassis',(.94,.47,-2.25),(.67,.89,.66),'Cream ceramic',.026)
  box('Oven dark aperture',(.94,.42,-1.9),(.53,.4,.035),'Charcoal enamel',.025)
  box('Oven glass',(.94,.42,-1.878),(.43,.29,.012),'Ink',.015)
  handle('Oven handle',.94,.69,-1.87,.46)
  for xx in [.76,1.1]:
   for zz in [-2.08,-2.4]:torus('Stove burner',(xx,.925,zz),.085,.012,'Charcoal enamel')
 # Small bevelled backsplash tiles articulate the fitted zone.
 for row in range(5):
  for col in range(17):box('Glazed backsplash tile',(-1.38+(col+.5)*2.76/17,1.02+row*.14,-d+.052),(2.76/17-.006,.134,.022),'Cream ceramic',.007)
 for x in [-1.0,.95]:
  box('Upper cabinet',(x,2.05,-2.42),(.68,.74,.37),'Sage painted wood',.02)
  shaker_door('Upper cabinet door',x,2.05,-2.22,.62,.68)
 for y in [1.72,2.11]:
  box('Open plate shelf',(-.02,y,-2.37),(1.13,.055,.44),'Warm oak',.012)
  for s in [-1,1]:beam('Shelf brass bracket',(-.02+s*.42,y-.15,-2.57),(-.02+s*.42,y-.02,-2.21),.012,'Muted brass')
 for i in range(4):
  bowl('Stacked ceramic bowl',(-.28,1.76+i*.035,-2.37),.13,'Cream ceramic')
 for i in range(3):cup('Kitchen mug %d'%i,(.14+i*.2,2.14,-2.34),['Cream ceramic','Cobalt glaze','Cream ceramic'][i])
 box('Shelf concealed light',(-.02,1.686,-2.23),(.85,.012,.022),'emissive_neutral',.003)
 import_asset('electric-kettle',(.15,.96,-2.3),.24,0)
 # A preparation island with an inset drawer, turned feet and distinct culinary focal point.
 x=-.28;z=-.9
 box('Preparation island top',(x,.84,z),(1.08,.075,.6),'Warm oak',.024)
 for sx in [-1,1]:
  for sz in [-1,1]:
   lx=x+sx*.42;lz=z+sz*.22
   lathe('Turned island leg',(lx,.02,lz),[(.04,0),(.04,.08),(.03,.1),(.03,.58),(.05,.65),(.045,.78)],'Warm oak',24)
 box('Island lower shelf',(x,.2,z),(.96,.045,.52),'Warm oak',.01)
 drawer('Island drawer',x,.71,z+.29,.91,.18,'Sage painted wood')
 bowl('Fruit bowl',(x-.15,.89,z),.19,'Cobalt glaze')
 for i in range(4):ellipsoid('Golden pear',(x-.24+i*.06,.98+(.02 if i%2 else 0),z+.04*math.sin(i)),(.045,.065,.043),'Ochre paint',20,12)
 book('Recipe notebook',(x+.32,.9,z+.02),(.21,.04,.26),'Rust paint',-.17)
 # Linen towel with a physically modelled hanging fold.
 verts=[];faces=[]
 for j in range(16):
  t=j/15
  for i in range(12):
   u=i/11;verts.append(tuple(xyz((x-.39+u*.3,.8-t*.37,z+.335+.009*math.sin(u*math.pi*6)))))
 for j in range(15):
  for i in range(11):a=j*12+i;faces.append((a,a+1,a+13,a+12))
 me=bpy.data.meshes.new('Linen towel');me.from_pydata(verts,[],faces);o=bpy.data.objects.new('Linen towel',me);bpy.context.collection.objects.link(o);assign(o,'Linen')
 sol=o.modifiers.new('Textile thickness','SOLIDIFY');sol.thickness=.003
 pendant('Kitchen pendant',(-.2,2.23,-1.15),'Cream ceramic',True)
 return [{'position':[-.2,2.17,-1.15],'color':'#ffe4ba','intensity':3.0,'distance':4.6},{'position':[0,1.65,-2.25],'color':'#ffefcd','intensity':1.1,'distance':2.3}]


def piano(w=1.8,x=-.35,z=-2.12):
 # Upright piano: framed panel, curved fallboard, sloped music rest and 88-key layout.
 box('Upright piano main case',(x,.8,z),(w,1.45,.5),'Dark oiled walnut',.04)
 box('Piano top cap',(x,1.55,z-.02),(w+.09,.08,.58),'Dark oiled walnut',.03)
 box('Piano lower inset',(x,.35,z+.265),(w-.18,.52,.045),'Walnut joinery',.025)
 for s in [-1,1]:
  box('Piano pilaster',(x+s*(w/2-.06),.78,z+.285),(.09,1.37,.09),'Walnut joinery',.018)
  lathe('Piano turned front leg',(x+s*(w/2-.13),.04,z+.55),[(.05,0),(.055,.06),(.036,.1),(.032,.43),(.06,.48),(.05,.6)],'Dark oiled walnut',24)
 box('Piano keybed',(x,.7,z+.5),(w,.12,.53),'Dark oiled walnut',.024)
 kw=(w-.24)/52
 for i in range(52):
  xx=x-(w-.24)/2+(i+.5)*kw
  box('Ivory piano key %02d'%i,(xx,.783,z+.57),(kw-.0018,.027,.35),'Cream ceramic',.003)
  if i%7 not in [2,6] and i<51:box('Ebony piano key %02d'%i,(xx+kw*.5,.81,z+.46),(kw*.58,.032,.2),'Ink',.003)
 box('Piano fallboard',(x,.9,z+.28),(w-.14,.12,.12),'Dark oiled walnut',.025)
 box('Brass piano maker plaque',(x,1.06,z+.273),(.28,.045,.01),'Muted brass',.003)
 box('Angled piano music desk',(x,1.17,z+.37),(1.0,.38,.028),'Walnut joinery',.012,rot=(-.22,0,0))
 for side in [-1,1]:
  box('Sheet music page',(x+side*.215,1.18,z+.396),(.39,.32,.005),'Warm paper',.003,rot=(-.22,0,side*.015))
  for row in range(5):
   for line in range(5):box('Staff line',(x+side*.215,1.3-row*.055-line*.004,z+.412),(.33,.0012,.002),'Ink',.0003)
 for i in [-1,0,1]:
  beam('Piano pedal stem',(x+i*.11,.16,z+.3),(x+i*.11,.11,z+.65),.014,'Muted brass')
  ellipsoid('Piano brass pedal',(x+i*.11,.1,z+.65),(.033,.018,.067),'Muted brass',20,12)
 # Deep stitched leather bench with rounded edge and shallow tufting.
 box('Piano bench seat',(x,.47,z+1.1),(1.04,.15,.4),'Claret fabric',.055)
 for sx in [-1,1]:
  for sz in [-1,1]:lathe('Piano bench leg',(x+sx*.42,.02,z+1.1+sz*.12),[(.03,0),(.04,.05),(.025,.11),(.025,.36),(.04,.39)],'Dark oiled walnut',24)
 for i in range(7):ellipsoid('Bench covered button',(x-.42+i*.14,.546,z+1.1),(.018,.006,.018),'Claret fabric',16,8)


def music_room(w,d,h):
 shell('music',w,d,h)
 piano(1.8,-.38,-2.12)
 # Record console is a different silhouette to any other room's furniture.
 cx=.99;cz=-.95
 box('Record console body',(cx,.53,cz),(.62,.55,.75),'Walnut joinery',.026)
 box('Record console top',(cx,.83,cz),(.69,.07,.79),'Dark oiled walnut',.025)
 for sx in [-1,1]:
  for sz in [-1,1]:lathe('Record console tapered foot',(cx+sx*.23,.02,cz+sz*.29),[(.02,0),(.032,.27),(.035,.29)],'Walnut joinery',20)
 # Fluted speaker grille and brass dial on the console front.
 for i in range(12):box('Console grille slat',(cx-.25+i*.045,.52,cz+.388),(.013,.38,.025),'Warm oak',.005)
 cyl('Console tuning dial',(cx+.2,.7,cz+.411),.035,.025,'Muted brass',28,rot=(math.pi/2,0,0))
 box('Turntable plinth',(cx,.9,cz),(.55,.085,.46),'Warm oak',.019)
 platter=cyl('RecordPlatter',(cx-.025,.953,cz),.185,.013,'Ink',64)
 label=cyl('RecordLabel',(cx-.025,.962,cz),.052,.007,'Rust paint',40)
 for o in [platter,label]:DYNAMIC.append(o)
 for r in [.09,.12,.15,.17]:
  o=torus('RecordGroove',(cx-.025,.961,cz),r,.001,'Charcoal enamel');DYNAMIC.append(o)
 beam('Turntable tonearm',(cx+.21,.97,cz-.15),(cx+.075,.977,cz+.115),.011,'Steel')
 box('Turntable cartridge',(cx+.073,.966,cz+.12),(.032,.027,.05),'Ink',.004)
 # Records stored upright in an original slatted crate at the front-left side.
 rx=-1.04;rz=-.48
 for sz in [-1,1]:
  for row in range(3):box('Vinyl crate slat',(rx,.12+row*.12,rz+sz*.2),(.58,.07,.03),'Warm oak',.007)
 for sx in [-1,1]:box('Vinyl crate side',(rx+sx*.285,.24,rz),(.04,.39,.42),'Warm oak',.009)
 for i,mat in enumerate(['Claret fabric','Cobalt glaze','Ochre paint','Sage painted wood','Linen']):
  box('Vinyl sleeve',(rx,.31,rz-.14+i*.062),(.45,.44,.025),mat,.005)
  cyl('Vinyl sleeve artwork',(rx,.31,rz-.124+i*.062),.1,.005,'Ink',40,rot=(math.pi/2,0,0))
 import_asset('boombox',(-.92,1.60,-2.10),.24,0)
 # Offset wall album arrangement adds musical character without bookshelves.
 for i,(x,y) in enumerate([(-.98,2.03),(-.28,2.08),(.48,2.12)]):
  frame('Album frame %d'%i,(x,y,-d+.07),.55,.58,'Warm oak',.05,.035)
  box('Album sleeve artwork',(x,y,-d+.108),(.46,.49,.005),['Cobalt glaze','Claret fabric','Ochre paint'][i],.002)
  cyl('Album disc',(x,y,-d+.117),.13,.008,'Ink',48,rot=(math.pi/2,0,0))
  cyl('Album label',(x,y,-d+.123),.039,.005,'Linen',32,rot=(math.pi/2,0,0))
 # A brass-stem piano lamp places its real light over the score.
 cyl('Piano lamp base',(.1,1.612,-2.10),.08,.038,'Muted brass',32)
 curve('Piano lamp neck',[(.1,1.63,-2.10),(.1,1.85,-2.10),(.1,1.9,-1.88),(.1,1.84,-1.82)],.012,'Muted brass')
 box('Piano lamp curved shade',(.1,1.83,-1.82),(.46,.085,.15),'Sage painted wood',.038)
 box('Piano lamp diffuser',(.1,1.785,-1.82),(.38,.012,.11),'emissive_warm',.005)
 # Milk-glass globe and a warm reading glow.
 beam('Music globe cord',(.77,2.65,-.72),(.77,2.2,-.72),.008,'Bronze hardware')
 ellipsoid('Music opal globe',(.77,2.07,-.72),(.16,.18,.16),'emissive_warm',40,24)
 return [{'position':[.77,2.02,-.72],'color':'#ffd09c','intensity':2.3,'distance':4.0},{'position':[.1,1.76,-1.82],'color':'#ffe1ad','intensity':1.1,'distance':2.7}]


def pegboard(name,center,w,h):
 # Real perforated surface: each aperture is a small circular hole, not painted dots.
 x,y,z=center;nx=20;ny=12;dx=w/nx;dy=h/ny;verts=[];faces=[]
 for row in range(ny):
  for col in range(nx):
   cx=x-w/2+(col+.5)*dx;cy=y-h/2+(row+.5)*dy;start=len(verts)
   for radius in ['outer','inner']:
    for i in range(8):
     a=2*math.pi*i/8
     if radius=='inner':px=cx+.011*math.cos(a);py=cy+.011*math.sin(a)
     else:
      # Square ring parametrisation fills the complete cell while retaining a round opening.
      f=max(abs(math.cos(a)),abs(math.sin(a)));px=cx+(dx/2)*math.cos(a)/f;py=cy+(dy/2)*math.sin(a)/f
     verts.append(tuple(xyz((px,py,z))))
   for i in range(8):faces.append((start+i,start+(i+1)%8,start+8+(i+1)%8,start+8+i))
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);assign(o,'Warm oak')
 sol=o.modifiers.new('Perforated board depth','SOLIDIFY');sol.thickness=.018;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=sol.name)
 return o

def wrench(name,x,y,z,size=.35):
 beam(name+' shaft',(x,y-size*.35,z),(x,y+size*.35,z),.022,'Steel',False)
 for end in [-1,1]:
  torus(name+' ring',(x,y+end*size*.4,z),size*.13,size*.035,'Steel',(math.pi/2,0,0))

def workshop_room(w,d,h):
 shell('workshop',w,d,h)
 bx=0;bz=-2.14
 box('Workbench oak top',(bx,.93,bz),(2.48,.13,.72),'Warm oak',.035)
 for sx in [-1,1]:
  cx=sx*.88
  box('Tool drawer carcass',(cx,.47,bz),(.61,.85,.62),'Dusty blue paint',.02)
  for i in range(4):drawer('Workshop tool drawer',cx,.18+i*.18,bz+.337,.55,.157,'Dusty blue paint')
  box('Cabinet plinth',(cx,.045,bz),(.66,.09,.64),'Walnut joinery',.015)
 box('Workbench lower shelf',(0,.2,bz),(1.2,.06,.59),'Warm oak',.016)
 # Cabinet cubby contents: paper model box, copper spool, mechanical drawings.
 box('Workshop storage box',(-.25,.34,bz),(.46,.24,.47),'Linen',.015)
 box('Box lid',(-.25,.47,bz),(.49,.035,.49),'Warm oak',.008)
 cyl('Copper wire spool',(.34,.37,bz),.16,.26,'Copper',36,rot=(0,0,math.pi/2))
 pegboard('Perforated tool wall',(0,1.74,-d+.09),2.38,1.16)
 for x in [-1.24,1.24]:box('Tool board frame',(x,1.74,-d+.08),(.055,1.23,.09),'Walnut joinery',.012)
 for y in [1.13,2.35]:box('Tool board frame',(0,y,-d+.08),(2.425,.055,.09),'Walnut joinery',.012)
 # Authored hand tools have distinct metal heads, wooden grips and curved handles.
 for i,x in enumerate([-.95,-.65,-.35]):
  wrench('Hanging combination wrench',x,1.8,-d+.18,.28+i*.08)
 for i,x in enumerate([.1,.3,.5]):
  beam('Screwdriver shaft',(x,1.57,-d+.19),(x,2.06,-d+.19),.009,'Steel')
  lathe('Turned screwdriver grip',(x,1.5,-d+.19),[(.025,0),(.038,.04),(.038,.15),(.024,.19)],'Walnut joinery',24)
 beam('Hammer handle',(.86,1.5,-d+.2),(.75,2.08,-d+.2),.025,'Warm oak')
 box('Hammer steel head',(.75,2.08,-d+.2),(.24,.07,.08),'Steel',.015,rot=(0,0,-.2))
 # Small experimental wheeled automaton, mechanical gear assembly as the focal point.
 ax=.12;az=-2.03
 box('Mechanical model base',(ax,1.035,az),(.62,.07,.4),'Walnut joinery',.018)
 for xx in [ax-.2,ax+.2]:
  for zz in [az-.2,az+.2]:
   cyl('Model brass wheel',(xx,1.075,zz),.07,.03,'Muted brass',36,rot=(math.pi/2,0,0))
   cyl('Model wheel hub',(xx,1.075,zz+.02),.025,.035,'Bronze hardware',24,rot=(math.pi/2,0,0))
 box('Model clockwork body',(ax,1.17,az),(.36,.22,.29),'Dusty blue paint',.035)
 # 20 individually beveled gear teeth remain separate from the static room for optional animation.
 gear=cyl('WorkshopGear',(ax,1.38,az+.16),.115,.03,'Muted brass',48,rot=(math.pi/2,0,0));DYNAMIC.append(gear)
 for i in range(16):
  a=i*2*math.pi/16;o=box('WorkshopGearTooth',(ax+.124*math.cos(a),1.38+.124*math.sin(a),az+.16),(.038,.036,.035),'Muted brass',.004,rot=(0,0,a));DYNAMIC.append(o)
 cyl('Automaton clock face',(ax,1.38,az+.184),.068,.007,'Cream ceramic',40,rot=(math.pi/2,0,0))
 beam('Model clock hand',(ax,1.38,az+.19),(ax+.036,1.42,az+.19),.004,'Ink')
 import_asset('bench-vise',(-.89,.941,-1.91),.18,0)
 import_asset('hand-plane',(.76,1.01,-2.08),.13,-.3)
 import_asset('articulated-desk-lamp',(1.02,.9485,-2.28),.62,-.6)
 # Drafting plans and measuring tools occupy a deliberate open patch of work surface.
 box('Mechanism drawing',(-.35,1.003,-1.96),(.42,.008,.31),'Warm paper',.004,rot=(0,.12,0))
 for i in range(3):torus('Blueprint circles',(-.39+i*.1,1.01,-1.96),.035+i*.005,.002,'Dusty blue paint')
 box('Steel ruler',(-.42,1.014,-1.78),(.48,.012,.035),'Steel',.003)
 # Purpose-made round swivelling workshop stool with turned base.
 sx=-.52;sz=-.99
 cyl('Workshop stool seat',(sx,.55,sz),.24,.095,'Warm oak',40)
 cyl('Stool screw spindle',(sx,.37,sz),.026,.3,'Steel',24)
 for i in range(4):
  a=i*math.pi/2;beam('Stool splayed leg',(sx+.08*math.cos(a),.37,sz+.08*math.sin(a)),(sx+.25*math.cos(a),.03,sz+.25*math.sin(a)),.025,'Dusty blue paint')
 pendant('Workshop enamel pendant',(-.4,2.24,-1.05),'Sage painted wood',True)
 return [{'position':[-.4,2.2,-1.05],'color':'#e5eff0','intensity':2.7,'distance':4.3},{'position':[1.10074,1.49279,-2.38214],'color':'#ffe4b4','intensity':1.5,'distance':2.4}]


def merge_static():
 # Apply import transforms, then group all static surfaces by material. Preserve animation names.
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
 for o in meshes:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  for mod in list(o.modifiers):
   try:bpy.ops.object.modifier_apply(modifier=mod.name)
   except:pass
 # Split mixed material meshes first, keeping live record parts apart.
 for o in meshes:
  if o in DYNAMIC or len(o.data.materials)<=1:continue
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.separate(type='MATERIAL');bpy.ops.object.mode_set(mode='OBJECT')
 groups={}
 for o in list(bpy.context.scene.objects):
  if o.type!='MESH' or o in DYNAMIC:continue
  key=o.data.materials[0].name if o.data.materials else 'unassigned';groups.setdefault(key,[]).append(o)
 for name,obs in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in obs:o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();bpy.context.object.name='Surface_'+name.replace(' ','_')
 # Record groove family and gear teeth share exactly one animated node per mechanism.
 for stem,obs in [('RecordPlatter',[o for o in DYNAMIC if o.name.startswith(('RecordPlatter','RecordLabel','RecordGroove'))]),('WorkshopGear',[o for o in DYNAMIC if o.name.startswith('WorkshopGear')])]:
  if not obs:continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in obs:o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=bpy.context.object;o.name=stem
  bpy.context.scene.cursor.location=o.location;bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
  bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 # Delete imported empty hierarchies without disturbing merged meshes.
 for o in list(bpy.context.scene.objects):
  if o.type=='EMPTY' and not o.children:bpy.data.objects.remove(o,do_unlink=True)


def setup_review(kind,lightdata,w,d,h):
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=False
 scene.world=bpy.data.worlds.new('Inspection ambient');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.64,.69,.72,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.35
 scene.render.resolution_x=900;scene.render.resolution_y=850;scene.render.resolution_percentage=100
 scene.render.image_settings.file_format='PNG';scene.render.filepath=str(REVIEW/(kind+'.png'))
 scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=.5
 bpy.ops.object.camera_add(location=xyz((.12,1.63,4.45)));cam=bpy.context.object;cam.name='Inspection camera';direction=xyz((0,1.25,-1.3))-cam.location;cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();cam.data.lens=42;scene.camera=cam
 bpy.ops.object.light_add(type='AREA',location=xyz((0,2.2,2.2)));light=bpy.context.object;light.data.energy=180;light.data.shape='DISK';light.data.size=4;direction=xyz((0,1,-1.5))-light.location;light.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
 for data in lightdata:
  bpy.ops.object.light_add(type='POINT',location=xyz(data['position']));l=bpy.context.object;l.data.energy=data['intensity']*14;l.data.shadow_soft_size=.14;l.data.color=rgba(data['color'])[:3]
 bpy.ops.render.render(write_still=True)


def main():
 records=[]
 selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['art','kitchen','music','workshop']
 if (OUT/'east-layout.json').exists():
  records=[r for r in json.loads((OUT/'east-layout.json').read_text()) if r['kind'] not in selected]
 for kind in selected:
  bpy.ops.wm.read_factory_settings(use_empty=True);DYNAMIC.clear();matinit()
  cfg=next(r for r in LAYOUT['rooms'] if r['kind']==kind);w,d,h=cfg['width'],cfg['depth'],cfg['height']
  lights=globals()[kind+'_room'](w,d,h)
  fixture_names={'art':['Studio enamel pendant bulb','Articulated studio task lamp'],'kitchen':['Kitchen ceramic pendant bulb','Undershelf task strip'],'music':['Opal music globe','Piano score lamp'],'workshop':['Workshop enamel pendant bulb','Articulated workbench task lamp']}
  for light,name in zip(lights,fixture_names[kind]):light['name']=name
  merge_static()
  # Embedded images stay at 512px, except already smaller original derivatives.
  for im in bpy.data.images:
   if max(im.size)>512:
    ratio=512/max(im.size);im.scale(max(1,int(im.size[0]*ratio)),max(1,int(im.size[1]*ratio)))
  bpy.ops.object.select_all(action='DESELECT')
  for o in bpy.context.scene.objects:
   if o.type=='MESH':o.select_set(True)
  path=OUT/(kind+'.glb')
  bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_image_format='JPEG',export_jpeg_quality=84,export_materials='EXPORT',export_texcoords=True,export_normals=True)
  meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];rec={'kind':kind,'file':'/assets/interiors/'+kind+'.glb','bytes':path.stat().st_size,'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes),'drawMeshes':len(meshes),'lights':lights,'dynamicNodes':[o.name for o in meshes if o.name in ['RecordPlatter','WorkshopGear']]}
  metadata=dict(rec,width=w,depth=d,height=h,origin='floor center at entrance, +Y up, interior toward -Z');metadata['file']=kind+'.glb'
  (OUT/(kind+'-metadata.json')).write_text(json.dumps(metadata,indent=2)+'\n')
  records.append(rec);print('ROOM_RESULT',json.dumps(rec),flush=True)
  (OUT/'east-layout.json').write_text(json.dumps(records,indent=2)+'\n')
  setup_review(kind,lights,w,d,h)
 (OUT/'east-layout.json').write_text(json.dumps(records,indent=2)+'\n')
if __name__=='__main__':main()
