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
  constructor(
    message: string,
    public status: number,
    public details?: unknown,
  ) {
    super(message);
    this.name = "AuthApiError";
  }
}

async function authRequest<T>(
  path: string,
  options: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
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
    let details: unknown;

    try {
      details = await response.json();
    } catch {
      details = await response.text();
    }

    throw new AuthApiError(
      "Could not verify session",
      response.status,
      details,
    );
  }

  return (await response.json()) as AuthUser;
}