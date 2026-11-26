import { useRef } from 'react';
import type { ThreeEvent } from '@react-three/fiber';
import { useWorld } from './useWorld';
/** Only visible mesh raycasts reach these handlers. A drag can never become a tap. */
export function useSelectable(label:string, onSelect:()=>void, onHover?:(value:boolean)=>void) {
  const down=useRef<{x:number;y:number;id:number}|null>(null);
  return {
    onPointerOver:(e:ThreeEvent<PointerEvent>)=>{e.stopPropagation();useWorld.getState().setHint(label);onHover?.(true);},
    onPointerOut:()=>{useWorld.getState().setHint('');onHover?.(false);},
    onPointerDown:(e:ThreeEvent<PointerEvent>)=>{e.stopPropagation();down.current={x:e.clientX,y:e.clientY,id:e.pointerId};},
    onPointerUp:(e:ThreeEvent<PointerEvent>)=>{e.stopPropagation();const start=down.current;down.current=null;if(start&&start.id===e.pointerId&&Math.hypot(start.x-e.clientX,start.y-e.clientY)<6&&e.delta<6){useWorld.getState().touch();onSelect();}},
  };
}
