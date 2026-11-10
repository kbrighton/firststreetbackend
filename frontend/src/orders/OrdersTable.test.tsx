import { fireEvent, render, screen, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import type { Order } from '../api/orders';
import { OrdersPagination } from './OrdersPagination';
import { OrdersTable } from './OrdersTable';

const sampleOrder: Order = {
  id: 42,
  log: 'LOG42',
  artlo: 'ART42',
  cust: 'CUST1',
  title: 'Sample order',
  prior: '2',
  datin: '2025-01-02',
  dueout: null,
  colorf: 4,
  print_n: 250,
  logtype: 'TR',
  rush: true,
};

describe('OrdersTable', () => {
  it('renders the Jinja-style caption, headers, rows, and edit action', () => {
    render(
      <MemoryRouter>
        <OrdersTable
          rows={[sampleOrder]}
          caption="Searches"
          sort={null}
          onSortChange={() => undefined}
          showActions
        />
      </MemoryRouter>,
    );

    const table = screen.getByRole('table');
    expect(table).toHaveClass('table', 'table-striped');
    expect(within(table).getByText('Searches')).toBeInTheDocument();
    expect(table.querySelector('thead')).toHaveClass('thead-dark');
    expect(within(table).getAllByRole('columnheader').map((header) => header.textContent?.trim())).toEqual([
      'Log#', 'Artlog', 'Customer', 'Title', 'Priority', 'Date In', 'Due Out', 'Colors',
      'Print Number', 'Logtype', 'Rush', 'Artist ID', 'Actions',
    ]);
    expect(within(table).getByText('Sample order')).toBeInTheDocument();
    expect(within(table).getByText('True')).toBeInTheDocument();
    expect(within(table).getByRole('link', { name: 'Edit order LOG42' })).toHaveAttribute(
      'href',
      '/order/LOG42',
    );
    expect(within(table).getByRole('columnheader', { name: 'Artist ID' }).querySelector('button'))
      .toBeNull();
  });

  it('exposes sort state and reports the next sort when a header is clicked', () => {
    const onSortChange = vi.fn();
    const { rerender } = render(
      <MemoryRouter>
        <OrdersTable
          rows={[sampleOrder]}
          caption="Due Outs"
          sort={null}
          onSortChange={onSortChange}
        />
      </MemoryRouter>,
    );

    const dateHeader = screen.getByRole('columnheader', { name: 'Date In' });
    expect(dateHeader).toHaveAttribute('aria-sort', 'none');
    fireEvent.click(within(dateHeader).getByRole('button', { name: 'Date In' }));
    expect(onSortChange).toHaveBeenCalledWith({ field: 'datin', dir: 'asc' });

    rerender(
      <MemoryRouter>
        <OrdersTable
          rows={[sampleOrder]}
          caption="Due Outs"
          sort={{ field: 'datin', dir: 'desc' }}
          onSortChange={onSortChange}
          responsive
        />
      </MemoryRouter>,
    );

    expect(screen.getByRole('columnheader', { name: 'Date In' })).toHaveAttribute('aria-sort', 'descending');
    expect(screen.getByRole('table').parentElement).toHaveClass('table-responsive');
    expect(screen.getByText('▼')).toBeInTheDocument();
  });

  it('renders pagination controls and requests the selected page', () => {
    const onPageChange = vi.fn();
    render(<OrdersPagination page={2} pages={4} onPageChange={onPageChange} />);

    expect(screen.getByRole('navigation', { name: 'Search results pages' })).toBeInTheDocument();
    expect(document.querySelector('.page-item.active .page-link')).toHaveTextContent('2');
    fireEvent.click(screen.getByLabelText('Next'));
    expect(onPageChange).toHaveBeenCalledWith(3);
  });
});
