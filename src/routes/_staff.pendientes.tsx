import { createFileRoute } from '@tanstack/react-router';
import { PendingPage } from '@/features/triage/PendingPage';
import { PermissionGuard } from '@/layouts/StaffLayout';
import { pageHead } from '@/utils/metadata';
export const Route = createFileRoute('/_staff/pendientes')({head:()=>pageHead('Pendientes de triage','Pacientes que esperan una evaluación presencial de triage APS.'),component:Page});
function Page(){return <PermissionGuard roles={['RECEPTION','TRIAGE','CLINICAL_MANAGER']}><PendingPage/></PermissionGuard>;}
