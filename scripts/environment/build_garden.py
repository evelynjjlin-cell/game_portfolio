"""Original restrained V03 cottage terrace and planting composition.

Run from any directory: blender -b -t 3 -P scripts/environment/build_garden.py
Coordinates in helpers are runtime +Y up/+Z front. The one imported botanical
prop is Poly Haven Potted Plant 02 (Rico Cilliers, CC0); all terrace furniture,
hydrangeas, ivy, groundcover and pavers are original geometry.
"""
import bpy
import json
import math
import random
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "public/assets/environment/garden.glb"
LAYOUT = json.loads((ROOT/"scripts/environment/layout.json").read_text())
RNG = random.Random(4128)
bpy.ops.wm.read_factory_settings(use_empty=True)


def xyz(p):
    return (p[0], -p[2], p[1])


def surface(x, z=0):
    t = min(1, abs(x)/6.94)
    return .59+.37*math.sin(math.pi*t)-.19*math.exp(-13*t)+.018*math.sin(z*.8)*math.sin(math.pi*t)


def material(name, color, rough=.8, metal=0, texture=None, normal=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = (*color,1)
    node = mat.node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value = (*color,1)
    node.inputs["Roughness"].default_value = rough
    node.inputs["Metallic"].default_value = metal
    if texture:
        tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(str(ROOT/"public/assets/textures"/texture),check_existing=True)
        tint = mat.node_tree.nodes.new("ShaderNodeMixRGB")
        tint.blend_type = "MULTIPLY"
        tint.inputs[0].default_value = 1
        tint.inputs[2].default_value = (*color,1)
        mat.node_tree.links.new(tex.outputs["Color"],tint.inputs[1])
        mat.node_tree.links.new(tint.outputs[0],node.inputs["Base Color"])
    if normal:
        tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(str(ROOT/"public/assets/textures"/normal),check_existing=True)
        tex.image.colorspace_settings.name = "Non-Color"
        norm = mat.node_tree.nodes.new("ShaderNodeNormalMap")
        norm.inputs["Strength"].default_value = .22
        mat.node_tree.links.new(tex.outputs["Color"],norm.inputs["Color"])
        mat.node_tree.links.new(norm.outputs["Normal"],node.inputs["Normal"])
    return mat


wood = material("Garden · oiled walnut",(.44,.255,.12),.68,normal="oak-normal.jpg")
cloth = material("Garden · woven oat linen",(.70,.60,.43),.96,normal="bookcloth-normal.jpg")
clay = material("Garden · warm terracotta",(.37,.20,.115),.9,normal="plaster-normal.jpg")
soil = material("Garden · rich potting soil",(.075,.055,.024),1)
stone = material("Garden · worn sandstone pavers",(.57,.47,.32),.96,normal="stone-normal.jpg")
stem = material("Garden · woody stems",(.15,.16,.065),.96)
leaf_dark = material("Garden · deep botanical green",(.065,.13,.035),.88)
leaf_light = material("Garden · olive leaf variation",(.17,.23,.058),.9)
petal_cream = material("Garden · ivory hydrangea petals",(.88,.84,.64),.94)
petal_pink = material("Garden · pale blush hydrangea petals",(.67,.48,.42),.96)
flower_center = material("Garden · ochre flower stamens",(.45,.31,.08),.92)
moss = material("Garden · irregular moss islands",(.13,.155,.036),1)
grass = material("Garden · straw green blades",(.22,.25,.06),.94)
brass = material("Garden · aged brass details",(.43,.27,.10),.4,.7)


class Batch:
    def __init__(self, name, mat):
        self.name,self.material = name,mat
        self.verts,self.faces,self.smooth = [],[],[]

    def add(self, verts, faces, smooth=True):
        offset=len(self.verts)
        self.verts.extend(verts)
        self.faces.extend(tuple(offset+i for i in face) for face in faces)
        self.smooth.extend([smooth]*len(faces))

    def finish(self):
        if not self.faces:
            return
        mesh=bpy.data.meshes.new(self.name)
        mesh.from_pydata([xyz(v) for v in self.verts],[],self.faces)
        mesh.materials.append(self.material)
        mesh.update()
        uv=mesh.uv_layers.new(name="GardenSurfaceUV")
        for poly,smooth in zip(mesh.polygons,self.smooth):
            poly.use_smooth=smooth
            for li in poly.loop_indices:
                p=self.verts[mesh.loops[li].vertex_index]
                uv.data[li].uv=(p[0]*2+p[1]*.17,p[2]*2+p[1]*.7)
        obj=bpy.data.objects.new(self.name,mesh)
        bpy.context.collection.objects.link(obj)
        return obj


BATCHES={mat.name:Batch(mat.name,mat) for mat in [wood,cloth,clay,soil,stone,stem,leaf_dark,leaf_light,petal_cream,petal_pink,flower_center,moss,grass,brass]}


def batch(mat):
    return BATCHES[mat.name]


def tube(points, radius, mat, sides=6, end_radius=None):
    """Parallel-transport tubular stem/turned furniture part, all authored mesh."""
    pts=[Vector(p) for p in points]
    verts=[];faces=[]
    for i,p in enumerate(pts):
        tangent=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized()
        side=tangent.cross(Vector((0,0,1)))
        if side.length<.01:side=tangent.cross(Vector((1,0,0)))
        side.normalize();up=tangent.cross(side).normalized()
        r=radius if end_radius is None else radius+(end_radius-radius)*i/(len(pts)-1)
        for k in range(sides):
            angle=2*math.pi*k/sides
            verts.append(tuple(p+r*(math.cos(angle)*side+math.sin(angle)*up)))
    for i in range(len(pts)-1):
        for k in range(sides):
            faces.append((i*sides+k,i*sides+(k+1)%sides,(i+1)*sides+(k+1)%sides,(i+1)*sides+k))
    faces.extend([tuple(reversed(range(sides))),tuple((len(pts)-1)*sides+k for k in range(sides))])
    batch(mat).add(verts,faces)


def lathe(center, profile, mat, sides=36):
    x,y,z=center;verts=[];faces=[]
    for h,r in profile:
        for i in range(sides):
            a=i*2*math.pi/sides
            verts.append((x+r*math.cos(a),y+h,z+r*math.sin(a)))
    for j in range(len(profile)-1):
        for i in range(sides):
            faces.append((j*sides+i,j*sides+(i+1)%sides,(j+1)*sides+(i+1)%sides,(j+1)*sides+i))
    batch(mat).add(verts,[tuple(reversed(face)) for face in faces])


def ball(center, radius, mat, rings=4, sides=8, scale=(1,1,1)):
    verts=[];faces=[]
    for j in range(rings+1):
        a=math.pi*j/rings
        for i in range(sides):
            b=2*math.pi*i/sides
            verts.append((center[0]+radius*math.sin(a)*math.cos(b)*scale[0],center[1]+radius*math.cos(a)*scale[1],center[2]+radius*math.sin(a)*math.sin(b)*scale[2]))
    for j in range(rings):
        for i in range(sides):faces.append((j*sides+i,j*sides+(i+1)%sides,(j+1)*sides+(i+1)%sides,(j+1)*sides+i))
    batch(mat).add(verts,faces)


def leaf(center, direction, length, width, mat, ivy=False):
    center=Vector(center);axis=Vector(direction).normalized()
    side=axis.cross(Vector((0,1,0)))
    if side.length<.05:side=axis.cross(Vector((0,0,1)))
    side.normalize();normal=side.cross(axis).normalized()
    if ivy:
        # Five slightly cupped lobes, rather than a collection of flat circles.
        outline=[(0,0),(-.43,.18),(-.5,.43),(-.23,.40),(-.39,.68),(-.14,.58),(0,1),(.14,.58),(.39,.68),(.23,.40),(.5,.43),(.43,.18)]
    else:
        outline=[(0,0),(-.32,.17),(-.5,.42),(-.39,.69),(0,1),(.39,.69),(.5,.42),(.32,.17)]
    verts=[tuple(center+axis*length*.45+normal*length*.09)]
    verts.extend(tuple(center+side*(x*width)+axis*(t*length)+normal*(math.sin(t*math.pi)*length*.015)) for x,t in outline)
    faces=[(0,1+i,1+(i+1)%len(outline)) for i in range(len(outline))]
    batch(mat).add(verts,faces)
    tube([center,center+axis*length*.45+normal*length*.092,center+axis*length*.88],length*.008,stem,4,end_radius=length*.003)


def petal(center, radial, normal, size, mat):
    center=Vector(center);axis=Vector(radial).normalized();normal=Vector(normal).normalized();side=normal.cross(axis).normalized()
    verts=[tuple(center+axis*size*.42+normal*size*.18),tuple(center),tuple(center+axis*size*.52-side*size*.4),tuple(center+axis*size),tuple(center+axis*size*.52+side*size*.4)]
    batch(mat).add(verts,[(0,1,2),(0,2,3),(0,3,4),(0,4,1)])


def hydrangea(x,z,height=.72):
    y=surface(x,z)+.015
    radius=.245
    lathe((x,y,z),[(0,.15),(.035,.17),(.07,.173),(.34,.231),(.36,.255),(.40,.257),(.421,.245),(.421,.219),(.385,.217),(.075,.145)],clay,40)
    lathe((x,y,z),[(.385,.001),(.385,.217)],soil,32)
    # Raised wheel-thrown bands and a turned foot read at the entrance scale.
    lathe((x,y,z),[(.045,.175),(.055,.18),(.065,.175)],clay,40)
    for j in range(7):
        angle=j*2.399
        rr=.18 if j else .02
        center=Vector((x+rr*math.cos(angle),y+.69+.05*math.sin(j*2),z+rr*math.sin(angle)))
        root=Vector((x,y+.37,z))
        tube([root,root*.35+center*.65,center],.012,stem,6,end_radius=.006)
        for k in range(3):
            start=root.lerp(center,.35+k*.16)
            turn=angle+k*2.1
            leaf(start,(math.cos(turn),.25,math.sin(turn)),.25,.17,leaf_dark if k%2 else leaf_light)
        # A spherical corymb of small four-petalled florets, each with real depth.
        for k in range(27):
            az=k*2.399;yy=.15+ .85*k/27
            rr2=math.sqrt(max(0,1-yy*yy))
            normal=Vector((rr2*math.cos(az),yy,rr2*math.sin(az)))
            spot=center+normal*.13
            axis=normal.cross(Vector((0,1,0))).normalized()
            other=normal.cross(axis).normalized()
            size=.032+RNG.random()*.012
            for q in range(4):
                radial=axis*math.cos(q*math.pi/2)+other*math.sin(q*math.pi/2)
                petal(spot,radial,normal,size,petal_cream if RNG.random()>.13 else petal_pink)
            ball(spot+normal*.004,.009,flower_center,2,5)


# Keep planted pots outside both living leaves and in front of the sunroom plane.
living=next(room for room in LAYOUT["rooms"] if room["kind"]=="living")
lx,_,lz=living["position"]
hydrangea(lx-living["width"]/2-.46,lz+1.07)
hydrangea(lx+living["width"]/2+.49,lz+1.02)


def ivy_vine(anchor, height, side_wall=False, direction=-1, spread=.15):
    ax,ay,az=anchor
    points=[]
    segments=max(12,int(height*8))
    for i in range(segments+1):
        t=i/segments
        sway=spread*math.sin(t*7.5)+.035*math.sin(t*23)
        points.append((ax,ay-height*t,az+sway) if side_wall else (ax+sway,ay-height*t,az))
    tube(points,.011,stem,5,end_radius=.004)
    for i in range(1,segments):
        p=Vector(points[i]);sgn=-1 if i%2 else 1
        branch=Vector((direction*.045,-.05,sgn*(.09+RNG.random()*.05))) if side_wall else Vector((sgn*(.09+RNG.random()*.05),-.04,direction*.035))
        end=p+branch;tube([p,end],.004,stem,4)
        orientation=Vector((direction*.13,-.43,sgn*.5)) if side_wall else Vector((sgn*.5,-.43,direction*.13))
        leaf(end,orientation,.17+RNG.random()*.055,.16,leaf_dark if i%3 else leaf_light,True)


# V035: side windows and masonry articulate the end elevations; no masking ivy.
# Keep only the restrained existing accents on the solid front and rear piers.
for x in [-.72,-.47]:
    ivy_vine((x,6.28,3.252),1.95,False,1,.09)
for x in [-.18,.12]:
    ivy_vine((x,6.14,-3.252),1.84,False,-1,.08)


def ground_patch(cx,cz,rx,rz,seed):
    rng=random.Random(seed);sides=23
    verts=[(cx,surface(cx,cz)+.032,cz)]
    for i in range(sides):
        a=i*2*math.pi/sides;r=.75+.16*math.sin(a*5+seed)+.09*rng.random();x=cx+math.cos(a)*rx*r;z=cz+math.sin(a)*rz*r
        verts.append((x,surface(x,z)+.014,z))
    batch(moss).add(verts,[(0,1+(i+1)%sides,1+i) for i in range(sides)])
    for i in range(int(rx*rz*115)):
        a=rng.random()*2*math.pi;r=math.sqrt(rng.random())*.9
        x=cx+math.cos(a)*rx*r;z=cz+math.sin(a)*rz*r;y=surface(x,z)+.023
        for q in range(3):
            turn=q*2.1+rng.random();h=.035+rng.random()*.065;w=.008
            side=Vector((math.cos(turn)*w,0,math.sin(turn)*w));base=Vector((x,y,z));tip=base+Vector((math.sin(turn)*h*.2,h,math.cos(turn)*h*.2))
            batch(grass).add([tuple(base-side),tuple(base+side),tuple(tip)],[(0,1,2)])
        if i%20==0:
            for q in range(4):petal((x,y+.045,z),(math.cos(q*math.pi/2),0,math.sin(q*math.pi/2)),(0,1,0),.022,petal_cream)


for i,args in enumerate([(-5.7,-3.5,.62,.72),(-5.72,-1.6,.58,.8),(-5.8,.45,.6,.8),(5.25,-2.55,.36,1.75),(5.4,.55,.30,1.45),(5.8,1.95,.16,.22),(-3.8,4.64,.78,.26),(4.62,4.62,.56,.28),(-4.6,-4.72,.55,.24),(4.6,-4.72,.55,.24)]):
    ground_patch(*args,150+i)


def paver(x,z,rx,rz,top=None,seed=0):
    rng=random.Random(seed);n=14;verts=[];faces=[]
    h=surface(x,z)+.025 if top is None else top
    for y in [h-.05,h]:
        for i in range(n):
            a=i*math.pi*2/n;r=.94+.06*rng.random();verts.append((x+rx*math.cos(a)*r,y,z+rz*math.sin(a)*r))
    faces.append(tuple(reversed(range(n,n*2))))
    for i in range(n):faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
    batch(stone).add(verts,faces,False)


# Small stepping stones expose generous paper between individual garden islands.
for i,(x,z) in enumerate([(-5.7,-2.55),(-5.8,-.55),(-5.9,1.32),(5.7,-2.65),(5.7,-.78),(5.78,1.18),(5.4,2.82)]):
    paver(x,z,.27,.21,seed=30+i)


# The book's outer page is lower here. A thin, irregular paved terrace follows it
# and carries two bentwood chairs and a turned round table wholly outside sunroom.
terrace_x,terrace_z=-5.85,3.25
terrace_y=surface(terrace_x,terrace_z)+.065
# The shallow terrace footing reaches the curved page; no outer paver floats.
outline=[(-6.65,2.0),(-6.52,1.94),(-5.27,1.94),(-5.12,2.08),(-5.12,4.27),(-5.27,4.36),(-6.51,4.36),(-6.65,4.23)]
verts=[(x,surface(x,z)-.006,z) for x,z in outline]+[(x,terrace_y-.012,z) for x,z in outline]
faces=[tuple(reversed(range(8,16)))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
batch(stone).add(verts,faces,False)
for i in range(4):
    for j in range(6):
        paver(-6.41+i*.35,2.17+j*.38,.23,.25,terrace_y,500+i*7+j)


def rotated(p,center,angle):
    x,y,z=p;cx,cy,cz=center
    return (cx+x*math.cos(angle)+z*math.sin(angle),cy+y,cz-x*math.sin(angle)+z*math.cos(angle))


def furniture_tube(points,center,angle,radius,mat=wood,sides=8,end_radius=None):
    tube([rotated(p,center,angle) for p in points],radius,mat,sides,end_radius)


def rounded_box(name, center, size, mat, radius=.035, rotation=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(center))
    obj=bpy.context.object;obj.name=name;obj.dimensions=(size[0],size[2],size[1]);obj.rotation_euler[2]=-rotation
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    obj.data.materials.append(mat)
    bevel=obj.modifiers.new("Softly tailored edges","BEVEL");bevel.width=radius;bevel.segments=4
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    for face in obj.data.polygons:face.use_smooth=True
    normal=obj.modifiers.new("Weighted upholstery normals","WEIGHTED_NORMAL");bpy.ops.object.modifier_apply(modifier=normal.name)
    return obj


def chair(center,angle):
    # Four subtly splayed legs, lower stretchers, continuous bowed back and slats.
    for sx in [-1,1]:
        for sz in [-1,1]:
            furniture_tube([(sx*.23,.015,sz*.21),(sx*.18,.20,sz*.17),(sx*.185,.43,sz*.175)],center,angle,.025,end_radius=.020)
        furniture_tube([(sx*.21,.19,-.19),(sx*.20,.22,.19)],center,angle,.014)
        furniture_tube([(sx*.18,.40,-.18),(sx*.22,.60,-.23),(sx*.23,.85,-.25),(sx*.16,.92,-.25)],center,angle,.024)
    furniture_tube([(-.16,.92,-.25),(0,.95,-.26),(.16,.92,-.25)],center,angle,.026)
    furniture_tube([(-.2,.46,-.19),(.2,.46,-.19)],center,angle,.023)
    for x in [-.14,-.07,0,.07,.14]:
        furniture_tube([(x,.47,-.20),(x,.66,-.25),(x*.93,.90,-.25)],center,angle,.011)
    # Sculpted oval seat with thin apron and tailored oat cushion.
    c=rotated((0,.42,0),center,angle)
    lathe(c,[(0,.22),(.018,.238),(.045,.235),(.05,.22)],wood,40)
    rounded_box("Garden · oat linen seat cushion",rotated((0,.49,0),center,angle),(.39,.09,.36),cloth,.04,angle)
    # Gentle lumbar cushion, kept small enough to show the bentwood back frame.
    rounded_box("Garden · oat linen lumbar cushion",rotated((0,.66,-.195),center,angle),(.33,.30,.075),cloth,.034,angle)


chair((-5.85,terrace_y,2.42),0)
chair((-5.85,terrace_y,4.04),math.pi)
lathe((terrace_x,terrace_y,terrace_z),[(0,.18),(.035,.2),(.08,.12),(.13,.08),(.21,.055),(.30,.08),(.38,.065),(.58,.055),(.64,.12),(.67,.13)],wood,32)
for i in range(3):
    a=i*math.pi*2/3
    tube([(terrace_x,terrace_y+.14,terrace_z),(terrace_x+.18*math.cos(a),terrace_y+.06,terrace_z+.18*math.sin(a)),(terrace_x+.28*math.cos(a),terrace_y+.035,terrace_z+.28*math.sin(a))],.038,wood,8,end_radius=.025)
lathe((terrace_x,terrace_y,terrace_z),[(.65,.30),(.66,.345),(.69,.356),(.72,.345),(.723,.001)],wood,48)
# A modest ceramic cup and brass candleholder leave the table largely open.
lathe((terrace_x-.10,terrace_y+.726,terrace_z+.035),[(0,.04),(.012,.043),(.082,.047),(.087,.043),(.087,.034),(.015,.031)],petal_cream,24)
tube([(terrace_x-.055,terrace_y+.745,terrace_z+.035),(terrace_x-.025,terrace_y+.756,terrace_z+.035),(terrace_x-.022,terrace_y+.79,terrace_z+.035),(terrace_x-.055,terrace_y+.80,terrace_z+.035)],.006,petal_cream,6)
lathe((terrace_x+.12,terrace_y+.724,terrace_z-.035),[(0,.045),(.013,.05),(.022,.027),(.075,.017),(.088,.033),(.098,.032)],brass,24)
lathe((terrace_x+.12,terrace_y+.824,terrace_z-.035),[(0,.018),(.10,.018),(.105,.001)],petal_cream,16)


for item in BATCHES.values():
    item.finish()

# One professionally scanned/modelled botanical accent by the left terrace.
# The imported pot is placed on the book surface, not on an invisible flat floor.
before=set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=str(ROOT/"public/assets/models/potted-plant.glb"))
new=[o for o in bpy.context.scene.objects if o not in before]
position=Vector(xyz((-6.38,surface(-6.38,1.55)+.02,1.55)))
for obj in new:
    if obj.parent is None:
        obj.matrix_world=Matrix.Translation(position) @ Matrix.Scale(.69,4) @ obj.matrix_world

# Material batching preserves every modeled silhouette, including chair curves.
for mat in list(bpy.data.materials):
    objects=[o for o in bpy.context.scene.objects if o.type=="MESH" and len(o.data.materials)==1 and o.data.materials[0]==mat]
    if len(objects)>1:
        bpy.ops.object.select_all(action="DESELECT")
        for obj in objects:obj.select_set(True)
        bpy.context.view_layer.objects.active=objects[0]
        bpy.ops.object.join()

OUT.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.export_scene.gltf(filepath=str(OUT),export_format="GLB",export_apply=True,
    export_yup=True,export_image_format="AUTO",export_animations=False,
    export_cameras=False,export_lights=False)
objects=[o for o in bpy.context.scene.objects if o.type=="MESH"]
report={"file":"garden.glb","triangles":sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objects),
    "meshes":len(objects),"materials":len({m for o in objects for m in o.data.materials}),
    "imported_source":"Poly Haven Potted Plant 02 — Rico Cilliers, CC0; existing normalized derivative",
    "original_geometry":"Bentwood terrace chairs, turned pedestal table, textiles, hydrangeas, ivy, flowers, moss islands, grass blades, pavers, candleholder and cup",
    "book_surface":".59 + .37*sin(pi*t) - .19*exp(-13*t) + .018*sin(z*.8)*sin(pi*t); t=abs(x)/6.94",
    "kept_clear":["all eight room apertures","both About doors","mailbox [5.35,.83,3.65]","outer book rim","central front and rear steps"],
    "terrace_bounds_xyz":[[-6.65,terrace_y-.05,1.92],[-5.08,terrace_y+1,4.33]],
    "bytes_before_texture_packing":OUT.stat().st_size}
(OUT.parent/"garden-manifest.json").write_text(json.dumps(report,indent=2)+"\n")
print("GARDEN_EXPORT",json.dumps(report),flush=True)
