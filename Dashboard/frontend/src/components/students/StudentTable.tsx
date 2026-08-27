"use client";

import ToggleSwitch from "@/components/ui/ToggleSwitch";
import { OnboardingFieldDefinition, Student } from "@/lib/api";
import { surfaceCard } from "@/lib/ui";
import { cn } from "@/lib/utils";
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
  onToggleHumanMode,
  onRowClick,
}: StudentTableProps) {
  return (
    <div className={cn(surfaceCard, "min-h-0 flex-1 overflow-auto")}>
      <table className="min-w-full divide-y divide-border">
        <thead className="sticky top-0 z-10 bg-surface">
          <tr className="text-left text-xs uppercase tracking-wider text-muted">
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
            <th className="min-w-[160px] px-5 py-4 font-medium">AI mode</th>
            <th className="px-5 py-4 font-medium">Joined</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {students.map((student) => {
            const aiEnabled = !student.human_mode;

            return (
              <tr
                key={student.id}
                onClick={() => onRowClick(student)}
                className="cursor-pointer transition-colors hover:bg-hover"
              >
                <td className="px-5 py-4 align-middle">
                  <p className="text-sm font-medium text-heading">
                    {student.name?.trim() || "Unnamed"}
                  </p>
                  <p className="mt-1 font-mono text-xs tabular text-muted">
                    {student.id}
                  </p>
                </td>
                {fields.map((field) => (
                  <td
                    key={field.field_key}
                    className="px-5 py-4 align-middle text-sm text-muted"
                  >
                    {formatStudentFieldValue(student, field)}
                  </td>
                ))}
                <td className="px-5 py-4 align-middle text-sm uppercase text-muted">
                  {student.language_pref || "en"}
                </td>
                <td className="px-5 py-4 align-middle">
                  {Array.isArray(student.enrollments) &&
                  student.enrollments.length > 0 ? (
                    <div className="flex flex-wrap gap-1.5">
                      {student.enrollments.map((enrollment) => (
                        <span
                          key={enrollment.id}
                          className="inline-flex items-center rounded-md border border-border px-2.5 py-1 text-xs font-medium text-fg"
                        >
                          {enrollment.class_subject ??
                            enrollment.class_name ??
                            enrollment.class_id}
                          <span className="ml-1.5 capitalize text-muted">
                            {enrollment.status}
                          </span>
                        </span>
                      ))}
                    </div>
                  ) : (
                    <span className="text-sm italic text-muted">
                      Not enrolled
                    </span>
                  )}
                </td>
                <td
                  className="px-5 py-4 align-middle"
                  onClick={(event) => event.stopPropagation()}
                >
                  <ToggleSwitch
                    size="sm"
                    label={aiEnabled ? "AI on" : "Human"}
                    checked={aiEnabled}
                    onChange={() => onToggleHumanMode(student)}
                    className="min-w-[8.5rem]"
                  />
                </td>
                <td className="px-5 py-4 align-middle text-sm tabular text-muted">
                  {student.created_at
                    ? new Date(student.created_at).toLocaleDateString()
                    : "—"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
