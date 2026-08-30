import { ApiError } from "./api";

/**
 * Turns any thrown value into text that is safe to show a tutor.
 *
 * Raw error text is never returned: backend `detail` strings are only passed
 * through when they read as a short, human-written sentence, and everything
 * else falls back to the caller's copy. Full errors stay in the console.
 */

const MAX_DETAIL_LENGTH = 160;

const STATUS_MESSAGES: Record<number, string> = {
  400: "That request wasn't valid. Please check the details and try again.",
  401: "Your session has expired. Please sign in again.",
  403: "You don't have permission to do that.",
  404: "We couldn't find that item. It may have been removed.",
  409: "That conflicts with existing data. Refresh and try again.",
  413: "That file is too large to upload.",
  422: "Some details were missing or invalid. Please review and try again.",
  429: "Too many requests. Please wait a moment and try again.",
};

const TECHNICAL_PATTERNS: RegExp[] = [
  /traceback/i,
  /\bexception\b/i,
  /\bstack\b/i,
  /^request failed/i,
  /failed to fetch/i,
  /network\s?error/i,
  /\.(ts|tsx|js|jsx|py):\d+/i,
  /https?:\/\//i,
  /127\.0\.0\.1|localhost/i,
  /:\d{4}\b/,
  /<[^>]+>/,
  /\{|\}|\[object\s/,
  /sqlalchemy|psycopg|asyncpg|supabase|qdrant|uvicorn|fastapi|pydantic|langchain|httpx/i,
];

function isPresentable(text: string): boolean {
  const trimmed = text.trim();

  if (trimmed.length < 4 || trimmed.length > MAX_DETAIL_LENGTH) {
    return false;
  }

  if (trimmed.includes("\n")) {
    return false;
  }

  return !TECHNICAL_PATTERNS.some((pattern) => pattern.test(trimmed));
}

export function safeDetail(details: unknown): string | null {
  if (typeof details === "string") {
    return isPresentable(details) ? details.trim() : null;
  }

  if (typeof details !== "object" || details === null) {
    return null;
  }

  const detail = (details as { detail?: unknown }).detail;

  // FastAPI validation errors arrive as an array of objects — never presentable.
  if (typeof detail === "string" && isPresentable(detail)) {
    return detail.trim();
  }

  return null;
}

export function userMessage(error: unknown, fallback: string): string {
  if (!(error instanceof ApiError)) {
    return fallback;
  }

  const detail = safeDetail(error.details);

  if (detail) {
    return detail;
  }

  if (error.status >= 500) {
    return "Something went wrong on our end. Please try again in a moment.";
  }

  return STATUS_MESSAGES[error.status] ?? fallback;
}
