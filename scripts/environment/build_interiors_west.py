"""Original V0.3 interior art, modelled and exported with Blender.
Four functionally distinct rooms; runtime positions are +Y up, entrance Z=0.
Run: blender -b --python scripts/environment/build_interiors_west.py -- [room]
Licensed external component provenance remains in ASSET_CREDITS.md.
"""
import bpy, math, json, sys, random, os, re
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'public/assets/interiors'; OUT.mkdir(parents=True,exist_ok=True)
REVIEW=ROOT.parent/'v03-interior-review';REVIEW.mkdir(parents=True,exist_ok=True)
LAYOUT=json.loads((ROOT/'scripts/environment/layout.json').read_text())
ROOMS={r['kind']:r for r in LAYOUT['rooms']}
M={}

def B(p):return Vector((p[0],-p[2],p[1]))
def clear():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for collection in [bpy.data.meshes,bpy.data.curves,bpy.data.materials]:
  for block in list(collection):
   if block.users==0:collection.remove(block)
 M.clear()

def material(name,color,rough=.8,metal=0,texture=None,normal=.12,emission=None):
 if name in M:return M[name]
 m=bpy.data.materials.new(('emissive_'+name) if emission else name);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
 if emission:
  bs.inputs['Emission Color'].default_value=(*emission,1);bs.inputs['Emission Strength'].default_value=.7
 if texture:
  for typ,socket in [('color','Base Color'),('roughness','Roughness'),('normal','Normal')]:
   p=ROOT/f'public/assets/textures/{texture}-{typ}.jpg'
   if not p.exists():continue
   img=bpy.data.images.load(str(p),check_existing=True)
   tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=img
   if typ!='color':img.colorspace_settings.name='Non-Color'
   if typ=='normal':
    nor=m.node_tree.nodes.new('ShaderNodeNormalMap');nor.inputs['Strength'].default_value=normal
    m.node_tree.links.new(tex.outputs['Color'],nor.inputs['Color']);m.node_tree.links.new(nor.outputs['Normal'],bs.inputs[socket])
   elif typ=='color':
    mix=m.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(*color,1)
    m.node_tree.links.new(tex.outputs['Color'],mix.inputs[1]);m.node_tree.links.new(mix.outputs[0],bs.inputs[socket])
   else:m.node_tree.links.new(tex.outputs['Color'],bs.inputs[socket])
 M[name]=m;return m

def palette(kind):
 material('Ivory plaster',(.82,.76,.64),1,texture='plaster')
 material('Warm limestone',(.68,.61,.49),.95,texture='stone')
 material('Oak joinery',(.53,.32,.16),.75,texture='oak')
 material('Walnut',(.24,.12,.063),.77,texture='oak')
 material('Painted cream',(.85,.79,.66),.82)
 material('Muted brass',(.49,.32,.12),.4,.72)
 material('Linen',(.82,.74,.59),.94,texture='bookcloth',normal=.2)
 material('Ivory textile',(.91,.85,.71),1,texture='bookcloth',normal=.18)
 material('Sage textile',(.34,.43,.31),.95,texture='bookcloth',normal=.15)
 material('Terracotta textile',(.57,.32,.22),.96,texture='bookcloth',normal=.14)
 material('Rug braid',(.53,.39,.23),1,texture='bookcloth',normal=.26)
 material('Dark metal',(.055,.06,.055),.5,.58)
 material('Leather',(.25,.12,.07),.72)
 material('Paper',(.89,.82,.66),1,texture='paper')
 material('Ceramic',(.82,.79,.64),.28)
 material('Coffee',(.06,.03,.01),.23)
 material('Candle wax',(.96,.83,.57),.62)
 material('Flame',(.85,.22,.009),.4,emission=(1,.39,.015))
 material('Flame core',(1,.69,.13),.4,emission=(1,.68,.12))
 material('Charred timber',(.045,.024,.012),1,texture='oak')
 material('Lamp glow',(.95,.8,.5),.5,emission=(1,.7,.35))
 material('Library green',(.16,.25,.19),.78,texture='oak')
 material('Bedroom wall',(.53,.59,.48),.96,texture='plaster')
 material('Living wall',(.67,.56,.43),.96,texture='plaster')
 material('Sunroom tile',(.67,.6,.46),.93,texture='stone')
 for i,c in enumerate([(.22,.3,.25),(.47,.25,.14),(.57,.44,.24),(.32,.39,.4),(.63,.56,.39),(.38,.24,.2)]):material(f'Book cloth {i}',c,.95,texture='bookcloth')
 return M

def finish(obj,mat,bevel=0,segments=3,smooth=False):
 if mat:obj.data.materials.append(M[mat] if isinstance(mat,str) else mat)
 if bevel:
  mod=obj.modifiers.new('Soft crafted edges','BEVEL');mod.width=bevel;mod.segments=segments
  mod.limit_method='ANGLE';mod.harden_normals=True
  bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=mod.name)
 if smooth:
  for p in obj.data.polygons:p.use_smooth=True
 if bevel:
  mod=obj.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=40
  try:bpy.ops.object.modifier_apply(modifier=mod.name)
  except RuntimeError:pass
 return obj

