"use client";

import { useCallback, useEffect, useState } from "react";
import {
  AlertTriangle,
  BookOpen,
  CreditCard,
  MessageSquare,
  RefreshCw,
  Users,
} from "lucide-react";

import MetricCard from "@/components/MetricCard";
import {
  DashboardSummary,
  getClasses,
  getDashboardSummary,
  getMessageLogs,
} from "@/lib/api";

interface OverviewData {
  totalStudents: number;
  activeClasses: number;
  pendingPayments: number;
  activeConversations: number;
  openEscalations: number;
}

export default function OverviewPage() {
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadOverview = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [summary, classes, messageLogs] = await Promise.all([
        getDashboardSummary(),
        getClasses(),
        getMessageLogs(),
      ]);

      const summaryData: DashboardSummary = summary;

      setData({
        totalStudents: summaryData.total_students,
        activeClasses:
          summaryData.active_classes ?? classes.length,
        pendingPayments: summaryData.pending_payments,
        activeConversations:
          summaryData.active_conversations ??
          new Set(messageLogs.map((log) => log.student_id)).size,
        openEscalations: summaryData.open_escalations,
      });
    } catch (requestError) {
      console.error(requestError);
      setError(
        "Could not load dashboard data. Confirm the FastAPI server is running.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadOverview();
  }, [loadOverview]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <div className="h-8 w-56 animate-pulse rounded bg-gray-700" />
          <div className="mt-2 h-4 w-72 animate-pulse rounded bg-gray-800" />
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-5">
          {Array.from({ length: 5 }).map((_, index) => (
            <div
              key={index}
              className="h-28 animate-pulse rounded-lg bg-gray-800"
            />
          ))}
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-6">
        <div className="flex items-center gap-3 text-red-200">
          <AlertTriangle className="h-5 w-5" />
          <p>{error ?? "Dashboard data is unavailable."}</p>
        </div>

        <button
          type="button"
          onClick={() => void loadOverview()}
          className="mt-4 flex items-center gap-2 rounded-lg bg-white px-4 py-2 text-sm font-medium text-black"
        >
          <RefreshCw className="h-4 w-4" />
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">
            Dashboard Overview
          </h1>
          <p className="mt-1 text-sm text-gray-400">
            Live operational data from Axiom AI.
          </p>
        </div>

        <button
          type="button"
          onClick={() => void loadOverview()}
          className="flex items-center gap-2 rounded-lg border border-gray-700 px-4 py-2 text-sm text-gray-200 hover:bg-gray-800"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-5">
        <MetricCard
          title="Total Students"
          value={data.totalStudents}
          icon={<Users className="h-5 w-5" />}
        />

        <MetricCard
          title="Active Classes"
          value={data.activeClasses}
          icon={<BookOpen className="h-5 w-5" />}
        />

        <MetricCard
          title="Pending Payments"
          value={data.pendingPayments}
          icon={<CreditCard className="h-5 w-5" />}
        />

        <MetricCard
          title="Active Conversations"
          value={data.activeConversations}
          icon={<MessageSquare className="h-5 w-5" />}
        />

        <MetricCard
          title="Open Escalations"
          value={data.openEscalations}
          icon={<AlertTriangle className="h-5 w-5" />}
        />
      </div>

      <div className="rounded-xl border border-gray-800 bg-gray-900 p-5">
        <h2 className="font-medium text-white">System status</h2>
        <p className="mt-2 text-sm text-gray-400">
          The dashboard is connected to the FastAPI backend. Use the
          Classes, Payments, Chats, and Logs modules to review live
          operational records.
        </p>
      </div>
    </div>
  );
}