export type ApiErrorFields = Record<string, string[]>;

type ErrorEnvelope = {
  error?: unknown;
  message?: unknown;
  fields?: unknown;
};

type ApiRequestInit = RequestInit & {
  json?: unknown;
};

export class ApiError extends Error {
  readonly status: number;
  readonly error: string;
  readonly fields?: ApiErrorFields;

  constructor(status: number, error: string, message: string, fields?: ApiErrorFields) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.error = error;
    this.fields = fields;
  }
}

let csrfToken: string | null = null;
let csrfTokenRequest: Promise<string> | null = null;
let unauthorizedHandler: (() => void) | null = null;

export function resetCsrfToken(): void {
  csrfToken = null;
  csrfTokenRequest = null;
}

export async function refreshCsrfToken(): Promise<string> {
  resetCsrfToken();
  return getCsrfToken();
}

export function setUnauthorizedHandler(handler: (() => void) | null): void {
  unauthorizedHandler = handler;
}

async function getCsrfToken(): Promise<string> {
  if (csrfToken) {
    return csrfToken;
  }
  if (csrfTokenRequest) {
    return csrfTokenRequest;
  }

  const request = (async () => {
    const response = await fetch('/api/auth/csrf', {
      credentials: 'same-origin',
      headers: { Accept: 'application/json' },
    });
    if (!response.ok) {
      throw await responseError(response);
    }

    const body: unknown = await response.json();
    if (!isRecord(body) || typeof body.csrf_token !== 'string' || body.csrf_token.length === 0) {
      throw new ApiError(response.status, 'Invalid Response', 'The server did not return a CSRF token');
    }
    csrfToken = body.csrf_token;
    return csrfToken;
  })();

  csrfTokenRequest = request;
  try {
    return await request;
  } finally {
    if (csrfTokenRequest === request) {
      csrfTokenRequest = null;
    }
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function parseFields(value: unknown): ApiErrorFields | undefined {
  if (!isRecord(value)) {
    return undefined;
  }

  const fields: ApiErrorFields = {};
  for (const [name, messages] of Object.entries(value)) {
    if (typeof messages === 'string') {
      fields[name] = [messages];
    } else if (Array.isArray(messages)) {
      fields[name] = messages.filter((message): message is string => typeof message === 'string');
    }
  }
  return Object.keys(fields).length > 0 ? fields : undefined;
}

async function responseError(response: Response): Promise<ApiError> {
  let body: ErrorEnvelope = {};
  try {
    const parsed: unknown = await response.json();
    if (isRecord(parsed)) {
      body = parsed;
    }
  } catch {
    // Keep the HTTP status and status text when the server does not send JSON.
  }

  const error = typeof body.error === 'string' ? body.error : 'Request Error';
  const message = typeof body.message === 'string'
    ? body.message
    : response.statusText || 'The request could not be completed';
  return new ApiError(response.status, error, message, parseFields(body.fields));
}

function isWriteMethod(method: string): boolean {
  return ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method);
}

function shouldRedirectOnUnauthorized(path: string): boolean {
  const pathname = path.split('?')[0];
  return !pathname.endsWith('/auth/me') && !pathname.endsWith('/auth/login');
}

export function apiFetch<T>(path: string, init: ApiRequestInit = {}): Promise<T> {
  return request<T>(path, init, true);
}

async function request<T>(path: string, init: ApiRequestInit, retryCsrf: boolean): Promise<T> {
  const { json, ...requestInit } = init;
  const method = (requestInit.method || (json === undefined ? 'GET' : 'POST')).toUpperCase();
  const write = isWriteMethod(method);
  const headers = new Headers(requestInit.headers);
  headers.set('Accept', 'application/json');

  let body = requestInit.body;
  if (json !== undefined) {
    headers.set('Content-Type', 'application/json');
    body = JSON.stringify(json);
  }
  if (write) {
    headers.set('X-CSRFToken', await getCsrfToken());
  }

  const response = await fetch(path, {
    ...requestInit,
    method,
    headers,
    body,
    credentials: 'same-origin',
  });

  if (!response.ok) {
    const error = await responseError(response);
    if (write && retryCsrf && response.status === 400 && error.error === 'CSRF Error') {
      await refreshCsrfToken();
      return request<T>(path, init, false);
    }
    if (response.status === 401 && shouldRedirectOnUnauthorized(path)) {
      unauthorizedHandler?.();
    }
    throw error;
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const text = await response.text();
  if (!text) {
    return undefined as T;
  }
  try {
    return JSON.parse(text) as T;
  } catch {
    return text as T;
  }
}
