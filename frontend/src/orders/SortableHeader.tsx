import type { OrderColumn } from './columns';
import { nextSort, type SortState } from './sort';

type SortableHeaderProps = {
  column: OrderColumn;
  sort: SortState;
  onSortChange: (sort: SortState) => void;
};

export function SortableHeader({ column, sort, onSortChange }: SortableHeaderProps) {
  const direction = sort?.field === column.key ? sort.dir : null;
  const ariaSort = direction === 'asc'
    ? 'ascending'
    : direction === 'desc' ? 'descending' : 'none';
  const arrow = direction === 'asc' ? '▲' : direction === 'desc' ? '▼' : '';

  return (
    <th scope="col" aria-sort={ariaSort}>
      {column.sortable ? (
        <button
          type="button"
          className="orders-sort-button"
          onClick={() => onSortChange(nextSort(sort, column.key))}
        >
          {column.title}
          {arrow && <span className="ms-1" aria-hidden="true">{arrow}</span>}
        </button>
      ) : column.title}
    </th>
  );
}
