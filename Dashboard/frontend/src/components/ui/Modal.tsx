"use client";

import {
  ReactNode,
  useCallback,
  useEffect,
  useId,
  useRef,
} from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { X } from "lucide-react";

import { cn } from "@/lib/utils";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: ReactNode;
  description?: ReactNode;
  children?: ReactNode;
  footer?: ReactNode;
  className?: string;
  maxWidthClass?: string;
}

export default function Modal({
  open,
  onClose,
  title,
  description,
  children,
  footer,
  className,
  maxWidthClass = "max-w-lg",
}: ModalProps) {
  const reduced = useReducedMotion();
  const panelRef = useRef<HTMLDivElement>(null);
  const titleId = useId();
  const descriptionId = useId();

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
      }
    },
    [onClose],
  );

  useEffect(() => {
    if (!open) {
      return;
    }
    document.addEventListener("keydown", handleKeyDown);
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    panelRef.current?.focus({ preventScroll: true });
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = previousOverflow;
    };
  }, [open, handleKeyDown]);

  const duration = reduced ? 0 : 0.2;

  return (
    <AnimatePresence>
      {open ? (
        <motion.div
          key="modal"
          className="fixed inset-0 z-50 grid place-items-center p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration }}
        >
          <button
            type="button"
            aria-label="Close dialog"
            className="absolute inset-0 bg-ink/55"
            onClick={onClose}
          />
          <motion.div
            ref={panelRef}
            role="dialog"
            aria-modal="true"
            aria-labelledby={titleId}
            aria-describedby={description ? descriptionId : undefined}
            tabIndex={-1}
            className={cn(
              "relative flex max-h-[90vh] w-full flex-col overflow-hidden rounded-md border border-border bg-surface text-fg outline-none",
              maxWidthClass,
              className,
            )}
            initial={reduced ? false : { opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={reduced ? { opacity: 0 } : { opacity: 0, y: 6 }}
            transition={{ duration, ease: [0.23, 1, 0.32, 1] }}
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex shrink-0 items-start justify-between gap-3 border-b border-border px-5 py-4">
              <div className="min-w-0">
                <h2
                  id={titleId}
                  className="font-display text-lg font-semibold text-heading"
                >
                  {title}
                </h2>
                {description ? (
                  <p id={descriptionId} className="mt-1 text-sm text-muted">
                    {description}
                  </p>
                ) : null}
              </div>
              <button
                type="button"
                onClick={onClose}
                className="rounded-md p-1.5 text-muted transition-colors hover:bg-hover hover:text-fg"
                aria-label="Close dialog"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            {children ? (
              <div className="min-h-0 flex-1 overflow-y-auto px-5 py-4">
                {children}
              </div>
            ) : null}
            {footer ? (
              <div className="flex shrink-0 items-center justify-end gap-2 border-t border-border px-5 py-3">
                {footer}
              </div>
            ) : null}
          </motion.div>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}
