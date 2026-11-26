import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
export default function WorldScene(){return <Canvas shadows camera={{position:[11,9,15],fov:37}}><ambientLight intensity={1}/><directionalLight position={[5,12,8]} intensity={3}/><OrbitControls target={[0,3,0]}/></Canvas>;}
