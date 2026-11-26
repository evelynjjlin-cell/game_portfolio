import assert from 'node:assert/strict';
import * as THREE from 'three';
import { useWorld } from '../src/hooks/useWorld';
import { rooms } from '../src/config/rooms';
import { WORLD_CENTER,SAFE_RADIUS,frameRect,overviewPose,roomPose,projectedBounds,apertureCorners,approachSegments,returnSegments,interpolateLinear,interpolateOrbit,clonePose,resizeOverviewPose,type CameraSegment } from '../src/components/camera/cameraMath';
const reset=()=>useWorld.setState(useWorld.getInitialState(),true);
reset();
const a=rooms[0].id,b=rooms[4].id;
useWorld.getState().selectRoom(a);
const firstToken=useWorld.getState().transitionId;
assert.equal(useWorld.getState().phases[a],'opening');
assert.equal(useWorld.getState().cameraPhase,'entering');
useWorld.getState().selectRoom(b);
useWorld.getState().finish(a,'open');
assert.equal(useWorld.getState().activeRoom,b);
assert.equal(useWorld.getState().phases[a],'open','The previous entrance stays open until the camera has retreated.');
useWorld.getState().beginClose(a,firstToken);
assert.equal(useWorld.getState().phases[a],'open','An interrupted flight cannot close a door.');
useWorld.getState().finishCamera(firstToken,'room');
assert.equal(useWorld.getState().cameraPhase,'entering','A stale camera arrival cannot complete the new transition.');
useWorld.getState().beginClose(a,useWorld.getState().transitionId);
useWorld.getState().finish(a,'open');
assert.equal(useWorld.getState().phases[a],'closing','An old completion must not reopen a replaced room.');
useWorld.getState().finish(a,'idle');
useWorld.getState().selectRoom(b);
const exitToken=useWorld.getState().transitionId;
assert.equal(useWorld.getState().activeRoom,null);
assert.equal(useWorld.getState().phases[b],'opening','Exit initially holds the entrance open.');
useWorld.getState().selectRoom(b);
useWorld.getState().beginClose(b,exitToken);
useWorld.getState().finish(b,'idle');
assert.equal(useWorld.getState().phases[b],'opening','Reversing a close must ignore stale close completion.');
useWorld.getState().finish(b,'open');
useWorld.getState().finishCamera(useWorld.getState().transitionId,'room');
useWorld.getState().hover(b);
useWorld.getState().hover(null);
assert.equal(useWorld.getState().phases[b],'open','Hover must never overwrite an open state.');
assert.equal(useWorld.getState().hovered,null,'Local room inspection does not activate overview hover.');
useWorld.getState().setView('front');
assert.equal(useWorld.getState().activeRoom,null);
assert.equal(useWorld.getState().phases[b],'open');
useWorld.getState().beginClose(b,useWorld.getState().transitionId);
assert.equal(useWorld.getState().phases[b],'closing');
useWorld.getState().finish(b,'idle');
useWorld.getState().finishCamera(useWorld.getState().transitionId,'overview');
assert.equal(useWorld.getState().cameraPhase,'overview');
assert.equal(useWorld.getState().closingRoom,null);
useWorld.getState().hover(a);
assert.equal(useWorld.getState().phases[a],'focused');
useWorld.getState().hover(null);
assert.equal(useWorld.getState().phases[a],'idle');
assert.equal(new Set(rooms.map(r=>r.id)).size,8);
assert.equal(new Set(rooms.map(r=>r.kind)).size,8,'All eight rooms have distinct residential identities.');
assert.equal(new Set(rooms.map(r=>JSON.stringify(r.camera.position))).size,8,'Close-ups are individually authored.');
assert.ok(rooms.every(r=>r.availability==='unassigned'&&!r.project.title&&!r.project.description&&!r.project.contentRef&&!r.project.route));
reset();

