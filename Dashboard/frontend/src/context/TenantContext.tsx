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

import { listTenants, TenantSummary } from "@/lib/api";
import {
  AVAILABLE_TENANTS,
  getTenantId,
  setTenantId as persistTenantId,
} from "@/lib/tenant";

export interface TenantOption {
  id: string;
  label: string;
}

interface TenantContextValue {
  tenantId: string;
  setTenantId: (tenantId: string) => void;
  tenants: TenantOption[];
  refreshTenants: () => Promise<void>;
}

const TenantContext = createContext<TenantContextValue | null>(null);

function toTenantOptions(rows: TenantSummary[]): TenantOption[] {
  return rows.map((tenant) => ({
    id: tenant.id,
    label: tenant.name,
  }));
}

export function TenantProvider({ children }: { children: ReactNode }) {
  const [tenantId, setTenantIdState] = useState(getTenantId);
  const [tenants, setTenants] = useState<TenantOption[]>(
    AVAILABLE_TENANTS.map((tenant) => ({
      id: tenant.id,
      label: tenant.label,
    })),
  );

  const refreshTenants = useCallback(async () => {
    try {
      const rows = await listTenants();
      if (rows.length > 0) {
        setTenants(toTenantOptions(rows));
      }
    } catch (requestError) {
      console.error("Could not load tenant list:", requestError);
    }
  }, []);

  useEffect(() => {
    setTenantIdState(getTenantId());
    void refreshTenants();
  }, [refreshTenants]);

  const setTenantId = useCallback((nextTenantId: string) => {
    persistTenantId(nextTenantId);
    setTenantIdState(nextTenantId);
  }, []);

  const value = useMemo(
    () => ({
      tenantId,
      setTenantId,
      tenants,
      refreshTenants,
    }),
    [tenantId, setTenantId, tenants, refreshTenants],
  );

  return (
    <TenantContext.Provider value={value}>{children}</TenantContext.Provider>
  );
}

export function useTenant() {
  const context = useContext(TenantContext);

  if (!context) {
    throw new Error("useTenant must be used within TenantProvider");
  }

  return context;
}
