import { useEffect, useRef } from 'react';
import { Spinner } from 'react-bootstrap';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { ApiError } from '../api/client';
import { useAlerts } from '../alerts/useAlerts';
import { APP_PATHS } from '../appPaths';
import { OrdersPagination } from '../orders/OrdersPagination';
import { OrdersTable } from '../orders/OrdersTable';
import { useOrderSearch } from '../orders/queries';
import { parseSortParam, toSortParam, type SortState } from '../orders/sort';

function parsePage(value: string | null): number | null {
  if (value === null) return 1;
  if (!/^[1-9]\d*$/.test(value)) return null;
  const page = Number(value);
  return Number.isSafeInteger(page) ? page : null;
}

export function SearchResultsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const { addAlert } = useAlerts();
  const pageParam = searchParams.get('page');
  const pageValue = parsePage(pageParam);
  const page = pageValue ?? 1;
  const sortParam = searchParams.get('sort');
  const sort = parseSortParam(sortParam ?? undefined);
  const malformedPage = pageParam !== null && pageValue === null;
  const malformedSort = searchParams.has('sort') && sort === null;
  const cust = searchParams.has('cust') ? searchParams.get('cust') ?? '' : undefined;
  const title = searchParams.has('title') ? searchParams.get('title') ?? '' : undefined;
  const { data, error, isPending } = useOrderSearch({
    cust,
    title,
    page,
    perPage: 20,
    sort: toSortParam(sort),
  });
  const handledError = useRef<unknown>(null);
  const handledEmptyResults = useRef(false);

  useEffect(() => {
    if (!malformedPage && !malformedSort) return;
    const nextParams = new URLSearchParams(searchParams);
    if (malformedPage) nextParams.delete('page');
    if (malformedSort) nextParams.delete('sort');
    setSearchParams(nextParams, { replace: true });
  }, [malformedPage, malformedSort, searchParams, setSearchParams]);

  useEffect(() => {
    if (!error || handledError.current === error) return;
    handledError.current = error;
    if (error instanceof ApiError && error.status === 401) return;
    addAlert(error instanceof Error ? error.message : 'Could not load orders', 'danger');
  }, [addAlert, error]);

  useEffect(() => {
    if (!data || data.total !== 0 || handledEmptyResults.current) return;
    handledEmptyResults.current = true;
    addAlert('Could not find any orders that match', 'danger');
    navigate(APP_PATHS.search, { replace: true });
  }, [addAlert, data, navigate]);

  const changePage = (nextPage: number) => {
    const nextParams = new URLSearchParams(searchParams);
    if (nextPage === 1) nextParams.delete('page');
    else nextParams.set('page', String(nextPage));
    setSearchParams(nextParams);
  };

  const changeSort = (nextSort: SortState) => {
    const nextParams = new URLSearchParams(searchParams);
    const nextSortParam = toSortParam(nextSort);
    if (nextSortParam) nextParams.set('sort', nextSortParam);
    else nextParams.delete('sort');
    nextParams.delete('page');
    setSearchParams(nextParams);
  };

  return (
    <section>
      <h2>Search</h2>
      {isPending ? (
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading orders…</span>
        </Spinner>
      ) : (
        <>
          <OrdersTable
            rows={data?.data ?? []}
            caption="Searches"
            sort={sort}
            onSortChange={changeSort}
            showActions
          />
          <OrdersPagination
            page={data?.page ?? page}
            pages={data?.pages ?? 0}
            onPageChange={changePage}
          />
        </>
      )}
    </section>
  );
}