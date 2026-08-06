"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import {
  AlertTriangle,
  Building2,
  Loader2,
  RefreshCw,
  Save,
} from "lucide-react";

import { useToast } from "@/context/ToastContext";
import { useTenant } from "@/context/TenantContext";
import {
  getTenantProfile,
  TenantProfile,
  updateTenantProfile,
} from "@/lib/api";

interface SettingsFormState {
  name: string;
  slug: string;
  whatsapp_number: string;
  drive_folder_id: string;
  status: "active" | "suspended";
}

function profileToForm(profile: TenantProfile): SettingsFormState {
  return {
    name: profile.name,
    slug: profile.slug,
    whatsapp_number: profile.whatsapp_number ?? "",
    drive_folder_id: profile.drive_folder_id ?? "",
    status: profile.status === "suspended" ? "suspended" : "active",
  };
}

export default function SettingsPage() {
  const { tenantId, refreshTenants } = useTenant();
  const { showToast } = useToast();

  const [profile, setProfile] = useState<TenantProfile | null>(null);
  const [form, setForm] = useState<SettingsFormState | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadProfile = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const tenantProfile = await getTenantProfile(tenantId);
      setProfile(tenantProfile);
      setForm(profileToForm(tenantProfile));
    } catch (requestError) {
      console.error(requestError);
      setProfile(null);
      setForm(null);
      setError("Could not load tenant settings.");
    } finally {
      setLoading(false);
    }
  }, [tenantId]);

  useEffect(() => {
    void loadProfile();
  }, [loadProfile]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!form) {
      return;
    }

    if (!form.name.trim() || !form.slug.trim()) {
      showToast("Name and slug are required.", "error");
      return;
    }

    setSaving(true);

    try {
      const updated = await updateTenantProfile(
        {
          name: form.name.trim(),
          slug: form.slug.trim().toLowerCase(),
          whatsapp_number: form.whatsapp_number.trim() || null,
          drive_folder_id: form.drive_folder_id.trim() || null,
          status: form.status,
        },
        tenantId,
      );

      setProfile(updated);
      setForm(profileToForm(updated));
      await refreshTenants();
      showToast("Tenant settings saved.", "success");
    } catch (requestError) {
      console.error(requestError);
      showToast("Could not save tenant settings.", "error");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-48 items-center justify-center">
        <Loader2 className="h-7 w-7 animate-spin text-gray-400" />
      </div>
    );
  }

  if (error || !profile || !form) {
    return (
      <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-6">
        <div className="flex items-center gap-3 text-red-200">
          <AlertTriangle className="h-5 w-5" />
          <p>{error ?? "Tenant settings are unavailable."}</p>
        </div>
        <button
          type="button"
          onClick={() => void loadProfile()}
          className="mt-4 flex items-center gap-2 rounded-lg bg-white px-4 py-2 text-sm font-medium text-black"
        >
          <RefreshCw className="h-4 w-4" />
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">Settings</h1>
          <p className="mt-1 text-sm text-gray-400">
            Tenant profile and organization configuration.
          </p>
        </div>

        <button
          type="button"
          onClick={() => void loadProfile()}
          className="flex items-center gap-2 rounded-lg border border-gray-700 px-4 py-2 text-sm text-gray-200 hover:bg-gray-800"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </button>
      </div>

      <div className="rounded-xl border border-gray-800 bg-gray-900 p-5">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-300">
            <Building2 className="h-5 w-5" />
          </div>
          <div>
            <h2 className="font-medium text-white">{profile.name}</h2>
            <p className="text-sm text-gray-400">Tenant ID: {profile.id}</p>
          </div>
        </div>

        <dl className="mt-5 grid gap-3 border-t border-gray-800 pt-5 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-gray-500">Created</dt>
            <dd className="mt-1 text-gray-300">
              {new Date(profile.created_at).toLocaleString()}
            </dd>
          </div>
          <div>
            <dt className="text-gray-500">Last updated</dt>
            <dd className="mt-1 text-gray-300">
              {profile.updated_at
                ? new Date(profile.updated_at).toLocaleString()
                : "—"}
            </dd>
          </div>
        </dl>
      </div>

      <form
        onSubmit={handleSubmit}
        className="space-y-5 rounded-xl border border-gray-800 bg-gray-900 p-6"
      >
        <div>
          <h2 className="text-lg font-medium text-white">Organization profile</h2>
          <p className="mt-1 text-sm text-gray-400">
            Update institute details used across the dashboard and integrations.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block space-y-2 sm:col-span-2">
            <span className="text-sm text-gray-300">Institute name</span>
            <input
              required
              value={form.name}
              onChange={(event) =>
                setForm((current) =>
                  current ? { ...current, name: event.target.value } : current,
                )
              }
              className="w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-white outline-none focus:border-indigo-500"
            />
          </label>

          <label className="block space-y-2">
            <span className="text-sm text-gray-300">Slug</span>
            <input
              required
              value={form.slug}
              onChange={(event) =>
                setForm((current) =>
                  current ? { ...current, slug: event.target.value } : current,
                )
              }
              className="w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-white outline-none focus:border-indigo-500"
              placeholder="demo-physics"
            />
            <span className="text-xs text-gray-500">
              Lowercase letters, numbers, and hyphens only.
            </span>
          </label>

          <label className="block space-y-2">
            <span className="text-sm text-gray-300">Status</span>
            <select
              value={form.status}
              onChange={(event) =>
                setForm((current) =>
                  current
                    ? {
                        ...current,
                        status: event.target.value as "active" | "suspended",
                      }
                    : current,
                )
              }
              className="w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-white outline-none focus:border-indigo-500"
            >
              <option value="active">Active</option>
              <option value="suspended">Suspended</option>
            </select>
          </label>

          <label className="block space-y-2 sm:col-span-2">
            <span className="text-sm text-gray-300">WhatsApp number</span>
            <input
              value={form.whatsapp_number}
              onChange={(event) =>
                setForm((current) =>
                  current
                    ? { ...current, whatsapp_number: event.target.value }
                    : current,
                )
              }
              className="w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-white outline-none focus:border-indigo-500"
              placeholder="whatsapp:+14155238886"
            />
          </label>

          <label className="block space-y-2 sm:col-span-2">
            <span className="text-sm text-gray-300">Google Drive folder ID</span>
            <input
              value={form.drive_folder_id}
              onChange={(event) =>
                setForm((current) =>
                  current
                    ? { ...current, drive_folder_id: event.target.value }
                    : current,
                )
              }
              className="w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-white outline-none focus:border-indigo-500"
              placeholder="drive-folder-physics-demo"
            />
          </label>
        </div>

        <div className="flex justify-end border-t border-gray-800 pt-4">
          <button
            type="submit"
            disabled={saving}
            className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
          >
            {saving ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Save className="h-4 w-4" />
            )}
            Save settings
          </button>
        </div>
      </form>
    </div>
  );
}
