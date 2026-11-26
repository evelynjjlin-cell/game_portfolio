import { useWorld } from '../../hooks/useWorld';
import { roomById } from '../../config/rooms';
import { Dialog } from '../ui/Dialog';
import { useCallback } from 'react';
export type CaseStudyContent={
 overview:string;role:string;mechanics?:string;playerExperience?:string;research?:string;
 process?:string;prototyping?:string;iteration?:string;outcomes?:string;reflection?:string;
 media?:{type:'image'|'video';src:string;alt:string}[];
};
/** Intentionally empty. Publish only verified real content in a future phase. */
export const caseStudyContent:Record<string,CaseStudyContent>={};
const sectionNames:Record<string,string>={overview:'Overview',role:'Role & responsibilities',mechanics:'Game mechanics',playerExperience:'Player experience',research:'UX research',process:'Design process',prototyping:'Prototyping',iteration:'Iteration',outcomes:'Outcomes',reflection:'Reflection'};
export function CaseStudy(){
 const active=useWorld(s=>s.activeRoom),phases=useWorld(s=>s.phases),cameraPhase=useWorld(s=>s.cameraPhase);const close=useCallback(()=>useWorld.getState().closeRoom(),[]);if(!active)return null;
 const room=roomById[active],content=caseStudyContent[room.project.contentRef];
 if(room.availability!=='published'||!content||phases[active]!=='open'||cameraPhase!=='room')return null;
 return <Dialog title={room.project.title} close={close}>{Object.entries(sectionNames).map(([key,label])=>{const text=content[key as keyof CaseStudyContent];return typeof text==='string'&&text?<section key={key}><h2>{label}</h2><p>{text}</p></section>:null;})}{content.media?.map((m,i)=>m.type==='image'?<img key={i} src={m.src} alt={m.alt} style={{maxWidth:'100%'}}/>:<video key={i} controls src={m.src} aria-label={m.alt} style={{maxWidth:'100%'}}/>)}{room.project.prototypeUrl&&<a className="solid-button" href={room.project.prototypeUrl} target="_blank" rel="noopener noreferrer">Play the prototype</a>}{room.project.route&&<a className="text-button" href={room.project.route}>Read the full case study</a>}</Dialog>;
}
