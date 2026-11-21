import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { authService } from '@/api';
import { useQueryClient } from '@tanstack/react-query';
import type { User } from '@/types';
interface AuthContextValue {user:User|null; loading:boolean; login:(email:string,password:string)=>Promise<void>;logout:()=>Promise<void>}
const AuthContext=createContext<AuthContextValue|null>(null);
export function AuthProvider({children}:{children:ReactNode}) {
 const [user,setUser]=useState<User|null>(null);const [loading,setLoading]=useState(true);const client=useQueryClient();
 useEffect(()=>{let mounted=true;authService.restore().then(session=>{if(mounted)setUser(session?.user ?? null);}).finally(()=>{if(mounted)setLoading(false);});return()=>{mounted=false;};},[]);
 async function login(email:string,password:string){const session=await authService.login(email,password);const verified=await authService.me();client.clear();setUser({...session.user,...verified});}
 async function logout(){await authService.logout();setUser(null);client.clear();}
 return <AuthContext.Provider value={{user,loading,login,logout}}>{children}</AuthContext.Provider>;
}
export function useAuth(){const context=useContext(AuthContext);if(!context)throw new Error('AuthProvider missing');return context;}
