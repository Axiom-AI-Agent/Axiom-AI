"use client";

import { useCallback, useEffect, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Loader2,
  RefreshCw,
  UserCheck,
} from "lucide-react";

import {
  assignEscalation,
  Escalation,
  getEscalations,
  resolveEscalation,
} from "@/lib/api";

import {
  EscalationSocketEvent,
  useEscalationSocket,
} from "@/hooks/useEscalationSocket";

const TENANT_ID = "tenant-demo-physics";

function statusClass(status: Escalation["status"]) {
  if (status === "resolved") {
    return "bg-emerald-500/10 text-emerald-300";
  }

  if (status === "assigned") {
    return "bg-blue-500/10 text-blue-300";
  }

  return "bg-amber-500/10 text-amber-300";
}

export default function ChatsPage() {
  const [escalations, setEscalations] = useState<Escalation[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionId, setActionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadEscalations = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      setEscalations(await getEscalations());
    } catch (requestError) {
      console.error(requestError);
      setError(
        "Could not load escalations. Confirm the backend is running.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadEscalations();
  }, [loadEscalations]);

  const handleSocketEvent = useCallback(
    (event: EscalationSocketEvent) => {
      if (
        event.type === "escalation.created" ||
        event.type === "escalation.assigned" ||
        event.type === "escalation.resolved"
      ) {
        void loadEscalations();
      }
    },
    [loadEscalations],
  );

  const { connected } = useEscalationSocket({
    tenantId: TENANT_ID,
    onEvent: handleSocketEvent,
  });

  async function handleAssign(escalationId: string) {
    setActionId(escalationId);
    setError(null);

    try {
      const updated = await assignEscalation(escalationId);

      setEscalations((current) =>
        current.map((item) =>
          item.id === escalationId ? updated : item,
        ),
      );
    } catch (requestError) {
      console.error(requestError);
      setError("The escalation could not be assigned.");
    } finally {
      setActionId(null);
    }
  }

  async function handleResolve(escalationId: string) {
    setActionId(escalationId);
    setError(null);

    try {
      const updated = await resolveEscalation(escalationId);

      setEscalations((current) =>
        current.map((item) =>
          item.id === escalationId ? updated : item,
        ),
      );
    } catch (requestError) {
      console.error(requestError);
      setError("The escalation could not be resolved.");
    } finally {
      setActionId(null);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">
            Escalation Inbox
          </h1>

          <p className="mt-1 text-sm text-gray-400">
            Review conversations that require human attention.
          </p>

          <div
            className={`mt-3 inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium ${
              connected
                ? "bg-emerald-500/10 text-emerald-300"
                : "bg-amber-500/10 text-amber-300"
            }`}
          >
            <span
              className={`h-2 w-2 rounded-full ${
                connected ? "bg-emerald-400" : "bg-amber-400"
              }`}
            />

            {connected
              ? "Live updates connected"
              : "Reconnecting..."}
          </div>
        </div>

        <button
          type="button"
          onClick={() => void loadEscalations()}
          disabled={loading}
          className="flex items-center gap-2 rounded-lg border border-gray-700 px-4 py-2 text-sm text-gray-200 hover:bg-gray-800 disabled:opacity-50"
        >
          <RefreshCw
            className={`h-4 w-4 ${
              loading ? "animate-spin" : ""
            }`}
          />
          Refresh
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-200">
          <AlertTriangle className="h-5 w-5" />
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex min-h-48 items-center justify-center">
          <Loader2 className="h-7 w-7 animate-spin text-gray-400" />
        </div>
      ) : escalations.length === 0 ? (
        <div className="rounded-xl border border-gray-800 bg-gray-900 p-10 text-center text-gray-400">
          No escalations have been recorded.
        </div>
      ) : (
        <div className="space-y-4">
          {escalations.map((escalation) => {
            const processing = actionId === escalation.id;

            return (
              <article
                key={escalation.id}
                className="rounded-xl border border-gray-800 bg-gray-900 p-5"
              >
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <h2 className="font-semibold text-white">
                      {escalation.student_name ??
                        escalation.student_id}
                    </h2>

                    <p className="mt-1 text-sm text-gray-400">
                      Reason:{" "}
                      {escalation.reason_code.replaceAll(
                        "_",
                        " ",
                      )}
                    </p>
                  </div>

                  <span
                    className={`rounded-full px-3 py-1 text-xs font-medium capitalize ${statusClass(
                      escalation.status,
                    )}`}
                  >
                    {escalation.status}
                  </span>
                </div>

                {escalation.student_message && (
                  <div className="mt-4 rounded-lg border border-gray-800 bg-gray-950 p-4">
                    <p className="text-xs uppercase tracking-wide text-gray-500">
                      Student message
                    </p>

                    <p className="mt-2 text-sm text-gray-200">
                      {escalation.student_message}
                    </p>
                  </div>
                )}

                <div className="mt-4 flex flex-wrap items-end justify-between gap-4">
                  <div className="text-xs text-gray-500">
                    <p>Escalation ID: {escalation.id}</p>

                    <p className="mt-1">
                      Created:{" "}
                      {new Date(
                        escalation.created_at,
                      ).toLocaleString()}
                    </p>
                  </div>

                  <div className="flex gap-2">
                    {escalation.status === "open" && (
                      <button
                        type="button"
                        disabled={processing}
                        onClick={() =>
                          void handleAssign(escalation.id)
                        }
                        className="flex items-center gap-2 rounded-lg bg-blue-600 px-3 py-2 text-sm text-white hover:bg-blue-500 disabled:opacity-50"
                      >
                        {processing ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <UserCheck className="h-4 w-4" />
                        )}
                        Assign
                      </button>
                    )}

                    {escalation.status !== "resolved" && (
                      <button
                        type="button"
                        disabled={processing}
                        onClick={() =>
                          void handleResolve(escalation.id)
                        }
                        className="flex items-center gap-2 rounded-lg bg-emerald-600 px-3 py-2 text-sm text-white hover:bg-emerald-500 disabled:opacity-50"
                      >
                        {processing ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <CheckCircle2 className="h-4 w-4" />
                        )}
                        Resolve
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
  );
}