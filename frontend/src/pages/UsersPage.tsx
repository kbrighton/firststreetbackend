import { useEffect, useRef } from 'react';
import { Spinner, Table } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { ApiError } from '../api/client';
import type { User } from '../api/users';
import { useAlerts } from '../alerts/useAlerts';
import { useAuth } from '../auth/useAuth';
import { useUsers } from '../users/queries';

function createdAt(value: string | null | undefined): string {
  return value ? value.replace('T', ' ').slice(0, 16) : '';
}

export function UsersPage() {
  const { user, isAdmin } = useAuth();
  const { addAlert } = useAlerts();
  const { data: allUsers, error, isPending } = useUsers(isAdmin);
  const handledError = useRef<unknown>(null);
  const users: User[] = isAdmin ? allUsers ?? [] : user ? [user] : [];

  useEffect(() => {
    if (!error || handledError.current === error) return;
    handledError.current = error;
    if (error instanceof ApiError && error.status === 401) return;
    addAlert(error instanceof Error ? error.message : 'Could not load users', 'danger');
  }, [addAlert, error]);

  return (
    <section>
      <h2>{isAdmin ? 'User Management' : 'Manage My Profile'}</h2>
      {isAdmin && (
        <p className="mb-3">
          <Link className="btn btn-primary" to="/user/new">Create New User</Link>
        </p>
      )}
      {isAdmin && isPending ? (
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading users…</span>
        </Spinner>
      ) : (
        <Table striped className="mb-0">
          <thead>
            <tr>
              <th scope="col">Username</th>
              <th scope="col">Email</th>
              <th scope="col">Role</th>
              <th scope="col">Created At</th>
              <th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((listedUser) => (
              <tr key={listedUser.id ?? listedUser.username}>
                <td>{listedUser.username}</td>
                <td>{listedUser.email}</td>
                <td>{listedUser.role}</td>
                <td>{createdAt(listedUser.created_at)}</td>
                <td>
                  {listedUser.id !== undefined && (
                    <Link
                      className="btn btn-info btn-sm"
                      to={`/user/${listedUser.id}/edit`}
                    >
                      Edit
                    </Link>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </section>
  );
}
