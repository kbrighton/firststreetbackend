import { zodResolver } from '@hookform/resolvers/zod';
import { useQueryClient } from '@tanstack/react-query';
import { useEffect, useRef, useState } from 'react';
import { Button, Col, Form, Modal, Row, Spinner } from 'react-bootstrap';
import { useForm } from 'react-hook-form';
import { useNavigate, useParams } from 'react-router-dom';
import { ApiError } from '../api/client';
import {
  createOrder,
  deleteOrder,
  updateOrder,
  type OrderDetail,
  type OrderInput,
} from '../api/orders';
import { useAlerts } from '../alerts/useAlerts';
import { useAuth } from '../auth/useAuth';
import { APP_PATHS } from '../appPaths';
import { orderKeys, useOrderByLog } from '../orders/queries';
import { orderFormSchema, type OrderFormValues } from '../orders/schemas';

type EditableField = Exclude<keyof OrderFormValues, 'logtype' | 'rush'>;
type OrderField = {
  name: keyof OrderFormValues;
  label: string;
  type: 'text' | 'date' | 'number' | 'select' | 'checkbox';
};

const ORDER_FIELDS: OrderField[] = [
  { name: 'log', label: 'LOG#', type: 'text' },
  { name: 'cust', label: 'Customer#', type: 'text' },
  { name: 'title', label: 'Title', type: 'text' },
  { name: 'datin', label: 'Date In', type: 'date' },
  { name: 'artout', label: 'Art Due Out', type: 'date' },
  { name: 'dueout', label: 'Order Due Out', type: 'date' },
  { name: 'print_n', label: 'Quantity', type: 'number' },
  { name: 'artlo', label: 'Art Log', type: 'text' },
  { name: 'rush', label: 'RUSH?', type: 'checkbox' },
  { name: 'prior', label: 'Priority', type: 'number' },
  { name: 'logtype', label: 'Log Type', type: 'select' },
  { name: 'colorf', label: '# of Colors', type: 'number' },
  { name: 'ref_artlo', label: 'Art Reference', type: 'text' },
  { name: 'howship', label: 'How Shipped', type: 'number' },
  { name: 'artno', label: 'Artist ID', type: 'text' },
  { name: 'datout', label: 'DATOUT', type: 'date' },
];

const ORDER_FORM_FIELDS = new Set<string>([
  'log', 'cust', 'title', 'datin', 'artout', 'dueout', 'print_n', 'artlo',
  'rush', 'prior', 'logtype', 'colorf', 'ref_artlo', 'howship', 'artno', 'datout',
]);

const EMPTY_ORDER: OrderFormValues = {
  log: '',
  cust: '',
  title: '',
  datin: '',
  artout: '',
  dueout: '',
  print_n: '',
  artlo: '',
  rush: false,
  prior: '',
  logtype: '',
  colorf: '',
  ref_artlo: '',
  howship: '',
  artno: '',
  datout: '',
};

function formString(value: string | number | boolean | null | undefined): string {
  if (value === null || value === undefined) return '';
  return String(value);
}

function orderToForm(order: OrderDetail): OrderFormValues {
  return {
    log: formString(order.log),
    cust: formString(order.cust),
    title: formString(order.title),
    datin: formString(order.datin),
    artout: formString(order.artout),
    dueout: formString(order.dueout),
    print_n: formString(order.print_n),
    artlo: formString(order.artlo),
    rush: Boolean(order.rush),
    prior: formString(order.prior),
    logtype: formString(order.logtype),
    colorf: formString(order.colorf),
    ref_artlo: formString(order.ref_artlo),
    howship: formString(order.howship),
    artno: formString(order.artno),
    datout: formString(order.datout),
  };
}

function nullableString(value: string): string | null {
  return value === '' ? null : value;
}

function nullableNumber(value: string): number | null {
  return value === '' ? null : Number(value);
}

function toOrderInput(values: OrderFormValues): OrderInput {
  return {
    log: values.log,
    cust: values.cust,
    title: values.title,
    datin: values.datin,
    logtype: values.logtype as OrderInput['logtype'],
    artout: nullableString(values.artout),
    dueout: nullableString(values.dueout),
    print_n: nullableNumber(values.print_n),
    artlo: nullableString(values.artlo),
    rush: values.rush,
    prior: nullableNumber(values.prior),
    colorf: nullableNumber(values.colorf),
    ref_artlo: nullableString(values.ref_artlo),
    howship: nullableNumber(values.howship),
    artno: nullableString(values.artno),
    datout: nullableString(values.datout),
  };
}

function displayTimestamp(value: string | null | undefined): string {
  if (!value) return 'N/A';
  return value.replace('T', ' ').slice(0, 16);
}

