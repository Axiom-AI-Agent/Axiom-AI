import { OnboardingFieldDefinition, Student } from "@/lib/api";

export function studentFieldValue(student: Student, key: string): string {
  const extra = student.extra_fields ?? {};
  const raw = extra[key];

  if (raw !== undefined && raw !== null && String(raw).trim() !== "") {
    if (typeof raw === "boolean") {
      return raw ? "true" : "false";
    }
    return String(raw);
  }

  if (raw === false) {
    return "false";
  }

  if (key === "district") {
    return student.district ?? "";
  }
  if (key === "school") {
    return student.school ?? "";
  }
  return "";
}

export function formatStudentFieldValue(
  student: Student,
  field: OnboardingFieldDefinition,
): string {
  const value = studentFieldValue(student, field.field_key);
  if (field.field_type === "boolean") {
    if (value === "true" || value === "Yes") {
      return "Yes";
    }
    if (value === "false" || value === "No") {
      return "No";
    }
    return "—";
  }
  return value.trim() || "—";
}

export function extraFieldsFromStudent(
  student: Student | null,
  fields: OnboardingFieldDefinition[],
): Record<string, string> {
  const out: Record<string, string> = {};
  for (const field of fields) {
    const value = student ? studentFieldValue(student, field.field_key) : "";
    if (field.field_type === "boolean") {
      out[field.field_key] =
        value === "true" || value === "Yes" || value === "1" ? "true" : "false";
    } else {
      out[field.field_key] = value;
    }
  }
  return out;
}

export function extraFieldsPayload(
  fields: OnboardingFieldDefinition[],
  extra: Record<string, string>,
): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const field of fields) {
    const raw = extra[field.field_key] ?? "";
    if (field.field_type === "boolean") {
      out[field.field_key] = raw === "true" || raw === "Yes";
      continue;
    }
    if (field.field_type === "number") {
      const trimmed = String(raw).trim();
      if (!trimmed) {
        out[field.field_key] = "";
        continue;
      }
      const parsed = Number(trimmed);
      out[field.field_key] = Number.isFinite(parsed) ? parsed : trimmed;
      continue;
    }
    out[field.field_key] = String(raw).trim();
  }
  return out;
}

export function missingRequiredExtraFields(
  fields: OnboardingFieldDefinition[],
  extra: Record<string, string>,
): string[] {
  return fields
    .filter((field) => {
      if (!field.required || field.field_type === "boolean") {
        return false;
      }
      return !String(extra[field.field_key] ?? "").trim();
    })
    .map((field) => field.label);
}
