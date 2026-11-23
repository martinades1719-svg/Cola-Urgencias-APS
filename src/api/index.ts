import { http, setAccessToken, USE_MOCKS } from './client';
import { mockApi } from '@/mocks/adapter';
import type { ApiResponse, ArrivalInput, AssessmentInput, AuthSession, User, PublicStatus, Episode, QueueItem, QueuePosition, Alert, AuditLog, DashboardMetrics, Role } from '@/types';
const get = async <T,>(path: string) => (await http<ApiResponse<T>>(path)).data;
const post = async <T,>(path:string, input:unknown={}) => (await http<ApiResponse<T>>(path,'POST',input)).data;
export const authService = {
 login: async (email:string,password:string):Promise<AuthSession> => {const session=USE_MOCKS?await mockApi.login(email,password):await post<AuthSession>('/api/auth/login',{email,password});setAccessToken(session.accessToken);if(USE_MOCKS) sessionStorage.setItem('aps-demo-email',session.user.email);return session;},
 me:()=>USE_MOCKS?mockApi.me():get<User>('/api/auth/me'),
 refresh:async()=>{const session=USE_MOCKS?await mockApi.refresh():await post<AuthSession>('/api/auth/refresh');if(session)setAccessToken(session.accessToken);return session;},
 restore:async()=>{if(USE_MOCKS)return mockApi.restore();try {const session=await authService.refresh();if(session)await authService.me();return session;}catch{return null;}},
 logout:async()=>{if(USE_MOCKS)await mockApi.logout();else await post('/api/auth/logout');setAccessToken(null);sessionStorage.removeItem('aps-demo-email');},
};
export const publicService = {arrival:(input:ArrivalInput)=>USE_MOCKS?mockApi.arrival(input):post<{ticket:string;token:string;arrivedAt:string}>('/api/public/arrival',input),status:(token:string)=>USE_MOCKS?mockApi.publicStatus(token):get<PublicStatus>(`/api/public/status/${encodeURIComponent(token)}`)};
export const episodeService = {
 list:()=>USE_MOCKS?mockApi.episodes():get<Episode[]>('/api/episodes'),
 detail:(id:string)=>USE_MOCKS?mockApi.episode(id):get<Episode>(`/api/episodes/${id}`),
 pending:()=>USE_MOCKS?mockApi.pending():get<Episode[]>('/api/episodes/pending-triage'),
 triage:(id:string,input:AssessmentInput)=>USE_MOCKS?mockApi.triage(id,input):post<Episode>(`/api/episodes/${id}/triage`,input),
 reassess:(id:string,input:AssessmentInput)=>USE_MOCKS?mockApi.reassess(id,input):post<Episode>(`/api/episodes/${id}/reassessments`,input),
 call:(id:string,box:string)=>USE_MOCKS?mockApi.transition(id,'CALLED',box):post<Episode>(`/api/episodes/${id}/call`,{box}),
 startCare:(id:string)=>USE_MOCKS?mockApi.transition(id,'IN_CARE',''):post<Episode>(`/api/episodes/${id}/start-care`),
 close:(id:string,reason:string)=>USE_MOCKS?mockApi.transition(id,['Retiro voluntario','Abandono'].includes(reason)?'WITHDRAWN':'CLOSED',reason):post<Episode>(`/api/episodes/${id}/close`,{reason}),
};
export const queueService={list:()=>USE_MOCKS?mockApi.queue():get<QueueItem[]>('/api/queue'),position:(id:string)=>USE_MOCKS?mockApi.position(id):get<QueuePosition>(`/api/queue/${id}/position`)};
export const alertService={list:()=>USE_MOCKS?mockApi.alerts():get<Alert[]>('/api/alerts'),take:(id:string)=>USE_MOCKS?mockApi.alertAction(id,'take'):post<Alert>(`/api/alerts/${id}/take`),resolve:(id:string)=>USE_MOCKS?mockApi.alertAction(id,'resolve'):post<Alert>(`/api/alerts/${id}/resolve`)};
export const reportService={dashboard:()=>USE_MOCKS?mockApi.dashboard():get<DashboardMetrics>('/api/reports/dashboard')};
export const auditService={list:()=>USE_MOCKS?mockApi.audit():get<AuditLog[]>('/api/audit-logs')};
export const userService={list:()=>USE_MOCKS?mockApi.users():get<User[]>('/api/users'),create:(input:{email:string;role:Role})=>USE_MOCKS?mockApi.createUser(input):post<User>('/api/users',input),status:(id:string,active:boolean)=>USE_MOCKS?mockApi.userStatus(id,active):http<ApiResponse<User>>(`/api/users/${id}/status`,'PATCH',{active}).then(r=>r.data)};
export const settingsService={threshold:(value?:number)=>USE_MOCKS?mockApi.threshold(value):Promise.reject(new Error('La configuración requiere un endpoint adicional en FastAPI.'))};
export { USE_MOCKS };
export * from './health';