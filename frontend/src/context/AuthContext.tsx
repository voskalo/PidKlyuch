import React, { createContext, useContext, useEffect, useState } from 'react';
import type { User } from '../types/api';
import { api, getStoredToken, removeStoredToken } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  signin: (email: string, pass: string) => Promise<void>;
  signup: (email: string, pass: string, name?: string) => Promise<void>;
  googleLogin: (credential: string) => Promise<void>;
  signout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(getStoredToken());
  const [loading, setLoading] = useState<boolean>(true);

  const refreshUser = async () => {
    const currentToken = getStoredToken();
    if (!currentToken) {
      setUser(null);
      setToken(null);
      setLoading(false);
      return;
    }

    try {
      const userData = await api.getMe();
      setUser(userData);
      setToken(currentToken);
    } catch {
      removeStoredToken();
      setUser(null);
      setToken(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();

    const handleUnauthorized = () => {
      setUser(null);
      setToken(null);
    };

    window.addEventListener('auth:unauthorized', handleUnauthorized);
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized);
  }, []);

  const signin = async (email: string, pass: string) => {
    const res = await api.signin(email, pass);
    setUser(res.user);
    setToken(res.access_token);
  };

  const signup = async (email: string, pass: string, name?: string) => {
    const res = await api.signup(email, pass, name);
    setUser(res.user);
    setToken(res.access_token);
  };

  const googleLogin = async (credential: string) => {
    const res = await api.googleAuth(credential);
    setUser(res.user);
    setToken(res.access_token);
  };

  const signout = () => {
    removeStoredToken();
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        signin,
        signup,
        googleLogin,
        signout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
