import { useMemo } from 'react';
import * as THREE from 'three';
import { Box } from './Primitives';
import { materials } from './materials';

// A miniature sewn book, built as two curved page blocks rather than two slabs.
// The exposed fore-edges have 60 individual, slightly uneven paper strata.
const PAGE_W = 5.83;
const PAGE_D = 3.96;
const COVER_W = 6.08;
const COVER_D = 4.15;
const SEGMENTS = 72;
const edgeMaterial = new THREE.MeshStandardMaterial({color:'#bfa780',roughness:1,side:THREE.DoubleSide});
const fineEdgeMaterial = new THREE.MeshStandardMaterial({color:'#d7c4a0',roughness:1,side:THREE.DoubleSide});
const bookCloth = materials.cover.clone();
bookCloth.color.set('#233d32');
bookCloth.roughness = .92;
const ribbonMaterial = new THREE.MeshStandardMaterial({color:'#956149',roughness:.9,side:THREE.DoubleSide});
const gilding = materials.brass.clone();
gilding.color.set('#b99653');
gilding.roughness=.53;

const pageTop = (t:number) => .53 + .185*Math.sin(Math.PI*t) - .16*Math.exp(-t*13);
const pageBottom = (t:number) => .17 + .055*Math.sin(Math.PI*t) - .022*Math.exp(-t*13);
const coverTop = (t:number) => .155 + .055*Math.sin(Math.PI*t) - .025*Math.exp(-t*13);

/** One closed curved profile, swept along the book's binding. */
function sectionGeometry(side:number,cover=false){
 const width=cover?COVER_W:PAGE_W, depth=cover?COVER_D:PAGE_D;
 const shape=new THREE.Shape();
 const top=cover?coverTop:pageTop;
 const bottom=cover?(t:number)=>coverTop(t)-.115:pageBottom;
 shape.moveTo(.035,bottom(0));
 for(let i=1;i<=SEGMENTS;i++)shape.lineTo(.035+width*i/SEGMENTS,bottom(i/SEGMENTS));
 for(let i=SEGMENTS;i>=0;i--)shape.lineTo(.035+width*i/SEGMENTS,top(i/SEGMENTS));
 shape.closePath();
 const geometry=new THREE.ExtrudeGeometry(shape,{depth:depth*2,bevelEnabled:true,bevelSize:cover?.035:.009,bevelThickness:cover?.035:.008,bevelSegments:3,curveSegments:SEGMENTS,steps:1});
 geometry.translate(0,0,-depth);
 if(side<0){
  // ExtrudeGeometry is non-indexed: reflection needs reversed triangle winding.
  geometry.scale(-1,1,1);
  const ids:number[]=[];
  for(let i=0;i<geometry.attributes.position.count;i+=3)ids.push(i,i+2,i+1);
  geometry.setIndex(ids);
  geometry.computeVertexNormals();
 }
 return geometry;
}

function edgeStrata(side:number,alternate=false){
 const vertices:number[]=[];
 const addQuad=(a:number[],b:number[],c:number[],d:number[])=>vertices.push(...a,...b,...d,...b,...c,...d);
 for(let layer=1;layer<60;layer++){
  if((layer%4===0)!==alternate)continue;
  const f=layer/60;
  const thickness=layer%7===0?.0035:.0022;
  const height=(t:number)=>THREE.MathUtils.lerp(pageBottom(t),pageTop(t),f)+.0015*Math.sin(t*28+layer*1.71);
  // Each page edge follows the same curved binding-to-fore-edge section.
  for(const front of [-1,1])for(let i=0;i<SEGMENTS;i++){
   const t0=i/SEGMENTS,t1=(i+1)/SEGMENTS;
   const x0=side*(.035+PAGE_W*t0),x1=side*(.035+PAGE_W*t1);
   const z=front*(PAGE_D+.010+Math.sin(layer*2.71)*.0018);
   addQuad([x0,height(t0),z],[x1,height(t1),z],[x1,height(t1)+thickness,z],[x0,height(t0)+thickness,z]);
  }
  const x=side*(PAGE_W+.046);
  // Folded fore-edge: enough irregularity to read as paper, never zig-zagging.
  for(let i=0;i<24;i++){
   const z0=-PAGE_D+i*PAGE_D/12,z1=-PAGE_D+(i+1)*PAGE_D/12;
   const h0=height(1)+.0008*Math.sin(z0*5+layer),h1=height(1)+.0008*Math.sin(z1*5+layer);
   addQuad([x,h0,z0],[x,h1,z1],[x,h1+thickness,z1],[x,h0+thickness,z0]);
  }
 }
 const geometry=new THREE.BufferGeometry();
 geometry.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));
 geometry.computeVertexNormals();
 return geometry;
}

