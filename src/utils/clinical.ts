import type { Episode, EpisodeStatus, Priority, Role, WaitEstimate } from '@/types';
export const priorities: Priority[] = ['C1', 'C2', 'C3', 'C4', 'C5'];
export const statusLabels: Record<EpisodeStatus, string> = { PENDING_TRIAGE: 'Pendiente de triage', WAITING: 'Esperando atención', CALLED: 'Paciente llamado', IN_CARE: 'En atención', CLOSED: 'Atención finalizada', WITHDRAWN: 'Paciente retirado' };
export const roleLabels: Record<Role, string> = { RECEPTION: 'Recepción', TRIAGE: 'Triage', CLINICAL_MANAGER: 'Jefatura clínica', ADMIN: 'Administración' };
export const canAssess = (role: Role) => role === 'TRIAGE' || role === 'CLINICAL_MANAGER';
export const canOperate = (role: Role) => role === 'RECEPTION' || role === 'CLINICAL_MANAGER';
export const canManageUsers = (role: Role) => role === 'ADMIN';
export const canAudit = (role: Role) => role === 'ADMIN' || role === 'CLINICAL_MANAGER';
export const sortQueue = (episodes: Episode[]) => episodes.filter(e => e.status === 'WAITING' && e.priority !== null).sort((a,b) => (a.priority ?? 'C5').localeCompare(b.priority ?? 'C5') || Date.parse(a.triageAt ?? a.arrivedAt) - Date.parse(b.triageAt ?? b.arrivedAt));
export function estimateWait(episode: Episode, queue: Episode[], professionals = 3, averageMinutes = 15): WaitEstimate {
  const index = queue.findIndex(e => e.id === episode.id);
  if (index < 0 || professionals <= 0 || averageMinutes <= 0) return { min: 0, max: 0, available: false };
  const base = Math.ceil((index + 1) * averageMinutes / professionals);
  return { min: Math.max(0, base - 5), max: base + 15, available: true };
}
export function validateAssessment(role: Role, current: Priority | null, next: Priority, reason: string) {
  if (!canAssess(role)) throw new Error('No tienes permisos para modificar prioridades.');
  if (current !== null && current !== next && !reason.trim()) throw new Error('El motivo es obligatorio al cambiar la prioridad.');
}
export const minutesSince = (date: string) => Math.max(0, Math.floor((Date.now() - Date.parse(date)) / 60000));
export const time = (date: string) => new Date(date).toLocaleTimeString('es-CL', {hour: '2-digit', minute: '2-digit', hour12: false});
export const maskedName = (e: Episode) => `${e.patient.firstName} ${e.patient.lastName.charAt(0)}.`;
export const waitLabel = (estimate: WaitEstimate) => estimate.available ? `${estimate.min} a ${estimate.max} min` : 'Estimación temporalmente no disponible.';
export function randomTicket() { return `URG-${crypto.randomUUID().replaceAll('-', '').slice(0, 6).toUpperCase()}`; }
export const transitions: Partial<Record<EpisodeStatus, EpisodeStatus>> = { WAITING: 'CALLED', CALLED: 'IN_CARE', IN_CARE: 'CLOSED' };
