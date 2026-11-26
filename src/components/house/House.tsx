import {useEffect} from 'react';
import {useThree} from '@react-three/fiber';
import { Mailbox } from '../interactions/Mailbox';
import { EnvironmentShell } from './EnvironmentShell';
import { GardenAsset } from './GardenAsset';
import { BookAsset } from './BookAsset';
import { Room } from '../rooms/Room';
import { AboutJoinery } from '../rooms/ArchitecturalJoinery';
import { rooms } from '../../config/rooms';
export function House(){const{gl,invalidate}=useThree();useEffect(()=>{gl.shadowMap.needsUpdate=true;invalidate();},[gl,invalidate]);return <group onPointerOver={e=>e.stopPropagation()} onPointerDown={e=>e.stopPropagation()} onPointerUp={e=>e.stopPropagation()}><BookAsset/><EnvironmentShell/><GardenAsset/><AboutJoinery/><AboutJoinery back/><Mailbox/>{rooms.map(room=><Room key={room.id} room={room}/>)}</group>;}
