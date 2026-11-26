import {useEffect,useRef} from 'react';
import {useFrame,useThree} from '@react-three/fiber';
import {useWorld} from '../../hooks/useWorld';
/** Static miniature frames are cached. Only motion or a settling light change requests another. */
export function RenderActivity(){
 const state=useWorld(),{gl,invalidate}=useThree(),settleUntil=useRef(0);
 useEffect(()=>{gl.shadowMap.autoUpdate=false;gl.shadowMap.needsUpdate=true;invalidate();},[gl,invalidate]);
 useEffect(()=>{settleUntil.current=performance.now()+850;invalidate();},[state,invalidate]);
 useFrame(()=>{
  const s=useWorld.getState(),doors=Object.values(s.phases).some(p=>p==='opening'||p==='closing');
  const moving=s.cameraPhase==='entering'||s.cameraPhase==='exiting'||s.cameraPhase==='moving';
  if(doors)gl.shadowMap.needsUpdate=true;
  if(doors||moving||performance.now()<settleUntil.current)invalidate();
 });
 return null;
}
