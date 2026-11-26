import { useMemo,useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Box, Cylinder, Beam } from '../house/Primitives';
import { archShape,archFrameGeometry,extrudeProfile } from '../house/ArchShapes';
import { materials } from '../house/materials';
import { useWorld } from '../../hooks/useWorld';
import { useSelectable } from '../../hooks/useSelectable';
export function Entrance({back=false}:{back?:boolean}){
 const hinge=useRef<THREE.Group>(null);const light=useRef<THREE.PointLight>(null);
 const props=useSelectable('Come in · About Evelyn',()=>useWorld.getState().openDialog('about'));
 const panel=useMemo(()=>extrudeProfile(archShape(1.67,2.2,.8),.08,.015),[]);
 const frame=useMemo(()=>archFrameGeometry(1.85,2.32,.85,.085,.18),[]);
 useFrame((_,dt)=>{const s=useWorld.getState(),open=s.dialog==='about';if(hinge.current)hinge.current.rotation.y=THREE.MathUtils.damp(hinge.current.rotation.y,open?-1.45:0,s.reducedMotion?1000:5,dt);if(light.current)light.current.intensity=THREE.MathUtils.damp(light.current.intensity,open?6:s.evening?4:2.5,5,dt);});
 return <group position={[.15,1.94,back?-2.4:2.4]} rotation={[0,back?Math.PI:0,0]} {...props}>
 <Box size={[1.85,2.3,.1]} position={[0,0,-1.3]} material={materials.darkWood}/><Box size={[1.86,.09,1.4]} position={[0,-1.12,-.6]} material={materials.lightWood}/>
 <mesh geometry={frame} material={materials.wood} castShadow receiveShadow/>
 <group ref={hinge} position={[-.835,0,.19]}><group position={[.835,0,0]}>
 <mesh geometry={panel} material={materials.wood} castShadow receiveShadow/>
 {Array.from({length:9},(_,i)=><Box key={i} size={[.008,1.4,.015]} position={[-.7+i*.175,-.33,.095]} material={materials.darkWood} radius={.002}/>)}
 {[-.75,.15].map(y=><Box key={y} size={[1.48,.08,.06]} position={[0,y,.11]} material={materials.darkWood}/>)}
 <mesh position={[0,.53,.1]} material={materials.glass}><circleGeometry args={[.39,32]}/></mesh><mesh position={[0,.53,.12]} material={materials.darkWood}><torusGeometry args={[.4,.045,8,32]}/></mesh>
 <Box size={[.03,.75,.04]} position={[0,.53,.12]} material={materials.wood}/><Box size={[.75,.03,.04]} position={[0,.53,.12]} material={materials.wood}/>
 <Box size={[.1,.29,.035]} position={[.61,-.18,.12]} material={materials.brass}/><Cylinder radius={.027} height={.17} position={[.61,-.15,.2]} material={materials.brass}/>
 <Box size={[.35,.07,.035]} position={[0,-.22,.12]} material={materials.brass}/>
 </group></group>
 {[-.69,.55].map(y=><Cylinder key={y} radius={.035} height={.19} position={[-.84,y,.22]} material={materials.brass}/>)}
 {[-1,1].map(s=><group key={s} position={[s*1.08,.25,.07]}><Beam from={[0,.32,-.03]} to={[0,.45,.22]} width={.04} material={materials.brass}/><Box size={[.27,.39,.27]} position={[0,.13,.22]} material={materials.glass}/>{[-.12,.12].flatMap(x=>[-.12,.12].map(z=><Box key={`${x}${z}`} size={[.022,.39,.022]} position={[x,.13,.22+z]} material={materials.brass}/>))}<mesh position={[0,.36,.22]} material={materials.brass}><coneGeometry args={[.23,.16,4]}/></mesh><Cylinder radius={.1} height={.035} position={[0,-.1,.22]} material={materials.brass}/><mesh position={[0,.1,.22]}><sphereGeometry args={[.07,12,8]}/><meshStandardMaterial color="#ffe0a1" emissive="#ffbc58" emissiveIntensity={1.5}/></mesh></group>)}
 <pointLight ref={light} position={[0,.6,.3]} color="#ffc271" intensity={2.5} distance={3}/>
 </group>;
}
