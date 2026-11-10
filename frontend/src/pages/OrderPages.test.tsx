import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { resetCsrfToken, setUnauthorizedHandler } from '../api/client';
import type { Order } from '../api/orders';
import { renderApp } from '../test/renderApp';

const staffUser = {
  id: 8,
  username: 'staff',
  email: 'staff@example.com',
  role: 'user' as const,
};

const sampleOrder: Order = {
  id: 42,
  log: 'LOG42',
  artlo: 'ART42',
  cust: 'CUST1',
  title: 'Sample order',
  prior: '2',
  datin: '2025-01-02',
  artout: '2025-01-10',
  dueout: '2025-01-12',
  print_n: 250,
  colorf: 4,
  logtype: 'TR',
  rush: true,
};

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

type Reply = { body: unknown; status?: number };

function mockApi({
  searchReply = {
    body: { data: [sampleOrder], total: 1, page: 1, per_page: 20, pages: 1 },
  },
  logReply = { body: sampleOrder },
}: { searchReply?: Reply; logReply?: Reply | ((path: string) => Reply) } = {}) {
  const fetchMock = vi.fn<typeof fetch>(async (input) => {
    const path = String(input);
    if (path === '/api/auth/me') return jsonResponse({ user: staffUser });
    if (path.startsWith('/api/orders?')) {
      return jsonResponse(searchReply.body, searchReply.status ?? 200);
    }
    if (path.startsWith('/api/orders/log/')) {
      const reply = typeof logReply === 'function' ? logReply(path) : logReply;
      return jsonResponse(reply.body, reply.status ?? 200);
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

describe('Search page', () => {
  it('validates empty fields and navigates to URL-backed search results', async () => {
    const user = userEvent.setup();
    mockApi();
    renderApp('/search');

    await screen.findByRole('heading', { name: 'Search Form' });
    await user.click(screen.getByRole('button', { name: 'Submit' }));
    expect(await screen.findByText('At least one search field is required')).toBeInTheDocument();

    await user.type(screen.getByLabelText('Customer ID'), '123456');
    await user.click(screen.getByRole('button', { name: 'Submit' }));
    expect(await screen.findByText('Customer ID must be 5 characters or less')).toBeInTheDocument();
    await user.clear(screen.getByLabelText('Customer ID'));
    await user.type(screen.getByLabelText('Customer ID'), 'CUST1');
    await user.type(screen.getByLabelText('Title'), 'Screen print');
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    expect(await screen.findByRole('heading', { name: 'Search' })).toBeInTheDocument();
    expect(screen.getByTestId('current-location')).toHaveTextContent(
      '/order_search?cust=CUST1&title=Screen+print',
    );
  });
});

describe('Search results page', () => {
  it('requests 20 results and updates URL state for sorting and pagination', async () => {
    const user = userEvent.setup();
    const fetchMock = mockApi({
      searchReply: {
        body: { data: [sampleOrder], total: 43, page: 1, per_page: 20, pages: 3 },
      },
    });
    renderApp('/order_search?cust=CUST1');

    expect(await screen.findByText('Sample order')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Search' })).toBeInTheDocument();
    const table = screen.getByRole('table');
    expect(table).toHaveClass('table-striped');
    expect(screen.getByText('Searches')).toBeInTheDocument();

    const initialRequest = fetchMock.mock.calls.find(([input]) => String(input).startsWith('/api/orders?'));
    const initialQuery = new URL(String(initialRequest?.[0]), 'http://localhost').searchParams;
    expect(initialQuery.get('per_page')).toBe('20');

    await user.click(screen.getByRole('button', { name: 'Date In' }));
    await waitFor(() => expect(screen.getByTestId('current-location')).toHaveTextContent('sort=%2Bdatin'));
    const sortedRequest = fetchMock.mock.calls
      .filter(([input]) => String(input).startsWith('/api/orders?'))
      .at(-1);
    expect(new URL(String(sortedRequest?.[0]), 'http://localhost').searchParams.get('sort')).toBe('+datin');

    await user.click(screen.getByLabelText('Next'));
    await waitFor(() => expect(screen.getByTestId('current-location')).toHaveTextContent('page=2'));
    expect(screen.getByTestId('current-location')).toHaveTextContent('sort=%2Bdatin');
  });

  it('falls back to page one and default sorting for malformed URL state', async () => {
    const fetchMock = mockApi();
    renderApp('/order_search?cust=CUST1&page=bad&sort=%2Bartno');

    await screen.findByText('Sample order');
    const request = fetchMock.mock.calls.find(([input]) => String(input).startsWith('/api/orders?'));
    const query = new URL(String(request?.[0]), 'http://localhost').searchParams;
    expect(query.get('page')).toBe('1');
    expect(query.has('sort')).toBe(false);
  });

  it('returns to Search Form with an alert when there are no matches', async () => {
    mockApi({ searchReply: { body: { data: [], total: 0, page: 1, per_page: 20, pages: 0 } } });
    renderApp('/order_search?cust=MISS1');

    expect(await screen.findByRole('heading', { name: 'Search Form' })).toBeInTheDocument();
    expect(await screen.findByRole('alert')).toHaveTextContent('Could not find any orders that match');
  });

  it('shows API validation messages in a dismissible danger alert', async () => {
    mockApi({
      searchReply: {
        body: {
          error: 'Bad Request',
          message: 'At least one search field is required',
          status: 400,
          fields: { cust: ['At least one search field is required'] },
        },
        status: 400,
      },
    });
    renderApp('/order_search?cust=CUST1');

    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('At least one search field is required');
    expect(alert).toHaveClass('alert-danger');
    expect(alert.querySelector('.btn-close')).not.toBeNull();
  });
});

describe('Search Log and Order Detail pages', () => {
  it('validates the log and shows the not-found alert without leaving Search Log', async () => {
    const user = userEvent.setup();
    mockApi({ logReply: { body: { error: 'Not Found', message: 'Order not found', status: 404 }, status: 404 } });
    renderApp('/search_log');

    await screen.findByRole('heading', { name: 'Search Form' });
    await user.click(screen.getByRole('button', { name: 'Submit' }));
    expect(await screen.findByText('LOG # is required')).toBeInTheDocument();
    await user.type(screen.getByLabelText('LOG #'), '1234');
    await user.click(screen.getByRole('button', { name: 'Submit' }));
    expect(await screen.findByText('LOG # must be exactly 5 characters')).toBeInTheDocument();
    await user.clear(screen.getByLabelText('LOG #'));
    await user.type(screen.getByLabelText('LOG #'), 'MISS1');
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    expect(await screen.findByRole('alert')).toHaveTextContent('Log number does not exist');
    expect(screen.getByTestId('current-location')).toHaveTextContent('/search_log');
  });

  it('opens a found order as read-only detail with a classic edit link', async () => {
    const user = userEvent.setup();
    mockApi();
    renderApp('/search_log');

    await screen.findByRole('heading', { name: 'Search Form' });
    await user.type(screen.getByLabelText('LOG #'), 'LOG42');
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    expect(await screen.findByLabelText('LOG#')).toHaveValue('LOG42');
    expect(screen.getByLabelText('Customer#')).toHaveValue('CUST1');
    expect(screen.getByLabelText('Date In')).toHaveValue('2025-01-02');
    expect(screen.getByLabelText('Order Due Out')).toHaveValue('2025-01-12');
    expect(screen.getByRole('link', { name: 'Edit in classic app' })).toHaveAttribute(
      'href',
      'http://localhost:5000/order/LOG42',
    );
  });

  it('redirects a missing order detail to Search Form with the log in the alert', async () => {
    mockApi({ logReply: { body: { error: 'Not Found', message: 'Order not found', status: 404 }, status: 404 } });
    renderApp('/order/MISS1');

    expect(await screen.findByRole('heading', { name: 'Search Form' })).toBeInTheDocument();
    expect(await screen.findByRole('alert')).toHaveTextContent('Order with log number MISS1 not found');
    expect(screen.getByTestId('current-location')).toHaveTextContent('/search');
  });
});
