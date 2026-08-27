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
  payments_enabled?: boolean;
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
  payments_enabled?: boolean;
}

export interface UpdateClassPayload {
  subject?: string;
  fee_amount?: number;
  fee_cycle?: string;
  name?: string;
  grade?: string;
  payments_enabled?: boolean;
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

/* ---------- Class Telegram broadcast (AI backend) ---------- */

export interface BroadcastRecipients {
  class_id: string;
  class_name: string;
  enrolled: number;
  reachable: number;
  skipped_no_telegram: number;
  reachable_names: string[];
}

export interface BroadcastFailure {
  student_id: string;
  name: string;
}

export interface BroadcastResult {
  class_id: string;
  sent: number;
  failed: number;
  skipped_no_telegram: number;
  failures: BroadcastFailure[];
}

export function getBroadcastRecipients(
  classId: string,
  tenantId?: string,
): Promise<BroadcastRecipients> {
  return aiRequest<BroadcastRecipients>(
    `/dashboard/classes/${encodeURIComponent(classId)}/broadcast-recipients`,
    {},
    tenantId,
  );
}

export function sendClassBroadcast(
  classId: string,
  message: string,
  tenantId?: string,
): Promise<BroadcastResult> {
  const tenant = tenantId ?? getTenantId();

  return aiRequest<BroadcastResult>(
    `/dashboard/classes/${encodeURIComponent(classId)}/broadcast`,
    {
      method: "POST",
      body: JSON.stringify({ tenant_id: tenant, message }),
    },
    tenant,
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
  school?: string | null;
  district: string | null;
  extra_fields?: Record<string, unknown>;
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
  school?: string;
  district?: string;
  extra_fields?: Record<string, unknown>;
  language_pref?: string;
  class_id?: string;
}

export interface UpdateStudentPayload {
  name?: string;
  phone?: string;
  school?: string;
  district?: string;
  extra_fields?: Record<string, unknown>;
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
  document_id?: string;
  document_title?: string;
  source_filename?: string;
  source_type?: string;
  page_count?: number | null;
  ocr_pages?: number;
  skipped?: boolean;
  chunks_deleted?: number;
  warnings?: string[];
  status?: string;
  async?: boolean;
  error?: string | null;
}

export interface IngestDocumentResult {
  ok: boolean;
  tenant_id: string;
  document: KbDocumentRecord;
}

export interface KbDocumentRecord {
  id: string;
  tenant_id: string;
  class_id: string;
  document_id: string;
  filename: string;
  title?: string | null;
  lesson?: string | null;
  source_type: string;
  byte_size: number;
  page_count?: number | null;
  ocr_pages?: number;
  chunks_upserted?: number | null;
  status: string;
  error?: string | null;
  warnings?: string[];
  created_at?: string | null;
  updated_at?: string | null;
}

export interface IngestDocumentListResult {
  ok: boolean;
  tenant_id: string;
  documents: KbDocumentRecord[];
}

/** Formats the ingest pipeline can extract. Keep in sync with the AI backend. */
export const INGEST_ACCEPT = ".pdf,.docx,.md,.markdown,.txt";

export const INGEST_MAX_MB: Record<string, number> = {
  pdf: 50,
  docx: 25,
  md: 5,
  markdown: 5,
  txt: 5,
};

/** Client-side size guard so oversized files fail instantly instead of after an upload. */
export function ingestSizeError(file: File): string | null {
  const extension = file.name.split(".").pop()?.toLowerCase() ?? "";
  const limitMb = INGEST_MAX_MB[extension];

  if (!limitMb) {
    return `Unsupported file type ".${extension}". Upload a PDF, Word (.docx) or Markdown file.`;
  }

  if (file.size > limitMb * 1024 * 1024) {
    return `${file.name} is ${Math.ceil(file.size / (1024 * 1024))} MB — the limit for .${extension} is ${limitMb} MB.`;
  }

  return null;
}

const INGEST_POLL_INTERVAL_MS = 2000;
const INGEST_POLL_TIMEOUT_MS = 10 * 60 * 1000;

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

export function getIngestDocument(
  documentId: string,
  tenantId?: string,
): Promise<IngestDocumentResult> {
  const tenant = tenantId ?? getTenantId();
  return aiRequest<IngestDocumentResult>(
    `/tools/ingest/documents/${encodeURIComponent(documentId)}?tenant_id=${encodeURIComponent(tenant)}`,
    {},
    tenant,
  );
}

export async function pollIngestDocument(
  documentId: string,
  tenantId?: string,
  onStatus?: (document: KbDocumentRecord) => void,
): Promise<KbDocumentRecord> {
  const tenant = tenantId ?? getTenantId();
  const deadline = Date.now() + INGEST_POLL_TIMEOUT_MS;

  while (Date.now() < deadline) {
    const { document } = await getIngestDocument(documentId, tenant);
    onStatus?.(document);

    if (document.status === "ready" || document.status === "failed") {
      return document;
    }

    await sleep(INGEST_POLL_INTERVAL_MS);
  }

  throw new Error("Document ingest timed out while waiting for completion.");
}

export async function uploadDocument(
  payload: {
    classId: string;
    file: File;
    title?: string;
    lesson?: string;
  },
  tenantId?: string,
  onStatus?: (document: KbDocumentRecord) => void,
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

  const initial = await aiRequest<IngestUploadResult>(
    "/tools/ingest/upload",
    {
      method: "POST",
      body: formData,
    },
    tenant,
  );

  if (initial.skipped || !initial.async || !initial.document_id) {
    return initial;
  }

  const document = await pollIngestDocument(initial.document_id, tenant, onStatus);

  if (document.status === "failed") {
    throw new Error(document.error ?? "Document ingest failed.");
  }

  return {
    ...initial,
    status: document.status,
    chunks_upserted: document.chunks_upserted ?? 0,
    document_title: document.title ?? initial.document_title,
    source_filename: document.filename ?? initial.source_filename,
    source_type: document.source_type,
    page_count: document.page_count,
    ocr_pages: document.ocr_pages,
    warnings: document.warnings ?? [],
    async: false,
  };
}

export function listIngestDocuments(
  tenantId?: string,
  classId?: string,
): Promise<IngestDocumentListResult> {
  const tenant = tenantId ?? getTenantId();
  const params = new URLSearchParams({ tenant_id: tenant });
  if (classId) {
    params.set("class_id", classId);
  }
  return aiRequest<IngestDocumentListResult>(
    `/tools/ingest/documents?${params.toString()}`,
    {},
    tenant,
  );
}

export function deleteIngestDocument(
  documentId: string,
  tenantId?: string,
): Promise<{ ok: boolean; chunks_deleted: number }> {
  const tenant = tenantId ?? getTenantId();
  return aiRequest(
    `/tools/ingest/documents/${encodeURIComponent(documentId)}?tenant_id=${tenant}`,
    { method: "DELETE" },
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

export function queryDashboardAgent(
  message: string,
  tenantId?: string,
): Promise<{ reply: string; staff_id: string; tenant_id: string }> {
  return aiRequest(
    "/dashboard/agent/query",
    {
      method: "POST",
      body: JSON.stringify({ message }),
    },
    tenantId,
  );
}

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

export interface OnboardingFieldDefinition {
  field_key: string;
  label: string;
  field_type: string;
  options?: string[] | null;
  required: boolean;
  sort_order: number;
  active?: boolean;
}

export interface OnboardingFieldsResponse {
  locked: boolean;
  fields: OnboardingFieldDefinition[];
}

export function getOnboardingFields(
  tenantId?: string,
): Promise<OnboardingFieldsResponse> {
  return dashboardRequest<OnboardingFieldsResponse>(
    "/tenant/onboarding-fields",
    {},
    tenantId,
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
  period: string;

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

export type AnalyticsPeriod =
  | "today"
  | "7d"
  | "month";

export function getDashboardAnalytics(
  tenantId?: string,
  period: AnalyticsPeriod = "7d",
): Promise<DashboardAnalytics> {
  return dashboardRequest<DashboardAnalytics>(
    `/dashboard/analytics?period=${period}`,
    {},
    tenantId,
  );
}

/* Class Documents */

export type ClassDocumentUploadResponse = IngestUploadResult;

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
  period: string;
  attribution_mode: string;
  classes: ClassAnalyticsMetric[];
}

export function getClassAnalytics(
  tenantId?: string,
  period: AnalyticsPeriod = "7d",
): Promise<ClassAnalyticsComparison> {
  return dashboardRequest<
    ClassAnalyticsComparison
  >(
    `/dashboard/analytics/classes?period=${period}`,
    {},
    tenantId,
  );
}

export function updateClassHumanMode(
  classId: string,
  humanMode: boolean,
  tenantId?: string,
): Promise<{
  ok: boolean;
  class_id: string;
  human_mode: boolean;
  students_updated: number;
}> {
  return dashboardRequest(
    `/classes/${classId}/human-mode`,
    {
      method: "PATCH",
      body: JSON.stringify({
        human_mode: humanMode,
      }),
    },
    tenantId,
  );
}

export function updateClassPaymentsEnabled(
  classId: string,
  paymentsEnabled: boolean,
  tenantId?: string,
): Promise<SubjectClass> {
  return dashboardRequest<SubjectClass>(
    `/classes/${classId}/payments-enabled`,
    {
      method: "PATCH",
      body: JSON.stringify({
        payments_enabled: paymentsEnabled,
      }),
    },
    tenantId,
  );
}

export interface StudentImportResult {
  created: number;
  skipped: number;
  errors: Array<{
    row: number;
    reason: string;
  }>;
}

export function importStudentsExcel(
  file: File,
  tenantId?: string,
): Promise<StudentImportResult> {
  const formData = new FormData();
  formData.append("file", file);

  return dashboardRequest<StudentImportResult>(
    "/students/import",
    {
      method: "POST",
      body: formData,
    },
    tenantId,
  );
}

export type StaffRoleValue =
  | "admin"
  | "tutor"
  | "marker"
  | "viewer";

export interface StaffMember {
  id: string;
  tenant_id: string;
  name: string;
  email: string;
  role: StaffRoleValue;
  is_active: boolean;
}

export interface StaffCreatePayload {
  name: string;
  email: string;
  password: string;
  role: StaffRoleValue;
}

export interface StaffUpdatePayload {
  name?: string;
  role?: StaffRoleValue;
  is_active?: boolean;
}

export function getStaff(
  tenantId?: string,
): Promise<StaffMember[]> {
  return dashboardRequest<StaffMember[]>(
    "/staff",
    {},
    tenantId,
  );
}

export function createStaff(
  payload: StaffCreatePayload,
  tenantId?: string,
): Promise<StaffMember> {
  return dashboardRequest<StaffMember>(
    "/staff",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    tenantId,
  );
}

export function updateStaff(
  staffId: string,
  payload: StaffUpdatePayload,
  tenantId?: string,
): Promise<StaffMember> {
  return dashboardRequest<StaffMember>(
    `/staff/${staffId}`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    },
    tenantId,
  );
}

export interface FaqCluster {
  question: string;
  category: string;
  frequency: number;
  examples: string[];
  suggested_answer: string;
}

export interface FaqAnalysisResult {
  tenant_id: string;
  class_id?: string | null;
  analyzed_messages: number;
  clusters: FaqCluster[];
}

export function analyzeFaqs(
  classId: string,
  tenantId?: string,
  limit = 200,
  minimumFrequency = 2,
): Promise<FaqAnalysisResult> {
  return aiRequest<FaqAnalysisResult>(
    `/dashboard/faqs/analyze?class_id=${encodeURIComponent(classId)}&limit=${limit}&minimum_frequency=${minimumFrequency}`,
    { method: "POST" },
    tenantId,
  );
}

export function uploadClassDocument(
  classId: string,
  tenantId: string,
  file: File,
  title?: string,
  lesson?: string,
): Promise<ClassDocumentUploadResponse> {
  return uploadDocument({ classId, file, title, lesson }, tenantId);
}

/* ---------- Schedules (AI backend — /dashboard/schedules) ---------- */

export interface Schedule {
  id: string;
  tenant_id: string;
  class_id: string;
  teacher_id?: string | null;
  day_of_week: string;
  start_time: string;
  end_time: string;
  room?: string | null;
  status: string;
  effective_from: string;
  effective_until?: string | null;
  created_at: string;
  updated_at: string;
  class_name?: string | null;
  subject?: string | null;
  teacher_name?: string | null;
}

export interface CreateSchedulePayload {
  class_id: string;
  teacher_id?: string;
  day_of_week: string;
  start_time: string;
  end_time: string;
  room?: string;
  effective_from?: string;
  effective_until?: string;
}

export interface UpdateSchedulePayload {
  teacher_id?: string;
  day_of_week?: string;
  start_time?: string;
  end_time?: string;
  room?: string;
  effective_from?: string;
  effective_until?: string;
  status?: string;
}

export interface ScheduleException {
  id: string;
  tenant_id: string;
  schedule_id: string;
  exception_date: string;
  status: string;
  new_start_time?: string | null;
  new_end_time?: string | null;
  new_room?: string | null;
  new_date?: string | null;
  notes?: string | null;
  created_at: string;
}

interface ScheduleListResponse {
  ok?: boolean;
  tenant_id: string;
  schedules: Schedule[];
}

interface ScheduleDetailResponse {
  ok?: boolean;
  tenant_id: string;
  schedule: Schedule;
}

interface ExceptionListResponse {
  ok?: boolean;
  tenant_id: string;
  exceptions: ScheduleException[];
}

function asScheduleList(
  response: ScheduleListResponse | Schedule[],
): Schedule[] {
  return Array.isArray(response) ? response : (response.schedules ?? []);
}

function asSchedule(response: ScheduleDetailResponse | Schedule): Schedule {
  if (response && typeof response === "object" && "schedule" in response) {
    return response.schedule;
  }
  return response;
}

export function getSchedules(
  tenantId?: string,
  params?: { class_id?: string; teacher_id?: string; day_of_week?: string },
): Promise<Schedule[]> {
  const query = new URLSearchParams();
  if (params?.class_id) query.set("class_id", params.class_id);
  if (params?.teacher_id) query.set("teacher_id", params.teacher_id);
  if (params?.day_of_week) query.set("day_of_week", params.day_of_week);
  const qs = query.toString();
  return aiRequest<ScheduleListResponse | Schedule[]>(
    `/dashboard/schedules${qs ? `?${qs}` : ""}`,
    {},
    tenantId,
  ).then(asScheduleList);
}

export function getSchedule(
  scheduleId: string,
  tenantId?: string,
): Promise<Schedule> {
  return aiRequest<ScheduleDetailResponse | Schedule>(
    `/dashboard/schedules/${scheduleId}`,
    {},
    tenantId,
  ).then(asSchedule);
}

export function createSchedule(
  payload: CreateSchedulePayload,
  tenantId?: string,
): Promise<Schedule> {
  return aiRequest<ScheduleDetailResponse | Schedule>(
    "/dashboard/schedules",
    { method: "POST", body: JSON.stringify(payload) },
    tenantId,
  ).then(asSchedule);
}

export function updateSchedule(
  scheduleId: string,
  payload: UpdateSchedulePayload,
  tenantId?: string,
): Promise<Schedule> {
  return aiRequest<ScheduleDetailResponse | Schedule>(
    `/dashboard/schedules/${scheduleId}`,
    { method: "PATCH", body: JSON.stringify(payload) },
    tenantId,
  ).then(asSchedule);
}

export function deleteSchedule(
  scheduleId: string,
  tenantId?: string,
): Promise<void> {
  return aiRequest<void>(
    `/dashboard/schedules/${scheduleId}`,
    { method: "DELETE" },
    tenantId,
  );
}

export function getScheduleExceptions(
  scheduleId: string,
  tenantId?: string,
): Promise<ScheduleException[]> {
  return aiRequest<ExceptionListResponse | ScheduleException[]>(
    `/dashboard/schedules/${scheduleId}/exceptions`,
    {},
    tenantId,
  ).then((response) =>
    Array.isArray(response) ? response : (response.exceptions ?? []),
  );
}

export function createScheduleException(
  scheduleId: string,
  payload: {
    exception_date: string;
    status?: string;
    new_start_time?: string;
    new_end_time?: string;
    notes?: string;
  },
  tenantId?: string,
): Promise<ScheduleException> {
  return aiRequest<ScheduleException>(
    `/dashboard/schedules/${scheduleId}/exceptions`,
    { method: "POST", body: JSON.stringify(payload) },
    tenantId,
  );
}

export function deleteScheduleException(
  scheduleId: string,
  exceptionId: string,
  tenantId?: string,
): Promise<void> {
  return aiRequest<void>(
    `/dashboard/schedules/${scheduleId}/exceptions/${exceptionId}`,
    { method: "DELETE" },
    tenantId,
  );
}


