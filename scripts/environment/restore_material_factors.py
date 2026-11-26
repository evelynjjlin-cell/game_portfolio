"""Retain authored tint multipliers omitted by Blender's MixRGB glTF export.
Only original, named material palettes are changed; third-party materials stay untouched.
Works on both ordinary and Meshopt GLBs without touching binary geometry/image buffers.
"""
import ast,json,re,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def palette(which):
 tree=ast.parse((Path(__file__).with_name('build_interiors_'+which+'.py')).read_text());out={}
 for node in ast.walk(tree):
  if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='material' and len(node.args)>1:
   try:name,color=ast.literal_eval(node.args[0]),ast.literal_eval(node.args[1])
   except (ValueError,TypeError):continue
   if not isinstance(name,str):continue
   if isinstance(color,str):
    values=[int(color.lstrip('#')[i:i+2],16)/255 for i in (0,2,4)];color=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values]
   out[name]=list(color)+[1]
 if which=='west':
  for i,c in enumerate([(.22,.3,.25),(.47,.25,.14),(.57,.44,.24),(.32,.39,.4),(.63,.56,.39),(.38,.24,.2)]):out['Book cloth '+str(i)]=list(c)+[1]
 return out
for which,kinds in [('west',['living','bedroom','library','sunroom']),('east',['art','kitchen','music','workshop'])]:
 colors=palette(which)
 for kind in kinds:
  file=ROOT/'public/assets/interiors'/f'{kind}.glb'
  if not file.exists():continue
  raw=file.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);changed=0
  for mat in doc.get('materials',[]):
   name=re.sub(r'\.\d{3}$','',mat.get('name',''));color=colors.get(name)
   if color is None:continue
   pbr=mat.setdefault('pbrMetallicRoughness',{})
   if pbr.get('baseColorFactor')!=color:pbr['baseColorFactor']=color;changed+=1
  if changed:
   data=json.dumps(doc,separators=(',',':')).encode();data+=b' '*((-len(data))%4);tail=raw[20+n:]
   file.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
   print(f'{kind}: restored {changed} authored material factors')
