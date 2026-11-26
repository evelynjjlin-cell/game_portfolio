import {useMemo} from 'react';
import {useGLTF} from '@react-three/drei';
import * as THREE from 'three';
export function GardenAsset(){
 const {scene}=useGLTF('/assets/environment/garden.glb',false,true);
 const model=useMemo(()=>{const copy=scene.clone(true);copy.traverse(o=>{if(o instanceof THREE.Mesh){o.castShadow=o.receiveShadow=true;for(const m of Array.isArray(o.material)?o.material:[o.material]){if(m instanceof THREE.MeshStandardMaterial){m.envMapIntensity=.35;if(m.map)m.map.anisotropy=4;if(m.transparent){o.castShadow=false;m.depthWrite=false;}}}}});return copy;},[scene]);
 return <primitive object={model} dispose={null}/>;
}
