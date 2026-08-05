// src/lib/api.ts
/**
 * Dashboard API client placeholder.
 * This file provides TypeScript functions that represent the real backend endpoints
 * defined in the Phase 5 API contract. For now, each function returns mock data via
 * resolved promises. The UI components can import these functions and later switch
 * to real network calls without changing component logic.
 */

export type TenantId = string;

export interface Escalation {
  id: string;
  tenant_id: TenantId;
  student_id: string;
  student_name: string;
  student_phone: string;
  enrollment_id: string;
  reason_code: 'payment_receipt' | 'talk_to_tutor';
  status: 'open' | 'assigned' | 'resolved';
  media_url: string | null;
  student_message: string;
  resolution: string | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface OverviewStats {
  tenant_id: TenantId;
  open_escalations: number;
  open_payment_receipts: number;
  open_talk_to_tutor: number;
  pending_enrollments: number;
  students: number;
  classes: number;
}

export interface ChatTurn {
  id: string;
  role: 'user' | 'assistant' | 'staff';
  content: string;
  created_at: string;
}

export interface ChatLog {
  tenant_id: TenantId;
  session_id: string;
  turns: ChatTurn[];
}

// Helper to simulate network latency for the demo UI.
const fakeDelay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * GET /dashboard/escalations
 */
export async function getEscalations(
  tenantId: TenantId,
  params?: { status?: string; reason_code?: string }
): Promise<Escalation[]> {
  await fakeDelay(300);
  // Mock data – in a real implementation this would `fetch` the endpoint.
  return [
    {
      id: 'esc-001',
      tenant_id: tenantId,
      student_id: 'stu-001',
      student_name: 'Amaya Perera',
      student_phone: '94771234567',
      enrollment_id: 'enr-001',
      reason_code: 'payment_receipt',
      status: 'open',
      media_url: null,
      student_message: 'Here is my payment receipt.',
      resolution: null,
      reviewed_by: null,
      reviewed_at: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'esc-002',
      tenant_id: tenantId,
      student_id: 'stu-002',
      student_name: 'Nadeesha Silva',
      student_phone: '94773332211',
      enrollment_id: '',
      reason_code: 'talk_to_tutor',
      status: 'open',
      media_url: null,
      student_message: 'Can I speak to a tutor?',
      resolution: null,
      reviewed_by: null,
      reviewed_at: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ];
}

/**
 * PATCH /dashboard/escalations/{id}/resolve
 */
export async function resolveEscalation(
  tenantId: TenantId,
  escalationId: string,
  options?: { notify?: boolean; reviewed_by?: string }
): Promise<{ ok: true; escalation_id: string; reason_code: string; resolution: string }> {
  await fakeDelay(200);
  // Return a static success shape.
  return {
    ok: true,
    escalation_id: escalationId,
    reason_code: 'payment_receipt',
    resolution: 'approved',
  };
}

/**
 * PATCH /dashboard/escalations/{id}/reject
 */
export async function rejectEscalation(
  tenantId: TenantId,
  escalationId: string,
  options?: { notify?: boolean; reviewed_by?: string }
): Promise<{ ok: true; escalation_id: string; reason_code: string; resolution: string }> {
  await fakeDelay(200);
  return {
    ok: true,
    escalation_id: escalationId,
    reason_code: 'payment_receipt',
    resolution: 'rejected',
  };
}

/**
 * GET /dashboard/overview
 */
export async function getOverviewStats(tenantId: TenantId): Promise<OverviewStats> {
  await fakeDelay(250);
  return {
    tenant_id: tenantId,
    open_escalations: 2,
    open_payment_receipts: 1,
    open_talk_to_tutor: 1,
    pending_enrollments: 1,
    students: 42,
    classes: 3,
  };
}

/**
 * GET /dashboard/chat-logs
 */
export async function getChatLogs(
  tenantId: TenantId,
  phone?: string
): Promise<ChatLog[]> {
  await fakeDelay(300);
  return [
    {
      tenant_id: tenantId,
      session_id: `${tenantId}:94771234567`,
      turns: [
        { id: 't1', role: 'user', content: 'Hello', created_at: new Date().toISOString() },
        { id: 't2', role: 'assistant', content: 'Hi! How can I help?', created_at: new Date().toISOString() },
      ],
    },
  ];
}

/**
 * POST /dashboard/chat/send
 */
export async function sendChatMessage(
  tenantId: TenantId,
  phone: string,
  message: string
): Promise<{ ok: true }> {
  await fakeDelay(200);
  console.log('Mock sendChatMessage', { tenantId, phone, message });
  return { ok: true };
}
