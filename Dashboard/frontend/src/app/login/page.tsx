"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import {
  Building2,
  Loader2,
  PlayCircle,
} from "lucide-react";

import {
  AuthApiError,
  loginStaff,
} from "@/lib/auth-api";

import {
  saveAuthSession,
} from "@/lib/auth";

const DEMO_EMAIL = "demo.physics@axiom.ai";
const DEMO_PASSWORD = "DemoPhysics123!";

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
    if (requestError instanceof AuthApiError) {
      if (
        typeof requestError.details === "object" &&
        requestError.details !== null &&
        "detail" in requestError.details
      ) {
        const detail = (
          requestError.details as {
            detail?: unknown;
          }
        ).detail;

        if (typeof detail === "string") {
          return detail;
        }
      }
    }

    return fallback;
  }

  async function performLogin(
    loginEmail: string,
    loginPassword: string,
  ) {
    const response = await loginStaff({
      email: loginEmail.trim().toLowerCase(),
      password: loginPassword,
    });

    saveAuthSession(response);

    router.replace("/dashboard/overview");
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setError(null);

    if (!email.trim() || !password) {
      setError("Enter your email and password.");
      return;
    }

    setLoading(true);

    try {
      await performLogin(
        email,
        password,
      );
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
      await performLogin(
        DEMO_EMAIL,
        DEMO_PASSWORD,
      );
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

  const busy =
    loading || demoLoading;

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-4 text-white">
      <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-8 shadow-xl">
        <div className="mb-7 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-blue-600">
            <Building2 className="h-6 w-6" />
          </div>

          <h1 className="mt-4 text-2xl font-semibold">
            Staff Login
          </h1>

          <p className="mt-2 text-sm text-slate-400">
            Sign in to your institution dashboard.
          </p>
        </div>

        <button
          type="button"
          onClick={() =>
            void handleDemoLogin()
          }
          disabled={busy}
        className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-3 font-medium text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"        >
          {demoLoading ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <PlayCircle className="h-5 w-5" />
          )}

          {demoLoading
            ? "Opening Demo..."
            : "Proceed to Demo"}
        </button>

        <p className="mt-2 text-center text-xs text-slate-500">
          Click to open the preconfigured Demo Physics dashboard.
        </p>

        <div className="my-6 flex items-center gap-3">
          <div className="h-px flex-1 bg-slate-800" />

          <span className="text-xs uppercase tracking-wider text-slate-500">
            or sign in
          </span>

          <div className="h-px flex-1 bg-slate-800" />
        </div>

        {error && (
          <div className="mb-5 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300">
            {error}
          </div>
        )}

        <form
          onSubmit={handleSubmit}
          className="space-y-4"
        >
          <label className="block space-y-2">
            <span className="text-sm text-slate-300">
              Email
            </span>

            <input
              type="email"
              required
              value={email}
              onChange={(event) =>
                setEmail(
                  event.target.value,
                )
              }
              disabled={busy}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 outline-none focus:border-blue-500 disabled:opacity-50"
            />
          </label>

          <label className="block space-y-2">
            <span className="text-sm text-slate-300">
              Password
            </span>

            <input
              type="password"
              required
              value={password}
              onChange={(event) =>
                setPassword(
                  event.target.value,
                )
              }
              disabled={busy}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 outline-none focus:border-blue-500 disabled:opacity-50"
            />
          </label>

          <button
            type="submit"
            disabled={busy}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 font-medium hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading && (
              <Loader2 className="h-4 w-4 animate-spin" />
            )}

            Sign In
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-400">
          New institution?{" "}

          <Link
            href="/register"
            className="font-medium text-blue-400 hover:text-blue-300"
          >
            Create organization
          </Link>
        </p>
      </div>
    </main>
  );
}