def box(name,loc,size,mat='Oak joinery',bevel=.02,rotation=None,segments=3):
 bpy.ops.mesh.primitive_cube_add(size=1,location=B(loc));o=bpy.context.object;o.name=name;o.dimensions=(size[0],size[2],size[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if rotation:o.rotation_euler=(rotation[0],rotation[2],rotation[1])
 return finish(o,mat,min(bevel,min(size)*.44),segments)

def ellipsoid(name,loc,size,mat,rotation=0):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=B(loc));o=bpy.context.object;o.name=name;o.scale=(size[0],size[2],size[1]);o.rotation_euler.z=rotation;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,mat,smooth=True)

def cyl(name,loc,r,h,mat='Muted brass',r2=None,vertices=32):
 bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=r,radius2=r if r2 is None else r2,depth=h,location=B(loc));o=bpy.context.object;o.name=name;return finish(o,mat,min(.008,h/4,r/8),2,True)

def lathe(name,loc,profile,mat='Oak joinery',segments=32):
 verts=[];faces=[]
 for radius,y in profile:
  for i in range(segments):
   a=2*math.pi*i/segments;verts.append(tuple(B((loc[0]+math.cos(a)*radius,loc[1]+y,loc[2]+math.sin(a)*radius))))
 for j in range(len(profile)-1):
  for i in range(segments):a=j*segments+i;b=j*segments+(i+1)%segments;faces.append((a,b,b+segments,a+segments))
 faces.append(tuple(reversed(tuple(range(segments)))));faces.append(tuple((len(profile)-1)*segments+i for i in range(segments)))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);return finish(o,mat,smooth=True)

def curve(name,points,radius,mat='Muted brass',resolution=3,cyclic=False):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=resolution;cu.bevel_depth=radius;cu.bevel_resolution=3
 s=cu.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
 for p,co in zip(s.bezier_points,points):p.co=B(co);p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 s.use_cyclic_u=cyclic;o=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(o);cu.materials.append(M[mat]);return o

def beam(name,a,b,r=.025,mat='Oak joinery'):
 start,end=B(a),B(b);d=end-start
 bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=d.length,location=(start+end)/2);o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return finish(o,mat,min(r/3,.008),2,True)

def cushion(name,loc,size,mat='Ivory textile',yaw=0,seed=0):
 # A sewn, domed cushion with softened corners and lightly relaxed surface.
 random.seed(seed);o=box(name,loc,size,mat,bevel=min(size)*.44,segments=5)
 sub=o.modifiers.new('Upholstery surface','SUBSURF');sub.levels=1;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=sub.name)
 for v in o.data.vertices:
  x,y,z=v.co;v.co.z+=.006*math.sin(x*19+seed)*math.sin(y*16+seed*.3)*(1-min(1,abs(z)/(size[1]*.5)))
 for p in o.data.polygons:p.use_smooth=True
 o.rotation_euler.z=yaw
 # slim sewn piping along the cushion's upper perimeter
 wx=size[0]*.45;dz=size[2]*.45;pts=[]
 for i in range(32):
  a=2*math.pi*i/32;xx=math.copysign(abs(math.cos(a))**.32,a if False else math.cos(a))*wx;zz=math.copysign(abs(math.sin(a))**.32,math.sin(a))*dz
  xr=xx*math.cos(yaw)+zz*math.sin(yaw);zr=-xx*math.sin(yaw)+zz*math.cos(yaw)
  pts.append((loc[0]+xr,loc[1]+size[1]*.22,loc[2]+zr))
 curve(name+' sewn piping',pts,.0055,mat,cyclic=True)
 return o

def fabric_surface(name,loc,width,depth,mat,drop=0,seed=1):
 # Gridded cloth with a genuine hanging edge, folded hem and controlled wrinkles.
 nx,nz=32,40;verts=[];faces=[]
 for iz in range(nz+1):
  t=iz/nz;z=-depth/2+t*depth
  for ix in range(nx+1):
   u=ix/nx;x=-width/2+u*width
   edge=max(0,(abs(x)-width*.455)/(width*.045));front=max(0,(z-depth*.46)/(depth*.04))
   yy=-drop*(edge**1.6+front**1.7)*.62+.006*math.sin(x*24+z*8+seed)*(.2+edge+front)+.006*math.cos(z*23-x*4)
   verts.append(tuple(B((loc[0]+x,loc[1]+yy,loc[2]+z))))
 for iz in range(nz):
  for ix in range(nx):a=iz*(nx+1)+ix;faces.append((a,a+1,a+nx+2,a+nx+1))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);finish(o,mat,smooth=True)
 sol=o.modifiers.new('Fine textile thickness','SOLIDIFY');sol.thickness=.009
 sub=o.modifiers.new('Soft cloth folds','SUBSURF');sub.levels=1
 bpy.context.view_layer.objects.active=o
 for m in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=m.name)
 return o

