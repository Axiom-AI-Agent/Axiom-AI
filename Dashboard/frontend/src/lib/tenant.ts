export const DEFAULT_TENANT_ID = "tenant-demo-physics";

export const AVAILABLE_TENANTS = [
  { id: DEFAULT_TENANT_ID, label: "Demo Physics Academy" },
  { id: "tenant-demo-chemistry", label: "Demo Chemistry Institute" },
] as const;

const STORAGE_KEY = "axiom_tenant_id";

export function getTenantId(): string {
  if (typeof window === "undefined") {
    return DEFAULT_TENANT_ID;
  }

  return localStorage.getItem(STORAGE_KEY) ?? DEFAULT_TENANT_ID;
}

export function setTenantId(tenantId: string): void {
  if (typeof window === "undefined") {
    return;
  }

  localStorage.setItem(STORAGE_KEY, tenantId);
}
