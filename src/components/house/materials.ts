import * as THREE from 'three';

/** Small, self-hosted derivatives of CC0 Poly Haven scans (see ASSET_CREDITS.md).
 * Color maps are gently neutralized so all architecture shares a controlled palette.
 * Normal and roughness maps remain linear data; albedo is explicitly sRGB.
 */
function texture(file:string,repeat:[number,number]=[1,1],color=false){
 const map = typeof document==='undefined' ? new THREE.Texture() : new THREE.TextureLoader().load(`/assets/textures/${file}.jpg`);
 map.wrapS=map.wrapT=THREE.RepeatWrapping;
 map.repeat.set(...repeat);
 map.anisotropy=4;
 map.colorSpace=color?THREE.SRGBColorSpace:THREE.NoColorSpace;
 map.magFilter=THREE.LinearFilter;
 map.minFilter=THREE.LinearMipmapLinearFilter;
 return map;
}
function surface(name:string,repeat:[number,number]=[1,1],strength=.14){
 return {
  map:texture(`${name}-color`,repeat,true),
  normalMap:texture(`${name}-normal`,repeat),
  normalScale:new THREE.Vector2(strength,strength),
  roughnessMap:texture(`${name}-roughness`,repeat),
 };
}
const plaster=surface('plaster',[2,2],.1);
const wood=surface('oak',[1,1],.12);
// A single slate face was cropped from the scan: no miniature tiled-roof pattern on every tile.
const slate=surface('slate',[1,1],.22);
const stone=surface('stone',[1,1],.17);
const cloth=surface('bookcloth',[2,2],.1);
const paper=texture('paper-color',[2,2],true);

export const materials={
 plaster:new THREE.MeshStandardMaterial({color:'#eee3ce',...plaster,roughness:1}),
 trim:new THREE.MeshStandardMaterial({color:'#f1e7d1',...stone,roughness:.96}),
 stone:new THREE.MeshStandardMaterial({color:'#d3c5ab',...stone,roughness:1}),
 wood:new THREE.MeshStandardMaterial({color:'#a77c52',...wood,roughness:.86}),
 darkWood:new THREE.MeshStandardMaterial({color:'#704d33',...wood,roughness:.92}),
 lightWood:new THREE.MeshStandardMaterial({color:'#c8a477',...wood,roughness:.88}),
 roof:new THREE.MeshStandardMaterial({color:'#405a42',...slate,roughness:.94}),
 roofEdge:new THREE.MeshStandardMaterial({color:'#2d4334',...slate,roughness:.94}),
 sage:new THREE.MeshStandardMaterial({color:'#829471',...wood,roughness:.95}),
 leaf:new THREE.MeshStandardMaterial({color:'#526b45',roughness:.95}),
 terracotta:new THREE.MeshStandardMaterial({color:'#ad795d',...plaster,roughness:1}),
 brass:new THREE.MeshStandardMaterial({color:'#b49a62',metalness:.76,roughness:.42}),
 paper:new THREE.MeshStandardMaterial({color:'#f5e8cd',map:paper,roughness:1,side:THREE.DoubleSide}),
 pageEdge:new THREE.MeshStandardMaterial({color:'#cfc0a2',map:paper,roughness:1}),
 cover:new THREE.MeshStandardMaterial({color:'#304d40',...cloth,roughness:.96}),
 cream:new THREE.MeshStandardMaterial({color:'#eee0c7',...cloth,roughness:1}),
 fabric:new THREE.MeshStandardMaterial({color:'#a3aa8b',...cloth,roughness:1}),
 ink:new THREE.MeshStandardMaterial({color:'#303e36',roughness:.8}),
 glass:new THREE.MeshStandardMaterial({color:'#d5ded5',transparent:true,opacity:.15,roughness:.13,metalness:.12,depthWrite:false}),
};
export const colored=(color:string)=>new THREE.MeshStandardMaterial({color,roughness:.88});
