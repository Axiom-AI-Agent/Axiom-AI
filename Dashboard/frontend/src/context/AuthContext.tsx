"use client";

import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  clearAuthSession,
  getStoredAuthUser,
  saveAuthSession,
} from "@/lib/auth";

import {
  getMe,
} from "@/lib/auth-api";

import type {
  AuthResponse,
  AuthUser,
} from "@/types/auth";


interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  authenticated: boolean;
  setSession:
    (response: AuthResponse)
      => void;
  logout:
    () => void;
  refreshUser:
    () => Promise<void>;
}


const AuthContext =
  createContext<
    AuthContextValue | null
  >(null);


export function AuthProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [
    user,
    setUser,
  ] = useState<AuthUser | null>(
    null,
  );

  const [
    loading,
    setLoading,
  ] = useState(true);


  const refreshUser =
    useCallback(
      async () => {
        const storedUser =
          getStoredAuthUser();

        if (!storedUser) {
          setUser(null);
          setLoading(false);
          return;
        }

        try {
          const verifiedUser =
            await getMe();

          setUser(
            verifiedUser,
          );

        } catch {
          clearAuthSession();
          setUser(null);

        } finally {
          setLoading(false);
        }
      },
      [],
    );


  useEffect(() => {
    void refreshUser();
  }, [
    refreshUser,
  ]);


  const setSession =
    useCallback(
      (
        response:
          AuthResponse,
      ) => {
        saveAuthSession(
          response,
        );

        setUser(
          response.user,
        );
      },
      [],
    );


  const logout =
    useCallback(
      () => {
        clearAuthSession();

        setUser(null);
      },
      [],
    );


  const value =
    useMemo(
      () => ({
        user,
        loading,
        authenticated:
          Boolean(user),
        setSession,
        logout,
        refreshUser,
      }),
      [
        user,
        loading,
        setSession,
        logout,
        refreshUser,
      ],
    );


  return (
    <AuthContext.Provider
      value={value}
    >
      {children}
    </AuthContext.Provider>
  );
}


export function useAuth() {
  const context =
    useContext(
      AuthContext,
    );

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider",
    );
  }

  return context;
}