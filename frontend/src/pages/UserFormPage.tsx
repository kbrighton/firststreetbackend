import { zodResolver } from '@hookform/resolvers/zod';
import { useQueryClient } from '@tanstack/react-query';
import { useEffect, useRef } from 'react';
import { Button, Form, Spinner } from 'react-bootstrap';
import { useForm } from 'react-hook-form';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ApiError } from '../api/client';
import { createUser, updateUser, type User, type UserInput } from '../api/users';
import { useAlerts } from '../alerts/useAlerts';
import { useAuth } from '../auth/useAuth';
import { APP_PATHS } from '../appPaths';
import { userCreateSchema, userEditSchema, type UserFormValues } from '../users/schemas';
import { userKeys, useUser } from '../users/queries';

const USER_FORM_FIELDS = new Set(['username', 'email', 'password', 'role']);
const EMPTY_USER: UserFormValues = {
  username: '',
  email: '',
  password: '',
  role: 'user',
};

function userToForm(user: User): UserFormValues {
  return {
    username: user.username ?? '',
    email: user.email ?? '',
    password: '',
    role: user.role === 'admin' ? 'admin' : 'user',
  };
}

export function UserFormPage() {
  const { userId } = useParams();
  const isCreating = userId === undefined;
  const parsedUserId = Number(userId);
  const isValidUserId = Number.isSafeInteger(parsedUserId) && parsedUserId > 0;
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { addAlert } = useAlerts();
  const { user: currentUser, isAdmin } = useAuth();
  const isForbidden = !isCreating && !isAdmin && currentUser?.id !== parsedUserId;
  const { data: fetchedUser, error, isPending } = useUser(
    parsedUserId,
    !isCreating && isAdmin && isValidUserId,
  );
  const targetUser = isCreating ? undefined : isAdmin ? fetchedUser : currentUser ?? undefined;
  const handledError = useRef<unknown>(null);
  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<UserFormValues>({
    resolver: zodResolver(isCreating ? userCreateSchema : userEditSchema),
    defaultValues: EMPTY_USER,
  });

  useEffect(() => {
    if (isCreating || !isAdmin || isValidUserId) return;
    addAlert('User not found', 'danger');
    navigate(APP_PATHS.users, { replace: true });
  }, [addAlert, isAdmin, isCreating, isValidUserId, navigate]);

  useEffect(() => {
    if (!isForbidden) return;
    addAlert('You can only manage your own profile', 'danger');
    navigate(APP_PATHS.users, { replace: true });
  }, [addAlert, isForbidden, navigate]);

  useEffect(() => {
    if (!targetUser || isCreating) return;
    reset(userToForm(targetUser));
  }, [isCreating, reset, targetUser]);

  useEffect(() => {
    if (!error || handledError.current === error) return;
    handledError.current = error;
    if (error instanceof ApiError && error.status === 401) return;
    if (error instanceof ApiError && error.status === 404) {
      addAlert('User not found', 'danger');
      navigate(APP_PATHS.users, { replace: true });
      return;
    }
    addAlert(error instanceof Error ? error.message : 'Could not load this user', 'danger');
  }, [addAlert, error, navigate]);

  const showSubmitError = (submissionError: unknown) => {
    if (submissionError instanceof ApiError && submissionError.status === 401) return;
    if (submissionError instanceof ApiError && submissionError.fields) {
      let mappedFieldError = false;
      for (const [field, messages] of Object.entries(submissionError.fields)) {
        if (!USER_FORM_FIELDS.has(field) || !messages[0]) continue;
        setError(field as keyof UserFormValues, { type: 'server', message: messages[0] });
        mappedFieldError = true;
      }
      if (mappedFieldError) return;
    }
    addAlert(
      submissionError instanceof Error ? submissionError.message : 'Could not save this user',
      'danger',
    );
  };

  const onSubmit = async (values: UserFormValues) => {
    try {
      if (isCreating) {
        const payload: UserInput = {
          username: values.username,
          email: values.email,
          password: values.password,
          role: values.role as UserInput['role'],
        };
        const created = await createUser(payload);
        await queryClient.invalidateQueries({ queryKey: userKeys.all });
        addAlert(`User ${created.username ?? values.username} created successfully`, 'success');
      } else {
        const payload: Partial<UserInput> = {
          username: values.username,
          email: values.email,
        };
        if (values.password) payload.password = values.password;
        if (isAdmin) payload.role = values.role as UserInput['role'];
        await updateUser(parsedUserId, payload);
        await queryClient.invalidateQueries({ queryKey: userKeys.all });
        await queryClient.invalidateQueries({ queryKey: ['auth', 'me'] });
        addAlert(`User ${values.username} updated successfully`, 'success');
      }
      navigate(APP_PATHS.users, { replace: true });
    } catch (submissionError) {
      showSubmitError(submissionError);
    }
  };

  if (!isCreating && isForbidden) return null;
  if (!isCreating && isAdmin && !isValidUserId) return null;
  if (!isCreating && isAdmin && isPending) {
    return (
      <section>
        <h2>Edit User</h2>
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading user…</span>
        </Spinner>
      </section>
    );
  }
  if (!isCreating && !targetUser) return null;

  return (
    <section>
      <h2>{isCreating ? 'New User' : `Edit User: ${targetUser?.username ?? ''}`}</h2>
      <Form noValidate onSubmit={handleSubmit(onSubmit)}>
        <Form.Group className="mb-3" controlId="userForm-username">
          <Form.Label>Username</Form.Label>
          <Form.Control type="text" isInvalid={Boolean(errors.username)} {...register('username')} />
          <Form.Control.Feedback type="invalid">{errors.username?.message}</Form.Control.Feedback>
        </Form.Group>
        <Form.Group className="mb-3" controlId="userForm-email">
          <Form.Label>Email</Form.Label>
          <Form.Control type="email" isInvalid={Boolean(errors.email)} {...register('email')} />
          <Form.Control.Feedback type="invalid">{errors.email?.message}</Form.Control.Feedback>
        </Form.Group>
        <Form.Group className="mb-3" controlId="userForm-password">
          <Form.Label>Password</Form.Label>
          <Form.Control
            type="password"
            autoComplete="new-password"
            isInvalid={Boolean(errors.password)}
            {...register('password')}
          />
          <Form.Control.Feedback type="invalid">{errors.password?.message}</Form.Control.Feedback>
          {!isCreating && <Form.Text>Leave blank to keep the current password.</Form.Text>}
        </Form.Group>
        {isAdmin && (
          <Form.Group className="mb-3" controlId="userForm-role">
            <Form.Label>Role</Form.Label>
            <Form.Select isInvalid={Boolean(errors.role)} {...register('role')}>
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </Form.Select>
            <Form.Control.Feedback type="invalid">{errors.role?.message}</Form.Control.Feedback>
          </Form.Group>
        )}
        <div className="d-flex gap-2">
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Saving…' : 'Submit'}
          </Button>
          <Link className="btn btn-secondary" to={APP_PATHS.users}>Back to List</Link>
        </div>
      </Form>
    </section>
  );
}
