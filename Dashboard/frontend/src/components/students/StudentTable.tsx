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
  onRowClick: (student: Student) => void;
}

export default function StudentTable({
  students,
  fields,
  onEdit,
  onEnroll,
  onDelete,
  onToggleHumanMode,
  onRowClick,
}: StudentTableProps) {
  return (
    <div className="flex-1 min-h-0 overflow-auto rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm">
      <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
        <thead className="sticky top-0 z-10 bg-slate-50 dark:bg-slate-800/90 backdrop-blur-sm shadow-sm">
          <tr className="text-left text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400">
            <th className="px-5 py-4 font-medium">Name</th>
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
          </tr>
        </thead>

        <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
          {students.map((student) => (
            <tr 
              key={student.id} 
              onClick={() => onRowClick(student)}
              className="cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
            >
              <td className="px-5 py-4 align-top">
                <p className="text-sm font-medium text-slate-900 dark:text-white">
                  {student.name?.trim() || "Unnamed"}
                </p>
                <p className="mt-1 font-mono text-xs text-slate-500 dark:text-slate-400">
                  {student.id}
                </p>
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
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
