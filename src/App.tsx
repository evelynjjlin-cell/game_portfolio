import { Component, Suspense, lazy, useCallback, useEffect, useState, type ReactNode } from 'react';
import { Sun, Moon, RotateCcw, X, SlidersHorizontal, BookOpen } from 'lucide-react';
import { profile } from './config/profile';
import { rooms, roomById } from './config/rooms';
import { useWorld } from './hooks/useWorld';
import { Dialog } from './components/ui/Dialog';
import { Contact } from './components/contact/Contact';
const WorldScene=lazy(()=>import('./components/scene/WorldScene'));
class SceneBoundary extends Component<{children:ReactNode},{failed:boolean}>{state={failed:false};static getDerivedStateFromError(){return {failed:true};}render(){return this.state.failed?<div className="scene-fallback"><BookOpen size={38}/><h2>A little world, best seen in 3D.</h2><p>The 3D scene could not start on this device.<br/>You can still find me through About and Contact.</p></div>:this.props.children;}}
export default function App(){
 const {dialog,evening,activeRoom,hint,interacted,openDialog,setView,setEvening,closeRoom,selectRoom,phases}=useWorld();
 const [access,setAccess]=useState(false);const close=useCallback(()=>openDialog(null),[openDialog]);
 useEffect(()=>{const media=matchMedia('(prefers-reduced-motion: reduce)');const update=()=>useWorld.getState().setReducedMotion(media.matches);update();media.addEventListener('change',update);return()=>media.removeEventListener('change',update);},[]);
 useEffect(()=>{const key=(e:KeyboardEvent)=>{if(e.key==='Escape'&&!useWorld.getState().dialog){closeRoom();setAccess(false);}};window.addEventListener('keydown',key);return()=>window.removeEventListener('keydown',key);},[closeRoom]);
 return <main className={`world-page ${evening?'is-evening':''}`}>
  <a className="skip-link" href="#explore-controls">Skip to exploration controls</a>
  <header><a href="#" className="identity" onClick={e=>{e.preventDefault();setView('reset');}} aria-label="Evelyn Lin, reset view"><span>{profile.name}</span><small>{profile.discipline}</small></a><nav aria-label="Main navigation"><button onClick={()=>openDialog('about')}>About</button><button onClick={()=>openDialog('contact')}>Contact</button><a href={profile.portfolio} target="_blank" rel="noopener noreferrer" className="portfolio-link">UX Portfolio <span aria-hidden="true">↗</span></a></nav></header>
  <div className="scene" aria-label="Interactive miniature house on an open book"><SceneBoundary><Suspense fallback={<div className="loading"><BookOpen size={24}/><span>Setting the scene…</span></div>}><WorldScene/></Suspense></SceneBoundary></div>
  <div className="scene-caption" aria-hidden="true"><span>A SMALL WORLD,</span><span>A LITTLE CURIOSITY.</span></div>
  <div className="lighting-control"><button className="icon-button" onClick={setEvening} aria-label={evening?'Switch to daylight':'Switch to evening'} title={evening?'Daylight':'Evening'}>{evening?<Moon size={19}/>:<Sun size={20}/>}</button><span>{evening?'Evening':'Daylight'}</span></div>
  <div className={`interaction-hint ${hint?'visible':''}`} role="status">{hint}</div>
  {activeRoom&&<div className="room-controls"><span>{roomById[activeRoom].label}</span><button onClick={closeRoom}><X size={16}/> Close room</button></div>}
  <footer id="explore-controls"><div className={`gesture-hint ${interacted?'quiet':''}`}><span className="drag-icon" aria-hidden="true">⤺</span><span>Drag to explore<span className="desktop-hint"> · Scroll to zoom</span><small>Open a window. Stay curious.</small></span></div><div className="view-controls" role="group" aria-label="Camera controls"><button onClick={()=>setView('front')}>Front</button><span/><button onClick={()=>setView('back')}>Back</button><span/><button aria-label="Reset view" title="Reset view" onClick={()=>setView('reset')}><RotateCcw size={17}/></button></div><button className="explore-button" onClick={()=>setAccess(!access)} aria-expanded={access} aria-controls="room-navigation"><SlidersHorizontal size={17}/><span>Explore</span></button></footer>
  {access&&<section className="access-panel" id="room-navigation" aria-label="Keyboard exploration"><div className="panel-heading"><h2>Find a room</h2><button className="icon-button" aria-label="Close room navigation" onClick={()=>setAccess(false)}><X size={18}/></button></div><p>Choose a window, or explore by touch.</p><div className="room-list">{rooms.map(r=><button key={r.id} aria-pressed={activeRoom===r.id} onFocus={()=>useWorld.getState().hover(r.id)} onBlur={()=>useWorld.getState().hover(null)} onClick={()=>{selectRoom(r.id);setAccess(false);}}>{r.label}<span>{phases[r.id]==='open'?'Open':'＋'}</span></button>)}</div><button className="text-button" onClick={()=>{openDialog('contact');setAccess(false);}}>Open the mailbox</button></section>}
  {dialog&&<Dialog title={dialog==='about'?profile.greeting:'Let’s make something.'} close={close}>{dialog==='about'?<><p>{profile.introduction}</p><p>{profile.detail}</p><a className="solid-button" href={profile.portfolio} target="_blank" rel="noopener noreferrer">Visit my UX portfolio</a></>:<Contact/>}</Dialog>}
 </main>;
}
