import { useMemo } from 'react';
import * as THREE from 'three';
import { Box, Repeated, type Piece } from './Primitives';
import { materials } from './materials';
/** Swept page sections form a closed volume, including curved top and fore-edge. */
function leafGeometry(side:number,cover=false){
 const shape=new THREE.Shape();const width=cover?5.95:5.76;const lower=cover?.06:.18;
 shape.moveTo(0,lower);shape.lineTo(width,lower+.02);shape.lineTo(width,cover?.2:.46);
 for(let i=40;i>=0;i--){const t=i/40;const y=cover?.2+.04*Math.sin(t*Math.PI):.46+.24*Math.sin(t*Math.PI*.88)-.19*Math.exp(-t*12);shape.lineTo(t*width,y);}
 shape.closePath();const geo=new THREE.ExtrudeGeometry(shape,{depth:cover?8.05:7.78,bevelEnabled:true,bevelSize:cover?.04:.025,bevelThickness:cover?.04:.02,bevelSegments:2,steps:1});geo.translate(0,0,cover?-4.025:-3.89);if(side<0){geo.scale(-1,1,1);geo.computeVertexNormals();}return geo;
}
export function OpenBook(){
 const pages=useMemo(()=>[leafGeometry(1),leafGeometry(-1)],[]);const covers=useMemo(()=>[leafGeometry(1,true),leafGeometry(-1,true)],[]);
 const strata=useMemo(()=>Array.from({length:17},(_,i)=>({position:[0,.205+i*.014,0] as [number,number,number]})),[]);
 const edgeLines:Piece[]=strata.flatMap(p=>[-1,1].map(side=>({position:[side*2.89,p.position[1],3.908],scale:[1,1,1]})));
 return <group>
  {covers.map((g,i)=><mesh key={`cover${i}`} geometry={g} material={materials.cover} castShadow receiveShadow/>)}
  {pages.map((g,i)=><mesh key={i} geometry={g} material={materials.paper} castShadow receiveShadow/>)}
  <Repeated size={[5.72,.008,.009]} pieces={edgeLines} material={materials.pageEdge}/>
  <group rotation={[0,Math.PI,0]}><Repeated size={[5.72,.008,.009]} pieces={edgeLines} material={materials.pageEdge}/></group>
  {[-1,1].map(side=><group key={side}><Repeated size={[.009,.008,7.75]} pieces={strata.map(p=>({position:[side*5.785,p.position[1],0]}))} material={materials.pageEdge}/><Box size={[.02,.035,7.9]} position={[side*.09,.2,0]} material={materials.darkWood}/></group>)}
  <mesh position={[0,.14,0]} rotation={[Math.PI/2,0,0]} material={materials.cover} receiveShadow><cylinderGeometry args={[.22,.22,8.04,24,1,false,0,Math.PI]}/></mesh>
  <Box size={[.35,.018,1.05]} position={[.55,.14,4.24]} rotation={[0,-.08,0]} material={materials.terracotta}/>
  <Box size={[.38,.02,.04]} position={[.59,.155,4.74]} material={materials.brass}/>
 </group>;
}
