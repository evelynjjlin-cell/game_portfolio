import { create } from 'zustand';
import { rooms, type RoomId, type RoomPhase } from '../config/rooms';
export type View='front'|'back'|'reset';
export type CameraPhase='overview'|'moving'|'entering'|'room'|'exiting';
type World={
 activeRoom:RoomId|null;closingRoom:RoomId|null;phases:Record<RoomId,RoomPhase>;hovered:RoomId|null;cameraPhase:CameraPhase;transitionId:number;
 dialog:'about'|'contact'|null;evening:boolean;reducedMotion:boolean;hint:string;interacted:boolean;view:{name:View;key:number};
 selectRoom:(id:RoomId)=>void;closeRoom:()=>void;hover:(id:RoomId|null)=>void;finish:(id:RoomId,phase:'open'|'idle')=>void;
 beginClose:(id:RoomId,transitionId:number)=>void;finishCamera:(transitionId:number,phase:'overview'|'room')=>void;
 openDialog:(dialog:'about'|'contact'|null)=>void;setHint:(hint:string)=>void;setEvening:()=>void;setReducedMotion:(value:boolean)=>void;setView:(name:View)=>void;touch:()=>void;
};
function unfocus(phases:Record<RoomId,RoomPhase>){return Object.fromEntries(Object.entries(phases).map(([id,p])=>[id,p==='focused'?'idle':p])) as Record<RoomId,RoomPhase>;}
export const useWorld=create<World>(set=>({
 activeRoom:null,closingRoom:null,phases:Object.fromEntries(rooms.map(r=>[r.id,'idle'])) as Record<RoomId,RoomPhase>,hovered:null,cameraPhase:'overview',transitionId:0,
 dialog:null,evening:false,reducedMotion:false,hint:'',interacted:false,view:{name:'reset',key:0},
 selectRoom:id=>set(s=>{
  if(s.activeRoom===id)return{activeRoom:null,closingRoom:id,cameraPhase:'exiting',transitionId:s.transitionId+1,hovered:null,hint:'',interacted:true};
  const phases=unfocus(s.phases),previous=s.activeRoom??s.closingRoom;
  // A replaced room stays open until the camera has backed out of its sash sweep.
  for(const r of rooms)if(r.id!==id&&r.id!==previous&&(phases[r.id]==='opening'||phases[r.id]==='open'))phases[r.id]='closing';
  phases[id]='opening';
  return{activeRoom:id,closingRoom:previous&&previous!==id?previous:null,phases,cameraPhase:'entering',transitionId:s.transitionId+1,hovered:null,hint:'',interacted:true};
 }),
 closeRoom:()=>set(s=>s.activeRoom?{activeRoom:null,closingRoom:s.activeRoom,cameraPhase:'exiting',transitionId:s.transitionId+1,hovered:null,hint:'',interacted:true}:{}),
 hover:id=>set(s=>{const phases=unfocus(s.phases);if(s.cameraPhase==='overview'&&id&&phases[id]==='idle')phases[id]='focused';return{hovered:s.cameraPhase==='overview'?id:null,phases};}),
 finish:(id,phase)=>set(s=>{const current=s.phases[id];if((current==='opening'&&phase==='open')||(current==='closing'&&phase==='idle'))return{phases:{...s.phases,[id]:phase}};return{};}),
 beginClose:(id,token)=>set(s=>token===s.transitionId&&id!==s.activeRoom?{phases:{...s.phases,[id]:'closing'}}:{}),
 finishCamera:(token,phase)=>set(s=>{
  if(token!==s.transitionId||phase==='room'&&!s.activeRoom||phase==='overview'&&s.activeRoom)return{};
  return{cameraPhase:phase,closingRoom:null};
 }),
 openDialog:dialog=>set({dialog,hint:'',interacted:true}),setHint:hint=>set({hint}),setEvening:()=>set(s=>({evening:!s.evening,interacted:true})),setReducedMotion:reducedMotion=>set({reducedMotion}),
 setView:name=>set(s=>({activeRoom:null,closingRoom:s.activeRoom??s.closingRoom,hovered:null,hint:'',phases:unfocus(s.phases),cameraPhase:s.activeRoom||s.closingRoom?'exiting':'moving',transitionId:s.transitionId+1,view:{name,key:s.view.key+1},interacted:true})),
 touch:()=>set({interacted:true}),
}));
