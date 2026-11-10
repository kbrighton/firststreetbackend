import { useQuery } from '@tanstack/react-query';
import { getUser, getUsers } from '../api/users';

export const userKeys = {
  all: ['users'] as const,
  list: () => ['users', 'list'] as const,
  detail: (id: number) => ['users', 'detail', id] as const,
};

export function useUsers(enabled = true) {
  return useQuery({
    queryKey: userKeys.list(),
    queryFn: getUsers,
    enabled,
  });
}

export function useUser(id: number, enabled = true) {
  return useQuery({
    queryKey: userKeys.detail(id),
    queryFn: () => getUser(id),
    enabled,
  });
}
