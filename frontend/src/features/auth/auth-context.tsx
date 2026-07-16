"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import * as authService from "@/services/auth";
import { clearAuthToken, getAuthToken, setAuthToken } from "@/lib/auth-storage";
import type { LoginCredentials, User } from "@/types/auth";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadUser = useCallback(async () => {
    const stored = getAuthToken();
    if (!stored) {
      setUser(null);
      setToken(null);
      setIsLoading(false);
      return;
    }
    setToken(stored);
    try {
      const me = await authService.getMe();
      setUser(me);
    } catch {
      clearAuthToken();
      setUser(null);
      setToken(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    queueMicrotask(() => {
      void loadUser();
    });
  }, [loadUser]);

  const login = useCallback(async (credentials: LoginCredentials) => {
    const result = await authService.login(credentials);
    setAuthToken(result.access_token);
    setToken(result.access_token);
    const me = await authService.getMe();
    setUser(me);
  }, []);

  const logout = useCallback(() => {
    clearAuthToken();
    setUser(null);
    setToken(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(token && user),
      isLoading,
      login,
      logout,
      loadUser,
    }),
    [user, token, isLoading, login, logout, loadUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuthContext must be used within AuthProvider");
  return ctx;
}
