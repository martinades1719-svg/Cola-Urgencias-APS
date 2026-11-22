import { createFileRoute } from '@tanstack/react-router';
import { ArrivalPage } from '@/features/registration/ArrivalPage';
import { pageHead } from '@/utils/metadata';
export const Route = createFileRoute('/registrar')({head:()=>pageHead('Registrar llegada','Registro de llegada y generación de ticket de urgencias APS.'),component:ArrivalPage});
