/** Geometry delivery step; Blender sources remain full-detail and independently reproducible. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const walk=dir=>fs.existsSync(dir)?fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(dir,e.name)):[path.join(dir,e.name)]):[];
const targets=process.argv.slice(2);
const all=targets.length?targets.flatMap(p=>fs.statSync(path.resolve(root,p)).isDirectory()?walk(path.resolve(root,p)):[path.resolve(root,p)]):['environment','interiors'].flatMap(p=>walk(path.join(root,'public/assets',p)));
for(const file of all.filter(p=>p.endsWith('.glb')&&!p.endsWith('.compressed.glb'))){
 const bytes=fs.readFileSync(file),doc=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)).toString());
 if(!doc.extensionsRequired?.includes('EXT_meshopt_compression')){
  const temp=file.replace(/\.glb$/,'.compressed.glb');
  const result=spawnSync(path.join(root,'node_modules/.bin/gltf-transform'),['meshopt',file,temp,'--level','medium'],{encoding:'utf8'});
  if(result.status!==0)throw Error(result.stderr||result.stdout);
  fs.renameSync(temp,file);console.log(`${path.relative(root,file)}: ${bytes.length} → ${fs.statSync(file).size} bytes`);
 }
 const meta=file.replace(/\.glb$/,'-metadata.json');
 if(fs.existsSync(meta)){const data=JSON.parse(fs.readFileSync(meta,'utf8'));data.bytes=fs.statSync(file).size;data.sha256=createHash('sha256').update(fs.readFileSync(file)).digest('hex');data.deliveryCompression='EXT_meshopt_compression';fs.writeFileSync(meta,JSON.stringify(data,null,2)+'\n');}
}
const delivery=['environment','interiors'].flatMap(p=>walk(path.join(root,'public/assets',p))).filter(p=>p.endsWith('.glb')).map(file=>{
 const bytes=fs.readFileSync(file),doc=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)).toString());
 return{path:path.relative(path.join(root,'public'),file),bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex'),meshopt:doc.extensionsRequired?.includes('EXT_meshopt_compression')??false,materials:doc.materials?.length??0,primitives:doc.meshes?.reduce((sum,m)=>sum+m.primitives.length,0)??0};
});
fs.writeFileSync(path.join(root,'public/assets/environment/delivery-manifest.json'),JSON.stringify({files:delivery,totalBytes:delivery.reduce((s,f)=>s+f.bytes,0)},null,2)+'\n');
