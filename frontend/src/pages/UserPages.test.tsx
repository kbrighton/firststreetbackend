import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { resetCsrfToken, setUnauthorizedHandler } from '../api/client';
import { renderApp } from '../test/renderApp';

const adminUser = {
  id: 1,
  username: 'admin',
  email: 'admin@example.com',
  role: 'admin',
};
const staffUser = {
  id: 8,
  username: 'staff',
  email: 'staff@example.com',
  role: 'user',
  created_at: '2025-01-02T10:00:00',
};
const otherUser = {
  id: 9,
  username: 'other',
  email: 'other@example.com',
  role: 'user',
  created_at: '2025-01-02T10:00:00',
  updated_at: '2025-01-02T10:00:00',
};
const allUsers = [adminUser, staffUser, otherUser];

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

function mockApi({
  role = 'admin',
  createStatus = 201,
  updateStatus = 200,
}: { role?: string; createStatus?: number; updateStatus?: number } = {}) {
  const currentUser = role === 'admin' ? adminUser : staffUser;
  const fetchMock = vi.fn<typeof fetch>(async (input, init) => {
    const path = String(input);
    const method = (init?.method ?? 'GET').toUpperCase();
    if (path === '/api/auth/me') return jsonResponse({ user: currentUser });
    if (path === '/api/auth/csrf') return jsonResponse({ csrf_token: 'csrf-token' });
    if (path === '/api/users' && method === 'GET') return jsonResponse(allUsers);
    if (path === '/api/users/9' && method === 'GET') return jsonResponse(otherUser);
    if (path === '/api/users' && method === 'POST') {
      if (createStatus !== 201) {
        return jsonResponse({
          error: 'Validation Error',
          message: 'User data is invalid',
          status: createStatus,
          fields: { email: ['Invalid email format'] },
        }, createStatus);
      }
      return jsonResponse({ id: 10, username: 'newuser', email: 'new@example.com', role: 'admin' }, 201);
    }
    if (path.startsWith('/api/users/') && method === 'PUT') {
      if (updateStatus !== 200) {
        return jsonResponse({
          error: 'Validation Error',
          message: 'User data is invalid',
          status: updateStatus,
          fields: { password: ['Field must be at least 8 characters long.'] },
        }, updateStatus);
      }
      return jsonResponse({ ...staffUser, username: 'updatedstaff' });
    }
    return jsonResponse({ error: 'Not Found', message: 'Not found', status: 404 }, 404);
  });
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

beforeEach(() => {
  resetCsrfToken();
  setUnauthorizedHandler(null);
});

describe('Users page', () => {
  it('shows all users and a create link to admins', async () => {
    const fetchMock = mockApi();
    renderApp('/users');

    expect(await screen.findByRole('heading', { name: 'User Management' })).toBeInTheDocument();
    expect(await screen.findByText('other@example.com')).toBeInTheDocument();
    expect(screen.getAllByText('2025-01-02 10:00')).toHaveLength(2);
    expect(screen.getByRole('link', { name: 'Create New User' })).toHaveAttribute('href', '/user/new');
    expect(screen.getAllByRole('link', { name: 'Edit' }).some((link) => (
      link.getAttribute('href') === '/user/9/edit'
    ))).toBe(true);
    expect(fetchMock).toHaveBeenCalledWith('/api/users', expect.anything());
  });

  it('shows only the current user profile and never requests the admin-only list for regular users', async () => {
    const fetchMock = mockApi({ role: 'user' });
    renderApp('/users');

    expect(await screen.findByRole('heading', { name: 'Manage My Profile' })).toBeInTheDocument();
    expect(screen.getByText('staff@example.com')).toBeInTheDocument();
    expect(screen.getByText('2025-01-02 10:00')).toBeInTheDocument();
    expect(screen.queryByText('other@example.com')).not.toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Edit' })).toHaveAttribute('href', '/user/8/edit');
    expect(fetchMock.mock.calls.some(([input]) => String(input) === '/api/users')).toBe(false);
  });
});

describe('User form page', () => {
  it('validates required fields and creates users with the selected role', async () => {
    const user = userEvent.setup();
    const fetchMock = mockApi();
    renderApp('/user/new');

    await screen.findByRole('heading', { name: 'New User' });
    await user.click(screen.getByRole('button', { name: 'Submit' }));
    expect(await screen.findByText('Username is required')).toBeInTheDocument();
    expect(screen.getByText('Email is required')).toBeInTheDocument();
    expect(screen.getByText('This field is required.')).toBeInTheDocument();

    await user.type(screen.getByLabelText('Username'), 'newuser');
    await user.type(screen.getByLabelText('Email'), 'new@example.com');
    await user.type(screen.getByLabelText('Password'), 'newpass123');
    await user.selectOptions(screen.getByLabelText('Role'), 'admin');
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    const createCall = fetchMock.mock.calls.find(([input, init]) => (
      String(input) === '/api/users' && init?.method === 'POST'
    ));
    expect(JSON.parse(String(createCall?.[1]?.body))).toEqual({
      username: 'newuser',
      email: 'new@example.com',
      password: 'newpass123',
      role: 'admin',
    });
    expect(await screen.findByRole('heading', { name: 'User Management' })).toBeInTheDocument();
  });

  it('shows server field errors under the matching create input', async () => {
    const user = userEvent.setup();
    mockApi({ createStatus: 400 });
    renderApp('/user/new');

    await screen.findByRole('heading', { name: 'New User' });
    await user.type(screen.getByLabelText('Username'), 'newuser');
    await user.type(screen.getByLabelText('Email'), 'new@example.com');
    await user.type(screen.getByLabelText('Password'), 'newpass123');
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    expect(await screen.findByText('Invalid email format')).toBeInTheDocument();
  });

  it('lets admins edit another user, change its role, and update the password', async () => {
    const user = userEvent.setup();
    const fetchMock = mockApi();
    renderApp('/user/9/edit');

    await screen.findByDisplayValue('other');
    expect(screen.getByLabelText('Role')).toBeInTheDocument();
    await user.type(screen.getByLabelText('Password'), 'updatedpass123');
    await user.selectOptions(screen.getByLabelText('Role'), 'admin');
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    const updateCall = fetchMock.mock.calls.find(([input, init]) => (
      String(input) === '/api/users/9' && init?.method === 'PUT'
    ));
    expect(JSON.parse(String(updateCall?.[1]?.body))).toMatchObject({
      password: 'updatedpass123',
      role: 'admin',
    });
    await screen.findByRole('heading', { name: 'User Management' });
  });

  it('allows regular users to update their own profile and password without a role field', async () => {
    const user = userEvent.setup();
    const fetchMock = mockApi({ role: 'user' });
    renderApp('/user/8/edit');

    expect(await screen.findByDisplayValue('staff')).toBeInTheDocument();
    expect(screen.queryByLabelText('Role')).not.toBeInTheDocument();
    await user.type(screen.getByLabelText('Password'), 'updatedpass123');
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    const updateCall = fetchMock.mock.calls.find(([input, init]) => (
      String(input) === '/api/users/8' && init?.method === 'PUT'
    ));
    expect(JSON.parse(String(updateCall?.[1]?.body))).toEqual({
      username: 'staff',
      email: 'staff@example.com',
      password: 'updatedpass123',
    });
  });

  it('prevents regular users from opening another user edit page', async () => {
    const fetchMock = mockApi({ role: 'user' });
    renderApp('/user/9/edit');

    expect(await screen.findByRole('heading', { name: 'Manage My Profile' })).toBeInTheDocument();
    expect(await screen.findByRole('alert')).toHaveTextContent('You can only manage your own profile');
    expect(fetchMock.mock.calls.some(([input]) => String(input) === '/api/users/9')).toBe(false);
  });
});
