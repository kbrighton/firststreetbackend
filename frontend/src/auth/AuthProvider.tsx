import { useCallback, useEffect, useMemo, type ReactNode } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useLocation, useNavigate } from 'react-router-dom';
import { getMe, login as loginRequest, logout as logoutRequest } from '../api/auth';
import { setUnauthorizedHandler } from '../api/client';
import { AuthContext, type AuthContextValue, type LoginCredentials } from './AuthContext';

const authQueryKey = ['auth', 'me'] as const;

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const location = useLocation();
  const navigate = useNavigate();
  const { data: user = null, isPending } = useQuery({
    queryKey: authQueryKey,
    queryFn: getMe,
    retry: false,
    staleTime: 60_000,
  });

  useEffect(() => {
    setUnauthorizedHandler(() => {
      queryClient.removeQueries({ predicate: (query) => query.queryKey[0] !== 'auth' });
      queryClient.setQueryData(authQueryKey, null);
      if (location.pathname !== '/login') {
        const next = `${location.pathname}${location.search}${location.hash}`;
        navigate(`/login?${new URLSearchParams({ next })}`, { replace: true });
      }
    });
    return () => setUnauthorizedHandler(null);
  }, [location.hash, location.pathname, location.search, navigate, queryClient]);

  const login = useCallback(async (credentials: LoginCredentials) => {
    const authenticatedUser = await loginRequest(credentials);
    queryClient.setQueryData(authQueryKey, authenticatedUser);
    return authenticatedUser;
  }, [queryClient]);

  const logout = useCallback(async () => {
    try {
      await logoutRequest();
    } finally {
      queryClient.removeQueries({ predicate: (query) => query.queryKey[0] !== 'auth' });
      queryClient.setQueryData(authQueryKey, null);
    }
  }, [queryClient]);

  const value = useMemo<AuthContextValue>(() => ({
    user,
    isLoading: isPending,
    isAdmin: user?.role === 'admin',
    login,
    logout,
  }), [isPending, login, logout, user]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
