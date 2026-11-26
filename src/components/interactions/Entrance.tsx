import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Box, Ball, Cylinder } from '../house/Primitives';
import { materials } from '../house/materials';
import { useWorld } from '../../hooks/useWorld';
import { useSelectable } from '../../hooks/useSelectable';
export function Entrance({back=false}:{back?:boolean}){
 const door=useRef<THREE.Group>(null);const open=useWorld(s=>s.dialog==='about');const props=useSelectable('Come in · About Evelyn',()=>useWorld.getState().openDialog('about'));
 useFrame((_,dt)=>{if(door.current)door.current.rotation.y=THREE.MathUtils.damp(door.current.rotation.y,open?-1.25:0,useWorld.getState().reducedMotion?1000:6,dt);});
 return <group rotation={[0,back?Math.PI:0,0]}>
 <group position={[0,1.69,2.31]} {...props}>
 <Box size={[1.11,1.94,.06]} position={[0,0,-.46]} material={materials.darkWood}/>
 <Box size={[.83,1.66,.07]} position={[0,0,-.42]} material={materials.wood}/>
 <group ref={door} position={[-.51,0,.04]}><group position={[.51,0,0]}><Box size={[1.02,1.9,.1]} material={materials.wood}/>{[-.55,.04].map(y=><Box key={y} size={[.78,.44,.06]} position={[0,y,.07]} material={materials.lightWood}/>)}<Box size={[.77,.42,.04]} position={[0,.63,.055]} material={materials.glass}/><Box size={[.035,.42,.06]} position={[0,.63,.08]} material={materials.wood}/><Ball position={[.34,-.08,.14]} scale={[.05,.05,.05]} material={materials.brass}/><Box size={[.23,.04,.02]} position={[0,.04,.105]} material={materials.brass}/></group></group>
 {[-.57,.57].map(x=><Box key={x} size={[.09,2.08,.22]} position={[x,0,0]} material={materials.trim}/>)}
 <Box size={[1.23,.1,.22]} position={[0,1.01,0]} material={materials.trim}/>
 {[-.67,.67].map(y=><Cylinder key={y} radius={.035} height={.12} position={[-.51,y,.09]} material={materials.brass}/>)}
 </group>
 <group position={[.92,2.32,2.47]}><Box size={[.11,.35,.09]} material={materials.brass}/><mesh position={[0,0,.06]}><boxGeometry args={[.17,.23,.14]}/><meshStandardMaterial color="#f4d8a2" emissive="#ffc47a" emissiveIntensity={.5}/></mesh><Box size={[.24,.035,.23]} position={[0,.14,.05]} material={materials.roof}/></group>
 <mesh position={[0,4.15,2.32]} material={materials.wood}><torusGeometry args={[.34,.045,12,32]}/></mesh>
 <mesh position={[0,4.15,2.3]} material={materials.glass}><circleGeometry args={[.31,32]}/></mesh><Box size={[.035,.62,.05]} position={[0,4.15,2.34]} material={materials.wood}/><Box size={[.62,.035,.05]} position={[0,4.15,2.34]} material={materials.wood}/>
 </group>;
}
