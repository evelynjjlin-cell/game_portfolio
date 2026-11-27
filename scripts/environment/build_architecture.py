"""Original V03 cottage shell. Run: blender --background --python scripts/environment/build_architecture.py
Runtime coordinates are +Y up/+Z front; all geometry is authored here in those units.
Source meshes use Boolean aperture construction, multi-segment bevels, weighted normals,
lathed balusters, modeled slate courses and consistent UV scale. Exported meshes are merged
by material. Existing third-party PBR scans are documented in ASSET_CREDITS.md.
"""
import bpy, math, json, random, os, bmesh
from pathlib import Path
from mathutils import Vector, Matrix, Euler
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'public/assets/environment';OUT.mkdir(parents=True,exist_ok=True)
REVIEW=ROOT.parent/'architecture-work';REVIEW.mkdir(parents=True,exist_ok=True)
LAYOUT=json.loads((Path(__file__).with_name('layout.json')).read_text())
random.seed(4021)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
M=Matrix(((1,0,0),(0,0,-1),(0,1,0)))
def V(v): return M@Vector(v)
def lin(x):return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
def rgb(h):return tuple(lin(int(h[i:i+2],16)/255) for i in (1,3,5))+(1,)
def material(name,color,texture=None,rough=.8,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=rgb(color);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if texture:
  for typ in ['color','normal','roughness']:
   f=ROOT/f'public/assets/textures/{texture}-{typ}.jpg'
   if not f.exists():continue
   t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(f),check_existing=True);t.image.pack()
   if typ!='color':t.image.colorspace_settings.name='Non-Color'
   if typ=='color':
    mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=rgb(color);l.new(t.outputs['Color'],mix.inputs[1]);l.new(mix.outputs[0],p.inputs['Base Color'])
   elif typ=='normal':
    nm=n.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.23 if texture=='slate' else .12;l.new(t.outputs['Color'],nm.inputs['Color']);l.new(nm.outputs[0],p.inputs['Normal'])
   else:l.new(t.outputs['Color'],p.inputs['Roughness'])
 # glTF supports multiply Base Color factor; use native tint as export fallback.
 m.diffuse_color=rgb(color);m['base_color_factor']=color
 return m
plaster=material('Ivory lime plaster','#e7dbc4','plaster',.96)
stone=[material('Honed limestone '+str(i),c,'stone',.92) for i,c in enumerate(['#cdbb9c','#dbccb0','#c4b397'])]
wood=material('Warm walnut joinery','#805434','oak',.76)
woodLight=material('Worn oak edge','#aa7c4f','oak',.82)
woodDark=material('Walnut end grain','#503622','oak',.86)
slates=[material('Forest slate '+str(i),c,'slate',.88) for i,c in enumerate(['#344a35','#3e533b','#40543d','#374a36','#42543c'])]
brass=material('Muted brass','#a78547',None,.42,.7)
bronze=material('Bronze conservatory','#665e3c','oak',.57,.3)
lead=material('Dark bronze flashing','#48513c',None,.66,.35)
glass=material('Conservatory glass','#d6e0d7',None,.14,.05);p=glass.node_tree.nodes.get('Principled BSDF');p.inputs['Alpha'].default_value=.13;glass.surface_render_method='DITHERED';glass.diffuse_color=(*rgb('#d6e0d7')[:3],.13)
shadow=material('Recessed glazing','#403d32',None,.5)
cache={}
def smooth(obj,weighted=True):
 for p in obj.data.polygons:p.use_smooth=True
 if weighted:
  mod=obj.modifiers.new('Weighted architectural normals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=60
  bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=mod.name)
def uv_project(obj,scale=1):
 # World-sized planar coordinates keep plaster, stone and wood at consistent miniature scale.
 mesh=obj.data;uv=mesh.uv_layers.new(name='UVMap') if not mesh.uv_layers else mesh.uv_layers[0]
 for poly in mesh.polygons:
  n=poly.normal;axis=max(range(3),key=lambda i:abs(n[i]));a,b=((1,2),(0,2),(0,1))[axis]
  for li in poly.loop_indices:
   p=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(p[a]*scale,p[b]*scale)
