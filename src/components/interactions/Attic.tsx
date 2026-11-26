import { useMemo, useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Box, Ball, Beam } from '../house/Primitives';
import { materials } from '../house/materials';
import { useSelectable } from '../../hooks/useSelectable';
import { useWorld } from '../../hooks/useWorld';
export function Attic({back=false}:{back?:boolean}){
 const rotor=useRef<THREE.Group>(null);const [spinning,setSpinning]=useState(false);const props=useSelectable('Set the attic mobile in motion',()=>setSpinning(s=>!s));
 const gable=useMemo(()=>{const s=new THREE.Shape();s.moveTo(-.89,0);s.lineTo(.89,0);s.lineTo(0,.7);s.closePath();return new THREE.ExtrudeGeometry(s,{depth:.7,bevelEnabled:false});},[]);
 useFrame((_,dt)=>{if(rotor.current&&spinning)rotor.current.rotation.y+=useWorld.getState().reducedMotion?0:dt*.9;});
 return <group rotation={[0,back?Math.PI:0,0]}><group position={[0,5.75,1.93]}>
 <Box size={[1.66,.09,1.2]} position={[0,0,0]} material={materials.trim}/>
 {[-.75,.75].map(x=><Box key={x} size={[.16,1.05,1]} position={[x,.52,0]} material={materials.plaster}/>)}
 <Box size={[1.5,1.06,.08]} position={[0,.52,-.49]} material={materials.darkWood}/>
 <mesh geometry={gable} position={[0,1.02,-.4]} material={materials.plaster} castShadow/>
 {[-1,1].map(s=><Box key={s} size={[1.23,.12,1.35]} position={[s*.46,1.39,.01]} rotation={[0,0,-s*.665]} material={materials.roof}/>)}
 <Box size={[1.62,.06,.08]} position={[0,1.02,.57]} material={materials.wood}/>
 <group {...props}><group ref={rotor} position={[0,.55,.08]}><Beam from={[-.45,.22,0]} to={[.45,.22,0]} width={.02} material={materials.brass}/><Beam from={[0,.22,-.3]} to={[0,.22,.3]} width={.02} material={materials.brass}/>{[[-.4,0,0],[.4,.1,0],[0,-.1,.28]].map((p,i)=><group key={i} position={p as [number,number,number]}><Beam from={[0,.22,0]} to={[0,-.1,0]} width={.012} material={materials.brass}/><Ball position={[0,-.15,0]} scale={[.105,.105,.035]} material={i%2?materials.brass:materials.terracotta}/></group>)}</group><Box size={[1.38,.06,.08]} position={[0,.08,.57]} material={materials.wood}/></group>
 <pointLight position={[0,.7,.25]} intensity={1.1} color="#ffc47e" distance={2}/>
 </group></group>;
}
