import { useMemo } from 'react';
import * as THREE from 'three';
import { Box, Beam, Cylinder, Repeated } from './Primitives';
import { materials } from './materials';
import { Roof } from './Roof';
import { rooms } from '../../config/rooms';
import { archShape } from './ArchShapes';

type Opening={x:number;y:number;w:number;h:number;a:number};
function Wall({x,z,w,eave,rise=0,back=false,openings=[]}:{x:number;z:number;w:number;eave:number;rise?:number;back?:boolean;openings?:Opening[]}){
 const g=useMemo(()=>{const s=new THREE.Shape();s.moveTo(-w/2,.72);s.lineTo(w/2,.72);s.lineTo(w/2,eave);if(rise)s.lineTo(0,eave+rise);s.lineTo(-w/2,eave);s.closePath();
 openings.forEach(o=>{const p=archShape(o.w,o.h,o.a);const points=p.getPoints(32);const hole=new THREE.Path();points.forEach((p,i)=>{const xx=(back?-1:1)*(o.x-x)+p.x,yy=o.y+p.y;i?hole.lineTo(xx,yy):hole.moveTo(xx,yy);});hole.closePath();s.holes.push(hole);});
 return new THREE.ExtrudeGeometry(s,{depth:.18,bevelEnabled:true,bevelSegments:1,steps:1,bevelSize:.015,bevelThickness:.015,curveSegments:24});},[x,w,eave,rise,back,JSON.stringify(openings)]);
 return <mesh position={[x,0,z]} rotation={[0,back?Math.PI:0,0]} geometry={g} material={materials.plaster} castShadow receiveShadow/>;
}
function FixedArch({position,width=1.8,height=1.6,recess=false}:{position:[number,number,number];width?:number;height?:number;recess?:boolean}){
 const geometry=useMemo(()=>new THREE.ShapeGeometry(archShape(width,height,width*.47),32),[width,height]);
 return <group position={position}><mesh geometry={geometry} material={materials.darkWood} position={[0,0,recess?-1.42:0]}/><mesh geometry={geometry} scale={[.92,.94,1]} position={[0,0,.015]} material={materials.glass}/>
 {[-.35,0,.35].map(v=><Box key={v} size={[.05,height*(Math.abs(v)<.01?.95:.8),.08]} position={[v*width,0,.04]} material={materials.wood}/>)}
 <Box size={[width,.06,.08]} position={[0,-height*.1,.04]} material={materials.wood}/><Box size={[width+.3,.1,.35]} position={[0,-height/2-.05,.03]} material={materials.stone}/>
 {!recess&&<pointLight position={[0,.1,.2]} color="#ffc275" intensity={1.5} distance={2.1}/>}</group>;
}
function Balcony({back=false}:{back?:boolean}){return <group position={[3.15,3.32,back?-2.39:2.35]} rotation={[0,back?Math.PI:0,0]}>
 <Box size={[2.65,.16,1.05]} material={materials.stone}/><Box size={[2.5,.07,1.02]} position={[0,.1,0]} material={materials.lightWood}/>
 <Box size={[2.65,.1,.13]} position={[0,.82,.48]} material={materials.wood}/><Box size={[2.5,.07,.12]} position={[0,.19,.48]} material={materials.wood}/>
 {Array.from({length:10},(_,i)=><group key={i} position={[-1.14+i*.253,.5,.48]}><Cylinder radius={.045} top={.055} height={.56} material={materials.wood}/><Cylinder radius={.073} top={.04} height={.21} material={materials.wood}/></group>)}
 {[-1,1].map(s=><group key={s}><Box size={[.13,.86,.13]} position={[s*1.26,.43,.48]} material={materials.wood}/><Cylinder radius={.1} height={.09} position={[s*1.26,.9,.48]} material={materials.brass}/><Box size={[.1,.1,.85]} position={[s*1.26,.82,0]} material={materials.wood}/><Beam from={[s*.85,-.08,.32]} to={[s*.85,-.65,-.32]} width={.1} material={materials.wood}/></group>)}
 </group>;}
