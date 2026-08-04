// src/app/login/page.tsx
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Mock validation – any non‑empty values are accepted.
    if (!email || !password) {
      setError("Please enter both email and password.");
      return;
    }
    // In a real app we would call Supabase Auth here.
    // For now simply navigate to the dashboard overview.
    router.push("/dashboard/overview");
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-900 text-gray-100">
      <div className="w-full max-w-md rounded-lg bg-gray-800 p-8 shadow-lg">
        <h2 className="mb-6 text-center text-2xl font-semibold">Staff Login</h2>
        {error && <p className="mb-4 text-sm text-red-400">{error}</p>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1" htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded border border-gray-600 bg-gray-700 px-3 py-2 text-white focus:outline-none focus:border-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1" htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded border border-gray-600 bg-gray-700 px-3 py-2 text-white focus:outline-none focus:border-indigo-500"
            />
          </div>
          <button
            type="submit"
            className="w-full rounded bg-indigo-600 px-4 py-2 font-medium text-white hover:bg-indigo-500 transition"
          >
            Sign In
          </button>
        </form>
      </div>
    </div>
  );
}
