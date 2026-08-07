"use client";

import {
  FormEvent,
  useState,
} from "react";

import Link from "next/link";

import {
  useRouter,
} from "next/navigation";

import {
  Building2,
  Loader2,
} from "lucide-react";

import {
  AuthApiError,
  loginStaff,
} from "@/lib/auth-api";

import {
  saveAuthSession,
} from "@/lib/auth";


export default function LoginPage() {
  const router =
    useRouter();

  const [
    email,
    setEmail,
  ] = useState("");

  const [
    password,
    setPassword,
  ] = useState("");

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null);

  const [
    loading,
    setLoading,
  ] = useState(false);


  async function handleSubmit(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setError(null);

    if (
      !email.trim()
      || !password
    ) {
      setError(
        "Enter your email and password.",
      );

      return;
    }

    setLoading(true);

    try {
      const response =
        await loginStaff({
          email:
            email
              .trim()
              .toLowerCase(),

          password,
        });

      saveAuthSession(
        response,
      );

      router.replace(
        "/dashboard/overview",
      );

    } catch (requestError) {
      console.error(
        requestError,
      );

      if (
        requestError
        instanceof AuthApiError
      ) {
          const details = requestError.details as
            | { detail?: string }
            | undefined;

        setError(
          details?.detail
          ?? "Login failed.",
        );

      } else {
        setError(
          "Could not connect to the authentication server.",
        );
      }

    } finally {
      setLoading(false);
    }
  }


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


        {error && (
          <div className="mb-5 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300">
            {error}
          </div>
        )}


        <form
          onSubmit={
            handleSubmit
          }
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
              onChange={(
                event,
              ) =>
                setEmail(
                  event.target
                    .value,
                )
              }
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 outline-none focus:border-blue-500"
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
              onChange={(
                event,
              ) =>
                setPassword(
                  event.target
                    .value,
                )
              }
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 outline-none focus:border-blue-500"
            />
          </label>


          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 font-medium hover:bg-blue-500 disabled:opacity-50"
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