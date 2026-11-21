export type Role = 'RECEPTION' | 'TRIAGE' | 'CLINICAL_MANAGER' | 'ADMIN';
export type Priority = 'C1' | 'C2' | 'C3' | 'C4' | 'C5';
export type EpisodeStatus = 'PENDING_TRIAGE' | 'WAITING' | 'CALLED' | 'IN_CARE' | 'CLOSED' | 'WITHDRAWN';
export interface User { id: string; email: string; role: Role; active: boolean }
export interface Patient { id: string; document: string; firstName: string; lastName: string; birthDate: string }
export interface TriageAssessment { id: string; priority: Priority; observation: string; createdAt: string; userId: string }
export interface Reassessment extends TriageAssessment { previousPriority: Priority; reason: string }
export interface Episode { id: string; ticket: string; token: string; patient: Patient; status: EpisodeStatus; priority: Priority | null; arrivedAt: string; updatedAt: string; triageAt: string | null; calledAt: string | null; box: string | null; assessments: TriageAssessment[]; reassessments: Reassessment[]; closureReason: string | null; closedAt: string | null; closedBy: string | null }
export interface WaitEstimate { min: number; max: number; available: boolean }
export interface QueuePosition { approximate: number | null; estimate: WaitEstimate; reordered: boolean }
export interface QueueItem extends Episode { position: number; estimate: WaitEstimate; hasAlert: boolean }
export interface PublicStatus { ticket: string; status: EpisodeStatus; arrivedAt: string; updatedAt: string; box: string | null; position: QueuePosition }
export interface Alert { id: string; episodeId: string; ticket: string; priority: Priority; type: 'LONG_WAIT' | 'REASSESSMENT' | 'CALLED_DELAY'; status: 'OPEN' | 'TAKEN' | 'RESOLVED'; createdAt: string; takenBy: string | null }
export interface AuditLog { id: string; createdAt: string; user: string; role: Role; action: string; entity: string; ticket: string; previous: string; next: string; result: string }
export interface DashboardMetrics { pending: number; waiting: number; called: number; inCare: number; alerts: number; averageWait: number; registered: number; arrivalTriage: number; triageCare: number; reassessments: number; priorityChanges: number; resolvedAlerts: number; withdrawals: number; estimateAccuracy: number; byPriority: { priority: Priority; count: number }[] }
export interface ApiResponse<T> { data: T }
export interface PaginatedResponse<T> { data: T[]; total: number; page: number; pageSize: number }
export interface ArrivalInput { document: string; firstName: string; lastName: string; birthDate: string; privacy: boolean }
export interface AssessmentInput { priority: Priority; observation: string; reason: string }
export interface AuthSession { user: User; accessToken: string; refreshToken: string }
