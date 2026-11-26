import {
  getAccessToken,
  http,
  setAccessToken,
  USE_MOCKS,
} from './client';

import { mockApi } from '@/mocks/adapter';

import type {
  Alert,
  ApiResponse,
  ArrivalInput,
  AssessmentInput,
  AuditLog,
  AuthSession,
  DashboardMetrics,
  Episode,
  PublicStatus,
  QueueItem,
  QueuePosition,
  Role,
  User,
} from '@/types';


interface BackendRoleResponse {
  id: number;
  name: Role;
}


interface BackendUserResponse {
  id: string;
  name: string;
  email: string;
  role: BackendRoleResponse;
  active: boolean;
}


interface BackendTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: BackendUserResponse;
}


const get = async <T,>(
  path: string,
): Promise<T> => {
  const response =
    await http<ApiResponse<T>>(path);

  return response.data;
};


const post = async <T,>(
  path: string,
  input: unknown = {},
): Promise<T> => {
  const response =
    await http<ApiResponse<T>>(
      path,
      'POST',
      input,
    );

  return response.data;
};


function adaptBackendUser(
  backendUser: BackendUserResponse,
): User {
  return {
    id: backendUser.id,
    name: backendUser.name,
    email: backendUser.email,
    role: backendUser.role.name,
    active: backendUser.active,
  };
}


async function loginWithFastApi(
  email: string,
  password: string,
): Promise<AuthSession> {
  const response =
    await http<BackendTokenResponse>(
      '/api/auth/login',
      'POST',
      {
        email,
        password,
      },
    );

  const session: AuthSession = {
    user: adaptBackendUser(
      response.user,
    ),
    accessToken:
      response.access_token,
  };

  setAccessToken(
    session.accessToken,
  );

  /*
   * La autenticación es real mediante FastAPI,
   * JWT y PostgreSQL. Esta sincronización permite
   * utilizar temporalmente el dashboard, cola y
   * alertas simuladas hasta implementar sus endpoints.
   */
  await mockApi.setAuthenticatedUser(
    session.user,
  );

  return session;
}


async function getCurrentUserFromFastApi(): Promise<User> {
  const response =
    await http<BackendUserResponse>(
      '/api/auth/me',
    );

  const user =
    adaptBackendUser(response);

  /*
   * Al actualizar el navegador, restaura también
   * la sesión de los módulos demostrativos.
   */
  await mockApi.setAuthenticatedUser(
    user,
  );

  return user;
}


export const authService = {
  login: async (
    email: string,
    password: string,
  ): Promise<AuthSession> => {
    return loginWithFastApi(
      email,
      password,
    );
  },


  me: async (): Promise<User> => {
    return getCurrentUserFromFastApi();
  },


  refresh: async (): Promise<AuthSession | null> => {
    /*
     * Aún no se implementa refresh token.
     * Se valida el access token existente mediante /me.
     */
    const token = getAccessToken();

    if (!token) {
      return null;
    }

    try {
      const user =
        await getCurrentUserFromFastApi();

      return {
        user,
        accessToken: token,
      };
    } catch {
      await mockApi.logout();
      setAccessToken(null);
      return null;
    }
  },


  restore: async (): Promise<AuthSession | null> => {
    const token = getAccessToken();

    if (!token) {
      return null;
    }

    try {
      const user =
        await getCurrentUserFromFastApi();

      return {
        user,
        accessToken: token,
      };
    } catch {
      await mockApi.logout();
      setAccessToken(null);
      return null;
    }
  },


  logout: async (): Promise<void> => {
    /*
     * Actualmente el JWT es stateless.
     * El cierre elimina el token del navegador
     * y también limpia la sesión híbrida.
     */
    await mockApi.logout();
    setAccessToken(null);

    sessionStorage.removeItem(
      'aps-demo-email',
    );
  },
};


