// frontend/src/context/AuthContext.tsx
import { createContext, useState, useEffect, ReactNode } from 'react';
import { User } from '../../../../shared/types';
import api from '../services/api';

interface AuthContextType {
  user: User | null;
  setUser: (user: User | null) => void;
  loading: boolean;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkUser = async () => {
      const token = localStorage.getItem('accessToken');
      if (token) {
        try {
          // A better approach would be to have a /me endpoint to verify the token and get user data
          // For now, we'll try to refresh the token to check validity
          const response = await api.post('/auth/refresh-token');
          localStorage.setItem('accessToken', response.data.accessToken);
          // Here you would typically fetch user data again
          // For simplicity, we'll assume the user is valid if refresh succeeds
          // In a real app, decode the token or fetch from a /me endpoint
        } catch (error) {
          console.error('Session expired, please login again.');
          localStorage.removeItem('accessToken');
          setUser(null);
        }
      }
      setLoading(false);
    };
    checkUser();
  }, []);

  const logout = () => {
    api.post('/auth/logout');
    localStorage.removeItem('accessToken');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, setUser, loading, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
