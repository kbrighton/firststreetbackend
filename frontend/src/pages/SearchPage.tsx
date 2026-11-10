import { zodResolver } from '@hookform/resolvers/zod';
import { Button, Form } from 'react-bootstrap';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { APP_PATHS } from '../appPaths';
import { searchSchema, type SearchFormValues } from '../orders/schemas';

export function SearchPage() {
  const navigate = useNavigate();
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<SearchFormValues>({
    resolver: zodResolver(searchSchema),
    defaultValues: { cust: '', title: '' },
  });

  const onSubmit = ({ cust, title }: SearchFormValues) => {
    const query = new URLSearchParams();
    if (cust) query.set('cust', cust);
    if (title) query.set('title', title);
    navigate(`${APP_PATHS.orderSearch}?${query.toString()}`);
  };

  return (
    <section>
      <h2>Search Form</h2>
      <Form noValidate onSubmit={handleSubmit(onSubmit)}>
        <Form.Group className="mb-3" controlId="orderSearchCustomerId">
          <Form.Label>Customer ID</Form.Label>
          <Form.Control
            type="text"
            isInvalid={Boolean(errors.cust)}
            {...register('cust')}
          />
          <Form.Control.Feedback type="invalid">{errors.cust?.message}</Form.Control.Feedback>
        </Form.Group>

        <Form.Group className="mb-3" controlId="orderSearchTitle">
          <Form.Label>Title</Form.Label>
          <Form.Control
            type="text"
            isInvalid={Boolean(errors.title)}
            {...register('title')}
          />
          <Form.Control.Feedback type="invalid">{errors.title?.message}</Form.Control.Feedback>
        </Form.Group>

        <Button type="submit" disabled={isSubmitting}>Submit</Button>
      </Form>
    </section>
  );
}