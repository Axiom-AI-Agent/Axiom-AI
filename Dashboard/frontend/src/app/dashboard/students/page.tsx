"use client";

import { FormEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  AlertTriangle,
  FileSpreadsheet,
  Loader2,
  Plus,
  RefreshCw,
  Search,
  X,
} from "lucide-react";

import EnrollModal from "@/components/students/EnrollModal";
import {
  extraFieldsFromStudent,
  extraFieldsPayload,
  missingRequiredExtraFields,
} from "@/components/students/extraFields";
import StudentFormModal, {
  StudentFormState,
} from "@/components/students/StudentFormModal";
import StudentTable from "@/components/students/StudentTable";
import { useToast } from "@/context/ToastContext";
import { useTenant } from "@/context/TenantContext";
import {
  createStudent,
  deleteStudent,
  enrollStudent,
  getClasses,
  getOnboardingFields,
  getStudents,
  importStudentsExcel,
  OnboardingFieldDefinition,
  Student,
  SubjectClass,
  updateStudent,
  updateStudentHumanMode,
} from "@/lib/api";

type ModalMode = "create" | "edit" | "enroll" | null;

const FALLBACK_DISTRICT_FIELD: OnboardingFieldDefinition = {
  field_key: "district",
  label: "District",
  field_type: "text",
  options: null,
  required: false,
  sort_order: 0,
  active: true,
};

function emptyForm(fields: OnboardingFieldDefinition[]): StudentFormState {
  return {
    name: "",
    phone: "",
    language_pref: "en",
    class_id: "",
    extra_fields: extraFieldsFromStudent(null, fields),
  };
}