const viewports=[[1440,900],[1363,1023],[1920,1080],[390,844],[360,640],[844,390]];
const inside=(p:ReturnType<typeof projectedBounds>,rect:ReturnType<typeof frameRect>,label:string)=>{
 assert.ok(p.left>=rect.left-1e-6&&p.right<=rect.right+1e-6&&p.bottom>=rect.bottom-1e-6&&p.top<=rect.top+1e-6,`${label}: complete bounds fit the usable viewport.`);
 assert.ok(p.near>-1&&p.far<1,`${label}: no near/far clipping.`);
};
const sample=(s:CameraSegment,t:number)=>s.mode==='hold'?s.from:s.mode==='orbit'?interpolateOrbit(s.from,s.to,t):interpolateLinear(s.from,s.to,t);
const architecture=new THREE.Box3(new THREE.Vector3(-5.45,.7,-4.2),new THREE.Vector3(5.45,9.8,4.5));
const safePath=(segments:CameraSegment[],label:string)=>{
 for(const seg of segments)for(let i=0;i<=30;i++){
  const p=sample(seg,i/30);
  assert.ok(!architecture.containsPoint(p.position),`${label}: camera never enters the architecture envelope.`);
  if(seg.mode==='orbit')assert.ok(p.position.distanceTo(WORLD_CENTER)>=SAFE_RADIUS-.02,`${label}: orbit stays outside the safety sphere.`);
 }
};
let compositions=0,paths=0;
for(const[width,height]of viewports){
 for(const view of ['front','back','reset'] as const){
  const overview=overviewPose(width,height,view),bounds=projectedBounds(overview,width,height),rect=frameRect(width,height);
  inside(bounds,rect,`${view} ${width}×${height}`);
  const occupancy=Math.max((bounds.right-bounds.left)/(rect.right-rect.left),(bounds.top-bounds.bottom)/(rect.top-rect.bottom))*.92;
  assert.ok(occupancy>=.85&&occupancy<=.95,`Overview occupancy ${occupancy.toFixed(3)} meets the 85–95% brief.`);
  for(const room of rooms){
   const closeup=roomPose(room,width,height),points=apertureCorners(room);
   inside(projectedBounds(closeup,width,height,points),frameRect(width,height,true),`${room.id} ${width}×${height}`);
   assert.ok(closeup.position.clone().sub(new THREE.Vector3(...room.position)).dot(new THREE.Vector3(...room.normal))>room.opening.width/2+.3,'Arrival clears the complete outward sash sweep.');
   const entry=approachSegments(overview,room,width,height);
   assert.ok(entry.reduce((sum,s)=>sum+s.duration,0)<=1.5,'Normal entry takes at most 1.5 seconds.');
   assert.ok(entry.reduce((sum,s)=>sum+s.duration,0)>room.animation.duration,'The entrance is fully open before camera arrival.');
   safePath(entry,`entry ${room.id}`);paths++;
   const exit=returnSegments(closeup,overview,room);safePath(exit,`exit ${room.id}`);paths++;
   const restored=exit.at(-1)!.to;
   assert.deepEqual(restored.position.toArray(),overview.position.toArray());
   assert.deepEqual(restored.quaternion.toArray(),overview.quaternion.toArray());
   assert.deepEqual(restored.target.toArray(),overview.target.toArray());
   assert.equal(restored.fov,overview.fov);assert.equal(restored.zoom,overview.zoom);
   // Early exits must remain safe at each leg of a cross-facade entry.
   for(const seg of entry){const interrupted=sample(seg,.45);safePath(returnSegments(interrupted,overview,room),`interrupted ${room.id}`);paths++;}
   compositions++;
  }
 }
}
const closeA=roomPose(rooms[0],1440,900);
for(const room of rooms.slice(1)){safePath(approachSegments(closeA,room,1440,900,rooms[0]),`direct switch ${room.id}`);paths++;}
const saved=clonePose(overviewPose(1440,900,'back'));saved.zoom=1.15;saved.fov=35;
const resized=resizeOverviewPose(saved,390,844);
inside(projectedBounds(resized,390,844),frameRect(390,844),'Rotated viewport');
assert.deepEqual(resized.quaternion.toArray(),saved.quaternion.toArray());
assert.equal(resized.zoom,saved.zoom);assert.equal(resized.fov,saved.fov);
console.log(`PASS: interruption-safe room state; 8 unique empty room slots; ${compositions} responsive compositions; ${paths} collision-free entry, exit and interrupted routes; exact overview pose restoration.`);
