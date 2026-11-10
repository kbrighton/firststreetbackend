import { useState, type ReactNode } from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import type { CurrentUser } from '../api/auth';
import { AuthContext } from '../auth/AuthContext';
import { RequireAuth } from '../auth/RequireAuth';
import { AppLayout } from './AppLayout';
import { HomePage } from '../pages/HomePage';

function StatefulAuth({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>({
    id: 1, username: 'staff', email: 'staff@example.com', role: 'user',
  });
  return (
    <AuthContext.Provider value={{
      user,
      isLoading: false,
      isAdmin: false,
      login: async () => { throw new Error('Not used in this test'); },
      logout: async () => {
        await Promise.resolve();
        setUser(null);
      },
    }}>
      {children}
    </AuthContext.Provider>
  );
}

function LocationProbe() {
  const location = useLocation();
  return <p data-testid="location">{`${location.pathname}${location.search}`}</p>;
}

describe('AppLayout', () => {
  it('logs out from a protected page to a clean login URL', async () => {
    render(
      <MemoryRouter initialEntries={['/users']}>
        <StatefulAuth>
          <Routes>
            <Route element={<AppLayout />}>
              <Route path="/login" element={<LocationProbe />} />
              <Route element={<RequireAuth />}>
                <Route path="/users" element={<p>Users page</p>} />
              </Route>
            </Route>
          </Routes>
        </StatefulAuth>
      </MemoryRouter>,
    );

    const logoutLink = screen.getByRole('link', { name: 'Logout' });
    expect(logoutLink).toHaveAttribute('href', '/login');
    expect(logoutLink).not.toHaveClass('btn');
    fireEvent.click(logoutLink);

    expect(await screen.findByText('You have been logged out')).toBeInTheDocument();
    expect(screen.getByTestId('location')).toHaveTextContent(/^\/login$/);
    expect(screen.queryByRole('link', { name: 'Logout' })).not.toBeInTheDocument();
  });
  it('renders the home content, navigation and footer in the shared shell', () => {
    render(
      <MemoryRouter
        initialEntries={['/']}
      >
        <AuthContext.Provider value={{
          user: null,
          isLoading: false,
          isAdmin: false,
          login: async () => { throw new Error('Not used in this test'); },
          logout: async () => undefined,
        }}>
          <Routes>
            <Route element={<AppLayout />}>
              <Route index element={<HomePage />} />
            </Route>
          </Routes>
        </AuthContext.Provider>
      </MemoryRouter>,
    );

    expect(screen.getByRole('heading', { name: '1st Street Graphics Order Intake System' })).toBeInTheDocument();
    expect(screen.getByText("It's MENU for 2024!")).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Home' })).toHaveAttribute('aria-current', 'page');
    expect(screen.getByRole('contentinfo')).toHaveTextContent('Nick Burtner');
    expect(document.querySelector('main.container-fluid')).toBeInTheDocument();
    expect(document.querySelector('main')).not.toContainElement(screen.getByRole('navigation'));
    expect(document.querySelector('main')).not.toContainElement(screen.getByRole('contentinfo'));
  });
});
