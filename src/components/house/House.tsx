import { Suspense } from 'react';
import { Mailbox } from '../interactions/Mailbox';
import { Entrance } from '../interactions/Entrance';
import { Architecture } from './Architecture';
import { OpenBook } from './OpenBook';
import { Room } from '../rooms/Room';
import { rooms } from '../../config/rooms';
export function House(){return <group onPointerOver={e=>e.stopPropagation()} onPointerDown={e=>e.stopPropagation()} onPointerUp={e=>e.stopPropagation()}><OpenBook/><Architecture/><Entrance/><Entrance back/><Mailbox/><Suspense fallback={null}>{rooms.map(room=><Room key={room.id} room={room}/>)}</Suspense></group>;}
