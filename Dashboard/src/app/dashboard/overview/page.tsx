// src/app/dashboard/overview/page.tsx
"use client";

import { useEffect, useState } from "react";
import MetricCard from "@/components/MetricCard";
import ChartCard from "@/components/ChartCard";
import { overviewMetrics } from "@/mock/overview";
import { studentGrowth, paymentTrends } from "@/mock/overviewCharts";
import { Users, BookOpen, CreditCard, MessageSquare } from "lucide-react";

export default function OverviewPage() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 800); // mock async fetch
    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    // Skeleton placeholders matching the card layout
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            className="flex items-center p-4 bg-gradient-to-r from-gray-800 to-gray-700 rounded-lg animate-pulse"
          >
            <div className="mr-4 h-6 w-6 rounded bg-gray-600" />
            <div className="flex-1 space-y-2">
              <div className="h-4 w-3/4 bg-gray-600 rounded" />
              <div className="h-6 w-1/2 bg-gray-600 rounded" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Metric cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Students"
          value={overviewMetrics.totalStudents}
          icon={<Users className="h-5 w-5 text-gray-200" />}
        />
        <MetricCard
          title="Active Classes"
          value={overviewMetrics.activeClasses}
          icon={<BookOpen className="h-5 w-5 text-gray-200" />}
        />
        <MetricCard
          title="Pending Payments"
          value={overviewMetrics.pendingPayments}
          icon={<CreditCard className="h-5 w-5 text-gray-200" />}
        />
        <MetricCard
          title="Active Chats"
          value={overviewMetrics.activeChats}
          icon={<MessageSquare className="h-5 w-5 text-gray-200" />}
        />
      </div>
      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChartCard
          title="Student Growth"
          type="line"
          labels={studentGrowth.labels}
          data={studentGrowth.data}
        />
        <ChartCard
          title="Payment Trends"
          type="bar"
          labels={paymentTrends.labels}
          data={paymentTrends.data}
        />
      </div>
    </div>
  );
}
