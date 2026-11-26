import { useEffect, useRef } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import type { OrbitControls as Controls } from 'three-stdlib';
import * as THREE from 'three';
import { useWorld } from '../../hooks/useWorld';
import { roomById } from '../../config/rooms';
type Pose={position:THREE.Vector3;target:THREE.Vector3};
type Flight={from:Pose;to:Pose;t:number};
const center=new THREE.Vector3(0,3.1,0);
export function CameraRig(){
 const controls=useRef<Controls>(null);const {camera,size}=useThree();const active=useWorld(s=>s.activeRoom);const view=useWorld(s=>s.view);const dialog=useWorld(s=>s.dialog);const reduced=useWorld(s=>s.reducedMotion);
 const flight=useRef<Flight|null>(null);const previous=useRef<Pose|null>(null);const lastView=useRef(view.key);const initialized=useRef(false);
 const scale=Math.max(1,Math.min(2.05,1.22/(size.width/size.height)));
 const pose=():Pose=>({position:camera.position.clone(),target:controls.current?.target.clone()??center.clone()});
 const go=(to:Pose)=>{if(controls.current){controls.current.autoRotate=false;controls.current.enableDamping=false;controls.current.update();}flight.current={from:pose(),to,t:0};};
 useEffect(()=>{const to={position:new THREE.Vector3(9.5,8.1,19.5).sub(center).multiplyScalar(scale).add(center),target:center.clone()};if(!initialized.current){camera.position.copy(to.position);controls.current?.target.copy(to.target);controls.current?.update();initialized.current=true;}else if(!active)go(to);},[scale]);
 useEffect(()=>{
  if(active){if(!previous.current)previous.current=pose();const room=roomById[active];const target=new THREE.Vector3(...room.camera.target);const position=new THREE.Vector3(...room.camera.position).sub(target).multiplyScalar(scale).add(target);go({position,target});}
  else if(previous.current){go(previous.current);previous.current=null;}
 },[active]);
 useEffect(()=>{if(view.key===lastView.current)return;lastView.current=view.key;previous.current=null;const position=view.name==='front'?new THREE.Vector3(5.6,7.8,20.5):view.name==='back'?new THREE.Vector3(-6.5,8,-20):new THREE.Vector3(9.5,8.1,19.5);go({position:position.sub(center).multiplyScalar(scale).add(center),target:center.clone()});},[view]);
 useFrame((_,dt)=>{
  const f=flight.current,c=controls.current;if(!c)return;c.dampingFactor=1-Math.exp(-5*dt);if(!f)return;
  f.t=reduced?1:Math.min(1,f.t+dt/1.15);const t=f.t*f.t*(3-2*f.t);
  const from=new THREE.Spherical().setFromVector3(f.from.position.clone().sub(center));const to=new THREE.Spherical().setFromVector3(f.to.position.clone().sub(center));
  let angle=to.theta-from.theta;angle=THREE.MathUtils.euclideanModulo(angle+Math.PI,Math.PI*2)-Math.PI;
  const current=new THREE.Spherical(THREE.MathUtils.lerp(from.radius,to.radius,t),THREE.MathUtils.lerp(from.phi,to.phi,t),from.theta+angle*t);
  camera.position.setFromSpherical(current).add(center);c.target.lerpVectors(f.from.target,f.to.target,t);c.update();if(f.t===1){flight.current=null;c.enableDamping=!reduced;}
 });
 return <OrbitControls ref={controls} makeDefault target={[0,3.1,0]} enableDamping dampingFactor={.08} rotateSpeed={.65} zoomSpeed={.7} minDistance={10*scale} maxDistance={30*scale} minPolarAngle={.43} maxPolarAngle={1.39} enablePan={false} enabled={!dialog} onStart={()=>{flight.current=null;if(controls.current)controls.current.enableDamping=!reduced;useWorld.getState().touch();useWorld.getState().setHint('');}}/>;
}
