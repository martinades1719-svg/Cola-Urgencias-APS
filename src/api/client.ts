export const USE_MOCKS =
  import.meta.env['VITE_USE_MOCKS'] !== 'false';

export const API_URL =
  import.meta.env['VITE_API_URL'] || 'http://localhost:8000';

const ACCESS_TOKEN_KEY = 'aps-access-token';

let accessToken: string | null =
  typeof window !== 'undefined'
    ? sessionStorage.getItem(ACCESS_TOKEN_KEY)
    : null;

export const setAccessToken = (
  token: string | null,
): void => {
  accessToken = token;

  if (typeof window === 'undefined') {
    return;
  }

  if (token) {
    sessionStorage.setItem(ACCESS_TOKEN_KEY, token);
  } else {
    sessionStorage.removeItem(ACCESS_TOKEN_KEY);
  }
};

export const getAccessToken = (): string | null => {
  return accessToken;
};

export async function http<T>(
  path: string,
  method = 'GET',
  body?: unknown,
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(accessToken
        ? {
            Authorization: `Bearer ${accessToken}`,
          }
        : {}),
    },
    ...(body === undefined
      ? {}
      : {
          body: JSON.stringify(body),
        }),
  });

  if (!response.ok) {
    let message = 'No pudimos completar la solicitud. Inténtalo nuevamente.';

    try {
      const errorBody = (await response.json()) as {
        detail?: string;
      };

      if (errorBody.detail) {
        message = errorBody.detail;
      }
    } catch {
      if (response.status === 401) {
        message = 'La sesión ha expirado. Vuelve a iniciar sesión.';
      } else if (response.status === 403) {
        message = 'No tienes permiso para realizar esta acción.';
      }
    }

    if (response.status === 401) {
      setAccessToken(null);
    }

    throw new Error(message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}