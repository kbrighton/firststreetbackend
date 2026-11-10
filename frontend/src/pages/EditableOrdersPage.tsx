import { useQueryClient } from '@tanstack/react-query';
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  type ColumnDef,
  type PaginationState,
  type SortingState,
} from '@tanstack/react-table';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Form, Pagination, Spinner, Table } from 'react-bootstrap';
import { ApiError } from '../api/client';
import { useAlerts } from '../alerts/useAlerts';
import { updateOrder, type Order, type OrderInput } from '../api/orders';
import { orderKeys, useGridOrders } from '../orders/queries';

type GridFieldKey = 'log' | 'artlo' | 'cust' | 'title' | 'prior' | 'datin' | 'dueout'
  | 'colorf' | 'print_n' | 'logtype' | 'rush' | 'datout';
type GridField = { key: GridFieldKey; label: string; inputType: 'text' | 'date' | 'number' };

const PAGE_SIZE = 10;
const GRID_FIELDS: GridField[] = [
  { key: 'log', label: 'Log#', inputType: 'text' },
  { key: 'artlo', label: 'Artlog', inputType: 'text' },
  { key: 'cust', label: 'Customer', inputType: 'text' },
  { key: 'title', label: 'Title', inputType: 'text' },
  { key: 'prior', label: 'Priority', inputType: 'number' },
  { key: 'datin', label: 'Date In', inputType: 'date' },
  { key: 'dueout', label: 'Due Out', inputType: 'date' },
  { key: 'colorf', label: 'Colors', inputType: 'number' },
  { key: 'print_n', label: 'Print Number', inputType: 'number' },
  { key: 'logtype', label: 'Logtype', inputType: 'text' },
  { key: 'rush', label: 'Rush', inputType: 'text' },
  { key: 'datout', label: 'Date Out', inputType: 'date' },
];

function displayValue(value: unknown): string {
  return value === null || value === undefined ? '' : String(value);
}

function toUpdateValue(field: GridField, value: string): unknown {
  if (field.key === 'rush') {
    return /^(true|1|yes)$/i.test(value.trim());
  }
  if (field.inputType === 'number') {
    return value === '' ? null : Number(value);
  }
  return value === '' ? null : value;
}

type EditableGridCellProps = {
  order: Order;
  field: GridField;
  value: unknown;
  onSave: (order: Order, field: GridField, value: string) => void;
};

function EditableGridCell({ order, field, value, onSave }: EditableGridCellProps) {
  const serverValue = displayValue(value);
  const [cellValue, setCellValue] = useState(serverValue);
  const originalValue = useRef(serverValue);

  useEffect(() => {
    setCellValue(serverValue);
    originalValue.current = serverValue;
  }, [serverValue]);

  const handleBlur = () => {
    if (cellValue === originalValue.current) return;
    originalValue.current = cellValue;
    onSave(order, field, cellValue);
  };

  return (
    <Form.Control
      size="sm"
      type={field.inputType}
      step={field.inputType === 'number' ? '1' : undefined}
      aria-label={`Edit ${field.label} for ${order.log ?? 'order'}`}
      value={cellValue}
      onChange={(event) => setCellValue(event.target.value)}
      onBlur={handleBlur}
      onKeyDown={(event) => {
        if (event.key === 'Escape') {
          setCellValue(originalValue.current);
          event.currentTarget.blur();
        } else if (event.key === 'Enter') {
          event.preventDefault();
          event.currentTarget.blur();
        }
      }}
      className="border-0 bg-transparent"
    />
  );
}

