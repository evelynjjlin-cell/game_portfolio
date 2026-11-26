import { useMemo } from 'react';
import { useGLTF } from '@react-three/drei';
import * as THREE from 'three';
export function BookAsset(){
 const {scene}=useGLTF('/assets/environment/book.glb',false,true);
 const model=useMemo(()=>{const copy=scene.clone(true);copy.traverse(o=>{if(o instanceof THREE.Mesh){o.castShadow=o.receiveShadow=true;const ms=Array.isArray(o.material)?o.material:[o.material];ms.forEach(m=>{if(m instanceof THREE.MeshStandardMaterial){m.envMapIntensity=.4;if(m.map)m.map.anisotropy=4;}});}});return copy;},[scene]);
 return <primitive object={model} dispose={null}/>;
}