function matchesStudentSearch(student: Student, query: string) {
  const normalized = query.trim().toLowerCase();
  if (!normalized) {
    return true;
  }

  const enrollmentText = Array.isArray(student.enrollments)
    ? student.enrollments
        .map(
          (enrollment) =>
            `${enrollment.class_subject ?? ""} ${enrollment.class_name ?? ""} ${enrollment.class_id} ${enrollment.status}`,
        )
        .join(" ")
    : "";

  const extraText = Object.values(student.extra_fields ?? {})
    .filter((value) => value !== null && value !== undefined)
    .map((value) => String(value))
    .join(" ");

  const haystack = [
    student.name,
    student.phone,
    student.school,
    student.district,
    extraText,
    student.id,
    student.language_pref,
    enrollmentText,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();

  return haystack.includes(normalized);
}

export default function StudentsPage() {
  const { tenantId } = useTenant();
  const { showToast } = useToast();

  const [students, setStudents] = useState<Student[]>([]);
  const [classes, setClasses] = useState<SubjectClass[]>([]);
  const [fieldDefs, setFieldDefs] = useState<OnboardingFieldDefinition[]>([]);
  const [form, setForm] = useState<StudentFormState>(() => emptyForm([]));
  const [editingStudent, setEditingStudent] = useState<Student | null>(null);
  const [enrollingStudent, setEnrollingStudent] = useState<Student | null>(null);
  const [enrollClassId, setEnrollClassId] = useState("");
  const [modalMode, setModalMode] = useState<ModalMode>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [importing, setImporting] = useState(false);
  const importInputRef = useRef<HTMLInputElement>(null);

  const filteredStudents = useMemo(
    () => students.filter((student) => matchesStudentSearch(student, searchQuery)),
    [students, searchQuery],
  );

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [studentRows, classRows, fieldResponse] = await Promise.all([
        getStudents(tenantId),
        getClasses(tenantId),
        getOnboardingFields(tenantId).catch(() => null),
      ]);

      setStudents(Array.isArray(studentRows) ? studentRows : []);
      setClasses(Array.isArray(classRows) ? classRows : []);

      if (fieldResponse === null) {
        setFieldDefs([FALLBACK_DISTRICT_FIELD]);
      } else {
        const fields = Array.isArray(fieldResponse.fields)
          ? fieldResponse.fields
          : [];
        const active = fields
          .filter((field) => field.active !== false)
          .sort((a, b) => a.sort_order - b.sort_order);
        setFieldDefs(active);
      }
    } catch (requestError) {
      console.error(requestError);
      setStudents([]);
      setError(
        "Could not load students. Restart Dashboard/backend on port 8001 if needed.",
      );
    } finally {
      setLoading(false);
    }
  }, [tenantId]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  function closeModal() {
    setModalMode(null);
    setEditingStudent(null);
    setEnrollingStudent(null);
    setEnrollClassId("");
    setForm(emptyForm(fieldDefs));
  }

  function openCreateModal() {
    setForm(emptyForm(fieldDefs));
    setEditingStudent(null);
    setModalMode("create");
  }

  function openEditModal(student: Student) {
    setEditingStudent(student);
    setForm({
      name: student.name ?? "",
      phone: student.phone,
      language_pref: student.language_pref,
      class_id: "",
      extra_fields: extraFieldsFromStudent(student, fieldDefs),
    });
    setModalMode("edit");
  }

  function openEnrollModal(student: Student) {
    setEnrollingStudent(student);
    setEnrollClassId("");
    setModalMode("enroll");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!form.phone.trim()) {
      showToast("Phone number is required.", "error");
      return;
    }

    const missing = missingRequiredExtraFields(fieldDefs, form.extra_fields);
    if (missing.length > 0) {
      showToast(`${missing[0]} is required.`, "error");
      return;
    }

    const extra = extraFieldsPayload(fieldDefs, form.extra_fields);
    const district =
      typeof extra.district === "string" ? extra.district : undefined;
    const school =
      typeof extra.school === "string" ? extra.school : undefined;

    setSaving(true);

    try {
      if (modalMode === "edit" && editingStudent) {
        await updateStudent(
          editingStudent.id,
          {
            name: form.name.trim() || undefined,
            phone: form.phone.trim(),
            school,
            district,
            extra_fields: extra,
            language_pref: form.language_pref,
          },
          tenantId,
        );
        showToast("Student updated.", "success");
      } else {
        await createStudent(
          {
            name: form.name.trim() || undefined,
            phone: form.phone.trim(),
            school,
            district,
            extra_fields: extra,
            language_pref: form.language_pref,
            class_id: form.class_id || undefined,
          },
          tenantId,
        );
        showToast("Student created.", "success");
      }

      closeModal();
      await loadData();
    } catch (requestError) {
      console.error(requestError);
      showToast("Could not save the student.", "error");
    } finally {
      setSaving(false);
    }
  }

  async function handleEnrollSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!enrollingStudent || !enrollClassId) {
      return;
    }

    setSaving(true);

    try {
      await enrollStudent(
        enrollingStudent.id,
        enrollClassId,
        "pending",
        tenantId,
      );
      showToast("Student enrolled.", "success");
      closeModal();
      await loadData();
    } catch (requestError) {
      console.error(requestError);
      showToast("Could not enroll the student.", "error");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(studentId: string) {
    if (!window.confirm("Delete this student and related records?")) {
      return;
    }

    try {
      await deleteStudent(studentId, tenantId);
      showToast("Student deleted.", "success");
      await loadData();
    } catch (requestError) {
      console.error(requestError);
      showToast("Could not delete the student.", "error");
    }
  }
  async function handleHumanModeToggle(
    student: Student,
  ) {
    try {
      const updated =
        await updateStudentHumanMode(
          student.id,
          !student.human_mode,
          tenantId,
        );

      setStudents((current) =>
        current.map((item) =>
          item.id === student.id
            ? { ...item, ...updated, enrollments: item.enrollments }
            : item,
        ),
      );

      showToast(
        updated.human_mode
          ? "AI disabled for this student."
          : "AI responses enabled for this student.",
        "success",
      );
    } catch (error) {
      console.error(error);

      showToast(
        "Could not update AI mode.",
        "error",
      );
    }
  }

  async function handleExcelImport(
    file: File | undefined,
  ) {
    if (!file) {
      return;
    }

    if (!file.name.toLowerCase().endsWith(".xlsx")) {
      showToast("Only .xlsx files are supported.", "error");
      return;
    }

    setImporting(true);

    try {
      const result = await importStudentsExcel(
        file,
        tenantId,
      );

      showToast(
        `${result.created} created · ${result.skipped} skipped · ${result.errors.length} error${result.errors.length === 1 ? "" : "s"}`,
        result.errors.length > 0 ? "error" : "success",
      );
      await loadData();
    } catch (requestError) {
      console.error(requestError);
      showToast("Could not import Excel file.", "error");
    } finally {
      setImporting(false);
      if (importInputRef.current) {
        importInputRef.current.value = "";
      }
    }
  }
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Students</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            {searchQuery.trim()
              ? `${filteredStudents.length} of ${students.length} students`
              : `${students.length} student${students.length === 1 ? "" : "s"}`}
            {" · "}table view with class enrollments
          </p>
        </div>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => void loadData()}
            disabled={loading}
            className="flex items-center gap-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700/50 shadow-sm transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>

          <input
            ref={importInputRef}
            type="file"
            accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            className="hidden"
            onChange={(event) =>
              void handleExcelImport(
                event.target.files?.[0],
              )
            }
          />

          <button
            type="button"
            onClick={() =>
              importInputRef.current?.click()
            }
            disabled={importing}
            className="flex items-center gap-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700/50 shadow-sm transition-colors disabled:opacity-50"
          >
            {importing ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <FileSpreadsheet className="h-4 w-4" />
            )}
            Import Excel
          </button>

          <button
            type="button"
            onClick={openCreateModal}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500 shadow-sm transition-colors"
          >
            <Plus className="h-4 w-4" />
            Add student
          </button>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-200 dark:border-red-500/30 bg-red-50 dark:bg-red-500/10 p-4 text-red-800 dark:text-red-200">
          <AlertTriangle className="h-5 w-5" />
          {error}
        </div>
      )}

      {!loading && students.length > 0 && (
        <div className="relative max-w-xl">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500" />
          <input
            type="search"
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
            placeholder="Search by name, phone, extra fields, class, or ID…"
            className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 py-2.5 pl-10 pr-10 text-sm text-slate-900 dark:text-white outline-none placeholder:text-slate-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 shadow-sm transition-colors"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => setSearchQuery("")}
              className="absolute right-2 top-1/2 -translate-y-1/2 rounded-md p-1.5 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-600 dark:hover:text-white transition-colors"
              aria-label="Clear search"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      )}

      {loading ? (
        <div className="flex min-h-48 items-center justify-center rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm">
          <Loader2 className="h-7 w-7 animate-spin text-blue-500 dark:text-blue-400" />
        </div>
      ) : filteredStudents.length === 0 ? (
        <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-10 text-center text-slate-500 dark:text-slate-400 shadow-sm">
          {searchQuery.trim()
            ? `No students match "${searchQuery.trim()}".`
            : 'No students registered yet. Click "Add student" to create one.'}
        </div>
      ) : (
          <StudentTable
            students={filteredStudents}
            fields={fieldDefs}
            onEdit={openEditModal}
            onEnroll={openEnrollModal}
            onDelete={(studentId) => void handleDelete(studentId)}
            onToggleHumanMode={(student) =>
              void handleHumanModeToggle(student)
            }
          />
      )}

      {(modalMode === "create" || modalMode === "edit") && (
        <StudentFormModal
          mode={modalMode}
          form={form}
          saving={saving}
          classes={classes}
          fields={fieldDefs}
          onClose={closeModal}
          onChange={setForm}
          onSubmit={handleSubmit}
        />
      )}

      {modalMode === "enroll" && enrollingStudent && (
        <EnrollModal
          student={enrollingStudent}
          classes={classes}
          classId={enrollClassId}
          saving={saving}
          onClose={closeModal}
          onChange={setEnrollClassId}
          onSubmit={handleEnrollSubmit}
        />
      )}
    </div>
  );
}
