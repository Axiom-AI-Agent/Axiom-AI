import { getTenantId } from "./tenant";
import {
  clearAuthSession,
  getAccessToken,
} from "./auth";

const DASHBOARD_API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8001";

const AI_API_URL =
  process.env.NEXT_PUBLIC_AI_API_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000";

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

async function request<T>(
  baseUrl: string,
  path: string,
  options: RequestInit = {},
  tenantId?: string,
): Promise<T> {
  const tenant = tenantId ?? getTenantId();
  const hasBody = options.body !== undefined && options.body !== null;
  const isFormData = hasBody && options.body instanceof FormData;

  const url = new URL(`${baseUrl}${path}`);

  if (!url.searchParams.has("tenant_id")) {
    url.searchParams.set("tenant_id", tenant);
  }

  const token =
    getAccessToken();

  const headers:
    Record<string, string> = {
      "X-Tenant-ID": tenant,
    };

  if (token) {
    headers.Authorization =
      `Bearer ${token}`;
  }

  if (hasBody && !isFormData) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(url.toString(), {
    ...options,
    cache: "no-store",
    headers: {
      ...headers,
      ...(options.headers as Record<string, string> | undefined),
    },
  });
    if (
    response.status === 401
  ) {
    clearAuthSession();

    if (
      typeof window
      !== "undefined"
    ) {
      window.location.href =
        "/login";
    }
  }

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

function dashboardRequest<T>(
  path: string,
  options: RequestInit = {},
  tenantId?: string,
) {
  return request<T>(DASHBOARD_API_URL, path, options, tenantId);
}

function aiRequest<T>(
  path: string,
  options: RequestInit = {},
  tenantId?: string,
) {
  return request<T>(AI_API_URL, path, options, tenantId);
}

function withQuery(
  path: string,
  params: Record<string, string | boolean | undefined>,
): string {
  const search = new URLSearchParams();

  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") {
      search.set(key, String(value));
    }
  }

  const query = search.toString();
  return query ? `${path}?${query}` : path;
}

/* ---------- Overview (Dashboard backend) ---------- */

export interface DashboardOverview {
  tenant_id: string;
  open_escalations: number;
  open_payment_receipts: number;
  open_talk_to_tutor: number;
  pending_enrollments: number;
  students: number;
  classes: number;
}

export function getDashboardOverview(
  tenantId?: string,
): Promise<DashboardOverview> {
  return dashboardRequest<DashboardOverview>(
    "/dashboard/overview",
    {},
    tenantId,
  );
}

export function getDashboardSummary(tenantId?: string) {
  return getDashboardOverview(tenantId).then((overview) => ({
    total_students: overview.students,
    active_classes: overview.classes,
    pending_payments: overview.open_payment_receipts,
    active_conversations: 0,
    open_escalations: overview.open_escalations,
  }));
}

/* ---------- Classes (Dashboard backend) ---------- */

