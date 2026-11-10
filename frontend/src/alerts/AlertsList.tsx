import { Alert } from 'react-bootstrap';
import { useAlerts } from './useAlerts';

export function AlertsList() {
  const { alerts, dismissAlert } = useAlerts();

  return (
    <div aria-live="polite" aria-relevant="additions">
      {alerts.map((alert) => (
        <Alert
          key={alert.id}
          variant={alert.variant}
          dismissible
          onClose={() => dismissAlert(alert.id)}
        >
          {alert.message}
        </Alert>
      ))}
    </div>
  );
}
