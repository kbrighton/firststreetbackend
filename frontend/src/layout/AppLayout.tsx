import { Outlet, useNavigate } from 'react-router-dom';
import { AlertsList } from '../alerts/AlertsList';
import { AlertsProvider } from '../alerts/AlertsProvider';
import { useAlerts } from '../alerts/useAlerts';
import { useAuth } from '../auth/useAuth';
import { Footer } from './Footer';
import { NavBar } from './NavBar';

export function AppLayout() {
  return (
    <AlertsProvider>
      <AppLayoutContent />
    </AlertsProvider>
  );
}

function AppLayoutContent() {
  const { user, logout } = useAuth();
  const { addAlert } = useAlerts();
  const navigate = useNavigate();

  const handleLogout = async () => {
    // Leave the current page before clearing the user, so route guards don't add a stale `next`.
    navigate('/login', { replace: true });
    try {
      await logout();
    } catch {
      addAlert('The server could not confirm logout.', 'danger');
    } finally {
      addAlert('You have been logged out', 'success');
    }
  };

  return (
    <>
      <NavBar user={user} onLogout={user ? handleLogout : undefined} />
      <main className="container-fluid">
        <AlertsList />
        <Outlet />
      </main>
      <Footer />
    </>
  );
}
