"use client";

import { FormEvent } from "react";
import { Loader2 } from "lucide-react";

import Modal from "@/components/ui/Modal";
import { OnboardingFieldDefinition, SubjectClass } from "@/lib/api";
import { btnPrimary, btnQuiet, inputClass } from "@/lib/ui";

export interface StudentFormState {
  name: string;
  phone: string;
  language_pref: string;
  class_id: string;
  extra_fields: Record<string, string>;
}

interface StudentFormModalProps {
  mode: "create" | "edit";
  form: StudentFormState;
  saving: boolean;
  classes: SubjectClass[];
  fields: OnboardingFieldDefinition[];
  onClose: () => void;
  onChange: (form: StudentFormState) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}

function ExtraFieldInput({
  field,
  value,
  onChange,
}: {
  field: OnboardingFieldDefinition;
  value: string;
  onChange: (value: string) => void;
}) {
  const label = (
    <span className="text-sm font-medium text-fg">
      {field.label}
      {field.required ? <span className="text-blue"> *</span> : null}
    </span>
  );

  if (field.field_type === "boolean") {
    return (
      <label className="flex items-center gap-3 rounded-md border border-border px-3 py-2">
        <input
          type="checkbox"
          checked={value === "true"}
          onChange={(event) =>
            onChange(event.target.checked ? "true" : "false")
          }
          className="h-4 w-4 rounded-sm border-border text-blue focus:ring-indigo-soft"
        />
        {label}
      </label>
    );
  }

  if (field.field_type === "select") {
    return (
      <label className="block space-y-2">
        {label}
        <select
          required={field.required}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          className={inputClass}
        >
          <option value="">{field.required ? "Select…" : "Not set"}</option>
          {(field.options ?? []).map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </label>
    );
  }

  const inputType =
    field.field_type === "number"
      ? "number"
      : field.field_type === "date"
        ? "date"
        : "text";

  return (
    <label className="block space-y-2">
      {label}
      <input
        type={inputType}
        required={field.required}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className={inputClass}
      />
    </label>
  );
}

export default function StudentFormModal({
  mode,
  form,
  saving,
  classes,
  fields,
  onClose,
  onChange,
  onSubmit,
}: StudentFormModalProps) {
  return (
    <Modal
      open
      onClose={onClose}
      title={mode === "create" ? "Add student" : "Edit student"}
      description={
        mode === "create"
          ? "Create a new student record."
          : "Update this student's profile."
      }
    >
      <form id="student-form" onSubmit={onSubmit} className="space-y-4">
        <label className="block space-y-2">
          <span className="text-sm font-medium text-fg">Name</span>
          <input
            value={form.name}
            onChange={(event) =>
              onChange({ ...form, name: event.target.value })
            }
            className={inputClass}
          />
        </label>

        <label className="block space-y-2">
          <span className="text-sm font-medium text-fg">Phone</span>
          <input
            required
            value={form.phone}
            onChange={(event) =>
              onChange({ ...form, phone: event.target.value })
            }
            className={inputClass}
          />
        </label>

        {fields.length > 0 ? (
          <div className="grid gap-4 sm:grid-cols-2">
            {fields.map((field) => (
              <ExtraFieldInput
                key={field.field_key}
                field={field}
                value={form.extra_fields[field.field_key] ?? ""}
                onChange={(value) =>
                  onChange({
                    ...form,
                    extra_fields: {
                      ...form.extra_fields,
                      [field.field_key]: value,
                    },
                  })
                }
              />
            ))}
          </div>
        ) : null}

        <label className="block space-y-2">
          <span className="text-sm font-medium text-fg">Language</span>
          <select
            value={form.language_pref}
            onChange={(event) =>
              onChange({ ...form, language_pref: event.target.value })
            }
            className={inputClass}
          >
            <option value="en">English</option>
            <option value="si">Sinhala</option>
            <option value="ta">Tamil</option>
          </select>
        </label>

        {mode === "create" ? (
          <label className="block space-y-2">
            <span className="text-sm font-medium text-fg">Initial class</span>
            <select
              value={form.class_id}
              onChange={(event) =>
                onChange({ ...form, class_id: event.target.value })
              }
              className={inputClass}
            >
              <option value="">No enrollment yet</option>
              {classes.map((subjectClass) => (
                <option key={subjectClass.id} value={subjectClass.id}>
                  {subjectClass.subject}
                </option>
              ))}
            </select>
          </label>
        ) : null}

        <div className="flex justify-end gap-2 border-t border-border pt-4">
          <button type="button" onClick={onClose} className={btnQuiet}>
            Cancel
          </button>
          <button type="submit" disabled={saving} className={btnPrimary}>
            {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            {mode === "create" ? "Create student" : "Save changes"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
