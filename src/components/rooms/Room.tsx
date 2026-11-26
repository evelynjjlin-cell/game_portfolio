import { useMemo } from 'react';
import type { RoomConfig } from '../../config/rooms';
import { Box } from '../house/Primitives';
import { materials, colored } from '../house/materials';
import { Furniture } from '../house/Furniture';
export function Room({room}:{room:RoomConfig}){
 const wall=useMemo(()=>colored(room.wall),[room.wall]);
 return <group position={room.position} rotation={[0,room.facade==='back'?Math.PI:0,0]}>
 <Box size={[1.96,1.85,.07]} position={[0,0,-1.92]} material={wall}/>
 {[-1,1].map(s=><Box key={s} size={[.1,1.9,1.95]} position={[s*.98,0,-.96]} material={wall}/>)}
 <Box size={[1.96,.06,1.95]} position={[0,-.87,-.98]} material={materials.wood}/>
 <group position={[0,-.82,-.68]}><Furniture kind={room.furniture}/></group>
 {[-1,1].map(s=><Box key={s} size={[.13,1.92,.23]} position={[s*1.02,0,.04]} material={materials.wood}/>)}
 {[-1,1].map(s=><Box key={s} size={[2.17,.12,.23]} position={[0,s*.93,.04]} material={materials.wood}/>)}
 <Box size={[2.32,.12,.4]} position={[0,-1.01,.07]} material={materials.trim}/>
 <pointLight position={[0,.45,-.6]} color="#ffd18a" intensity={1.5} distance={2.8}/>
 </group>;
}
