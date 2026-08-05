import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError, chatApi } from "@/api/client";
import type { ChatTurnRecord, DemoSession, UIMessage } from "@/types";

function turnToUi(t: ChatTurnRecord): UIMessage {
  return {
    id: t.id,
    sender: t.sender,
    content: t.content,
    createdAt: t.created_at,
  };
}

function uid(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function useChat(session: DemoSession) {
  const [messages, setMessages] = useState<UIMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [backendOk, setBackendOk] = useState<boolean | null>(null);
  const sessionKey = `${session.tenantId}:${session.phone}`;
  const abortRef = useRef(0);

  const loadHistory = useCallback(async () => {
    const token = ++abortRef.current;
    setLoadingHistory(true);
    setError(null);
    try {
      const res = await chatApi.turns(session.tenantId, session.phone);
      if (token !== abortRef.current) return;
      setMessages(res.turns.map(turnToUi));
      setBackendOk(true);
    } catch (e) {
      if (token !== abortRef.current) return;
      setMessages([]);
      if (e instanceof ApiError && e.status === 404) {
        setBackendOk(true);
      } else {
        setBackendOk(false);
        setError(e instanceof Error ? e.message : "Failed to load history");
      }
    } finally {
      if (token === abortRef.current) setLoadingHistory(false);
    }
  }, [session.tenantId, session.phone]);

  useEffect(() => {
    void loadHistory();
  }, [loadHistory, sessionKey]);

  const clearLocal = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const send = useCallback(
    async (text: string, mediaUrl?: string | null) => {
      const trimmed = text.trim();
      if ((!trimmed && !mediaUrl) || loading) return null;

      const userMsg: UIMessage = {
        id: uid("local"),
        sender: "student",
        content: trimmed || (mediaUrl ? "[Payment slip attached]" : ""),
        createdAt: new Date().toISOString(),
        mediaUrl: mediaUrl ?? null,
        pending: true,
      };
      setMessages((prev) => [...prev, userMsg]);
      setLoading(true);
      setError(null);

      try {
        const res = await chatApi.send({
          tenant_id: session.tenantId,
          phone: session.phone,
          message: trimmed || "Please find my payment slip attached.",
          media_url: mediaUrl ?? undefined,
        });
        setBackendOk(true);
        const botMsg: UIMessage = {
          id: uid("bot"),
          sender: "bot",
          content: res.reply || "(empty reply)",
          createdAt: new Date().toISOString(),
        };
        setMessages((prev) => [
          ...prev.map((m) =>
            m.id === userMsg.id ? { ...m, pending: false } : m,
          ),
          botMsg,
        ]);
        return { studentText: userMsg.content, botText: botMsg.content, mediaUrl };
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Send failed";
        setError(msg);
        setBackendOk(false);
        setMessages((prev) =>
          prev.map((m) =>
            m.id === userMsg.id ? { ...m, pending: false, error: true } : m,
          ),
        );
        return null;
      } finally {
        setLoading(false);
      }
    },
    [loading, session.phone, session.tenantId],
  );

  return {
    messages,
    loading,
    loadingHistory,
    error,
    backendOk,
    send,
    clearLocal,
    reload: loadHistory,
  };
}
