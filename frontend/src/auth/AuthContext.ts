import { createContext } from 'react';
import type { CurrentUser } from '../api/auth';

export type LoginCredentials = {
  username: string;
  password: string;
  remember: boolean;
};

export type AuthContextValue = {
  user: CurrentUser | null;
  isLoading: boolean;
  isAdmin: boolean;
  login: (credentials: LoginCredentials) => Promise<CurrentUser>;
  logout: () => Promise<void>;
};

export const AuthContext = createContext<AuthContextValue | null>(null);
