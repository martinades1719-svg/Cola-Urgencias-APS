import { Link } from '@tanstack/react-router';
import { ArrowUpRight, ShieldCheck } from 'lucide-react';
import type { ReactNode } from 'react';
import { Brand, DemoNotice } from '@/components/shared/Primitives';
import { Button } from '@/components/ui/button';
import { USE_MOCKS } from '@/api';
export function PublicLayout({children}:{children:ReactNode}){return <><header className="public-header"><Link to="/" aria-label="Cola Urgencias APS, inicio"><Brand/></Link><div className="public-header-actions">{USE_MOCKS&&<DemoNotice/>}<Button variant="outline" asChild><Link to="/acceso">Acceso funcionarios<ArrowUpRight/></Link></Button></div></header><main className="public-main">{children}<footer className="public-footer"><span>Cola Urgencias APS · Atención primaria de salud</span><span className="flex items-center gap-2"><ShieldCheck size={14}/>Tu información es privada y protegida</span></footer></main></>;}
