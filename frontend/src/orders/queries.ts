import { useQuery } from '@tanstack/react-query';
import {
  getDueouts,
  getGridOrders,
  getOrderByLog,
  searchOrders,
  type DueoutRange,
  type GridOrdersParams,
  type OrderSearchParams,
} from '../api/orders';

export const orderKeys = {
  all: ['orders'] as const,
  search: (params: OrderSearchParams) => ['orders', 'search', params] as const,
  grid: (params: GridOrdersParams) => ['orders', 'grid', params] as const,
  log: (log: string) => ['orders', 'log', log] as const,
  dueouts: (range?: DueoutRange) => ['orders', 'dueouts', range ?? 'all'] as const,
};

export function useOrderSearch(params: OrderSearchParams) {
  return useQuery({
    queryKey: orderKeys.search(params),
    queryFn: () => searchOrders(params),
  });
}

export function useGridOrders(params: GridOrdersParams) {
  return useQuery({
    queryKey: orderKeys.grid(params),
    queryFn: () => getGridOrders(params),
  });
}

export function useOrderByLog(log: string) {
  return useQuery({
    queryKey: orderKeys.log(log),
    queryFn: () => getOrderByLog(log),
    enabled: Boolean(log),
  });
}

export function useDueouts(range?: DueoutRange, enabled = true) {
  return useQuery({
    queryKey: orderKeys.dueouts(range),
    queryFn: () => getDueouts(range),
    enabled,
  });
}
