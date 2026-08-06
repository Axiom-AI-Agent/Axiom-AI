"use client";

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
  Plus,
  RefreshCw,
  Upload,
  X,
} from "lucide-react";

import {
  createClass,
  getClasses,
  SubjectClass,
  uploadClassDocument,
} from "@/lib/api";

interface ClassFormState {
  subject: string;
  fee_amount: string;
  fee_cycle: string;
}

const initialForm: ClassFormState = {
  subject: "",
  fee_amount: "",
  fee_cycle: "monthly",
};

export default function ClassesPage() {
  const [classes, setClasses] = useState<SubjectClass[]>([]);
  const [form, setForm] =
    useState<ClassFormState>(initialForm);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadingClassId, setUploadingClassId] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadClasses = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      setClasses(await getClasses());
    } catch (requestError) {
      console.error(requestError);
      setError(
        "Could not load classes. Confirm the backend is running.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadClasses();
  }, [loadClasses]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const amount = Number(form.fee_amount);

    if (!form.subject.trim()) {
      setError("Enter a subject name.");
      return;
    }

    if (!Number.isFinite(amount) || amount <= 0) {
      setError("Enter a valid fee amount.");
      return;
    }

    setSaving(true);
    setError(null);

    try {
      const createdClass = await createClass({
        subject: form.subject.trim(),
        fee_amount: amount,
        fee_cycle: form.fee_cycle,
      });

      setClasses((current) => [...current, createdClass]);
      setForm(initialForm);
      setShowForm(false);
    } catch (requestError) {
      console.error(requestError);
      setError("The class could not be created.");
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
    setUploadingClassId(classId);
    setUploadError(null);

    try {
      await uploadClassDocument(classId, "tenant-demo-physics", file);
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

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">
            Classes
          </h1>
          <p className="mt-1 text-sm text-gray-400">
            View and create tuition classes.
          </p>
        </div>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => void loadClasses()}
            disabled={loading}
            className="flex items-center gap-2 rounded-lg border border-gray-700 px-4 py-2 text-sm text-gray-200 hover:bg-gray-800 disabled:opacity-50"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>

          <button
            type="button"
            onClick={() => setShowForm((current) => !current)}
            className="flex items-center gap-2 rounded-lg bg-white px-4 py-2 text-sm font-medium text-black hover:bg-gray-200"
          >
            {showForm ? (
              <X className="h-4 w-4" />
            ) : (
              <Plus className="h-4 w-4" />
            )}
            {showForm ? "Cancel" : "Add Class"}
          </button>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-200">
          <AlertTriangle className="h-5 w-5" />
          <span>{error}</span>
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
        accept=".pdf"
        className="hidden"
        onChange={(e) => {
          const classId = e.currentTarget.dataset.classId;
          if (classId) handleFileSelect(e, classId);
        }}
      />

      {showForm && (
        <form
          onSubmit={handleSubmit}
          className="grid gap-4 rounded-xl border border-gray-800 bg-gray-900 p-5 md:grid-cols-3"
        >
          <label className="space-y-2">
            <span className="text-sm text-gray-300">Subject</span>
            <input
              type="text"
              value={form.subject}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  subject: event.target.value,
                }))
              }
              placeholder="Physics"
              className="w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-white outline-none focus:border-gray-500"
            />
          </label>

          <label className="space-y-2">
            <span className="text-sm text-gray-300">
              Fee amount
            </span>
            <input
              type="number"
              min="1"
              step="0.01"
              value={form.fee_amount}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  fee_amount: event.target.value,
                }))
              }
              placeholder="5000"
              className="w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-white outline-none focus:border-gray-500"
            />
          </label>

          <label className="space-y-2">
            <span className="text-sm text-gray-300">
              Fee cycle
            </span>
            <select
              value={form.fee_cycle}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  fee_cycle: event.target.value,
                }))
              }
              className="w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-white outline-none focus:border-gray-500"
            >
              <option value="monthly">Monthly</option>
              <option value="termly">Termly</option>
              <option value="one-time">One-time</option>
            </select>
          </label>

          <div className="md:col-span-3">
            <button
              type="submit"
              disabled={saving}
              className="flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {saving && (
                <Loader2 className="h-4 w-4 animate-spin" />
              )}
              Create Class
            </button>
          </div>
        </form>
      )}

      {loading ? (
        <div className="flex min-h-48 items-center justify-center">
          <Loader2 className="h-7 w-7 animate-spin text-gray-400" />
        </div>
      ) : classes.length === 0 ? (
        <div className="rounded-xl border border-gray-800 bg-gray-900 p-10 text-center">
          <BookOpen className="mx-auto h-10 w-10 text-gray-500" />
          <p className="mt-3 text-gray-300">
            No classes have been created.
          </p>
          <p className="mt-1 text-sm text-gray-500">
            Use Add Class to create the first class.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {classes.map((subjectClass) => (
            <article
              key={subjectClass.id}
              className="rounded-xl border border-gray-800 bg-gray-900 p-5"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="text-lg font-semibold text-white">
                    {subjectClass.subject}
                  </h2>
                  <p className="mt-1 text-xs text-gray-500">
                    ID: {subjectClass.id}
                  </p>
                </div>

                <BookOpen className="h-5 w-5 text-gray-400" />
              </div>

              <dl className="mt-5 space-y-3 text-sm">
                <div className="flex justify-between gap-4">
                  <dt className="text-gray-400">Fee</dt>
                  <dd className="font-medium text-white">
                    LKR{" "}
                    {Number(
                      subjectClass.fee_amount,
                    ).toLocaleString()}
                  </dd>
                </div>

                <div className="flex justify-between gap-4">
                  <dt className="text-gray-400">Cycle</dt>
                  <dd className="capitalize text-gray-200">
                    {subjectClass.fee_cycle}
                  </dd>
                </div>

                <div className="flex justify-between gap-4">
                  <dt className="text-gray-400">Created</dt>
                  <dd className="text-right text-gray-300">
                    {new Date(
                      subjectClass.created_at,
                    ).toLocaleDateString()}
                  </dd>
                </div>
              </dl>

              <div className="mt-4">
                <button
                  type="button"
                  onClick={() => triggerFileInput(subjectClass.id)}
                  disabled={uploadingClassId === subjectClass.id}
                  className="flex w-full items-center justify-center gap-2 rounded-lg border border-gray-700 px-3 py-2 text-sm text-gray-200 hover:bg-gray-800 disabled:opacity-50"
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
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
