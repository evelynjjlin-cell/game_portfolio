import * as THREE from 'three';
/** Seeded, tiny local surface maps: no network assets or runtime image services. */
function surface(kind:'paper'|'plaster'|'wood'|'cloth'){
 const size=128,data=new Uint8Array(size*size*4);let seed=22;
 for(let y=0;y<size;y++)for(let x=0;x<size;x++){seed=(seed*16807)%2147483647;const noise=seed/2147483647;const weave=kind==='cloth'?((x%3===0?-.1:0)+(y%3===0?-.08:0)):kind==='wood'?Math.sin(x*.65+Math.sin(y*.03)*2)*.05:0;const v=Math.round(244+noise*10+weave*35);const i=(y*size+x)*4;data[i]=data[i+1]=data[i+2]=v;data[i+3]=255;}
 const map=new THREE.DataTexture(data,size,size);map.wrapS=map.wrapT=THREE.RepeatWrapping;map.repeat.set(kind==='wood'?2:4,kind==='wood'?1:4);map.magFilter=THREE.LinearFilter;map.minFilter=THREE.LinearMipmapLinearFilter;map.generateMipmaps=true;map.needsUpdate=true;map.colorSpace=THREE.SRGBColorSpace;return map;
}
const plaster=surface('plaster'),paper=surface('paper'),wood=surface('wood'),cloth=surface('cloth');
export const materials={
 plaster:new THREE.MeshStandardMaterial({color:'#e9dec7',map:plaster,roughness:.92}),
 trim:new THREE.MeshStandardMaterial({color:'#f4e9d2',roughness:.75}),
 stone:new THREE.MeshStandardMaterial({color:'#c5bcaa',roughness:.95}),
 wood:new THREE.MeshStandardMaterial({color:'#9a6945',map:wood,roughness:.7}),
 darkWood:new THREE.MeshStandardMaterial({color:'#694933',map:wood,roughness:.77}),
 lightWood:new THREE.MeshStandardMaterial({color:'#c49b69',map:wood,roughness:.7}),
 roof:new THREE.MeshStandardMaterial({color:'#284b40',map:cloth,roughness:.85}),
 roofEdge:new THREE.MeshStandardMaterial({color:'#203f35',roughness:.7}),
 sage:new THREE.MeshStandardMaterial({color:'#8a9c7b',roughness:.92}),
 leaf:new THREE.MeshStandardMaterial({color:'#4e6947',roughness:.9}),
 terracotta:new THREE.MeshStandardMaterial({color:'#ab7258',roughness:1}),
 brass:new THREE.MeshStandardMaterial({color:'#bc9654',metalness:.65,roughness:.35}),
 paper:new THREE.MeshStandardMaterial({color:'#eee2c6',map:paper,roughness:1,side:THREE.DoubleSide}),
 pageEdge:new THREE.MeshStandardMaterial({color:'#c9bda0',roughness:1}),
 cover:new THREE.MeshStandardMaterial({color:'#4f6961',map:cloth,roughness:1}),
 cream:new THREE.MeshStandardMaterial({color:'#eee0c2',roughness:.95}),
 fabric:new THREE.MeshStandardMaterial({color:'#a5ad91',map:cloth,roughness:1}),
 ink:new THREE.MeshStandardMaterial({color:'#303e36',roughness:.65}),
 glass:new THREE.MeshStandardMaterial({color:'#b2c5ac',transparent:true,opacity:.22,roughness:.18,metalness:.08,depthWrite:false}),
};
export const colored=(color:string)=>new THREE.MeshStandardMaterial({color,roughness:.88});
