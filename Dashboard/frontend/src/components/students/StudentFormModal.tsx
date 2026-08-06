"use client";

import { FormEvent } from "react";
import { Loader2, X } from "lucide-react";

import { SubjectClass } from "@/lib/api";

export interface StudentFormState {
  name: string;
  phone: string;
  district: string;
  language_pref: string;
  class_id: string;
}

interface StudentFormModalProps {
  mode: "create" | "edit";
  form: StudentFormState;
  saving: boolean;
  classes: SubjectClass[];
  onClose: () => void;
  onChange: (form: StudentFormState) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}

export default function StudentFormModal({
  mode,
  form,
  saving,
  classes,
  onClose,
  onChange,
  onSubmit,
}: StudentFormModalProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <button
        type="button"
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
        aria-label="Close dialog"
      />

      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="student-form-title"
        className="relative z-10 w-full max-w-lg rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-2xl"
      >
        <div className="mb-5 flex items-start justify-between gap-4">
          <div>
            <h2
              id="student-form-title"
              className="text-lg font-semibold text-slate-900 dark:text-white"
            >
              {mode === "create" ? "Add student" : "Edit student"}
            </h2>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              {mode === "create"
                ? "Create a new student record."
                : "Update this student's profile."}
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-600 dark:hover:text-white transition-colors"
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          <label className="block space-y-2">
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Name</span>
            <input
              value={form.name}
              onChange={(event) =>
                onChange({ ...form, name: event.target.value })
              }
              className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 px-3 py-2 text-slate-900 dark:text-white outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors shadow-sm"
            />
          </label>

          <label className="block space-y-2">
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Phone</span>
            <input
              required
              value={form.phone}
              onChange={(event) =>
                onChange({ ...form, phone: event.target.value })
              }
              className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 px-3 py-2 text-slate-900 dark:text-white outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors shadow-sm"
            />
          </label>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block space-y-2">
              <span className="text-sm font-medium text-slate-700 dark:text-slate-300">District</span>
              <input
                value={form.district}
                onChange={(event) =>
                  onChange({ ...form, district: event.target.value })
                }
                className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 px-3 py-2 text-slate-900 dark:text-white outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors shadow-sm"
              />
            </label>

            <label className="block space-y-2">
              <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Language</span>
              <select
                value={form.language_pref}
                onChange={(event) =>
                  onChange({ ...form, language_pref: event.target.value })
                }
                className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 px-3 py-2 text-slate-900 dark:text-white outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors shadow-sm"
              >
                <option value="en">English</option>
                <option value="si">Sinhala</option>
                <option value="ta">Tamil</option>
              </select>
            </label>
          </div>

          {mode === "create" && (
            <label className="block space-y-2">
              <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Initial class</span>
              <select
                value={form.class_id}
                onChange={(event) =>
                  onChange({ ...form, class_id: event.target.value })
                }
                className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 px-3 py-2 text-slate-900 dark:text-white outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors shadow-sm"
              >
                <option value="">No enrollment yet</option>
                {classes.map((subjectClass) => (
                  <option key={subjectClass.id} value={subjectClass.id}>
                    {subjectClass.subject}
                  </option>
                ))}
              </select>
            </label>
          )}

          <div className="flex justify-end gap-2 border-t border-slate-200 dark:border-slate-800 pt-5 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-slate-200 dark:border-slate-700 px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 shadow-sm transition-colors"
            >
              {saving && <Loader2 className="h-4 w-4 animate-spin" />}
              {mode === "create" ? "Create student" : "Save changes"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
