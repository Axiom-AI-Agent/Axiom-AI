"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import {
  AlertTriangle,
  Calendar,
  Loader2,
  Pencil,
  Plus,
  RefreshCw,
  Trash2,
  X,
} from "lucide-react";

import {
  createSchedule,
  deleteSchedule,
  getClasses,
  getSchedules,
  Schedule,
  SubjectClass,
  updateSchedule,
} from "@/lib/api";
import { useTenant } from "@/context/TenantContext";
import { useToast } from "@/context/ToastContext";
import { btnPrimary, btnQuiet } from "@/lib/ui";

const DAYS = [
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
  "sunday",
];

interface ScheduleFormState {
  class_id: string;
  day_of_week: string;
  start_time: string;
  end_time: string;
  room: string;
}

const initialForm: ScheduleFormState = {
  class_id: "",
  day_of_week: "monday",
  start_time: "09:00",
  end_time: "10:30",
  room: "",
};

function normalizeTime(value: string): string {
  if (!value) {
    return "";
  }
  return value.slice(0, 5);
}

export default function SchedulesPage() {
  const { tenantId } = useTenant();
  const { showToast } = useToast();

  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [classes, setClasses] = useState<SubjectClass[]>([]);
  const [form, setForm] = useState<ScheduleFormState>(initialForm);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [scheds, cls] = await Promise.all([
        getSchedules(tenantId),
        getClasses(tenantId),
      ]);
      setSchedules(Array.isArray(scheds) ? scheds : []);
      setClasses(Array.isArray(cls) ? cls : []);
    } catch (requestError) {
      console.error(requestError);
      setError("Could not load schedules.");
    } finally {
      setLoading(false);
    }
  }, [tenantId]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  function closeForm() {
    setShowForm(false);
    setEditingId(null);
    setForm(initialForm);
    setError(null);
  }

  function openCreateForm() {
    setEditingId(null);
    setForm(initialForm);
    setShowForm(true);
  }

  function openEditForm(schedule: Schedule) {
    setEditingId(schedule.id);
    setForm({
      class_id: schedule.class_id,
      day_of_week: schedule.day_of_week,
      start_time: normalizeTime(schedule.start_time),
      end_time: normalizeTime(schedule.end_time),
      room: schedule.room ?? "",
    });
    setShowForm(true);
    setError(null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!form.class_id) {
      setError("Select a class.");
      return;
    }

    setSaving(true);
    setError(null);

    try {
      if (editingId) {
        await updateSchedule(
          editingId,
          {
            day_of_week: form.day_of_week,
            start_time: form.start_time,
            end_time: form.end_time,
            room: form.room || undefined,
          },
          tenantId,
        );
        showToast("Schedule updated.", "success");
      } else {
        await createSchedule(
          {
            class_id: form.class_id,
            day_of_week: form.day_of_week,
            start_time: form.start_time,
            end_time: form.end_time,
            room: form.room || undefined,
          },
          tenantId,
        );
        showToast("Schedule created.", "success");
      }

      closeForm();
      await loadData();
    } catch (requestError) {
      console.error(requestError);
      showToast(
        editingId ? "Could not update schedule." : "Could not create schedule.",
        "error",
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(scheduleId: string) {
    if (!window.confirm("Delete this schedule?")) return;
    try {
      await deleteSchedule(scheduleId, tenantId);
      if (editingId === scheduleId) {
        closeForm();
      }
      setSchedules((current) => current.filter((s) => s.id !== scheduleId));
      showToast("Schedule deleted.", "success");
    } catch (requestError) {
      console.error(requestError);
      showToast("Could not delete schedule.", "error");
    }
  }

  function getClassName(classId: string): string {
    const cls = classes.find((c) => c.id === classId);
    return cls?.name || cls?.subject || classId;
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col space-y-6 overflow-hidden">
      <div className="flex shrink-0 flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-heading">
            Schedules
          </h1>
          <p className="mt-1 text-sm text-muted">
            Manage class timetables and recurring schedules.
          </p>
        </div>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => void loadData()}
            disabled={loading}
            className={btnQuiet}
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>

          <button
            type="button"
            onClick={() => (showForm ? closeForm() : openCreateForm())}
            className={showForm ? btnQuiet : btnPrimary}
          >
            {showForm ? (
              <X className="h-4 w-4" />
            ) : (
              <Plus className="h-4 w-4" />
            )}
            {showForm ? "Cancel" : "Add Schedule"}
          </button>
        </div>
      </div>

      {error && (
        <div className="flex shrink-0 items-center gap-2 rounded-lg border border-border bg-surface p-4 text-fg">
          <AlertTriangle className="h-5 w-5" />
          <span>{error}</span>
        </div>
      )}

      {showForm && (
        <form
          onSubmit={handleSubmit}
          className="shrink-0 grid gap-4 rounded-xl border border-border bg-surface p-5 md:grid-cols-2 xl:grid-cols-3"
        >
          <div className="md:col-span-2 xl:col-span-3">
            <h2 className="text-sm font-semibold text-heading">
              {editingId ? "Edit schedule" : "New schedule"}
            </h2>
          </div>

          <label className="block space-y-2">
            <span className="text-sm font-medium text-fg">Class</span>
            {editingId ? (
              <p className="rounded-lg border border-border bg-bg/60 px-3 py-2 text-sm text-heading">
                {getClassName(form.class_id)}
              </p>
            ) : (
              <select
                required
                value={form.class_id}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    class_id: event.target.value,
                  }))
                }
                className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-heading outline-none transition-colors focus:border-indigo-soft focus:ring-1 focus:ring-indigo-soft"
              >
                <option value="">Select a class</option>
                {classes.map((cls) => (
                  <option key={cls.id} value={cls.id}>
                    {cls.name || cls.subject}
                  </option>
                ))}
              </select>
            )}
          </label>

          <label className="block space-y-2">
            <span className="text-sm font-medium text-fg">Day</span>
            <select
              value={form.day_of_week}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  day_of_week: event.target.value,
                }))
              }
              className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-heading outline-none transition-colors focus:border-indigo-soft focus:ring-1 focus:ring-indigo-soft"
            >
              {DAYS.map((day) => (
                <option key={day} value={day}>
                  {day.charAt(0).toUpperCase() + day.slice(1)}
                </option>
              ))}
            </select>
          </label>

          <label className="block space-y-2">
            <span className="text-sm font-medium text-fg">Start Time</span>
            <input
              type="time"
              required
              value={form.start_time}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  start_time: event.target.value,
                }))
              }
              className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-heading outline-none transition-colors focus:border-indigo-soft focus:ring-1 focus:ring-indigo-soft"
            />
          </label>

          <label className="block space-y-2">
            <span className="text-sm font-medium text-fg">End Time</span>
            <input
              type="time"
              required
              value={form.end_time}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  end_time: event.target.value,
                }))
              }
              className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-heading outline-none transition-colors focus:border-indigo-soft focus:ring-1 focus:ring-indigo-soft"
            />
          </label>

          <label className="block space-y-2">
            <span className="text-sm font-medium text-fg">Room</span>
            <input
              type="text"
              value={form.room}
              onChange={(event) =>
                setForm((current) => ({ ...current, room: event.target.value }))
              }
              placeholder="Room A"
              className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-heading outline-none transition-colors focus:border-indigo-soft focus:ring-1 focus:ring-indigo-soft"
            />
          </label>

          <div className="flex items-end gap-2">
            <button
              type="submit"
              disabled={saving}
              className={btnPrimary}
            >
              {saving && <Loader2 className="h-4 w-4 animate-spin" />}
              {editingId ? "Save changes" : "Create schedule"}
            </button>
          </div>
        </form>
      )}

      {loading ? (
        <div className="flex min-h-48 items-center justify-center">
          <Loader2 className="h-7 w-7 animate-spin text-muted" />
        </div>
      ) : schedules.length === 0 ? (
        <div className="rounded-xl border border-border bg-surface p-10 text-center">
          <Calendar className="mx-auto h-10 w-10 text-muted" />
          <p className="mt-3 text-fg">No schedules yet.</p>
          <p className="mt-1 text-sm text-muted">
            Use Add Schedule to create the first one.
          </p>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto pr-1">
          <div className="grid gap-4 pb-6 md:grid-cols-2 xl:grid-cols-3">
            {schedules.map((schedule) => (
              <article
                key={schedule.id}
                className="rounded-xl border border-border bg-surface p-5"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h2 className="text-lg font-semibold text-heading">
                      {getClassName(schedule.class_id)}
                    </h2>
                    <p className="mt-1 text-xs text-muted">
                      {schedule.day_of_week.charAt(0).toUpperCase() +
                        schedule.day_of_week.slice(1)}
                    </p>
                  </div>
                  <div className="flex gap-1.5">
                    <button
                      type="button"
                      onClick={() => openEditForm(schedule)}
                      className="rounded-md border border-border px-2.5 py-1.5 text-xs font-medium text-muted transition-colors hover:bg-hover"
                      aria-label="Edit schedule"
                    >
                      <Pencil className="h-4 w-4" />
                    </button>
                    <button
                      type="button"
                      onClick={() => void handleDelete(schedule.id)}
                      className="rounded-md border border-border px-2.5 py-1.5 text-xs font-medium text-muted transition-colors hover:bg-hover"
                      aria-label="Delete schedule"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                <dl className="mt-5 space-y-3 text-sm">
                  <div className="flex justify-between gap-4">
                    <dt className="text-muted">Time</dt>
                    <dd className="font-medium text-heading">
                      {normalizeTime(schedule.start_time)} -{" "}
                      {normalizeTime(schedule.end_time)}
                    </dd>
                  </div>

                  {schedule.room && (
                    <div className="flex justify-between gap-4">
                      <dt className="text-muted">Room</dt>
                      <dd className="text-fg">{schedule.room}</dd>
                    </div>
                  )}

                  {schedule.teacher_name && (
                    <div className="flex justify-between gap-4">
                      <dt className="text-muted">Teacher</dt>
                      <dd className="text-fg">{schedule.teacher_name}</dd>
                    </div>
                  )}

                  <div className="flex justify-between gap-4">
                    <dt className="text-muted">Status</dt>
                    <dd className="text-fg">
                      <span
                        className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                          schedule.status === "active"
                            ? "bg-sage/15 text-sage"
                            : "bg-muted/20 text-muted"
                        }`}
                      >
                        {schedule.status}
                      </span>
                    </dd>
                  </div>
                </dl>
              </article>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