def curtains(x,y,z,width=.55,height=2.05,mat='Linen'):
 nx,ny=30,30;verts=[];faces=[]
 for iy in range(ny+1):
  t=iy/ny
  for ix in range(nx+1):
   u=ix/nx;gather=.94-.2*math.sin(t*math.pi)
   xx=x+(u-.5)*width*gather
   zz=z+.048*math.sin(u*math.pi*10)*(1+.2*t)
   yy=y-height*t+.018*math.cos(u*math.pi*10)*t*t
   verts.append(tuple(B((xx,yy,zz))))
 for iy in range(ny):
  for ix in range(nx):a=iy*(nx+1)+ix;faces.append((a,a+1,a+nx+2,a+nx+1))
 mesh=bpy.data.meshes.new('Linen folds');mesh.from_pydata(verts,[],faces);o=bpy.data.objects.new('Bedroom tailored linen curtain',mesh);bpy.context.collection.objects.link(o);finish(o,mat,smooth=True)
 sol=o.modifiers.new('Woven thickness','SOLIDIFY');sol.thickness=.007;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=sol.name)
 for j in range(7):
  bpy.ops.mesh.primitive_torus_add(major_radius=.025,minor_radius=.005,major_segments=16,minor_segments=6,location=B((x+(j/6-.5)*width,y+.04,z)))
  o=bpy.context.object;o.name='Curtain ring';o.rotation_euler.x=math.pi/2;finish(o,'Muted brass',smooth=True)

def shell(kind):
 r=ROOMS[kind];w,h,d=r['width'],r['height'],r['depth'];wall={'living':'Living wall','bedroom':'Bedroom wall','library':'Library green','sunroom':'Ivory plaster'}[kind]
 box(kind+' back plaster',[0,h/2,-d+.03],[w,h,.1],wall,.018)
 if kind!='sunroom':
  for side in [-1,1]:box(kind+' side plaster',[side*(w/2+.015),h/2,-d/2],[.07,h,d],wall,.015)
  box(kind+' ceiling',[0,h+.025,-d/2],[w+.1,.07,d],'Painted cream',.015)
 # Sunroom architecture owns the glass sidewalls and sloped conservatory roof.
 for i in range(12):
  xx=-w/2+(i+.5)*w/12
  box(kind+' oak floor plank',[xx,.018,-d/2],[w/12-.008,.045,d-.02],'Oak joinery',.006)
 for side in [-1,1]:
  if kind!='sunroom':
   box('Continuous deep skirting',[side*(w/2-.025),.1,-d/2],[.045,.18,d],'Painted cream',.01)
   box('Skirting bead',[side*(w/2-.05),.2,-d/2],[.026,.025,d],'Painted cream',.007)
   box('Coved cornice',[side*(w/2-.045),h-.06,-d/2],[.09,.11,d],'Painted cream',.024)
 box('Rear deep skirting',[0,.1,-d+.1],[w-.07,.18,.05],'Painted cream',.01)
 box('Rear cornice',[0,h-.06,-d+.12],[w,.11,.13],'Painted cream',.025)
 return w,h,d

def rug(name,x,z,width,depth,mat='Terracotta textile'):
 box(name,[x,.055,z],[width,.018,depth],'Rug braid',.006)
 box(name+' woven border',[x,.066,z],[width-.07,.012,depth-.07],'Ivory textile',.004)
 box(name+' inset field',[x,.073,z],[width-.16,.008,depth-.16],mat,.003)
 # Sparse jacquard strips and individual fringe give textiles an authored edge.
 for side in [-1,1]:
  for i in range(int(width/.06)):
   xx=x-width/2+.035+i*.06
   curve('Rug cotton fringe',[(xx,.06,z+side*depth/2),(xx+.007,.055,z+side*(depth/2+.06)),(xx+.014,.056,z+side*(depth/2+.09))],.0025,'Linen')

def imported(name,asset,height,loc,yaw=0):
 p=ROOT/'public/assets/models'/asset
 if not p.exists():return None
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(p));objs=[o for o in bpy.data.objects if o not in before]
 root=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(root)
 for o in objs:
  if o.parent not in objs:o.parent=root
 root.scale=(height,height,height);root.rotation_euler.z=yaw;root.location=B(loc)
 return root

