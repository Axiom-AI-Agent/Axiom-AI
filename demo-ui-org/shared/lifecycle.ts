/** Client-side lifecycle checklist — heuristic ticks only (no backend state). */

export type LifecycleStepId =
  | "intent"
  | "profile"
  | "class"
  | "consent"
  | "payment"
  | "enrolled"
  | "resource"
  | "escalation";

export interface LifecycleStep {
  id: LifecycleStepId;
  label: string;
  hint: string;
}

export const LIFECYCLE_STEPS: LifecycleStep[] = [
  { id: "intent", label: "Intent", hint: "Ask to join A/L Physics" },
  { id: "profile", label: "Profile", hint: "Name, school, district" },
  { id: "class", label: "Class", hint: "Confirm A/L Physics" },
  { id: "consent", label: "Consent", hint: "Reply YES" },
  { id: "payment", label: "Payment sent", hint: "Attach sample slip" },
  { id: "enrolled", label: "Enrolled", hint: "Bot confirms after payment review" },
  { id: "resource", label: "Resource", hint: "Ask about velocity notes" },
  { id: "escalation", label: "Escalation", hint: "Ask to speak to sir" },
];

export type LifecycleState = Record<LifecycleStepId, boolean>;

export function emptyLifecycle(): LifecycleState {
  return {
    intent: false,
    profile: false,
    class: false,
    consent: false,
    payment: false,
    enrolled: false,
    resource: false,
    escalation: false,
  };
}

function includesAny(text: string, needles: string[]): boolean {
  const lower = text.toLowerCase();
  return needles.some((n) => lower.includes(n));
}

/** Merge heuristic detections from the latest student/bot turn (client-side only). */
export function detectLifecycleProgress(
  prev: LifecycleState,
  opts: {
    studentText?: string;
    botText?: string;
    sentMedia?: boolean;
  },
): LifecycleState {
  const next = { ...prev };
  const student = opts.studentText ?? "";
  const bot = opts.botText ?? "";

  if (includesAny(student, ["join", "enroll", "admission", "sign up", "a/l physics"])) {
    next.intent = true;
  }
  if (
    includesAny(student, ["my name", "i am ", "i'm ", "school", "college", "district", "colombo"]) ||
    includesAny(bot, ["school", "district", "which class", "your name"])
  ) {
    if (next.intent) next.profile = true;
  }
  if (
    includesAny(student, ["a/l physics", "al physics", "physics class"]) ||
    includesAny(bot, ["selected", "confirm", "class", "payment"])
  ) {
    if (next.profile) next.class = true;
  }
  if (
    student.trim().toUpperCase() === "YES" ||
    includesAny(bot, ["pending", "payment", "bank", "transfer", "slip", "consent"])
  ) {
    if (next.class || next.profile) next.consent = true;
  }
  if (opts.sentMedia || includesAny(bot, ["receipt", "verif", "payment", "review"])) {
    if (opts.sentMedia) next.payment = true;
  }
  if (includesAny(bot, ["enrolled", "welcome", "activated", "you are in", "approved"])) {
    next.enrolled = true;
  }
  if (
    includesAny(student, ["velocity", "notes", "tutor notes", "explain"]) ||
    includesAny(bot, ["velocity", "speed", "displacement", "from the notes"])
  ) {
    next.resource = true;
  }
  if (
    includesAny(student, ["speak to", "talk to", "sir", "tutor", "teacher"]) ||
    includesAny(bot, ["escalat", "tutor", "notified", "staff"])
  ) {
    next.escalation = true;
  }

  return next;
}
