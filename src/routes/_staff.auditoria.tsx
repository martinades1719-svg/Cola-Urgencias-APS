import { createFileRoute } from '@tanstack/react-router';
import { AuditPage } from '@/features/audit/AuditPage';
import { PermissionGuard } from '@/layouts/StaffLayout';
import { pageHead } from '@/utils/metadata';
export const Route = createFileRoute('/_staff/auditoria')({head:()=>pageHead('Auditoría de acciones','Trazabilidad de acciones de usuarios del centro de urgencias APS.'),component:Page});
function Page(){return <PermissionGuard roles={['CLINICAL_MANAGER','ADMIN']}><AuditPage/></PermissionGuard>;}
