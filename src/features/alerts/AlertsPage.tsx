import { useState } from 'react';
import { useMutation, useQueryClient, useSuspenseQuery } from '@tanstack/react-query';
import { AlertTriangle, Bell, Check, UserCheck } from 'lucide-react';
import { toast } from 'sonner';
import { alertsQuery } from '@/api/queries';
import { alertService } from '@/api';
import { useAuth } from '@/features/auth/AuthProvider';
import { canAssess, minutesSince } from '@/utils/clinical';
import { PriorityBadge } from '@/components/shared/StatusBadge';
import { Empty, PageHeading } from '@/components/shared/Primitives';
import { Button } from '@/components/ui/button';
import type { Alert } from '@/types';
export const alertLabels:Record<Alert['type'],string>={LONG_WAIT:'Espera prolongada',REASSESSMENT:'Reevaluación pendiente',CALLED_DELAY:'Llamado sin iniciar atención'};
export function AlertList({compact=false}:{compact?:boolean}){const {data}=useSuspenseQuery(alertsQuery());const {user}=useAuth();const client=useQueryClient();const [filter,setFilter]=useState('active');const mutation=useMutation({mutationFn:({id,action}:{id:string;action:'take'|'resolve'})=>action==='take'?alertService.take(id):alertService.resolve(id),onSuccess:()=>{client.invalidateQueries();toast.success('Alerta actualizada');},onError:error=>toast.error(error.message)});const filtered=data.filter(a=>filter==='all'||(filter==='active'?a.status!=='RESOLVED':a.status==='RESOLVED'));
 return <>{!compact&&<div className="table-toolbar"><select className="filter-select" aria-label="Estado de alertas" value={filter} onChange={e=>setFilter(e.target.value)}><option value="active">Alertas activas</option><option value="resolved">Resueltas</option><option value="all">Todas las alertas</option></select></div>}<div className="alert-list">{filtered.length?filtered.map(a=><article className="alert-item" key={a.id}><span className={`alert-symbol ${a.priority==='C1'?'critical':''}`}><AlertTriangle size={16}/></span><div className="alert-content"><h3>{alertLabels[a.type]}</h3><div className="flex items-center gap-2"><span className="ticket">{a.ticket}</span><PriorityBadge priority={a.priority}/></div><p>Hace {minutesSince(a.createdAt)} min · {a.status==='TAKEN'?'En gestión':a.status==='RESOLVED'?'Resuelta':'Pendiente'}</p>{user&&canAssess(user.role)&&a.status!=='RESOLVED'&&<div className="alert-bottom">{a.status==='OPEN'&&<Button size="sm" variant="outline" onClick={()=>mutation.mutate({id:a.id,action:'take'})} disabled={mutation.isPending}><UserCheck/>Tomar</Button>}<Button size="sm" variant="ghost" className="text-primary" onClick={()=>mutation.mutate({id:a.id,action:'resolve'})} disabled={mutation.isPending}><Check/>Resolver</Button></div>}</div></article>):<Empty text="No hay alertas en este estado."/>}</div></>;
}
export function AlertsPage(){return <><PageHeading eyebrow="SEGUIMIENTO DE LA ATENCIÓN" title="Alertas" description="Gestiona esperas prolongadas y evaluaciones pendientes. Ninguna alerta modifica automáticamente la prioridad."/><section className="data-section"><div className="section-title"><h2 className="flex items-center gap-2"><Bell size={17}/>Alertas de atención</h2></div><AlertList/></section></>;}
