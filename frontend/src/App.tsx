import { AppRoutes } from './routes';
import { useAuth } from './auth/useAuth';
import { SessionSpinner } from './auth/SessionSpinner';

export function App() {
  const { isLoading } = useAuth();
  if (isLoading) {
    return <SessionSpinner />;
  }
  return <AppRoutes />;
}
