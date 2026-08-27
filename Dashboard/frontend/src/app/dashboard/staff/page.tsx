"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import {
  AlertTriangle,
  Loader2,
  Plus,
  RefreshCw,
  UserCog,
  X,
} from "lucide-react";

import { useToast } from "@/context/ToastContext";
import { useTenant } from "@/context/TenantContext";
import ToggleSwitch from "@/components/ui/ToggleSwitch";
import {
  createStaff,
  getStaff,
  StaffMember,
  StaffRoleValue,
  updateStaff,
} from "@/lib/api";
import {
  btnPrimary,
  btnQuiet,
  emptyState,
  errorBanner,
  pageHeader,
  pageSubtitle,
  pageTitle,
  surfaceCard,
} from "@/lib/ui";

interface StaffFormState {
  name: string;
  email: string;
  password: string;
  role: StaffRoleValue;
}

const emptyForm: StaffFormState = {
  name: "",
  email: "",
  password: "",
  role: "tutor",
};

export default function StaffPage() {
  const { tenantId } = useTenant();
  const { showToast } = useToast();

  const [staff, setStaff] = useState<StaffMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState<StaffFormState>(emptyForm);

  const loadStaff = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      setStaff(await getStaff(tenantId));
    } catch (requestError) {
      console.error(requestError);
      setError("Could not load staff members.");
    } finally {
      setLoading(false);
    }
  }, [tenantId]);

  useEffect(() => {
    void loadStaff();
  }, [loadStaff]);

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    setSaving(true);

    try {
      await createStaff(
        {
          name: form.name.trim(),
          email: form.email.trim().toLowerCase(),
          password: form.password,
          role: form.role,
        },
        tenantId,
      );
      showToast("Staff member added.", "success");
      setShowForm(false);
      setForm(emptyForm);
      await loadStaff();
    } catch (requestError) {
      console.error(requestError);
      showToast("Could not create staff member.", "error");
    } finally {
      setSaving(false);
    }
  }

  async function toggleActive(member: StaffMember) {
    try {
      const updated = await updateStaff(
        member.id,
        { is_active: !member.is_active },
        tenantId,
      );
      setStaff((current) =>
        current.map((item) =>
          item.id === member.id ? updated : item,
        ),
      );
      showToast(
        updated.is_active
          ? "Staff member activated."
          : "Staff member deactivated.",
        "success",
      );
    } catch (requestError) {
      console.error(requestError);
      showToast("Could not update staff member.", "error");
    }
  }

  return (
    <div className="space-y-6">
      <div className={pageHeader}>
        <div className="min-w-0">
          <h1 className={pageTitle}>Staff</h1>
          <p className={pageSubtitle}>
            Manage administrator and tutor accounts.
          </p>
        </div>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => void loadStaff()}
            disabled={loading}
            className={btnQuiet}
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>
          <button
            type="button"
            onClick={() => setShowForm(true)}
            className={btnPrimary}
          >
            <Plus className="h-4 w-4" />
            Add Staff
          </button>
        </div>
      </div>

      {error && (
        <div className={errorBanner}>
          <AlertTriangle className="h-5 w-5 shrink-0 text-blue" />
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex min-h-48 items-center justify-center">
          <Loader2 className="h-7 w-7 animate-spin text-muted" />
        </div>
      ) : staff.length === 0 ? (
        <div className={emptyState}>
          <UserCog className="mx-auto h-10 w-10 text-muted" />
          <p className="mt-3 text-muted">
            No staff members yet.
          </p>
        </div>
      ) : (
        <div className={`${surfaceCard} overflow-x-auto`}>
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-border bg-bg/50 text-muted">
              <tr>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Email</th>
                <th className="px-4 py-3 font-medium">Role</th>
                <th className="px-4 py-3 font-medium">Active</th>
              </tr>
            </thead>
            <tbody>
              {staff.map((member) => (
                <tr
                  key={member.id}
                  className="border-b border-border last:border-0"
                >
                  <td className="px-4 py-3 text-heading">
                    {member.name}
                  </td>
                  <td className="px-4 py-3 text-muted">
                    {member.email}
                  </td>
                  <td className="px-4 py-3 capitalize text-fg">
                    {member.role}
                  </td>
                  <td className="px-4 py-3">
                    <ToggleSwitch
                      label={member.is_active ? "Active" : "Inactive"}
                      checked={member.is_active}
                      onChange={() => void toggleActive(member)}
                      className="min-w-[9.5rem]"
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showForm && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-ink/55 p-4"
          role="presentation"
          onClick={() => setShowForm(false)}
        >
          <div
            role="dialog"
            aria-modal="true"
            className="w-full max-w-lg rounded-xl border border-border bg-surface p-6  bg-surface"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-heading">
                Add Staff
              </h2>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="rounded-lg p-2 text-muted hover:bg-hover"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4">
              <label className="block space-y-2">
                <span className="text-sm text-muted">
                  Name
                </span>
                <input
                  required
                  value={form.name}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      name: event.target.value,
                    }))
                  }
                  className="w-full rounded-lg border border-border bg-surface px-3 py-2  bg-surface"
                />
              </label>

              <label className="block space-y-2">
                <span className="text-sm text-muted">
                  Email
                </span>
                <input
                  required
                  type="email"
                  value={form.email}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      email: event.target.value,
                    }))
                  }
                  className="w-full rounded-lg border border-border bg-surface px-3 py-2  bg-surface"
                />
              </label>

              <label className="block space-y-2">
                <span className="text-sm text-muted">
                  Temporary password
                </span>
                <input
                  required
                  type="password"
                  minLength={8}
                  value={form.password}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      password: event.target.value,
                    }))
                  }
                  className="w-full rounded-lg border border-border bg-surface px-3 py-2  bg-surface"
                />
              </label>

              <label className="block space-y-2">
                <span className="text-sm text-muted">
                  Role
                </span>
                <select
                  value={form.role}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      role: event.target.value as StaffRoleValue,
                    }))
                  }
                  className="w-full rounded-lg border border-border bg-surface px-3 py-2  bg-surface"
                >
                  <option value="admin">Admin</option>
                  <option value="tutor">Tutor</option>
                  <option value="marker">Marker</option>
                  <option value="viewer">Viewer</option>
                </select>
              </label>

              <button
                type="submit"
                disabled={saving}
                className="inline-flex items-center gap-2 rounded-lg bg-blue px-4 py-2 text-sm font-medium text-paper disabled:opacity-50"
              >
                {saving && <Loader2 className="h-4 w-4 animate-spin" />}
                Create staff
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
