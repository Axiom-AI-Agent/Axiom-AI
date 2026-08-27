"use client";

import {
  FormEvent,
  useCallback,
  useEffect,
  useState,
} from "react";
import {
  AlertTriangle,
  Building2,
  Loader2,
  RefreshCw,
  Save,
  Smartphone,
} from "lucide-react";

import { useToast } from "@/context/ToastContext";
import { useTenant } from "@/context/TenantContext";
import {
  getTenantProfile,
  TenantProfile,
  updateTenantProfile,
} from "@/lib/api";
import {
  createTelegramLinkCode,
  getTelegramLinkStatus,
  unlinkTelegram,
  type TelegramLinkCode,
  type TelegramLinkStatus,
} from "@/lib/auth-api";

interface SettingsFormState {
  name: string;
  slug: string;
  whatsapp_number: string;
  drive_folder_id: string;
  status: "active" | "suspended";
}

function profileToForm(
  profile: TenantProfile,
): SettingsFormState {
  return {
    name: profile.name,
    slug: profile.slug,
    whatsapp_number:
      profile.whatsapp_number ?? "",
    drive_folder_id:
      profile.drive_folder_id ?? "",
    status:
      profile.status === "suspended"
        ? "suspended"
        : "active",
  };
}

export default function SettingsPage() {
  const {
    tenantId,
    refreshTenants,
  } = useTenant();

  const { showToast } =
    useToast();

  const [
    profile,
    setProfile,
  ] = useState<TenantProfile | null>(
    null,
  );

  const [
    form,
    setForm,
  ] = useState<SettingsFormState | null>(
    null,
  );

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    saving,
    setSaving,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<string | null>(
    null,
  );

  const [
    telegramStatus,
    setTelegramStatus,
  ] = useState<TelegramLinkStatus | null>(null);

  const [
    telegramCode,
    setTelegramCode,
  ] = useState<TelegramLinkCode | null>(null);

  const [
    telegramBusy,
    setTelegramBusy,
  ] = useState(false);

  const loadProfile =
    useCallback(async () => {
      setLoading(true);
      setError(null);

      try {
        const tenantProfile =
          await getTenantProfile(
            tenantId,
          );

        setProfile(
          tenantProfile,
        );

        setForm(
          profileToForm(
            tenantProfile,
          ),
        );

        try {
          setTelegramStatus(await getTelegramLinkStatus());
        } catch (telegramError) {
          console.error(telegramError);
          setTelegramStatus(null);
        }
      } catch (requestError) {
        console.error(
          requestError,
        );

        setProfile(null);
        setForm(null);

        setError(
          "Could not load tenant settings.",
        );
      } finally {
        setLoading(false);
      }
    }, [tenantId]);

  useEffect(() => {
    void loadProfile();
  }, [loadProfile]);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!form) {
      return;
    }

    if (
      !form.name.trim() ||
      !form.slug.trim()
    ) {
      showToast(
        "Name and slug are required.",
        "error",
      );

      return;
    }

    setSaving(true);

    try {
      const updated =
        await updateTenantProfile(
          {
            name:
              form.name.trim(),

            slug:
              form.slug
                .trim()
                .toLowerCase(),

            whatsapp_number:
              form.whatsapp_number
                .trim() || null,

            drive_folder_id:
              form.drive_folder_id
                .trim() || null,

            status:
              form.status,
          },
          tenantId,
        );

      setProfile(updated);

      setForm(
        profileToForm(
          updated,
        ),
      );

      await refreshTenants();

      showToast(
        "Tenant settings saved.",
        "success",
      );
    } catch (requestError) {
      console.error(
        requestError,
      );

      showToast(
        "Could not save tenant settings.",
        "error",
      );
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-48 items-center justify-center">
        <Loader2 className="h-7 w-7 animate-spin text-slate-600 dark:text-slate-400" />
      </div>
    );
  }

  if (
    error ||
    !profile ||
    !form
  ) {
    return (
      <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-6">
        <div className="flex items-center gap-3 text-red-200">
          <AlertTriangle className="h-5 w-5" />

          <p>
            {error ??
              "Tenant settings are unavailable."}
          </p>
        </div>

        <button
          type="button"
          onClick={() =>
            void loadProfile()
          }
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
          <h1 className="text-2xl font-semibold text-slate-900 dark:text-white">
            Settings
          </h1>

          <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
            Tenant profile and
            organization configuration.
          </p>
        </div>

        <button
          type="button"
          onClick={() =>
            void loadProfile()
          }
          className="flex items-center gap-2 rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-800 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </button>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-blue-500/10 text-blue-300">
            <Building2 className="h-5 w-5" />
          </div>

          <div>
            <h2 className="font-medium text-slate-900 dark:text-white">
              {profile.name}
            </h2>

            <p className="text-sm text-slate-600 dark:text-slate-400">
              Tenant ID: {profile.id}
            </p>
          </div>
        </div>

        <dl className="mt-5 grid gap-3 border-t border-slate-200 pt-5 text-sm sm:grid-cols-2 dark:border-slate-800">
          <div>
            <dt className="text-slate-500 dark:text-slate-400">
              Created
            </dt>

            <dd className="mt-1 text-slate-700 dark:text-slate-300">
              {new Date(
                profile.created_at,
              ).toLocaleString()}
            </dd>
          </div>

          <div>
            <dt className="text-slate-500 dark:text-slate-400">
              Last updated
            </dt>

            <dd className="mt-1 text-slate-700 dark:text-slate-300">
              {profile.updated_at
                ? new Date(
                    profile.updated_at,
                  ).toLocaleString()
                : "—"}
            </dd>
          </div>
        </dl>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900">
        <div className="flex items-start gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-300">
            <Smartphone className="h-5 w-5" />
          </div>
          <div>
            <h2 className="font-medium text-slate-900 dark:text-white">
              Telegram staff access
            </h2>
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
              Generate a one-time code, then send it to this institute&apos;s
              Telegram bot. Students cannot gain staff access this way.
            </p>
          </div>
        </div>

        {telegramStatus?.linked ? (
          <div className="mt-5 space-y-3">
            <p className="text-sm text-emerald-300">
              Linked
              {telegramStatus.channel_address
                ? ` (chat ${telegramStatus.channel_address})`
                : ""}
              .
            </p>
            <button
              type="button"
              disabled={telegramBusy}
              onClick={async () => {
                setTelegramBusy(true);
                try {
                  await unlinkTelegram();
                  setTelegramStatus(await getTelegramLinkStatus());
                  setTelegramCode(null);
                  showToast("Telegram unlinked.", "success");
                } catch (unlinkError) {
                  console.error(unlinkError);
                  showToast("Could not unlink Telegram.", "error");
                } finally {
                  setTelegramBusy(false);
                }
              }}
              className="rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-800 hover:bg-slate-100 disabled:opacity-50 dark:border-slate-700 dark:text-slate-200"
            >
              {telegramBusy ? "Working…" : "Unlink Telegram"}
            </button>
          </div>
        ) : (
          <div className="mt-5 space-y-3">
            {telegramCode ? (
              <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-4">
                <p className="text-xs uppercase tracking-wide text-emerald-300">
                  Send this code to the bot
                </p>
                <p className="mt-2 font-mono text-2xl font-semibold text-slate-900 dark:text-white">
                  {telegramCode.code}
                </p>
                <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                  Expires in {telegramCode.ttl_minutes} minutes
                  {telegramCode.telegram_bot_username
                    ? ` · @${telegramCode.telegram_bot_username.replace(/^@/, "")}`
                    : ""}
                  .
                </p>
              </div>
            ) : null}
            <button
              type="button"
              disabled={telegramBusy}
              onClick={async () => {
                setTelegramBusy(true);
                try {
                  const created = await createTelegramLinkCode();
                  setTelegramCode(created);
                  showToast("Link code generated.", "success");
                } catch (codeError) {
                  console.error(codeError);
                  showToast("Could not generate a link code.", "error");
                } finally {
                  setTelegramBusy(false);
                }
              }}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-50"
            >
              {telegramBusy ? "Working…" : "Generate Telegram code"}
            </button>
          </div>
        )}
      </div>

      <form
        onSubmit={handleSubmit}
        className="space-y-5 rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900"
      >
        <div>
          <h2 className="text-lg font-medium text-slate-900 dark:text-white">
            Organization profile
          </h2>

          <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
            Update institute details
            used across the dashboard
            and integrations.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block space-y-2 sm:col-span-2">
            <span className="text-sm text-slate-700 dark:text-slate-300">
              Institute name
            </span>

            <input
              required
              value={form.name}
              onChange={(event) =>
                setForm(
                  (current) =>
                    current
                      ? {
                          ...current,
                          name:
                            event.target
                              .value,
                        }
                      : current,
                )
              }
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white"
            />
          </label>

          <label className="block space-y-2">
            <span className="text-sm text-slate-700 dark:text-slate-300">
              Slug
            </span>

            <input
              required
              value={form.slug}
              onChange={(event) =>
                setForm(
                  (current) =>
                    current
                      ? {
                          ...current,
                          slug:
                            event.target
                              .value,
                        }
                      : current,
                )
              }
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white"
              placeholder="demo-physics"
            />

            <span className="text-xs text-slate-500 dark:text-slate-400">
              Lowercase letters, numbers,
              and hyphens only.
            </span>
          </label>

          <label className="block space-y-2">
            <span className="text-sm text-slate-700 dark:text-slate-300">
              Status
            </span>

            <select
              value={form.status}
              onChange={(event) =>
                setForm(
                  (current) =>
                    current
                      ? {
                          ...current,
                          status:
                            event.target
                              .value as
                              | "active"
                              | "suspended",
                        }
                      : current,
                )
              }
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white"
            >
              <option value="active">
                Active
              </option>

              <option value="suspended">
                Suspended
              </option>
            </select>
          </label>

          <label className="block space-y-2 sm:col-span-2">
            <span className="text-sm text-slate-700 dark:text-slate-300">
              WhatsApp number
            </span>

            <input
              value={
                form.whatsapp_number
              }
              onChange={(event) =>
                setForm(
                  (current) =>
                    current
                      ? {
                          ...current,
                          whatsapp_number:
                            event.target
                              .value,
                        }
                      : current,
                )
              }
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white"
              placeholder="whatsapp:+14155238886"
            />
          </label>

          <label className="block space-y-2 sm:col-span-2">
            <span className="text-sm text-slate-700 dark:text-slate-300">
              Google Drive folder ID
            </span>

            <input
              value={
                form.drive_folder_id
              }
              onChange={(event) =>
                setForm(
                  (current) =>
                    current
                      ? {
                          ...current,
                          drive_folder_id:
                            event.target
                              .value,
                        }
                      : current,
                )
              }
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white"
              placeholder="drive-folder-physics-demo"
            />
          </label>
        </div>

        <p className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300">
          Payment collection is controlled per class on the Classes page.
        </p>

        <div className="flex justify-end border-t border-slate-200 pt-4 dark:border-slate-800">
          <button
            type="submit"
            disabled={saving}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-50"
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