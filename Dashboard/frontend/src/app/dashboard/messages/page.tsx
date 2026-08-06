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
import { usePolling } from "@/hooks/usePolling";
import {
  ChatConversation,
  ChatThread,
  getChatConversations,
  getChatThread,
  sendStaffMessage,
} from "@/lib/api";

function senderBubbleClass(sender: string) {
  if (sender === "student") {
    return "bg-slate-100 dark:bg-slate-800 text-gray-100 self-start";
  }

  if (sender === "staff") {
    return "bg-blue-600 text-slate-900 dark:text-white self-end";
  }

  return "bg-emerald-900/60 text-emerald-100 self-start";
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
  const [message, setMessage] = useState("");
  const [loadingList, setLoadingList] = useState(true);
  const [loadingThread, setLoadingThread] = useState(false);
  const [sending, setSending] = useState(false);
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
    async (phone: string) => {
      if (!phone) {
        setThread(null);
        return;
      }

      setLoadingThread(true);
      setError(null);

      try {
        setThread(await getChatThread(phone, { limit: 100 }, tenantId));
      } catch (requestError) {
        console.error(requestError);
        setThread(null);
        setError("Could not load this conversation.");
      } finally {
        setLoadingThread(false);
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
    }
  }, [loadThread, selectedPhone]);

  usePolling({
    enabled: true,
    intervalMs: 5000,
    onPoll: async () => {
      await loadConversations();
      if (selectedPhone) {
        await loadThread(selectedPhone);
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
          ? "Message sent to student."
          : "Message saved (dry-run delivery).",
        "success",
      );
    } catch (requestError) {
      console.error(requestError);
      showToast("Could not send the message.", "error");
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900 dark:text-white">Messages</h1>
          <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
            Staff chat with students — same threads as WhatsApp.
          </p>
        </div>

        <div className="flex gap-2">
          <Link
            href={
              needsAttention
                ? "/dashboard/messages"
                : "/dashboard/messages?attention=1"
            }
            className="rounded-lg border border-slate-300 dark:border-slate-700 px-3 py-2 text-sm text-slate-800 dark:text-slate-200 hover:bg-slate-100 dark:bg-slate-800"
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
            className="flex items-center gap-2 rounded-lg border border-slate-300 dark:border-slate-700 px-3 py-2 text-sm text-slate-800 dark:text-slate-200 hover:bg-slate-100 dark:bg-slate-800"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-200">
          <AlertTriangle className="h-5 w-5" />
          {error}
        </div>
      )}

      <div className="grid min-h-[32rem] grid-cols-1 overflow-hidden rounded-xl border border-slate-200 dark:border-slate-800 lg:grid-cols-[18rem_1fr]">
        <aside className="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 lg:border-b-0 lg:border-r">
          <div className="border-b border-slate-200 dark:border-slate-800 px-4 py-3 text-sm font-medium text-slate-700 dark:text-slate-300">
            Conversations
          </div>

          {loadingList ? (
            <div className="flex justify-center p-8">
              <Loader2 className="h-6 w-6 animate-spin text-slate-600 dark:text-slate-400" />
            </div>
          ) : conversations.length === 0 ? (
            <p className="p-4 text-sm text-slate-500 dark:text-slate-400">No conversations yet.</p>
          ) : (
            <ul className="max-h-[28rem] overflow-y-auto">
              {conversations.map((conversation) => {
                const active = conversation.phone === selectedPhone;

                return (
                  <li key={conversation.session_id}>
                    <button
                      type="button"
                      onClick={() => selectConversation(conversation.phone)}
                      className={`w-full border-b border-gray-900 px-4 py-3 text-left transition hover:bg-white dark:bg-slate-900 ${
                        active ? "bg-white dark:bg-slate-900" : ""
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <p className="truncate text-sm font-medium text-slate-900 dark:text-white">
                          {conversation.student_name ?? conversation.phone}
                        </p>
                        {conversation.has_open_escalation && (
                          <span className="rounded-full bg-amber-500/20 px-2 py-0.5 text-[10px] text-amber-300">
                            !
                          </span>
                        )}
                      </div>
                      <p className="mt-1 truncate text-xs text-slate-500 dark:text-slate-400">
                        {conversation.last_message}
                      </p>
                    </button>
                  </li>
                );
              })}
            </ul>
          )}
        </aside>

        <section className="flex min-h-[32rem] flex-col bg-white dark:bg-slate-900">
          {!selectedPhone ? (
            <div className="flex flex-1 items-center justify-center text-sm text-slate-500 dark:text-slate-400">
              Select a conversation to view the thread.
            </div>
          ) : loadingThread || !thread ? (
            <div className="flex flex-1 items-center justify-center">
              <Loader2 className="h-7 w-7 animate-spin text-slate-600 dark:text-slate-400" />
            </div>
          ) : (
            <>
              <div className="border-b border-slate-200 dark:border-slate-800 px-4 py-3">
                <h2 className="font-medium text-slate-900 dark:text-white">
                  {thread.student_name ?? thread.phone}
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400">{thread.phone}</p>

                {thread.open_escalations.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {thread.open_escalations.map((escalation) => (
                      <Link
                        key={escalation.id}
                        href={`/dashboard/inbox?status=open&reason_code=${encodeURIComponent(
                          escalation.reason_code,
                        )}`}
                        className="rounded-full bg-amber-500/10 px-2 py-1 text-xs text-amber-300 hover:bg-amber-500/20"
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
                    className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm ${senderBubbleClass(
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
                className="flex gap-2 border-t border-slate-200 dark:border-slate-800 p-4"
              >
                <input
                  type="text"
                  value={message}
                  onChange={(event) => setMessage(event.target.value)}
                  placeholder="Type a staff reply…"
                  className="flex-1 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 px-3 py-2 text-sm text-slate-900 dark:text-white outline-none focus:border-gray-500"
                />
                <button
                  type="submit"
                  disabled={sending || !message.trim()}
                  className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-50"
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
          <Loader2 className="h-7 w-7 animate-spin text-slate-600 dark:text-slate-400" />
        </div>
      }
    >
      <MessagesContent />
    </Suspense>
  );
}
