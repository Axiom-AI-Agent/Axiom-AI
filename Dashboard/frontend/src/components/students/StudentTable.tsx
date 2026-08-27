"use client";

import Link from "next/link";
import {
  MessageSquare,
  Pencil,
  Trash2,
  UserPlus,
} from "lucide-react";

import { OnboardingFieldDefinition, Student } from "@/lib/api";

import { formatStudentFieldValue } from "./extraFields";

interface StudentTableProps {
  students: Student[];
  fields: OnboardingFieldDefinition[];
  onEdit: (student: Student) => void;
  onEnroll: (student: Student) => void;
  onDelete: (studentId: string) => void;
  onToggleHumanMode: (student: Student) => void;
}

export default function StudentTable({
  students,
  fields,
  onEdit,
  onEnroll,
  onDelete,
  onToggleHumanMode,
}: StudentTableProps) {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm">
      <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
        <thead className="bg-slate-50 dark:bg-slate-800/50">
          <tr className="text-left text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400">
            <th className="px-5 py-4 font-medium">Name</th>
            <th className="px-5 py-4 font-medium">Phone</th>
            {fields.map((field) => (
              <th key={field.field_key} className="px-5 py-4 font-medium">
                {field.label}
              </th>
            ))}
            <th className="px-5 py-4 font-medium">Language</th>
            <th className="min-w-[220px] px-5 py-4 font-medium">
              Registered classes
            </th>
            <th className="px-5 py-4 font-medium">Joined</th>
            <th className="px-5 py-4 text-right font-medium">Actions</th>
          </tr>
        </thead>

        <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
          {students.map((student) => (
            <tr key={student.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
              <td className="px-5 py-4 align-top">
                <p className="text-sm font-medium text-slate-900 dark:text-white">
                  {student.name?.trim() || "Unnamed"}
                </p>
                <p className="mt-1 font-mono text-xs text-slate-500 dark:text-slate-400">
                  {student.id}
                </p>
              </td>

              <td className="px-5 py-4 align-top text-sm text-slate-700 dark:text-slate-300">
                {student.phone}
              </td>

              {fields.map((field) => (
                <td
                  key={field.field_key}
                  className="px-5 py-4 align-top text-sm text-slate-600 dark:text-slate-400"
                >
                  {formatStudentFieldValue(student, field)}
                </td>
              ))}

              <td className="px-5 py-4 align-top text-sm uppercase text-slate-600 dark:text-slate-400">
                {student.language_pref || "en"}
              </td>

              <td className="px-5 py-4 align-top">
                {Array.isArray(student.enrollments) &&
                student.enrollments.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {student.enrollments.map((enrollment) => (
                      <span
                        key={enrollment.id}
                        className="inline-flex items-center rounded-full border border-blue-200 dark:border-blue-500/20 bg-blue-50 dark:bg-blue-500/10 px-2.5 py-1 text-xs font-medium text-blue-700 dark:text-blue-300"
                      >
                        {enrollment.class_subject ??
                          enrollment.class_name ??
                          enrollment.class_id}
                        <span className="ml-1.5 capitalize text-blue-500 dark:text-blue-400/70">
                          {enrollment.status}
                        </span>
                      </span>
                    ))}
                  </div>
                ) : (
                  <span className="text-sm text-slate-500 dark:text-slate-400 italic">Not enrolled</span>
                )}
              </td>

              <td className="px-5 py-4 align-top text-sm text-slate-600 dark:text-slate-400">
                {student.created_at
                  ? new Date(student.created_at).toLocaleDateString()
                  : "—"}
              </td>

              <td className="px-5 py-4 align-top">
                <div className="flex flex-wrap justify-end gap-1.5">
                  <Link
                    href={`/dashboard/messages?phone=${encodeURIComponent(student.phone)}`}
                    className="inline-flex items-center gap-1 rounded-md border border-slate-200 dark:border-slate-700 px-2.5 py-1.5 text-xs font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700/50 bg-white dark:bg-transparent shadow-sm transition-colors"
                  >
                    <MessageSquare className="h-3.5 w-3.5" />
                    Chat
                  </Link>
                  <button
                    type="button"
                    onClick={() => onToggleHumanMode(student)}
                    title={
                      student.human_mode
                        ? "AI replies are disabled for this student"
                        : "AI replies are enabled for this student"
                    }
                    className={`inline-flex items-center gap-1 rounded-md border px-2.5 py-1.5 text-xs font-medium shadow-sm transition-colors ${
                      student.human_mode
                        ? "border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100 dark:border-blue-500/30 dark:bg-blue-500/10 dark:text-blue-300 dark:hover:bg-blue-500/20"
                        : "border-emerald-200 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300 dark:hover:bg-emerald-500/20"
                    }`}
                  >
                    {student.human_mode
                      ? "Human mode"
                      : "AI active"}
                  </button>
                  <button
                    type="button"
                    onClick={() => onEnroll(student)}
                    className="inline-flex items-center gap-1 rounded-md border border-slate-200 dark:border-slate-700 px-2.5 py-1.5 text-xs font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700/50 bg-white dark:bg-transparent shadow-sm transition-colors"
                  >
                    <UserPlus className="h-3.5 w-3.5" />
                    Enroll
                  </button>

                  <button
                    type="button"
                    onClick={() => onEdit(student)}
                    className="inline-flex items-center gap-1 rounded-md border border-slate-200 dark:border-slate-700 px-2.5 py-1.5 text-xs font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700/50 bg-white dark:bg-transparent shadow-sm transition-colors"
                  >
                    <Pencil className="h-3.5 w-3.5" />
                    Edit
                  </button>

                  <button
                    type="button"
                    onClick={() => onDelete(student.id)}
                    className="inline-flex items-center gap-1 rounded-md border border-red-200 dark:border-red-500/30 px-2.5 py-1.5 text-xs font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 bg-white dark:bg-transparent shadow-sm transition-colors"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
