import { zodResolver } from '@hookform/resolvers/zod';
import { Button, Form } from 'react-bootstrap';
import { useForm } from 'react-hook-form';
import { useLocation, useNavigate } from 'react-router-dom';
import { z } from 'zod';
import { ApiError } from '../api/client';
import { useAlerts } from '../alerts/useAlerts';
import { useAuth } from '../auth/useAuth';
import { safeNextPath } from '../auth/safeNextPath';

const loginSchema = z.object({
  username: z.string().superRefine((value, context) => {
    if (!value) {
      context.addIssue({ code: z.ZodIssueCode.custom, message: 'Username is required' });
    } else if (value.length < 3 || value.length > 64) {
      context.addIssue({ code: z.ZodIssueCode.custom, message: 'Username must be between 3 and 64 characters' });
    } else if (!/^[A-Za-z0-9_.-]+$/.test(value)) {
      context.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Username can only contain letters, numbers, underscores, periods, and hyphens',
      });
    }
  }).transform((value) => value.toLowerCase()),
  password: z.string().superRefine((value, context) => {
    if (!value) {
      context.addIssue({ code: z.ZodIssueCode.custom, message: 'Password is required' });
    } else if (value.length < 8) {
      context.addIssue({ code: z.ZodIssueCode.custom, message: 'Password must be at least 8 characters' });
    }
  }),
  remember: z.boolean(),
});

type LoginFormInput = z.input<typeof loginSchema>;
type LoginFormOutput = z.output<typeof loginSchema>;

export function LoginPage() {
  const { login } = useAuth();
  const { addAlert } = useAlerts();
  const location = useLocation();
  const navigate = useNavigate();
  const { register, handleSubmit, setError, formState: { errors, isSubmitting } } = useForm<
    LoginFormInput,
    unknown,
    LoginFormOutput
  >({
    resolver: zodResolver(loginSchema),
    defaultValues: { username: '', password: '', remember: false },
  });

  const onSubmit = async (values: LoginFormOutput) => {
    try {
      await login(values);
      const next = new URLSearchParams(location.search).get('next');
      navigate(safeNextPath(next, window.location.origin), { replace: true });
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        addAlert('Invalid username or password', 'danger');
        return;
      }

      if (error instanceof ApiError && error.fields) {
        let hasFieldErrors = false;
        for (const name of ['username', 'password'] as const) {
          const message = error.fields[name]?.[0];
          if (message) {
            setError(name, { type: 'server', message });
            hasFieldErrors = true;
          }
        }
        if (hasFieldErrors) {
          return;
        }
      }

      addAlert(error instanceof Error ? error.message : 'Unable to sign in', 'danger');
    }
  };

  return (
    <section>
      <h2>Login Page</h2>
      <Form noValidate onSubmit={handleSubmit(onSubmit)}>
        <Form.Group className="mb-3" controlId="loginUsername">
          <Form.Label>Username</Form.Label>
          <Form.Control
            type="text"
            autoComplete="username"
            isInvalid={Boolean(errors.username)}
            {...register('username')}
          />
          <Form.Control.Feedback type="invalid">{errors.username?.message}</Form.Control.Feedback>
        </Form.Group>

        <Form.Group className="mb-3" controlId="loginPassword">
          <Form.Label>Password</Form.Label>
          <Form.Control
            type="password"
            autoComplete="current-password"
            isInvalid={Boolean(errors.password)}
            {...register('password')}
          />
          <Form.Control.Feedback type="invalid">{errors.password?.message}</Form.Control.Feedback>
        </Form.Group>

        <Form.Group className="mb-3" controlId="loginRemember">
          <Form.Check type="checkbox" label="Remember Me" {...register('remember')} />
        </Form.Group>

        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Signing In…' : 'Sign In'}
        </Button>
      </Form>
    </section>
  );
}
