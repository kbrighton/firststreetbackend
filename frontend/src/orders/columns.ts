import type { Order } from '../api/orders';

export type OrderColumnKey = keyof Order | 'artno';

export type OrderColumn = {
  key: OrderColumnKey;
  title: string;
  sortable: boolean;
};

export const SORTABLE_ORDER_FIELDS: ReadonlySet<string> = new Set([
  'id', 'log', 'artlo', 'cust', 'title', 'prior', 'datin', 'dueout',
  'colorf', 'print_n', 'logtype', 'rush', 'datout',
]);

const column = (key: OrderColumnKey, title: string): OrderColumn => ({
  key,
  title,
  sortable: SORTABLE_ORDER_FIELDS.has(key),
});

export const ORDER_COLUMNS: OrderColumn[] = [
  column('log', 'Log#'),
  column('artlo', 'Artlog'),
  column('cust', 'Customer'),
  column('title', 'Title'),
  column('prior', 'Priority'),
  column('datin', 'Date In'),
  column('dueout', 'Due Out'),
  column('colorf', 'Colors'),
  column('print_n', 'Print Number'),
  column('logtype', 'Logtype'),
  column('rush', 'Rush'),
  column('artno', 'Artist ID'),
];
