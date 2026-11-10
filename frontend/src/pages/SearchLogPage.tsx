import { zodResolver } from '@hookform/resolvers/zod';
import { Button, Form, Spinner } from 'react-bootstrap';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { ApiError } from '../api/client';
import { useAlerts } from '../alerts/useAlerts';
import { getOrderByLog } from '../api/orders';
import { APP_PATHS } from '../appPaths';
import { logSearchSchema, type LogSearchValues } from '../orders/schemas';

export function SearchLogPage() {
  const navigate = useNavigate();
  const { addAlert } = useAlerts();
  const { register, handleSubmit, setError, formState: { errors, isSubmitting } } = useForm<LogSearchValues>({
    resolver: zodResolver(logSearchSchema),
    defaultValues: { log: '' },
  });

  const onSubmit = async ({ log }: LogSearchValues) => {
    const requestedLog = log ?? '';
    try {
      const order = await getOrderByLog(requestedLog);
      if (!order) {
        addAlert('Log number does not exist', 'danger');
        return;
      }
      navigate(`${APP_PATHS.order}/${encodeURIComponent(order.log ?? requestedLog)}`);
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) return;
      if (error instanceof ApiError && error.fields?.log?.[0]) {
        setError('log', { type: 'server', message: error.fields.log[0] });
        return;
      }
      addAlert(error instanceof Error ? error.message : 'Could not search for that log number', 'danger');
    }
  };

  return (
    <section>
      <h2>Search Form</h2>
      <Form noValidate onSubmit={handleSubmit(onSubmit)}>
        <Form.Group className="mb-3" controlId="orderSearchLog">
          <Form.Label>LOG #</Form.Label>
          <Form.Control
            type="text"
            isInvalid={Boolean(errors.log)}
            {...register('log')}
          />
          <Form.Control.Feedback type="invalid">{errors.log?.message}</Form.Control.Feedback>
        </Form.Group>

        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? <Spinner animation="border" size="sm" aria-label="Searching" /> : 'Submit'}
        </Button>
      </Form>
    </section>
  );
}