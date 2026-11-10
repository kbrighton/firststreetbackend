import { beforeEach, describe, expect, it, vi } from 'vitest';
import { apiFetch } from './client';
import { createUser, getUser, getUsers, updateUser } from './users';

vi.mock('./client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('./client')>();
  return { ...actual, apiFetch: vi.fn() };
});

const fetchMock = vi.mocked(apiFetch);

beforeEach(() => fetchMock.mockReset());

describe('users API', () => {
  it('loads the user list and a user by ID', async () => {
    fetchMock.mockResolvedValue([] as never);

    await getUsers();
    await getUser(9);

    expect(fetchMock).toHaveBeenNthCalledWith(1, '/api/users');
    expect(fetchMock).toHaveBeenNthCalledWith(2, '/api/users/9');
  });

  it('uses the existing create and update endpoints', async () => {
    fetchMock.mockResolvedValue({} as never);
    const createPayload = {
      username: 'newuser',
      email: 'new@example.com',
      password: 'newpass123',
      role: 'user' as const,
    };

    await createUser(createPayload);
    await updateUser(9, { username: 'updateduser', password: 'updatedpass123' });

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      '/api/users',
      { method: 'POST', json: createPayload },
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      '/api/users/9',
      { method: 'PUT', json: { username: 'updateduser', password: 'updatedpass123' } },
    );
  });
});