def lamp(name,x,y,z,height=.55,shade=.22):
 lathe(name+' turned base',(x,y,z),[(.13,0),(.14,.018),(.11,.04),(.065,.065),(.027,.08),(.023,height*.68)],'Muted brass')
 lathe(name+' pleated shade',(x,y,z),[(shade,height*.7),(shade*.97,height*.72),(shade*.58,height),(shade*.56,height+.005),(shade*.59,height*.98),(shade*.94,height*.71)],'Linen',48)
 ellipsoid(name+' bulb',(x,y+height*.78,z),(.04,.052,.04),'Lamp glow')
 # Fine ribs align the linen shade's silhouette.
 for i in range(24):
  a=i*math.pi/12;curve('Lampshade stitched rib',[(x+math.cos(a)*shade,y+height*.7,z+math.sin(a)*shade),(x+math.cos(a)*shade*.58,y+height,z+math.sin(a)*shade*.58)],.0018,'Ivory textile')

def cup(x,y,z):
 lathe('Hand-thrown tea cup',(x,y,z),[(.035,0),(.052,.015),(.057,.1),(.054,.11),(.047,.1),(.042,.022)],'Ceramic')
 lathe('Ceramic saucer',(x,y-.008,z),[(.025,0),(.085,.006),(.09,.013),(.075,.018)],'Ceramic')
 curve('Tea cup loop handle',[(x+.049,y+.083,z),(x+.088,y+.08,z),(x+.086,y+.036,z),(x+.05,y+.026,z)],.007,'Ceramic')
 cyl('Tea surface',(x,y+.082,z),.045,.003,'Coffee')

def small_book(name,loc,size=(.22,.035,.3),mat='Book cloth 1',yaw=0):
 o=box(name,loc,size,mat,.005);o.rotation_euler.z=yaw
 o=box(name+' paper block',(loc[0],loc[1]+.002,loc[2]-.007),(size[0]-.018,size[1]-.012,size[2]-.012),'Paper',.002);o.rotation_euler.z=yaw

def picture(name,x,y,z,width=.7,height=.52,style=0):
 box(name+' framed artwork',(x,y,z),(width,height,.045),'Walnut',.014)
 box(name+' gilt inner moulding',(x,y,z+.027),(width-.045,height-.045,.016),'Muted brass',.005)
 box(name+' linen mount',(x,y,z+.038),(width-.075,height-.075,.014),'Paper',.003)
 if style==0:
  # Abstract hand-cut landscape, geometry rather than invented portfolio imagery.
  box('Muted landscape sky',(x,y+.04,z+.048),(width-.15,height-.19,.008),'Sage textile',.002)
  for j in range(3):ellipsoid('Landscape hill',(x+(j-1)*width*.21,y-height*.19+j*.017,z+.056),(width*.22,.07,.006),'Terracotta textile' if j==1 else 'Library green')
 else:
  for j in range(3):curve('Botanical study stem',[(x+(j-1)*.12,y-height*.22,z+.05),(x+(j-1)*.09,y+.1,z+.05),(x+(j-1)*.15,y+height*.23,z+.05)],.004,'Library green')
  for j in range(6):ellipsoid('Botanical study leaf',(x+(j%3-1)*.12+.04*(j%2),y-.1+j*.04,z+.054),(.045,.018,.004),'Sage textile')

def flame(name,loc,height=.24,width=.04,lean=.025,mat='Flame'):
 # Curved, tapered tongues of fire; separate warm core reads against the dark hearth.
 verts=[];faces=[];levels=9;segments=12
 for j in range(levels):
  t=j/(levels-1);radius=width*(math.sin(math.pi*(t*.94+.04))**.8)*(1-t*.72)
  cx=loc[0]+lean*math.sin(t*math.pi*1.3);cz=loc[2]-.022*t
  for i in range(segments):
   a=i*math.pi*2/segments;verts.append(tuple(B((cx+math.cos(a)*radius,loc[1]+height*t,cz+math.sin(a)*radius*.55))))
 for j in range(levels-1):
  for i in range(segments):a=j*segments+i;b=j*segments+(i+1)%segments;faces.append((a,b,b+segments,a+segments))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);return finish(o,mat,smooth=True)

def fireplace():
 x,z=1.12,-2.31
 box('Fireplace chimney breast',(x,1.35,z),(.74,2.6,.32),'Ivory plaster',.03)
 box('Fireplace hearth',(x,.1,z+.31),(1.01,.15,.72),'Warm limestone',.04)
 box('Fireplace dark opening',(x,.53,z+.175),(.57,.7,.04),'Dark metal',.01)
 for s in [-1,1]:box('Fireplace carved jamb',(x+s*.36,.53,z+.24),(.15,.85,.25),'Warm limestone',.035)
 box('Fireplace arched lintel',(x,.93,z+.25),(.85,.18,.29),'Warm limestone',.04)
 box('Fireplace walnut mantel',(x,1.055,z+.25),(1,.12,.39),'Walnut',.035)
 for j in range(3):
  beam('Hearth split charred log',(x-.24+j*.025,.255+j*.03,z+.5-j*.035),(x+.2-j*.025,.28+(2-j)*.035,z+.46+j*.02),.044,'Charred timber')
 for i,(a,hh,ww,lean) in enumerate([(-.17,.13,.025,-.016),(-.075,.27,.045,.035),(.015,.17,.034,-.023),(.10,.22,.039,.017),(.19,.105,.022,-.012)]):
  ellipsoid('Fireplace glowing coal',(x+a,.285,z+.38),(.034,.017,.028),'Flame')
  flame('Living fireplace flame '+str(i),(x+a,.29+(i%2)*.02,z+.36),hh,ww,lean)
  if i in [1,2,3]:flame('Living fireplace yellow heart '+str(i),(x+a,.30,z+.385),hh*.52,ww*.48,lean*.6,'Flame core')
 picture('Small mantel landscape',x,1.58,z+.19,.58,.56)
 for a in [-.33,.33]:lathe('Mantel candle holder',(x+a,1.12,z+.27),[(.055,0),(.04,.04),(.022,.13),(.044,.16)],'Muted brass');cyl('Mantel candle',(x+a,1.36,z+.27),.025,.16,'Candle wax')