export const publicService = {
  /*
   * Registro y consulta pública utilizan siempre FastAPI.
   * Los módulos internos continúan con mocks temporalmente.
   */
  arrival: (
    input: ArrivalInput,
  ): Promise<{
    ticket: string;
    token: string;
    arrivedAt: string;
  }> =>
    post<{
      ticket: string;
      token: string;
      arrivedAt: string;
    }>(
      '/api/public/arrival',
      input,
    ),

  status: (
    token: string,
  ): Promise<PublicStatus> =>
    get<PublicStatus>(
      `/api/public/status/${encodeURIComponent(
        token.trim(),
      )}`,
    ),
};

export const episodeService = {
  list: () =>
    USE_MOCKS
      ? mockApi.episodes()
      : get<Episode[]>('/api/episodes'),

  detail: (
    id: string,
  ) =>
    USE_MOCKS
      ? mockApi.episode(id)
      : get<Episode>(
          `/api/episodes/${id}`,
        ),

  pending: (): Promise<Episode[]> =>
    get<Episode[]>(
      '/api/episodes/pending-triage',
    ),

  triage: (
    id: string,
    input: AssessmentInput,
  ): Promise<Episode> =>
    post<Episode>(
      `/api/episodes/${id}/triage`,
      input,
    ),

  reassess: (
    id: string,
    input: AssessmentInput,
  ) =>
    USE_MOCKS
      ? mockApi.reassess(id, input)
      : post<Episode>(
          `/api/episodes/${id}/reassessments`,
          input,
        ),

  call: (
    id: string,
    box: string,
  ): Promise<Episode> =>
    post<Episode>(
      `/api/episodes/${id}/call`,
      {
        box,
      },
    ),

  startCare: (
    id: string,
  ): Promise<Episode> =>
    post<Episode>(
      `/api/episodes/${id}/start-care`,
    ),

  close: (
    id: string,
    reason: string,
  ): Promise<Episode> =>
    post<Episode>(
      `/api/episodes/${id}/close`,
      {
        reason,
      },
    ),
};


export const queueService = {
  /*
   * La cola clínica y las posiciones utilizan
   * FastAPI y PostgreSQL de forma permanente.
   */
  list: (): Promise<QueueItem[]> =>
    get<QueueItem[]>(
      '/api/queue',
    ),

  position: (
    id: string,
  ): Promise<QueuePosition> =>
    get<QueuePosition>(
      `/api/queue/${id}/position`,
    ),
};


export const alertService = {
  list: (): Promise<Alert[]> =>
    get<Alert[]>('/api/alerts'),

  take: (
    id: string,
  ): Promise<Alert> =>
    post<Alert>(
      `/api/alerts/${id}/take`,
    ),

  resolve: (
    id: string,
  ): Promise<Alert> =>
    post<Alert>(
      `/api/alerts/${id}/resolve`,
    ),
};
export const reportService = {
  dashboard: (): Promise<DashboardMetrics> =>
    get<DashboardMetrics>(
      '/api/reports/dashboard',
    ),
};
export const auditService = {
 
  list: (): Promise<AuditLog[]> =>
    get<AuditLog[]>(
      '/api/audit-logs',
    ),
};

export const userService = {
  list: (): Promise<User[]> =>
    get<User[]>('/api/users'),

  create: (
    input: {
      name: string;
      email: string;
      role: Role;
      password: string;
    },
  ): Promise<User> =>
    post<User>(
      '/api/users',
      input,
    ),

  status: (
    id: string,
    active: boolean,
  ): Promise<User> =>
    http<ApiResponse<User>>(
      `/api/users/${id}/status`,
      'PATCH',
      {
        active,
      },
    ).then(
      (response) => response.data,
    ),
};


export const settingsService = {
  threshold: (
    value?: number,
  ) =>
    USE_MOCKS
      ? mockApi.threshold(value)
      : Promise.reject(
          new Error(
            'La configuración requiere un endpoint adicional en FastAPI.',
          ),
        ),
};


export {
  USE_MOCKS,
};

export * from './health';