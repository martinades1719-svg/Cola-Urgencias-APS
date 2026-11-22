import { createFileRoute } from '@tanstack/react-router';
import { QueuePage } from '@/features/queue/QueuePage';
import { PermissionGuard } from '@/layouts/StaffLayout';
import { pageHead } from '@/utils/metadata';
export const Route = createFileRoute('/_staff/cola')({head:()=>pageHead('Cola de atención','Cola de urgencias organizada por prioridad clínica y antigüedad.'),component:Page});
function Page(){return <PermissionGuard roles={['RECEPTION','TRIAGE','CLINICAL_MANAGER']}><QueuePage/></PermissionGuard>;}
