"use client";

import { useId } from "react";

import { cn } from "@/lib/utils";

interface ToggleSwitchProps {
  checked: boolean;
  onChange: (next: boolean) => void;
  disabled?: boolean;
  label?: string;
  description?: string;
  id?: string;
  className?: string;
  /** Smaller control for dense tables */
  size?: "md" | "sm";
}

export default function ToggleSwitch({
  checked,
  onChange,
  disabled = false,
  label,
  description,
  id,
  className,
  size = "md",
}: ToggleSwitchProps) {
  const reactId = useId();
  // Always unique — never derive from label alone (duplicate labels broke class cards).
  const switchId = id ?? `toggle-${reactId}`;

  const track =
    size === "sm"
      ? "h-5 w-9"
      : "h-7 w-12";
  const thumb =
    size === "sm"
      ? "h-3.5 w-3.5"
      : "h-5 w-5";
  const thumbOn =
    size === "sm" ? "translate-x-[1.125rem]" : "translate-x-6";
  const thumbOff = "translate-x-1";

  return (
    <div
      className={cn(
        "flex items-center justify-between gap-3",
        description && "items-start",
        className,
      )}
    >
      {(label || description) && (
        <div className="min-w-0 flex-1">
          {label ? (
            <label
              htmlFor={switchId}
              className="block cursor-pointer text-sm font-medium text-heading"
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
        aria-label={label ?? (checked ? "On" : "Off")}
        disabled={disabled}
        onClick={(event) => {
          event.preventDefault();
          event.stopPropagation();
          onChange(!checked);
        }}
        className={cn(
          "relative z-10 inline-flex shrink-0 items-center rounded-full border transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] disabled:cursor-not-allowed disabled:opacity-50",
          track,
          checked
            ? "border-blue bg-blue shadow-[0_0_0_3px_color-mix(in_srgb,var(--blue)_18%,transparent)]"
            : "border-border bg-muted/25 dark:bg-surface-elevated",
        )}
      >
        <span
          className={cn(
            "pointer-events-none inline-block rounded-full bg-white shadow-md transition-transform duration-200",
            thumb,
            checked ? thumbOn : thumbOff,
          )}
        />
      </button>
    </div>
  );
}