export function OrderFormPage() {
  const { logId = '' } = useParams();
  const isEditing = Boolean(logId);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { addAlert } = useAlerts();
  const { isAdmin } = useAuth();
  const { data: order, error, isPending } = useOrderByLog(logId);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const handledError = useRef<unknown>(null);
  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<OrderFormValues>({
    resolver: zodResolver(orderFormSchema),
    defaultValues: EMPTY_ORDER,
  });

  useEffect(() => {
    if (order) reset(orderToForm(order));
  }, [order, reset]);

  useEffect(() => {
    if (order !== null || !isEditing) return;
    addAlert(`Order with log number ${logId} not found`, 'danger');
    navigate(APP_PATHS.search, { replace: true });
  }, [addAlert, isEditing, logId, navigate, order]);

  useEffect(() => {
    if (!error || handledError.current === error) return;
    handledError.current = error;
    if (error instanceof ApiError && error.status === 401) return;
    addAlert(error instanceof Error ? error.message : 'Could not load this order', 'danger');
  }, [addAlert, error]);

  const showSubmitError = (submissionError: unknown) => {
    if (submissionError instanceof ApiError && submissionError.status === 401) return;
    if (submissionError instanceof ApiError && submissionError.fields) {
      let mappedFieldError = false;
      for (const [field, messages] of Object.entries(submissionError.fields)) {
        if (!ORDER_FORM_FIELDS.has(field) || !messages[0]) continue;
        setError(field as keyof OrderFormValues, { type: 'server', message: messages[0] });
        mappedFieldError = true;
      }
      if (mappedFieldError) return;
    }
    addAlert(
      submissionError instanceof Error ? submissionError.message : 'Could not save this order',
      'danger',
    );
  };

  const onSubmit = async (values: OrderFormValues) => {
    try {
      if (isEditing && order?.id !== undefined) {
        await updateOrder(order.id, toOrderInput(values));
        await queryClient.invalidateQueries({ queryKey: orderKeys.all });
        addAlert('Order updated successfully', 'success');
        return;
      }
      const created = await createOrder(toOrderInput(values));
      await queryClient.invalidateQueries({ queryKey: orderKeys.all });
      addAlert('Order created successfully', 'success');
      navigate(`${APP_PATHS.order}/${encodeURIComponent(created.log ?? values.log)}`, { replace: true });
    } catch (submissionError) {
      showSubmitError(submissionError);
    }
  };

  const onDelete = async () => {
    if (order?.id === undefined) return;
    setIsDeleting(true);
    try {
      await deleteOrder(order.id);
      await queryClient.invalidateQueries({ queryKey: orderKeys.all });
      setConfirmDelete(false);
      addAlert('Order deleted successfully', 'success');
      navigate(APP_PATHS.search, { replace: true });
    } catch (deleteError) {
      showSubmitError(deleteError);
    } finally {
      setIsDeleting(false);
    }
  };

  if (isEditing && isPending) {
    return (
      <section>
        <h2>Order Form</h2>
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading order…</span>
        </Spinner>
      </section>
    );
  }
  if (isEditing && !order) return null;

  const legacyBaseUrl = (import.meta.env.VITE_LEGACY_BASE_URL || 'http://localhost:5000').replace(/\/$/, '');
  const orderLog = order?.log ?? logId;

  return (
    <section>
      <h2>Order Form</h2>
      {order && isAdmin && (
        <div className="mb-3">
          <small className="text-muted">
            Created by: {order.created_by_username || 'Unknown'} on {displayTimestamp(order.created_at)}
            <br />
            Last updated by: {order.updated_by_username || 'Unknown'} on {displayTimestamp(order.updated_at)}
          </small>
        </div>
      )}
      <Form noValidate onSubmit={handleSubmit(onSubmit)}>
        <Row className="g-3">
          {ORDER_FIELDS.map(({ name, label, type }) => (
            <Col key={name} xs={12} md={6} lg={4}>
              <Form.Group controlId={`orderForm-${name}`}>
                {type === 'checkbox' ? (
                  <>
                    <Form.Check
                      id={`orderForm-${name}`}
                      label={label}
                      isInvalid={Boolean(errors.rush)}
                      {...register('rush')}
                    />
                    {errors.rush?.message && (
                      <div className="invalid-feedback d-block">{errors.rush.message}</div>
                    )}
                  </>
                ) : (
                  <>
                    <Form.Label>{label}</Form.Label>
                    {type === 'select' ? (
                      <Form.Select isInvalid={Boolean(errors.logtype)} {...register('logtype')}>
                        <option value="">Choose a log type</option>
                        <option value="TR">Transfer</option>
                        <option value="DP">Direct Print</option>
                        <option value="AA">Art Approval</option>
                        <option value="VG">Vinyl</option>
                        <option value="DG">Digital Graphics</option>
                        <option value="GM">General Maintenance</option>
                        <option value="DTF">Direct to Film</option>
                        <option value="PP">Promotional Products</option>
                      </Form.Select>
                    ) : (
                      <Form.Control
                        type={type}
                        step={type === 'number' ? '1' : undefined}
                        isInvalid={Boolean(errors[name])}
                        {...register(name as EditableField)}
                      />
                    )}
                    <Form.Control.Feedback type="invalid">
                      {type === 'select' ? errors.logtype?.message : errors[name]?.message}
                    </Form.Control.Feedback>
                  </>
                )}
              </Form.Group>
            </Col>
          ))}
        </Row>
        <div className="d-flex gap-2 mt-3">
          <Button type="submit" disabled={isSubmitting || isDeleting}>
            {isSubmitting ? 'Saving…' : 'Submit'}
          </Button>
          {order && (
            <Button
              type="button"
              variant="danger"
              disabled={isSubmitting || isDeleting}
              onClick={() => setConfirmDelete(true)}
            >
              Delete Order
            </Button>
          )}
        </div>
      </Form>
      {order && (
        <p className="mt-3">
          <a href={`${legacyBaseUrl}/order/${encodeURIComponent(orderLog)}`}>
            Edit in classic app
          </a>
        </p>
      )}
      <Modal show={confirmDelete} onHide={() => setConfirmDelete(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Delete order?</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          Delete order {orderLog}? This action cannot be undone.
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" disabled={isDeleting} onClick={() => setConfirmDelete(false)}>
            Cancel
          </Button>
          <Button variant="danger" disabled={isDeleting} onClick={onDelete}>
            {isDeleting ? 'Deleting…' : 'Delete order'}
          </Button>
        </Modal.Footer>
      </Modal>
    </section>
  );
}
