import { useEffect,useLayoutEffect,useMemo,useRef,useState } from 'react';
import { useFrame,useThree } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import type { OrbitControls as Controls } from 'three-stdlib';
import * as THREE from 'three';
import { useWorld } from '../../hooks/useWorld';
import { roomById,type RoomId } from '../../config/rooms';
import { WORLD_CENTER,SAFE_RADIUS,clonePose,ease,overviewPose,roomPose,approachSegments,returnSegments,resizeOverviewPose,interpolateLinear,interpolateOrbit,type CameraPose,type CameraSegment } from './cameraMath';

type Flight={token:number;segments:CameraSegment[];index:number;elapsed:number;total:number;closeRoom:RoomId|null;closeAt:number;closed:boolean;destination:'overview'|'room';final:CameraPose};
export function CameraRig(){
 const controls=useRef<Controls>(null),{camera:rawCamera,size}=useThree(),camera=rawCamera as THREE.PerspectiveCamera;
 const request=useWorld(s=>s.transitionId),cameraPhase=useWorld(s=>s.cameraPhase),dialog=useWorld(s=>s.dialog),reduced=useWorld(s=>s.reducedMotion);
 const viewName=useWorld(s=>s.view.name);
 const overviewDistance=useMemo(()=>{const p=overviewPose(size.width,size.height,viewName);return p.position.distanceTo(p.target);},[size.width,size.height,viewName]);
 const flight=useRef<Flight|null>(null),overviewSnapshot=useRef<CameraPose|null>(null),lastRoom=useRef<RoomId|null>(null),lastView=useRef(useWorld.getState().view.key);
 const initialized=useRef(false),pendingInitial=useRef<CameraPose|null>(null),lastSize=useRef({width:size.width,height:size.height}),lastRequest=useRef(request);
 const [moving,setMoving]=useState(false);
 const fittedOverview=useMemo(()=>overviewPose(size.width,size.height,useWorld.getState().view.name),[size.width,size.height,request]);
 const capture=():CameraPose=>({position:camera.position.clone(),target:controls.current?.target.clone()??WORLD_CENTER.clone(),quaternion:camera.quaternion.clone(),fov:camera.fov,zoom:camera.zoom});
 const apply=(p:CameraPose,exact=false)=>{
  camera.position.copy(p.position);camera.fov=p.fov;camera.zoom=p.zoom;camera.quaternion.copy(p.quaternion);camera.updateProjectionMatrix();
  const c=controls.current;if(c){c.target.copy(p.target);c.minDistance=.05;c.maxDistance=180;c.minPolarAngle=.01;c.maxPolarAngle=Math.PI-.01;c.enableDamping=false;c.update();}
  // An exact restoration includes orientation, fov and zoom, not just the orbit coordinates.
  if(exact){camera.position.copy(p.position);camera.quaternion.copy(p.quaternion);camera.updateMatrixWorld();}
 };
 const stopManual=()=>{const c=controls.current;if(c){c.autoRotate=false;c.enableDamping=false;c.update();}};
 const begin=(segments:CameraSegment[],token:number,destination:'overview'|'room',closingRoom:RoomId|null,closeAt:number)=>{
  stopManual();apply(segments[0].from,true);setMoving(true);const final=clonePose(segments[segments.length-1].to);
  flight.current={token,segments,index:0,elapsed:0,total:0,closeRoom:closingRoom,closeAt,closed:false,destination,final};
 };
 useLayoutEffect(()=>{
  if(initialized.current)return;
  const p=overviewPose(size.width,size.height,'reset');apply(p,true);pendingInitial.current=p;initialized.current=true;
 },[size.width,size.height]);
 useEffect(()=>{
  if(lastRequest.current===request)return;lastRequest.current=request;
  const s=useWorld.getState(),from=capture(),viewChanged=s.view.key!==lastView.current;lastView.current=s.view.key;
  const oldRoom=lastRoom.current??s.closingRoom;
  if(s.activeRoom){
   const room=roomById[s.activeRoom];if(!overviewSnapshot.current)overviewSnapshot.current=clonePose(from);
   const segments=approachSegments(from,room,size.width,size.height,oldRoom?roomById[oldRoom]:undefined);
   begin(segments,request,'room',s.closingRoom,room.animation.closeDelay);lastRoom.current=s.activeRoom;
  }else{
   const destination=viewChanged?overviewPose(size.width,size.height,s.view.name):overviewSnapshot.current?clonePose(overviewSnapshot.current):overviewPose(size.width,size.height,s.view.name);
   const segments=returnSegments(from,destination,oldRoom?roomById[oldRoom]:undefined);
   begin(segments,request,'overview',s.closingRoom,oldRoom?roomById[oldRoom].animation.closeDelay:.3);lastRoom.current=null;
  }
 },[request]);
 useEffect(()=>{
  const before=lastSize.current;if(before.width===size.width&&before.height===size.height)return;lastSize.current={width:size.width,height:size.height};
  if(!initialized.current)return;
  // A changed aspect needs a new fit, but preserves the visitor's exact viewing direction.
  if(overviewSnapshot.current)overviewSnapshot.current=resizeOverviewPose(overviewSnapshot.current,size.width,size.height);
  const s=useWorld.getState(),from=capture(),to=s.activeRoom?roomPose(roomById[s.activeRoom],size.width,size.height):s.cameraPhase==='overview'?resizeOverviewPose(from,size.width,size.height):overviewSnapshot.current??overviewPose(size.width,size.height,s.view.name);
  const segments=s.activeRoom?approachSegments(from,roomById[s.activeRoom],size.width,size.height,lastRoom.current?roomById[lastRoom.current]:undefined):returnSegments(from,to,s.closingRoom?roomById[s.closingRoom]:undefined);
  begin(segments,s.transitionId,s.activeRoom?'room':'overview',s.closingRoom,.18);
 },[size.width,size.height]);
 useFrame((_,dt)=>{
  const c=controls.current;if(!c)return;
  if(pendingInitial.current){apply(pendingInitial.current,true);pendingInitial.current=null;}
  const f=flight.current,s=useWorld.getState();
  if(!f){
   if(s.cameraPhase==='overview'){
    c.minDistance=SAFE_RADIUS;c.maxDistance=Math.max(overviewDistance*1.65,34);c.minPolarAngle=.48;c.maxPolarAngle=1.43;c.enableDamping=!s.reducedMotion;c.dampingFactor=1-Math.exp(-5*dt);
   }
   return;
  }
  if(f.token!==s.transitionId)return;
  f.total+=dt;
  if(f.closeRoom&&!f.closed&&(s.reducedMotion||f.total>=f.closeAt)){s.beginClose(f.closeRoom,f.token);f.closed=true;}
  let remaining=s.reducedMotion?100:dt;
  while(remaining>0&&f.index<f.segments.length){
   const current=f.segments[f.index],available=current.duration-f.elapsed,tick=Math.min(remaining,available);f.elapsed+=tick;remaining-=tick;
   const t=ease(Math.min(1,f.elapsed/current.duration));
   apply(current.mode==='hold'?current.from:current.mode==='orbit'?interpolateOrbit(current.from,current.to,t):interpolateLinear(current.from,current.to,t));
   if(f.elapsed>=current.duration-1e-8){f.index++;f.elapsed=0;}else break;
  }
  if(f.index===f.segments.length){
   apply(f.final,true);flight.current=null;setMoving(false);s.finishCamera(f.token,f.destination);
   if(f.destination==='overview'){overviewSnapshot.current=null;c.enableDamping=!s.reducedMotion;}
  }
 });
 return <OrbitControls ref={controls} makeDefault target={WORLD_CENTER} enabled={!dialog&&!moving&&cameraPhase==='overview'} enableDamping={!reduced} dampingFactor={.08} enablePan={false} rotateSpeed={.55} zoomSpeed={.65} minDistance={SAFE_RADIUS} maxDistance={90} minPolarAngle={.48} maxPolarAngle={1.43}
 onStart={()=>{if(useWorld.getState().cameraPhase!=='overview')return;flight.current=null;useWorld.getState().touch();useWorld.getState().setHint('');}}/>;
}
