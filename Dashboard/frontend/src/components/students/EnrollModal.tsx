"use client";

import { FormEvent } from "react";
import { Loader2 } from "lucide-react";

import Modal from "@/components/ui/Modal";
import { Student, SubjectClass } from "@/lib/api";
import { btnPrimary, btnQuiet, inputClass } from "@/lib/ui";

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
    <Modal
      open
      onClose={onClose}
      title="Enroll student"
      description={student.name ?? student.phone}
    >
      <form onSubmit={onSubmit} className="space-y-4">
        <label className="block space-y-2">
          <span className="text-sm font-medium text-fg">Class</span>
          <select
            required
            value={classId}
            onChange={(event) => onChange(event.target.value)}
            className={inputClass}
          >
            <option value="">Select a class</option>
            {classes.map((subjectClass) => (
              <option key={subjectClass.id} value={subjectClass.id}>
                {subjectClass.subject}
              </option>
            ))}
          </select>
        </label>

        <div className="flex justify-end gap-2 border-t border-border pt-4">
          <button type="button" onClick={onClose} className={btnQuiet}>
            Cancel
          </button>
          <button
            type="submit"
            disabled={saving || !classId}
            className={btnPrimary}
          >
            {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            Enroll
          </button>
        </div>
      </form>
    </Modal>
  );
}
