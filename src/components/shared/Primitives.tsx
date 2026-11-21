import { Activity, ArrowUpRight, Inbox, Loader2, RefreshCw, Search, ShieldCheck } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { ReactNode } from 'react';
export function Brand({compact=false}:{compact?:boolean}){return <div className="brand"><span className="brand-mark"><Activity size={24}/></span><span>Cola Urgencias <strong>APS</strong>{!compact&&<small>ATENCIÓN PRIMARIA DE SALUD</small>}</span></div>;}
export function PageHeading({eyebrow,title,description,action}:{eyebrow?:string;title:string;description:string;action?:ReactNode}){return <div className="page-heading"><div>{eyebrow&&<span className="eyebrow">{eyebrow}</span>}<h1>{title}</h1><p>{description}</p></div>{action}</div>;}
export function Loading(){return <div className="empty-state"><Loader2 className="animate-spin"/><p>Cargando información…</p></div>;}
export function Empty({text='No hay registros para los filtros seleccionados.'}:{text?:string}){return <div className="empty-state"><Inbox size={30}/><p>{text}</p></div>;}
export function ErrorState({error,retry}:{error:Error;retry:()=>void}){return <div className="empty-state"><p>{error.message}</p><Button variant="outline" onClick={retry}><RefreshCw/>Volver a intentar</Button></div>;}
export function SearchInput({value,onChange,placeholder='Buscar por ticket…'}:{value:string;onChange:(v:string)=>void;placeholder?:string}){return <div className="search-input"><Search size={17}/><input aria-label={placeholder} value={value} onChange={e=>onChange(e.target.value)} placeholder={placeholder}/></div>;}
export function DemoNotice(){return <span className="demo-badge"><span/>Modo demostración</span>;}
export function SafetyNote(){return <div className="safety-note"><ShieldCheck size={20}/><p>La atención se organiza según la gravedad de cada paciente y no exclusivamente por orden de llegada.</p></div>;}
export function SectionTitle({title,children}:{title:string;children?:ReactNode}){return <div className="section-title"><h2>{title}</h2>{children}</div>;}
export function TinyLink({children}:{children:ReactNode}){return <span className="tiny-link">{children}<ArrowUpRight size={15}/></span>;}
