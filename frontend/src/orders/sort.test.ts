import { describe, expect, it } from 'vitest';
import type { Order } from '../api/orders';
import { nextSort, parseSortParam, sortRows, toSortParam } from './sort';

describe('order sort helpers', () => {
  it('parses only supported single-field sort parameters', () => {
    expect(parseSortParam('+datin')).toEqual({ field: 'datin', dir: 'asc' });
    expect(parseSortParam('-cust')).toEqual({ field: 'cust', dir: 'desc' });
    expect(parseSortParam('log')).toEqual({ field: 'log', dir: 'asc' });
    expect(parseSortParam(undefined)).toBeNull();
    expect(parseSortParam('')).toBeNull();
    expect(parseSortParam('+artno')).toBeNull();
    expect(parseSortParam('+datin,-cust')).toBeNull();
  });

  it('serializes sort state and cycles ascending, descending, then default', () => {
    expect(toSortParam({ field: 'datin', dir: 'asc' })).toBe('+datin');
    expect(toSortParam({ field: 'datin', dir: 'desc' })).toBe('-datin');
    expect(toSortParam(null)).toBeUndefined();
    expect(nextSort(null, 'datin')).toEqual({ field: 'datin', dir: 'asc' });
    expect(nextSort({ field: 'datin', dir: 'asc' }, 'datin')).toEqual({
      field: 'datin', dir: 'desc',
    });
    expect(nextSort({ field: 'datin', dir: 'desc' }, 'datin')).toBeNull();
    expect(nextSort({ field: 'datin', dir: 'desc' }, 'cust')).toEqual({
      field: 'cust', dir: 'asc',
    });
  });

  it('sorts text, dates, numeric columns and leaves nulls last in either direction', () => {
    const rows: Order[] = [
      { id: 1, log: 'LOG10', datin: '2025-02-01', prior: '10' },
      { id: 2, log: 'LOG02', datin: '2025-01-01', prior: '2' },
      { id: 3, log: 'LOG01', datin: null, prior: null },
    ];

    expect(sortRows(rows, { field: 'log', dir: 'asc' }).map((row) => row.id)).toEqual([3, 2, 1]);
    expect(sortRows(rows, { field: 'datin', dir: 'desc' }).map((row) => row.id)).toEqual([1, 2, 3]);
    expect(sortRows(rows, { field: 'prior', dir: 'asc' }).map((row) => row.id)).toEqual([2, 1, 3]);
    expect(sortRows(rows, { field: 'prior', dir: 'desc' }).map((row) => row.id)).toEqual([1, 2, 3]);
  });

  it('keeps the input order when sorting is unset or unsupported', () => {
    const rows: Order[] = [{ id: 2, log: 'LOG02' }, { id: 1, log: 'LOG01' }];

    expect(sortRows(rows, null)).toEqual(rows);
    expect(sortRows(rows, { field: 'unknown', dir: 'asc' })).toEqual(rows);
  });
});
