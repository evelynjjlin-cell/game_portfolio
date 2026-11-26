import { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Box, Cylinder, Repeated } from '../house/Primitives';
import { materials } from '../house/materials';
import type { RoomConfig } from '../../config/rooms';
import { useWorld } from '../../hooks/useWorld';
function GlazedLeaf({side}:{side:number}){return <group position={[-side*.465,0,0]}>
 <Box size={[.92,1.76,.065]} material={materials.glass} castShadow={false}/>
 {[-.43,.43].map(x=><Box key={x} size={[.065,1.8,.09]} position={[x,0,0]} material={materials.wood}/>)}
 {[-.86,-.35,.3,.86].map(y=><Box key={y} size={[.92,.055,.09]} position={[0,y,0]} material={materials.wood}/>)}
 <Box size={[.76,.43,.055]} position={[0,-.6,0]} material={materials.wood}/>
 <Box size={[.62,.3,.045]} position={[0,-.6,.048]} material={materials.lightWood}/>
 <Cylinder radius={.025} height={.19} position={[-side*.29,-.12,.09]} material={materials.brass}/>
 <Cylinder radius={.035} height={.03} position={[-side*.29,-.12,.063]} rotation={[Math.PI/2,0,0]} material={materials.brass}/>
 </group>;}
function Shutter({side}:{side:number}){const slats=useMemo(()=>Array.from({length:11},(_,i)=>({position:[-side*.23,-.69+i*.138,0] as [number,number,number],rotation:[.22,0,0] as [number,number,number]})),[side]);return <group>
 {[-.02,-side*.45].map((x,i)=><Box key={i} size={[.055,1.86,.075]} position={[x,0,0]} material={materials.roof}/>)}
 {[-.9,.9].map(y=><Box key={y} size={[.48,.065,.075]} position={[-side*.23,y,0]} material={materials.roof}/>)}
 <Repeated size={[.4,.12,.045]} pieces={slats} material={materials.roof}/>
 </group>;}
export function HingedWindow({room}:{room:RoomConfig}){
 const leaves=useRef<(THREE.Group|null)[]>([]);const shutters=useRef<(THREE.Group|null)[]>([]);const amount=useRef(0);
 useFrame((_,dt)=>{
  const s=useWorld.getState(),phase=s.phases[room.id];const target=phase==='opening'||phase==='open'?1:0;
  amount.current=s.reducedMotion?target:THREE.MathUtils.clamp(amount.current+(target?1:-1)*Math.min(dt,.05)/room.animation.duration,0,1);
  const t=amount.current*amount.current*(3-2*amount.current);
  [-1,1].forEach((side,index)=>{const leaf=leaves.current[index],shutter=shutters.current[index];if(leaf)leaf.rotation.y=side*(.035+t*1.45);if(shutter)shutter.rotation.y=side*(.19+t*room.animation.angle);});
  if(amount.current===target&&(phase==='opening'||phase==='closing'))s.finish(room.id,target?'open':'idle');
 });
 return <group>{[-1,1].map((side,index)=><group key={side}>
  <group position={[side*.94,0,.13]} ref={el=>{leaves.current[index]=el;}}><GlazedLeaf side={side}/></group>
  <group position={[side*1.1,0,.24]} ref={el=>{shutters.current[index]=el;}}><Shutter side={side}/></group>
  {[-.65,.65].map(y=><Cylinder key={y} radius={.035} height={.13} position={[side*1.09,y,.245]} material={materials.brass}/>)}
 </group>)}</group>;
}
