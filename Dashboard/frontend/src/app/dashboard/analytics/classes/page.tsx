"use client";

import {
  AlertTriangle,
  BookOpen,
  Clock3,
  MessageSquare,
  RefreshCw,
  TimerReset,
  TrendingUp,
  Users,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import { useTenant } from "@/context/TenantContext";
import {
  AnalyticsPeriod,
  ClassAnalyticsComparison,
  getClassAnalytics,
} from "@/lib/api";

type SortKey =
  | "deflection_rate"
  | "total_messages"
  | "total_conversations"
  | "total_escalations"
  | "average_response_seconds";

const PERIOD_OPTIONS: Array<
  [AnalyticsPeriod, string]
> = [
  ["today", "Today"],
  ["48h", "Last 48 Hours"],
  ["7d", "Last 7 Days"],
  ["30d", "Last 30 Days"],
  ["90d", "Last 90 Days"],
];

function formatClassTitle(
  className: string | null | undefined,
  subject: string,
) {
  return className?.trim() || subject;
}

export default function ClassAnalyticsPage() {
  const { tenantId } = useTenant();

  const [data, setData] =
    useState<ClassAnalyticsComparison | null>(null);

  const [period, setPeriod] =
    useState<AnalyticsPeriod>("7d");

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [sortKey, setSortKey] =
    useState<SortKey>("deflection_rate");

  const loadAnalytics = useCallback(
    async (showSpinner = true) => {
      if (showSpinner) {
        setLoading(true);
      }

      setError(null);

      try {
        const response =
          await getClassAnalytics(
            tenantId,
            period,
          );

        setData(response);
      } catch (requestError) {
        console.error(requestError);

        setError(
          "Could not load per-class analytics. Confirm the dashboard backend is running and the analytics endpoint is available.",
        );
      } finally {
        if (showSpinner) {
          setLoading(false);
        }
      }
    },
    [tenantId, period],
  );

  useEffect(() => {
    void loadAnalytics(true);
  }, [loadAnalytics]);

  const sortedClasses = useMemo(() => {
    if (!data) {
      return [];
    }

    return [...data.classes].sort(
      (a, b) => {
        const first = Number(
          a[sortKey] ?? 0,
        );

        const second = Number(
          b[sortKey] ?? 0,
        );

        return second - first;
      },
    );
  }, [data, sortKey]);

  const totals = useMemo(() => {
    if (!data) {
      return {
        classes: 0,
        students: 0,
        messages: 0,
        escalations: 0,
      };
    }

    return data.classes.reduce(
      (current, item) => ({
        classes:
          current.classes + 1,

        students:
          current.students +
          item.enrolled_students,

        messages:
          current.messages +
          item.total_messages,

        escalations:
          current.escalations +
          item.total_escalations,
      }),
      {
        classes: 0,
        students: 0,
        messages: 0,
        escalations: 0,
      },
    );
  }, [data]);

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col overflow-hidden">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900 dark:text-white">
            Class Analytics
          </h1>

          <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
            Compare AI automation and
            escalation performance across
            classes.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <select
            value={period}
            onChange={(event) => setPeriod(event.target.value as AnalyticsPeriod)}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white"
          >
            {PERIOD_OPTIONS.map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>

          <button
            type="button"
            onClick={() =>
              void loadAnalytics(false)
            }
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100 disabled:opacity-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        </div>
      </div>

      <div className="flex-1 space-y-6 overflow-y-auto pr-1">
        {error && (
        <div className="flex items-start gap-3 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-700 dark:text-red-300">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />

          <div>
            <p className="font-medium">
              Could not load analytics
            </p>

            <p className="mt-1 text-sm">
              {error}
            </p>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex min-h-64 items-center justify-center">
          <RefreshCw className="h-7 w-7 animate-spin text-slate-500" />
        </div>
      ) : !data ? (
        <div className="rounded-xl border border-slate-200 bg-white p-10 text-center text-slate-500 dark:border-slate-800 dark:bg-slate-900">
          Class analytics are unavailable.
        </div>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <SummaryCard
              label="Classes"
              value={totals.classes}
              icon={
                <BookOpen className="h-5 w-5" />
              }
            />

            <SummaryCard
              label="Enrolled Students"
              value={totals.students}
              icon={
                <Users className="h-5 w-5" />
              }
            />

            <SummaryCard
              label="Messages"
              value={totals.messages}
              icon={
                <MessageSquare className="h-5 w-5" />
              }
            />

            <SummaryCard
              label="Escalations"
              value={totals.escalations}
              icon={
                <AlertTriangle className="h-5 w-5" />
              }
            />
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
            <div>
              <p className="text-sm font-medium text-slate-900 dark:text-white">
                Compare classes by
              </p>

              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                Classes are sorted from
                highest to lowest.
              </p>
            </div>

            <select
              value={sortKey}
              onChange={(event) =>
                setSortKey(
                  event.target
                    .value as SortKey,
                )
              }
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white"
            >
              <option value="deflection_rate">
                Deflection rate
              </option>

              <option value="total_messages">
                Message volume
              </option>

              <option value="total_conversations">
                Conversations
              </option>

              <option value="total_escalations">
                Escalations
              </option>

              <option value="average_response_seconds">
                Response time
              </option>
            </select>
          </div>

          {sortedClasses.length === 0 ? (
            <div className="rounded-xl border border-slate-200 bg-white p-10 text-center text-slate-500 dark:border-slate-800 dark:bg-slate-900">
              No classes are available for
              comparison.
            </div>
          ) : (
            <div className="grid gap-5 xl:grid-cols-2">
              {sortedClasses.map(
                (item) => (
                  <article
                    key={item.class_id}
                    className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <BookOpen className="h-5 w-5 text-blue-500" />

                          <h2 className="font-semibold text-slate-900 dark:text-white">
                            {formatClassTitle(
                              item.class_name,
                              item.subject,
                            )}
                          </h2>
                        </div>

                        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                          {item.subject}

                          {item.grade
                            ? ` · ${item.grade}`
                            : ""}
                        </p>
                      </div>

                      <div className="text-right">
                        <p className="text-xs uppercase tracking-wide text-slate-500">
                          Deflection
                        </p>

                        <p className="mt-1 text-2xl font-semibold text-blue-600 dark:text-blue-400">
                          {
                            item.deflection_rate
                          }
                          %
                        </p>
                      </div>
                    </div>

                    <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3">
                      <MetricCard
                        icon={
                          <Users className="h-4 w-4" />
                        }
                        label="Students"
                        value={
                          item.enrolled_students
                        }
                      />

                      <MetricCard
                        icon={
                          <MessageSquare className="h-4 w-4" />
                        }
                        label="Messages"
                        value={
                          item.total_messages
                        }
                      />

                      <MetricCard
                        icon={
                          <TrendingUp className="h-4 w-4" />
                        }
                        label="Conversations"
                        value={
                          item.total_conversations
                        }
                      />

                      <MetricCard
                        icon={
                          <Clock3 className="h-4 w-4" />
                        }
                        label="Avg response"
                        value={`${item.average_response_seconds}s`}
                      />

                      <MetricCard
                        icon={
                          <TimerReset className="h-4 w-4" />
                        }
                        label="Time saved"
                        value={`${item.estimated_minutes_saved} min`}
                      />

                      <MetricCard
                        icon={
                          <AlertTriangle className="h-4 w-4" />
                        }
                        label="Escalations"
                        value={
                          item.total_escalations
                        }
                      />
                    </div>

                    <div className="mt-5 grid gap-3 sm:grid-cols-2">
                      <div className="rounded-lg border border-slate-200 bg-slate-50 p-3 dark:border-slate-800 dark:bg-slate-950">
                        <p className="text-xs text-slate-500">
                          Enrollment
                        </p>

                        <div className="mt-2 flex flex-wrap gap-2">
                          <span className="rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-medium text-emerald-700 dark:text-emerald-300">
                            {
                              item.active_students
                            }{" "}
                            active
                          </span>

                          <span className="rounded-full bg-amber-500/10 px-2.5 py-1 text-xs font-medium text-amber-700 dark:text-amber-300">
                            {
                              item.pending_students
                            }{" "}
                            pending
                          </span>
                        </div>
                      </div>

                      <div className="rounded-lg border border-slate-200 bg-slate-50 p-3 dark:border-slate-800 dark:bg-slate-950">
                        <p className="text-xs text-slate-500">
                          Escalation status
                        </p>

                        <div className="mt-2 flex flex-wrap gap-2">
                          <span className="rounded-full bg-red-500/10 px-2.5 py-1 text-xs font-medium text-red-700 dark:text-red-300">
                            {
                              item.open_escalations
                            }{" "}
                            open
                          </span>

                          <span className="rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-medium text-emerald-700 dark:text-emerald-300">
                            {
                              item.resolved_escalations
                            }{" "}
                            resolved
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 border-t border-slate-200 pt-4 text-xs text-slate-500 dark:border-slate-800 dark:text-slate-400">
                      <span>
                        {
                          item.deflected_conversations
                        }{" "}
                        of{" "}
                        {
                          item.total_conversations
                        }{" "}
                        conversations estimated
                        as deflected.
                      </span>
                    </div>
                  </article>
                ),
              )}
            </div>
          )}
        </>
      )}
      </div>
    </div>
  );
}

function SummaryCard({
  label,
  value,
  icon,
}: {
  label: string;
  value: number;
  icon: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            {label}
          </p>

          <p className="mt-2 text-2xl font-semibold text-slate-900 dark:text-white">
            {value}
          </p>
        </div>

        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-500/10 text-blue-600 dark:text-blue-400">
          {icon}
        </div>
      </div>
    </div>
  );
}

function MetricCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-3 dark:border-slate-800 dark:bg-slate-950">
      <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
        {icon}

        <span className="text-xs">
          {label}
        </span>
      </div>

      <p className="mt-2 text-lg font-semibold text-slate-900 dark:text-white">
        {value}
      </p>
    </div>
  );
}