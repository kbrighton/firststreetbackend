import { zodResolver } from '@hookform/resolvers/zod';
import { useEffect, useMemo, useRef, useState } from 'react';
import { Button, Col, Form, Row, Spinner } from 'react-bootstrap';
import { useForm } from 'react-hook-form';
import { useSearchParams } from 'react-router-dom';
import { ApiError } from '../api/client';
import { useAlerts } from '../alerts/useAlerts';
import type { DueoutRange, Order } from '../api/orders';
import { OrdersTable } from '../orders/OrdersTable';
import { dueoutSchema, type DueoutFormValues } from '../orders/schemas';
import { useDueouts } from '../orders/queries';
import { sortRows, type SortState } from '../orders/sort';

export function DueoutsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { addAlert } = useAlerts();
  const startDate = searchParams.get('start_date') ?? '';
  const endDate = searchParams.get('end_date') ?? '';
  const hasAnyDate = searchParams.has('start_date') || searchParams.has('end_date');
  const rangeResult = dueoutSchema.safeParse({ start_date: startDate, end_date: endDate });
  const hasValidRange = hasAnyDate && rangeResult.success;
  const range: DueoutRange | undefined = hasValidRange
    ? { start_date: startDate, end_date: endDate }
    : undefined;
  const { data, error, isPending } = useDueouts(range, Boolean(range));
  const [sort, setSort] = useState<SortState>(null);
  const handledError = useRef<unknown>(null);
  const {
    register,
    handleSubmit,
    trigger,
    formState: { errors, isSubmitting },
  } = useForm<DueoutFormValues>({
    resolver: zodResolver(dueoutSchema),
    defaultValues: { start_date: startDate, end_date: endDate },
  });

  useEffect(() => {
    if (hasAnyDate && !hasValidRange) void trigger();
  }, [hasAnyDate, hasValidRange, trigger]);

  useEffect(() => {
    if (!error || handledError.current === error) return;
    handledError.current = error;
    if (error instanceof ApiError && error.status === 401) return;
    addAlert(error instanceof Error ? error.message : 'Could not load due-outs', 'danger');
  }, [addAlert, error]);

  const onSubmit = (values: DueoutFormValues) => {
    const query = new URLSearchParams();
    query.set('start_date', values.start_date);
    query.set('end_date', values.end_date);
    setSearchParams(query);
  };

  const rows = useMemo<Order[]>(() => sortRows(data ?? [], sort), [data, sort]);

  if (!hasValidRange) {
    return (
      <section>
        <h2>Search Form</h2>
        <Form noValidate onSubmit={handleSubmit(onSubmit)}>
          <Row>
            <Col xs={12} md={6}>
              <Form.Group className="mb-3" controlId="dueoutsStartDate">
                <Form.Label>Start Due Outs Date</Form.Label>
                <Form.Control
                  type="date"
                  isInvalid={Boolean(errors.start_date)}
                  {...register('start_date')}
                />
                <Form.Control.Feedback type="invalid">
                  {errors.start_date?.message}
                </Form.Control.Feedback>
              </Form.Group>
            </Col>
            <Col xs={12} md={6}>
              <Form.Group className="mb-3" controlId="dueoutsEndDate">
                <Form.Label>End Due Outs Date</Form.Label>
                <Form.Control
                  type="date"
                  isInvalid={Boolean(errors.end_date)}
                  {...register('end_date')}
                />
                <Form.Control.Feedback type="invalid">
                  {errors.end_date?.message}
                </Form.Control.Feedback>
              </Form.Group>
            </Col>
          </Row>
          <Button type="submit" disabled={isSubmitting}>Submit</Button>
        </Form>
      </section>
    );
  }

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