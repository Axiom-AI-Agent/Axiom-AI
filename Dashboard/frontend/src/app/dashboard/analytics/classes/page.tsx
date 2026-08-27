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
import SageCheck from "@/components/SageCheck";
import {
  AnalyticsPeriod,
  ClassAnalyticsComparison,
  getClassAnalytics,
} from "@/lib/api";
import {
  btnQuiet,
  emptyState,
  errorBanner,
  pageSubtitle,
  pageTitle,
  selectClass,
  surfaceCard,
} from "@/lib/ui";
import { cn } from "@/lib/utils";

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
          <h1 className={pageTitle}>
            Class Analytics
          </h1>

          <p className={pageSubtitle}>
            Compare AI automation and
            human review performance across
            classes.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <select
            value={period}
            onChange={(event) => setPeriod(event.target.value as AnalyticsPeriod)}
            className={selectClass}
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
            className={btnQuiet}
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        </div>
      </div>

      <div className="flex-1 space-y-6 overflow-y-auto pr-1">
        {error && (
        <div className={errorBanner}>
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-blue" />

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
          <RefreshCw className="h-7 w-7 animate-spin text-muted" />
        </div>
      ) : !data ? (
        <div className={emptyState}>
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
              label="Requires Attention"
              value={totals.escalations}
              icon={
                <AlertTriangle className="h-5 w-5" />
              }
              attention={totals.escalations > 0}
              healthy={totals.escalations === 0}
            />
          </div>

          <div className={`${surfaceCard} flex flex-wrap items-center justify-between gap-3 p-4`}>
            <div>
              <p className="text-sm font-medium text-heading">
                Compare classes by
              </p>

              <p className="mt-1 text-xs text-muted">
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
              className={selectClass}
            >
              <option value="deflection_rate">
                Resolved by AI
              </option>

              <option value="total_messages">
                Message volume
              </option>

              <option value="total_conversations">
                Conversations
              </option>

              <option value="total_escalations">
                Requires Attention
              </option>

              <option value="average_response_seconds">
                Response time
              </option>
            </select>
          </div>

          {sortedClasses.length === 0 ? (
            <div className={emptyState}>
              No classes are available for
              comparison.
            </div>
          ) : (
            <div className="grid gap-5 xl:grid-cols-2">
              {sortedClasses.map(
                (item) => (
                  <article
                    key={item.class_id}
                    className={`${surfaceCard} p-5`}
                  >
                    <div className="flex flex-wrap items-start justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <BookOpen className="h-5 w-5 text-muted" />

                          <h2 className="font-display font-semibold text-heading">
                            {formatClassTitle(
                              item.class_name,
                              item.subject,
                            )}
                          </h2>
                        </div>

                        <p className="mt-1 text-sm text-muted">
                          {item.subject}

                          {item.grade
                            ? ` · ${item.grade}`
                            : ""}
                        </p>
                      </div>

                      <div className="text-right">
                        <p className="text-xs uppercase tracking-wide text-muted">
                          Resolved by AI
                        </p>

                        <p className="font-display mt-1 text-2xl font-semibold tabular text-heading">
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
                        label="Requires Attention"
                        value={
                          item.total_escalations
                        }
                      />
                    </div>

                    <div className="mt-5 grid gap-3 sm:grid-cols-2">
                      <div className={`${surfaceCard} p-3`}>
                        <p className="text-xs text-muted">
                          Enrollment
                        </p>

                        <div className="mt-2 flex flex-wrap gap-2">
                          <span className="inline-flex items-center gap-1 rounded-md px-2.5 py-1 text-xs font-medium tabular text-sage">
                            <SageCheck label="Active students" />
                            {
                              item.active_students
                            }{" "}
                            active
                          </span>

                          <span className="rounded-md border border-border px-2.5 py-1 text-xs font-medium tabular text-fg">
                            {
                              item.pending_students
                            }{" "}
                            pending
                          </span>
                        </div>
                      </div>

                      <div className={`${surfaceCard} p-3`}>
                        <p className="text-xs text-muted">
                          Needs Review status
                        </p>

                        <div className="mt-2 flex flex-wrap gap-2">
                          <span
                            className={cn(
                              "rounded-md border border-border px-2.5 py-1 text-xs font-medium tabular text-fg",
                              item.open_escalations > 0 && "text-blue",
                            )}
                          >
                            {
                              item.open_escalations
                            }{" "}
                            open
                          </span>

                          <span className="inline-flex items-center gap-1 rounded-md px-2.5 py-1 text-xs font-medium tabular text-sage">
                            <SageCheck label="Resolved" />
                            {
                              item.resolved_escalations
                            }{" "}
                            resolved
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 border-t border-border pt-4 text-xs text-muted">
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
  attention = false,
  healthy = false,
}: {
  label: string;
  value: number;
  icon: React.ReactNode;
  attention?: boolean;
  healthy?: boolean;
}) {
  return (
      <div className={cn(surfaceCard, "p-5")}>
        <div className="flex items-center justify-between">
          <div>
            <p className="flex items-center gap-1.5 text-sm text-muted">
              {label}
              {healthy && !attention ? <SageCheck /> : null}
            </p>
            <p className="font-display mt-2 text-2xl font-semibold tabular text-heading">
              {value}
            </p>
          </div>
          <div
            className={cn(
              "flex h-10 w-10 items-center justify-center rounded-md",
              attention
                ? "bg-blue/15 text-blue"
                : "bg-indigo-soft/20 text-muted",
            )}
          >
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
    <div className={`${surfaceCard} p-3`}>
      <div className="flex items-center gap-2 text-muted">
        {icon}
        <span className="text-xs">{label}</span>
      </div>
      <p className="mt-2 text-lg font-semibold tabular text-heading">{value}</p>
    </div>
  );
}