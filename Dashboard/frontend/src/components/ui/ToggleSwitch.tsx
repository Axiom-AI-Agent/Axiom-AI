"use client";

import { cn } from "@/lib/utils";

interface ToggleSwitchProps {
  checked: boolean;
  onChange: (next: boolean) => void;
  disabled?: boolean;
  label?: string;
  description?: string;
  id?: string;
  className?: string;
}

export default function ToggleSwitch({
  checked,
  onChange,
  disabled = false,
  label,
  description,
  id,
  className,
}: ToggleSwitchProps) {
  const switchId = id ?? (label ? `toggle-${label.replace(/\s+/g, "-").toLowerCase()}` : undefined);

  return (
    <div className={cn("flex items-start justify-between gap-4", className)}>
      {(label || description) && (
        <div className="min-w-0 flex-1">
          {label ? (
            <label
              htmlFor={switchId}
              className="block text-sm font-medium text-heading"
            >
              {label}
            </label>
          ) : null}
          {description ? (
            <p className="mt-0.5 text-xs leading-relaxed text-muted">
              {description}
            </p>
          ) : null}
        </div>
      )}

      <button
        id={switchId}
        type="button"
        role="switch"
        aria-checked={checked}
        aria-label={label}
        disabled={disabled}
        onClick={() => onChange(!checked)}
        className={cn(
          "relative inline-flex h-6 w-11 shrink-0 items-center rounded-full border transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] disabled:cursor-not-allowed disabled:opacity-50",
          checked
            ? "border-blue/40 bg-blue"
            : "border-border bg-bg dark:bg-surface-elevated",
        )}
      >
        <span
          className={cn(
            "pointer-events-none inline-block h-4 w-4 rounded-full bg-white shadow-sm transition-transform duration-200",
            checked ? "translate-x-6" : "translate-x-1",
          )}
        />
      </button>
    </div>
  );
}
