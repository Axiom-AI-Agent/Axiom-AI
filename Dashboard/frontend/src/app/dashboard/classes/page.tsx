"use client";

import Link from "next/link";
import {
  FormEvent,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  AlertTriangle,
  BookOpen,
  Loader2,
  Megaphone,
  Pencil,
  Plus,
  RefreshCw,
  Trash2,
  Upload,
  X,
} from "lucide-react";

import { useToast } from "@/context/ToastContext";
import { useTenant } from "@/context/TenantContext";
import ToggleSwitch from "@/components/ui/ToggleSwitch";
import {
  ApiError,
  BroadcastRecipients,
  createClass,
  deleteClass,
  getBroadcastRecipients,
  getClasses,
  INGEST_ACCEPT,
  ingestSizeError,
  sendClassBroadcast,
  SubjectClass,
  updateClassHumanMode,
  updateClassPaymentsEnabled,
  uploadClassDocument,
  updateClass,
} from "@/lib/api";
import { btnPrimary, btnQuiet } from "@/lib/ui";

interface ClassFormState {
  subject: string;
  name: string;
  grade: string;
  fee_amount: string;
  fee_cycle: string;
}

const emptyForm: ClassFormState = {
  subject: "",
  name: "",
  grade: "",
  fee_amount: "",
  fee_cycle: "monthly",
};

