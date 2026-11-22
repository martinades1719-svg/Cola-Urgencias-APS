import { createFileRoute } from '@tanstack/react-router';
import { DashboardPage } from '@/features/dashboard/DashboardPage';
import { PermissionGuard } from '@/layouts/StaffLayout';
import { pageHead } from '@/utils/metadata';
export const Route = createFileRoute('/_staff/resumen')({head:()=>pageHead('Resumen de atención','Resumen de actividad y atención del centro de urgencias APS.'),component:Page});
function Page(){return <DashboardPage/>;}
