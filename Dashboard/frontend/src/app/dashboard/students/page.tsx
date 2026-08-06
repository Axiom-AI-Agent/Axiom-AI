"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  Loader2,
  Plus,
  RefreshCw,
  Search,
  X,
} from "lucide-react";

import EnrollModal from "@/components/students/EnrollModal";
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
  getStudents,
  Student,
  SubjectClass,
  updateStudent,
} from "@/lib/api";

type ModalMode = "create" | "edit" | "enroll" | null;

const emptyForm: StudentFormState = {
  name: "",
  phone: "",
  district: "",
  language_pref: "en",
  class_id: "",
};

function matchesStudentSearch(student: Student, query: string) {
  const normalized = query.trim().toLowerCase();
  if (!normalized) {
    return true;
  }

  const enrollmentText =
    student.enrollments
      ?.map(
        (enrollment) =>
          `${enrollment.class_subject ?? ""} ${enrollment.class_name ?? ""} ${enrollment.class_id} ${enrollment.status}`,
      )
      .join(" ") ?? "";

  const haystack = [
    student.name,
    student.phone,
    student.district,
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
  const [form, setForm] = useState<StudentFormState>(emptyForm);
  const [editingStudent, setEditingStudent] = useState<Student | null>(null);
  const [enrollingStudent, setEnrollingStudent] = useState<Student | null>(null);
  const [enrollClassId, setEnrollClassId] = useState("");
  const [modalMode, setModalMode] = useState<ModalMode>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  const filteredStudents = useMemo(
    () => students.filter((student) => matchesStudentSearch(student, searchQuery)),
    [students, searchQuery],
  );

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [studentRows, classRows] = await Promise.all([
        getStudents(tenantId),
        getClasses(tenantId),
      ]);

      setStudents(Array.isArray(studentRows) ? studentRows : []);
      setClasses(Array.isArray(classRows) ? classRows : []);
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
    setForm(emptyForm);
  }

  function openCreateModal() {
    setForm(emptyForm);
    setEditingStudent(null);
    setModalMode("create");
  }

  function openEditModal(student: Student) {
    setEditingStudent(student);
    setForm({
      name: student.name ?? "",
      phone: student.phone,
      district: student.district ?? "",
      language_pref: student.language_pref,
      class_id: "",
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

    setSaving(true);

    try {
      if (modalMode === "edit" && editingStudent) {
        await updateStudent(
          editingStudent.id,
          {
            name: form.name.trim() || undefined,
            phone: form.phone.trim(),
            district: form.district.trim() || undefined,
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
            district: form.district.trim() || undefined,
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

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">Students</h1>
          <p className="mt-1 text-sm text-gray-400">
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
            className="flex items-center gap-2 rounded-lg border border-gray-700 px-4 py-2 text-sm text-gray-200 hover:bg-gray-800 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>

          <button
            type="button"
            onClick={openCreateModal}
            className="flex items-center gap-2 rounded-lg bg-white px-4 py-2 text-sm font-medium text-black hover:bg-gray-200"
          >
            <Plus className="h-4 w-4" />
            Add student
          </button>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-200">
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
            placeholder="Search by name, phone, district, class, or ID…"
            className="w-full rounded-lg border border-gray-700 bg-gray-900 py-2.5 pl-10 pr-10 text-sm text-white outline-none placeholder:text-gray-500 focus:border-indigo-500"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => setSearchQuery("")}
              className="absolute right-2 top-1/2 -translate-y-1/2 rounded-md p-1.5 text-gray-400 hover:bg-gray-800 hover:text-white"
              aria-label="Clear search"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      )}

      {loading ? (
        <div className="flex min-h-48 items-center justify-center rounded-xl border border-gray-800 bg-gray-900">
          <Loader2 className="h-7 w-7 animate-spin text-gray-400" />
        </div>
      ) : filteredStudents.length === 0 ? (
        <div className="rounded-xl border border-gray-800 bg-gray-900 p-10 text-center text-gray-400">
          {searchQuery.trim()
            ? `No students match "${searchQuery.trim()}".`
            : 'No students registered yet. Click "Add student" to create one.'}
        </div>
      ) : (
        <StudentTable
          students={filteredStudents}
          onEdit={openEditModal}
          onEnroll={openEnrollModal}
          onDelete={(studentId) => void handleDelete(studentId)}
        />
      )}

      {(modalMode === "create" || modalMode === "edit") && (
        <StudentFormModal
          mode={modalMode}
          form={form}
          saving={saving}
          classes={classes}
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
