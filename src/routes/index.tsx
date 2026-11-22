import { createFileRoute, Link } from '@tanstack/react-router';
import { ArrowRight, ClipboardPlus, Search, ShieldCheck } from 'lucide-react';
import { PublicLayout } from '@/layouts/PublicLayout';
import { SafetyNote } from '@/components/shared/Primitives';
import { Button } from '@/components/ui/button';
import { pageHead } from '@/utils/metadata';

export const Route = createFileRoute('/')({
  head: () => pageHead('Portal de pacientes', 'Registra tu llegada y consulta de forma privada el estado de tu ticket de urgencias APS.'),
  component: Index,
});

function Index() {
  return <PublicLayout>
    <section className="public-welcome">
      <span className="public-eyebrow"><ShieldCheck size={15}/>PORTAL DE PACIENTES</span>
      <h1 className="public-title">Cola Urgencias APS</h1>
      <p className="public-description">Registra tu llegada y consulta el estado de tu atención. El equipo de salud evaluará tu prioridad de forma presencial.</p>
      <SafetyNote/>
      <div className="patient-actions">
        <article className="patient-action primary"><span className="patient-action-icon"><ClipboardPlus/></span><h2>Registrar mi llegada</h2><p>Si acabas de llegar al centro, registra tus datos para recibir tu ticket de atención.</p><Button size="lg" asChild><Link to="/registrar">Registrar llegada<ArrowRight/></Link></Button></article>
        <article className="patient-action"><span className="patient-action-icon"><Search/></span><h2>Consultar mi atención</h2><p>¿Ya tienes un ticket? Revisa tu estado, la espera aproximada y el box cuando te llamen.</p><Button size="lg" variant="outline" asChild><Link to="/mi-ticket" search={{codigo:''}}>Consultar mi ticket<ArrowRight/></Link></Button></article>
      </div>
    </section>
    <section className="public-process" aria-label="Etapas de la atención">{[
      ['Registra tu llegada','Recibe un ticket único y privado.'],['Evaluación de triage','El equipo asigna tu prioridad presencialmente.'],['Espera tu llamado','Consulta tu estado y la espera aproximada.'],['Recibe atención','Dirígete al box indicado cuando te llamen.'],
    ].map(([title,description],index)=><article key={title}><span className="process-number">{index+1}</span><div><h3>{title}</h3><p>{description}</p></div></article>)}</section>
  </PublicLayout>;
}
