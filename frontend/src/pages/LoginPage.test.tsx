import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { resetCsrfToken, setUnauthorizedHandler } from '../api/client';
import { renderApp } from '../test/renderApp';

const staffUser = {
  id: 8,
  username: 'staff',
  email: 'staff@example.com',
  role: 'user' as const,
};

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

function mockFetch(...responses: Response[]) {
  const fetchMock = vi.fn<typeof fetch>();
  for (const response of responses) {
    fetchMock.mockResolvedValueOnce(response);
  }
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

describe('login and protected routes', () => {
  beforeEach(() => {
    resetCsrfToken();
    setUnauthorizedHandler(null);
  });

  it('redirects an unauthenticated protected route to login with a safe next path', async () => {
    mockFetch(jsonResponse({ error: 'Unauthorized', message: 'Login required', status: 401 }, 401));

    renderApp('/search?cust=12345');

    expect(await screen.findByRole('heading', { name: 'Login Page' })).toBeInTheDocument();
    expect(screen.getByTestId('current-location')).toHaveTextContent('/login?next=%2Fsearch%3Fcust%3D12345');
  });

  it('blocks a regular user from the admin-only new-user route', async () => {
    mockFetch(jsonResponse({ user: staffUser }));

    renderApp('/user/new');

    expect(await screen.findByRole('heading', { name: '1st Street Graphics Order Intake System' })).toBeInTheDocument();
    expect(screen.getByTestId('current-location')).toHaveTextContent('/');
  });

  it('validates login fields and lowercases a valid username before posting', async () => {
    const fetchMock = mockFetch(jsonResponse({ error: 'Unauthorized', message: 'Login required', status: 401 }, 401));
    const user = userEvent.setup();

    renderApp('/login');
    await screen.findByRole('heading', { name: 'Login Page' });
    await user.type(screen.getByLabelText('Username'), 'a!');
    await user.type(screen.getByLabelText('Password'), 'short');
    await user.click(screen.getByRole('button', { name: 'Sign In' }));

    expect(await screen.findByText('Username must be between 3 and 64 characters')).toBeInTheDocument();
    expect(screen.getByText('Password must be at least 8 characters')).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('shows invalid credentials in a dismissible danger alert without redirecting', async () => {
    const fetchMock = mockFetch(
      jsonResponse({ error: 'Unauthorized', message: 'Login required', status: 401 }, 401),
      jsonResponse({ csrf_token: 'csrf-before-login' }),
      jsonResponse({ error: 'Unauthorized', message: 'Invalid username or password', status: 401 }, 401),
    );
    const user = userEvent.setup();

    renderApp('/login');
    await screen.findByRole('heading', { name: 'Login Page' });
    await user.type(screen.getByLabelText('Username'), 'staff');
    await user.type(screen.getByLabelText('Password'), 'password123');
    await user.click(screen.getByRole('button', { name: 'Sign In' }));

    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('Invalid username or password');
    expect(alert).toHaveClass('alert-danger');
    expect(screen.getByTestId('current-location')).toHaveTextContent('/login');
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });

  it('shows server field errors under the matching login inputs', async () => {
    mockFetch(
      jsonResponse({ error: 'Unauthorized', message: 'Login required', status: 401 }, 401),
      jsonResponse({ csrf_token: 'csrf-before-login' }),
      jsonResponse({
        error: 'Validation Error',
        message: 'Please correct the form',
        status: 400,
        fields: { username: ['Username is not recognized'] },
      }, 400),
    );
    const user = userEvent.setup();

    renderApp('/login');
    await screen.findByRole('heading', { name: 'Login Page' });
    await user.type(screen.getByLabelText('Username'), 'staff');
    await user.type(screen.getByLabelText('Password'), 'password123');
    await user.click(screen.getByRole('button', { name: 'Sign In' }));

    expect(await screen.findByText('Username is not recognized')).toBeInTheDocument();
    expect(screen.getByTestId('current-location')).toHaveTextContent('/login');
  });

  it('returns to the requested internal route after login and ignores external next values', async () => {
    const fetchMock = mockFetch(
      jsonResponse({ error: 'Unauthorized', message: 'Login required', status: 401 }, 401),
      jsonResponse({ csrf_token: 'csrf-before-login' }),
      jsonResponse({ message: 'Login successful', user: staffUser }),
      jsonResponse({ csrf_token: 'csrf-after-login' }),
    );
    const user = userEvent.setup();
    const { queryClient } = renderApp('/login?next=%2F%2Fevil.example');

    await screen.findByRole('heading', { name: 'Login Page' });
    await user.type(screen.getByLabelText('Username'), 'STAFF');
    await user.type(screen.getByLabelText('Password'), 'password123');
    await user.click(screen.getByRole('button', { name: 'Sign In' }));

    expect(await screen.findByRole('heading', { name: '1st Street Graphics Order Intake System' })).toBeInTheDocument();
    expect(screen.getByTestId('current-location')).toHaveTextContent('/');
    expect(queryClient.getQueryData(['auth', 'me'])).toEqual(staffUser);
    const loginCall = fetchMock.mock.calls.find(([url]) => url === '/api/auth/login');
    expect(JSON.parse(String(loginCall?.[1]?.body))).toEqual({
      username: 'staff',
      password: 'password123',
      remember: false,
    });
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(4));
  });

  it('logs out, clears cached data and shows the confirmation message', async () => {
    const fetchMock = mockFetch(
      jsonResponse({ user: staffUser }),
      jsonResponse({ csrf_token: 'csrf-before-logout' }),
      jsonResponse({ message: 'Logged out' }),
      jsonResponse({ csrf_token: 'csrf-after-logout' }),
    );
    const user = userEvent.setup();
    const { queryClient } = renderApp('/search');
    queryClient.setQueryData(['orders'], [{ id: 12 }]);

    await user.click(await screen.findByRole('link', { name: 'Logout' }));

    expect(await screen.findByRole('heading', { name: 'Login Page' })).toBeInTheDocument();
    expect(await screen.findByRole('alert')).toHaveTextContent('You have been logged out');
    expect(screen.getByTestId('current-location')).toHaveTextContent('/login');
    expect(queryClient.getQueryData(['auth', 'me'])).toBeNull();
    expect(queryClient.getQueryData(['orders'])).toBeUndefined();
    expect(fetchMock).toHaveBeenCalledTimes(4);
  });
});
