import * as THREE from 'three';
import type { RoomConfig } from '../../config/rooms';
import type { View } from '../../hooks/useWorld';
export type CameraPose={position:THREE.Vector3;target:THREE.Vector3;quaternion:THREE.Quaternion;fov:number;zoom:number};
export type CameraSegment={from:CameraPose;to:CameraPose;duration:number;mode:'linear'|'orbit'|'hold'};
export type FrameRect={left:number;right:number;bottom:number;top:number};
export const WORLD_BOUNDS=new THREE.Box3(new THREE.Vector3(-7.15,-.1,-5.4),new THREE.Vector3(7.15,9.8,5.75));
export const WORLD_CENTER=WORLD_BOUNDS.getCenter(new THREE.Vector3());
export const SAFE_RADIUS=12.65;
const UP=new THREE.Vector3(0,1,0);
export const ease=(t:number)=>t*t*t*(t*(t*6-15)+10);
export function makePose(position:THREE.Vector3,target:THREE.Vector3,fov=37,zoom=1):CameraPose{
 return{position,target,quaternion:new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().lookAt(position,target,UP)),fov,zoom};
}
export function clonePose(p:CameraPose):CameraPose{return{position:p.position.clone(),target:p.target.clone(),quaternion:p.quaternion.clone(),fov:p.fov,zoom:p.zoom};}
export function boxCorners(box:THREE.Box3){return[-1,1].flatMap(x=>[-1,1].flatMap(y=>[-1,1].map(z=>new THREE.Vector3(x<0?box.min.x:box.max.x,y<0?box.min.y:box.max.y,z<0?box.min.z:box.max.z))));}
export function frameRect(width:number,height:number,room=false):FrameRect{
 const phone=width<600;
 const left=phone?10:24,right=left,top=phone?110:91,bottom=phone?112:91;
 const cx=0,cy=(bottom-top)/height,halfX=(1-(left+right)/width)*(room?.91:.92),halfY=(1-(top+bottom)/height)*(room?.91:.92);
 return{left:cx-halfX,right:cx+halfX,bottom:cy-halfY,top:cy+halfY};
}
function projected(pose:CameraPose,aspect:number,points:THREE.Vector3[]){const camera=new THREE.PerspectiveCamera(pose.fov,aspect,.04,200);camera.zoom=pose.zoom;camera.position.copy(pose.position);camera.quaternion.copy(pose.quaternion);camera.updateProjectionMatrix();camera.updateMatrixWorld(true);return points.map(p=>p.clone().project(camera));}
export function projectedBounds(pose:CameraPose,width:number,height:number,points=boxCorners(WORLD_BOUNDS)){
 const p=projected(pose,width/height,points);return{left:Math.min(...p.map(v=>v.x)),right:Math.max(...p.map(v=>v.x)),bottom:Math.min(...p.map(v=>v.y)),top:Math.max(...p.map(v=>v.y)),near:Math.min(...p.map(v=>v.z)),far:Math.max(...p.map(v=>v.z))};
}
function fits(pose:CameraPose,width:number,height:number,points:THREE.Vector3[],rect:FrameRect){const p=projectedBounds(pose,width,height,points);return p.left>=rect.left&&p.right<=rect.right&&p.bottom>=rect.bottom&&p.top<=rect.top&&p.near>-1&&p.far<1;}
/** Fit the complete silhouette, not a guessed width multiplier. Header and controls get real pixel clearance. */
export function overviewPose(width:number,height:number,view:View='reset'):CameraPose{
 width=Math.max(1,width);height=Math.max(1,height);
 const dir=(view==='front'?new THREE.Vector3(.19,.2,1):view==='back'?new THREE.Vector3(-.25,.22,-1):new THREE.Vector3(.38,.25,1)).normalize();
 const right=new THREE.Vector3().crossVectors(UP,dir).normalize(),up=new THREE.Vector3().crossVectors(dir,right).normalize();
 const rect=frameRect(width,height),shiftY=(rect.top+rect.bottom)/2,fov=37,tan=Math.tan(THREE.MathUtils.degToRad(fov/2));
 const poseAt=(distance:number)=>{
  const target=WORLD_CENTER.clone();let pose=makePose(target.clone().addScaledVector(dir,distance),target,fov);
  // Perspective makes a box's projected extent asymmetric. Center its actual screen bounds
  // before fitting distance, otherwise one edge fits while the opposite side wastes space.
  for(let i=0;i<10;i++){
   const b=projectedBounds(pose,width,height);
   target.addScaledVector(right,((b.left+b.right)/2)*distance*tan*(width/height));
   target.addScaledVector(up,((b.bottom+b.top)/2-shiftY)*distance*tan);
   pose=makePose(target.clone().addScaledVector(dir,distance),target.clone(),fov);
  }
  return pose;
 };
 const points=boxCorners(WORLD_BOUNDS);let lo=SAFE_RADIUS,hi=160;
 for(let i=0;i<45;i++){const mid=(lo+hi)/2;if(fits(poseAt(mid),width,height,points,rect))hi=mid;else lo=mid;}
 return poseAt(hi+.015);
}
export function apertureCorners(room:RoomConfig){const [x,y,z]=room.position,s=room.normal[2];return[-1,1].flatMap(a=>[-1,1].flatMap(b=>[-.06,.2].map(c=>new THREE.Vector3(x+a*(room.opening.width/2+.13),y+b*(room.opening.height/2+.12),z+s*c))));}
/** Keep an individually authored angle, adding only the distance needed for a narrow viewport. */
export function roomPose(room:RoomConfig,width:number,height:number):CameraPose{
 const target=new THREE.Vector3(...room.camera.target),position=new THREE.Vector3(...room.camera.position),dir=position.clone().sub(target).normalize();
 const base=position.distanceTo(target),rect=frameRect(width,height,true),points=apertureCorners(room);
 const poseAt=(d:number)=>makePose(target.clone().addScaledVector(dir,d),target.clone(),room.camera.fov);
 let lo=base,hi=120;if(fits(poseAt(lo),width,height,points,rect))return poseAt(lo);
 for(let i=0;i<40;i++){const mid=(lo+hi)/2;if(fits(poseAt(mid),width,height,points,rect))hi=mid;else lo=mid;}
 return poseAt(hi+.01);
}
export function stagePose(room:RoomConfig,fov=37):CameraPose{
 const side=room.normal[2],target=new THREE.Vector3(...room.camera.target);
 const position=new THREE.Vector3(room.position[0]*.6,room.position[1]+1.4,side*SAFE_RADIUS);
 if(position.distanceTo(WORLD_CENTER)<SAFE_RADIUS)position.sub(WORLD_CENTER).setLength(SAFE_RADIUS).add(WORLD_CENTER);
 return makePose(position,target,fov);
}
export function segment(from:CameraPose,to:CameraPose,duration:number,mode:CameraSegment['mode']='linear'):CameraSegment{return{from:clonePose(from),to:clonePose(to),duration,mode};}
function retreatPose(room:RoomConfig,from:CameraPose){
 const stage=stagePose(room,from.fov);
 if(from.position.distanceTo(WORLD_CENTER)>stage.position.distanceTo(WORLD_CENTER))stage.position.copy(from.position);
 return makePose(stage.position,stage.target,stage.fov,from.zoom);
}
export function approachSegments(from:CameraPose,room:RoomConfig,width:number,height:number,previousRoom?:RoomConfig):CameraSegment[]{
 const to=roomPose(room,width,height),stage=stagePose(room),segments:CameraSegment[]=[];
 let start=from;
 // Only a close-up needs a straight retreat. An interrupted exterior orbit remains on the sphere.
 if(previousRoom&&previousRoom.id!==room.id&&from.position.distanceTo(WORLD_CENTER)<SAFE_RADIUS-.01){
  const retreat=retreatPose(previousRoom,from);segments.push(segment(from,retreat,.32));start=retreat;
 }
 const sameFacade=new THREE.Vector3(...room.normal).dot(start.position.clone().sub(new THREE.Vector3(...room.position)))>0;
 if(start.position.distanceTo(WORLD_CENTER)<SAFE_RADIUS&&sameFacade){
  segments.push(segment(start,start,room.animation.entryDelay,'hold'),segment(start,to,room.animation.entryDuration));
 }else{
  if(start.position.distanceTo(WORLD_CENTER)<SAFE_RADIUS){const position=start.position.clone().sub(WORLD_CENTER).setLength(SAFE_RADIUS+.2).add(WORLD_CENTER);const safe=makePose(position,start.target.clone(),start.fov,start.zoom);segments.push(segment(start,safe,.25));start=safe;}
  segments.push(segment(start,start,room.animation.entryDelay,'hold'),segment(start,stage,.4,'orbit'),segment(stage,to,room.animation.entryDuration-.4));
 }
 return segments;
}
export function returnSegments(from:CameraPose,to:CameraPose,previousRoom?:RoomConfig):CameraSegment[]{
 if(previousRoom&&from.position.distanceTo(WORLD_CENTER)<SAFE_RADIUS-.01){
  const stage=retreatPose(previousRoom,from),duration=previousRoom.animation.exitDuration;
  return[segment(from,stage,.44),segment(stage,to,duration-.44,'orbit')];
 }
 // An early exit during the around-house leg must not cut across the building to a doorway.
 return[segment(from,to,previousRoom?.animation.exitDuration??1.1,'orbit')];
}
/** Preserve the chosen overview angle when viewport orientation changes. */
export function resizeOverviewPose(saved:CameraPose,width:number,height:number):CameraPose{
 const rect=frameRect(width,height),points=boxCorners(WORLD_BOUNDS),dir=saved.position.clone().sub(saved.target).normalize();
 const poseAt=(distance:number)=>({...clonePose(saved),position:saved.target.clone().addScaledVector(dir,distance)});
 let lo=SAFE_RADIUS,hi=160;
 for(let i=0;i<45;i++){const mid=(lo+hi)/2;if(fits(poseAt(mid),width,height,points,rect))hi=mid;else lo=mid;}
 return poseAt(hi+.015);
}
export function interpolateLinear(a:CameraPose,b:CameraPose,t:number):CameraPose{
 const position=a.position.clone().lerp(b.position,t),target=a.target.clone().lerp(b.target,t);
 return makePose(position,target,THREE.MathUtils.lerp(a.fov,b.fov,t),THREE.MathUtils.lerp(a.zoom,b.zoom,t));
}
/** The orbit leg never cuts a chord through the building. */
export function interpolateOrbit(a:CameraPose,b:CameraPose,t:number):CameraPose{
 const sa=new THREE.Spherical().setFromVector3(a.position.clone().sub(WORLD_CENTER)),sb=new THREE.Spherical().setFromVector3(b.position.clone().sub(WORLD_CENTER));
 const delta=THREE.MathUtils.euclideanModulo(sb.theta-sa.theta+Math.PI,Math.PI*2)-Math.PI;
 const sp=new THREE.Spherical(THREE.MathUtils.lerp(sa.radius,sb.radius,t),THREE.MathUtils.lerp(sa.phi,sb.phi,t),sa.theta+delta*t);
 const position=new THREE.Vector3().setFromSpherical(sp).add(WORLD_CENTER),target=a.target.clone().lerp(b.target,t);
 return makePose(position,target,THREE.MathUtils.lerp(a.fov,b.fov,t),THREE.MathUtils.lerp(a.zoom,b.zoom,t));
}
