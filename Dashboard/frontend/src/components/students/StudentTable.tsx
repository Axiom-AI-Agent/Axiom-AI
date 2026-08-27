"use client";

import AttentionGlow from "@/components/AttentionGlow";
import { OnboardingFieldDefinition, Student } from "@/lib/api";
import { surfaceCard } from "@/lib/ui";
import { cn } from "@/lib/utils";
import { formatStudentFieldValue } from "./extraFields";
import { studentNeedsAttention } from "./attention";

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
            <th className="px-5 py-4 font-medium">Joined</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {students.map((student) => {
            const attention = studentNeedsAttention(student);
            return (
              <tr
                key={student.id}
                onClick={() => onRowClick(student)}
                className="cursor-pointer transition-colors hover:bg-hover"
              >
                <td className="px-5 py-4 align-top">
                  <AttentionGlow active={attention} className="rounded-md">
                    <div className="px-1">
                      <p className="text-sm font-medium text-heading">
                        {student.name?.trim() || "Unnamed"}
                      </p>
                      <p className="mt-1 font-mono text-xs tabular text-muted">
                        {student.id}
                      </p>
                    </div>
                  </AttentionGlow>
                </td>
                {fields.map((field) => (
                  <td
                    key={field.field_key}
                    className="px-5 py-4 align-top text-sm text-muted"
                  >
                    {formatStudentFieldValue(student, field)}
                  </td>
                ))}
                <td className="px-5 py-4 align-top text-sm uppercase text-muted">
                  {student.language_pref || "en"}
                </td>
                <td className="px-5 py-4 align-top">
                  {Array.isArray(student.enrollments) &&
                  student.enrollments.length > 0 ? (
                    <div className="flex flex-wrap gap-1.5">
                      {student.enrollments.map((enrollment) => {
                        const pending = enrollment.status === "pending";
                        return (
                          <span
                            key={enrollment.id}
                            className={cn(
                              "inline-flex items-center rounded-md border border-border px-2.5 py-1 text-xs font-medium text-fg",
                              pending && "attention-glow border-ember/40",
                            )}
                          >
                            {enrollment.class_subject ??
                              enrollment.class_name ??
                              enrollment.class_id}
                            <span className="ml-1.5 capitalize text-muted">
                              {enrollment.status}
                            </span>
                          </span>
                        );
                      })}
                    </div>
                  ) : (
                    <span className="text-sm italic text-muted">
                      Not enrolled
                    </span>
                  )}
                </td>
                <td className="px-5 py-4 align-top text-sm tabular text-muted">
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
