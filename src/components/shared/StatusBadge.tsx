import type { EpisodeStatus, Priority } from '@/types';
import { statusLabels } from '@/utils/clinical';
export function PriorityBadge({priority}:{priority:Priority|null}){return priority?<span className={`priority-badge priority-${priority.toLowerCase()}`}><span className="priority-dot"/>{priority}</span>:<span className="text-muted-foreground">—</span>;}
export function StatusBadge({status}:{status:EpisodeStatus}){return <span className={`status-badge status-${status.toLowerCase()}`}><span/>{statusLabels[status]}</span>;}
