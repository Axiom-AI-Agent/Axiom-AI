// src/components/ChartCard.tsx
"use client";

import { useEffect, useState } from "react";
import { Line, Bar, Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

interface ChartCardProps {
  title: string;
  type: "line" | "bar" | "donut";
  labels: string[];
  data: number[];
}

export default function ChartCard({ title, type, labels, data }: ChartCardProps) {
  const [isDark, setIsDark] = useState(() => typeof window !== "undefined" && document.documentElement.classList.contains("dark"));

  useEffect(() => {
    const update = () => {
      setIsDark(document.documentElement.classList.contains("dark"));
    };
    const observer = new MutationObserver(update);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
    window.addEventListener("storage", update);
    return () => {
      observer.disconnect();
      window.removeEventListener("storage", update);
    };
  }, []);

  const chartData = {
    labels,
    datasets: [
      {
        label: title,
        data,
        borderColor: type === "donut" ? "transparent" : "#2563EB",
        backgroundColor: type === "donut" 
          ? ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"] 
          : "rgba(37, 99, 235, 0.1)",
        tension: 0.4,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: { display: false },
      tooltip: {
        titleColor: isDark ? "#fff" : "#000",
        bodyColor: isDark ? "#fff" : "#000",
        backgroundColor: isDark ? "rgba(0,0,0,0.8)" : "rgba(255,255,255,0.9)",
      },
    },
    scales: {
      x: {
        ticks: { color: isDark ? "#fff" : "#333" },
        grid: { color: isDark ? "rgba(255,255,255,0.2)" : "rgba(0,0,0,0.1)" },
      },
      y: {
        ticks: { color: isDark ? "#fff" : "#333" },
        grid: { color: isDark ? "rgba(255,255,255,0.2)" : "rgba(0,0,0,0.1)" },
      },
    },
  };

  return (
    <div className="p-5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">{title}</h2>
      {type === "line" ? <Line data={chartData} options={options} /> : type === "bar" ? <Bar data={chartData} options={options} /> : <div className="max-w-xs mx-auto"><Doughnut data={chartData} options={options} /></div>}
    </div>
  );
}
