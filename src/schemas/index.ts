import { z } from 'zod';
export const arrivalSchema = z.object({ document: z.string().min(5, 'Ingresa un documento válido.'), firstName: z.string().min(2, 'Ingresa tus nombres.'), lastName: z.string().min(2, 'Ingresa tus apellidos.'), birthDate: z.string().min(1, 'Selecciona una fecha.').refine(v => Date.parse(v) <= Date.now(), 'La fecha no puede ser futura.'), privacy: z.boolean().refine(v => v, 'Debes aceptar el aviso de privacidad.') });
export const loginSchema = z.object({ email: z.string().email('Ingresa un correo válido.'), password: z.string().min(1, 'Ingresa la contraseña.') });
export const assessmentSchema = z.object({ priority: z.enum(['C1','C2','C3','C4','C5']), observation: z.string().max(250, 'Máximo 250 caracteres.'), reason: z.string().max(250) });
export const userSchema = z.object({ name: z.string().min(2, 'Ingresa un nombre.'), email: z.string().email('Ingresa un correo válido.'), role: z.enum(['RECEPTION','TRIAGE','CLINICAL_MANAGER','ADMIN']) });
