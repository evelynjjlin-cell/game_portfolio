import { create } from 'zustand';
import { rooms, type RoomId, type RoomPhase } from '../config/rooms';
export type View = 'front'|'back'|'reset';
type World = {
  activeRoom: RoomId|null; phases: Record<RoomId,RoomPhase>; hovered: RoomId|null;
  dialog: 'about'|'contact'|null; evening: boolean; reducedMotion: boolean;
  hint: string; interacted: boolean; view: {name:View; key:number};
  selectRoom: (id:RoomId)=>void; closeRoom:()=>void; hover:(id:RoomId|null)=>void;
  finish:(id:RoomId, phase:'open'|'idle')=>void;
  openDialog:(dialog:'about'|'contact'|null)=>void; setHint:(hint:string)=>void;
  setEvening:()=>void; setReducedMotion:(value:boolean)=>void; setView:(name:View)=>void; touch:()=>void;
};
export const useWorld = create<World>((set)=>({
  activeRoom:null, phases:Object.fromEntries(rooms.map(r=>[r.id,'idle'])) as Record<RoomId,RoomPhase>,
  hovered:null, dialog:null, evening:false, reducedMotion:false, hint:'', interacted:false, view:{name:'reset',key:0},
  selectRoom:(id)=>set(s=>{
    if(s.activeRoom===id) return {activeRoom:null, phases:{...s.phases,[id]:'closing'}, interacted:true};
    return {activeRoom:id, phases:{...s.phases,...(s.activeRoom?{[s.activeRoom]:'closing'}:{}),[id]:'opening'},interacted:true};
  }),
  closeRoom:()=>set(s=>s.activeRoom?{activeRoom:null,phases:{...s.phases,[s.activeRoom]:'closing'}}:{}),
  hover:(id)=>set(s=>{const phases={...s.phases};if(s.hovered&&phases[s.hovered]==='focused')phases[s.hovered]='idle';if(id&&phases[id]==='idle')phases[id]='focused';return {hovered:id,phases};}),
  finish:(id,phase)=>set(s=>{
    const current=s.phases[id];
    if((current==='opening'&&phase==='open')||(current==='closing'&&phase==='idle'))return {phases:{...s.phases,[id]:phase}};
    return {};
  }),
  openDialog:(dialog)=>set({dialog, hint:'',interacted:true}), setHint:(hint)=>set({hint}),
  setEvening:()=>set(s=>({evening:!s.evening,interacted:true})),
  setReducedMotion:(reducedMotion)=>set({reducedMotion}),
  setView:(name)=>set(s=>({activeRoom:null,phases:{...s.phases,...(s.activeRoom?{[s.activeRoom]:'closing'}:{})}, view:{name,key:s.view.key+1},interacted:true})),
  touch:()=>set({interacted:true}),
}));