def living():
 shell('living');rug('Living woven rug',-.18,-.98,2.36,1.46,'Terracotta textile');imported('Living carved upholstered sofa','v03/sofa-victorian.glb',.8,(-.42,.07,-1.82));fireplace()
 cushion('Living soft linen pillow',(-.94,.66,-1.66),(.3,.34,.13),'Ivory textile',yaw=-.1,seed=81)
 cushion('Living sage pillow',(.1,.66,-1.67),(.3,.31,.13),'Sage textile',yaw=.1,seed=82)
 # Rounded oval coffee table with turned tapered legs.
 ellipsoid('Living oval walnut coffee top',(-.25,.52,-.69),(.68,.045,.37),'Walnut')
 for a in [-.44,.44]:
  for b in [-.2,.2]:lathe('Coffee table turned leg',(-.25+a,.08,-.69+b),[(.025,0),(.038,.025),(.026,.31),(.047,.39)],'Oak joinery',24)
 small_book('Living coffee table book',(-.43,.577,-.69),(.28,.034,.36),'Book cloth 2',.12);cup(.06,.572,-.6)
 lamp('Living floor lamp',-1.39,.06,-1.13,1.6,.25)
 picture('Living wall landscape',-.44,1.87,-2.52,1.38,.6)
 return [{'name':'Living floor lamp bulb','position':[-1.39,1.31,-1.13],'color':'#ffe2b0','intensity':2.2},{'name':'Living fireplace embers','position':[1.12,.58,-1.87],'color':'#ff9c42','intensity':1.6}]

def bedside(name,x,z):
 for a in [-.16,.16]:
  for b in [-.14,.14]:lathe(name+' tapered leg',(x+a,.02,z+b),[(.02,0),(.025,.15),(.035,.34)],'Oak joinery',24)
 box(name+' drawer carcass',(x,.48,z),(.44,.31,.4),'Oak joinery',.035)
 box(name+' moulded top',(x,.65,z),(.48,.055,.44),'Walnut',.025)
 box(name+' inset drawer',(x,.49,z+.21),(.37,.21,.035),'Walnut',.015)
 cyl(name+' brass knob',(x,.49,z+.25),.022,.03,'Muted brass')
 imported(name+' oil lamp','v03/vintage-oil-lamp.glb',.43,(x,.69,z))

def bedroom():
 shell('bedroom');rug('Bedroom woven rug',0,-1.29,2.23,2.19,'Sage textile')
 z=-1.32
 for x in [-.64,.64]:
  for zz in [-.83,.83]:lathe('Bed turned leg',(x,.055,z+zz),[(.04,0),(.045,.06),(.03,.22),(.05,.28)],'Walnut',24)
 box('Bed oak base',(0,.37,z),(1.49,.25,1.94),'Oak joinery',.055)
 box('Bed footboard moulding',(0,.49,z+.90),(1.55,.13,.1),'Walnut',.035)
 cushion('Bedroom sprung mattress',(0,.56,z),(1.45,.23,1.91),'Ivory textile',seed=30)
 # Arched upholstery headboard with piped panels and oak rim.
 box('Bedroom headboard carved oak frame',(0,.99,-2.32),(1.64,1.45,.15),'Walnut',.16,segments=6)
 cushion('Bedroom linen headboard',(0,1.06,-2.24),(1.48,1.24,.16),'Linen',seed=14)
 for i in range(5):ellipsoid('Headboard tuft button',((i-2)*.25,1.13,-2.142),(.018,.018,.006),'Muted brass')
 fabric_surface('Bedroom soft sage duvet',(0,.705,z+.12),1.61,1.76,'Sage textile',drop=.29,seed=22)
 # Folded duvet top and a contrasting foot throw reveal thickness rather than a flat plane.
 cushion('Bedroom folded duvet edge',(0,.75,-1.96),(1.45,.1,.23),'Sage textile',seed=5)
 fabric_surface('Bedroom woven foot throw',(0,.76,-.62),1.65,.54,'Ivory textile',drop=.28,seed=29)
 for x in [-.37,.37]:cushion('Bedroom full feather pillow',(x,.8,-2.04),(.65,.19,.42),'Ivory textile',yaw=x*.12,seed=40 if x<0 else 41)
 for x in [-1.03,1.03]:bedside('Bedroom bedside',x,-2.14)
 # Painted wardrobe is a functional room-specific silhouette.
 box('Bedroom wardrobe',(-1.23,1.01,-.72),(.32,1.91,.67),'Painted cream',.035)
 for j in [-1,1]:
  box('Wardrobe recessed door',(-1.055,1.03,-.72+j*.158),(.035,1.69,.3),'Linen',.014)
  beam('Wardrobe brass handle',(-1.028,.92,-.72+j*.06),(-1.028,1.11,-.72+j*.06),.012,'Muted brass')
 # Front-side curtains sit on the reveals and keep the middle of the entrance free.
 for s in [-1,1]:curtains(s*1.23,2.47,-.27,.31,2.25,'Linen')
 beam('Bedroom curtain rod',(-1.4,2.54,-.27),(1.4,2.54,-.27),.018,'Muted brass')
 picture('Bedroom botanical',0,2.1,-2.52,.56,.43,1)
 return [{'name':'Bedroom bedside left bulb','position':[-1.03,1.02,-2.14],'color':'#ffe1ba','intensity':1.3},{'name':'Bedroom bedside right bulb','position':[1.03,1.02,-2.14],'color':'#ffd8a1','intensity':1.2}]