/** Fine bands run along the curved edge of the cloth binding and page block. */
function edgePiping(side:number,front:number,yOffset:number){
 const points:THREE.Vector3[]=[];
 for(let i=0;i<=SEGMENTS;i++){
  const t=i/SEGMENTS;
  points.push(new THREE.Vector3(side*(.035+COVER_W*t),coverTop(t)+yOffset,front*(COVER_D+.027)));
 }
 return new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points),SEGMENTS,.009,5,false);
}

function spineGeometry(){
 const s=new THREE.Shape();
 s.moveTo(-.3,.18);s.bezierCurveTo(-.2,.05,-.12,-.045,0,-.055);
 s.bezierCurveTo(.12,-.045,.2,.05,.3,.18);
 s.lineTo(.25,.205);s.bezierCurveTo(.14,.09,.09,.055,0,.052);
 s.bezierCurveTo(-.09,.055,-.14,.09,-.25,.205);s.closePath();
 const g=new THREE.ExtrudeGeometry(s,{depth:COVER_D*2,bevelEnabled:true,bevelSize:.012,bevelThickness:.018,bevelSegments:3,curveSegments:20});
 g.translate(0,0,-COVER_D);return g;
}

function cornerGeometry(){
 // Thin cast brass corner protectors wrap the outer cover instead of big cubes.
 const s=new THREE.Shape();
 s.moveTo(0,0);s.lineTo(.36,0);s.lineTo(.36,.07);s.lineTo(.12,.07);
 s.quadraticCurveTo(.07,.07,.07,.12);s.lineTo(.07,.37);s.lineTo(0,.37);s.closePath();
 return new THREE.ExtrudeGeometry(s,{depth:.027,bevelEnabled:true,bevelSize:.012,bevelThickness:.007,bevelSegments:2});
}

function ribbonGeometry(){
 const pts=[new THREE.Vector3(.12,.39,3.5),new THREE.Vector3(.23,.29,3.87),new THREE.Vector3(.31,.11,4.18),new THREE.Vector3(.43,.075,4.62)];
 const curve=new THREE.CatmullRomCurve3(pts);
 const vertices:number[]=[];
 for(let i=0;i<25;i++){
  const a=curve.getPoint(i/25),b=curve.getPoint((i+1)/25);
  const aw=.095,bw=i===24?.045:.095;
  vertices.push(a.x-aw,a.y,a.z,a.x+aw,a.y,a.z,b.x+bw,b.y,b.z,a.x-aw,a.y,a.z,b.x+bw,b.y,b.z,b.x-bw,b.y,b.z);
 }
 const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));geometry.computeVertexNormals();return geometry;
}

export function OpenBook(){
 const geometry=useMemo(()=>({
  pages:[sectionGeometry(1),sectionGeometry(-1)],
  covers:[sectionGeometry(1,true),sectionGeometry(-1,true)],
  strata:[edgeStrata(1),edgeStrata(-1)],
  fine:[edgeStrata(1,true),edgeStrata(-1,true)],
  piping:[-1,1].flatMap(s=>[-1,1].map(f=>edgePiping(s,f,-.028))),
  spine:spineGeometry(),corner:cornerGeometry(),ribbon:ribbonGeometry(),
 }),[]);
 return <group>
  {geometry.covers.map((g,i)=><mesh key={`cover${i}`} geometry={g} material={bookCloth} castShadow receiveShadow/>)}
  <mesh geometry={geometry.spine} material={bookCloth} castShadow receiveShadow/>
  {geometry.pages.map((g,i)=><mesh key={`pages${i}`} geometry={g} material={materials.paper} castShadow receiveShadow/>)}
  {geometry.strata.map((g,i)=><mesh key={`strata${i}`} geometry={g} material={fineEdgeMaterial}/>)}
  {geometry.fine.map((g,i)=><mesh key={`fine${i}`} geometry={g} material={edgeMaterial}/>)}
  {geometry.piping.map((g,i)=><mesh key={`piping${i}`} geometry={g} material={gilding}/>)}
  {[-1,1].flatMap(side=>[-1,1].map(front=><group key={`${side}:${front}`} position={[side*(COVER_W+.03),.16,front*(COVER_D+.014)]} rotation={[-Math.PI/2,0,0]} scale={[-side,front,1]}><mesh geometry={geometry.corner} material={gilding} castShadow receiveShadow/></group>))}
  {/* Tightly sewn end bands at the two exposed ends of the gutter. */}
  {[-1,1].map(front=><group key={`sewn${front}`} position={[0,.327,front*3.95]}>
   <Box size={[.12,.043,.05]} material={materials.darkWood}/>
   {Array.from({length:7},(_,i)=><mesh key={i} position={[-.049+i*.016,.018,0]} material={i%2?materials.cream:gilding}><sphereGeometry args={[.01,6,4]}/></mesh>)}
  </group>)}
  <mesh geometry={geometry.ribbon} material={ribbonMaterial} castShadow receiveShadow/>
  <Box size={[.115,.018,.042]} position={[.431,.083,4.618]} rotation={[0,-.24,0]} material={gilding}/>
 </group>;
}
