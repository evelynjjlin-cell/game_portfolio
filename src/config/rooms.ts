import layout from '../../scripts/environment/layout.json';
export type RoomId = `front-room-0${1|2|3|4}` | `back-room-0${1|2|3|4}`;
export type RoomPhase = 'idle' | 'focused' | 'opening' | 'open' | 'closing';
export type RoomKind = 'living'|'art'|'library'|'kitchen'|'bedroom'|'music'|'sunroom'|'workshop';
export type Vec3 = [number,number,number];
export type RoomConfig = {
 id:RoomId;kind:RoomKind;facade:'front'|'back';label:string;position:Vec3;floor:number;orientation:number;normal:Vec3;entranceMesh:string;
 model:'hinged-french-window';opening:{width:number;height:number;arch:number;style:'french'|'shutter'|'greenhouse'};depth:number;hinge:'outward'|'inward';
 animation:{duration:number;angle:number;entryDelay:number;entryDuration:number;exitDuration:number;closeDelay:number};
 camera:{position:Vec3;target:Vec3;fov:number;localOrbit:{azimuth:number;polar:number};safeDistance:number};
 lighting:{color:string;idle:number;focused:number;open:number;localPosition:Vec3};
 /** Compatibility aliases for dormant V02 components; V03 interiors use kind. */
 furniture:'study'|'reading'|'music'|'atelier';wall:string;
 project:{title:string;description:string;route:string;contentRef:string;prototypeUrl?:string};availability:'unassigned'|'published';
};
const authored:Record<RoomKind,{camera:{position:Vec3;target:Vec3;fov:number};lighting:{color:string;idle:number;focused:number;open:number;localPosition:Vec3};wall:string;furniture:RoomConfig['furniture']}>={
 sunroom:{camera:{position:[-3.02,2.55,7.65],target:[-3.25,2.11,2.95],fov:42},lighting:{color:'#ffedcf',idle:1.55,focused:2.3,open:3.6,localPosition:[-.28,.73,-1.05]},wall:'#e6dec5',furniture:'reading'},
 living:{camera:{position:[.38,2.72,7.03],target:[.62,2.25,2.18],fov:44},lighting:{color:'#ffc789',idle:1.7,focused:2.9,open:4.5,localPosition:[-.65,.55,-1.05]},wall:'#c6b49a',furniture:'reading'},
 library:{camera:{position:[-2.78,5.42,6.96],target:[-2.64,5.08,2.21],fov:40},lighting:{color:'#ffd7a3',idle:1.25,focused:2.5,open:4.3,localPosition:[.65,.42,-.9]},wall:'#9b9f83',furniture:'study'},
 art:{camera:{position:[2.19,5.78,7.5],target:[2.0,5.25,2.1],fov:43},lighting:{color:'#fff1dc',idle:1.6,focused:2.9,open:4.65,localPosition:[-.4,.77,-1.15]},wall:'#e5dcc8',furniture:'atelier'},
 bedroom:{camera:{position:[-2.56,2.68,-7.17],target:[-2.68,2.21,-2.1],fov:42},lighting:{color:'#ffd5ac',idle:1.05,focused:2.0,open:3.8,localPosition:[-.75,.25,-1.1]},wall:'#c7bbb4',furniture:'reading'},
 kitchen:{camera:{position:[2.55,2.69,-7.2],target:[2.72,2.22,-2.22],fov:43},lighting:{color:'#ffeed0',idle:1.55,focused:2.8,open:4.5,localPosition:[.1,.9,-1.2]},wall:'#d9d4bc',furniture:'study'},
 music:{camera:{position:[-2.54,5.45,-7.08],target:[-2.7,5.0,-2.12],fov:41},lighting:{color:'#ffbf7e',idle:1.1,focused:2.3,open:4.15,localPosition:[.7,.45,-1.12]},wall:'#9fafa8',furniture:'music'},
 workshop:{camera:{position:[2.62,5.52,-7.23],target:[2.7,5.1,-2.14],fov:42},lighting:{color:'#ffe9c2',idle:1.5,focused:2.8,open:4.7,localPosition:[-.48,.65,-1.0]},wall:'#bbb5a2',furniture:'atelier'},
};
export const rooms:RoomConfig[]=layout.rooms.map(p=>{
 const kind=p.kind as RoomKind,details=authored[kind],facade=p.facade as 'front'|'back';
 return {id:p.id as RoomId,kind,facade,label:p.label,position:p.position as Vec3,floor:p.floor,orientation:facade==='back'?Math.PI:0,normal:[0,0,facade==='back'?-1:1],entranceMesh:`${p.id}_Entrance`,model:'hinged-french-window',
 opening:{width:p.width,height:p.height,arch:p.arch,style:kind==='sunroom'?'greenhouse':kind==='art'||kind==='bedroom'?'shutter':'french'},depth:p.depth,hinge:p.hinge as 'outward'|'inward',
 animation:{duration:kind==='art'?.88:.82,angle:p.hinge==='inward'?1.47:1.62,entryDelay:.12,entryDuration:1.28,exitDuration:1.14,closeDelay:.3},
 camera:{...details.camera,localOrbit:{azimuth:.08,polar:.06},safeDistance:12.65},lighting:details.lighting,wall:details.wall,furniture:details.furniture,
 project:{title:'',description:'',route:'',contentRef:'',prototypeUrl:''},availability:'unassigned'};
});
export const roomById=Object.fromEntries(rooms.map(r=>[r.id,r])) as Record<RoomId,RoomConfig>;
