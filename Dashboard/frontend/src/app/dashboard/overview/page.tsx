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

import ChartCard from "@/components/ChartCard";
import MetricCard from "@/components/MetricCard";
import { useTenant } from "@/context/TenantContext";
import { DashboardOverview, getDashboardOverview } from "@/lib/api";
import {
  btnPrimary,
  btnQuiet,
  errorBanner,
  pageHeader,
  pageSubtitle,
  pageTitle,
  surfaceCard,
} from "@/lib/ui";

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
        "Could not load dashboard data. Please try again.",
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
          <div className="h-8 w-56 animate-pulse rounded-md bg-hover" />
          <div className="mt-2 h-4 w-72 animate-pulse rounded-md bg-hover" />
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <div key={index} className="h-28 animate-pulse rounded-md bg-hover" />
          ))}
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className={errorBanner}>
        <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-blue" />
        <div>
          <p>{error ?? "Dashboard data is unavailable."}</p>
          <button
            type="button"
            onClick={() => void loadOverview()}
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
    <div className="space-y-6">
      <div className={pageHeader}>
        <div className="min-w-0">
          <h1 className={pageTitle}>Dashboard Overview</h1>
          <p className={pageSubtitle}>
            Live operational data for {data.tenant_id}.
          </p>
        </div>

        <button
          type="button"
          onClick={() => void loadOverview()}
          className={btnQuiet}
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
            attention={data.open_escalations > 0}
            healthy={data.open_escalations === 0}
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
            attention={data.open_payment_receipts > 0}
            healthy={data.open_payment_receipts === 0}
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
            attention={data.open_talk_to_tutor > 0}
            healthy={data.open_talk_to_tutor === 0}
          />
        </Link>

        <Link href="/dashboard/students" className="block">
          <MetricCard
            title="Pending Enrollments"
            value={data.pending_enrollments}
            icon={<MessageSquare className="h-5 w-5" />}
            attention={data.pending_enrollments > 0}
            healthy={data.pending_enrollments === 0}
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
            Math.max(
              0,
              data.open_escalations -
                data.open_payment_receipts -
                data.open_talk_to_tutor,
            ),
          ]}
        />

        <div className="flex flex-col justify-center gap-4">
          <MetricCard
            title="Active Students"
            value={data.students - data.pending_enrollments}
            icon={<UserCheck className="h-5 w-5" />}
            healthy
          />
          <MetricCard
            title="Pending Students"
            value={data.pending_enrollments}
            icon={<AlertTriangle className="h-5 w-5" />}
            attention={data.pending_enrollments > 0}
            healthy={data.pending_enrollments === 0}
          />
        </div>
      </div>

      <div className={`${surfaceCard} p-6`}>
        <h2 className="font-display mb-4 text-lg font-semibold text-heading">
          Quick actions
        </h2>
        <div className="flex flex-wrap gap-3 text-sm">
          <Link href="/dashboard/inbox?status=open" className={btnQuiet}>
            Open inbox
          </Link>
          <Link href="/dashboard/messages" className={btnQuiet}>
            Messages
          </Link>
          <Link href="/dashboard/classes" className={btnPrimary}>
            <Megaphone className="h-4 w-4" />
            Broadcast to class
          </Link>
          <Link href="/dashboard/ingest" className={btnQuiet}>
            Upload tutor notes
          </Link>
        </div>
      </div>
    </div>
  );
}
