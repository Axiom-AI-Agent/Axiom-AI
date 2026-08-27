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
    const ember = readToken("--ember", "#E8985E");
    const sage = readToken("--sage", "#6FA287");
    const indigoSoft = readToken("--indigo-soft", "#2C3E63");
    const ink = readToken("--ink", "#0B1220");
    const paper = readToken("--paper", "#F7F8FB");
    const muted = readToken("--muted", indigoSoft);
    const border = readToken("--border", indigoSoft);
    const tick = isDark ? paper : ink;
    return { ember, sage, indigoSoft, tick, muted, border, ink, paper };
  }, [isDark]);

  const chartData = {
    labels,
    datasets: [
      {
        label: title,
        data,
        borderColor: type === "donut" ? "transparent" : palette.ember,
        backgroundColor:
          type === "donut"
            ? labels.map(
                (_, index) =>
                  [palette.ember, palette.sage, palette.indigoSoft][index % 3],
              )
            : `${palette.ember}1A`,
        tension: 0.35,
      },
    ],
  };

  const options = {
    responsive: true,
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
        <Line data={chartData} options={options} />
      ) : type === "bar" ? (
        <Bar data={chartData} options={options} />
      ) : (
        <div className="mx-auto max-w-xs">
          <Doughnut data={chartData} options={options} />
        </div>
      )}
    </div>
  );
}
