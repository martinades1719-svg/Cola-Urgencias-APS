import { createFileRoute } from '@tanstack/react-router';
import { UsersPage } from '@/features/users/UsersPage';
import { PermissionGuard } from '@/layouts/StaffLayout';
import { pageHead } from '@/utils/metadata';
export const Route = createFileRoute('/_staff/usuarios')({head:()=>pageHead('Usuarios del centro','Gestión administrativa de correos, roles y estados de acceso APS.'),component:Page});
function Page(){return <PermissionGuard roles={['ADMIN']}><UsersPage/></PermissionGuard>;}
