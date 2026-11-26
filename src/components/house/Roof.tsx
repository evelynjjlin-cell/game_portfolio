import { useMemo } from 'react';
import * as THREE from 'three';
import { Box, Beam, Repeated, type Piece } from './Primitives';
import { materials } from './materials';
/** Original modular pitched roof; overlapping slate geometry shares three instanced draws. */
export function Roof({position=[0,0,0],width,depth,rise,rotation=0}:{position?:[number,number,number];width:number;depth:number;rise:number;rotation?:number}){
 const half=width/2,angle=Math.atan2(rise,half),slope=Math.hypot(half,rise);
 const cols=Math.ceil(depth/.37),rows=Math.ceil(slope/.36),tileWidth=depth/cols;
 const tiles=useMemo(()=>{const groups:Piece[][]=[[],[],[]];for(const side of [-1,1])for(let row=0;row<rows;row++)for(let col=0;col<cols;col++){
 const dist=(row+.48)*slope/rows,x=side*dist*Math.cos(angle),y=rise-dist*Math.sin(angle)+.07;
 groups[(col*7+row*11+(side+1))%3].push({position:[x,y,-depth/2+(col+.5)*tileWidth],rotation:[0,0,-side*angle]});}return groups;},[width,depth,rise]);
 const variants=useMemo(()=>[materials.roof,...[.91,1.07].map(v=>{const m=materials.roof.clone();m.color.multiplyScalar(v);return m;})],[]);
 return <group position={position} rotation={[0,rotation,0]}>
 {[-1,1].map(s=><group key={s}>
 <Box size={[slope,.14,depth]} position={[s*half/2,rise/2,0]} rotation={[0,0,-s*angle]} material={materials.roofEdge}/>
 <Box size={[.12,.15,depth+.1]} position={[s*half,-.04,0]} material={materials.wood}/>
 {[-1,1].map(z=><group key={z}><Beam from={[0,rise+.03,z*depth/2]} to={[s*half,-.06,z*depth/2]} width={.16} material={materials.wood}/><Beam from={[0,rise+.11,z*(depth/2+.01)]} to={[s*half,.02,z*(depth/2+.01)]} width={.04} material={materials.lightWood}/></group>)}
 </group>)}
 {tiles.map((pieces,i)=><Repeated key={i} size={[slope/rows+.14,.045,tileWidth-.014]} pieces={pieces} material={variants[i]}/>)}
 <mesh position={[0,rise+.09,0]} rotation={[Math.PI/2,0,0]} material={materials.roofEdge} castShadow><cylinderGeometry args={[.12,.12,depth+.14,12,1,false,0,Math.PI]}/></mesh>
 {[-1,1].map(z=><Box key={z} size={[.22,.11,.17]} position={[0,rise+.07,z*depth/2]} material={materials.brass}/>)}
 </group>;
}
