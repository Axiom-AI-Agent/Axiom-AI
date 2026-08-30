"use client";

import { useCallback, useEffect, useState } from "react";
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
  getClasses,
  SubjectClass,
} from "@/lib/api";

export default function FaqsPage() {
  const { tenantId } = useTenant();

  const [classes, setClasses] = useState<SubjectClass[]>([]);
  const [selectedClassId, setSelectedClassId] = useState("");
  const [result, setResult] =
    useState<FaqAnalysisResult | null>(null);
  const [loadingClasses, setLoadingClasses] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadClasses = useCallback(async () => {
    setLoadingClasses(true);
    setError(null);

    try {
      const response = await getClasses(tenantId);
      setClasses(response);
      setSelectedClassId((current) => {
        if (current && response.some((item) => item.id === current)) {
          return current;
        }
        return response[0]?.id ?? "";
      });
    } catch (requestError) {
      console.error(requestError);
      setError("Could not load classes.");
    } finally {
      setLoadingClasses(false);
    }
  }, [tenantId]);

  useEffect(() => {
    void loadClasses();
  }, [loadClasses]);

  useEffect(() => {
    setResult(null);
  }, [selectedClassId]);

  async function handleAnalyze() {
    if (!selectedClassId) {
      setError("Select a class before analyzing FAQs.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await analyzeFaqs(selectedClassId, tenantId);
      setResult(response);
    } catch (requestError) {
      console.error(requestError);
      setError(
        "Could not analyze recent questions. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  }

  const selectedClass = classes.find(
    (item) => item.id === selectedClassId,
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-heading">
            FAQ Intelligence
          </h1>
          <p className="mt-1 text-sm text-muted">
            Cluster recent student questions for one class into recurring themes.
          </p>
        </div>

        <button
          type="button"
          onClick={() => void handleAnalyze()}
          disabled={loading || loadingClasses || !selectedClassId}
          className="inline-flex items-center gap-2 rounded-lg bg-blue px-4 py-2 text-sm font-medium text-paper hover:bg-blue/90 disabled:opacity-50"
        >
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Sparkles className="h-4 w-4" />
          )}
          Analyze Class Questions
        </button>
      </div>

      <label className="block max-w-md space-y-2">
        <span className="text-sm text-fg">
          Class
        </span>
        <select
          value={selectedClassId}
          onChange={(event) => setSelectedClassId(event.target.value)}
          disabled={loadingClasses || classes.length === 0}
          className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-heading outline-none focus:border-indigo-soft  bg-surface "
        >
          {classes.length === 0 ? (
            <option value="">No classes available</option>
          ) : (
            classes.map((subjectClass) => (
              <option key={subjectClass.id} value={subjectClass.id}>
                {subjectClass.name ?? subjectClass.subject}
              </option>
            ))
          )}
        </select>
      </label>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 p-4 text-red-800   text-fg">
          <AlertTriangle className="h-5 w-5" />
          {error}
        </div>
      )}

      {!result && !loading && !error && (
        <div className="rounded-xl border border-dashed border-border bg-surface p-10 text-center  bg-surface">
          <HelpCircle className="mx-auto h-10 w-10 text-muted" />
          <p className="mt-3 text-muted">
            {selectedClass
              ? `Run an analysis for ${selectedClass.name ?? selectedClass.subject}.`
              : "Select a class, then run an analysis."}
          </p>
        </div>
      )}

      {result && (
        <>
          <p className="text-sm text-muted">
            {selectedClass
              ? `${selectedClass.name ?? selectedClass.subject} · `
              : ""}
            Analyzed {result.analyzed_messages} recent messages ·{" "}
            {result.clusters.length} cluster
            {result.clusters.length === 1 ? "" : "s"}
          </p>

          {result.clusters.length === 0 ? (
            <div className="rounded-xl border border-border bg-surface p-8 text-center text-muted  bg-surface">
              No recurring questions found for this class yet.
            </div>
          ) : (
            <div className="grid gap-4">
              {result.clusters.map((cluster, index) => (
                <article
                  key={`${cluster.question}-${index}`}
                  className="rounded-xl border border-border bg-surface p-5  bg-surface"
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <h2 className="text-lg font-semibold text-heading">
                        {cluster.question}
                      </h2>
                      <p className="mt-1 text-xs uppercase tracking-wide text-muted">
                        {cluster.category}
                      </p>
                    </div>
                    <span className="rounded-full bg-indigo-soft/20 px-3 py-1 text-xs font-medium text-fg">
                      Asked {cluster.frequency} times
                    </span>
                  </div>

                  {cluster.examples.length > 0 && (
                    <div className="mt-4">
                      <p className="text-xs font-medium uppercase tracking-wide text-muted">
                        Examples
                      </p>
                      <ul className="mt-2 space-y-1 text-sm text-muted">
                        {cluster.examples.map((example) => (
                          <li key={example}>• {example}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {cluster.suggested_answer && (
                    <div className="mt-4 rounded-lg bg-surface p-3 text-sm text-fg bg-surface dark:text-muted">
                      <p className="text-xs font-medium uppercase tracking-wide text-muted">
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
