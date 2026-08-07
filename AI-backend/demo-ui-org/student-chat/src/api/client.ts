/**
 * Thin fetch wrapper for Axiom FastAPI (adapted from BookMe AI frontend/src/api/client.ts).
 * No Clerk, no SSE — POST /chat + GET /chat/turns only.
 */

import type {
  ChatRequest,
  ChatResponse,
  ChatTurnsResponse,
  HealthResponse,
} from "@/types";

function resolveApiBase(): string {
  const url = import.meta.env.VITE_API_URL?.trim();
  if (!url) {
    throw new Error("VITE_API_URL is not set — add it to student-chat/.env");
  }
  return url.replace(/\/$/, "");
}

const BASE = resolveApiBase();

export class ApiError extends Error {
  constructor(
    public status: number,
    public body: unknown,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  init: RequestInit & { json?: unknown } = {},
): Promise<T> {
  const { json, headers, ...rest } = init;
  const res = await fetch(`${BASE}${path}`, {
    ...rest,
    headers: {
      "content-type": "application/json",
      ...(headers || {}),
    },
    body: json !== undefined ? JSON.stringify(json) : rest.body,
  });

  if (!res.ok) {
    let body: unknown = null;
    try {
      body = await res.json();
    } catch {
      /* ignore */
    }
    const detail = body as { detail?: string | { msg?: string }[] };
    let msg = res.statusText || "Request failed";
    if (typeof detail?.detail === "string") msg = detail.detail;
    else if (Array.isArray(detail?.detail) && detail.detail[0]?.msg) {
      msg = detail.detail[0].msg;
    }
    if (res.status === 503) {
      msg = `Backend unavailable (503). Check VITE_API_URL (${BASE}).`;
    }
    throw new ApiError(res.status, body, msg);
  }

  const text = await res.text();
  return (text ? JSON.parse(text) : null) as T;
}

export const chatApi = {
  send: (req: ChatRequest) =>
    request<ChatResponse>("/chat", { method: "POST", json: req }),

  turns: (tenantId: string, phone: string) =>
    request<ChatTurnsResponse>(
      `/chat/turns?tenant_id=${encodeURIComponent(tenantId)}&phone=${encodeURIComponent(phone)}`,
    ),
};

export const systemApi = {
  health: () => request<HealthResponse>("/health"),
};

export { BASE as API_BASE };
