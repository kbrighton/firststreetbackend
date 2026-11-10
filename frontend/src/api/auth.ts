import { ApiError, apiFetch, refreshCsrfToken, resetCsrfToken } from './client';
import type { components } from './schema';

type CurrentUserFields = components['schemas']['CurrentUser']['user'];
export type CurrentUser = Required<Pick<CurrentUserFields, 'id' | 'username' | 'email' | 'role'>>
  & Pick<CurrentUserFields, 'created_at'>;

type CurrentUserResponse = {
  user: CurrentUser;
};

type LoginResponse = {
  message: string;
  user: CurrentUser;
};

export async function getMe(): Promise<CurrentUser | null> {
  try {
    const response = await apiFetch<CurrentUserResponse>('/api/auth/me');
    return response.user;
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      return null;
    }
    throw error;
  }
}

export async function login(body: {
  username: string;
  password: string;
  remember: boolean;
}): Promise<CurrentUser> {
  const response = await apiFetch<LoginResponse>('/api/auth/login', {
    method: 'POST',
    json: body,
  });
  await refreshCsrfToken();
  return response.user;
}

export async function logout(): Promise<void> {
  try {
    await apiFetch<void>('/api/auth/logout', { method: 'POST' });
  } catch (error) {
    if (!(error instanceof ApiError && error.status === 401)) {
      throw error;
    }
  } finally {
    resetCsrfToken();
  }
  await refreshCsrfToken();
}
