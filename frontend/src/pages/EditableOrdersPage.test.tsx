import { fireEvent, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { resetCsrfToken, setUnauthorizedHandler } from '../api/client';
import { renderApp } from '../test/renderApp';

const sampleRows = [
  {
    id: 12,
    log: 'LOG12',
    artlo: 'ART12',
    cust: 'CUST1',
    title: 'Sample order',
    prior: '2',
    datin: '2025-01-02',
    dueout: '2025-01-12',
    colorf: 4,
    print_n: 250,
    logtype: 'TR',
    rush: false,
    datout: null,
  },
];

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

function mockApi({ updateStatus = 200 }: { updateStatus?: number } = {}) {
  const fetchMock = vi.fn<typeof fetch>(async (input, init) => {
    const path = String(input);
    const method = (init?.method ?? 'GET').toUpperCase();
    if (path === '/api/auth/me') {
      return jsonResponse({ user: { id: 8, username: 'staff', email: 'staff@example.com', role: 'user' } });
    }
    if (path === '/api/auth/csrf') return jsonResponse({ csrf_token: 'csrf-token' });
    if (path.startsWith('/api/data?')) return jsonResponse({ data: sampleRows, total: 25 });
    if (path === '/api/orders/12' && method === 'PUT') {
      if (updateStatus !== 200) {
        return jsonResponse({
          error: 'Validation Error',
          message: 'The order could not be updated',
          status: updateStatus,
          fields: { title: ['Title could not be saved'] },
        }, updateStatus);
      }
      return jsonResponse({ ...sampleRows[0], title: 'Updated order' });
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

describe('Editable orders grid', () => {
  it('loads the legacy grid API data and keeps search, sort, and paging server-side', async () => {
    const user = userEvent.setup();
    const fetchMock = mockApi();
    renderApp('/newsearch');

    expect(await screen.findByLabelText('Edit Title for LOG12')).toHaveValue('Sample order');
    const firstRequest = fetchMock.mock.calls.find(([input]) => String(input).startsWith('/api/data?'));
    const firstQuery = new URL(String(firstRequest?.[0]), 'http://localhost').searchParams;
    expect(firstQuery.get('start')).toBe('0');
    expect(firstQuery.get('length')).toBe('10');

    await user.type(screen.getByLabelText('Search orders'), 'CUST1');
    await waitFor(() => {
      const request = fetchMock.mock.calls.find(([input]) => (
        String(input).includes('/api/data?')
        && new URL(String(input), 'http://localhost').searchParams.get('search') === 'CUST1'
      ));
      expect(request).toBeDefined();
    });

    await user.click(screen.getByRole('button', { name: 'Log#' }));
    await waitFor(() => {
      const requests = fetchMock.mock.calls.filter(([input]) => String(input).includes('/api/data?'));
      expect(new URL(String(requests.at(-1)?.[0]), 'http://localhost').searchParams.get('sort'))
        .toBe('+log');
    });

    await user.click(screen.getByLabelText('Next'));
    await waitFor(() => {
      const requests = fetchMock.mock.calls.filter(([input]) => String(input).includes('/api/data?'));
      const query = new URL(String(requests.at(-1)?.[0]), 'http://localhost').searchParams;
      expect(query.get('start')).toBe('10');
      expect(query.get('length')).toBe('10');
    });
  });

  it('saves edited cells on blur and shows field-level API errors without dropping the row', async () => {
    const user = userEvent.setup();
    const fetchMock = mockApi({ updateStatus: 400 });
    renderApp('/newsearch');

    const title = await screen.findByLabelText('Edit Title for LOG12');
    await user.clear(title);
    await user.type(title, 'Rejected title');
    fireEvent.blur(title);

    expect(await screen.findByRole('alert')).toHaveTextContent('Title could not be saved');
    expect(screen.getByLabelText('Edit Title for LOG12')).toHaveValue('Rejected title');
    const updateCall = fetchMock.mock.calls.find(([input, init]) => (
      String(input) === '/api/orders/12' && init?.method === 'PUT'
    ));
    expect(JSON.parse(String(updateCall?.[1]?.body))).toEqual({ title: 'Rejected title' });
  });

  it('supports the planned /new_search alias', async () => {
    mockApi();
    renderApp('/new_search');

    expect(await screen.findByLabelText('Edit Title for LOG12')).toHaveValue('Sample order');
    expect(screen.getByRole('heading', { name: /BETA SEARCH/ })).toBeInTheDocument();
  });
});
