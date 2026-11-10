import { fireEvent, screen, within } from '@testing-library/react';
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

const laterOrder: Order = {
  id: 2,
  log: 'LATER',
  cust: 'CUST1',
  title: 'Later dueout',
  datin: '2025-01-01',
  dueout: '2025-03-02',
  logtype: 'TR',
};

const earlierOrder: Order = {
  id: 1,
  log: 'EARLY',
  cust: 'CUST1',
  title: 'Earlier dueout',
  datin: '2025-01-01',
  dueout: '2025-03-01',
  logtype: 'TR',
};

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

function mockApi(dueouts: unknown = [laterOrder, earlierOrder], status = 200) {
  const fetchMock = vi.fn<typeof fetch>(async (input) => {
    const path = String(input);
    if (path === '/api/auth/me') return jsonResponse({ user: staffUser });
    if (path.startsWith('/api/orders/dueouts')) return jsonResponse(dueouts, status);
    return jsonResponse({ error: 'Not Found', message: 'Not found', status: 404 }, 404);
  });
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

beforeEach(() => {
  resetCsrfToken();
  setUnauthorizedHandler(null);
});

describe('Due Outs page', () => {
  it('validates required dates and the inclusive date range before submitting', async () => {
    const user = userEvent.setup();
    mockApi([laterOrder]);
    renderApp('/dueouts');

    await screen.findByRole('heading', { name: 'Search Form' });
    await user.click(screen.getByRole('button', { name: 'Submit' }));
    expect(await screen.findByText('Start date is required')).toBeInTheDocument();
    expect(screen.getByText('End date is required')).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText('Start Due Outs Date'), {
      target: { value: '2025-03-02' },
    });
    fireEvent.change(screen.getByLabelText('End Due Outs Date'), {
      target: { value: '2025-03-01' },
    });
    await user.click(screen.getByRole('button', { name: 'Submit' }));
    expect(await screen.findByText('End date must be after start date')).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText('End Due Outs Date'), {
      target: { value: '2025-03-02' },
    });
    await user.click(screen.getByRole('button', { name: 'Submit' }));
    expect(await screen.findByText('Later dueout')).toBeInTheDocument();
  });

  it('restores a shared date-range URL and shows the responsive, sortable table', async () => {
    const fetchMock = mockApi([laterOrder, earlierOrder]);
    renderApp('/dueouts?start_date=2025-03-01&end_date=2025-03-02');

    expect(await screen.findByText('Later dueout')).toBeInTheDocument();
    const table = screen.getByRole('table');
    expect(table).toHaveClass('table-striped');
    expect(screen.getByRole('heading', { name: 'Due Outs' })).toBeInTheDocument();
    expect(within(table).getByText('Due Outs')).toBeInTheDocument();
    expect(table.parentElement).toHaveClass('table-responsive');
    expect(within(table).queryByRole('columnheader', { name: 'Actions' })).not.toBeInTheDocument();
    expect(screen.getByTestId('current-location')).toHaveTextContent(
      '/dueouts?start_date=2025-03-01&end_date=2025-03-02',
    );

    const dueoutsRequest = fetchMock.mock.calls.find(([input]) => String(input).startsWith('/api/orders/dueouts?'));
    const query = new URL(String(dueoutsRequest?.[0]), 'http://localhost').searchParams;
    expect(query.get('start_date')).toBe('2025-03-01');
    expect(query.get('end_date')).toBe('2025-03-02');

    await userEvent.setup().click(screen.getByRole('button', { name: 'Due Out' }));
    const rows = screen.getAllByRole('row').slice(1);
    expect(rows.map((row) => row.querySelector('td')?.textContent)).toEqual(['EARLY', 'LATER']);
  });
});

describe('All Due Outs page', () => {
  it('loads all due-outs without date parameters and sorts in the browser', async () => {
    const fetchMock = mockApi([laterOrder, earlierOrder]);
    renderApp('/dueouts_all');

    expect(await screen.findByText('Later dueout')).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith('/api/orders/dueouts', expect.anything());
    await userEvent.setup().click(screen.getByRole('button', { name: 'Due Out' }));
    expect(screen.getAllByRole('row').slice(1).map((row) => row.querySelector('td')?.textContent))
      .toEqual(['EARLY', 'LATER']);
  });

  it('shows an empty table without an alert when there are no due-outs', async () => {
    mockApi([]);
    renderApp('/dueouts_all');

    const table = await screen.findByRole('table');
    expect(screen.getByRole('heading', { name: 'Due Outs' })).toBeInTheDocument();
    expect(within(table).getByText('Due Outs')).toBeInTheDocument();
    expect(within(table).getAllByRole('row')).toHaveLength(1);
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('shows API failures in a dismissible danger alert', async () => {
    mockApi({ error: 'Internal Server Error', message: 'Could not load due-outs', status: 500 }, 500);
    renderApp('/dueouts_all');

    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('Could not load due-outs');
    expect(alert).toHaveClass('alert-danger');
  });
});