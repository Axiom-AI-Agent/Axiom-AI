/** TypeScript mirror of Axiom `src/api/schemas.py` chat types. */

export type MessageSender = "student" | "bot" | "staff";

export interface ChatRequest {
  tenant_id: string;
  phone: string;
  message: string;
  media_url?: string | null;
}

export interface ChatResponse {
  reply: string;
  tenant_id: string;
  tenant_slug?: string | null;
  tenant_name?: string | null;
  student_id: string;
  phone: string;
  session_id: string;
  student_exists: boolean;
}

export interface ChatTurnRecord {
  id: string;
  role: "user" | "assistant" | "system";
  sender: MessageSender;
  content: string;
  created_at: string;
}

export interface ChatTurnsResponse {
  tenant_id: string;
  session_id: string;
  turns: ChatTurnRecord[];
}

export interface HealthResponse {
  status: string;
  [key: string]: unknown;
}

export interface UIMessage {
  id: string;
  sender: MessageSender;
  content: string;
  createdAt: string;
  mediaUrl?: string | null;
  pending?: boolean;
  error?: boolean;
}

export interface DemoSession {
  tenantId: string;
  phone: string;
  startedAt: string;
}
