import {
  getStoredAuthUser,
} from "@/lib/auth";


export const DEFAULT_TENANT_ID =
  "tenant-demo-physics";


const STORAGE_KEY =
  "axiom_tenant_id";


export function getTenantId():
  string {
  if (
    typeof window === "undefined"
  ) {
    return DEFAULT_TENANT_ID;
  }

  const user =
    getStoredAuthUser();

  if (user?.tenant_id) {
    return user.tenant_id;
  }

  return (
    localStorage.getItem(
      STORAGE_KEY,
    )
    ?? DEFAULT_TENANT_ID
  );
}


export function setTenantId(
  tenantId: string,
): void {
  if (
    typeof window === "undefined"
  ) {
    return;
  }

  localStorage.setItem(
    STORAGE_KEY,
    tenantId,
  );
}