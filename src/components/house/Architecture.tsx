import { useMemo } from 'react';
import * as THREE from 'three';
import { Box, Beam, Repeated, type Piece } from './Primitives';
import { materials } from './materials';
import { Plant } from './Furniture';
function Gable({side}:{side:number}){const g=useMemo(()=>{const s=new THREE.Shape();s.moveTo(-2.28,0);s.lineTo(2.28,0);s.lineTo(0,1.8);s.closePath();return new THREE.ExtrudeGeometry(s,{depth:.18,bevelEnabled:false});},[]);return <mesh position={[side*3.8,5.48,0]} rotation={[0,Math.PI/2,0]} geometry={g} material={materials.plaster} castShadow receiveShadow/>;}
export function Architecture(){
 const tiles=useMemo(()=>{const pieces:Piece[]=[];for(const side of [-1,1])for(let row=0;row<8;row++)for(let col=0;col<20;col++){const z=.1+row*.325;pieces.push({position:[-4.12+col*.433+(row%2)*.08,7.39-z*.71,side*z],rotation:[side*.617,0,0]});}return pieces;},[]);
 const boards=useMemo(()=>[.67,3.01,5.43].flatMap(y=>Array.from({length:21},(_,i)=>({position:[-3.7+i*.37,y,0] as [number,number,number]}))),[]);
 return <group>
  <Box size={[8.1,.18,4.9]} position={[0,.56,0]} material={materials.stone}/>
  <Repeated size={[.355,.07,4.36]} pieces={boards} material={materials.lightWood}/>
  <Box size={[7.7,4.8,.14]} position={[0,3.03,0]} material={materials.plaster}/>
  {[-1,1].map(s=><group key={`side${s}`}><Box size={[.2,4.8,4.6]} position={[s*3.85,3.06,0]} material={materials.plaster}/><Gable side={s}/><group position={[s*3.98,3.1,0]} rotation={[0,s*Math.PI/2,0]}><Box size={[1.14,1.55,.08]} material={materials.darkWood}/><Box size={[.96,1.36,.08]} position={[0,0,.045]} material={materials.glass}/>{[-.55,.55].map(x=><Box key={x} size={[.08,1.63,.18]} position={[x,0,.1]} material={materials.trim}/>)}{[-.77,0,.77].map(y=><Box key={y} size={[1.2,.07,.18]} position={[0,y,.1]} material={materials.trim}/>)}<Box size={[.04,1.5,.15]} position={[0,0,.12]} material={materials.wood}/><Box size={[1.4,.12,.35]} position={[0,-.87,.07]} material={materials.stone}/></group><Beam from={[s*3.98,5.55,-2.17]} to={[s*3.98,7.18,0]} width={.09} material={materials.wood}/><Beam from={[s*3.98,7.18,0]} to={[s*3.98,5.55,2.17]} width={.09} material={materials.wood}/><Beam from={[s*3.99,5.5,0]} to={[s*3.99,7.18,0]} width={.08} material={materials.wood}/></group>)}
  {[-1,1].map(s=><group key={`facade${s}`} rotation={[0,s===-1?Math.PI:0,0]}>
   {[-2.2,2.2].map(x=><group key={x}>
    <Box size={[3,.19,.2]} position={[x,.78,2.18]} material={materials.plaster}/>
    <Box size={[3,.55,.2]} position={[x,2.88,2.18]} material={materials.plaster}/>
    <Box size={[3,.54,.2]} position={[x,5.23,2.18]} material={materials.plaster}/>
    {[-1.27,1.27].map(off=><Box key={off} size={[.6,4.7,.2]} position={[x+off,3.03,2.18]} material={materials.plaster}/>)}
   </group>)}
   <Box size={[1.4,2.9,.22]} position={[0,4.06,2.18]} material={materials.plaster}/>
   {[-.6,.6].map(x=><Box key={x} size={[.17,2.05,.23]} position={[x,1.63,2.18]} material={materials.plaster}/>)}
   {[-3.82,3.82].map(x=><group key={x}><Box size={[.12,4.85,.16]} position={[x,3.05,2.32]} material={materials.trim}/>{Array.from({length:9},(_,i)=><Box key={i} size={[.34,.19,.12]} position={[x,i*.52+.9,2.35]} material={materials.stone}/>)}</group>)}
   {[.75,2.98,5.48].map(y=><group key={y}><Box size={[8.05,.12,4.8]} position={[0,y,0]} material={materials.trim}/><Box size={[8.14,.045,4.88]} position={[0,y+.07,0]} material={materials.lightWood}/></group>)}
   <Box size={[1.7,.12,.95]} position={[0,.64,2.68]} material={materials.stone}/><Box size={[1.94,.1,.52]} position={[0,.55,3.15]} material={materials.stone}/>
   <Box size={[1.44,.12,.72]} position={[0,2.87,2.45]} rotation={[.08,0,0]} material={materials.roof}/><Beam from={[-.55,2.45,2.35]} to={[-.55,2.81,2.69]} material={materials.wood}/><Beam from={[.55,2.45,2.35]} to={[.55,2.81,2.69]} material={materials.wood}/>
   {[-1,1].map(k=><Plant key={k} position={[k*1.12,.7,2.9]} scale={.73} interactive/>)}
  </group>)}
  {[-1,1].map(s=><group key={`roof${s}`}><Box size={[8.75,.16,3.2]} position={[0,6.38,s*1.34]} rotation={[s*.617,0,0]} material={materials.roofEdge}/><Box size={[8.85,.14,.12]} position={[0,5.4,s*2.72]} material={materials.roofEdge}/>{[-4.31,4.31].map(x=><Beam key={x} from={[x,7.38,0]} to={[x,5.44,s*2.72]} width={.13} material={materials.roofEdge}/>)}</group>)}
  <Repeated size={[.43,.045,.45]} pieces={tiles} material={materials.roof}/><Box size={[8.9,.16,.2]} position={[0,7.42,0]} material={materials.roofEdge}/>
  <group position={[-2.7,7.1,-.45]}><Box size={[.65,1.9,.68]} material={materials.stone}/>{[-.65,-.35,-.05,.25,.55,.85].map(y=><Box key={y} size={[.67,.025,.7]} position={[0,y,0]} material={materials.cream}/>)}<Box size={[.84,.16,.88]} position={[0,.96,0]} material={materials.trim}/>{[-.18,.18].map(x=><mesh key={x} position={[x,1.16,0]} material={materials.terracotta} castShadow><cylinderGeometry args={[.13,.15,.35,16]}/></mesh>)}</group>
 </group>;
}
