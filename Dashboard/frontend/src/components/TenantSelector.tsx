"use client";

import { useTenant } from "@/context/TenantContext";
import { selectClass } from "@/lib/ui";

export default function TenantSelector() {
  const { tenantId, setTenantId, tenants } = useTenant();

  return (
    <label className="flex items-center gap-2 text-sm text-muted">
      <span className="hidden font-medium sm:inline">Tenant</span>
      <select
        value={tenantId}
        onChange={(event) => setTenantId(event.target.value)}
        className={selectClass}
      >
        {tenants.map((tenant) => (
          <option key={tenant.id} value={tenant.id}>
            {tenant.label}
          </option>
        ))}
      </select>
    </label>
  );
}