def bookcase(name,x,z,width,height,side=False,seed=0):
 # Original full-height millwork: thick cornice, adjustable shelves and a cabinet base.
 rng=random.Random(seed);parts=[]
 before=set(bpy.data.objects)
 box(name+' back',(x,height/2,z),(width,height,.05),'Library green',.01)
 for s in [-1,1]:
  box(name+' fluted upright',(x+s*(width/2-.035),height/2,z+.15),(.08,height,.35),'Walnut',.012)
  for j in [-1,0,1]:box('Carved pilaster flute',(x+s*(width/2-.035)+j*.017,height/2,z+.331),(.006,height-.13,.006),'Muted brass',.002)
 box(name+' cornice',(x,height+.035,z+.15),(width+.13,.13,.43),'Walnut',.028)
 box(name+' crown bead',(x,height+.11,z+.15),(width+.06,.027,.38),'Oak joinery',.01)
 box(name+' plinth',(x,.13,z+.15),(width+.08,.18,.4),'Walnut',.02)
 for yy in [.27,.68,1.09,1.5,1.91]:
  if yy>height:continue
  box(name+' shelf',(x,yy,z+.15),(width,.055,.36),'Oak joinery',.008)
  box(name+' front shelf bead',(x,yy+.025,z+.334),(width,.025,.028),'Walnut',.007)
  if yy>.29:
   n=int((width-.16)/.077)
   for i in range(n):
    if (i+int(yy*7)+seed)%13==0:continue
    ww=rng.uniform(.045,.065);hh=rng.uniform(.21,.32);xx=x-width/2+.13+i*.077
    mat=f'Book cloth {rng.randrange(6)}'
    o=box('Library bound volume',(xx,yy+.03+hh/2,z+.17),(ww,hh,.23),mat,.005)
    if i==n-1:o.rotation_euler.y=.08
    for hy in [.055,hh-.035]:box('Library gilded spine band',(xx,yy+.03+hy,z+.288),(ww*.74,.006,.005),'Muted brass',.001)
 if side:
  pivot=bpy.data.objects.new(name+' side bank pivot',None);bpy.context.collection.objects.link(pivot);pivot.location=B((x,0,z));bpy.context.view_layer.update()
  for o in set(bpy.data.objects)-before:
   if o!=pivot:o.parent=pivot;o.matrix_parent_inverse=pivot.matrix_world.inverted()
  pivot.rotation_euler.z=math.pi/2

def library():
 shell('library');rug('Library Persian-style rug',0,-1.15,2.18,1.85,'Terracotta textile')
 bookcase('Library rear bookcase',0,-2.53,2.57,2.35,seed=42)
 bookcase('Library left bookcase',-1.29,-1.36,1.67,2.3,side=True,seed=52)
 imported('Library reading armchair','carved-armchair.glb',1.22,(.14,.08,-1.15),-.12)
 imported('Library side table','oak-side-table.glb',.56,(.86,.08,-.88),.2)
 lamp('Library reading lamp',.91,.66,-.91,.46,.16);cup(.6,.65,-.77)
 small_book('Library open-at-hand volume',(.81,.655,-.83),(.24,.035,.32),'Book cloth 1',.14)
 # Library ladder is correctly pitched against the shelf, with shaped feet and brass rail.
 beam('Library ladder left',(-1.03,.09,-1.72),(-1.03,2.29,-2.17),.027,'Oak joinery')
 beam('Library ladder right',(-.65,.09,-1.72),(-.65,2.29,-2.17),.027,'Oak joinery')
 for i in range(7):
  yy=.31+i*.285;zz=-1.72-(yy-.09)/2.2*.45
  box('Library ladder tread',(-.84,yy,zz),(.42,.045,.1),'Walnut',.012)
 beam('Library rolling rail',(-1.26,2.32,-2.17),(1.25,2.32,-2.17),.018,'Muted brass')
 return [{'name':'Library reading lamp bulb','position':[.91,1.02,-.91],'color':'#ffcd87','intensity':2.0}]

