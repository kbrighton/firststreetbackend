import { ApiError, apiFetch } from './client';
import type { components } from './schema';

export type Order = components['schemas']['Order'];
export type OrderDetail = components['schemas']['OrderDetail'];
export type OrderInput = components['schemas']['OrderInput'];

export type OrderPage = {
  data: Order[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
};

export type GridOrdersParams = {
  search: string;
  start: number;
  length: number;
  sort?: string;
};

export type GridOrdersPage = {
  data: Order[];
  total: number;
};

export type OrderSearchParams = {
  cust?: string;
  title?: string;
  page: number;
  perPage?: number;
  sort?: string;
};

export type DueoutRange = {
  start_date: string;
  end_date: string;
};

export async function searchOrders(params: OrderSearchParams): Promise<OrderPage> {
  const query = new URLSearchParams();
  if (params.cust !== undefined) query.set('cust', params.cust);
  if (params.title !== undefined) query.set('title', params.title);
  query.set('page', String(params.page));
  query.set('per_page', String(params.perPage ?? 20));
  if (params.sort) query.set('sort', params.sort);

  return apiFetch<OrderPage>(`/api/orders?${query.toString()}`);
}

export function getGridOrders(params: GridOrdersParams): Promise<GridOrdersPage> {
  const query = new URLSearchParams();
  if (params.search) query.set('search', params.search);
  query.set('start', String(params.start));
  query.set('length', String(params.length));
  if (params.sort) query.set('sort', params.sort);
  return apiFetch<GridOrdersPage>(`/api/data?${query.toString()}`);
}

export async function getOrderByLog(log: string): Promise<OrderDetail | null> {
  try {
    return await apiFetch<OrderDetail>(`/api/orders/log/${encodeURIComponent(log)}`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return null;
    }
    throw error;
  }
}

export function createOrder(order: OrderInput): Promise<Order> {
  return apiFetch<Order>('/api/orders', { method: 'POST', json: order });
}

export function updateOrder(id: number, order: Partial<OrderInput>): Promise<Order> {
  return apiFetch<Order>(`/api/orders/${id}`, { method: 'PUT', json: order });
}

export function deleteOrder(id: number): Promise<void> {
  return apiFetch<void>(`/api/orders/${id}`, { method: 'DELETE' });
}

export function getDueouts(range?: DueoutRange): Promise<Order[]> {
  const query = new URLSearchParams();
  if (range) {
    query.set('start_date', range.start_date);
    query.set('end_date', range.end_date);
  }
  const queryString = query.toString();
  const suffix = queryString ? `?${queryString}` : '';
  return apiFetch<Order[]>(`/api/orders/dueouts${suffix}`);
}
