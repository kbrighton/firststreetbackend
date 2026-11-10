import { createContext } from 'react';

export type AlertVariant = 'success' | 'danger' | 'info';

export type AlertMessage = {
  id: number;
  message: string;
  variant: AlertVariant;
};

type AlertsContextValue = {
  addAlert: (message: string, variant?: AlertVariant) => void;
  alerts: AlertMessage[];
  dismissAlert: (id: number) => void;
};

export const AlertsContext = createContext<AlertsContextValue | null>(null);