export interface SubjectClass {
  id: string;
  tenant_id?: string;
  subject: string;
  name?: string | null;
  grade?: string | null;
  fee_amount?: string | number;
  fee_cycle?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CreateClassPayload {
  tenant_id?: string;
  subject: string;
  fee_amount: number;
  fee_cycle: string;
  name?: string;
  grade?: string;
}

export interface UpdateClassPayload {
  subject?: string;
  fee_amount?: number;
  fee_cycle?: string;
  name?: string;
  grade?: string;
}

export function getClasses(tenantId?: string): Promise<SubjectClass[]> {
  return dashboardRequest<SubjectClass[]>("/classes", {}, tenantId);
}

export function createClass(
  payload: CreateClassPayload,
  tenantId?: string,
): Promise<SubjectClass> {
  const tenant = tenantId ?? getTenantId();

  return dashboardRequest<SubjectClass>(
    "/classes",
    {
      method: "POST",
      body: JSON.stringify({ ...payload, tenant_id: tenant }),
    },
    tenant,
  );
}

export function updateClass(
  classId: string,
  payload: UpdateClassPayload,
  tenantId?: string,
): Promise<SubjectClass> {
  return dashboardRequest<SubjectClass>(
    `/classes/${classId}`,
    {
      method: "PUT",
      body: JSON.stringify(payload),
    },
    tenantId,
  );
}

export function deleteClass(classId: string, tenantId?: string): Promise<void> {
  return dashboardRequest<void>(
    `/classes/${classId}`,
    { method: "DELETE" },
    tenantId,
  );
}

/* ---------- Escalations / Inbox (Dashboard backend) ---------- */

export type EscalationStatus = "open" | "assigned" | "resolved";

export interface Escalation {
  id: string;
  tenant_id: string;
  student_id: string;
  student_name?: string | null;
  student_phone?: string | null;
  enrollment_id?: string | null;
  reason_code: string;
  status: EscalationStatus;
  student_message?: string | null;
  media_url?: string | null;
  resolution?: string | null;
  reviewed_by?: string | null;
  reviewed_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface EscalationActionResult {
  ok: boolean;
  escalation_id: string;
  reason_code: string;
  resolution?: string | null;
  enrollment_status?: string | null;
  student_notified: boolean;
  notification_message?: string | null;
}

export function getEscalations(
  filters?: {
    status?: EscalationStatus;
    reason_code?: string;
  },
  tenantId?: string,
): Promise<Escalation[]> {
  const path = withQuery("/dashboard/escalations", {
    status: filters?.status,
    reason_code: filters?.reason_code,
  });

  return dashboardRequest<{ escalations: Escalation[] }>(path, {}, tenantId).then(
    (response) => response.escalations,
  );
}

export function getOpenEscalations(tenantId?: string) {
  return getEscalations({ status: "open" }, tenantId);
}

export function resolveEscalation(
  escalationId: string,
  options?: { notify?: boolean; reviewedBy?: string },
  tenantId?: string,
): Promise<EscalationActionResult> {
  const path = withQuery(`/dashboard/escalations/${escalationId}/resolve`, {
    reviewed_by: options?.reviewedBy ?? "staff@demo.com",
  });

  return dashboardRequest<EscalationActionResult>(
    path,
    { method: "PATCH" },
    tenantId,
  );
}

export function rejectEscalation(
  escalationId: string,
  options?: { notify?: boolean; reviewedBy?: string },
  tenantId?: string,
): Promise<EscalationActionResult> {
  const path = withQuery(`/dashboard/escalations/${escalationId}/reject`, {
    reviewed_by: options?.reviewedBy ?? "staff@demo.com",
  });

  return dashboardRequest<EscalationActionResult>(
    path,
    { method: "PATCH" },
    tenantId,
  );
}

export async function assignEscalation(
  escalationId: string,
  tenantId?: string,
): Promise<Escalation> {
  return dashboardRequest<Escalation>(
    `/escalations/${escalationId}/assign`,
    { method: "PUT" },
    tenantId,
  );
}

/* ---------- Chat / Messages (AI backend only) ---------- */

export type ChatSender = "student" | "bot" | "staff";

export interface ChatTurn {
  id: string;
  role: string;
  sender: ChatSender;
  content: string;
  created_at: string;
}

export interface ChatConversation {
  session_id: string;
  student_id: string;
  student_name?: string | null;
  phone: string;
  last_message: string;
  last_message_at: string;
  last_sender: ChatSender;
  has_open_escalation: boolean;
  open_escalation_reason?: string | null;
}

export interface ChatThread {
  tenant_id: string;
  session_id: string;
  student_id: string;
  student_name?: string | null;
  phone: string;
  turns: ChatTurn[];
  open_escalations: Array<{
    id: string;
    reason_code: string;
    status: string;
    student_message?: string | null;
    media_url?: string | null;
    created_at: string;
  }>;
}

export function getChatConversations(
  options?: { limit?: number; openEscalationOnly?: boolean },
  tenantId?: string,
): Promise<ChatConversation[]> {
  const path = withQuery("/dashboard/chat/conversations", {
    limit: options?.limit !== undefined ? String(options.limit) : "50",
    open_escalation_only: options?.openEscalationOnly ? "true" : undefined,
  });

  return aiRequest<{ conversations: ChatConversation[] }>(
    path,
    {},
    tenantId,
  ).then((response) => response.conversations);
}

export function getChatThread(
  phone: string,
  options?: { limit?: number },
  tenantId?: string,
): Promise<ChatThread> {
  const path = withQuery(
    `/dashboard/chat/conversations/${encodeURIComponent(phone)}`,
    {
      limit: options?.limit !== undefined ? String(options.limit) : "100",
    },
  );

  return aiRequest<ChatThread>(path, {}, tenantId);
}

export function sendStaffMessage(
  payload: {
    phone: string;
    message: string;
    staffId?: string;
  },
  tenantId?: string,
): Promise<{
  ok: boolean;
  delivered: boolean;
  turn?: ChatTurn;
}> {
  const tenant = tenantId ?? getTenantId();

  return aiRequest(
    "/dashboard/chat/send",
    {
      method: "POST",
      body: JSON.stringify({
        tenant_id: tenant,
        phone: payload.phone,
        message: payload.message,
        staff_id: payload.staffId ?? "staff@demo.com",
      }),
    },
    tenant,
  );
}

/* ---------- Students (Dashboard backend) ---------- */

export interface EnrollmentSummary {
  id: string;
  class_id: string;
  class_subject?: string | null;
  class_name?: string | null;
  status: string;
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
  updated_at?: string;
  enrollments?: EnrollmentSummary[];
  human_mode?: boolean;
}

export interface StudentProfile {
  student: Student;
  enrollments: EnrollmentSummary[];
}

export function updateStudentHumanMode(
  studentId: string,
  humanMode: boolean,
  tenantId?: string,
): Promise<Student> {
  return dashboardRequest<Student>(
    `/students/${studentId}/human-mode`,
    {
      method: "PATCH",
      body: JSON.stringify({
        human_mode: humanMode,
      }),
    },
    tenantId,
  );
}
export interface CreateStudentPayload {
  tenant_id?: string;
  name?: string;
  phone: string;
  district?: string;
  language_pref?: string;
  class_id?: string;
}

export interface UpdateStudentPayload {
  name?: string;
  phone?: string;
  district?: string;
  language_pref?: string;
}

export function getStudents(tenantId?: string): Promise<Student[]> {
  return dashboardRequest<{ students: Student[] } | Student[]>(
    "/students",
    {},
    tenantId,
  ).then((response) =>
    Array.isArray(response) ? response : (response.students ?? []),
  );
}

export function getStudentByPhone(
  phone: string,
  tenantId?: string,
): Promise<StudentProfile> {
  return dashboardRequest<Student & { enrollments: EnrollmentSummary[] }>(
    `/students/by-phone/${encodeURIComponent(phone)}`,
    {},
    tenantId,
  ).then((student) => ({
    student,
    enrollments: student.enrollments ?? [],
  }));
}

export function createStudent(
  payload: CreateStudentPayload,
  tenantId?: string,
): Promise<Student> {
  const tenant = tenantId ?? getTenantId();

  return dashboardRequest<Student>(
    "/students",
    {
      method: "POST",
      body: JSON.stringify({ ...payload, tenant_id: tenant }),
    },
    tenant,
  );
}

export function updateStudent(
  studentId: string,
  payload: UpdateStudentPayload,
  tenantId?: string,
): Promise<Student> {
  return dashboardRequest<Student>(
    `/students/${studentId}`,
    {
      method: "PUT",
      body: JSON.stringify(payload),
    },
    tenantId,
  );
}

export function deleteStudent(
  studentId: string,
  tenantId?: string,
): Promise<void> {
  return dashboardRequest<void>(
    `/students/${studentId}`,
    { method: "DELETE" },
    tenantId,
  );
}

export function enrollStudent(
  studentId: string,
  classId: string,
  status: string = "pending",
  tenantId?: string,
): Promise<EnrollmentSummary> {
  return dashboardRequest<EnrollmentSummary>(
    `/students/${studentId}/enrollments`,
    {
      method: "POST",
      body: JSON.stringify({ class_id: classId, status }),
    },
    tenantId,
  );
}

/* ---------- Message logs (Dashboard backend) ---------- */

export interface MessageLog {
  id: string;
  tenant_id: string;
  student_id: string;
  student_name?: string | null;
  channel: string;
  intent: string | null;
  timestamp: string;
}

export function getMessageLogs(tenantId?: string): Promise<MessageLog[]> {
  return dashboardRequest<MessageLog[]>("/message-logs", {}, tenantId);
}

/* ---------- Document ingest (AI backend only) ---------- */

export interface IngestUploadResult {
  ok: boolean;
  tenant_id: string;
  strategy: string;
  documents: number;
  chunks_upserted: number;
  collection: string;
  points_count?: number;
  document_title?: string;
  source_filename?: string;
}

export function uploadDocument(
  payload: {
    classId: string;
    file: File;
    title?: string;
    lesson?: string;
  },
  tenantId?: string,
): Promise<IngestUploadResult> {
  const tenant = tenantId ?? getTenantId();
  const formData = new FormData();

  formData.append("tenant_id", tenant);
  formData.append("class_id", payload.classId);
  formData.append("file", payload.file);

  if (payload.title) {
    formData.append("title", payload.title);
  }

  if (payload.lesson) {
    formData.append("lesson", payload.lesson);
  }

  return aiRequest<IngestUploadResult>(
    "/tools/ingest/upload",
    {
      method: "POST",
      body: formData,
    },
    tenant,
  );
}

/* ---------- Legacy payment helpers ---------- */

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

export async function getPendingPayments(tenantId?: string): Promise<Payment[]> {
  const escalations = await getEscalations(
    { status: "open", reason_code: "payment_receipt" },
    tenantId,
  );

  return escalations.map((escalation) => ({
    id: escalation.id,
    tenant_id: escalation.tenant_id,
    student_id: escalation.student_id,
    student_name: escalation.student_name,
    student_phone: escalation.student_phone,
    period: escalation.reason_code,
    amount_due: 0,
    status: escalation.status,
    receipt_url: escalation.media_url,
    created_at: escalation.created_at,
  }));
}

export function approvePayment(paymentId: string, tenantId?: string) {
  return resolveEscalation(paymentId, undefined, tenantId);
}

export function rejectPayment(paymentId: string, tenantId?: string) {
  return rejectEscalation(paymentId, undefined, tenantId);
}

export function getAllPayments(tenantId?: string) {
  return getPendingPayments(tenantId);
}

export type DashboardSummary = {
  total_students: number;
  active_classes?: number;
  pending_payments: number;
  active_conversations?: number;
  open_escalations: number;
};

export const DASHBOARD_API_BASE = DASHBOARD_API_URL;
export const AI_API_BASE = AI_API_URL;

/* ---------- Tenant / Settings (Dashboard backend) ---------- */

export interface TenantSummary {
  id: string;
  name: string;
  slug: string;
  status: string;
}

export interface TenantProfile {
  id: string;
  name: string;
  slug: string;
  status: string;
  whatsapp_number?: string | null;
  drive_folder_id?: string | null;
  payments_enabled: boolean;
  created_at: string;
  updated_at?: string | null;
}

export interface UpdateTenantPayload {
  name: string;
  slug: string;
  whatsapp_number?: string | null;
  drive_folder_id?: string | null;
  status?: "active" | "suspended";
  payments_enabled?: boolean;
}

export function listTenants(): Promise<TenantSummary[]> {
  return dashboardRequest<{ tenants: TenantSummary[] }>("/tenants").then(
    (response) => response.tenants ?? [],
  );
}

export function getTenantProfile(tenantId?: string): Promise<TenantProfile> {
  return dashboardRequest<TenantProfile>("/tenant", {}, tenantId);
}

export function updateTenantProfile(
  payload: UpdateTenantPayload,
  tenantId?: string,
): Promise<TenantProfile> {
  return dashboardRequest<TenantProfile>(
    "/tenant",
    {
      method: "PUT",
      body: JSON.stringify(payload),
    },
    tenantId,
  );
}

export interface EscalationCategoryMetric {
  reason_code: string;
  count: number;
}

export interface StudentAnalyticsMetric {
  student_id: string;
  student_name?: string | null;
  messages: number;
  conversations: number;
  escalations: number;
}

export interface DashboardAnalytics {
  tenant_id: string;

