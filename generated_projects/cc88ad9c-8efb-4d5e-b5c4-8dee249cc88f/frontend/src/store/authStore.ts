import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { PublicUser } from '../../../shared/types/user';

interface AuthState {
  user: PublicUser | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  login: (user: PublicUser, accessToken: string) => void;
  logout: () => void;
  setTokens: (accessToken: string) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      login: (user, accessToken) =>
        set({
          user,
          accessToken,
          isAuthenticated: true,
        }),
      logout: () =>
        set({
          user: null,
          accessToken: null,
          isAuthenticated: false,
        }),
      setTokens: (accessToken) =>
        set({
          accessToken,
        }),
    }),
    {
      name: 'auth-storage', // unique name
    }
  )
);