export default function ClassesPage() {
  const { tenantId } = useTenant();
  const { showToast } = useToast();

  const [classes, setClasses] = useState<SubjectClass[]>([]);
  const [form, setForm] = useState<ClassFormState>(emptyForm);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadingClassId, setUploadingClassId] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [broadcastClass, setBroadcastClass] = useState<SubjectClass | null>(null);
  const [broadcastMessage, setBroadcastMessage] = useState("");
  const [broadcastRecipients, setBroadcastRecipients] =
    useState<BroadcastRecipients | null>(null);
  const [broadcastLoading, setBroadcastLoading] = useState(false);
  const [broadcastSending, setBroadcastSending] = useState(false);
  const [broadcastError, setBroadcastError] = useState<string | null>(null);
  const [busyClassId, setBusyClassId] = useState<string | null>(null);
  const [classAiEnabled, setClassAiEnabled] = useState<Record<string, boolean>>(
    {},
  );
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadClasses = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      setClasses(await getClasses(tenantId));
    } catch (requestError) {
      console.error(requestError);
      setError("Could not load classes.");
    } finally {
      setLoading(false);
    }
  }, [tenantId]);

  useEffect(() => {
    void loadClasses();
  }, [loadClasses]);

  function openCreateForm() {
    setEditingId(null);
    setForm(emptyForm);
    setShowForm(true);
  }

  function openEditForm(subjectClass: SubjectClass) {
    setEditingId(subjectClass.id);
    setForm({
      subject: subjectClass.subject,
      name: subjectClass.name ?? "",
      grade: subjectClass.grade ?? "",
      fee_amount: String(subjectClass.fee_amount ?? ""),
      fee_cycle: subjectClass.fee_cycle ?? "monthly",
    });
    setShowForm(true);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const amount = Number(form.fee_amount);

    if (!form.subject.trim()) {
      setError("Enter a subject name.");
      return;
    }

    if (!Number.isFinite(amount) || amount < 0) {
      setError("Enter a valid fee amount.");
      return;
    }

    setSaving(true);
    setError(null);

    try {
      if (editingId) {
        const updated = await updateClass(
          editingId,
          {
            subject: form.subject.trim(),
            name: form.name.trim() || undefined,
            grade: form.grade.trim() || undefined,
            fee_amount: amount,
            fee_cycle: form.fee_cycle,
          },
          tenantId,
        );

        setClasses((current) =>
          current.map((item) => (item.id === editingId ? updated : item)),
        );
        showToast("Class updated.", "success");
      } else {
        const created = await createClass(
          {
            subject: form.subject.trim(),
            name: form.name.trim() || undefined,
            grade: form.grade.trim() || undefined,
            fee_amount: amount,
            fee_cycle: form.fee_cycle,
          },
          tenantId,
        );

        setClasses((current) => [created, ...current]);
        showToast("Class created.", "success");
      }

      setForm(emptyForm);
      setEditingId(null);
      setShowForm(false);
    } catch (requestError) {
      console.error(requestError);
      showToast("Could not save the class.", "error");
    } finally {
      setSaving(false);
    }
  }

  function handleFileSelect(event: React.ChangeEvent<HTMLInputElement>, classId: string) {
    const file = event.target.files?.[0];
    if (!file) return;

    handleUpload(classId, file);
    event.target.value = "";
  }

  async function handleUpload(classId: string, file: File) {
    const sizeError = ingestSizeError(file);
    if (sizeError) {
      setUploadError(sizeError);
      return;
    }

    setUploadingClassId(classId);
    setUploadError(null);

    try {
      const result = await uploadClassDocument(classId, tenantId, file);

      showToast(
        `Uploaded ${result.source_filename ?? file.name} — ${result.chunks_upserted} chunks ingested.`,
        "success",
      );

      if (result.warnings?.length) {
        setUploadError(result.warnings.join(" "));
      }
    } catch (requestError) {
      console.error(requestError);
      setUploadError("Failed to upload document.");
    } finally {
      setUploadingClassId(null);
    }
  }

  function triggerFileInput(classId: string) {
    if (fileInputRef.current) {
      fileInputRef.current.dataset.classId = classId;
      fileInputRef.current.click();
    }
  }

  async function handleDelete(classId: string) {
    if (!window.confirm("Delete this class? Related enrollments may be removed.")) {
      return;
    }

    try {
      await deleteClass(classId, tenantId);
      setClasses((current) => current.filter((item) => item.id !== classId));
      showToast("Class deleted.", "success");
    } catch (requestError) {
      console.error(requestError);
      showToast("Could not delete the class.", "error");
    }
  }

  async function toggleClassHumanMode(
    classId: string,
    aiEnabled: boolean,
  ) {
    const action = aiEnabled
      ? "Enable AI for every enrolled student in this class?"
      : "Disable AI for every enrolled student in this class?";

    if (!window.confirm(action)) {
      return;
    }

    setBusyClassId(classId);

    try {
      const result = await updateClassHumanMode(
        classId,
        !aiEnabled,
        tenantId,
      );

      setClassAiEnabled((current) => ({
        ...current,
        [classId]: aiEnabled,
      }));

      showToast(
        aiEnabled
          ? `AI re-enabled for ${result.students_updated} student(s).`
          : `Human mode enabled for ${result.students_updated} student(s).`,
        "success",
      );
    } catch (requestError) {
      console.error(requestError);
      showToast(
        "Could not update class AI mode.",
        "error",
      );
    } finally {
      setBusyClassId(null);
    }
  }

  async function toggleClassPayments(
    subjectClass: SubjectClass,
    paymentsEnabled: boolean,
  ) {
    const classLabel =
      subjectClass.name ?? subjectClass.subject;
    const action = paymentsEnabled
      ? `Enable payment submissions for ${classLabel}?`
      : `Disable payment submissions for ${classLabel}?`;

    if (!window.confirm(action)) {
      return;
    }

    setBusyClassId(subjectClass.id);

    try {
      const updated = await updateClassPaymentsEnabled(
        subjectClass.id,
        paymentsEnabled,
        tenantId,
      );

      setClasses((current) =>
        current.map((item) =>
          item.id === subjectClass.id ? updated : item,
        ),
      );

      showToast(
        paymentsEnabled
          ? `Payment collection enabled for ${classLabel}.`
          : `Payment collection disabled for ${classLabel}.`,
        "success",
      );
    } catch (requestError) {
      console.error(requestError);
      showToast(
        "Could not update class payment settings.",
        "error",
      );
    } finally {
      setBusyClassId(null);
    }
  }

  async function openBroadcast(subjectClass: SubjectClass) {
    setBroadcastClass(subjectClass);
    setBroadcastMessage("");
    setBroadcastRecipients(null);
    setBroadcastError(null);
    setBroadcastLoading(true);

    try {
      setBroadcastRecipients(
        await getBroadcastRecipients(subjectClass.id, tenantId),
      );
    } catch (requestError) {
      console.error(requestError);
      setBroadcastError(
        requestError instanceof ApiError
          ? requestError.message
          : "Could not load Telegram recipients for this class.",
      );
    } finally {
      setBroadcastLoading(false);
    }
  }

  function closeBroadcast() {
    if (broadcastSending) {
      return;
    }
    setBroadcastClass(null);
    setBroadcastMessage("");
    setBroadcastRecipients(null);
    setBroadcastError(null);
  }

  async function handleBroadcastSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!broadcastClass) {
      return;
    }

    const message = broadcastMessage.trim();
    if (!message) {
      setBroadcastError("Enter a message to send.");
      return;
    }

    if (!broadcastRecipients || broadcastRecipients.reachable < 1) {
      setBroadcastError(
        "No students in this class have linked Telegram yet. They must start the bot first.",
      );
      return;
    }

    setBroadcastSending(true);
    setBroadcastError(null);

    try {
      const result = await sendClassBroadcast(
        broadcastClass.id,
        message,
        tenantId,
      );
      const parts = [`Sent to ${result.sent} student${result.sent === 1 ? "" : "s"}`];
      if (result.skipped_no_telegram > 0) {
        parts.push(`${result.skipped_no_telegram} skipped (no Telegram)`);
      }
      if (result.failed > 0) {
        parts.push(`${result.failed} failed`);
      }
      showToast(
        `${parts.join(". ")}.`,
        result.failed > 0 ? "error" : "success",
      );
      setBroadcastClass(null);
      setBroadcastMessage("");
      setBroadcastRecipients(null);
      setBroadcastError(null);
    } catch (requestError) {
      console.error(requestError);
      setBroadcastError(
        requestError instanceof ApiError
          ? requestError.message
          : "Could not send the class broadcast.",
      );
    } finally {
      setBroadcastSending(false);
    }
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col space-y-6 overflow-hidden">
      <div className="flex flex-wrap items-start justify-between gap-4 shrink-0">
        <div>
          <h1 className="text-2xl font-semibold text-heading">Classes</h1>
          <p className="mt-1 text-sm text-muted">
            Create classes and send Telegram broadcasts to enrolled students.
          </p>
        </div>

        <div className="flex gap-2">
          <Link
            href="/dashboard/ingest"
            className="flex items-center gap-2 rounded-lg border border-border px-4 py-2 text-sm text-fg hover:bg-hover bg-surface"
          >
            <Upload className="h-4 w-4" />
            Upload notes
          </Link>

          <button
            type="button"
            onClick={() => void loadClasses()}
            disabled={loading}
            className="flex items-center gap-2 rounded-lg border border-border px-4 py-2 text-sm text-fg hover:bg-hover bg-surface disabled:opacity-50"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>

          <button
            type="button"
            onClick={() => (showForm ? setShowForm(false) : openCreateForm())}
            className={showForm ? btnQuiet : btnPrimary}
          >
            {showForm ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
            {showForm ? "Cancel" : "Add class"}
          </button>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-border bg-surface p-4 text-fg">
          <AlertTriangle className="h-5 w-5" />
          {error}
        </div>
      )}

      {uploadError && (
        <div className="flex items-center gap-2 rounded-lg border border-blue/30 bg-blue/10 p-4 text-blue">
          <AlertTriangle className="h-5 w-5" />
          <span>{uploadError}</span>
        </div>
      )}

      <input
        ref={fileInputRef}
        type="file"
        accept={INGEST_ACCEPT}
        className="hidden"
        onChange={(e) => {
          const classId = e.currentTarget.dataset.classId;
          if (classId) handleFileSelect(e, classId);
        }}
      />

      {showForm && (
        <form
          onSubmit={handleSubmit}
          className="grid gap-4 rounded-xl border border-border bg-surface p-5 md:grid-cols-2 xl:grid-cols-3"
        >
          <label className="space-y-2">
            <span className="text-sm text-fg">Subject</span>
            <input
              required
              value={form.subject}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  subject: event.target.value,
                }))
              }
              className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-heading"
            />
          </label>

          <label className="space-y-2">
            <span className="text-sm text-fg">Display name</span>
            <input
              value={form.name}
              onChange={(event) =>
                setForm((current) => ({ ...current, name: event.target.value }))
              }
              className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-heading"
            />
          </label>

          <label className="space-y-2">
            <span className="text-sm text-fg">Grade</span>
            <input
              value={form.grade}
              onChange={(event) =>
                setForm((current) => ({ ...current, grade: event.target.value }))
              }
              className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-heading"
            />
          </label>

          <label className="space-y-2">
            <span className="text-sm text-fg">Fee amount (LKR)</span>
            <input
              required
              type="number"
              min="0"
              step="0.01"
              value={form.fee_amount}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  fee_amount: event.target.value,
                }))
              }
              className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-heading"
            />
          </label>

          <label className="space-y-2">
            <span className="text-sm text-fg">Fee cycle</span>
            <select
              value={form.fee_cycle}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  fee_cycle: event.target.value,
                }))
              }
              className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-heading"
            >
              <option value="monthly">Monthly</option>
              <option value="per_class">Per class</option>
              <option value="termly">Termly</option>
              <option value="one_time">One-time</option>
            </select>
          </label>

          <div className="flex items-end md:col-span-2 xl:col-span-3">
            <button
              type="submit"
              disabled={saving}
              className="inline-flex items-center gap-2 rounded-lg bg-blue px-4 py-2 text-sm font-medium text-paper disabled:opacity-50"
            >
              {saving && <Loader2 className="h-4 w-4 animate-spin" />}
              {editingId ? "Save changes" : "Create class"}
            </button>
          </div>
        </form>
      )}

      {loading ? (
        <div className="flex min-h-48 items-center justify-center">
          <Loader2 className="h-7 w-7 animate-spin text-muted" />
        </div>
      ) : classes.length === 0 ? (
        <div className="rounded-xl border border-border bg-surface p-10 text-center">
          <BookOpen className="mx-auto h-10 w-10 text-muted" />
          <p className="mt-3 text-fg">No classes yet.</p>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto pr-1">
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3 pb-6">
          {classes.map((subjectClass) => (
            <article
              key={subjectClass.id}
              className="rounded-xl border border-border bg-surface p-5"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="text-lg font-semibold text-heading">
                    {subjectClass.name ?? subjectClass.subject}
                  </h2>
                  <p className="text-sm text-muted">{subjectClass.subject}</p>
                  {subjectClass.grade && (
                    <p className="mt-1 text-xs text-muted">
                      Grade {subjectClass.grade}
                    </p>
                  )}
                </div>
                <BookOpen className="h-5 w-5 text-muted" />
              </div>

              <dl className="mt-5 space-y-2 text-sm">
                <div className="flex justify-between gap-4">
                  <dt className="text-muted">Fee</dt>
                  <dd className="text-heading">
                    LKR {Number(subjectClass.fee_amount ?? 0).toLocaleString()}
                  </dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-muted">Cycle</dt>
                  <dd className="capitalize text-fg">
                    {subjectClass.fee_cycle}
                  </dd>
                </div>
              </dl>

              <div className="mt-5 space-y-4 rounded-xl border border-blue/20 bg-blue/[0.04] p-4 dark:bg-blue/10">
                <p className="text-xs font-semibold uppercase tracking-wide text-muted">
                  Enable / disable
                </p>
                <ToggleSwitch
                  label="Payments"
                  description="Collect payment slips for this class"
                  checked={subjectClass.payments_enabled !== false}
                  disabled={busyClassId === subjectClass.id}
                  onChange={(next) =>
                    void toggleClassPayments(subjectClass, next)
                  }
                />
                <div className="border-t border-border/80 pt-4">
                  <ToggleSwitch
                    label="AI for class"
                    description="Off = human mode for all enrolled students"
                    checked={classAiEnabled[subjectClass.id] ?? true}
                    disabled={busyClassId === subjectClass.id}
                    onChange={(next) =>
                      void toggleClassHumanMode(subjectClass.id, next)
                    }
                  />
                </div>
              </div>

              <button
                type="button"
                onClick={() => void openBroadcast(subjectClass)}
                className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-blue px-3 py-2 text-sm font-medium text-paper hover:bg-blue/90"
              >
                <Megaphone className="h-4 w-4" />
                Broadcast to Telegram
              </button>

              <div className="mt-3 flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => triggerFileInput(subjectClass.id)}
                  disabled={uploadingClassId === subjectClass.id}
                  className="inline-flex items-center gap-1 rounded-lg border border-border px-3 py-1.5 text-sm text-fg hover:bg-hover bg-surface disabled:opacity-50"
                >
                  {uploadingClassId === subjectClass.id ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Upload className="h-4 w-4" />
                  )}
                  {uploadingClassId === subjectClass.id
                    ? "Uploading..."
                    : "Upload PDF"}
                </button>
                <button
                  type="button"
                  onClick={() => openEditForm(subjectClass)}
                  className="inline-flex items-center gap-1 rounded-lg border border-border px-3 py-1.5 text-sm text-fg hover:bg-hover bg-surface"
                >
                  <Pencil className="h-4 w-4" />
                  Edit
                </button>
                <button
                  type="button"
                  onClick={() => void handleDelete(subjectClass.id)}
                  className="inline-flex items-center gap-1 rounded-lg border border-border px-3 py-1.5 text-sm text-fg hover:bg-hover"
                >
                  <Trash2 className="h-4 w-4" />
                  Delete
                </button>
                <Link
                  href={`/dashboard/ingest?class_id=${encodeURIComponent(subjectClass.id)}`}
                  className="inline-flex items-center gap-1 rounded-lg border border-border px-3 py-1.5 text-sm text-muted hover:bg-hover bg-surface"
                >
                  <Upload className="h-4 w-4" />
                  Ingest
                </Link>
              </div>
            </article>
          ))}
          </div>
        </div>
      )}

      {broadcastClass && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-ink/55 p-4"
          role="presentation"
          onClick={closeBroadcast}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="broadcast-title"
            className="w-full max-w-lg rounded-xl border border-border bg-surface p-5   bg-surface"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <h2
                  id="broadcast-title"
                  className="text-lg font-semibold text-heading"
                >
                  Broadcast to {broadcastClass.name ?? broadcastClass.subject}
                </h2>
                <p className="mt-1 text-sm text-muted">
                  Sends a Telegram message to students enrolled in this class who have
                  linked the bot.
                </p>
              </div>
              <button
                type="button"
                onClick={closeBroadcast}
                disabled={broadcastSending}
                className="rounded-lg p-1 text-muted hover:bg-hover disabled:opacity-50 hover:bg-hover"
                aria-label="Close broadcast dialog"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {broadcastLoading ? (
              <div className="flex min-h-32 items-center justify-center">
                <Loader2 className="h-6 w-6 animate-spin text-muted" />
              </div>
            ) : (
              <form onSubmit={handleBroadcastSubmit} className="mt-4 space-y-4">
                {broadcastRecipients && (
                  <p className="text-sm text-fg">
                    {broadcastRecipients.reachable} of {broadcastRecipients.enrolled}{" "}
                    enrolled student
                    {broadcastRecipients.enrolled === 1 ? "" : "s"} will receive this
                    {broadcastRecipients.skipped_no_telegram > 0
                      ? ` (${broadcastRecipients.skipped_no_telegram} have not linked Telegram)`
                      : ""}
                    .
                    {broadcastRecipients.reachable_names.length > 0 && (
                      <span className="mt-1 block text-muted">
                        {broadcastRecipients.reachable_names.join(", ")}
                      </span>
                    )}
                  </p>
                )}

                <label className="block space-y-2">
                  <span className="text-sm text-fg">
                    Message
                  </span>
                  <textarea
                    required
                    rows={5}
                    maxLength={4000}
                    value={broadcastMessage}
                    onChange={(event) => setBroadcastMessage(event.target.value)}
                    disabled={broadcastSending}
                    placeholder="Exam is postponed to Friday."
                    className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-heading  bg-surface "
                  />
                </label>

                {broadcastError && (
                  <div className="flex items-start gap-2 rounded-lg border border-border bg-surface p-3 text-sm text-fg">
                    <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
                    <span>{broadcastError}</span>
                  </div>
                )}

                <div className="flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={closeBroadcast}
                    disabled={broadcastSending}
                    className="rounded-lg border border-border px-4 py-2 text-sm text-fg hover:bg-hover disabled:opacity-50  dark:text-muted hover:bg-hover"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={
                      broadcastSending ||
                      broadcastLoading ||
                      !broadcastRecipients ||
                      broadcastRecipients.reachable < 1
                    }
                    className="inline-flex items-center gap-2 rounded-lg bg-blue px-4 py-2 text-sm font-medium text-paper disabled:opacity-50"
                  >
                    {broadcastSending && (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    )}
                    Send to Telegram
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
