"use client";

import { CheckCircle2, Info, X, XCircle } from "lucide-react";

import { Toast, useToast } from "@/context/ToastContext";

function toastStyles(variant: Toast["variant"]) {
  if (variant === "success") {
    return "border-emerald-500/30 bg-emerald-500/10 text-emerald-100";
  }

  if (variant === "error") {
    return "border-red-500/30 bg-red-500/10 text-red-100";
  }

  return "border-blue-500/30 bg-blue-500/10 text-blue-100";
}

function ToastIcon({ variant }: { variant: Toast["variant"] }) {
  if (variant === "success") {
    return <CheckCircle2 className="h-5 w-5 shrink-0" />;
  }

  if (variant === "error") {
    return <XCircle className="h-5 w-5 shrink-0" />;
  }

  return <Info className="h-5 w-5 shrink-0" />;
}

export default function ToastContainer() {
  const { toasts, dismissToast } = useToast();

  if (toasts.length === 0) {
    return null;
  }

  return (
    <div className="pointer-events-none fixed bottom-4 right-4 z-[100] flex w-full max-w-sm flex-col gap-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`pointer-events-auto flex items-start gap-3 rounded-lg border px-4 py-3 shadow-lg ${toastStyles(
            toast.variant,
          )}`}
        >
          <ToastIcon variant={toast.variant} />
          <p className="flex-1 text-sm">{toast.message}</p>
          <button
            type="button"
            onClick={() => dismissToast(toast.id)}
            className="rounded p-0.5 hover:bg-white/10"
            aria-label="Dismiss notification"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ))}
    </div>
  );
}
