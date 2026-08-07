import { useCallback, useState } from "react";
import type { DemoSession } from "@/types";
import { ENROLLED_DEMO_PHONE, SESSION_STORAGE_KEY, TENANT_ID } from "@/shared/constants";

function generatePhone(): string {
  const suffix = Math.floor(Math.random() * 10000)
    .toString()
    .padStart(4, "0");
  return `9477099${suffix}`;
}

function createSession(): DemoSession {
  return {
    tenantId: TENANT_ID,
    phone: generatePhone(),
    startedAt: new Date().toISOString(),
  };
}

function loadSession(): DemoSession {
  try {
    const raw = localStorage.getItem(SESSION_STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as DemoSession;
      if (parsed?.phone && parsed?.tenantId) return parsed;
    }
  } catch {
    /* ignore */
  }
  const session = createSession();
  localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
  return session;
}

export function useDemoSession() {
  const [session, setSession] = useState<DemoSession>(() => loadSession());

  const resetDemo = useCallback(() => {
    const next = createSession();
    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(next));
    setSession(next);
    return next;
  }, []);

  const useEnrolledStudent = useCallback(() => {
    const next: DemoSession = {
      tenantId: TENANT_ID,
      phone: ENROLLED_DEMO_PHONE,
      startedAt: new Date().toISOString(),
    };
    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(next));
    setSession(next);
    return next;
  }, []);

  return { session, resetDemo, useEnrolledStudent };
}
