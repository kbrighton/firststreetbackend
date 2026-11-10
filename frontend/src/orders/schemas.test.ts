import { describe, expect, it } from 'vitest';
import { dueoutSchema, logSearchSchema, orderFormSchema, searchSchema } from './schemas';

function firstMessage(result:
  | ReturnType<typeof searchSchema.safeParse>
  | ReturnType<typeof logSearchSchema.safeParse>
  | ReturnType<typeof dueoutSchema.safeParse>
  | ReturnType<typeof orderFormSchema.safeParse>
) {
  return result.success ? undefined : result.error.issues[0]?.message;
}

describe('search form schemas', () => {
  it('requires at least one search term and matches SearchForm messages', () => {
    expect(firstMessage(searchSchema.safeParse({ cust: '', title: '' })))
      .toBe('At least one search field is required');
    expect(firstMessage(searchSchema.safeParse({ cust: '123456', title: '' })))
      .toBe('Customer ID must be 5 characters or less');
    expect(firstMessage(searchSchema.safeParse({ cust: '12-45', title: '' })))
      .toBe('Customer ID must contain only letters and numbers');
    expect(firstMessage(searchSchema.safeParse({ cust: '', title: 'x'.repeat(101) })))
      .toBe('Title must be less than 100 characters');
  });

  it('accepts either search field, including whitespace-only optional input as WTForms does', () => {
    expect(searchSchema.safeParse({ cust: 'A1234', title: '' }).success).toBe(true);
    expect(searchSchema.safeParse({ cust: '', title: 'Screen print' }).success).toBe(true);
    expect(searchSchema.safeParse({ cust: '   ', title: '' }).success).toBe(true);
  });

  it('matches SearchLog required, exact-length, and alphanumeric messages', () => {
    expect(firstMessage(logSearchSchema.safeParse({ log: '' }))).toBe('LOG # is required');
    expect(firstMessage(logSearchSchema.safeParse({ log: '1234' })))
      .toBe('LOG # must be exactly 5 characters');
    expect(firstMessage(logSearchSchema.safeParse({ log: '12!45' })))
      .toBe('LOG # must contain only letters and numbers');
    expect(logSearchSchema.safeParse({ log: 'a1234' }).success).toBe(true);
  });

  it('requires both due-out dates and allows an inclusive same-day range', () => {
    expect(dueoutSchema.safeParse({ start_date: '', end_date: '' }).success).toBe(false);
    expect(firstMessage(dueoutSchema.safeParse({ start_date: '', end_date: '2025-01-01' })))
      .toBe('Start date is required');
    expect(firstMessage(dueoutSchema.safeParse({ start_date: '2025-01-01', end_date: '' })))
      .toBe('End date is required');
    expect(firstMessage(dueoutSchema.safeParse({ start_date: 'not-a-date', end_date: '2025-01-01' })))
      .toBe('Not a valid date value.');
    expect(firstMessage(dueoutSchema.safeParse({ start_date: '2025-01-02', end_date: '2025-01-01' })))
      .toBe('End date must be after start date');
    expect(dueoutSchema.safeParse({ start_date: '2025-01-01', end_date: '2025-01-01' }).success)
      .toBe(true);
  });

  it('validates order fields and accepts every OrderForm log type', () => {
    const values = {
      log: 'LOG42',
      cust: 'CUST1',
      title: 'Sample order',
      datin: '2025-01-02',
      artout: '',
      dueout: '',
      print_n: '',
      artlo: '',
      rush: false,
      prior: '',
      logtype: 'DG',
      colorf: '',
      ref_artlo: '',
      howship: '',
      artno: '',
      datout: '',
    };

    expect(orderFormSchema.safeParse(values).success).toBe(true);
    expect(firstMessage(orderFormSchema.safeParse({ ...values, log: 'LO!42' })))
      .toBe('LOG# must contain only letters and numbers');
    expect(firstMessage(orderFormSchema.safeParse({ ...values, title: 'x'.repeat(101) })))
      .toBe('Title must be less than 100 characters');
    expect(firstMessage(orderFormSchema.safeParse({ ...values, datin: '2025-02-30' })))
      .toBe('Not a valid date value.');
    expect(firstMessage(orderFormSchema.safeParse({ ...values, print_n: '0' })))
      .toBe('Quantity must be a positive number');
    expect(firstMessage(orderFormSchema.safeParse({ ...values, artno: 'ABC' })))
      .toBe('Artist ID must be between 4 and 5 characters');
  });
});
