import type { ReactNode } from 'react';
import { Table } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { APP_PATHS } from '../appPaths';
import type { Order } from '../api/orders';
import { ORDER_COLUMNS } from './columns';
import { SortableHeader } from './SortableHeader';
import type { SortState } from './sort';

type OrdersTableProps = {
  rows: Order[];
  caption: string;
  sort: SortState;
  onSortChange: (sort: SortState) => void;
  showActions?: boolean;
  responsive?: boolean;
};

function displayValue(value: unknown): ReactNode {
  if (value === null || value === undefined) return '';
  if (typeof value === 'boolean') return value ? 'True' : 'False';
  return String(value);
}

export function OrdersTable({
  rows,
  caption,
  sort,
  onSortChange,
  showActions = false,
  responsive = false,
}: OrdersTableProps) {
  const table = (
    <Table striped className="mb-0">
      <caption>{caption}</caption>
      <thead className="thead-dark">
        <tr>
          {ORDER_COLUMNS.map((column) => (
            <SortableHeader
              key={column.key}
              column={column}
              sort={sort}
              onSortChange={onSortChange}
            />
          ))}
          {showActions && <th scope="col">Actions</th>}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, index) => (
          <tr key={row.id ?? row.log ?? index}>
            {ORDER_COLUMNS.map((column) => (
              <td key={column.key}>
                {column.key === 'artno' ? '' : displayValue(row[column.key])}
              </td>
            ))}
            {showActions && (
              <td>
                <Link
                  to={`${APP_PATHS.order}/${encodeURIComponent(row.log ?? '')}`}
                  className="text-decoration-none"
                  aria-label={`Edit order ${row.log ?? ''}`}
                  title="Edit order"
                >
                  <span aria-hidden="true">✎</span>
                </Link>
              </td>
            )}
          </tr>
        ))}
      </tbody>
    </Table>
  );

  return responsive ? <div className="table-responsive">{table}</div> : table;
}