def cane_seat(x,z,yaw=0):
 before=set(bpy.data.objects)
 for sx in [-.31,.31]:
  for sz in [-.29,.29]:beam('Cane chair tapered leg',(x+sx,.07,z+sz),(x+sx*.92,.47,z+sz*.92),.026,'Oak joinery')
 cushion('Sunroom linen seat',(x,.48,z),(.67,.14,.65),'Ivory textile',seed=70)
 # Continuous bentwood frame and woven cane are modelled as actual curved strands.
 curve('Sunroom curved bentwood back',[(x-.34,.47,z-.28),(x-.36,1.05,z-.31),(x-.21,1.27,z-.31),(x+.21,1.27,z-.31),(x+.36,1.05,z-.31),(x+.34,.47,z-.28)],.028,'Oak joinery')
 for i in range(13):
  xx=x-.285+i*.0475;curve('Rattan vertical weave',[(xx,.59,z-.29),(xx,1.02,z-.32),(xx,1.17-.06*(abs(i-6)/6),z-.31)],.006,'Rug braid')
 for i in range(11):
  yy=.61+i*.048;curve('Rattan horizontal weave',[(x-.29,yy,z-.29),(x,yy+.007,z-.305),(x+.29,yy,z-.29)],.006,'Linen')
 for side in [-1,1]:curve('Sunroom swept armrest',[(x+side*.32,.47,z+.26),(x+side*.35,.76,z+.25),(x+side*.34,.83,z-.19)],.027,'Oak joinery')
 cushion('Sunroom small sage pillow',(x,.78,z-.14),(.36,.37,.17),'Sage textile',seed=72)
 if yaw:
  pivot=bpy.data.objects.new('Sunroom seat orientation',None);bpy.context.collection.objects.link(pivot);pivot.location=B((x,0,z));bpy.context.view_layer.update()
  for o in set(bpy.data.objects)-before:
   if o!=pivot:o.parent=pivot;o.matrix_parent_inverse=pivot.matrix_world.inverted()
  pivot.rotation_euler.z=yaw

def sunroom():
 shell('sunroom')
 # Stone octagonal mosaic uses authored patterns rather than a flat tiled platform.
 for i in range(7):
  for j in range(6):
   mat='Sunroom tile' if (i+j)%2 else 'Warm limestone'
   box('Sunroom honed stone tile',(-1.15+i*.383,.06,-.24-j*.386),(.37,.027,.373),mat,.009)
 rug('Sunroom natural jute rug',0,-1.15,1.88,1.45,'Rug braid')
 cane_seat(-.65,-1.5,.13);cane_seat(.65,-1.5,-.13)
 # Delicate round tea table has a turned central pedestal and splayed tripod feet.
 lathe('Sunroom turned tea table',(0,.065,-.76),[(.09,0),(.06,.08),(.035,.4),(.08,.46),(.38,.49),(.39,.52),(.365,.54)],'Oak joinery',48)
 for i in range(3):
  a=i*math.pi*2/3;curve('Tea table curved foot',[(0,.2,-.76),(math.cos(a)*.15,.11,-.76+math.sin(a)*.15),(math.cos(a)*.28,.075,-.76+math.sin(a)*.28)],.028,'Walnut')
 imported('Sunroom professional tea service','v03/tea-set.glb',.115,(0,.615,-.76))
 imported('Sunroom plant left','potted-plant.glb',1.04,(-1.06,.09,-2.1),.2)
 imported('Sunroom plant right','potted-plant.glb',.79,(1.05,.08,-.62),1.6)
 # Slim rear console holds a propagation plant, not another bookshelf.
 box('Sunroom rear console top',(0,.78,-2.21),(1.25,.055,.33),'Oak joinery',.018)
 for x in [-.54,.54]:beam('Console slender leg',(x,.08,-2.21),(x,.75,-2.21),.025,'Oak joinery')
 imported('Sunroom propagated plant','potted-plant.glb',.43,(.32,.81,-2.19),.8)
 small_book('Sunroom gardening notebook',(-.3,.828,-2.19),(.23,.025,.27),'Book cloth 0',.08)
 return [{'name':'Sunroom daylight fill','position':[0,2.15,-.8],'color':'#fff2d8','intensity':2.8}]

