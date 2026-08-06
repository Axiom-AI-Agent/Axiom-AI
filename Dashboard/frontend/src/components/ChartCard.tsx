// src/components/ChartCard.tsx
"use client";

import { useEffect, useState } from "react";
import { Line, Bar } from "react-chartjs-2";
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
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface ChartCardProps {
  title: string;
  type: "line" | "bar";
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
        borderColor: "hsl(220, 80%, 60%)",
        backgroundColor: "hsla(220, 80%, 60%, 0.3)",
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
    <div className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
      <h2 className="text-lg font-medium text-gray-800 dark:text-gray-200 mb-2">{title}</h2>
      {type === "line" ? <Line data={chartData} options={options} /> : <Bar data={chartData} options={options} />}
    </div>
  );
}
