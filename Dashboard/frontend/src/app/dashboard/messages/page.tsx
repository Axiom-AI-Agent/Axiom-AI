"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import {
  FormEvent,
  Suspense,
  useCallback,
  useEffect,
  useState,
} from "react";
import {
  AlertTriangle,
  Loader2,
  RefreshCw,
  Send,
} from "lucide-react";

import { useToast } from "@/context/ToastContext";
import { useTenant } from "@/context/TenantContext";
import { cn } from "@/lib/utils";
import { usePolling } from "@/hooks/usePolling";
import {
  ChatConversation,
  ChatThread,
  getChatConversations,
  getChatThread,
  getStudentByPhone,
  sendStaffMessage,
  Student,
  updateStudentHumanMode,
} from "@/lib/api";
import ToggleSwitch from "@/components/ui/ToggleSwitch";

function senderBubbleClass(sender: string) {
  if (sender === "student") {
    return "self-start border border-border bg-bg text-fg";
  }

  if (sender === "staff") {
    return "self-end bg-blue text-paper";
  }

  return "self-start bg-indigo-soft/70 text-paper";
}

function MessagesContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { tenantId } = useTenant();
  const { showToast } = useToast();

  const selectedPhone = searchParams.get("phone") ?? "";
  const needsAttention = searchParams.get("attention") === "1";

  const [conversations, setConversations] = useState<ChatConversation[]>([]);
  const [thread, setThread] = useState<ChatThread | null>(null);
  const [threadStudent, setThreadStudent] = useState<Student | null>(null);
  const [message, setMessage] = useState("");
  const [loadingList, setLoadingList] = useState(true);
  const [loadingThread, setLoadingThread] = useState(false);
  const [sending, setSending] = useState(false);
  const [togglingAi, setTogglingAi] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadConversations = useCallback(async () => {
    setError(null);

    try {
      setConversations(
        await getChatConversations(
          {
            limit: 50,
            openEscalationOnly: needsAttention,
          },
          tenantId,
        ),
      );
    } catch (requestError) {
      console.error(requestError);
      setError("Could not load conversations.");
    } finally {
      setLoadingList(false);
    }
  }, [needsAttention, tenantId]);

  const loadThread = useCallback(
    async (phone: string, options?: { silent?: boolean }) => {
      if (!phone) {
        setThread(null);
        setThreadStudent(null);
        return;
      }

      const silent = options?.silent === true;
      if (!silent) {
        setLoadingThread(true);
        setError(null);
      }

      try {
        const [nextThread, profile] = await Promise.all([
          getChatThread(phone, { limit: 100 }, tenantId),
          getStudentByPhone(phone, tenantId).catch(() => null),
        ]);
        setThread(nextThread);
        setThreadStudent(profile?.student ?? null);
      } catch (requestError) {
        console.error(requestError);
        if (!silent) {
          setThread(null);
          setThreadStudent(null);
          setError("Could not load this conversation.");
        }
      } finally {
        if (!silent) {
          setLoadingThread(false);
        }
      }
    },
    [tenantId],
  );

  useEffect(() => {
    void loadConversations();
  }, [loadConversations]);

  useEffect(() => {
    if (selectedPhone) {
      void loadThread(selectedPhone);
    } else {
      setThread(null);
      setThreadStudent(null);
    }
  }, [loadThread, selectedPhone]);

  usePolling({
    enabled: true,
    intervalMs: 8000,
    onPoll: async () => {
      await loadConversations();
      if (selectedPhone) {
        // Silent refresh — keep the open thread readable (no spinner flash).
        await loadThread(selectedPhone, { silent: true });
      }
    },
  });

  function selectConversation(phone: string) {
    const params = new URLSearchParams(searchParams.toString());
    params.set("phone", phone);
    router.replace(`/dashboard/messages?${params.toString()}`);
  }

  async function handleSend(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!selectedPhone || !message.trim()) {
      return;
    }

    setSending(true);

    try {
      const result = await sendStaffMessage(
        {
          phone: selectedPhone,
          message: message.trim(),
        },
        tenantId,
      );

      setMessage("");
      await loadThread(selectedPhone);
      await loadConversations();

      showToast(
        result.delivered
          ? "Message sent to student on Telegram."
          : "Message could not be delivered.",
        result.delivered ? "success" : "error",
      );
    } catch (requestError) {
      console.error(requestError);
      showToast("Could not send the message.", "error");
    } finally {
      setSending(false);
    }
  }

  async function handleThreadHumanMode(nextAiEnabled: boolean) {
    if (!threadStudent) {
      return;
    }

    setTogglingAi(true);

    try {
      const updated = await updateStudentHumanMode(
        threadStudent.id,
        !nextAiEnabled,
        tenantId,
      );
      setThreadStudent((current) =>
        current ? { ...current, ...updated } : current,
      );
      showToast(
        updated.human_mode
          ? "Human mode on — AI paused for this student."
          : "AI responses enabled for this student.",
        "success",
      );
    } catch (requestError) {
      console.error(requestError);
      showToast("Could not update AI mode.", "error");
    } finally {
      setTogglingAi(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-heading">Messages</h1>
          <p className="mt-1 text-sm text-muted">
            Staff chat with students — same threads as Telegram.
          </p>
        </div>

        <div className="flex gap-2">
          <Link
            href={
              needsAttention
                ? "/dashboard/messages"
                : "/dashboard/messages?attention=1"
            }
            className="rounded-lg border border-border px-3 py-2 text-sm text-fg hover:bg-hover bg-surface"
          >
            {needsAttention ? "All conversations" : "Needs attention"}
          </Link>

          <button
            type="button"
            onClick={() => {
              void loadConversations();
              if (selectedPhone) {
                void loadThread(selectedPhone);
              }
            }}
            className="flex items-center gap-2 rounded-lg border border-border px-3 py-2 text-sm text-fg hover:bg-hover bg-surface"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-border bg-surface p-4 text-fg">
          <AlertTriangle className="h-5 w-5" />
          {error}
        </div>
      )}

      <div className="grid min-h-[32rem] grid-cols-1 overflow-hidden rounded-xl border border-border lg:grid-cols-[18rem_1fr]">
        <aside className="border-b border-border bg-surface lg:border-b-0 lg:border-r">
          <div className="border-b border-border px-4 py-3 text-sm font-medium text-fg">
            Conversations
          </div>

          {loadingList ? (
            <div className="flex justify-center p-8">
              <Loader2 className="h-6 w-6 animate-spin text-muted" />
            </div>
          ) : conversations.length === 0 ? (
            <p className="p-4 text-sm text-muted">No conversations yet.</p>
          ) : (
            <ul className="max-h-[28rem] overflow-y-auto">
              {conversations.map((conversation) => {
                const active = conversation.phone === selectedPhone;

                return (
                  <li key={conversation.session_id}>
                    <button
                      type="button"
                      onClick={() => selectConversation(conversation.phone)}
                      className={cn(
                        "w-full border-b border-border px-4 py-3 text-left transition hover:bg-hover",
                        active && "bg-hover",
                      )}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <p className="truncate text-sm font-medium text-heading">
                          {conversation.student_name ?? conversation.phone}
                        </p>
                        {conversation.has_open_escalation ? (
                          <span className="text-[10px] font-medium uppercase tracking-wide text-blue">
                            Attention
                          </span>
                        ) : null}
                      </div>
                      <p className="mt-1 truncate text-xs text-muted">
                        {conversation.last_message}
                      </p>
                    </button>
                  </li>
                );
              })}
            </ul>
          )}
        </aside>

        <section className="flex min-h-[32rem] flex-col bg-surface">
          {!selectedPhone ? (
            <div className="flex flex-1 items-center justify-center text-sm text-muted">
              Select a conversation to view the thread.
            </div>
          ) : loadingThread || !thread ? (
            <div className="flex flex-1 items-center justify-center">
              <Loader2 className="h-7 w-7 animate-spin text-muted" />
            </div>
          ) : (
            <>
              <div className="border-b border-border px-4 py-3">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0">
                    <h2 className="font-medium text-heading">
                      {thread.student_name ?? thread.phone}
                    </h2>
                    <p className="text-xs text-muted">{thread.phone}</p>
                  </div>

                  {threadStudent ? (
                    <div className="rounded-xl border border-border bg-bg/60 px-3 py-2">
                      <ToggleSwitch
                        size="sm"
                        label={
                          threadStudent.human_mode ? "Human mode" : "AI on"
                        }
                        checked={!threadStudent.human_mode}
                        disabled={togglingAi}
                        onChange={(next) => void handleThreadHumanMode(next)}
                        className="min-w-[9rem]"
                      />
                    </div>
                  ) : null}
                </div>

                {thread.open_escalations.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {thread.open_escalations.map((escalation) => (
                      <Link
                        key={escalation.id}
                        href={`/dashboard/inbox?status=open&reason_code=${encodeURIComponent(
                          escalation.reason_code,
                        )}`}
                        className="rounded-md border border-border px-2 py-1 text-xs text-blue hover:bg-hover"
                      >
                        Open: {escalation.reason_code.replaceAll("_", " ")}
                      </Link>
                    ))}
                  </div>
                )}
              </div>

              <div className="flex flex-1 flex-col gap-3 overflow-y-auto p-4">
                {thread.turns.map((turn) => (
                  <div
                    key={turn.id}
                    className={`max-w-[80%] rounded-md px-4 py-2 text-sm ${senderBubbleClass(
                      turn.sender,
                    )}`}
                  >
                    <p className="mb-1 text-[10px] uppercase tracking-wide opacity-70">
                      {turn.sender}
                    </p>
                    <p>{turn.content}</p>
                    <p className="mt-1 text-[10px] opacity-60">
                      {new Date(turn.created_at).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>

              <form
                onSubmit={handleSend}
                className="flex gap-2 border-t border-border p-4"
              >
                <input
                  type="text"
                  value={message}
                  onChange={(event) => setMessage(event.target.value)}
                  placeholder="Type a staff reply…"
                  className="flex-1 rounded-lg border border-border bg-surface px-3 py-2 text-sm text-heading outline-none focus:border-indigo-soft"
                />
                <button
                  type="submit"
                  disabled={sending || !message.trim()}
                  className="inline-flex items-center gap-2 rounded-lg bg-blue px-4 py-2 text-sm font-medium text-paper hover:bg-blue/90 disabled:opacity-50"
                >
                  {sending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                  Send
                </button>
              </form>
            </>
          )}
        </section>
      </div>
    </div>
  );
}

export default function MessagesPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-48 items-center justify-center">
          <Loader2 className="h-7 w-7 animate-spin text-muted" />
        </div>
      }
    >
      <MessagesContent />
    </Suspense>
  );
}
