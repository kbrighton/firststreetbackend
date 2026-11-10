import { useCallback, useRef, useState } from 'react';
import { AlertsContext, type AlertMessage, type AlertVariant } from './AlertsContext';

export function AlertsProvider({ children }: { children: React.ReactNode }) {
  const [alerts, setAlerts] = useState<AlertMessage[]>([]);
  const nextId = useRef(0);

  const addAlert = useCallback((message: string, variant: AlertVariant = 'info') => {
    nextId.current += 1;
    setAlerts((current) => [...current, { id: nextId.current, message, variant }]);
  }, []);

  const dismissAlert = useCallback((id: number) => {
    setAlerts((current) => current.filter((alert) => alert.id !== id));
  }, []);

  return (
    <AlertsContext.Provider value={{ addAlert, alerts, dismissAlert }}>
      {children}
    </AlertsContext.Provider>
  );
}
