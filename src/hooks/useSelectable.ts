import { useRef } from 'react';
import type { ThreeEvent } from '@react-three/fiber';
import { useWorld } from './useWorld';
export const sceneGesture={pointers:new Set<number>(),multitouch:false};
export const scenePointerCapture={
 onPointerDownCapture:(e:React.PointerEvent)=>{if(sceneGesture.pointers.size===0)sceneGesture.multitouch=false;sceneGesture.pointers.add(e.pointerId);if(sceneGesture.pointers.size>1)sceneGesture.multitouch=true;},
 onPointerUpCapture:(e:React.PointerEvent)=>{sceneGesture.pointers.delete(e.pointerId);},
 onPointerCancelCapture:()=>{sceneGesture.multitouch=true;sceneGesture.pointers.clear();},
};
/** Only visible mesh raycasts reach these handlers. A drag can never become a tap. */
export function useSelectable(label:string, onSelect:()=>void, onHover?:(value:boolean)=>void) {
  const down=useRef<{x:number;y:number;id:number}|null>(null);
  return {
    onPointerOver:(e:ThreeEvent<PointerEvent>)=>{e.stopPropagation();useWorld.getState().setHint(label);onHover?.(true);},
    onPointerOut:()=>{useWorld.getState().setHint('');onHover?.(false);},
    onPointerDown:(e:ThreeEvent<PointerEvent>)=>{e.stopPropagation();if(e.pointerType==='touch'&&!e.isPrimary){down.current=null;return;}down.current={x:e.clientX,y:e.clientY,id:e.pointerId};},
    onPointerUp:(e:ThreeEvent<PointerEvent>)=>{e.stopPropagation();const start=down.current;down.current=null;if(!sceneGesture.multitouch&&start&&start.id===e.pointerId&&Math.hypot(start.x-e.clientX,start.y-e.clientY)<6&&e.delta<6){useWorld.getState().touch();onSelect();}},
  };
}
