"use client";

import { useTenant } from "@/context/TenantContext";

export default function TenantSelector() {
  const { tenantId, setTenantId, tenants } = useTenant();

  return (
    <label className="flex items-center gap-2 text-sm text-gray-300">
      <span className="hidden sm:inline">Tenant</span>
      <select
        value={tenantId}
        onChange={(event) => setTenantId(event.target.value)}
        className="rounded-lg border border-gray-700 bg-gray-900 px-2 py-1.5 text-sm text-white outline-none focus:border-gray-500"
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