  total_conversations: number;
  total_messages: number;

  deflected_conversations: number;
  deflection_rate: number;

  average_response_seconds: number;
  estimated_minutes_saved: number;

  total_escalations: number;
  open_escalations: number;
  resolved_escalations: number;

  escalation_categories:
    EscalationCategoryMetric[];

  students: StudentAnalyticsMetric[];
}

export function getDashboardAnalytics(
  tenantId?: string,
): Promise<DashboardAnalytics> {
  return dashboardRequest<DashboardAnalytics>(
    "/dashboard/analytics",
    {},
    tenantId,
  );
}

/* Class Documents */

export interface ClassDocumentUploadResponse {
  ok: boolean;
  tenant_id: string;
  strategy: string;
  documents: number;
  chunks_upserted: number;
  collection: string;
  points_count: number | null;
  document_title: string | null;
  source_filename: string | null;
}
export interface ClassAnalyticsMetric {
  class_id: string;
  class_name?: string | null;
  subject: string;
  grade?: string | null;

  enrolled_students: number;
  active_students: number;
  pending_students: number;

  total_messages: number;
  total_conversations: number;

  deflected_conversations: number;
  deflection_rate: number;

  average_response_seconds: number;
  estimated_minutes_saved: number;

  total_escalations: number;
  open_escalations: number;
  resolved_escalations: number;
}

export interface ClassAnalyticsComparison {
  tenant_id: string;
  attribution_mode: string;
  classes: ClassAnalyticsMetric[];
}

export function getClassAnalytics(
  tenantId?: string,
): Promise<ClassAnalyticsComparison> {
  return dashboardRequest<
    ClassAnalyticsComparison
  >(
    "/dashboard/analytics/classes",
    {},
    tenantId,
  );
}

export async function uploadClassDocument(
  classId: string,
  tenantId: string,
  file: File,
  title?: string,
  lesson?: string,
): Promise<ClassDocumentUploadResponse> {
  const formData = new FormData();
  formData.append("tenant_id", tenantId);
  formData.append("class_id", classId);
  formData.append("file", file);

  if (title) {
    formData.append("title", title);
  }

  if (lesson) {
    formData.append("lesson", lesson);
  }

  const response = await fetch(
    `${AI_API_URL}/tools/ingest/upload`,
    {
      method: "POST",
      body: formData,
      cache: "no-store",
    },
  );

  if (!response.ok) {
    let details: unknown;

    try {
      details = await response.json();
    } catch {
      details = await response.text();
    }

    throw new ApiError(
      `Upload failed: ${response.status} ${response.statusText}`,
      response.status,
      details,
    );
  }

  return response.json() as Promise<ClassDocumentUploadResponse>;
}


