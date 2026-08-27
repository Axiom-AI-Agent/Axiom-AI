"use client";

import { useEffect, useState } from "react";
import { Bar, Doughnut, Line } from "react-chartjs-2";
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
);

const CHART_COLORS = [
  "#2563EB",
  "#10B981",
  "#F59E0B",
  "#EF4444",
  "#8B5CF6",
  "#06B6D4",
];

interface ChartCardProps {
  title: string;
  type: "line" | "bar" | "doughnut";
  labels: string[];
  data: number[];
  horizontal?: boolean;
  colors?: string[];
}

export default function ChartCard({
  title,
  type,
  labels,
  data,
  horizontal = false,
  colors = CHART_COLORS,
}: ChartCardProps) {
  const [isDark, setIsDark] = useState(
    () =>
      typeof window !== "undefined" &&
      document.documentElement.classList.contains("dark"),
  );

  useEffect(() => {
    const update = () => {
      setIsDark(document.documentElement.classList.contains("dark"));
    };
    const observer = new MutationObserver(update);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class"],
    });
    window.addEventListener("storage", update);
    return () => {
      observer.disconnect();
      window.removeEventListener("storage", update);
    };
  }, []);

  const tickColor = isDark ? "#cbd5e1" : "#475569";
  const gridColor = isDark ? "rgba(148,163,184,0.18)" : "rgba(15,23,42,0.08)";
  const isDoughnut = type === "doughnut";

  const chartData = {
    labels,
    datasets: [
      {
        label: title,
        data,
        borderColor: isDoughnut ? (isDark ? "#1e293b" : "#ffffff") : colors,
        backgroundColor: isDoughnut
          ? colors
          : type === "bar"
            ? colors.map((color) => `${color}CC`)
            : "rgba(37, 99, 235, 0.15)",
        borderWidth: isDoughnut ? 2 : 1,
        borderRadius: type === "bar" ? 6 : undefined,
        tension: 0.4,
        cutout: isDoughnut ? "62%" : undefined,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: horizontal ? ("y" as const) : ("x" as const),
    plugins: {
      legend: {
        display: isDoughnut,
        position: "bottom" as const,
        labels: {
          color: tickColor,
          boxWidth: 10,
          padding: 16,
          font: { size: 12 },
        },
      },
      title: { display: false },
      tooltip: {
        titleColor: isDark ? "#fff" : "#0f172a",
        bodyColor: isDark ? "#fff" : "#0f172a",
        backgroundColor: isDark ? "rgba(15,23,42,0.92)" : "rgba(255,255,255,0.96)",
      },
    },
    scales: isDoughnut
      ? undefined
      : {
          x: {
            ticks: { color: tickColor },
            grid: { color: gridColor },
            beginAtZero: true,
          },
          y: {
            ticks: { color: tickColor },
            grid: { color: gridColor },
            beginAtZero: true,
          },
        },
  };

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-white">
        {title}
      </h2>
      <div className={isDoughnut ? "h-64" : "h-72"}>
        {type === "line" ? (
          <Line data={chartData} options={options} />
        ) : type === "doughnut" ? (
          <Doughnut data={chartData} options={options} />
        ) : (
          <Bar data={chartData} options={options} />
        )}
      </div>
    </div>
  );
}
