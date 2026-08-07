import type {
  AuthResponse,
  AuthUser,
} from "@/types/auth";

const TOKEN_KEY =
  "axiom_access_token";

const USER_KEY =
  "axiom_auth_user";


export function saveAuthSession(
  response: AuthResponse,
): void {
  if (
    typeof window === "undefined"
  ) {
    return;
  }

  localStorage.setItem(
    TOKEN_KEY,
    response.access_token,
  );

  localStorage.setItem(
    USER_KEY,
    JSON.stringify(
      response.user,
    ),
  );
}


export function getAccessToken():
  string | null {
  if (
    typeof window === "undefined"
  ) {
    return null;
  }

  return localStorage.getItem(
    TOKEN_KEY,
  );
}


export function getStoredAuthUser():
  AuthUser | null {
  if (
    typeof window === "undefined"
  ) {
    return null;
  }

  const raw =
    localStorage.getItem(
      USER_KEY,
    );

  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(
      raw,
    ) as AuthUser;
  } catch {
    clearAuthSession();
    return null;
  }
}


export function clearAuthSession():
  void {
  if (
    typeof window === "undefined"
  ) {
    return;
  }

  localStorage.removeItem(
    TOKEN_KEY,
  );

  localStorage.removeItem(
    USER_KEY,
  );
}


export function isAuthenticated():
  boolean {
  return Boolean(
    getAccessToken()
    && getStoredAuthUser(),
  );
}