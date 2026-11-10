import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ApiError, apiFetch } from './client';
import {
  createOrder,
  deleteOrder,
  getDueouts,
  getGridOrders,
  getOrderByLog,
  searchOrders,
  updateOrder,
} from './orders';

vi.mock('./client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('./client')>();
  return { ...actual, apiFetch: vi.fn() };
});

const fetchMock = vi.mocked(apiFetch);

beforeEach(() => fetchMock.mockReset());

describe('orders API', () => {
  it('encodes search terms and sends pagination and server sort parameters', async () => {
    fetchMock.mockResolvedValue({} as never);

    await searchOrders({ cust: 'CUST1', title: 'Blue print', page: 2, sort: '+datin' });

    const [path] = fetchMock.mock.calls[0];
    const query = new URL(path, 'http://localhost').searchParams;
    expect(query.get('cust')).toBe('CUST1');
    expect(query.get('title')).toBe('Blue print');
    expect(query.get('page')).toBe('2');
    expect(query.get('per_page')).toBe('20');
    expect(query.get('sort')).toBe('+datin');
  });

  it('returns null for a missing log and rethrows other API errors', async () => {
    fetchMock.mockRejectedValueOnce(new ApiError(404, 'Not Found', 'Order not found'));
    await expect(getOrderByLog('LOG42')).resolves.toBeNull();

    const serverError = new ApiError(500, 'Internal Server Error', 'Unexpected error');
    fetchMock.mockRejectedValueOnce(serverError);
    await expect(getOrderByLog('LOG42')).rejects.toBe(serverError);
  });

  it('uses the order CRUD endpoints for create, update, and delete', async () => {
    fetchMock.mockResolvedValue({} as never);
    const payload = {
      log: 'LOG42',
      cust: 'CUST1',
      title: 'Sample order',
      datin: '2025-01-02',
      logtype: 'TR' as const,
    };

    await createOrder(payload);
    await updateOrder(42, { title: 'Updated order' });
    await deleteOrder(42);

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      '/api/orders',
      { method: 'POST', json: payload },
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      '/api/orders/42',
      { method: 'PUT', json: { title: 'Updated order' } },
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      '/api/orders/42',
      { method: 'DELETE' },
    );
  });

  it('uses the legacy grid read contract for search, sort, and pagination', async () => {
    fetchMock.mockResolvedValue({} as never);

    await getGridOrders({ search: 'CUST1', start: 10, length: 10, sort: '+title,-log' });

    const [path] = fetchMock.mock.calls[0];
    const query = new URL(path, 'http://localhost').searchParams;
    expect(path).toContain('/api/data?');
    expect(query.get('search')).toBe('CUST1');
    expect(query.get('start')).toBe('10');
    expect(query.get('length')).toBe('10');
    expect(query.get('sort')).toBe('+title,-log');
  });

  it('requests all due-outs without a range or sends both date parameters', async () => {
    fetchMock.mockResolvedValue([] as never);

    await getDueouts();
    expect(fetchMock).toHaveBeenLastCalledWith('/api/orders/dueouts');

    await getDueouts({ start_date: '2025-01-01', end_date: '2025-01-31' });
    const [path] = fetchMock.mock.calls[1];
    const query = new URL(path, 'http://localhost').searchParams;
    expect(query.get('start_date')).toBe('2025-01-01');
    expect(query.get('end_date')).toBe('2025-01-31');
  });
});
