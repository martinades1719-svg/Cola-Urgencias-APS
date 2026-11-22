import { createFileRoute } from '@tanstack/react-router';
import { HistoryPage } from '@/features/history/HistoryPage';
import { PermissionGuard } from '@/layouts/StaffLayout';
import { pageHead } from '@/utils/metadata';
export const Route = createFileRoute('/_staff/historial')({head:()=>pageHead('Historial de episodios','Consulta del historial de episodios, evaluaciones y cierres APS.'),component:Page});
function Page(){return <PermissionGuard roles={['RECEPTION','TRIAGE','CLINICAL_MANAGER']}><HistoryPage/></PermissionGuard>;}
