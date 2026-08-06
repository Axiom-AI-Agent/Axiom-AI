"use client";

import Link from "next/link";
import {
  FormEvent,
  useCallback,
  useEffect,
  useState,
} from "react";
import {
  AlertTriangle,
  BookOpen,
  Loader2,
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
  createClass,
  deleteClass,
  getClasses,
  SubjectClass,
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

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">Classes</h1>
          <p className="mt-1 text-sm text-gray-400">
            Create and manage tuition classes for this tenant.
          </p>
        </div>

        <div className="flex gap-2">
          <Link
            href="/dashboard/ingest"
            className="flex items-center gap-2 rounded-lg border border-gray-700 px-4 py-2 text-sm text-gray-200 hover:bg-gray-800"
          >
            <Upload className="h-4 w-4" />
            Upload notes
          </Link>

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

      {showForm && (
        <form
          onSubmit={handleSubmit}
          className="grid gap-4 rounded-xl border border-gray-800 bg-gray-900 p-5 md:grid-cols-2 xl:grid-cols-3"
        >
          <label className="space-y-2">
            <span className="text-sm text-gray-300">Subject</span>
            <input
              required
              value={form.subject}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  subject: event.target.value,
                }))
              }
              className="w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-white"
            />
          </label>

          <label className="space-y-2">
            <span className="text-sm text-gray-300">Display name</span>
            <input
              value={form.name}
              onChange={(event) =>
                setForm((current) => ({ ...current, name: event.target.value }))
              }
              className="w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-white"
            />
          </label>

          <label className="space-y-2">
            <span className="text-sm text-gray-300">Grade</span>
            <input
              value={form.grade}
              onChange={(event) =>
                setForm((current) => ({ ...current, grade: event.target.value }))
              }
              className="w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-white"
            />
          </label>

          <label className="space-y-2">
            <span className="text-sm text-gray-300">Fee amount (LKR)</span>
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
              className="w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-white"
            />
          </label>

          <label className="space-y-2">
            <span className="text-sm text-gray-300">Fee cycle</span>
            <select
              value={form.fee_cycle}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  fee_cycle: event.target.value,
                }))
              }
              className="w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-white"
            >
              <option value="monthly">Monthly</option>
              <option value="termly">Termly</option>
              <option value="annual">Annual</option>
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
          <Loader2 className="h-7 w-7 animate-spin text-gray-400" />
        </div>
      ) : classes.length === 0 ? (
        <div className="rounded-xl border border-gray-800 bg-gray-900 p-10 text-center">
          <BookOpen className="mx-auto h-10 w-10 text-gray-500" />
          <p className="mt-3 text-gray-300">No classes yet.</p>
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
                    {subjectClass.name ?? subjectClass.subject}
                  </h2>
                  <p className="text-sm text-gray-400">{subjectClass.subject}</p>
                  {subjectClass.grade && (
                    <p className="mt-1 text-xs text-gray-500">
                      Grade {subjectClass.grade}
                    </p>
                  )}
                </div>
                <BookOpen className="h-5 w-5 text-gray-400" />
              </div>

              <dl className="mt-5 space-y-2 text-sm">
                <div className="flex justify-between gap-4">
                  <dt className="text-gray-400">Fee</dt>
                  <dd className="text-white">
                    LKR {Number(subjectClass.fee_amount ?? 0).toLocaleString()}
                  </dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-gray-400">Cycle</dt>
                  <dd className="capitalize text-gray-200">
                    {subjectClass.fee_cycle}
                  </dd>
                </div>
              </dl>

              <div className="mt-5 flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => openEditForm(subjectClass)}
                  className="inline-flex items-center gap-1 rounded-lg border border-gray-700 px-3 py-1.5 text-sm text-gray-200 hover:bg-gray-800"
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
                  className="inline-flex items-center gap-1 rounded-lg border border-gray-700 px-3 py-1.5 text-sm text-indigo-300 hover:bg-gray-800"
                >
                  <Upload className="h-4 w-4" />
                  Ingest
                </Link>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
