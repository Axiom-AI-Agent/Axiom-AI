import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

interface AttentionGlowProps {
  active: boolean;
  className?: string;
  children: ReactNode;
}

export default function AttentionGlow({
  active,
  className,
  children,
}: AttentionGlowProps) {
  return (
    <div className={cn(className, active && "attention-glow")}>{children}</div>
  );
}
