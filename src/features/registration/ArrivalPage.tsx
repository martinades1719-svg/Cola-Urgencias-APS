import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation } from '@tanstack/react-query';
import { Link } from '@tanstack/react-router';
import { ArrowLeft, ArrowRight, CheckCircle2, Loader2 } from 'lucide-react';
import { QRCodeSVG } from 'qrcode.react';
import { arrivalSchema } from '@/schemas';
import { publicService } from '@/api';
import type { ArrivalInput } from '@/types';
import { PublicLayout } from '@/layouts/PublicLayout';
import { Button } from '@/components/ui/button';
import { SafetyNote } from '@/components/shared/Primitives';
import { time } from '@/utils/clinical';
export function ArrivalPage(){
 const form=useForm<ArrivalInput>({resolver:zodResolver(arrivalSchema),defaultValues:{document:'',firstName:'',lastName:'',birthDate:'',privacy:false}});
 const mutation=useMutation({mutationFn:publicService.arrival});
 const fields=[['document','Documento','Ej. 12.345.678-9'],['firstName','Nombres','Tus nombres'],['lastName','Apellidos','Tus apellidos'],['birthDate','Fecha de nacimiento','']] as const;
 return <PublicLayout><div className="public-form"><Link to="/" className="tiny-link"><ArrowLeft size={15}/>Volver al inicio</Link>{mutation.data?<><h1>Llegada registrada</h1><p>Tu ticket está listo. Conserva este código para consultar tu estado.</p><div className="form-panel"><div className="public-ticket"><CheckCircle2 className="mx-auto text-primary" size={32}/><h2>{mutation.data.ticket}</h2><span className="status-badge status-pending_triage">Pendiente de triage</span><p className="form-note">Llegada: {time(mutation.data.arrivedAt)} · {new Date(mutation.data.arrivedAt).toLocaleDateString('es-CL')}</p><QRCodeSVG className="qr-code" value={`${typeof window!=='undefined'?window.location.origin:''}/mi-ticket?codigo=${mutation.data.token}`}/></div><div className="patient-warning">Todavía no existe una posición en la cola clínica porque el triage está pendiente.</div><Button asChild className="w-full" size="lg"><Link to="/mi-ticket" search={{codigo:mutation.data.token}}>Consultar estado<ArrowRight/></Link></Button></div></>:<><h1>Registrar llegada</h1><p>Completa tus datos para registrar tu llegada. La evaluación de triage será realizada presencialmente por el equipo de salud.</p><form className="form-panel" onSubmit={form.handleSubmit(data=>mutation.mutate(data))}><div className="form-grid">{fields.map(([key,label,placeholder])=><div className="form-field" key={key}><label htmlFor={key}>{label}</label><input id={key} type={key==='birthDate'?'date':'text'} placeholder={placeholder} autoComplete={key==='firstName'?'given-name':key==='lastName'?'family-name':key==='birthDate'?'bday':'off'} {...form.register(key)}/>{form.formState.errors[key]&&<span className="field-error">{form.formState.errors[key]?.message}</span>}</div>)}</div><label className="privacy-check"><input type="checkbox" {...form.register('privacy')}/><span>Acepto el aviso de privacidad: mis datos se usarán únicamente para gestionar esta atención. Esta demostración no debe contener datos reales.</span></label>{form.formState.errors.privacy&&<p className="field-error">{form.formState.errors.privacy.message}</p>}{mutation.error&&<p role="alert" className="field-error mb-4">{mutation.error.message}</p>}<Button size="lg" className="w-full" disabled={mutation.isPending}>{mutation.isPending?<Loader2 className="animate-spin"/>:<ArrowRight/>}Registrar llegada</Button></form><div className="mt-5"><SafetyNote/></div></>}</div></PublicLayout>;
}
