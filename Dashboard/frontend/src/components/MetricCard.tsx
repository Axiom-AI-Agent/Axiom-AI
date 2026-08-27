"use client";

import { ReactNode } from "react";
import { motion, useReducedMotion } from "framer-motion";

import SageCheck from "@/components/SageCheck";
import { surfaceCard } from "@/lib/ui";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: number | string;
  icon?: ReactNode;
  attention?: boolean;
  healthy?: boolean;
  className?: string;
}

export default function MetricCard({
  title,
  value,
  icon,
  attention = false,
  healthy = false,
  className,
}: MetricCardProps) {
  const reduced = useReducedMotion();

  return (
    <motion.div
      className={cn("h-full", className)}
      initial={reduced ? false : { opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.28, ease: "easeOut" }}
      whileHover={reduced ? undefined : { y: -2 }}
    >
      <div
        className={cn(
          surfaceCard,
          "flex h-full items-center p-5 transition-shadow duration-200 hover:shadow-[var(--shadow-soft)]",
        )}
      >
        {icon ? (
          <div
            className={cn(
              "mr-4 flex h-11 w-11 shrink-0 items-center justify-center rounded-xl",
              attention
                ? "bg-blue/15 text-blue"
                : healthy
                  ? "bg-sage/15 text-sage"
                  : "bg-blue/10 text-blue",
            )}
          >
            {icon}
          </div>
        ) : null}
        <div className="min-w-0 flex-1">
          <p className="flex items-center gap-1.5 text-sm font-medium text-muted">
            {title}
            {healthy && !attention ? <SageCheck label="Healthy" /> : null}
          </p>
          <p className="font-display mt-1 text-2xl font-semibold tabular tracking-tight text-heading">
            {value}
          </p>
        </div>
      </div>
    </motion.div>
  );
}
