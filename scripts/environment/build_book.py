"""Original V03 book sculpture. Run: blender -b -t 2 -P scripts/environment/build_book.py"""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'public/assets/environment/book.glb'
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name,color,rough=.8,metal=0,texture=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if texture:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(ROOT/'public/assets/textures'/texture));m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
 return m
paper=mat('Handmade ivory paper',(.80,.716,.556),1)
cover=mat('Forest linen binding',(.028,.065,.044),.86)
edge=mat('Fine deckled page edges',(.53,.405,.26),1)
gold=mat('Aged brass bookbinding',(.52,.315,.105),.38,.7)
ribbon=mat('Terracotta woven bookmark',(.25,.075,.035),.95)
# Cloth microrelief is licensed CC0. Controlled tint keeps a unified forest palette.
for m in [cover]:
 ns=m.node_tree.nodes;tex=ns.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'public/assets/textures/bookcloth-normal.jpg'));tex.image.colorspace_settings.name='Non-Color';n=ns.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.18;m.node_tree.links.new(tex.outputs['Color'],n.inputs['Color']);m.node_tree.links.new(n.outputs['Normal'],ns.get('Principled BSDF').inputs['Normal'])

def xyz(p):return (p[0],-p[2],p[1])
def mesh(name,verts,faces,material,smooth=False,bevel=0):
 me=bpy.data.meshes.new(name);me.from_pydata([xyz(v) for v in verts],[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(material)
 for p in me.polygons:p.use_smooth=smooth
 uv=me.uv_layers.new(name='SurfaceUV')
 for poly in me.polygons:
  for li in poly.loop_indices:
   co=verts[me.loops[li].vertex_index];uv.data[li].uv=(co[0]*.5,co[2]*.5)
 if bevel:
  b=o.modifiers.new('Crafted edge radius','BEVEL');b.width=bevel;b.segments=3
  b.limit_method='ANGLE';b.angle_limit=.4
  n=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL');n.keep_sharp=True
 return o
W=6.94;D=5.12;N=100

def top(t,z=0):return .59+.37*math.sin(math.pi*t)-.19*math.exp(-t*13)+.018*math.sin(z*.8)*math.sin(math.pi*t)
def bottom(t):return .17+.095*math.sin(math.pi*t)-.015*math.exp(-t*12)
def prof(side,iscover=False):
 w=W+.15 if iscover else W;d=D+.16 if iscover else D
 upper=lambda t,z:bottom(t)-.025 if iscover else top(t,z)
 lower=lambda t:bottom(t)-.15 if iscover else bottom(t)
 verts=[];faces=[]
 # Front and rear strips join into closed curved volumes, with a smooth top surface.
 for z in [-d,d]:
  for layer in [0,1]:
   for i in range(N+1):
    t=i/N;verts.append((side*(.025+w*t),upper(t,z) if layer else lower(t),z))
 q=N+1
 for i in range(N):
  faces.extend([(i,i+1,q+i+1,q+i),(2*q+i,3*q+i,3*q+i+1,2*q+i+1),(q+i,q+i+1,3*q+i+1,3*q+i),(i,2*q+i,2*q+i+1,i+1)])
 faces +=[(0,q,3*q,2*q),(N,2*q+N,3*q+N,q+N)]
 if side<0:faces=[tuple(reversed(f)) for f in faces]
 return mesh(('Left' if side<0 else 'Right')+(' linen hardcover' if iscover else ' sewn page block'),verts,faces,cover if iscover else paper,False,.018 if iscover else .007)
for s in [-1,1]:prof(s);prof(s,True)
# Fine lamination follows both curved forefaces; slight deckling avoids manufactured-board appearance.
verts=[];faces=[]
for side in [-1,1]:
 for layer in range(1,125):
  frac=layer/125;thickness=.0017 if layer%5 else .0038
  for z in [-D-.009,D+.009]:
   for i in range(N):
    a=i/N;b=(i+1)/N
    def h(t):return bottom(t)+(top(t,z)-bottom(t))*frac+.001*math.sin(t*31+layer*2.6)
    k=len(verts);verts.extend([(side*(.025+W*a),h(a),z),(side*(.025+W*b),h(b),z),(side*(.025+W*b),h(b)+thickness,z),(side*(.025+W*a),h(a)+thickness,z)]);faces.append((k,k+1,k+2,k+3))
  for i in range(16):
   z0=-D+i*2*D/16;z1=-D+(i+1)*2*D/16;y=bottom(1)+(top(1)-bottom(1))*frac;k=len(verts);verts.extend([(side*(W+.034),y,z0),(side*(W+.034),y,z1),(side*(W+.034),y+thickness,z1),(side*(W+.034),y+thickness,z0)]);faces.append((k,k+1,k+2,k+3))
mesh('124 individually curved paper strata',verts,faces,edge)

def curve(name,pts,radius,material):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=16;cu.bevel_depth=radius;cu.bevel_resolution=3;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*xyz(co),1)
 ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);ob.data.materials.append(material);return ob
# Binding seams sit in the gutter, connecting the two covers into one object.
for front in [-1,1]:
 pts=[]
 for i in range(61):
  x=-.28+i*.56/60; y=.035+.15*(abs(x)/.28)**1.8;pts.append((x,y,front*(D+.17)))
 curve('Sewn brass headband',pts,.025,gold)
 for s in [-1,1]:
  pts=[(s*(.025+(W+.15)*i/N),bottom(i/N)-.075,front*(D+.178)) for i in range(N+1)]
  curve('Fine gilded cover tooling',pts,.009,gold)
# Cast corner protectors follow the cloth, kept thin enough to feel like binding hardware.
for sx in [-1,1]:
 for sz in [-1,1]:
  x=sx*(W+.165);z=sz*(D+.16)
  curve('Brass corner shoulder',[(x-sx*.39,.13,z),(x,.13,z),(x,.13,z-sz*.4)],.033,gold)
# A continuous flexible ribbon drapes over the exposed paper, not through the book.
verts=[];faces=[]
for i in range(41):
 t=i/40;z=4.37+t*1.35;x=.13+.22*t;y=.42*(1-t)**1.8+.065
 w=.095 if i<38 else .095-(i-38)*.023
 verts.extend([(x-w,y,z),(x+w,y,z)])
 if i:faces.append((2*i-2,2*i-1,2*i+1,2*i))
mesh('Silk reading ribbon',verts,faces,ribbon,True,.004)
# Join static mesh parts by material after modifiers; keep export draw calls low.
for o in list(bpy.context.scene.objects):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 if o.type=='CURVE':bpy.ops.object.convert(target='MESH')
 for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
for material in list(bpy.data.materials):
 os=[o for o in bpy.context.scene.objects if o.type=='MESH' and len(o.data.materials)==1 and o.data.materials[0]==material]
 if len(os)>1:
  bpy.ops.object.select_all(action='DESELECT')
  for o in os:o.select_set(True)
  bpy.context.view_layer.objects.active=os[0];bpy.ops.object.join()
OUT.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.export_scene.gltf(filepath=str(OUT),export_format='GLB',export_apply=True,export_yup=True,export_image_format='JPEG',export_jpeg_quality=88)
print('BOOK_EXPORT',OUT,OUT.stat().st_size)
