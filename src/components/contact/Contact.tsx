import { useState } from 'react';
import { Copy, Check, Mail, Linkedin, Globe } from 'lucide-react';
import { profile } from '../../config/profile';
export function Contact(){
 const [copied,setCopied]=useState(false);const [error,setError]=useState(false);
 const copy=async()=>{try{await navigator.clipboard.writeText(profile.email);setCopied(true);setError(false);}catch{setError(true);}};
 return <><p>Have something in mind?<br/>I’d love to hear about it.</p><a className="email-address" href={`mailto:${profile.email}`}>{profile.email}</a><div className="contact-actions"><a className="solid-button" href={`mailto:${profile.email}`}><Mail size={17}/> Send email</a><button className="text-button" onClick={copy}>{copied?<Check size={17}/>:<Copy size={17}/>} {copied?'Copied':'Copy email'}</button></div><p className="sr-only" role="status">{copied?'Email copied to clipboard.':''}</p>{error&&<p role="status">Please select and copy the email address above.</p>}<div className="external-links"><a href={profile.linkedin} target="_blank" rel="noopener noreferrer"><Linkedin size={17}/> LinkedIn</a><a href={profile.portfolio} target="_blank" rel="noopener noreferrer"><Globe size={17}/> UX Portfolio</a></div></>;
}