export function EditableOrdersPage() {
  const queryClient = useQueryClient();
  const { addAlert } = useAlerts();
  const [search, setSearch] = useState('');
  const [sorting, setSorting] = useState<SortingState>([]);
  const [pagination, setPagination] = useState<PaginationState>({ pageIndex: 0, pageSize: PAGE_SIZE });
  const sortParam = sorting
    .map(({ id, desc }) => `${desc ? '-' : '+'}${id}`)
    .join(',');
  const params = {
    search,
    start: pagination.pageIndex * PAGE_SIZE,
    length: PAGE_SIZE,
    sort: sortParam || undefined,
  };
  const { data, error, isPending } = useGridOrders(params);
  const handledError = useRef<unknown>(null);

  useEffect(() => {
    if (!error || handledError.current === error) return;
    handledError.current = error;
    if (error instanceof ApiError && error.status === 401) return;
    addAlert(error instanceof Error ? error.message : 'Could not load orders', 'danger');
  }, [addAlert, error]);

  const saveCell = useCallback(async (order: Order, field: GridField, value: string) => {
    if (order.id === undefined) return;
    const update = { [field.key]: toUpdateValue(field, value) } as Partial<OrderInput>;
    try {
      await updateOrder(order.id, update);
      await queryClient.invalidateQueries({ queryKey: orderKeys.all });
    } catch (saveError) {
      if (saveError instanceof ApiError && saveError.status === 401) return;
      const fieldError = saveError instanceof ApiError ? saveError.fields?.[field.key]?.[0] : undefined;
      addAlert(
        fieldError ?? (saveError instanceof Error ? saveError.message : 'Could not save this field'),
        'danger',
      );
    }
  }, [addAlert, queryClient]);

  const columns = useMemo<ColumnDef<Order>[]>(() => GRID_FIELDS.map((field) => ({
    id: field.key,
    accessorFn: (row) => row[field.key],
    header: ({ column }) => {
      const direction = column.getIsSorted();
      return (
        <button
          type="button"
          className="btn btn-link text-white p-0 text-nowrap"
          aria-label={field.label}
          onClick={column.getToggleSortingHandler()}
        >
          {field.label}{direction === 'asc' ? ' ▲' : direction === 'desc' ? ' ▼' : ''}
        </button>
      );
    },
    cell: ({ row, getValue }) => (
      <EditableGridCell
        order={row.original}
        field={field}
        value={getValue()}
        onSave={saveCell}
      />
    ),
  })), [saveCell]);

  const table = useReactTable({
    data: data?.data ?? [],
    columns,
    state: { sorting, pagination },
    manualSorting: true,
    manualPagination: true,
    pageCount: Math.ceil((data?.total ?? 0) / PAGE_SIZE),
    onSortingChange: (updater) => {
      setSorting(updater);
      setPagination((current) => ({ ...current, pageIndex: 0 }));
    },
    onPaginationChange: setPagination,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <section>
      <h2>BETA SEARCH - FIELDS ARE EDITABLE AND WILL DIRECTLY UPDATE THE ORDER</h2>
      <h2>CAN SORT ON EVERY COLUMN</h2>
      <h2>SEARCH FIELD IS FOR BOTH CUSTOMER AND TITLE FIELDS, BUT A CUSTOMER NUMBER OR TITLE</h2>
      <p className="text-muted">Edits are saved when you leave a cell.</p>
      <Form.Group className="mb-3" controlId="editableOrdersSearch">
        <Form.Label>Search orders</Form.Label>
        <Form.Control
          type="search"
          value={search}
          onChange={(event) => {
            setSearch(event.target.value);
            setPagination((current) => ({ ...current, pageIndex: 0 }));
          }}
        />
      </Form.Group>
      {isPending ? (
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading orders…</span>
        </Spinner>
      ) : (
        <>
          <div className="table-responsive">
            <Table striped hover size="sm" className="mb-0">
              <thead className="thead-dark">
                {table.getHeaderGroups().map((headerGroup) => (
                  <tr key={headerGroup.id}>
                    {headerGroup.headers.map((header) => {
                      const direction = header.column.getIsSorted();
                      const ariaSort = direction === 'asc'
                        ? 'ascending'
                        : direction === 'desc' ? 'descending' : 'none';
                      return (
                        <th key={header.id} scope="col" aria-sort={ariaSort}>
                          {header.isPlaceholder
                            ? null
                            : flexRender(header.column.columnDef.header, header.getContext())}
                        </th>
                      );
                    })}
                  </tr>
                ))}
              </thead>
              <tbody>
                {table.getRowModel().rows.map((row) => (
                  <tr key={row.id}>
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </Table>
          </div>
          <Pagination className="mt-3">
            <Pagination.First
              aria-label="First"
              disabled={!table.getCanPreviousPage()}
              onClick={() => table.setPageIndex(0)}
            />
            <Pagination.Prev
              aria-label="Previous"
              disabled={!table.getCanPreviousPage()}
              onClick={() => table.previousPage()}
            />
            <Pagination.Item active>{pagination.pageIndex + 1}</Pagination.Item>
            <Pagination.Next
              aria-label="Next"
              disabled={!table.getCanNextPage()}
              onClick={() => table.nextPage()}
            />
            <Pagination.Last
              aria-label="Last"
              disabled={!table.getCanNextPage()}
              onClick={() => table.setPageIndex(Math.max(table.getPageCount() - 1, 0))}
            />
          </Pagination>
        </>
      )}
    </section>
  );
}
