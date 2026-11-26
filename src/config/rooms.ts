export type RoomId = `front-room-0${1|2|3|4}` | `back-room-0${1|2|3|4}`;
export type RoomPhase = 'idle' | 'focused' | 'opening' | 'open' | 'closing';
export type RoomConfig = {
  id: RoomId; facade: 'front'|'back'; label: string;
  position: [number, number, number]; model: 'hinged-french-window';
  animation: { duration: number; angle: number };
  camera: { position: [number,number,number]; target: [number,number,number] };
  lighting: { color: string; idle: number; focused: number; open: number };
  furniture: 'study'|'reading'|'music'|'atelier'; wall: string;
  project: { title: string; description: string; route: string; contentRef: string; prototypeUrl?: string };
  availability: 'unassigned'|'published';
};
export const rooms: RoomConfig[] = (['front','back'] as const).flatMap((facade) => [0,1,2,3].map((i) => {
  const side = facade === 'front' ? 1 : -1;
  const x = i % 2 === 0 ? -2.2 : 2.2;
  const y = i < 2 ? 1.72 : 4.05;
  return {
    id: `${facade}-room-0${i+1}` as RoomId, facade,
    label: `${facade === 'front' ? 'Front' : 'Rear'} ${i < 2 ? 'ground' : 'upper'} ${i % 2 === 0 ? 'left' : 'right'} room`,
    position: [x,y,side*2.18], model: 'hinged-french-window',
    animation: { duration: 0.85, angle: 1.82 },
    camera: { position: [x*0.7, y+2.9, side*11.8], target: [x*0.45,y+0.3,side*0.75] },
    lighting: { color: '#ffc77c', idle: 1.25, focused: 2.8, open: 4.2 },
    furniture: (['study','reading','music','atelier'] as const)[facade === 'front' ? i : (i+2)%4],
    wall: ['#cbd0bc','#e1c5af','#bccbc8','#d6ccb8'][facade === 'front' ? i : (i+2)%4],
    project: { title:'', description:'', route:'', contentRef:'', prototypeUrl:'' },
    availability:'unassigned',
  } satisfies RoomConfig;
}));
export const roomById = Object.fromEntries(rooms.map(r => [r.id,r])) as Record<RoomId,RoomConfig>;
