import { useRef,useState } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { ImportedAsset, ImportedLantern, ImportedPlant } from './ImportedAssets';
import { Box,Beam,Cylinder } from './Primitives';
import { Furniture } from './Furniture';
import { materials } from './materials';
import { useSelectable } from '../../hooks/useSelectable';
import { useWorld } from '../../hooks/useWorld';
function WeatherVane(){const ref=useRef<THREE.Group>(null),[moving,setMoving]=useState(false);const events=useSelectable('Turn the little weather vane',()=>setMoving(v=>!v));useFrame((_,dt)=>{if(ref.current&&moving&&!useWorld.getState().reducedMotion)ref.current.rotation.y+=dt*.55;});return <group position={[3.4,6.1,-.3]} {...events}><Cylinder radius={.025} height={.7} position={[0,.35,0]} material={materials.brass}/><Cylinder radius={.08} height={.06} position={[0,.25,0]} material={materials.brass}/><group ref={ref} position={[0,.65,0]}><Beam from={[-.38,0,0]} to={[.4,0,0]} width={.032} material={materials.brass}/><mesh position={[.42,0,0]} rotation={[0,0,-Math.PI/2]} material={materials.brass}><coneGeometry args={[.095,.2,3]}/></mesh><Box size={[.18,.15,.022]} position={[-.29,0,0]} material={materials.brass}/></group></group>;}
export function Scenery(){return <group>
 <ImportedPlant position={[-4.72,.62,2.65]} height={1.04} rotation={[0,.3,0]} interactive/>
 <ImportedPlant position={[-1.35,.67,2.78]} height={.77} rotation={[0,1.6,0]} interactive/>
 <ImportedPlant position={[4.65,.64,2.65]} height={.83} rotation={[0,-.4,0]} interactive/>
 <ImportedPlant position={[4.71,.61,-2.8]} height={1.04} rotation={[0,2.2,0]} interactive/>
 <ImportedPlant position={[-4.62,.64,-2.87]} height={.69} rotation={[0,.7,0]}/>
 <ImportedAsset name="oak-side-table" height={.47} position={[-4.82,.6,3.45]} rotation={[0,.3,0]}/>
 <ImportedAsset name="carved-armchair" height={.84} position={[-5.52,.58,3.14]} rotation={[0,-.65,0]}/>
 <ImportedLantern position={[-4.72,1.07,3.4]} height={.27}/>
 {/* The balcony is a real furnished recess, with enough clearance at the balustrade. */}
 <Box size={[2.0,1.76,.08]} position={[3.15,4.16,.68]} material={materials.darkWood}/>
 <Box size={[2.0,.08,1.47]} position={[3.15,3.36,1.45]} material={materials.lightWood}/>
 <ImportedAsset name="carved-armchair" height={1.04} position={[2.72,3.42,1.35]} rotation={[0,.25,0]}/>
 <ImportedAsset name="oak-side-table" height={.48} position={[3.62,3.42,1.52]}/>
 <ImportedLantern position={[3.65,3.9,1.55]} height={.37} interactive/>
 <ImportedPlant position={[4.15,3.41,2.35]} height={.69}/>
 <group position={[3.15,3.36,-2.13]} rotation={[0,Math.PI,0]}><Box size={[2,.08,1.45]} position={[0,0,-.7]} material={materials.lightWood}/><Box size={[2,1.8,.08]} position={[0,.83,-1.45]} material={materials.darkWood}/><group position={[0,.05,-.6]} scale={.82}><Furniture kind="atelier"/></group></group><WeatherVane/>
 </group>;}
