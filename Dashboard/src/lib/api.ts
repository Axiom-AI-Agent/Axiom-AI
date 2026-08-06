const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000";

export interface DashboardSummary {
  total_students: number;
  active_classes?: number;
  pending_payments: number;
  active_conversations?: number;
  open_escalations: number;
}

export interface SubjectClass {
  id: string;
  tenant_id: string;
  subject: string;
  fee_amount: string | number;
  fee_cycle: string;
  created_at: string;
}

export interface CreateClassPayload {
  tenant_id?: string;
  subject: string;
  fee_amount: number;
  fee_cycle: string;
}

export interface UpdateClassPayload {
  subject?: string;
  fee_amount?: number;
  fee_cycle?: string;
}

export interface Payment {
  id: string;
  tenant_id: string;
  student_id: string;
  student_name?: string | null;
  student_phone?: string | null;
  period: string;
  amount_due: string | number;
  status: string;
  receipt_url?: string | null;
  created_at: string;
}

export interface Student {
  id: string;
  tenant_id: string;
  name: string | null;
  phone: string;
  district: string | null;
  language_pref: string;
  created_at: string;
}

export type EscalationStatus = "open" | "assigned" | "resolved";

export interface Escalation {
  id: string;
  tenant_id: string;
  student_id: string;
  student_name?: string | null;
  student_phone?: string | null;
  reason_code: string;
  status: EscalationStatus;
  student_message?: string | null;
  media_url?: string | null;
  created_at: string;
  updated_at: string;
}

export interface MessageLog {
  id: string;
  tenant_id: string;
  student_id: string;
  student_name?: string | null;
  channel: string;
  intent: string | null;
  timestamp: string;
}

export class ApiError extends Error {
  status: number;
  details: unknown;

  constructor(message: string, status: number, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    let details: unknown;

    try {
      details = await response.json();
    } catch {
      details = await response.text();
    }

    throw new ApiError(
      `Request failed: ${response.status} ${response.statusText}`,
      response.status,
      details,
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

/* Dashboard */

export function getDashboardSummary(): Promise<DashboardSummary> {
  return apiRequest<DashboardSummary>("/dashboard/summary");
}

/* Classes */

export function getClasses(): Promise<SubjectClass[]> {
  return apiRequest<SubjectClass[]>("/classes");
}

export function createClass(
  payload: CreateClassPayload,
): Promise<SubjectClass> {
  return apiRequest<SubjectClass>("/classes", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateClass(
  classId: string,
  payload: UpdateClassPayload,
): Promise<SubjectClass> {
  return apiRequest<SubjectClass>(`/classes/${classId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

/* Payments */

export function getPendingPayments(): Promise<Payment[]> {
  return apiRequest<Payment[]>("/payments/pending");
}

export function getAllPayments(): Promise<Payment[]> {
  return apiRequest<Payment[]>("/dashboard/payments");
}

export function approvePayment(paymentId: string): Promise<Payment> {
  return apiRequest<Payment>(`/payments/${paymentId}/approve`, {
    method: "PUT",
  });
}

export function rejectPayment(paymentId: string): Promise<Payment> {
  return apiRequest<Payment>(`/payments/${paymentId}/reject`, {
    method: "PUT",
  });
}

/* Students */

export function getStudents(): Promise<Student[]> {
  return apiRequest<Student[]>("/students");
}

/* Escalations */

export function getEscalations(): Promise<Escalation[]> {
  return apiRequest<Escalation[]>("/escalations");
}

export function getOpenEscalations(): Promise<Escalation[]> {
  return apiRequest<Escalation[]>("/escalations/open");
}

export function assignEscalation(
  escalationId: string,
): Promise<Escalation> {
  return apiRequest<Escalation>(
    `/escalations/${escalationId}/assign`,
    {
      method: "PUT",
    },
  );
}

export function resolveEscalation(
  escalationId: string,
): Promise<Escalation> {
  return apiRequest<Escalation>(
    `/escalations/${escalationId}/resolve`,
    {
      method: "PUT",
    },
  );
}

/* Logs */

export function getMessageLogs(): Promise<MessageLog[]> {
  return apiRequest<MessageLog[]>("/message-logs");
}
