import type { Order } from '../api/orders';
import { SORTABLE_ORDER_FIELDS } from './columns';

export type SortState = { field: string; dir: 'asc' | 'desc' } | null;

const NUMERIC_ORDER_FIELDS = new Set(['prior', 'colorf', 'print_n']);

export function parseSortParam(sort?: string): SortState {
  if (!sort) return null;

  const value = sort.trim();
  if (!value || value.includes(',')) return null;

  const hasDirection = value[0] === '+' || value[0] === '-';
  const field = hasDirection ? value.slice(1) : value;
  if (!SORTABLE_ORDER_FIELDS.has(field)) return null;

  return { field, dir: value[0] === '-' ? 'desc' : 'asc' };
}

export function toSortParam(sort: SortState): string | undefined {
  if (!sort || !SORTABLE_ORDER_FIELDS.has(sort.field)) return undefined;
  return `${sort.dir === 'asc' ? '+' : '-'}${sort.field}`;
}

export function nextSort(current: SortState, field: string): SortState {
  if (!SORTABLE_ORDER_FIELDS.has(field)) return current;
  if (current?.field !== field) return { field, dir: 'asc' };
  if (current.dir === 'asc') return { field, dir: 'desc' };
  return null;
}

function compareValues(first: unknown, second: unknown, field: string): number {
  if (NUMERIC_ORDER_FIELDS.has(field)) {
    const firstNumber = Number(first);
    const secondNumber = Number(second);
    if (Number.isFinite(firstNumber) && Number.isFinite(secondNumber)) {
      return firstNumber - secondNumber;
    }
  }

  if (typeof first === 'number' && typeof second === 'number') {
    return first - second;
  }
  if (typeof first === 'boolean' && typeof second === 'boolean') {
    return Number(first) - Number(second);
  }

  return String(first).localeCompare(String(second), undefined, {
    numeric: true,
    sensitivity: 'base',
  });
}

export function sortRows(rows: Order[], sort: SortState): Order[] {
  if (!sort || !SORTABLE_ORDER_FIELDS.has(sort.field)) return rows;

  const direction = sort.dir === 'asc' ? 1 : -1;
  return rows
    .map((row, index) => ({ row, index }))
    .sort(({ row: firstRow, index: firstIndex }, { row: secondRow, index: secondIndex }) => {
      const firstValue = firstRow[sort.field as keyof Order];
      const secondValue = secondRow[sort.field as keyof Order];
      const firstIsNull = firstValue === null || firstValue === undefined;
      const secondIsNull = secondValue === null || secondValue === undefined;

      if (firstIsNull && secondIsNull) return firstIndex - secondIndex;
      if (firstIsNull) return 1;
      if (secondIsNull) return -1;

      return compareValues(firstValue, secondValue, sort.field) * direction || firstIndex - secondIndex;
    })
    .map(({ row }) => row);
}
