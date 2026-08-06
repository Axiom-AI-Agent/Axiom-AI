"use client";

import { FormEvent } from "react";
import { Loader2, X } from "lucide-react";

import { Student, SubjectClass } from "@/lib/api";

interface EnrollModalProps {
  student: Student;
  classes: SubjectClass[];
  classId: string;
  saving: boolean;
  onClose: () => void;
  onChange: (classId: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}

export default function EnrollModal({
  student,
  classes,
  classId,
  saving,
  onClose,
  onChange,
  onSubmit,
}: EnrollModalProps) {
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
        className="relative z-10 w-full max-w-md rounded-xl border border-gray-700 bg-gray-900 p-6 shadow-2xl"
      >
        <div className="mb-5 flex items-start justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-white">Enroll student</h2>
            <p className="mt-1 text-sm text-gray-400">
              {student.name ?? student.phone}
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-2 text-gray-400 hover:bg-gray-800 hover:text-white"
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          <label className="block space-y-2">
            <span className="text-sm text-gray-300">Class</span>
            <select
              required
              value={classId}
              onChange={(event) => onChange(event.target.value)}
              className="w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-white outline-none focus:border-indigo-500"
            >
              <option value="">Select a class</option>
              {classes.map((subjectClass) => (
                <option key={subjectClass.id} value={subjectClass.id}>
                  {subjectClass.subject}
                </option>
              ))}
            </select>
          </label>

          <div className="flex justify-end gap-2 border-t border-gray-800 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-gray-700 px-4 py-2 text-sm text-gray-200 hover:bg-gray-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving || !classId}
              className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500 disabled:opacity-50"
            >
              {saving && <Loader2 className="h-4 w-4 animate-spin" />}
              Enroll
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
