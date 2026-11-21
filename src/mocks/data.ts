import type { Alert, AuditLog, Episode, EpisodeStatus, Priority, User } from '@/types';
const ago = (minutes: number) => new Date(Date.now() - minutes * 60000).toISOString();
export const demoUsers: User[] = [
 {id:'u1',email:'recepcion@demo.cl',role:'RECEPTION',active:true},
 {id:'u2',email:'triage@demo.cl',role:'TRIAGE',active:true},
 {id:'u3',email:'jefatura@demo.cl',role:'CLINICAL_MANAGER',active:true},
 {id:'u4',email:'admin@demo.cl',role:'ADMIN',active:true},
];
const names = ['Valentina','Jorge','Francisca','Pedro','Isabel','Diego','Antonia','Carlos','Sofía','Tomás','Elena','Matías','Paula','Ignacio','Laura','Benjamín','Ana','Felipe'];
const lastNames = ['González','Pérez','Muñoz','Soto','Rojas','Díaz'];
const tickets = ['A7K2P9','M4R8T1','B6N3W2','H9D5L7','F2X8Q4','J3V6S9','P8C4A2','T5E9K3','R1N7B6','W6L2F8','D4Q9M5','X8A3V7','K2S6H1','N9P4J8','E7T1R3','L5B8C2','Q3M7D9','V8F2X6'];
export const episodes: Episode[] = names.map((name, i) => {
 const status: EpisodeStatus = i < 4 ? 'PENDING_TRIAGE' : i < 12 ? 'WAITING' : i < 14 ? 'CALLED' : i < 16 ? 'IN_CARE' : 'CLOSED';
 const priority: Priority | null = i < 4 ? null : (['C2','C3','C4','C3','C5','C1','C4','C2','C3','C4','C2','C3','C4','C5'] as Priority[])[i-4] ?? 'C5';
 const arrivedAt = ago(12 + i * 8);
 const triageAt = priority ? ago(i === 9 ? 3 : 5 + (i-4) * 7) : null;
 return {id:`e${i+1}`,ticket:`URG-${tickets[i]}`,token:`demo-public-${tickets[i]}`,patient:{id:`p${i+1}`,document:`DEMO-${i+10000}`,firstName:name,lastName:lastNames[i%6] ?? 'Soto',birthDate:'1990-06-15'},status,priority,arrivedAt,updatedAt:triageAt ?? arrivedAt,triageAt,calledAt:status==='CALLED'?ago(8):null,box:status==='CALLED'||status==='IN_CARE'?`Box ${i%3+1}`:null,assessments:priority?[{id:`t${i}`,priority,observation:'Evaluación presencial registrada.',createdAt:triageAt ?? arrivedAt,userId:'u2'}]:[],reassessments:i===7?[{id:'r1',priority:'C3',previousPriority:'C4',reason:'Reevaluación presencial.',observation:'Nueva evaluación registrada.',createdAt:ago(10),userId:'u2'}]:[],closureReason:status==='CLOSED'?'Atención finalizada':null,closedAt:status==='CLOSED'?ago(3):null,closedBy:status==='CLOSED'?'u1':null};
});
export const alerts: Alert[] = [
 {id:'a1',episodeId:'e7',ticket:episodes[6]?.ticket ?? '',priority:'C4',type:'LONG_WAIT',status:'OPEN',createdAt:ago(18),takenBy:null},
 {id:'a2',episodeId:'e8',ticket:episodes[7]?.ticket ?? '',priority:'C3',type:'REASSESSMENT',status:'OPEN',createdAt:ago(12),takenBy:null},
 {id:'a3',episodeId:'e13',ticket:episodes[12]?.ticket ?? '',priority:'C3',type:'CALLED_DELAY',status:'OPEN',createdAt:ago(8),takenBy:null},
];
export const auditLogs: AuditLog[] = [{id:'log1',createdAt:ago(10),user:'Daniela Rojas',role:'TRIAGE',action:'Reevaluación de prioridad',entity:'Episodio',ticket:episodes[7]?.ticket ?? '',previous:'C4',next:'C3',result:'Completado'}, ...episodes.filter(e=>e.priority).slice(0,6).map((e,i)=>({id:`log${i+2}`,createdAt:e.triageAt ?? e.arrivedAt,user:'Daniela Rojas',role:'TRIAGE' as const,action:'Triage inicial',entity:'Episodio',ticket:e.ticket,previous:'Pendiente de triage',next:e.priority ?? '',result:'Completado'}))];