function Greenhouse(){const panels=Array.from({length:6},(_,i)=>-4.48+i*.59);return <group>
 <Box size={[3.16,.13,2.25]} position={[-3,.8,2.24]} material={materials.stone}/>
 <Box size={[3.28,.055,1.9]} position={[-3,3.29,2.2]} rotation={[-.29,0,0]} material={materials.glass} castShadow={false}/>
 {panels.map(x=><Beam key={x} from={[x,3.02,3.12]} to={[x,3.56,1.28]} width={.055} material={materials.trim}/>)}
 {[1.28,2.2,3.12].map((z,i)=><Box key={z} size={[3.22,.07,.06]} position={[-3,3.56-i*.27,z]} material={materials.trim}/>)}
 {[-4.5,-1.5].map(x=><group key={x}>
 <Box size={[.04,2.2,1.76]} position={[x,1.94,2.2]} material={materials.glass} castShadow={false}/>
 {[1.32,2.15,3.04].map(z=><Box key={z} size={[.065,2.23,.065]} position={[x,1.92,z]} material={materials.trim}/>)}
 {[.85,1.4,2.28,3.03].map(y=><Box key={y} size={[.07,.055,1.8]} position={[x,y,2.2]} material={materials.trim}/>)}
 </group>)}
 </group>;}
function Chimney(){const blocks=useMemo(()=>Array.from({length:7},(_,row)=>Array.from({length:3},(_,col)=>({position:[(col-1)*.27,5.34+row*.29,-.44] as [number,number,number]}))).flat(),[]);return <group position={[-2.4,0,0]}>
 <Box size={[.86,2.55,.76]} position={[0,6.38,-.44]} material={materials.stone}/>
 <Repeated size={[.252,.272,.785]} pieces={blocks} material={materials.stone}/>
 <Box size={[1.08,.18,.97]} position={[0,7.62,-.44]} material={materials.stone}/>
 <Box size={[.65,.27,.55]} position={[0,7.84,-.44]} material={materials.darkWood}/><Box size={[.95,.13,.84]} position={[0,8.03,-.44]} material={materials.wood}/>
 </group>;}