def mesh(name,vertices,faces,mat,bevel=0):
 me=bpy.data.meshes.new(name);me.from_pydata([V(v) for v in vertices],[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(mat)
 if bevel:
  bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Rounded dressed edges','BEVEL');mod.width=bevel;mod.segments=3;mod.affect='EDGES';bpy.ops.object.modifier_apply(modifier=mod.name)
 uv_project(ob,.65);smooth(ob);return ob

def box(name,pos,size,mat,bevel=.025,rot=(0,0,0),segments=3):
 key=tuple(round(v,5) for v in size)+(mat.name,round(bevel,4),segments)
 if key not in cache:
  bpy.ops.mesh.primitive_cube_add(size=1);o=bpy.context.object;o.name=name;o.dimensions=(size[0],size[2],size[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  if bevel:
   mod=o.modifiers.new('Soft chamfer','BEVEL');mod.width=min(bevel,min(size)*.4);mod.segments=segments;bpy.ops.object.modifier_apply(modifier=mod.name)
  o.data.materials.append(mat);uv_project(o,.65);smooth(o);cache[key]=o.data;o.location=V(pos);o.rotation_euler=(M@Euler(rot,'XYZ').to_matrix()@M.transposed()).to_euler();return o
 o=bpy.data.objects.new(name,cache[key]);bpy.context.collection.objects.link(o);o.location=V(pos);o.rotation_euler=(M@Euler(rot,'XYZ').to_matrix()@M.transposed()).to_euler();return o

def beam(name,a,b,w,d,mat,bevel=.018):
 a,b=Vector(a),Vector(b);o=box(name,(0,0,0),(w,(b-a).length,d),mat,bevel);o.location=V((a+b)/2);o.rotation_euler=V(b-a).to_track_quat('Z','Y').to_euler();return o

def profile(name,points,z0,z1,mat,bevel=.02):
 n=len(points);verts=[(x,y,z) for z in [z0,z1] for x,y in points];faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,verts,faces,mat,bevel)
def archpoints(w,h,rise,cx=0,cy=0,n=48):
 spring=cy+h/2-rise;pts=[(cx-w/2,cy-h/2),(cx+w/2,cy-h/2),(cx+w/2,spring)]
 pts +=[(cx+w/2*math.cos(i*math.pi/n),spring+rise*math.sin(i*math.pi/n)) for i in range(1,n+1)];return pts

def subtract(wall,points,z0,z1):
 cutter=profile('temporary opening cutter',points,z0,z1,plaster,0);bpy.context.view_layer.objects.active=wall;mod=wall.modifiers.new('Architectural through opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)

BASE=.84;EAVE=6.6;RIDGE=8.3;D=3.64;K=(RIDGE-6.42)/D
GABLES=[(-2.7,1.96,7.91),(2.05,2.28,8.24)]
def gable_y(x,c,h,p):return p-(p-6.42)*abs(x-c)/h
def main_y(z):return RIDGE-K*abs(z)
def roof_y(x,z):
 h=main_y(z)
 if z>=0:
  for c,hw,p in GABLES:
   if abs(x-c)<=hw:h=max(h,gable_y(x,c,hw,p))
 return h
# Continuous main volume, one front wall profile, one rear wall, two closed side gables.
xs=sorted(set([-4.8,4.8]+[round(-4.8+i*.04,4) for i in range(241)]+[c for c,h,p in GABLES]))
front_top=[(x,max(EAVE,roof_y(x,3.23)-.08)) for x in xs]
front=profile('Unified front masonry', [(-4.8,BASE),(4.8,BASE)]+list(reversed(front_top)),2.91,3.23,plaster,0)
rear=profile('Unified rear masonry',[(-4.8,BASE),(4.8,BASE),(4.8,EAVE),(-4.8,EAVE)],-3.23,-2.91,plaster,0)
for r in LAYOUT['rooms']:
 target=front if r['facade']=='front' else rear;x,y,z=r['position'];subtract(target,archpoints(r['width']+.035,r['height']+.025,r['arch'],x,y),-3.6 if r['facade']=='back' else 2.75,-2.75 if r['facade']=='back' else 3.55)
for d in LAYOUT['aboutDoors']:
 x,y,z=d['position'];subtract(rear if d['back'] else front,archpoints(d['width']+.03,d['height']+.025,d['arch'],x,y),-3.6 if d['back'] else 2.75,-2.75 if d['back'] else 3.55)
for ob in [front,rear]:
 bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Soft aperture edges','BEVEL');mod.width=.024;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name);uv_project(ob,.46);smooth(ob)
# V035: true side-wall apertures, arranged in two domestic storeys and an attic.
SIDE_WINDOWS=[(u,y,1.12,1.54,.30) for y in [2.36,5.15] for u in [-1.48,1.48]]
def side_place(ob,side):
 rot=M@Euler((0,side*math.pi/2,0)).to_matrix()@M.transposed()
 ob.location=V((side*4.64,0,0))+rot@ob.location
 ob.rotation_euler=(rot@ob.rotation_euler.to_matrix()).to_euler()
 return ob
for side in [-1,1]:
 pts=[(-3.23,BASE),(3.23,BASE),(3.23,EAVE),(0,RIDGE-.1),(-3.23,EAVE)]
 ob=profile('Perforated side masonry',pts,-.16,.16,plaster,0)
 for u,y,w,h,r in SIDE_WINDOWS:subtract(ob,archpoints(w,h,r,u,y),-.24,.24)
 circle=[(.36*math.cos(i*2*math.pi/64),7.17+.36*math.sin(i*2*math.pi/64)) for i in range(64)]
 subtract(ob,circle,-.24,.24)
 bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Soft side aperture arris','BEVEL');mod.width=.014;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
 uv_project(ob,.46);smooth(ob);side_place(ob,side)
# Ground course, continuous cornice rhythm and shallow stone plinth.
box('Limestone plinth',(0,.83,0),(9.82,.22,6.66),stone[1],.065)
for s in [-1,1]:
 for i in range(28):
  x=-4.65+i*.344
  # Base course omitted at entrances: no raised blocks across thresholds.
  opens=[r for r in LAYOUT['rooms'] if r['facade']==('front' if s>0 else 'back') and r['floor']<1]+[dict(d,position=d['position']) for d in LAYOUT['aboutDoors'] if d['back']==(s<0)]
  if any(abs(x-r['position'][0])<r['width']/2+.08 for r in opens):continue
  box('Dressed footing',(x,1.08,s*3.235),(.338,.29,.09),stone[1],.012)
 # Floor belt only on actual piers; deliberately avoids all arched crowns.
 for a,b in ([(-4.8,-4.66),(-1.68,-1.28),(2.16,3.08),(4.5,4.8)] if s>0 else [(-4.8,-4.2),(-1.1,1.1),(4.2,4.8)]):
  box('Floor string course',((a+b)/2,3.69,s*3.25),(b-a,.13,.14),stone[1],.025)
# The dressed plinth turns continuously onto the end elevations.
for side in [-1,1]:
 box('Side limestone water table',(side*4.80,1.08,0),(.12,.29,6.46),stone[1],.018)
 box('Side plinth weathering',(side*4.815,1.25,0),(.16,.05,6.47),stone[1],.012)
# V035: slim continuous dressed-stone corner returns, embedded in the plaster.
# Each course is a connected L profile; a hairline joint replaces alternating toy blocks.
# The outer arris projects only 0.035 beyond the finished wall on either elevation.
for sx in [-1,1]:
 for sz in [-1,1]:
  low,high=.94,6.50;courses=12;pitch=(high-low)/courses
  for row in range(courses):
   y0=low+row*pitch+.004;y1=low+(row+1)*pitch-.004
   plan=[(4.50,3.205),(4.775,3.205),(4.775,2.93),(4.835,2.93),(4.835,3.265),(4.50,3.265)]
   pts=[(sx*x,sz*z) for x,z in plan];n=len(pts)
   vs=[(x,y,z) for y in [y0,y1] for x,z in pts]
   fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
   mesh('Flush limestone corner return',vs,fs,stone[1],.007)
# Integrated arch masonry: detailed wedge voussoirs and consistent jamb stones.
def surround(x,y,z,w,h,rise,back=False):
 sign=-1 if back else 1;ri=w/2+.028;ro=ri+.18;spring=y+h/2-rise
 # Continuous dressed reveal goes back into the full wall thickness.
 inner=archpoints(w+.008,h+.008,rise+.004,x,y)
 outer=archpoints(w+.09,h+.09,rise+.045,x,y)
 n=len(inner);vs=[(px,py,zz) for zz in [z-sign*.22,z+sign*.025] for pts in [inner,outer] for px,py in pts]
 fs=[]
 for j in range(n):
  k=(j+1)%n;fs.extend([(j,k,k+2*n,j+2*n),(j+n,j+3*n,k+3*n,k+n),(j,j+n,k+n,k),(j+2*n,k+2*n,k+3*n,j+3*n)])
 mesh('Continuous recessed opening reveal',vs,fs,stone[1],.005)
 for i in range(15):
  a=i*math.pi/15+.0025;b=(i+1)*math.pi/15-.0025
  pts=[(x+ri*math.cos(a+(b-a)*j/4),spring+(rise+.028)*math.sin(a+(b-a)*j/4)) for j in range(5)]
  pts +=[(x+ro*math.cos(b-(b-a)*j/4),spring+(rise+.208)*math.sin(b-(b-a)*j/4)) for j in range(5)]
  profile('Arch voussoir',pts,z+sign*.015,z+sign*(.105+(.012 if i==7 else 0)),stone[1],.009)
 jh=h-rise;nr=max(3,round(jh/.32))
 for side in [-1,1]:
  for j in range(nr):box('Arch jamb block',(x+side*(w/2+.118),y-h/2+jh*(j+.5)/nr,z+sign*.045),(.18,jh/nr-.008,.14),stone[1],.009)
 # Deep stepped limestone sill with a drip groove visually separated below.
 box('Honed sill',(x,y-h/2-.04,z+sign*.05),(w+.47,.12,.44),stone[1],.035)
 box('Sill drip edge',(x,y-h/2-.105,z+sign*.11),(w+.37,.036,.35),stone[0],.012)
for r in LAYOUT['rooms']:
 if r['kind']=='sunroom':continue
 x,y,z=r['position'];surround(x,y,z,r['width'],r['height'],r['arch'],r['facade']=='back')
for d in LAYOUT['aboutDoors']:
 x,y,z=d['position'];surround(x,y,z,d['width'],d['height'],d['arch'],d['back'])
# Timber gable framing follows the connected roof envelope, not detached modules.
for c,hw,peak in GABLES:
 z=3.29
 beam('Gable king post',(c,6.62,z),(c,peak-.14,z),.12,.16,wood)
 for side in [-1,1]:
  beam('Gable diagonal brace',(c+side*hw*.77,6.64,z),(c,peak-.44,z),.11,.15,wood)
  box('Carved corbel',(c+side*hw*.79,6.54,z+.04),(.17,.36,.22),wood,.05)
# Continuous main roof: thin solid timber deck; detailed slate courses mask deck seam.
# Front deck is a joined heightfield following the upper envelope at valley junctions.
verts=[];faces=[];NX=106;NZ=74
for j in range(NZ+1):
 z=-D+j*D*2/NZ
 for i in range(NX+1):
  x=-5.18+i*10.36/NX;verts.append((x,roof_y(x,z),z))
for j in range(NZ):
 for i in range(NX):
  a=j*(NX+1)+i;faces.append((a,a+NX+1,a+NX+2,a+1))
roof=mesh('Continuous joined roof deck',verts,faces,woodDark,0)
mod=roof.modifiers.new('Timber roof thickness','SOLIDIFY');mod.thickness=.13;bpy.context.view_layer.objects.active=roof;bpy.ops.object.modifier_apply(modifier=mod.name)
# Slate courses are individually beveled and clipped to the actual roof valleys.
# Cutting each course at its meeting plane avoids ragged full-tile overlaps in the valleys.
def clip_polygon(poly,func):
 out=[]
 if not poly:return out
 for p,q in zip(poly,poly[1:]+poly[:1]):
  fp,fq=func(p),func(q);insidep=fp>=-1e-7;insideq=fq>=-1e-7
  if insidep:out.append(p)
  if insidep!=insideq:
   t=fp/(fp-fq);out.append((p[0]+(q[0]-p[0])*t,p[1]+(q[1]-p[1])*t))
 return out

slate_cache={}
def slate_polygon(poly,height,variant):
 if len(poly)<3:return
 # Build a closed thin piece with the slate surface elevated above the continuous deck.
 n=len(poly);cx=sum(x for x,z in poly)/n;cz=sum(z for x,z in poly)/n;cy=height(cx,cz)
 verts=[(x-cx,height(x,z)+offset-cy,z-cz) for offset in [.085,.132] for x,z in poly]
 key=(variant,tuple(round(value,5) for vertex in verts for value in vertex))
 if key in slate_cache:
  ob=bpy.data.objects.new('Cut beveled slate',slate_cache[key]);bpy.context.collection.objects.link(ob);ob.location=V((cx,cy,cz));return
 faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 ob=mesh('Cut beveled slate',verts,faces,slates[variant],0)
 bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Weathered slate edge','BEVEL');mod.width=.012;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name);smooth(ob);uv_project(ob,1.3);slate_cache[key]=ob.data;ob.location=V((cx,cy,cz))
for side in [-1,1]:
 rows=12;cols=29;stepz=D/rows;stepx=10.36/cols
 for row in range(rows):
  z=side*(row+.45)*stepz
  for col in range(cols):
   x=-5.18+(col+.5)*stepx+(stepx*.46 if row%2 else 0)
   if x>5.15:continue
   w=(stepx-.014)/2;d=(stepz+.12)/2
   polys=[[(x-w,z-d),(x+w,z-d),(x+w,z+d),(x-w,z+d)]]
   if side>0:
    for c,hw,peak in GABLES:
     cut=[]
     for poly in polys:
      if all(main_y(zz)>=gable_y(xx,c,hw,peak)-.001 for xx,zz in poly):cut.append(poly);continue
      for half in [-1,1]:
       part=clip_polygon(poly,lambda p:half*(p[0]-c))
       part=clip_polygon(part,lambda p:main_y(p[1])-gable_y(p[0],c,hw,peak))
       if len(part)>2:cut.append(part)
     polys=cut
   for poly in polys:slate_polygon(poly,lambda xx,zz,zc=z,sgn=side:main_y(zz)+.25*sgn*(zz-zc),(col*7+row*3)%5)
for c,hw,peak in GABLES:
 slope=(peak-6.42)/hw;ang=math.atan(slope);rows=math.ceil(hw/.29);cols=11;dz=D/cols
 for side in [-1,1]:
  for row in range(rows):
   dx=hw*(row+.45)/rows;x=c+side*dx;y=peak-slope*dx
   for col in range(cols):
    z=(col+.5)*dz;w=(hw/rows+.10)/2;d=(dz-.013)/2
    poly=[(x-w,z-d),(x+w,z-d),(x+w,z+d),(x-w,z+d)]
    poly=clip_polygon(poly,lambda p:hw-abs(p[0]-c))
    poly=clip_polygon(poly,lambda p:gable_y(p[0],c,hw,peak)-main_y(p[1]))
    if len(poly)>2:slate_polygon(poly,lambda xx,zz,xc=x,sgn=side:gable_y(xx,c,hw,peak)+.25*sgn*(xx-xc),(row*3+col*7)%5)
 # Valley flashings form exact straight junctions between the pitched roof fields.
 zstart=max(0,(RIDGE-peak)/K)
 for side in [-1,1]:
  a=(c,peak+.11,zstart);zend=D-.025;dx=(peak-main_y(zend))/slope;b=(c+side*dx,main_y(zend)+.11,zend)
  beam('Formed valley flashing',a,b,.17,.033,lead,.008)
 # Exposed front fascia/soffit is a coherent two-part timber construction.
 for side in [-1,1]:
  a=(c,peak+.018,D+.055);b=(c+side*hw,6.42,D+.055)
  beam('Carved gable fascia',a,b,.17,.22,wood,.035)
  beam('Gable fascia moulding',(a[0],a[1]+.075,a[2]+.05),(b[0],b[1]+.075,b[2]+.05),.043,.075,woodLight,.012)
# Continuous eave and side fascias.
for side in [-1,1]:
 for xa,xb in ([(-5.24,5.24)] if side<0 else [(-5.24,-4.66),(-.74,-.23),(4.33,5.24)]):
  box('Eave cornice',((xa+xb)/2,6.39,side*(D+.015)),(xb-xa,.18,.18),wood,.04)
  box('Eave moulded fillet',((xa+xb)/2,6.46,side*(D+.06)),(xb-xa,.045,.06),woodLight,.012)
 for sx in [-1,1]:beam('Side roof fascia',(sx*5.19,6.38,side*D),(sx*5.19,RIDGE,0),.16,.18,wood,.028)
# Closed sloping soffit returns bridge each end wall to its bargeboard.
for sx in [-1,1]:
 for sz in [-1,1]:
  z0,z1=0,sz*D
  vs=[(x,main_y(z)-.105,z) for x in [sx*4.77,sx*5.20] for z in [z0,z1]]
  mesh('Closed side oak soffit',vs,[(0,1,3,2)],woodDark,0)
  beam('Side soffit wall fillet',(sx*4.81,main_y(0)-.12,0),(sx*4.81,main_y(z1)-.12,z1),.065,.085,wood,.012)
for xa,xb in [(-5.18,-4.66),(-.74,-.23),(4.33,5.18)]:
 box('Front eave soffit',((xa+xb)/2,6.44,3.43),(xb-xa,.07,.47),woodDark,.01)
box('Rear eave soffit',(0,6.44,-3.43),(10.36,.07,.47),woodDark,.01)
# Curved barrel ridge tiles, source lathe profile shared across all ridge segments.
def cylinder(name,pos,radius,depth,mat,verts=32,rot=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=radius,depth=depth,location=V(pos));o=bpy.context.object;o.name=name;o.rotation_euler=(M@Euler(rot,'XYZ').to_matrix()@M.transposed()).to_euler();o.data.materials.append(mat);uv_project(o);smooth(o);return o
# A true half-tube profile with open lower edge, not a cylinder sitting above the roof.
def ridge_segment(a,b):
 r=.135;th=.035;n=16;pts=[(r*math.cos(i*math.pi/n),r*math.sin(i*math.pi/n)) for i in range(n+1)]+[((r-th)*math.cos(i*math.pi/n),(r-th)*math.sin(i*math.pi/n)) for i in range(n,-1,-1)]
 o=profile('Barrel ridge',pts,-.19,.19,slates[1],.012)
 av,bv=Vector(a),Vector(b);o.location=V((av+bv)/2);o.rotation_euler=V(bv-av).to_track_quat('Y','Z').to_euler();return o
# Direct half-tube mesh in world space, along an arbitrary horizontal ridge direction.
def ridge(name,a,b):
 av,bv=Vector(a),Vector(b);direction=(bv-av).normalized();side=Vector((direction.z,0,-direction.x));up=Vector((0,1,0));length=(bv-av).length;segments=math.ceil(length/.38)
 for k in range(segments):
  p0=av+(bv-av)*k/segments;p1=av+(bv-av)*(k+1)/segments
  vertices=[]
  for p in [p0,p1]:
   for radius in [.135,.10]:
    for j in range(17):vertices.append(tuple(p+side*math.cos(j*math.pi/16)*radius+up*math.sin(j*math.pi/16)*radius))
  faces=[]
  for j in range(16):faces.extend([(j,j+1,j+35,j+34),(j+17,j+51,j+52,j+18),(j,j+17,j+18,j+1),(j+34,j+35,j+52,j+51)])
  faces +=[(0,34,51,17),(16,33,67,50)]
  mesh(name,vertices,faces,slates[k%3],.004)
ridge('Main curved ridge',(-5.18,RIDGE+.07,0),(5.18,RIDGE+.07,0))
for c,hw,peak in GABLES:ridge('Gable curved ridge',(c,peak+.085,max(0,(RIDGE-peak)/K)),(c,peak+.085,D+.13))
# Quiet stone chimney with recessed mortar joints, sloped cap and clay flues.
cx,cz=-3.6,-.7
box('Solid chimney masonry core',(cx,8.15,cz),(.79,2.55,.76),stone[1],.015)
for row in range(9):
 y=7.05+row*.27
 for side in [-1,1]:
  for col in range(3):box('Chimney sandstone',(cx+(col-1)*.25,y,cz+side*.31),(.245,.262,.16),stone[1],.009)
 for side in [-1,1]:box('Chimney return',(cx+side*.34,y,cz),(.14,.262,.46),stone[1],.009)
box('Chimney cap drip course',(cx,9.16,cz),(.88,.06,.80),stone[0],.015)
box('Chimney weathered cap',(cx,9.3,cz),(1.02,.19,.93),stone[1],.05)
for dx in [-.21,.21]:
 cylinder('Clay chimney pot',(cx+dx,9.53,cz),.14,.42,woodDark,32)
 cylinder('Chimney pot rim',(cx+dx,9.75,cz),.18,.075,wood,32)
# Fine copper gutters/downpipes and properly attached brackets.
for sx in [-1,1]:
 for sz in [-1,1]:
  x=sx*4.86;z=sz*2.84
  beam('Copper downpipe',(x,1.0,z),(x,6.35,z),.065,.065,brass,.025)
  beam('Downpipe swan neck',(x,6.35,z),(x,6.45,sz*3.59),.065,.065,brass,.02)
  for y in [1.3,2.9,4.5,6.0]:box('Pipe bracket',(x,y,z),(.10,.035,.10),lead,.008)
# Conservatory is an attached glazed extension with actual continuous structural joints.
left,right=-4.76,-1.74;zback,zfront=3.13,4.1;yfront,yback=3.55,3.7
box('Conservatory wall ledger',(-3.25,3.72,3.245),(3.17,.12,.14),bronze,.018)
box('Conservatory wall flashing',(-3.25,3.81,3.26),(3.22,.045,.21),lead,.01)
box('Conservatory stone curb',(-3.25,.9,3.62),(3.12,.16,1.23),stone[1],.045)
for x in [left,right]:
 for z in [zback,(zback+zfront)/2,zfront]:
  top=yback+(yfront-yback)*(z-zback)/(zfront-zback);box('Conservatory mullion',(x,(.94+top)/2,z),(.055,top-.94,.055),bronze,.014)
 for y in [1.02,1.65,2.7]:box('Conservatory side transom',(x,y,(zback+zfront)/2),(.055,.045,zfront-zback),bronze,.012)
 box('Conservatory side glass',(x,2.23,(zback+zfront)/2),(.018,2.45,zfront-zback-.06),glass,.002)
 beam('Sloped conservatory eave',(x,yback,zback),(x,yfront,zfront),.075,.075,bronze,.015)
for j in range(8):
 x=left+(right-left)*j/7;beam('Glazed roof bar',(x,yback,zback),(x,yfront,zfront),.055,.055,bronze,.012)
for z in [zback,(zback+zfront)/2,zfront]:
 y=yback+(yfront-yback)*(z-zback)/(zfront-zback);box('Glazed roof tie',(-3.25,y,z),(right-left+.07,.07,.06),bronze,.015)
mesh('Conservatory roof glass',[(left,yback-.016,zback),(right,yback-.016,zback),(right,yfront-.016,zfront),(left,yfront-.016,zfront)],[(0,1,2,3)],glass,0)
# Balcony: dressed slab, real turned balusters, curved brackets and oak handrail.
bx=2.05;bwidth=3.65;bfront=4.25;bback=3.18;floor=3.77
box('Balcony limestone slab',(bx,3.71,(bfront+bback)/2),(bwidth,.12,bfront-bback+.12),stone[1],.045)
box('Balcony stone drip fascia',(bx,3.665,bfront+.04),(bwidth-.03,.055,.09),stone[0],.014)
for side in [-1,1]:box('Balcony slab return drip',(bx+side*(bwidth/2-.02),3.665,(bfront+bback)/2),(.07,.055,bfront-bback),stone[0],.014)
box('Balcony floorboard deck',(bx,3.79,(bfront+bback)/2),(bwidth-.12,.055,bfront-bback),woodLight,.02)
for j in range(14):
 x=bx-bwidth/2+.13+j*(bwidth-.26)/13
 # Lathed baluster profile gives true concave/convex furniture-style turning.
 prof=[(.047,0),(.058,.05),(.041,.11),(.031,.22),(.067,.33),(.071,.38),(.043,.46),(.035,.58),(.055,.66),(.055,.72)]
 vs=[];fs=[];n=20
 for r,y in prof:
  for k in range(n):a=2*math.pi*k/n;vs.append((x+r*math.cos(a),floor+.12+y,bfront+r*math.sin(a)))
 for a in range(len(prof)-1):
  for k in range(n):fs.append((a*n+k,a*n+(k+1)%n,(a+1)*n+(k+1)%n,(a+1)*n+k))
 mesh('Turned oak baluster',vs,fs,wood,0)
box('Balcony handrail',(bx,4.68,bfront),(bwidth+.1,.13,.17),wood,.05)
box('Balcony lower rail',(bx,3.93,bfront),(bwidth,.09,.11),wood,.025)
for side in [-1,1]:
 x=bx+side*(bwidth/2-.04)
 box('Balcony newel',(x,4.21,bfront),(.14,.92,.14),wood,.025)
 box('Newel cap',(x,4.74,bfront),(.21,.08,.21),woodLight,.028)
 box('Balcony return handrail',(x,4.68,(bfront+bback)/2),(.13,.13,bfront-bback),wood,.035)
 for z in [3.47,3.74,4.0]:box('Balcony return spindle',(x,4.27,z),(.06,.7,.06),wood,.018)
 # Brackets are smoothly curved profiles, visibly anchored to the wall.
 pts=[(0,0),(.75,0),(.65,-.10),(.42,-.2),(.24,-.36),(.13,-.6),(0,-.62)]
 # The left console intersects the living-room arch; carry that end in the slab.
 if side==1:
  ob=profile('Carved balcony console',pts,-.10,.10,wood,.04);ob.location=V((x,3.63,3.22));ob.rotation_euler=(M@Euler((0,-math.pi/2,0)).to_matrix()@M.transposed()).to_euler()
# Proper curved limestone steps connect the main entrance and book rather than floating slabs.
def sector_step(cx,z,y,radius,front=True,height=.11):
 pts=[(cx,z)]+[(cx+radius*math.sin(-math.pi/2+j*math.pi/64),z+(1 if front else -1)*radius*math.cos(-math.pi/2+j*math.pi/64)) for j in range(65)]
 verts=[(x,yy,zz) for yy in [y-height/2,y+height/2] for x,zz in pts];n=len(pts);faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh('Rounded limestone step',verts,faces,stone[1],.028)
for j in range(3):sector_step(.48,3.17,.63+j*.095,1.89-j*.15,True,.12)
for j in range(3):sector_step(0,-3.14,.63+j*.095,1.36-j*.13,False,.12)
for j in range(2):box('Side entry threshold',(3.8,.71+j*.1,3.55-j*.14),(1.48-j*.13,.12,.66),stone[1],.04)
# Recessed end-elevation casements: the opening, masonry reveal, timber sash,
# glazing and sill occupy separate depths instead of being pasted onto a blank wall.
casement=material('Forest green side casements','#455748','oak',.83)
side_glass=material('Quiet blue green side glazing','#8eaaa7',None,.32,.12)
reflection=material('Soft glazing reflection','#c8d4cc',None,.4,.02)
def ring_profile(name,inner,outer,d0,d1,mat):
 n=len(inner);vs=[(u,y,d) for d in [d0,d1] for pp in [inner,outer] for u,y in pp];fs=[]
 for j in range(n):
  k=(j+1)%n;fs.extend([(j,k,k+2*n,j+2*n),(j+n,j+3*n,k+3*n,k+n),(j,j+n,k+n,k),(j+2*n,k+2*n,k+3*n,j+3*n)])
 return mesh(name,vs,fs,mat,.006)
for side in [-1,1]:
 for u,y,w,h,r in SIDE_WINDOWS:
  inside=archpoints(w-.025,h-.025,r-.0125,u,y);outside=archpoints(w+.23,h+.23,r+.115,u,y)
  side_place(ring_profile('Side stone reveal',inside,outside,-.055,.215,stone[1]),side)
  inside=archpoints(w-.18,h-.18,r-.09,u,y);outside=archpoints(w-.01,h-.01,r-.005,u,y)
  side_place(ring_profile('Recessed casement sash',inside,outside,-.065,.075,casement),side)
  side_place(profile('Recessed side glazing',inside,-.025,-.019,side_glass,.002),side)
  side_place(box('Casement mullion',(u,y-.035,.032),(.045,h-.16,.07),casement,.009),side)
  side_place(box('Casement transom',(u,y+.035,.032),(w-.16,.04,.07),casement,.008),side)
  side_place(box('Side stone sill',(u,y-h/2-.035,.17),(w+.36,.11,.43),stone[1],.022),side)
  side_place(box('Side sill drip edge',(u,y-h/2-.095,.25),(w+.23,.025,.18),stone[0],.006),side)
  # Restrained narrow reflected highlights emphasize recessed glass, without fake rooms.
  for du in [-.32,.23]:side_place(box('Side pane reflected light',(u+du,y-.22,-.009),(.025,.50,.006),reflection,.002),side)
 # Oculus is in the attic, cut into the gable and deeply framed with a real reveal.
 for ri,ro,d0,d1,mat in [(.355,.49,-.04,.215,stone[1]),(.285,.355,-.055,.07,casement)]:
  inner=[(ri*math.cos(i*2*math.pi/64),7.17+ri*math.sin(i*2*math.pi/64)) for i in range(64)]
  outer=[(ro*math.cos(i*2*math.pi/64),7.17+ro*math.sin(i*2*math.pi/64)) for i in range(64)]
  side_place(ring_profile('Recessed attic oculus',inner,outer,d0,d1,mat),side)
 circle=[(.286*math.cos(i*2*math.pi/64),7.17+.286*math.sin(i*2*math.pi/64)) for i in range(64)]
 side_place(profile('Attic glazing',circle,-.025,-.019,side_glass,.002),side)
 side_place(box('Attic central mullion',(0,7.17,.032),(.035,.56,.06),casement,.006),side)
 side_place(box('Attic crossbar',(0,7.17,.032),(.56,.035,.06),casement,.006),side)
 # The floor course ties both facade returns to the same storey datum.
 side_place(box('End elevation string course',(0,3.69,.17),(6.48,.105,.12),stone[1],.016),side)
 side_place(box('End gable tie beam',(0,6.53,.185),(6.22,.105,.09),wood,.014),side)
 side_place(beam('End gable king post',(0,7.70,.185),(0,8.12,.185),.10,.09,wood,.014),side)
 for direction in [-1,1]:
  side_place(beam('End gable rake trim',(direction*3.03,6.58,.185),(0,8.12,.185),.095,.09,wood,.014),side)
# Consolidate static draw calls by material. Applied transforms preserve world-space openings.
for ob in list(bpy.context.scene.objects):
 if ob.type!='MESH':continue
 bpy.context.view_layer.objects.active=ob;ob.select_set(True)
 for mod in list(ob.modifiers):
  try:bpy.ops.object.modifier_apply(modifier=mod.name)
  except:pass
 ob.select_set(False)
groups={}
for ob in list(bpy.context.scene.objects):
 if ob.type=='MESH':groups.setdefault(ob.data.materials[0].name if ob.data.materials else 'None',[]).append(ob)
for name,obs in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=bpy.context.object;ob.name='Shell__'+name.replace(' ','_')
# Save static GLB; cameras/lights in preview are not exported.
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'house-shell.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_image_format='JPEG',export_jpeg_quality=85)
# Verify color multiplication survives glTF export, which omits factors for some node graphs.
import struct
asset=OUT/'house-shell.glb';raw=asset.read_bytes();jn=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+jn]);binchunk=raw[20+jn:]
for mm in doc.get('materials',[]):
 source=bpy.data.materials.get(mm.get('name',''))
 if source and source.get('base_color_factor'):
  color=list(rgb(source['base_color_factor']));color[3]=source.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value
  mm.setdefault('pbrMetallicRoughness',{})['baseColorFactor']=color
payload=json.dumps(doc,separators=(',',':')).encode();payload+=b' ' *((-len(payload))%4);asset.write_bytes(struct.pack('<III',0x46546c67,2,20+len(payload)+len(binchunk))+struct.pack('<II',len(payload),0x4e4f534a)+payload+binchunk)
tri=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in bpy.context.scene.objects if o.type=='MESH')
print('SHELL_STATS',json.dumps({'meshes':len(groups),'triangles':tri,'bytes':(OUT/'house-shell.glb').stat().st_size}))
# Rebuild without inspection renders using -- --skip-review.
import sys
if '--skip-review' in sys.argv:sys.exit(0)
# Save an inspectable source scene outside public web assets.
bpy.ops.wm.save_as_mainfile(filepath=str(REVIEW/'architecture-source.blend'))
# Internal studio render: an inspection tool, never final implementation evidence.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False
scene.world.color=(.75,.75,.75)
world=scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.70,.73,.68,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
for name,pos,energy,size in [('Key',(-7,13,9),1500,7),('Fill',(8,10,2),900,8),('Rim',(0,10,-10),1000,6)]:
 bpy.ops.object.light_add(type='AREA',location=V(pos));o=bpy.context.object;o.name=name;o.data.energy=energy;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(V((0,4,0))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.1));floorob=bpy.context.object;floorob.data.materials.append(material('Studio ground','#e9e2d6',None,.9))
bpy.ops.object.camera_add(location=V((13,10.5,19)));camera=bpy.context.object;camera.data.type='ORTHO';camera.data.ortho_scale=16.5;camera.rotation_euler=(V((0,4.4,.15))-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera
scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX'
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(REVIEW/'architecture-review-front.png');bpy.ops.render.render(write_still=True)
camera.location=V((-13,10.5,-19));camera.rotation_euler=(V((0,4.4,0))-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(REVIEW/'architecture-review-back.png');bpy.ops.render.render(write_still=True)
