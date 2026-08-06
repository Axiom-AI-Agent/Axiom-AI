"use client";

import Link from "next/link";
import {
  MessageSquare,
  Pencil,
  Trash2,
  UserPlus,
} from "lucide-react";

import { Student } from "@/lib/api";

interface StudentTableProps {
  students: Student[];
  onEdit: (student: Student) => void;
  onEnroll: (student: Student) => void;
  onDelete: (studentId: string) => void;
}

export default function StudentTable({
  students,
  onEdit,
  onEnroll,
  onDelete,
}: StudentTableProps) {
  return (
    <div className="overflow-x-auto rounded-xl border border-gray-800 bg-gray-950">
      <table className="min-w-full divide-y divide-gray-800">
        <thead className="bg-gray-900">
          <tr className="text-left text-xs uppercase tracking-wide text-gray-400">
            <th className="px-5 py-4 font-medium">Name</th>
            <th className="px-5 py-4 font-medium">Phone</th>
            <th className="px-5 py-4 font-medium">District</th>
            <th className="px-5 py-4 font-medium">Language</th>
            <th className="min-w-[220px] px-5 py-4 font-medium">
              Registered classes
            </th>
            <th className="px-5 py-4 font-medium">Joined</th>
            <th className="px-5 py-4 text-right font-medium">Actions</th>
          </tr>
        </thead>

        <tbody className="divide-y divide-gray-800">
          {students.map((student) => (
            <tr key={student.id} className="hover:bg-gray-900/70">
              <td className="px-5 py-4 align-top">
                <p className="text-sm font-medium text-white">
                  {student.name?.trim() || "Unnamed"}
                </p>
                <p className="mt-1 font-mono text-xs text-gray-500">
                  {student.id}
                </p>
              </td>

              <td className="px-5 py-4 align-top text-sm text-gray-300">
                {student.phone}
              </td>

              <td className="px-5 py-4 align-top text-sm text-gray-400">
                {student.district?.trim() || "—"}
              </td>

              <td className="px-5 py-4 align-top text-sm uppercase text-gray-400">
                {student.language_pref || "en"}
              </td>

              <td className="px-5 py-4 align-top">
                {student.enrollments && student.enrollments.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {student.enrollments.map((enrollment) => (
                      <span
                        key={enrollment.id}
                        className="inline-flex items-center rounded-full border border-indigo-500/20 bg-indigo-500/10 px-2.5 py-1 text-xs text-indigo-200"
                      >
                        {enrollment.class_subject ??
                          enrollment.class_name ??
                          enrollment.class_id}
                        <span className="ml-1.5 capitalize text-indigo-400/70">
                          {enrollment.status}
                        </span>
                      </span>
                    ))}
                  </div>
                ) : (
                  <span className="text-sm text-gray-500">Not enrolled</span>
                )}
              </td>

              <td className="px-5 py-4 align-top text-sm text-gray-400">
                {student.created_at
                  ? new Date(student.created_at).toLocaleDateString()
                  : "—"}
              </td>

              <td className="px-5 py-4 align-top">
                <div className="flex flex-wrap justify-end gap-1.5">
                  <Link
                    href={`/dashboard/messages?phone=${encodeURIComponent(student.phone)}`}
                    className="inline-flex items-center gap-1 rounded-md border border-gray-700 px-2.5 py-1.5 text-xs text-gray-200 hover:bg-gray-800"
                  >
                    <MessageSquare className="h-3.5 w-3.5" />
                    Chat
                  </Link>

                  <button
                    type="button"
                    onClick={() => onEnroll(student)}
                    className="inline-flex items-center gap-1 rounded-md border border-gray-700 px-2.5 py-1.5 text-xs text-gray-200 hover:bg-gray-800"
                  >
                    <UserPlus className="h-3.5 w-3.5" />
                    Enroll
                  </button>

                  <button
                    type="button"
                    onClick={() => onEdit(student)}
                    className="inline-flex items-center gap-1 rounded-md border border-gray-700 px-2.5 py-1.5 text-xs text-gray-200 hover:bg-gray-800"
                  >
                    <Pencil className="h-3.5 w-3.5" />
                    Edit
                  </button>

                  <button
                    type="button"
                    onClick={() => onDelete(student.id)}
                    className="inline-flex items-center gap-1 rounded-md border border-red-500/30 px-2.5 py-1.5 text-xs text-red-200 hover:bg-red-500/10"
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
