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
    humanMode: boolean,
  ) {
    const action = humanMode
      ? "Disable AI for every enrolled student in this class?"
      : "Enable AI for every enrolled student in this class?";

    if (!window.confirm(action)) {
      return;
    }

    try {
      const result = await updateClassHumanMode(
        classId,
        humanMode,
        tenantId,
      );

      showToast(
        humanMode
          ? `Human mode enabled for ${result.students_updated} student(s).`
          : `AI re-enabled for ${result.students_updated} student(s).`,
        "success",
      );
    } catch (requestError) {
      console.error(requestError);
      showToast(
        "Could not update class AI mode.",
        "error",
      );
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
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900 dark:text-white">Classes</h1>
          <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
            Create classes and send Telegram broadcasts to enrolled students.
          </p>
        </div>

        <div className="flex gap-2">
          <Link
            href="/dashboard/ingest"
            className="flex items-center gap-2 rounded-lg border border-slate-300 dark:border-slate-700 px-4 py-2 text-sm text-slate-800 dark:text-slate-200 hover:bg-slate-100 dark:bg-slate-800"
          >
            <Upload className="h-4 w-4" />
            Upload notes
          </Link>

          <button
            type="button"
            onClick={() => void loadClasses()}
            disabled={loading}
            className="flex items-center gap-2 rounded-lg border border-slate-300 dark:border-slate-700 px-4 py-2 text-sm text-slate-800 dark:text-slate-200 hover:bg-slate-100 dark:bg-slate-800 disabled:opacity-50"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>

          <button
            type="button"
            onClick={() => (showForm ? setShowForm(false) : openCreateForm())}
            className="flex items-center gap-2 rounded-lg bg-white px-4 py-2 text-sm font-medium text-black hover:bg-gray-200"
          >
            {showForm ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
            {showForm ? "Cancel" : "Add class"}
          </button>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-200">
          <AlertTriangle className="h-5 w-5" />
          {error}
        </div>
      )}

      {uploadError && (
        <div className="flex items-center gap-2 rounded-lg border border-yellow-500/30 bg-yellow-500/10 p-4 text-yellow-200">
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
          className="grid gap-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 md:grid-cols-2 xl:grid-cols-3"
        >
          <label className="space-y-2">
            <span className="text-sm text-slate-700 dark:text-slate-300">Subject</span>
            <input
              required
              value={form.subject}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  subject: event.target.value,
                }))
              }
              className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 px-3 py-2 text-slate-900 dark:text-white"
            />
          </label>

          <label className="space-y-2">
            <span className="text-sm text-slate-700 dark:text-slate-300">Display name</span>
            <input
              value={form.name}
              onChange={(event) =>
                setForm((current) => ({ ...current, name: event.target.value }))
              }
              className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 px-3 py-2 text-slate-900 dark:text-white"
            />
          </label>

          <label className="space-y-2">
            <span className="text-sm text-slate-700 dark:text-slate-300">Grade</span>
            <input
              value={form.grade}
              onChange={(event) =>
                setForm((current) => ({ ...current, grade: event.target.value }))
              }
              className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 px-3 py-2 text-slate-900 dark:text-white"
            />
          </label>

          <label className="space-y-2">
            <span className="text-sm text-slate-700 dark:text-slate-300">Fee amount (LKR)</span>
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
              className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 px-3 py-2 text-slate-900 dark:text-white"
            />
          </label>

          <label className="space-y-2">
            <span className="text-sm text-slate-700 dark:text-slate-300">Fee cycle</span>
            <select
              value={form.fee_cycle}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  fee_cycle: event.target.value,
                }))
              }
              className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 px-3 py-2 text-slate-900 dark:text-white"
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
              className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              {saving && <Loader2 className="h-4 w-4 animate-spin" />}
              {editingId ? "Save changes" : "Create class"}
            </button>
          </div>
        </form>
      )}

      {loading ? (
        <div className="flex min-h-48 items-center justify-center">
          <Loader2 className="h-7 w-7 animate-spin text-slate-600 dark:text-slate-400" />
        </div>
      ) : classes.length === 0 ? (
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-10 text-center">
          <BookOpen className="mx-auto h-10 w-10 text-slate-500 dark:text-slate-400" />
          <p className="mt-3 text-slate-700 dark:text-slate-300">No classes yet.</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {classes.map((subjectClass) => (
            <article
              key={subjectClass.id}
              className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                    {subjectClass.name ?? subjectClass.subject}
                  </h2>
                  <p className="text-sm text-slate-600 dark:text-slate-400">{subjectClass.subject}</p>
                  {subjectClass.grade && (
                    <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                      Grade {subjectClass.grade}
                    </p>
                  )}
                </div>
                <BookOpen className="h-5 w-5 text-slate-600 dark:text-slate-400" />
              </div>

              <dl className="mt-5 space-y-2 text-sm">
                <div className="flex justify-between gap-4">
                  <dt className="text-slate-600 dark:text-slate-400">Fee</dt>
                  <dd className="text-slate-900 dark:text-white">
                    LKR {Number(subjectClass.fee_amount ?? 0).toLocaleString()}
                  </dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-slate-600 dark:text-slate-400">Cycle</dt>
                  <dd className="capitalize text-slate-800 dark:text-slate-200">
                    {subjectClass.fee_cycle}
                  </dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-slate-600 dark:text-slate-400">
                    Payments
                  </dt>
                  <dd
                    className={
                      subjectClass.payments_enabled === false
                        ? "text-amber-700 dark:text-amber-300"
                        : "text-emerald-700 dark:text-emerald-300"
                    }
                  >
                    {subjectClass.payments_enabled === false
                      ? "Disabled"
                      : "Enabled"}
                  </dd>
                </div>
              </dl>

              <button
                type="button"
                onClick={() => void openBroadcast(subjectClass)}
                className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-500"
              >
                <Megaphone className="h-4 w-4" />
                Broadcast to Telegram
              </button>

              <div className="mt-3 flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() =>
                    void toggleClassPayments(
                      subjectClass,
                      subjectClass.payments_enabled === false,
                    )
                  }
                  className={
                    subjectClass.payments_enabled === false
                      ? "inline-flex items-center gap-1 rounded-lg border border-emerald-500/40 px-3 py-1.5 text-sm text-emerald-700 hover:bg-emerald-500/10 dark:text-emerald-300"
                      : "inline-flex items-center gap-1 rounded-lg border border-amber-500/40 px-3 py-1.5 text-sm text-amber-700 hover:bg-amber-500/10 dark:text-amber-300"
                  }
                >
                  {subjectClass.payments_enabled === false
                    ? "Enable payments"
                    : "Disable payments"}
                </button>
                <button
                  type="button"
                  onClick={() =>
                    void toggleClassHumanMode(
                      subjectClass.id,
                      true,
                    )
                  }
                  className="inline-flex items-center gap-1 rounded-lg border border-amber-500/40 px-3 py-1.5 text-sm text-amber-700 hover:bg-amber-500/10 dark:text-amber-300"
                >
                  Disable AI for class
                </button>
                <button
                  type="button"
                  onClick={() =>
                    void toggleClassHumanMode(
                      subjectClass.id,
                      false,
                    )
                  }
                  className="inline-flex items-center gap-1 rounded-lg border border-emerald-500/40 px-3 py-1.5 text-sm text-emerald-700 hover:bg-emerald-500/10 dark:text-emerald-300"
                >
                  Enable AI for class
                </button>
                <button
                  type="button"
                  onClick={() => triggerFileInput(subjectClass.id)}
                  disabled={uploadingClassId === subjectClass.id}
                  className="inline-flex items-center gap-1 rounded-lg border border-slate-300 dark:border-slate-700 px-3 py-1.5 text-sm text-slate-800 dark:text-slate-200 hover:bg-slate-100 dark:bg-slate-800 disabled:opacity-50"
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
                  className="inline-flex items-center gap-1 rounded-lg border border-slate-300 dark:border-slate-700 px-3 py-1.5 text-sm text-slate-800 dark:text-slate-200 hover:bg-slate-100 dark:bg-slate-800"
                >
                  <Pencil className="h-4 w-4" />
                  Edit
                </button>
                <button
                  type="button"
                  onClick={() => void handleDelete(subjectClass.id)}
                  className="inline-flex items-center gap-1 rounded-lg border border-red-500/30 px-3 py-1.5 text-sm text-red-200 hover:bg-red-500/10"
                >
                  <Trash2 className="h-4 w-4" />
                  Delete
                </button>
                <Link
                  href={`/dashboard/ingest?class_id=${encodeURIComponent(subjectClass.id)}`}
                  className="inline-flex items-center gap-1 rounded-lg border border-slate-300 dark:border-slate-700 px-3 py-1.5 text-sm text-blue-300 hover:bg-slate-100 dark:bg-slate-800"
                >
                  <Upload className="h-4 w-4" />
                  Ingest
                </Link>
              </div>
            </article>
          ))}
        </div>
      )}

      {broadcastClass && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
          role="presentation"
          onClick={closeBroadcast}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="broadcast-title"
            className="w-full max-w-lg rounded-xl border border-slate-200 bg-white p-5 shadow-xl dark:border-slate-800 dark:bg-slate-900"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <h2
                  id="broadcast-title"
                  className="text-lg font-semibold text-slate-900 dark:text-white"
                >
                  Broadcast to {broadcastClass.name ?? broadcastClass.subject}
                </h2>
                <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                  Sends a Telegram message to students enrolled in this class who have
                  linked the bot.
                </p>
              </div>
              <button
                type="button"
                onClick={closeBroadcast}
                disabled={broadcastSending}
                className="rounded-lg p-1 text-slate-500 hover:bg-slate-100 disabled:opacity-50 dark:hover:bg-slate-800"
                aria-label="Close broadcast dialog"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {broadcastLoading ? (
              <div className="flex min-h-32 items-center justify-center">
                <Loader2 className="h-6 w-6 animate-spin text-slate-500" />
              </div>
            ) : (
              <form onSubmit={handleBroadcastSubmit} className="mt-4 space-y-4">
                {broadcastRecipients && (
                  <p className="text-sm text-slate-700 dark:text-slate-300">
                    {broadcastRecipients.reachable} of {broadcastRecipients.enrolled}{" "}
                    enrolled student
                    {broadcastRecipients.enrolled === 1 ? "" : "s"} will receive this
                    {broadcastRecipients.skipped_no_telegram > 0
                      ? ` (${broadcastRecipients.skipped_no_telegram} have not linked Telegram)`
                      : ""}
                    .
                    {broadcastRecipients.reachable_names.length > 0 && (
                      <span className="mt-1 block text-slate-500 dark:text-slate-400">
                        {broadcastRecipients.reachable_names.join(", ")}
                      </span>
                    )}
                  </p>
                )}

                <label className="block space-y-2">
                  <span className="text-sm text-slate-700 dark:text-slate-300">
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
                    className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 dark:border-slate-700 dark:bg-slate-950 dark:text-white"
                  />
                </label>

                {broadcastError && (
                  <div className="flex items-start gap-2 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-200">
                    <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
                    <span>{broadcastError}</span>
                  </div>
                )}

                <div className="flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={closeBroadcast}
                    disabled={broadcastSending}
                    className="rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-800 hover:bg-slate-100 disabled:opacity-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
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
                    className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
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
