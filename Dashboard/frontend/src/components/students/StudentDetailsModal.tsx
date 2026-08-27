"use client";

import Link from "next/link";
import {
  MessageSquare,
  Pencil,
  Trash2,
  UserPlus,
} from "lucide-react";

import SageCheck from "@/components/SageCheck";
import Modal from "@/components/ui/Modal";
import ToggleSwitch from "@/components/ui/ToggleSwitch";
import { OnboardingFieldDefinition, Student } from "@/lib/api";
import { btnDanger, btnQuiet, surfaceCard } from "@/lib/ui";
import { cn } from "@/lib/utils";
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
    <Modal
      open
      onClose={onClose}
      title={student.name?.trim() || "Unnamed Student"}
      description={student.id}
      footer={
        <div className="grid w-full grid-cols-2 gap-2 sm:flex sm:flex-wrap sm:justify-end">
          <Link
            href={`/dashboard/messages?phone=${encodeURIComponent(student.phone)}`}
            className={btnQuiet}
          >
            <MessageSquare className="h-4 w-4" />
            Chat
          </Link>
          <button
            type="button"
            onClick={() => {
              onEnroll(student);
              onClose();
            }}
            className={btnQuiet}
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
            className={btnQuiet}
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
            className={cn(btnDanger, "col-span-2 sm:col-span-1")}
          >
            <Trash2 className="h-4 w-4" />
            Delete
          </button>
        </div>
      }
    >
      <div className="space-y-6">
          <section className={`${surfaceCard} p-4`}>
            <ToggleSwitch
              label="AI responses"
              description={
                student.human_mode
                  ? "Human mode is on — staff handle replies for this student."
                  : "AI is handling replies for this student."
              }
              checked={!student.human_mode}
              onChange={() => {
                onToggleHumanMode(student);
              }}
            />
            {!student.human_mode ? (
              <p className="mt-2 inline-flex items-center gap-1 text-xs text-sage">
                <SageCheck label="AI handling" />
                AI active
              </p>
            ) : null}
          </section>

          <section>
            <h3 className="mb-3 text-sm font-semibold text-heading">
              Contact Information
            </h3>
            <div className="space-y-3 text-sm">
              <div className="flex flex-col gap-1 sm:flex-row sm:justify-between">
                <span className="text-muted">Phone number</span>
                <span className="font-medium tabular text-fg">
                  {student.phone}
                </span>
              </div>
              <div className="flex flex-col gap-1 sm:flex-row sm:justify-between">
                <span className="text-muted">Language preference</span>
                <span className="font-medium uppercase text-fg">
                  {student.language_pref || "en"}
                </span>
              </div>
            </div>
          </section>

          {fields.length > 0 ? (
            <section>
              <h3 className="mb-3 text-sm font-semibold text-heading">
                Additional Details
              </h3>
              <div className="space-y-3 text-sm">
                {fields.map((field) => (
                  <div
                    key={field.field_key}
                    className="flex flex-col gap-1 sm:flex-row sm:justify-between"
                  >
                    <span className="text-muted">{field.label}</span>
                    <span className="font-medium text-fg">
                      {formatStudentFieldValue(student, field) || "—"}
                    </span>
                  </div>
                ))}
              </div>
            </section>
          ) : null}

          <section>
            <h3 className="mb-3 text-sm font-semibold text-heading">
              Registered Classes
            </h3>
            {Array.isArray(student.enrollments) &&
            student.enrollments.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {student.enrollments.map((enrollment) => (
                    <span
                      key={enrollment.id}
                      className="inline-flex items-center rounded-md border border-border px-3 py-1 text-sm font-medium text-fg"
                    >
                      {enrollment.class_subject ??
                        enrollment.class_name ??
                        enrollment.class_id}
                      <span className="ml-2 capitalize text-muted">
                        {enrollment.status}
                      </span>
                    </span>
                ))}
              </div>
            ) : (
              <p className="text-sm italic text-muted">
                Not enrolled in any classes.
              </p>
            )}
          </section>
        </div>
    </Modal>
  );
}
