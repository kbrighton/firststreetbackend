import { useContext } from 'react';
import { AlertsContext } from './AlertsContext';

export function useAlerts() {
  const context = useContext(AlertsContext);
  if (!context) {
    throw new Error('useAlerts must be used within an AlertsProvider');
  }
  return context;
}
