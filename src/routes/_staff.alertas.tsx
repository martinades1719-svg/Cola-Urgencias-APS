import { createFileRoute } from '@tanstack/react-router';
import { AlertsPage } from '@/features/alerts/AlertsPage';
import { PermissionGuard } from '@/layouts/StaffLayout';
import { pageHead } from '@/utils/metadata';
export const Route = createFileRoute('/_staff/alertas')({head:()=>pageHead('Alertas de atención','Gestión de alertas de espera y reevaluación de urgencias APS.'),component:Page});
function Page(){return <PermissionGuard roles={['RECEPTION','TRIAGE','CLINICAL_MANAGER']}><AlertsPage/></PermissionGuard>;}
