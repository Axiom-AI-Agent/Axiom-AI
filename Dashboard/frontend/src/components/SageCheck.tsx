import { Check } from "lucide-react";

import { cn } from "@/lib/utils";

export default function SageCheck({
  className,
  label = "Healthy",
}: {
  className?: string;
  label?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 text-sage",
        className,
      )}
    >
      <Check className="h-3.5 w-3.5" strokeWidth={2.5} aria-hidden />
      <span className="sr-only">{label}</span>
    </span>
  );
}
