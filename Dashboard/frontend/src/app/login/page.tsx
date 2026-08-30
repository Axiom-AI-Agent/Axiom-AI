"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Building2, Loader2, PlayCircle } from "lucide-react";

import { AuthApiError, loginDemo, loginStaff } from "@/lib/auth-api";
import { saveAuthSession } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [demoLoading, setDemoLoading] = useState(false);

  function getErrorMessage(
    requestError: unknown,
    fallback: string,
  ): string {
    if (requestError instanceof TypeError) {
      return "Cannot reach the server. Check your connection and try again.";
    }

    if (requestError instanceof AuthApiError) {
      if (requestError.status === 0) {
        return "Cannot reach the server. Check your connection and try again.";
      }

      if (requestError.status === 401) {
        return "Invalid email or password.";
      }

      if (requestError.status === 403) {
        return "This account is not active. Contact your administrator.";
      }

      if (requestError.status === 429) {
        return "Too many attempts. Please wait a moment and try again.";
      }
    }

    return fallback;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (!email.trim() || !password) {
      setError("Enter your email and password.");
      return;
    }

    setLoading(true);

    try {
      const response = await loginStaff({
        email: email.trim().toLowerCase(),
        password,
      });
      saveAuthSession(response);
      router.replace("/dashboard/overview");
    } catch (requestError: unknown) {
      console.error(requestError);
      setError(
        getErrorMessage(
          requestError,
          "Could not connect to the authentication server.",
        ),
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleDemoLogin() {
    setError(null);
    setDemoLoading(true);

    try {
      const response = await loginDemo();
      saveAuthSession(response);
      router.replace("/dashboard/overview");
    } catch (requestError: unknown) {
      console.error(requestError);
      setError(
        getErrorMessage(
          requestError,
          "Could not start the demo. Please try again.",
        ),
      );
    } finally {
      setDemoLoading(false);
    }
  }

  const busy = loading || demoLoading;

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-ink px-4 text-paper">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(720px_340px_at_50%_-12%,rgba(59,122,237,0.28),transparent_58%)]" />
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(520px_280px_at_90%_100%,rgba(111,162,135,0.16),transparent_50%)]" />

      <div className="relative w-full max-w-md rounded-2xl border border-white/12 bg-[linear-gradient(165deg,rgba(22,35,61,0.96),rgba(15,26,46,0.98))] p-8 shadow-[0_24px_60px_rgba(0,0,0,0.45)] backdrop-blur-md">
        <div className="mb-7 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-blue text-paper shadow-lg shadow-blue/30">
            <Building2 className="h-6 w-6" />
          </div>

          <h1 className="font-display mt-4 text-2xl font-semibold tracking-tight">
            Staff Login
          </h1>

          <p className="mt-2 text-sm text-paper/65">
            Sign in to your institution dashboard.
          </p>
        </div>

        <button
          type="button"
          onClick={() => void handleDemoLogin()}
          disabled={busy}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue px-4 py-3 font-medium text-paper transition hover:bg-blue/90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {demoLoading ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <PlayCircle className="h-5 w-5" />
          )}
          {demoLoading ? "Opening Demo..." : "Proceed to Demo"}
        </button>

        <p className="mt-2 text-center text-xs text-paper/55">
          Opens the preconfigured Demo Physics dashboard.
        </p>

        <div className="my-6 flex items-center gap-3">
          <div className="h-px flex-1 bg-white/10" />
          <span className="text-xs uppercase tracking-wider text-paper/45">
            or sign in
          </span>
          <div className="h-px flex-1 bg-white/10" />
        </div>

        {error ? (
          <div className="mb-5 rounded-lg border border-red-400/30 bg-red-500/10 p-3 text-sm text-red-100">
            {error}
          </div>
        ) : null}

        <form onSubmit={handleSubmit} className="space-y-4">
          <label className="block space-y-2">
            <span className="text-sm text-paper/70">Email</span>
            <input
              type="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              disabled={busy}
              className="w-full rounded-lg border border-white/10 bg-ink/70 px-3 py-2.5 text-paper outline-none transition focus:border-blue/70 focus:ring-2 focus:ring-blue/20 disabled:opacity-50"
            />
          </label>

          <label className="block space-y-2">
            <span className="text-sm text-paper/70">Password</span>
            <input
              type="password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              disabled={busy}
              className="w-full rounded-lg border border-white/10 bg-ink/70 px-3 py-2.5 text-paper outline-none transition focus:border-blue/70 focus:ring-2 focus:ring-blue/20 disabled:opacity-50"
            />
          </label>

          <button
            type="submit"
            disabled={busy}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue px-4 py-2.5 font-medium text-paper transition hover:bg-blue/90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            Sign In
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-paper/60">
          New institution?{" "}
          <Link
            href="/register"
            className="font-medium text-blue hover:text-blue/80"
          >
            Create organization
          </Link>
        </p>
      </div>
    </main>
  );
}
