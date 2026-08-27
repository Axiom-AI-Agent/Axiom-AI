"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  AlertTriangle,
  BookOpen,
  CreditCard,
  Megaphone,
  MessageSquare,
  RefreshCw,
  UserCheck,
  Users,
} from "lucide-react";

import MetricCard from "@/components/MetricCard";
import ChartCard from "@/components/ChartCard";
import { useTenant } from "@/context/TenantContext";
import { DashboardOverview, getDashboardOverview } from "@/lib/api";

export default function OverviewPage() {
  const { tenantId } = useTenant();
  const [data, setData] = useState<DashboardOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadOverview = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      setData(await getDashboardOverview(tenantId));
    } catch (requestError) {
      console.error(requestError);
      setError(
        "Could not load dashboard data. Confirm Dashboard/backend is running on port 8001.",
      );
    } finally {
      setLoading(false);
    }
  }, [tenantId]);

  useEffect(() => {
    void loadOverview();
  }, [loadOverview]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <div className="h-8 w-56 animate-pulse rounded bg-slate-200 dark:bg-slate-700" />
          <div className="mt-2 h-4 w-72 animate-pulse rounded bg-slate-200 dark:bg-slate-800" />
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <div
              key={index}
              className="h-28 animate-pulse rounded-xl bg-slate-200 dark:bg-slate-800"
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Dashboard Overview
          </h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Live operational data for {data.tenant_id}.
          </p>
        </div>

        <button
          type="button"
          onClick={() => void loadOverview()}
          className="flex items-center gap-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700/50 shadow-sm transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        <Link href="/dashboard/students" className="block">
          <MetricCard
            title="Students"
            value={data.students}
            icon={<Users className="h-5 w-5" />}
          />
        </Link>

        <Link href="/dashboard/classes" className="block">
          <MetricCard
            title="Classes"
            value={data.classes}
            icon={<BookOpen className="h-5 w-5" />}
          />
        </Link>

        <Link href="/dashboard/inbox?status=open" className="block">
          <MetricCard
            title="Requires Attention"
            value={data.open_escalations}
            icon={<AlertTriangle className="h-5 w-5" />}
          />
        </Link>

        <Link
          href="/dashboard/inbox?status=open&reason_code=payment_receipt"
          className="block"
        >
          <MetricCard
            title="Payment Receipts"
            value={data.open_payment_receipts}
            icon={<CreditCard className="h-5 w-5" />}
          />
        </Link>

        <Link
          href="/dashboard/inbox?status=open&reason_code=talk_to_tutor"
          className="block"
        >
          <MetricCard
            title="Talk to Tutor"
            value={data.open_talk_to_tutor}
            icon={<UserCheck className="h-5 w-5" />}
          />
        </Link>

        <Link href="/dashboard/students" className="block">
          <MetricCard
            title="Pending Enrollments"
            value={data.pending_enrollments}
            icon={<MessageSquare className="h-5 w-5" />}
          />
        </Link>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <ChartCard
          title="Requires Attention (Breakdown)"
          type="donut"
          labels={["Payment Receipts", "Talk to Tutor", "Other"]}
          data={[
            data.open_payment_receipts,
            data.open_talk_to_tutor,
            Math.max(0, data.open_escalations - data.open_payment_receipts - data.open_talk_to_tutor),
          ]}
        />

        <div className="flex flex-col gap-4 justify-center">
          <MetricCard
            title="Active Students"
            value={data.students - data.pending_enrollments}
            icon={<UserCheck className="h-5 w-5 text-emerald-500" />}
          />
          <MetricCard
            title="Pending Students"
            value={data.pending_enrollments}
            icon={<AlertTriangle className="h-5 w-5 text-amber-500" />}
          />
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-6 shadow-sm">
        <h2 className="font-semibold text-slate-900 dark:text-white text-lg mb-4">Quick actions</h2>
        <div className="flex flex-wrap gap-3 text-sm">
          <Link
            href="/dashboard/inbox?status=open"
            className="rounded-lg border border-slate-200 dark:border-slate-700 px-4 py-2 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors shadow-sm font-medium"
          >
            Open inbox
          </Link>
          <Link
            href="/dashboard/messages"
            className="rounded-lg border border-slate-200 dark:border-slate-700 px-4 py-2 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors shadow-sm font-medium"
          >
            Staff messages
          </Link>
          <Link
            href="/dashboard/classes"
            className="inline-flex items-center gap-2 rounded-lg border border-emerald-600 bg-emerald-600 px-4 py-2 text-white hover:bg-emerald-500 transition-colors shadow-sm font-medium"
          >
            <Megaphone className="h-4 w-4" />
            Broadcast to class
          </Link>
          <Link
            href="/dashboard/ingest"
            className="rounded-lg border border-slate-200 dark:border-slate-700 px-4 py-2 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors shadow-sm font-medium"
          >
            Upload tutor notes
          </Link>
        </div>
      </div>
    </div>
  );
}
