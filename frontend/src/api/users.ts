import { apiFetch } from './client';
import type { components } from './schema';

export type User = components['schemas']['User'];
export type UserInput = components['schemas']['UserInput'];

export function getUsers(): Promise<User[]> {
  return apiFetch<User[]>('/api/users');
}

export function getUser(id: number): Promise<User> {
  return apiFetch<User>(`/api/users/${id}`);
}

export function createUser(user: UserInput): Promise<User> {
  return apiFetch<User>('/api/users', { method: 'POST', json: user });
}

export function updateUser(id: number, user: Partial<UserInput>): Promise<User> {
  return apiFetch<User>(`/api/users/${id}`, { method: 'PUT', json: user });
}
