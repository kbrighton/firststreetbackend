import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { ApiError, apiFetch, resetCsrfToken, setUnauthorizedHandler } from './client';

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

describe('apiFetch', () => {
  let fetchMock: ReturnType<typeof vi.fn<typeof fetch>>;

  beforeEach(() => {
    resetCsrfToken();
    setUnauthorizedHandler(null);
    fetchMock = vi.fn<typeof fetch>();
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('uses same-origin credentials and does not request a CSRF token for reads', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse({ value: 1 }));

    await expect(apiFetch<{ value: number }>('/api/example')).resolves.toEqual({ value: 1 });
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0][1]?.credentials).toBe('same-origin');
    expect(new Headers(fetchMock.mock.calls[0][1]?.headers).has('X-CSRFToken')).toBe(false);
  });

  it('adds a cached CSRF token to write requests with JSON bodies', async () => {
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ csrf_token: 'token-one' }))
      .mockResolvedValueOnce(jsonResponse({ saved: true }));

    await apiFetch('/api/example', { method: 'POST', json: { name: 'order' } });

    const [url, init] = fetchMock.mock.calls[1];
    expect(url).toBe('/api/example');
    expect(new Headers(init?.headers).get('X-CSRFToken')).toBe('token-one');
    expect(new Headers(init?.headers).get('Content-Type')).toBe('application/json');
    expect(init?.body).toBe(JSON.stringify({ name: 'order' }));
    expect(init?.credentials).toBe('same-origin');
  });

  it('converts the JSON error envelope and field messages to ApiError', async () => {
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ csrf_token: 'token-one' }))
      .mockResolvedValueOnce(jsonResponse({
        error: 'Validation Error',
        message: 'Please correct the form',
        status: 400,
        fields: { username: ['Username is required'] },
      }, 400));

    await expect(apiFetch('/api/auth/login', { method: 'POST', json: {} })).rejects.toMatchObject({
      name: 'ApiError',
      status: 400,
      error: 'Validation Error',
      message: 'Please correct the form',
      fields: { username: ['Username is required'] },
    });
  });

  it('fetches a fresh token and retries once after a CSRF error', async () => {
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ csrf_token: 'expired-token' }))
      .mockResolvedValueOnce(jsonResponse({ error: 'CSRF Error', message: 'Expired', status: 400 }, 400))
      .mockResolvedValueOnce(jsonResponse({ csrf_token: 'fresh-token' }))
      .mockResolvedValueOnce(jsonResponse({ saved: true }));

    await expect(apiFetch('/api/example', { method: 'PUT', json: { id: 2 } })).resolves.toEqual({ saved: true });

    expect(fetchMock).toHaveBeenCalledTimes(4);
    expect(new Headers(fetchMock.mock.calls[1][1]?.headers).get('X-CSRFToken')).toBe('expired-token');
    expect(new Headers(fetchMock.mock.calls[3][1]?.headers).get('X-CSRFToken')).toBe('fresh-token');
  });

  it('does not retry a second CSRF failure', async () => {
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ csrf_token: 'expired-token' }))
      .mockResolvedValueOnce(jsonResponse({ error: 'CSRF Error', message: 'Expired', status: 400 }, 400))
      .mockResolvedValueOnce(jsonResponse({ csrf_token: 'fresh-token' }))
      .mockResolvedValueOnce(jsonResponse({ error: 'CSRF Error', message: 'Still expired', status: 400 }, 400));

    await expect(apiFetch('/api/example', { method: 'DELETE' })).rejects.toBeInstanceOf(ApiError);
    expect(fetchMock).toHaveBeenCalledTimes(4);
  });

  it('calls the unauthorized handler for protected API requests', async () => {
    const onUnauthorized = vi.fn();
    setUnauthorizedHandler(onUnauthorized);
    fetchMock.mockResolvedValueOnce(jsonResponse({ error: 'Unauthorized', message: 'Login required', status: 401 }, 401));

    await expect(apiFetch('/api/orders')).rejects.toMatchObject({ status: 401 });
    expect(onUnauthorized).toHaveBeenCalledOnce();
  });
});
