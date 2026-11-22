# Cola Urgencias APS

Frontend de demostración para llegada, triage presencial, cola clínica y trazabilidad en atención primaria. No contiene servicios de base de datos, autenticación externa ni datos clínicos reales.

## Desarrollo y exportación

React 19, TypeScript, Vite, TanStack Router/Start, TanStack Query, React Hook Form, Zod, cliente HTTP Fetch centralizado y Tailwind CSS. Se conserva TanStack Router en lugar de React Router para respetar la arquitectura obligatoria de la plataforma. El repositorio puede conectarse a GitHub y ejecutarse localmente.

```sh
bun install
cp .env.example .env
bun run dev
bun run test
```

Para generar la aplicación fuera de Lovable: `bun run build`. El despliegue conserva el soporte TanStack Start del proyecto; no es un paquete SPA con React Router.

## Modo demostración

`VITE_USE_MOCKS=true` (valor predeterminado). Los datos ficticios se encuentran en `src/mocks`; solo los servicios de `src/api` acceden a ellos. Las cuentas y la contraseña se presentan únicamente en la pantalla de acceso. Las cuentas contienen correo y rol, sin avatar ni preferencias.

Las modificaciones simuladas duran mientras la aplicación permanezca abierta. Recargar la página restaura la muestra inicial; solo se conserva el correo de la sesión demo en sessionStorage. No usar datos reales ni considerar la sesión demo un mecanismo de seguridad real.

## Conexión posterior a FastAPI

Configurar `VITE_USE_MOCKS=false` y `VITE_API_URL=https://tu-servidor` y reiniciar/recompilar. Los componentes permanecen sin cambios.

El cliente usa JSON y espera `{ "data": ... }` con nombres camelCase conforme a `src/types/index.ts`. Los listados actualmente esperan un arreglo dentro de `data`; si FastAPI pagina o utiliza snake_case, adaptar la normalización en `src/api`, no en las vistas. Los errores se presentan de forma genérica. Los endpoints sin contenido pueden responder 204.

Los servicios representan todos los endpoints solicitados: autenticación (`login`, `refresh`, `me`, `logout`), registro y consulta pública, episodios (listado, detalle, pendientes, triage, reevaluación, llamado, inicio y cierre), cola y posición, alertas (listado, toma y resolución), indicadores, auditoría y usuarios (listado, creación y estado).

`login` y `refresh` retornan `{data:{user,accessToken,refreshToken}}`. El access token vive en memoria y se envía como Bearer. Para restaurar una sesión, FastAPI debe usar una cookie HttpOnly de renovación en `refresh`; Fetch usa `credentials: include`. Configurar CORS con el origen concreto del frontend, autorización por roles y cookies seguras. No almacenar secretos ni tokens en archivos del frontend.

La configuración de umbrales es solo demostrativa: no existe un endpoint de configuración en el contrato solicitado. Para habilitarla fuera del demo se necesita añadir ese endpoint en FastAPI.

## Seguridad y reglas

- FastAPI debe validar todas las autorizaciones, transiciones y entradas de manera independiente: ocultar un botón no protege una API.
- Solo TRIAGE y CLINICAL_MANAGER asignan o cambian prioridad; cambiarla requiere motivo y conserva la evaluación anterior.
- La cola ordena por prioridad C1–C5 y antigüedad del triage, nunca únicamente por llegada.
- La respuesta pública contiene solo ticket, estado, horas, box y estimaciones; nunca pacientes, documentos, observaciones clínicas ni prioridades ajenas.
- El ticket es aleatorio. En producción, preferir el token de alta entropía y proteger consultas por ticket contra enumeración y abuso.
- Las estimaciones y métricas son simuladas y orientativas; no son recomendaciones clínicas ni garantías de atención.

## Organización

`src/api`: contratos y servicios; `src/mocks`: datos y adaptador; `src/types` y `src/schemas`: tipos y validación; `src/features`: pantallas por dominio; `src/layouts`: portal y área interna; `src/routes`: navegación y metadatos; `src/utils`: reglas y formatos; `src/test`: pruebas de navegación y reglas.
