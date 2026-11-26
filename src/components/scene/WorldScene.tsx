import { useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { ContactShadows, PerformanceMonitor } from '@react-three/drei';
import { House } from '../house/House';
import { CameraRig } from '../camera/CameraRig';
import { SceneLighting } from '../lighting/SceneLighting';
import { useWorld } from '../../hooks/useWorld';
export default function WorldScene(){
 const [dpr,setDpr]=useState(Math.min(window.devicePixelRatio,1.5));const hint=useWorld(s=>s.hint);
 return <Canvas style={{cursor:hint?'pointer':'grab'}} shadows dpr={dpr} camera={{position:[10.6,9,16.4],fov:38,near:.1,far:120}} gl={{antialias:true,alpha:true,powerPreference:'high-performance'}} fallback={<div className="scene-fallback"><h2>This device cannot display the 3D house.</h2><p>About and Contact are still available above.</p></div>}>
 <PerformanceMonitor onDecline={()=>setDpr(1)} onIncline={()=>setDpr(Math.min(window.devicePixelRatio,1.5))} flipflops={2} onFallback={()=>setDpr(1)}/>
 <SceneLighting/><House/><ContactShadows position={[0,-.04,0]} opacity={.37} scale={27} blur={2.6} far={12} resolution={512} frames={1} color="#2f3b29"/><CameraRig/>
 </Canvas>;
}
