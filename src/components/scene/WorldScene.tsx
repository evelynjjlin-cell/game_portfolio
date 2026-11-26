import { Suspense, useEffect, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { ContactShadows, PerformanceMonitor, Environment, Lightformer, useProgress } from '@react-three/drei';
import { House } from '../house/House';
import { CameraRig } from '../camera/CameraRig';
import { SceneLighting } from '../lighting/SceneLighting';
import { RenderActivity } from './RenderActivity';
import { AmbientOcclusion } from '../lighting/AmbientOcclusion';
import { scenePointerCapture, sceneGesture } from '../../hooks/useSelectable';
import { useWorld } from '../../hooks/useWorld';
function SceneProgress(){const {active,progress}=useProgress();return active?<div className="loading loading-models"><span>Opening the house</span><div className="loading-track"><i style={{width:`${Math.round(progress)}%`}}/></div></div>:null;}
export default function WorldScene(){
 useEffect(()=>{sceneGesture.pointers.clear();return()=>sceneGesture.pointers.clear();},[]);
 const [dpr,setDpr]=useState(Math.min(window.devicePixelRatio,1.5));const hint=useWorld(s=>s.hint);
 return <><Canvas frameloop="demand" onCreated={({gl})=>{const ctx=gl.getContext(),extension=ctx.getExtension('WEBGL_debug_renderer_info');const renderer=extension?String(ctx.getParameter(extension.UNMASKED_RENDERER_WEBGL)):'';if(/swiftshader|llvmpipe|software/i.test(renderer)){setDpr(1);}}} {...scenePointerCapture} style={{cursor:hint?'pointer':'grab'}} shadows dpr={dpr} camera={{position:[10.6,9,16.4],fov:38,near:.04,far:200}} gl={{antialias:true,preserveDrawingBuffer:true,alpha:true,powerPreference:'high-performance'}} fallback={<div className="scene-fallback"><h2>This device cannot display the 3D house.</h2><p>About and Contact are still available above.</p></div>}>
 <PerformanceMonitor onDecline={()=>setDpr(d=>Math.min(d,1))} onIncline={()=>{}} flipflops={2} onFallback={()=>setDpr(d=>Math.min(d,1))}/>
 <Environment resolution={64} frames={1}><Lightformer intensity={1.7} position={[-5,9,6]} scale={[8,8,1]} color="#fff0d9"/><Lightformer intensity={1} position={[5,4,-5]} scale={[5,5,1]} color="#e5edf2"/></Environment><SceneLighting/><Suspense fallback={null}><House/><ContactShadows position={[0,-.04,0]} opacity={.37} scale={27} blur={2.6} far={12} resolution={512} frames={2} color="#2f3b29"/></Suspense><CameraRig/><RenderActivity/><AmbientOcclusion/>
 </Canvas><SceneProgress/></>;
}
