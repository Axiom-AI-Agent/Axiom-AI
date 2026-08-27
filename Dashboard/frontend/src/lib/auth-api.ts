import {
  clearAuthSession,
  getAccessToken,
} from "@/lib/auth";

import type {
  AuthResponse,
  AuthUser,
  LoginPayload,
  RegisterOrganizationPayload,
} from "@/types/auth";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8001";

export class AuthApiError extends Error {
  status: number;
  details?: unknown;

  constructor(
    message: string,
    status: number,
    details?: unknown,
  ) {
    super(message);

    this.name = "AuthApiError";
    this.status = status;
    this.details = details;
  }
}

async function authRequest<T>(
  path: string,
  options: RequestInit,
): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });
  } catch (error) {
    throw new AuthApiError(
      error instanceof TypeError
        ? "Cannot reach the Dashboard API"
        : "Network request failed",
      0,
      error,
    );
  }

  if (!response.ok) {
    let details: unknown;

    try {
      details = await response.json();
    } catch {
      details = await response.text();
    }

    throw new AuthApiError(
      `Request failed: ${response.status}`,
      response.status,
      details,
    );
  }

  return (await response.json()) as T;
}

export function loginStaff(
  payload: LoginPayload,
): Promise<AuthResponse> {
  return authRequest<AuthResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function loginDemo(): Promise<AuthResponse> {
  return authRequest<AuthResponse>("/auth/demo-login", {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export function registerOrganization(
  payload: RegisterOrganizationPayload,
): Promise<AuthResponse> {
  return authRequest<AuthResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getMe(): Promise<AuthUser> {
  const token = getAccessToken();

  if (!token) {
    throw new AuthApiError(
      "Not authenticated",
      401,
    );
  }

  const response = await fetch(
    `${API_URL}/auth/me`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    },
  );

  if (response.status === 401) {
    clearAuthSession();

    throw new AuthApiError(
      "Session expired",
      401,
    );
  }

  if (!response.ok) {
    throw new AuthApiError(
      "Could not verify session",
      response.status,
    );
  }

  const user: AuthUser = await response.json();

  return user;
}

async function authedAuthRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getAccessToken();

  if (!token) {
    throw new AuthApiError("Not authenticated", 401);
  }

  return authRequest<T>(path, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      ...(options.headers as Record<string, string> | undefined),
    },
  });
}

export interface TelegramLinkCode {
  code: string;
  expires_at: string;
  ttl_minutes: number;
  telegram_bot_username?: string | null;
}

export interface TelegramLinkStatus {
  linked: boolean;
  channel?: string | null;
  channel_address?: string | null;
  linked_at?: string | null;
  telegram_bot_username?: string | null;
}

export function createTelegramLinkCode(): Promise<TelegramLinkCode> {
  return authedAuthRequest<TelegramLinkCode>("/auth/telegram/link-code", {
    method: "POST",
  });
}

export function getTelegramLinkStatus(): Promise<TelegramLinkStatus> {
  return authedAuthRequest<TelegramLinkStatus>("/auth/telegram/link");
}

export async function unlinkTelegram(): Promise<void> {
  const token = getAccessToken();

  if (!token) {
    throw new AuthApiError("Not authenticated", 401);
  }

  const response = await fetch(`${API_URL}/auth/telegram/link`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  });

  if (response.status === 401) {
    clearAuthSession();
    throw new AuthApiError("Session expired", 401);
  }

  if (!response.ok && response.status !== 204) {
    throw new AuthApiError("Could not unlink Telegram", response.status);
  }
}