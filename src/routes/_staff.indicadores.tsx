import { createFileRoute } from '@tanstack/react-router';
import { ReportsPage } from '@/features/reports/ReportsPage';
import { PermissionGuard } from '@/layouts/StaffLayout';
import { pageHead } from '@/utils/metadata';
export const Route = createFileRoute('/_staff/indicadores')({head:()=>pageHead('Indicadores de atención','Indicadores demostrativos de tiempos y actividad del centro APS.'),component:Page});
function Page(){return <PermissionGuard roles={['CLINICAL_MANAGER']}><ReportsPage/></PermissionGuard>;}
