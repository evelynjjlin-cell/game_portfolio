import {useEffect} from 'react';
import {useFrame,useThree} from '@react-three/fiber';
import {useWorld} from '../../hooks/useWorld';
/** Reuse static sun shadows while keeping the camera and room details continuously drawn. */
export function RenderActivity(){
 const {gl}=useThree();
 useEffect(()=>{gl.shadowMap.autoUpdate=false;gl.shadowMap.needsUpdate=true;},[gl]);
 useFrame(()=>{
  if(Object.values(useWorld.getState().phases).some(p=>p==='opening'||p==='closing'))gl.shadowMap.needsUpdate=true;
 });
 return null;
}
