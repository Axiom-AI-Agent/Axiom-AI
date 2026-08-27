"use client";

import Link from "next/link";
import {
  MessageSquare,
  Pencil,
  Trash2,
  UserPlus,
  X,
} from "lucide-react";

import { OnboardingFieldDefinition, Student } from "@/lib/api";
import { formatStudentFieldValue } from "./extraFields";

interface StudentDetailsModalProps {
  student: Student;
  fields: OnboardingFieldDefinition[];
  onClose: () => void;
  onEdit: (student: Student) => void;
  onEnroll: (student: Student) => void;
  onDelete: (studentId: string) => void;
  onToggleHumanMode: (student: Student) => void;
}

export default function StudentDetailsModal({
  student,
  fields,
  onClose,
  onEdit,
  onEnroll,
  onDelete,
  onToggleHumanMode,
}: StudentDetailsModalProps) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      role="presentation"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        className="w-full max-w-lg rounded-xl border border-slate-200 bg-white p-6 shadow-xl dark:border-slate-800 dark:bg-slate-900 flex flex-col max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-4 shrink-0">
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">
              {student.name?.trim() || "Unnamed Student"}
            </h2>
            <p className="mt-1 font-mono text-sm text-slate-500 dark:text-slate-400">
              {student.id}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            aria-label="Close dialog"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="py-5 flex-1 overflow-y-auto space-y-6">
          <section>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-3">Contact Information</h3>
            <div className="space-y-3 text-sm">
              <div className="flex flex-col sm:flex-row sm:justify-between gap-1">
                <span className="text-slate-500 dark:text-slate-400">Phone number</span>
                <span className="font-medium text-slate-900 dark:text-white">{student.phone}</span>
              </div>
              <div className="flex flex-col sm:flex-row sm:justify-between gap-1">
                <span className="text-slate-500 dark:text-slate-400">Language preference</span>
                <span className="font-medium text-slate-900 dark:text-white uppercase">{student.language_pref || "en"}</span>
              </div>
            </div>
          </section>

          {fields.length > 0 && (
            <section>
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-3">Additional Details</h3>
              <div className="space-y-3 text-sm">
                {fields.map((field) => (
                  <div key={field.field_key} className="flex flex-col sm:flex-row sm:justify-between gap-1">
                    <span className="text-slate-500 dark:text-slate-400">{field.label}</span>
                    <span className="font-medium text-slate-900 dark:text-white">
                      {formatStudentFieldValue(student, field) || "—"}
                    </span>
                  </div>
                ))}
              </div>
            </section>
          )}

          <section>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-3">Registered Classes</h3>
            {Array.isArray(student.enrollments) && student.enrollments.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {student.enrollments.map((enrollment) => (
                  <span
                    key={enrollment.id}
                    className="inline-flex items-center rounded-full border border-blue-200 dark:border-blue-500/20 bg-blue-50 dark:bg-blue-500/10 px-3 py-1 text-sm font-medium text-blue-700 dark:text-blue-300"
                  >
                    {enrollment.class_subject ?? enrollment.class_name ?? enrollment.class_id}
                    <span className="ml-2 capitalize text-blue-500 dark:text-blue-400/70">
                      {enrollment.status}
                    </span>
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500 dark:text-slate-400 italic">Not enrolled in any classes.</p>
            )}
          </section>
        </div>

        <div className="pt-4 border-t border-slate-100 dark:border-slate-800 shrink-0">
          <div className="grid grid-cols-2 gap-2 sm:flex sm:flex-wrap sm:justify-end">
            <Link
              href={`/dashboard/messages?phone=${encodeURIComponent(student.phone)}`}
              className="inline-flex justify-center items-center gap-2 rounded-lg border border-slate-200 dark:border-slate-700 px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
            >
              <MessageSquare className="h-4 w-4" />
              Chat
            </Link>
            
            <button
              type="button"
              onClick={() => {
                onToggleHumanMode(student);
                onClose();
              }}
              className={`inline-flex justify-center items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium transition-colors ${
                student.human_mode
                  ? "border-amber-200 bg-amber-50 text-amber-700 hover:bg-amber-100 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300 dark:hover:bg-amber-500/20"
                  : "border-emerald-200 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300 dark:hover:bg-emerald-500/20"
              }`}
            >
              {student.human_mode ? "Human mode" : "AI active"}
            </button>
            
            <button
              type="button"
              onClick={() => {
                onEnroll(student);
                onClose();
              }}
              className="inline-flex justify-center items-center gap-2 rounded-lg border border-slate-200 dark:border-slate-700 px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
            >
              <UserPlus className="h-4 w-4" />
              Enroll
            </button>

            <button
              type="button"
              onClick={() => {
                onEdit(student);
                onClose();
              }}
              className="inline-flex justify-center items-center gap-2 rounded-lg border border-slate-200 dark:border-slate-700 px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
            >
              <Pencil className="h-4 w-4" />
              Edit
            </button>

            <button
              type="button"
              onClick={() => {
                onDelete(student.id);
                onClose();
              }}
              className="col-span-2 sm:col-span-1 inline-flex justify-center items-center gap-2 rounded-lg border border-red-200 dark:border-red-500/30 px-4 py-2 text-sm font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
            >
              <Trash2 className="h-4 w-4" />
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
