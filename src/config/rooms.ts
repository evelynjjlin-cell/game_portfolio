export type RoomId = `front-room-0${1|2|3|4}` | `back-room-0${1|2|3|4}`;
export type RoomPhase = 'idle' | 'focused' | 'opening' | 'open' | 'closing';
export type RoomConfig = {
 id: RoomId; facade: 'front'|'back'; label: string;
 position: [number,number,number]; model: 'hinged-french-window';
 opening:{width:number;height:number;arch:number;style:'french'|'shutter'|'greenhouse'};depth:number;
 animation:{duration:number;angle:number}; camera:{position:[number,number,number];target:[number,number,number]};
 lighting:{color:string;idle:number;focused:number;open:number};
 furniture:'study'|'reading'|'music'|'atelier';wall:string;
 project:{title:string;description:string;route:string;contentRef:string;prototypeUrl?:string};availability:'unassigned'|'published';
};
const placements = [
 {facade:'front',position:[-3,1.94,3.0],width:2.45,height:2.3,arch:.75,style:'greenhouse',label:'Glasshouse studio',furniture:'atelier'},
 {facade:'front',position:[3.1,1.94,2.16],width:2.45,height:2.3,arch:.9,style:'french',label:'Front reading room',furniture:'reading'},
 {facade:'front',position:[-3,4.13,2.05],width:2.25,height:2.1,arch:.88,style:'french',label:'Upper library',furniture:'music'},
 {facade:'front',position:[.15,4.77,2.4],width:2.45,height:2.4,arch:1.05,style:'shutter',label:'Gabled drawing studio',furniture:'study'},
 {facade:'back',position:[-3,1.94,-2.24],width:2.35,height:2.3,arch:.8,style:'shutter',label:'Rear music room',furniture:'music'},
 {facade:'back',position:[3.1,1.94,-2.18],width:2.45,height:2.3,arch:.9,style:'french',label:'Garden workshop',furniture:'atelier'},
 {facade:'back',position:[-3,4.13,-2.24],width:2.25,height:2.1,arch:.88,style:'french',label:'Rear reading loft',furniture:'reading'},
 {facade:'back',position:[.15,4.77,-2.4],width:2.45,height:2.4,arch:1.05,style:'shutter',label:'Rear drawing studio',furniture:'study'},
] as const;
export const rooms:RoomConfig[]=placements.map((p,i)=>{
 const side=p.facade==='front'?1:-1,[x,y,z]=p.position;
 return {id:`${p.facade}-room-0${i%4+1}` as RoomId,facade:p.facade,label:p.label,position:[x,y,z],model:'hinged-french-window',
 opening:{width:p.width,height:p.height,arch:p.arch,style:p.style},depth:1.65,
 animation:{duration:.95,angle:1.62},camera:{position:[x*.9,y+1.6,z+side*10.4],target:[x*.75,y+.1,z-side*.5]},
 lighting:{color:'#ffcb86',idle:2,focused:3.5,open:5},furniture:p.furniture,wall:['#b9bca2','#b6a182','#a5b4a9','#bcad94'][i%4],
 project:{title:'',description:'',route:'',contentRef:'',prototypeUrl:''},availability:'unassigned'};
});
export const roomById=Object.fromEntries(rooms.map(r=>[r.id,r])) as Record<RoomId,RoomConfig>;
