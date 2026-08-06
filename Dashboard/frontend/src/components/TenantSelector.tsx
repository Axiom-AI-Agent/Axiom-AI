"use client";

import { useTenant } from "@/context/TenantContext";

export default function TenantSelector() {
  const { tenantId, setTenantId, tenants } = useTenant();

  return (
    <label className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
      <span className="hidden sm:inline font-medium">Tenant</span>
      <select
        value={tenantId}
        onChange={(event) => setTenantId(event.target.value)}
        className="rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-1.5 text-sm text-slate-900 dark:text-white outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors shadow-sm"
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
