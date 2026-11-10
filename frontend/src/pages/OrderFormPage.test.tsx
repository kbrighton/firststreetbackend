import { fireEvent, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { resetCsrfToken, setUnauthorizedHandler } from '../api/client';
import { renderApp } from '../test/renderApp';

const adminUser = {
  id: 8,
  username: 'admin',
  email: 'admin@example.com',
  role: 'admin',
};

const sampleOrder = {
  id: 42,
  log: 'LOG42',
  cust: 'CUST1',
  title: 'Sample order',
  datin: '2025-01-02',
  artout: '2025-01-10',
  dueout: '2025-01-12',
  print_n: 250,
  artlo: 'ART42',
  prior: '2',
  logtype: 'TR',
  colorf: 4,
  rush: true,
  ref_artlo: 'REF42',
  howship: 1,
  artno: 'A042',
  datout: null,
  created_at: '2025-01-02T10:00:00',
  updated_at: '2025-01-03T11:00:00',
  created_by_username: 'creator',
  updated_by_username: 'editor',
};

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

function mockApi({ updateStatus = 200, role = 'admin' }: { updateStatus?: number; role?: string } = {}) {
  const fetchMock = vi.fn<typeof fetch>(async (input, init) => {
    const path = String(input);
    const method = (init?.method ?? 'GET').toUpperCase();
    if (path === '/api/auth/me') return jsonResponse({ user: { ...adminUser, role } });
    if (path === '/api/auth/csrf') return jsonResponse({ csrf_token: 'csrf-token' });
    if (path.startsWith('/api/orders/log/')) return jsonResponse(sampleOrder);
    if (path === '/api/orders' && method === 'POST') {
      return jsonResponse(sampleOrder, 201);
    }
    if (path === '/api/orders/42' && method === 'PUT') {
      if (updateStatus !== 200) {
        return jsonResponse({
          error: 'Validation Error',
          message: 'The order could not be updated',
          status: updateStatus,
          fields: { title: ['Title could not be saved'] },
        }, updateStatus);
      }
      return jsonResponse(sampleOrder);
    }
    if (path === '/api/orders/42' && method === 'DELETE') return new Response(null, { status: 204 });
    if (path.startsWith('/api/orders?')) {
      return jsonResponse({ data: [], total: 0, page: 1, per_page: 20, pages: 0 });
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

describe('Order form page', () => {
  it('validates required fields and creates an order through the API', async () => {
    const user = userEvent.setup();
    const fetchMock = mockApi();
    renderApp('/order');

    await screen.findByRole('heading', { name: 'Order Form' });
    await user.click(screen.getByRole('button', { name: 'Submit' }));
    expect(await screen.findByText('LOG# is required')).toBeInTheDocument();
    expect(screen.getByText('Customer# is required')).toBeInTheDocument();
    expect(screen.getByText('Title is required')).toBeInTheDocument();
    expect(screen.getByText('Date In is required')).toBeInTheDocument();
    expect(screen.getByText('Log Type is required')).toBeInTheDocument();

    await user.type(screen.getByLabelText('LOG#'), 'LOG42');
    await user.type(screen.getByLabelText('Customer#'), 'CUST1');
    await user.type(screen.getByLabelText('Title'), 'Sample order');
    fireEvent.change(screen.getByLabelText('Date In'), { target: { value: '2025-01-02' } });
    await user.selectOptions(screen.getByLabelText('Log Type'), 'TR');
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      '/api/orders',
      expect.objectContaining({ method: 'POST' }),
    ));
    const createCall = fetchMock.mock.calls.find(([input, init]) => (
      String(input) === '/api/orders' && init?.method === 'POST'
    ));
    expect(JSON.parse(String(createCall?.[1]?.body))).toMatchObject({
      log: 'LOG42',
      cust: 'CUST1',
      title: 'Sample order',
      datin: '2025-01-02',
      logtype: 'TR',
      rush: false,
    });
  });

  it('loads edit values and shows audit information to admins', async () => {
    mockApi();
    renderApp('/order/LOG42');

    expect(await screen.findByLabelText('LOG#')).toHaveValue('LOG42');
    expect(screen.getByLabelText('Artist ID')).toHaveValue('A042');
    expect(screen.getByText(/Created by: creator/)).toBeInTheDocument();
    expect(screen.getByText(/Last updated by: editor/)).toBeInTheDocument();
  });

  it('does not show audit information to regular users', async () => {
    mockApi({ role: 'user' });
    renderApp('/order/LOG42');

    await screen.findByLabelText('LOG#');
    expect(screen.queryByText(/Created by:/)).not.toBeInTheDocument();
    expect(screen.queryByText(/Last updated by:/)).not.toBeInTheDocument();
  });

  it('updates an order and maps API field errors onto the form', async () => {
    const user = userEvent.setup();
    const fetchMock = mockApi({ updateStatus: 400 });
    renderApp('/order/LOG42');

    const title = await screen.findByLabelText('Title');
    await user.clear(title);
    await user.type(title, 'Changed title');
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    expect(await screen.findByText('Title could not be saved')).toBeInTheDocument();
    const updateCall = fetchMock.mock.calls.find(([input, init]) => (
      String(input) === '/api/orders/42' && init?.method === 'PUT'
    ));
    expect(JSON.parse(String(updateCall?.[1]?.body))).toMatchObject({ title: 'Changed title' });
  });

  it('requires confirmation before deleting an order', async () => {
    const user = userEvent.setup();
    const fetchMock = mockApi();
    renderApp('/order/LOG42');

    await screen.findByLabelText('LOG#');
    await user.click(screen.getByRole('button', { name: 'Delete Order' }));
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(fetchMock.mock.calls.some(([, init]) => init?.method === 'DELETE')).toBe(false);

    await user.click(screen.getByRole('button', { name: 'Delete order' }));
    await screen.findByRole('heading', { name: 'Search Form' });
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/orders/42',
      expect.objectContaining({ method: 'DELETE' }),
    );
    expect(await screen.findByRole('alert')).toHaveTextContent('Order deleted successfully');
  });
});
