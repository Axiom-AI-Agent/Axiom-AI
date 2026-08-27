"use client";

import { CheckCircle2, Info, X, XCircle } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";

import { Toast, useToast } from "@/context/ToastContext";
import { surfaceCard } from "@/lib/ui";
import { cn } from "@/lib/utils";

function toastAccent(variant: Toast["variant"]) {
  if (variant === "success") {
    return "text-sage";
  }
  if (variant === "error") {
    return "text-blue";
  }
  return "text-muted";
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

  return (
    <div className="pointer-events-none fixed bottom-4 right-4 z-[100] flex w-full max-w-sm flex-col gap-2">
      <AnimatePresence>
        {toasts.map((toast) => (
          <motion.div
            key={toast.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 6 }}
            transition={{ duration: 0.2 }}
            className={cn(
              surfaceCard,
              "pointer-events-auto flex items-start gap-3 px-4 py-3",
              toastAccent(toast.variant),
            )}
          >
            <ToastIcon variant={toast.variant} />
            <p className="flex-1 text-sm text-fg">{toast.message}</p>
            <button
              type="button"
              onClick={() => dismissToast(toast.id)}
              className="rounded-md p-0.5 text-muted transition-colors hover:bg-hover hover:text-fg"
              aria-label="Dismiss notification"
            >
              <X className="h-4 w-4" />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
