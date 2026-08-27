"use client";

import {
  AlertTriangle,
  Clock3,
  MessageSquare,
  RefreshCw,
  TimerReset,
  TrendingUp,
} from "lucide-react";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import ChartCard from "@/components/ChartCard";
import MetricCard from "@/components/MetricCard";

import { useTenant } from "@/context/TenantContext";

import {
  DashboardAnalytics,
  AnalyticsPeriod,
  getDashboardAnalytics,
} from "@/lib/api";

function humanizeReason(
  reason: string,
) {
  return reason
    .replaceAll("_", " ")
    .replace(/\b\w/g, (character) =>
      character.toUpperCase(),
    );
}

const PERIOD_OPTIONS: Array<
  [AnalyticsPeriod, string]
> = [
  ["today", "Today"],
  ["48h", "Last 48 Hours"],
  ["7d", "Last 7 Days"],
  ["30d", "Last 30 Days"],
  ["90d", "Last 90 Days"],
];

export default function AnalyticsPage() {
  const { tenantId } = useTenant();

  const [
    data,
    setData,
  ] = useState<DashboardAnalytics | null>(
    null,
  );

  const [
    period,
    setPeriod,
  ] = useState<AnalyticsPeriod>("7d");

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState<string | null>(null);

  const loadAnalytics =
    useCallback(async () => {
      setLoading(true);
      setError(null);

      try {
        const response =
          await getDashboardAnalytics(
            tenantId,
            period,
          );

        setData(response);
      } catch (requestError) {
        console.error(requestError);

        setError(
          "Could not load analytics data.",
        );
      } finally {
        setLoading(false);
      }
    }, [tenantId, period]);

  useEffect(() => {
    void loadAnalytics();
  }, [loadAnalytics]);

  const categoryLabels = useMemo(
    () =>
      data?.escalation_categories.map(
        (item) =>
          humanizeReason(
            item.reason_code,
          ),
      ) ?? [],
    [data],
  );

  const categoryValues = useMemo(
    () =>
      data?.escalation_categories.map(
        (item) => item.count,
      ) ?? [],
    [data],
  );

  if (loading) {
    return (
      <div className="flex min-h-80 items-center justify-center text-slate-500">
        Loading analytics...
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-6">
        <div className="flex items-center gap-3 text-red-700 dark:text-red-300">
          <AlertTriangle className="h-5 w-5" />
          <span>
            {error ??
              "Analytics unavailable."}
          </span>
        </div>

        <button
          type="button"
          onClick={() =>
            void loadAnalytics()
          }
          className="mt-4 flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500"
        >
          <RefreshCw className="h-4 w-4" />
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 lg:h-[calc(100vh-7.5rem)]">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Tutor Automation Analytics
          </h1>

          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Live automation and escalation
            metrics for {data.tenant_id}.
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
              void loadAnalytics()
            }
            className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          title="AI Deflection Rate"
          value={`${data.deflection_rate}%`}
          icon={
            <TrendingUp className="h-5 w-5" />
          }
        />

        <MetricCard
          title="Avg. Response Time"
          value={`${data.average_response_seconds}s`}
          icon={
            <Clock3 className="h-5 w-5" />
          }
        />

        <MetricCard
          title="Estimated Time Saved"
          value={`${data.estimated_minutes_saved} min`}
          icon={
            <TimerReset className="h-5 w-5" />
          }
        />

        <MetricCard
          title="Total Messages"
          value={data.total_messages}
          icon={
            <MessageSquare className="h-5 w-5" />
          }
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <ChartCard
          title="Open vs Resolved Escalations"
          type="doughnut"
          labels={[
            "Open",
            "Resolved",
          ]}
          data={[
            data.open_escalations,
            data.resolved_escalations,
          ]}
          colors={["#EF4444", "#10B981"]}
        />

        <ChartCard
          title="Escalations by Category"
          type="bar"
          horizontal
          labels={categoryLabels}
          data={categoryValues}
        />
      </div>

      <div className="flex min-h-0 flex-1 flex-col rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
              Student Automation Activity
            </h2>

            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Time saved uses an estimate of
              2 minutes per deflected
              conversation.
            </p>
          </div>

          <div className="text-sm text-slate-500">
            {data.total_conversations} total
            conversations
          </div>
        </div>

        <div className="mt-5 min-h-0 flex-1 overflow-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-slate-500 dark:border-slate-700 dark:text-slate-400">
                <th className="px-3 py-3">
                  Student
                </th>

                <th className="px-3 py-3">
                  Messages
                </th>

                <th className="px-3 py-3">
                  Conversations
                </th>

                <th className="px-3 py-3">
                  Escalations
                </th>
              </tr>
            </thead>

            <tbody>
              {data.students.map(
                (student) => (
                  <tr
                    key={
                      student.student_id
                    }
                    className="border-b border-slate-100 last:border-0 dark:border-slate-700"
                  >
                    <td className="px-3 py-3">
                      <div className="font-medium text-slate-900 dark:text-white">
                        {student.student_name ??
                          "Unknown student"}
                      </div>

                      <div className="text-xs text-slate-500">
                        {student.student_id}
                      </div>
                    </td>

                    <td className="px-3 py-3">
                      {student.messages}
                    </td>

                    <td className="px-3 py-3">
                      {
                        student.conversations
                      }
                    </td>

                    <td className="px-3 py-3">
                      {
                        student.escalations
                      }
                    </td>
                  </tr>
                ),
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}