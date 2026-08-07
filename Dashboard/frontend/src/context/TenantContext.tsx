"use client";

import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useMemo,
} from "react";

import {
  useAuth,
} from "@/context/AuthContext";

import {
  getTenantId,
} from "@/lib/tenant";


export interface TenantOption {
  id: string;
  label: string;
}


interface TenantContextValue {
  tenantId: string;

  setTenantId:
    (tenantId: string)
      => void;

  tenants:
    TenantOption[];

  refreshTenants:
    () => Promise<void>;
}


const TenantContext =
  createContext<
    TenantContextValue | null
  >(null);


export function TenantProvider({
  children,
}: {
  children: ReactNode;
}) {
  const {
    user,
  } = useAuth();


  const tenantId =
    user?.tenant_id
    ?? getTenantId();


  const tenants =
    useMemo(
      () => [
        {
          id: tenantId,

          label:
            user
              ?.institution_name
            ?? "Axiom AI",
        },
      ],
      [
        tenantId,
        user,
      ],
    );


  const setTenantId =
    useCallback(
      (
        _nextTenantId:
          string,
      ) => {
        // Tenant is controlled by authentication.
      },
      [],
    );


  const refreshTenants =
    useCallback(
      async () => {
        return;
      },
      [],
    );


  return (
    <TenantContext.Provider
      value={{
        tenantId,
        setTenantId,
        tenants,
        refreshTenants,
      }}
    >
      {children}
    </TenantContext.Provider>
  );
}


export function useTenant() {
  const context =
    useContext(
      TenantContext,
    );

  if (!context) {
    throw new Error(
      "useTenant must be used within TenantProvider",
    );
  }

  return context;
}