import { createFileRoute } from '@tanstack/react-router';
import { z } from 'zod';
import { PatientStatusPage } from '@/features/patient-status/PatientStatusPage';
import { pageHead } from '@/utils/metadata';
export const Route = createFileRoute('/mi-ticket')({ validateSearch: (search: Record<string, unknown>) => z.object({codigo:z.string().catch('')}).parse(search), head:()=>pageHead('Consultar mi ticket','Consulta privada del estado, posición aproximada y rango de espera de tu ticket APS.'), component: Page });
function Page(){ const {codigo}=Route.useSearch();return <PatientStatusPage initialCode={codigo}/>; }
