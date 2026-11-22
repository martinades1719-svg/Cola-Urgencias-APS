import { createFileRoute } from '@tanstack/react-router';
import { LoginPage } from '@/features/auth/LoginPage';
import { pageHead } from '@/utils/metadata';
export const Route = createFileRoute('/acceso')({head:()=>pageHead('Acceso funcionarios','Acceso de demostración para el equipo de urgencias APS.'),component:LoginPage});
