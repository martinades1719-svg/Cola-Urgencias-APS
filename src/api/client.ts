export const USE_MOCKS = import.meta.env['VITE_USE_MOCKS'] !== 'false';
export const API_URL = import.meta.env['VITE_API_URL'] || 'http://localhost:8000';
let accessToken: string | null = null;
export const setAccessToken = (token: string | null) => { accessToken = token; };
export async function http<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
 const response = await fetch(`${API_URL}${path}`, {method, credentials:'include', headers: {'Content-Type':'application/json', ...(accessToken ? {Authorization:`Bearer ${accessToken}`} : {})}, ...(body === undefined ? {} : {body:JSON.stringify(body)})});
 if (!response.ok) throw new Error(response.status === 401 ? 'La sesión ha expirado. Vuelve a iniciar sesión.' : response.status === 403 ? 'No tienes permiso para realizar esta acción.' : 'No pudimos completar la solicitud. Inténtalo nuevamente.');
 if (response.status === 204) return undefined as T;
 return response.json() as Promise<T>;
}
