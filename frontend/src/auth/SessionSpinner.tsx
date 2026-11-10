import { Spinner } from 'react-bootstrap';

export function SessionSpinner() {
  return (
    <main className="container-fluid">
      <div className="d-flex justify-content-center py-4" role="status" aria-label="Loading session">
        <Spinner animation="border" aria-hidden="true" />
      </div>
    </main>
  );
}
