"use client";

import { useEffect, useMemo, useState } from "react";
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

import { surfaceCard } from "@/lib/ui";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
);

interface ChartCardProps {
  title: string;
  type: "line" | "bar" | "donut";
  labels: string[];
  data: number[];
}

function readToken(name: string, fallback: string) {
  if (typeof window === "undefined") {
    return fallback;
  }
  const value = getComputedStyle(document.documentElement)
    .getPropertyValue(name)
    .trim();
  return value || fallback;
}

export default function ChartCard({
  title,
  type,
  labels,
  data,
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
    return () => observer.disconnect();
  }, []);

  const palette = useMemo(() => {
    const blue = readToken("--blue", "#3B7AED");
    const indigo = readToken("--indigo", "#1B2A4A");
    const indigoSoft = readToken("--indigo-soft", "#2C3E63");
    const ink = readToken("--ink", "#0B1220");
    const paper = readToken("--paper", "#F7F8FB");
    const muted = readToken("--muted", indigoSoft);
    const border = readToken("--border", indigoSoft);
    const tick = isDark ? paper : ink;
    return { blue, indigo, indigoSoft, tick, muted, border, ink, paper };
  }, [isDark]);

  const chartData = {
    labels,
    datasets: [
      {
        label: title,
        data,
        borderColor: type === "donut" ? "transparent" : palette.blue,
        backgroundColor:
          type === "donut"
            ? labels.map(
                (_, index) =>
                  [palette.blue, palette.indigoSoft, palette.indigo][index % 3],
              )
            : `${palette.blue}1A`,
        tension: 0.35,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: { display: false },
      title: { display: false },
      tooltip: {
        titleColor: palette.tick,
        bodyColor: palette.tick,
        backgroundColor: isDark ? `${palette.ink}CC` : `${palette.paper}F2`,
      },
    },
    scales:
      type === "donut"
        ? undefined
        : {
            x: {
              ticks: { color: palette.muted, font: { family: "inherit" } },
              grid: { color: `${palette.border}66` },
            },
            y: {
              ticks: { color: palette.muted, font: { family: "inherit" } },
              grid: { color: `${palette.border}66` },
            },
          },
  };

  return (
    <div className={`${surfaceCard} p-5`}>
      <h2 className="font-display mb-4 text-lg font-semibold text-heading">
        {title}
      </h2>
      {type === "line" ? (
        <div className="h-56">
          <Line data={chartData} options={options} />
        </div>
      ) : type === "bar" ? (
        <div className="h-56">
          <Bar data={chartData} options={options} />
        </div>
      ) : (
        <div className="mx-auto h-56 max-w-xs">
          <Doughnut data={chartData} options={options} />
        </div>
      )}
    </div>
  );
}
