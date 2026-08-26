"use client";

import { useState } from "react";
import {
  AlertTriangle,
  HelpCircle,
  Loader2,
  Sparkles,
} from "lucide-react";

import { useTenant } from "@/context/TenantContext";
import {
  analyzeFaqs,
  FaqAnalysisResult,
} from "@/lib/api";

export default function FaqsPage() {
  const { tenantId } = useTenant();

  const [result, setResult] =
    useState<FaqAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyze() {
    setLoading(true);
    setError(null);

    try {
      const response = await analyzeFaqs(tenantId);
      setResult(response);
    } catch (requestError) {
      console.error(requestError);
      setError(
        "Could not analyze recent questions. Confirm the AI backend is running.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            FAQ Intelligence
          </h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Cluster recent student questions into recurring themes.
          </p>
        </div>

        <button
          type="button"
          onClick={() => void handleAnalyze()}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-50"
        >
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Sparkles className="h-4 w-4" />
          )}
          Analyze Recent Questions
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 p-4 text-red-800 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-200">
          <AlertTriangle className="h-5 w-5" />
          {error}
        </div>
      )}

      {!result && !loading && !error && (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center dark:border-slate-700 dark:bg-slate-900">
          <HelpCircle className="mx-auto h-10 w-10 text-slate-400" />
          <p className="mt-3 text-slate-600 dark:text-slate-300">
            Run an analysis to see recurring student questions.
          </p>
        </div>
      )}

      {result && (
        <>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Analyzed {result.analyzed_messages} recent messages ·{" "}
            {result.clusters.length} cluster
            {result.clusters.length === 1 ? "" : "s"}
          </p>

          {result.clusters.length === 0 ? (
            <div className="rounded-xl border border-slate-200 bg-white p-8 text-center text-slate-500 dark:border-slate-800 dark:bg-slate-900">
              No recurring questions found yet.
            </div>
          ) : (
            <div className="grid gap-4">
              {result.clusters.map((cluster, index) => (
                <article
                  key={`${cluster.question}-${index}`}
                  className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900"
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                        {cluster.question}
                      </h2>
                      <p className="mt-1 text-xs uppercase tracking-wide text-slate-500">
                        {cluster.category}
                      </p>
                    </div>
                    <span className="rounded-full bg-blue-500/15 px-3 py-1 text-xs font-medium text-blue-700 dark:text-blue-300">
                      Asked {cluster.frequency} times
                    </span>
                  </div>

                  {cluster.examples.length > 0 && (
                    <div className="mt-4">
                      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                        Examples
                      </p>
                      <ul className="mt-2 space-y-1 text-sm text-slate-600 dark:text-slate-300">
                        {cluster.examples.map((example) => (
                          <li key={example}>• {example}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {cluster.suggested_answer && (
                    <div className="mt-4 rounded-lg bg-slate-50 p-3 text-sm text-slate-700 dark:bg-slate-950 dark:text-slate-200">
                      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                        Suggested answer
                      </p>
                      <p className="mt-1">{cluster.suggested_answer}</p>
                    </div>
                  )}
                </article>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
