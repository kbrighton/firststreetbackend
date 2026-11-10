import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { NavBar } from './NavBar';

describe('NavBar', () => {
  it('always shows Home and highlights the current route', () => {
    render(
      <MemoryRouter
        initialEntries={['/']}
      >
        <NavBar />
      </MemoryRouter>,
    );

    expect(screen.getByRole('link', { name: 'Home' })).toHaveAttribute('aria-current', 'page');
    expect(screen.queryByRole('link', { name: 'Search Form' })).not.toBeInTheDocument();
  });

  it('shows role-appropriate account navigation for an authenticated user', () => {
    render(
      <MemoryRouter
        initialEntries={['/search']}
      >
        <NavBar user={{ username: 'admin', role: 'admin' }} onLogout={() => undefined} />
      </MemoryRouter>,
    );

    expect(screen.getByRole('link', { name: 'Search Form' })).toHaveAttribute('aria-current', 'page');
    expect(screen.getByRole('link', { name: 'User Management' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Logout' })).toHaveClass('nav-link');
    expect(screen.queryByRole('button', { name: 'Logout' })).not.toBeInTheDocument();
  });

  it('shows the profile link to a regular user', () => {
    render(
      <MemoryRouter>
        <NavBar user={{ username: 'staff', role: 'user' }} />
      </MemoryRouter>,
    );

    expect(screen.getByRole('link', { name: 'Manage My Profile' })).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: 'User Management' })).not.toBeInTheDocument();
  });
});
