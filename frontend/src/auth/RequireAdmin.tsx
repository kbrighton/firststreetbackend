import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { SessionSpinner } from './SessionSpinner';
import { useAuth } from './useAuth';

export function RequireAdmin() {
  const { user, isAdmin, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <SessionSpinner />;
  }
  if (!user) {
    const next = `${location.pathname}${location.search}${location.hash}`;
    return <Navigate to={`/login?${new URLSearchParams({ next })}`} replace />;
  }
  if (!isAdmin) {
    return <Navigate to="/" replace />;
  }
  return <Outlet />;
}
