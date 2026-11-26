import { Architecture } from './Architecture';
import { OpenBook } from './OpenBook';
import { Room } from '../rooms/Room';
import { rooms } from '../../config/rooms';
export function House(){return <group><OpenBook/><Architecture/>{rooms.map(room=><Room key={room.id} room={room}/>)}</group>;}
