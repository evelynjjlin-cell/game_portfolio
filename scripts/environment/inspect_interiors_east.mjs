/** Validate exported room bounds, embedded assets and named animation pivots.
 * Run: node scripts/environment/inspect_interiors_east.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {NodeIO} from '@gltf-transform/core';
import {ALL_EXTENSIONS} from '@gltf-transform/extensions';
import {MeshoptDecoder} from 'meshoptimizer';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
await MeshoptDecoder.ready;
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.decoder':MeshoptDecoder});
const reports=[];
for(const kind of ['art','kitchen','music','workshop']){
 const filename=path.join(root,'public/assets/interiors',kind+'.glb');
 const meta=JSON.parse(fs.readFileSync(filename.replace('.glb','-metadata.json'),'utf8'));
 const bytes=fs.readFileSync(filename),json=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)));
 if((json.images??[]).some(x=>x.uri)||(json.buffers??[]).some(x=>x.uri))throw Error(kind+' contains external resource');
 const doc=await io.read(filename),min=[Infinity,Infinity,Infinity],max=[-Infinity,-Infinity,-Infinity];
 let primitives=0,triangles=0;
 for(const node of doc.getRoot().listNodes()){
  const mesh=node.getMesh();if(!mesh)continue;
  const m=node.getWorldMatrix();
  for(const primitive of mesh.listPrimitives()){
   primitives++;
   const position=primitive.getAttribute('POSITION');
   triangles+=(primitive.getIndices()?.getCount()??position.getCount())/3;
   const a=[];
   for(let j=0;j<position.getCount();j++){
    position.getElement(j,a);
    const p=[m[0]*a[0]+m[4]*a[1]+m[8]*a[2]+m[12],m[1]*a[0]+m[5]*a[1]+m[9]*a[2]+m[13],m[2]*a[0]+m[6]*a[1]+m[10]*a[2]+m[14]];
    for(let k=0;k<3;k++){if(!Number.isFinite(p[k]))throw Error(kind+' has nonfinite vertex');min[k]=Math.min(min[k],p[k]);max[k]=Math.max(max[k],p[k]);}
   }
  }
 }
 if(min[0]<-meta.width/2-.12||max[0]>meta.width/2+.12||min[1]<-.1||max[1]>meta.height+.12||min[2]<-meta.depth-.12||max[2]>.04)throw Error(kind+' out of bounds '+JSON.stringify({min,max}));
 const pivots={};for(const name of meta.dynamicNodes??[]){const node=doc.getRoot().listNodes().find(n=>n.getName()===name);if(!node)throw Error('Missing dynamic '+name);pivots[name]={translation:node.getTranslation(),rotation:node.getRotation()};}
 reports.push({kind,bytes:bytes.length,triangles,primitives,textures:doc.getRoot().listTextures().length,bounds:{min,max},pivots});
}
console.log(JSON.stringify(reports,null,2));
