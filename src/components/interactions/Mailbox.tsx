import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Box, Cylinder } from '../house/Primitives';
import { materials } from '../house/materials';
import { useWorld } from '../../hooks/useWorld';
import { useSelectable } from '../../hooks/useSelectable';
export function Mailbox(){
 const door=useRef<THREE.Group>(null),letter=useRef<THREE.Group>(null);const open=useWorld(s=>s.dialog==='contact');const props=useSelectable('Open the mailbox · Contact Evelyn',()=>useWorld.getState().openDialog('contact'));
 useFrame((_,dt)=>{const speed=useWorld.getState().reducedMotion?1000:6;if(door.current)door.current.rotation.x=THREE.MathUtils.damp(door.current.rotation.x,open?1.45:0,speed,dt);if(letter.current){letter.current.position.z=THREE.MathUtils.damp(letter.current.position.z,open?.48:0,speed,dt);letter.current.position.y=THREE.MathUtils.damp(letter.current.position.y,open?.18:0,speed,dt);}});
 return <group position={[5.35,.83,3.65]} rotation={[0,.1,0]} {...props}>
 <Cylinder radius={.09} height={.86} position={[0,.43,0]} material={materials.wood}/><Cylinder radius={.2} height={.05} position={[0,.025,0]} material={materials.stone}/>
 <Box size={[.8,.07,.8]} position={[0,.9,0]} material={materials.roofEdge}/>
 {[-1,1].map(s=><Box key={s} size={[.06,.52,.75]} position={[s*.37,1.18,0]} material={materials.roof}/>)}
 <Box size={[.76,.53,.06]} position={[0,1.18,-.37]} material={materials.roof}/>
 <mesh position={[0,1.43,0]} rotation={[Math.PI/2,0,0]} material={materials.roof} castShadow><cylinderGeometry args={[.4,.4,.83,28,1,false,Math.PI/2,Math.PI]}/></mesh>
 <group ref={letter}><Box size={[.53,.33,.025]} position={[0,1.16,.12]} rotation={[-.22,0,0]} material={materials.paper}/><mesh position={[0,1.16,.145]} rotation={[-.22,0,Math.PI]} material={materials.cream}><circleGeometry args={[.23,3]}/></mesh><Cylinder radius={.045} height={.012} position={[0,1.17,.157]} rotation={[Math.PI/2,0,0]} material={materials.terracotta}/></group>
 <group ref={door} position={[0,.94,.42]}><Box size={[.73,.54,.055]} position={[0,.27,0]} radius={.06} material={materials.roof}/><Box size={[.3,.065,.035]} position={[0,.42,.05]} material={materials.brass}/><Box size={[.22,.1,.015]} position={[0,.2,.04]} material={materials.cream}/></group>
 <Box size={[.035,.44,.035]} position={[.43,1.34,0]} material={materials.brass}/><Box size={[.16,.15,.035]} position={[.49,1.55,0]} material={materials.terracotta}/>
 </group>;
}
