import { Canvas } from '@react-three/fiber';
import { ContactShadows } from '@react-three/drei';
import { CameraRig } from '../camera/CameraRig';
import { House } from '../house/House';
export default function WorldScene(){return <Canvas shadows dpr={[1,1.5]} camera={{position:[11,9,16],fov:38,near:.1,far:100}} gl={{antialias:true,alpha:true}}><ambientLight intensity={.8}/><hemisphereLight args={['#e6edf0','#c3aa84',1.1]}/><directionalLight castShadow position={[-5,12,8]} intensity={3.5} color="#fff1d6" shadow-mapSize={[2048,2048]} shadow-camera-left={-10} shadow-camera-right={10} shadow-camera-top={12} shadow-camera-bottom={-8} shadow-normalBias={.04}/><directionalLight position={[8,6,-8]} intensity={1.1} color="#dbe6ed"/><House/><ContactShadows position={[0,-.03,0]} opacity={.35} scale={28} blur={2.5} far={12} resolution={512} frames={1}/><CameraRig/></Canvas>;}
