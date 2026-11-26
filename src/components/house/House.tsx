import { Mailbox } from '../interactions/Mailbox';
import { Entrance } from '../interactions/Entrance';
import { Attic } from '../interactions/Attic';
import { Architecture } from './Architecture';
import { OpenBook } from './OpenBook';
import { Room } from '../rooms/Room';
import { rooms } from '../../config/rooms';
export function House(){return <group onPointerOver={e=>e.stopPropagation()} onPointerDown={e=>e.stopPropagation()} onPointerUp={e=>e.stopPropagation()}><OpenBook/><Architecture/><Entrance/><Entrance back/><Attic/><Attic back/><Mailbox/>{rooms.map(room=><Room key={room.id} room={room}/>)}</group>;}
