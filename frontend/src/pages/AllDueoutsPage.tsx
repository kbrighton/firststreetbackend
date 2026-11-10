import { useEffect, useMemo, useRef, useState } from 'react';
import { Spinner } from 'react-bootstrap';
import { ApiError } from '../api/client';
import { useAlerts } from '../alerts/useAlerts';
import type { Order } from '../api/orders';
import { OrdersTable } from '../orders/OrdersTable';
import { useDueouts } from '../orders/queries';
import { sortRows, type SortState } from '../orders/sort';

export function AllDueoutsPage() {
  const { addAlert } = useAlerts();
  const { data, error, isPending } = useDueouts();
  const [sort, setSort] = useState<SortState>(null);
  const handledError = useRef<unknown>(null);

  useEffect(() => {
    if (!error || handledError.current === error) return;
    handledError.current = error;
    if (error instanceof ApiError && error.status === 401) return;
    addAlert(error instanceof Error ? error.message : 'Could not load due-outs', 'danger');
  }, [addAlert, error]);

  const rows = useMemo<Order[]>(() => sortRows(data ?? [], sort), [data, sort]);

  return (
    <section>
      <h2>Due Outs</h2>
      {isPending ? (
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading due-outs…</span>
        </Spinner>
      ) : (
        <OrdersTable
          rows={rows}
          caption="Due Outs"
          sort={sort}
          onSortChange={setSort}
          responsive
        />
      )}
    </section>
  );
}