function EndGable(){const geo=useMemo(()=>{const s=new THREE.Shape();s.moveTo(-2.18,0);s.lineTo(2.18,0);s.lineTo(0,.94);s.closePath();return new THREE.ExtrudeGeometry(s,{depth:.13,bevelEnabled:false});},[]);return <group position={[4.71,5.03,0]} rotation={[0,Math.PI/2,0]}><mesh geometry={geo} material={materials.plaster} castShadow receiveShadow/><mesh position={[0,.38,.145]} material={materials.darkWood}><circleGeometry args={[.23,32]}/></mesh><mesh position={[0,.38,.16]} material={materials.wood}><torusGeometry args={[.24,.045,10,32]}/></mesh><Box size={[.025,.42,.05]} position={[0,.38,.17]} material={materials.brass}/></group>;}
export function Architecture(){
 const openings=(facade:'front'|'back',indexes:number[])=>indexes.map(i=>{const r=rooms.filter(r=>r.facade===facade)[i];return {x:r.position[0],y:r.position[1],w:r.opening.width,h:r.opening.height,a:r.opening.arch};});
 return <group>
 <Box size={[9.5,.16,4.9]} position={[.05,.72,0]} material={materials.stone}/>
 {[-1,1].map(side=><group key={side}>
 <Wall x={-3} z={side>0?1.91:-2.1} w={3.02} eave={4.95} rise={1.17} back={side<0} openings={openings(side>0?'front':'back',[0,2])}/>
 <Wall x={.15} z={side*2.26} w={3.35} eave={5.23} rise={1.58} back={side<0} openings={[...openings(side>0?'front':'back',[3]),{x:.15,y:1.94,w:1.85,h:2.32,a:.85}]}/>
 <Wall x={3.22} z={side>0?2.02:-2.04} w={3.0} eave={5.03} back={side<0} openings={[...openings(side>0?'front':'back',[1]),{x:3.15,y:4.13,w:1.95,h:1.6,a:.78}]}/>
 <Box size={[3.08,.14,.24]} position={[-3,3.02,side*2.13]} material={materials.stone}/>
 <Box size={[3.1,.12,.24]} position={[3.2,3.1,side*2.22]} material={materials.stone}/>
 <group position={[3.15,4.13,side*2.14]} rotation={[0,side<0?Math.PI:0,0]}><FixedArch position={[0,0,0]} width={1.95} recess/></group>
 </group>)}
 {/* Narrow connecting roofs and truly different wing depths make a coherent building in orbit. */}
 {[-4.51,4.72].map((x,i)=><group key={x}>
 <Box size={[.18,4.25,4.3]} position={[x,2.9,-.04]} material={materials.plaster}/>
 <group position={[x+(i? .1:-.1),2.36,-.12]} rotation={[0,i?Math.PI/2:-Math.PI/2,0]}><FixedArch position={[0,0,0]} width={1.32} height={1.85}/></group>
 {[-1.88,1.8].map(z=><group key={z}>
 <Box size={[.18,4.27,.18]} position={[x,2.9,z]} material={materials.stone}/>
 {Array.from({length:10},(_,j)=><Box key={j} size={[j%2?.36:.23,.18,j%2?.23:.36]} position={[x,.95+j*.39,z]} material={materials.stone}/>)}
 </group>)}
 </group>)}
 <Box size={[9.05,4.15,.13]} position={[0,2.87,0]} material={materials.plaster}/>
 <Roof position={[-3,4.98,-.06]} width={3.55} depth={4.88} rise={1.36}/>
 <Roof position={[.15,5.23,0]} width={3.94} depth={5.52} rise={1.91}/>
 <Roof position={[3.16,5.04,0]} width={4.95} depth={3.42} rise={1.08} rotation={Math.PI/2}/>
 <Roof position={[.15,2.95,2.77]} width={2.9} depth={1.42} rise={.53}/>
 <Roof position={[.15,2.94,-2.69]} width={2.65} depth={1.3} rise={.54}/>
 <Greenhouse/><Balcony/><Chimney/><EndGable/>
 {[-1,1].map(s=><group key={s} position={[.15,0,s*2.51]} rotation={[0,s<0?Math.PI:0,0]}>
 {[0,1,2].map(i=><mesh key={i} position={[0,.6+i*.085,.5-i*.13]} material={materials.stone} receiveShadow castShadow><cylinderGeometry args={[1.46-i*.13,1.46-i*.13,.1,36,1,false,-Math.PI/2,Math.PI]}/></mesh>)}
 </group>)}
 {/* Discreet copper downpipes, restrained buttress brackets and gable carpentry. */}
 {[-4.46,4.58].flatMap(x=>[-2.04,2.04].map(z=><group key={`${x}${z}`}><Cylinder radius={.045} height={4.05} position={[x,2.86,z]} material={materials.brass}/>{[1.1,2.4,3.9].map(y=><Box key={y} size={[.14,.055,.15]} position={[x,y,z]} material={materials.wood}/>)}</group>))}
 {[-1,1].map(s=><group key={s}><Beam from={[.15,5.3,s*2.42]} to={[.15,6.91,s*2.42]} width={.12} material={materials.wood}/><Beam from={[-1.35,5.3,s*2.42]} to={[.15,6.5,s*2.42]} width={.1} material={materials.wood}/><Beam from={[1.65,5.3,s*2.42]} to={[.15,6.5,s*2.42]} width={.1} material={materials.wood}/></group>)}
 </group>;
}
