import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { useWorld } from '../../hooks/useWorld';
import { lighting } from '../../config/lighting';
export function SceneLighting(){
 const ambient=useRef<THREE.AmbientLight>(null),sun=useRef<THREE.DirectionalLight>(null),fill=useRef<THREE.DirectionalLight>(null);
 useFrame((_,dt)=>{const s=useWorld.getState(),l=lighting[s.evening?'evening':'daylight'],speed=s.reducedMotion?1000:4;if(ambient.current)ambient.current.intensity=THREE.MathUtils.damp(ambient.current.intensity,l.ambient,speed,dt);if(sun.current)sun.current.intensity=THREE.MathUtils.damp(sun.current.intensity,l.sun,speed,dt);if(fill.current)fill.current.intensity=THREE.MathUtils.damp(fill.current.intensity,l.fill,speed,dt);});
 return <><ambientLight ref={ambient} intensity={lighting.daylight.ambient}/><hemisphereLight args={['#dae4e9','#b1a18a',.65]}/><directionalLight ref={sun} castShadow position={[-5,12,8]} intensity={3.5} color="#fff0d5" shadow-mapSize={[2048,2048]} shadow-camera-left={-10} shadow-camera-right={10} shadow-camera-top={12} shadow-camera-bottom={-8} shadow-camera-near={1} shadow-camera-far={35} shadow-bias={-.0001} shadow-normalBias={.035} shadow-radius={3}/><directionalLight ref={fill} position={[8,7,-8]} intensity={1.1} color="#d4e3f1"/></>;
}
