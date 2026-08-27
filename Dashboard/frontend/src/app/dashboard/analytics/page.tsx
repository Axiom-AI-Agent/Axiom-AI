"use client";

import {
  AlertTriangle,
  Clock3,
  MessageSquare,
  RefreshCw,
  TimerReset,
  TrendingUp,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

import ChartCard from "@/components/ChartCard";
import MetricCard from "@/components/MetricCard";
import SageCheck from "@/components/SageCheck";
import { useTenant } from "@/context/TenantContext";
import {
  AnalyticsPeriod,
  DashboardAnalytics,
  getDashboardAnalytics,
} from "@/lib/api";
import {
  btnQuiet,
  errorBanner,
  pageHeader,
  pageSubtitle,
  pageTitle,
  pageToolbar,
  surfaceCard,
  toolbarSelect,
} from "@/lib/ui";

function humanizeReason(reason: string) {
  return reason
    .replaceAll("_", " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

const PERIOD_OPTIONS: Array<[AnalyticsPeriod, string]> = [
  ["today", "Today"],
  ["48h", "Last 48 Hours"],
  ["7d", "Last 7 Days"],
  ["30d", "Last 30 Days"],
  ["90d", "Last 90 Days"],
];

export default function AnalyticsPage() {
  const { tenantId } = useTenant();
  const [data, setData] = useState<DashboardAnalytics | null>(null);
  const [period, setPeriod] = useState<AnalyticsPeriod>("7d");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadAnalytics = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      setData(await getDashboardAnalytics(tenantId, period));
    } catch (requestError) {
      console.error(requestError);
      setError("Could not load analytics data.");
    } finally {
      setLoading(false);
    }
  }, [tenantId, period]);

  useEffect(() => {
    void loadAnalytics();
  }, [loadAnalytics]);

  const categoryLabels = useMemo(
    () => data?.escalation_categories.map((item) => humanizeReason(item.reason_code)) ?? [],
    [data],
  );

  const categoryValues = useMemo(
    () => data?.escalation_categories.map((item) => item.count) ?? [],
    [data],
  );

  if (loading) {
    return (
      <div className="flex min-h-80 items-center justify-center text-muted">
        Loading analytics...
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className={errorBanner}>
        <AlertTriangle className="h-5 w-5 shrink-0 text-blue" />
        <div>
          <p>{error ?? "Analytics unavailable."}</p>
          <button
            type="button"
            onClick={() => void loadAnalytics()}
            className={`${btnQuiet} mt-4`}
          >
            <RefreshCw className="h-4 w-4" />
            Try again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col overflow-hidden">
      <div className={pageHeader}>
        <div className="min-w-0">
          <h1 className={pageTitle}>Tutor Automation Analytics</h1>
          <p className={pageSubtitle}>
            Live automation and human review metrics for {data.tenant_id}.
          </p>
        </div>

        <div className={pageToolbar}>
          <select
            value={period}
            onChange={(event) =>
              setPeriod(event.target.value as AnalyticsPeriod)
            }
            className={toolbarSelect}
            aria-label="Analytics period"
          >
            {PERIOD_OPTIONS.map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>

          <button
            type="button"
            onClick={() => void loadAnalytics()}
            className={btnQuiet}
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        </div>
      </div>

      <div className="flex min-h-0 flex-1 flex-col gap-6 overflow-hidden pr-1">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          <MetricCard
            title="Resolved by AI"
            value={`${data.deflection_rate}%`}
            icon={<TrendingUp className="h-5 w-5" />}
            healthy
          />
          <MetricCard
            title="Avg. Response Time"
            value={`${data.average_response_seconds}s`}
            icon={<Clock3 className="h-5 w-5" />}
          />
          <MetricCard
            title="Estimated Time Saved"
            value={`${data.estimated_minutes_saved} min`}
            icon={<TimerReset className="h-5 w-5" />}
            healthy
          />
          <MetricCard
            title="Total Messages"
            value={data.total_messages}
            icon={<MessageSquare className="h-5 w-5" />}
          />
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <ChartCard
            title="Open vs Resolved (Requires Attention)"
            type="donut"
            labels={["Open", "Resolved"]}
            data={[data.open_escalations, data.resolved_escalations]}
          />
          <ChartCard
            title="Requires Attention by Category"
            type="donut"
            labels={categoryLabels}
            data={categoryValues}
          />
        </div>

        <div className={`${surfaceCard} flex min-h-0 flex-1 flex-col p-6`}>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="font-display text-lg font-semibold text-heading">
                Student Automation Activity
              </h2>
              <p className="mt-1 text-xs text-muted">
                Time saved uses an estimate of 2 minutes per deflected
                conversation.
              </p>
            </div>
            <div className="text-sm tabular text-muted">
              {data.total_conversations} total conversations
            </div>
          </div>

          <div className="mt-5 flex-1 overflow-auto rounded-md border border-border">
            <table className="min-w-full text-sm">
              <thead className="sticky top-0 z-10 bg-surface">
                <tr className="border-b border-border text-left text-muted">
                  <th className="px-3 py-3 font-medium">Student</th>
                  <th className="px-3 py-3 font-medium">Messages</th>
                  <th className="px-3 py-3 font-medium">Conversations</th>
                  <th className="px-3 py-3 font-medium">Requires Attention</th>
                </tr>
              </thead>
              <tbody>
                <AnimatePresence initial={false}>
                  {data.students.map((student) => {
                    const needsAttention = student.escalations > 0;
                    return (
                      <motion.tr
                        key={student.student_id}
                        layout
                        className="border-b border-border last:border-0"
                      >
                        <td className="px-3 py-3">
                          <div className="font-medium text-heading">
                            {student.student_name ?? "Unknown student"}
                          </div>
                          <div className="text-xs text-muted">
                            {student.student_id}
                          </div>
                        </td>
                        <td className="px-3 py-3 tabular text-fg">
                          {student.messages}
                        </td>
                        <td className="px-3 py-3 tabular text-fg">
                          {student.conversations}
                        </td>
                        <td className="px-3 py-3">
                          {needsAttention ? (
                            <span className="tabular text-blue">
                              {student.escalations}
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 tabular text-muted">
                              0
                              <SageCheck label="No open attention" />
                            </span>
                          )}
                        </td>
                      </motion.tr>
                    );
                  })}
                </AnimatePresence>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
