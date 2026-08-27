"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Suspense,
  useCallback,
  useEffect,
  useState,
} from "react";
import {
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  Loader2,
  MessageSquare,
  RefreshCw,
  Send,
  XCircle,
} from "lucide-react";

import { useToast } from "@/context/ToastContext";
import { useTenant } from "@/context/TenantContext";
import SageCheck from "@/components/SageCheck";
import { cn } from "@/lib/utils";
import { usePolling } from "@/hooks/usePolling";
import {
  EscalationSocketEvent,
  useEscalationSocket,
} from "@/hooks/useEscalationSocket";
import {
  Escalation,
  EscalationStatus,
  getEscalations,
  rejectEscalation,
  resolveEscalation,
  sendStaffMessage,
} from "@/lib/api";

function statusClass(status: EscalationStatus) {
  if (status === "resolved") {
    return "bg-sage/15 text-sage";
  }

  if (status === "assigned") {
    return "bg-indigo-soft/20 text-muted";
  }

  return "bg-ember/15 text-ember";
}

function isPaymentReason(reasonCode: string) {
  return (
    reasonCode === "payment_receipt" ||
    reasonCode === "enrollment_payment_review"
  );
}

function InboxContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { tenantId } = useTenant();
  const { showToast } = useToast();

  const [escalations, setEscalations] = useState<Escalation[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionId, setActionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [
    replyDrafts,
    setReplyDrafts,
  ] = useState<
    Record<string, string>
  >({});

  const [
    sendingReplyId,
    setSendingReplyId,
  ] = useState<string | null>(
    null,
  );

  const statusFilter =
    (searchParams.get("status") as EscalationStatus | null) ?? undefined;
  const reasonFilter = searchParams.get("reason_code") ?? undefined;

  const loadEscalations = useCallback(
    async (showSpinner = false) => {
      if (showSpinner) {
        setLoading(true);
      }

      setError(null);

      try {
        setEscalations(
          await getEscalations(
            {
              status: statusFilter,
              reason_code: reasonFilter,
            },
            tenantId,
          ),
        );
      } catch (requestError) {
        console.error(requestError);
        setError(
          "Could not load the escalation inbox. Confirm Dashboard/backend is running on port 8001.",
        );
      } finally {
        setLoading(false);
      }
    },
    [reasonFilter, statusFilter, tenantId],
  );

  useEffect(() => {
    void loadEscalations(true);
  }, [loadEscalations]);

  usePolling({
    enabled: true,
    intervalMs: 5000,
    onPoll: () => loadEscalations(false),
  });

  const handleSocketEvent = useCallback(
    (event: EscalationSocketEvent) => {
      if (
        event.type === "escalation.created" ||
        event.type === "escalation.assigned" ||
        event.type === "escalation.resolved"
      ) {
        void loadEscalations(false);
      }
    },
    [loadEscalations],
  );

  const { connected } = useEscalationSocket({
    tenantId,
    onEvent: handleSocketEvent,
  });

  async function handleResolve(escalation: Escalation) {
    setActionId(escalation.id);
    setError(null);

    try {
      const result = await resolveEscalation(escalation.id, undefined, tenantId);

      setEscalations((current) =>
        current.filter((item) => item.id !== escalation.id),
      );

      showToast(
        result.student_notified
          ? "Escalation resolved and student notified."
          : "Escalation resolved.",
        "success",
      );
    } catch (requestError) {
      console.error(requestError);
      showToast("The escalation could not be resolved.", "error");
    } finally {
      setActionId(null);
    }
  }

  async function handleReject(escalation: Escalation) {
    const confirmed = window.confirm(
      "Reject this payment receipt? The student will be notified and enrollment will not be activated.",
    );

    if (!confirmed) {
      return;
    }

    setActionId(escalation.id);
    setError(null);

    try {
      const result = await rejectEscalation(escalation.id, undefined, tenantId);

      setEscalations((current) =>
        current.filter((item) => item.id !== escalation.id),
      );

      showToast(
        result.student_notified
          ? "Payment rejected and student notified."
          : "Payment rejected.",
        "success",
      );
    } catch (requestError) {
      console.error(requestError);
      showToast("The payment could not be rejected.", "error");
    } finally {
      setActionId(null);
    }
  }
  async function handleReply(
    escalation: Escalation,
  ) {
    const phone =
      escalation.student_phone;

    const reply =
      (
        replyDrafts[
          escalation.id
        ] ?? ""
      ).trim();

    if (!phone) {
      showToast(
        "This student has no phone number.",
        "error",
      );

      return;
    }

    if (!reply) {
      return;
    }

    setSendingReplyId(
      escalation.id,
    );

    try {
      const result =
        await sendStaffMessage(
          {
            phone,
            message: reply,
          },
          tenantId,
        );

      if (!result.delivered) {
        throw new Error(
          "Message was not delivered.",
        );
      }

      setReplyDrafts(
        (current) => ({
          ...current,
          [escalation.id]: "",
        }),
      );

      showToast(
        "Reply sent to the student on WhatsApp.",
        "success",
      );
    } catch (requestError) {
      console.error(
        requestError,
      );

      showToast(
        "Could not send the WhatsApp reply.",
        "error",
      );
    } finally {
      setSendingReplyId(
        null,
      );
    }
  }
  function updateFilter(key: string, value: string) {
    const params = new URLSearchParams(searchParams.toString());

    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }

    router.replace(`/dashboard/inbox?${params.toString()}`);
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col overflow-hidden">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-heading">
            Escalation Inbox
          </h1>
          <p className="mt-1 text-sm text-muted">
            Unified HITL queue for payment receipts and tutor requests.
          </p>
          <p className="mt-2 text-xs text-muted">
            Auto-refreshes every 5 seconds
            {connected ? " · WebSocket connected" : " · WebSocket reconnecting"}
          </p>
        </div>

        <button
          type="button"
          onClick={() => void loadEscalations(true)}
          disabled={loading}
          className="flex items-center gap-2 rounded-lg border border-border px-4 py-2 text-sm text-fg hover:bg-hover bg-surface disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      <div className="flex flex-wrap gap-3">
        <select
          value={statusFilter ?? ""}
          onChange={(event) => updateFilter("status", event.target.value)}
          className="rounded-lg border border-border bg-surface px-3 py-2 text-sm text-heading"
        >
          <option value="">All statuses</option>
          <option value="open">Open</option>
          <option value="assigned">Assigned</option>
          <option value="resolved">Resolved</option>
        </select>

        <select
          value={reasonFilter ?? ""}
          onChange={(event) =>
            updateFilter("reason_code", event.target.value)
          }
          className="rounded-lg border border-border bg-surface px-3 py-2 text-sm text-heading"
        >
        <option value="">All reasons</option>
        <option value="payment_receipt">Payment receipt</option>
        <option value="talk_to_tutor">Talk to tutor</option>
        <option value="low_rag_confidence">
          Low RAG confidence
        </option>
        </select>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto pr-1">
        {error && (
        <div className="flex items-center gap-2 rounded-lg border border-border bg-surface p-4 text-fg">
          <AlertTriangle className="h-5 w-5" />
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex min-h-48 items-center justify-center">
          <Loader2 className="h-7 w-7 animate-spin text-muted" />
        </div>
      ) : escalations.length === 0 ? (
        <div className="rounded-xl border border-border bg-surface p-10 text-center text-muted">
          No escalations match the current filters.
        </div>
      ) : (
        <div className="space-y-4">
          {escalations.map((escalation) => {
            const processing = actionId === escalation.id;
            const payment = isPaymentReason(escalation.reason_code);

            return (
              <article
                key={escalation.id}
                className="rounded-md border border-border bg-surface p-5"
              >
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <h2 className="font-semibold text-heading">
                      {escalation.student_name ?? escalation.student_id}
                    </h2>
                    <p className="mt-1 text-sm text-muted">
                      {escalation.student_phone ?? "No phone on file"}
                    </p>
                    <p className="mt-1 text-sm text-muted">
                      Reason:{" "}
                      {escalation.reason_code.replaceAll("_", " ")}
                    </p>
                  </div>

                  <span
                    className={cn(
                      "inline-flex items-center gap-1 rounded-md px-3 py-1 text-xs font-medium capitalize",
                      statusClass(escalation.status),
                    )}
                  >
                    {escalation.status === "resolved" ? (
                      <SageCheck label="Resolved" />
                    ) : null}
                    {escalation.status}
                  </span>
                </div>

                {escalation.student_message && (
                  <div className="mt-4 rounded-lg border border-border bg-surface p-4">
                    <p className="text-xs uppercase tracking-wide text-muted">
                      Student message
                    </p>
                    <p className="mt-2 text-sm text-fg">
                      {escalation.student_message}
                    </p>
                  </div>
                )}

                {escalation.media_url && (
                  <div className="mt-4 rounded-lg border border-border bg-surface p-4">
                    <p className="text-xs uppercase tracking-wide text-muted">
                      Payment slip
                    </p>
                    <div className="mt-3 flex flex-wrap items-start gap-4">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={escalation.media_url}
                        alt="Payment receipt"
                        className="max-h-48 rounded-lg border border-border object-contain"
                      />
                      <a
                        href={escalation.media_url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-2 text-sm text-muted hover:text-fg"
                      >
                        Open full size
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    </div>
                  </div>
                )}

                {(escalation.reviewed_by || escalation.reviewed_at) && (
                  <div className="mt-4 text-xs text-muted">
                    {escalation.reviewed_by && (
                      <p>Reviewed by: {escalation.reviewed_by}</p>
                    )}
                    {escalation.reviewed_at && (
                      <p className="mt-1">
                        Reviewed at:{" "}
                        {new Date(escalation.reviewed_at).toLocaleString()}
                      </p>
                    )}
                    {escalation.resolution && (
                      <p className="mt-1">
                        Resolution: {escalation.resolution}
                      </p>
                    )}
                  </div>
                )}
{escalation.student_phone &&
  escalation.status !== "resolved" && (
    <div className="mt-4 rounded-lg border border-border bg-surface p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-muted">
        Reply to student
      </p>

      <div className="mt-3 flex flex-col gap-2 sm:flex-row">
        <input
          type="text"
          value={replyDrafts[escalation.id] ?? ""}
          onChange={(event) =>
            setReplyDrafts((current) => ({
              ...current,
              [escalation.id]: event.target.value,
            }))
          }
          onKeyDown={(event) => {
            if (
              event.key === "Enter" &&
              !event.shiftKey &&
              sendingReplyId !== escalation.id &&
              (replyDrafts[escalation.id] ?? "").trim()
            ) {
              event.preventDefault();
              void handleReply(escalation);
            }
          }}
          placeholder="Type a reply to send via WhatsApp..."
          className="flex-1 rounded-lg border border-border bg-surface px-3 py-2 text-sm text-heading outline-none focus:border-indigo-soft"
        />

        <button
          type="button"
          disabled={
            sendingReplyId === escalation.id ||
            !(replyDrafts[escalation.id] ?? "").trim()
          }
          onClick={() => void handleReply(escalation)}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-ember px-4 py-2 text-sm font-medium text-ink hover:bg-ember/90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {sendingReplyId === escalation.id ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}

          Send Reply
        </button>
      </div>

      <p className="mt-2 text-xs text-muted">
        Sends directly to {escalation.student_phone} through WhatsApp.
      </p>
    </div>
  )}
                <div className="mt-4 flex flex-wrap items-end justify-between gap-4">
                  <div className="text-xs text-muted">
                    <p>ID: {escalation.id}</p>
                    <p className="mt-1">
                      Created:{" "}
                      {new Date(escalation.created_at).toLocaleString()}
                    </p>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {escalation.student_phone && (
                      <Link
                        href={`/dashboard/messages?phone=${encodeURIComponent(
                          escalation.student_phone,
                        )}`}
                        className="inline-flex items-center gap-2 rounded-lg border border-border px-3 py-2 text-sm text-fg hover:bg-hover bg-surface"
                      >
                        <MessageSquare className="h-4 w-4" />
                        Open chat
                      </Link>
                    )}

                    {escalation.status !== "resolved" && (
                      <button
                        type="button"
                        disabled={processing}
                        onClick={() => void handleResolve(escalation)}
                        className="inline-flex items-center gap-2 rounded-lg bg-ember px-3 py-2 text-sm text-white hover:bg-ember/90 disabled:opacity-50"
                      >
                        {processing ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <CheckCircle2 className="h-4 w-4" />
                        )}
                        {payment ? "Approve" : "Resolve"}
                      </button>
                    )}

                    {payment && escalation.status !== "resolved" && (
                      <button
                        type="button"
                        disabled={processing}
                        onClick={() => void handleReject(escalation)}
                        className="inline-flex items-center gap-2 rounded-lg border border-border bg-surface px-3 py-2 text-sm text-fg hover:bg-hover disabled:opacity-50"
                      >
                        <XCircle className="h-4 w-4" />
                        Reject
                      </button>
                    )}
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      )}
      </div>
    </div>
  );
}

export default function InboxPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-48 items-center justify-center">
          <Loader2 className="h-7 w-7 animate-spin text-muted" />
        </div>
      }
    >
      <InboxContent />
    </Suspense>
  );
}