def prepare_export(kind,lights):
 # Convert selected authoring geometry in one evaluation, avoiding per-object overhead.
 bpy.ops.object.select_all(action='DESELECT')
 meshes=[o for o in bpy.context.scene.objects if o.type in {'MESH','CURVE'}]
 for o in meshes:o.select_set(True)
 bpy.context.view_layer.objects.active=meshes[0]
 bpy.ops.object.convert(target='MESH')
 meshes=[o for o in bpy.context.selected_objects if o.type=='MESH']
 # Curve and lathe surfaces receive UVs together; imported source UVs are retained.
 bpy.ops.object.select_all(action='DESELECT')
 unwrap=[o for o in meshes if not o.data.uv_layers]
 if unwrap:
  for o in unwrap:o.select_set(True)
  bpy.context.view_layer.objects.active=unwrap[0]
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.1519,island_margin=.01);bpy.ops.object.mode_set(mode='OBJECT')
 # Flatten hierarchy in world space before combining static meshes by material.
 bpy.context.view_layer.update()
 worlds={o:o.matrix_world.copy() for o in meshes}
 bpy.ops.object.select_all(action='DESELECT')
 for o in meshes:
  o.parent=None;o.matrix_world=worlds[o];o.select_set(True)
 bpy.context.view_layer.objects.active=meshes[0]
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 # Repeated imports share their source materials, preventing avoidable duplicate draws.
 canonical={}
 for o in meshes:
  for i,mat in enumerate(o.data.materials):
   base=re.sub(r'\.\d{3}$','',mat.name)
   if base in canonical:o.data.materials[i]=canonical[base]
   else:canonical[base]=mat
 for mat in canonical.values():
  if mat.use_nodes:
   bs=mat.node_tree.nodes.get('Principled BSDF')
   if bs and bs.inputs['Emission Strength'].default_value>0 and (bs.inputs['Emission Color'].is_linked or max(bs.inputs['Emission Color'].default_value[:3])>.01):
    if not mat.name.startswith('emissive_'):mat.name='emissive_'+mat.name
 groups={}
 for o in meshes:
  key=tuple(m.name for m in o.data.materials)
  groups.setdefault(key,[]).append(o)
 meshes=[]
 for key,objects in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in objects:o.select_set(True)
  bpy.context.view_layer.objects.active=objects[0]
  if len(objects)>1:bpy.ops.object.join()
  joined=bpy.context.object;joined.name=kind+'__'+('_'.join(key)[:90] or 'geometry')
  meshes.append(joined)
 # Material image data is packed so the resulting GLB is portable and self-hosted.
 for img in bpy.data.images:
  if img.source=='FILE' and img.filepath and img.has_data:
   try:img.pack()
   except RuntimeError:pass
 bpy.ops.object.select_all(action='DESELECT')
 for o in meshes:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(OUT/f'{kind}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_extras=True)
 tris=0
 for o in meshes:
  o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
 return {'file':f'{kind}.glb','bytes':(OUT/f'{kind}.glb').stat().st_size,'triangles':tris,'staticMeshCount':len(meshes),'drawCalls':sum(len(o.data.materials) for o in meshes),'emissiveMaterials':sorted(set(m.name for o in meshes for m in o.data.materials if m.name.startswith('emissive_'))),'lights':lights,'width':ROOMS[kind]['width'],'depth':ROOMS[kind]['depth'],'height':ROOMS[kind]['height'],'origin':'floor center at entrance, +Y up, interior toward -Z'}

def render_review(kind):
 sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=False
 sc.render.resolution_x=720;sc.render.resolution_y=680;sc.render.resolution_percentage=100
 sc.world.color=(.35,.35,.35)
 def area(name,loc,energy,size,color,target):
  dat=bpy.data.lights.new(name,'AREA');dat.energy=energy;dat.shape='DISK';dat.size=size;dat.color=color;o=bpy.data.objects.new(name,dat);bpy.context.collection.objects.link(o);o.location=B(loc);o.rotation_euler=(B(target)-o.location).to_track_quat('-Z','Y').to_euler()
 area('Room softbox',(0,2.2,2.3),140,3.8,(1,.88,.7),(0,1,-1))
 area('Interior ceiling fill',(.4,2.45,-1),35,1.7,(1,.81,.58),(0,.8,-1.3))
 bpy.ops.object.camera_add(location=B((.15,1.55,3.7)));cam=bpy.context.object;cam.rotation_euler=(B((0,1.18,-1.1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=43;sc.camera=cam
 sc.view_settings.view_transform='AgX';sc.render.image_settings.file_format='PNG';sc.render.filepath=str(REVIEW/f'{kind}.png');bpy.ops.render.render(write_still=True)

if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 names=args or ['living','bedroom','library','sunroom'];manifest=[]
 for kind in names:
  clear();palette(kind);lights=globals()[kind]();manifest.append(prepare_export(kind,lights));render_review(kind)
  (OUT/f'{kind}-metadata.json').write_text(json.dumps(manifest[-1],indent=2))
 print('WEST_INTERIORS_RESULT='+json.dumps(manifest))
