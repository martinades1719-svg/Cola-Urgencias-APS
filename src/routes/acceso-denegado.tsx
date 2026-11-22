import { createFileRoute } from '@tanstack/react-router';
import { AccessDenied } from '@/layouts/StaffLayout';
import { pageHead } from '@/utils/metadata';
export const Route = createFileRoute('/acceso-denegado')({head:()=>pageHead('Acceso denegado','Esta sección requiere permisos de acceso adicionales.'),component:AccessDenied});
