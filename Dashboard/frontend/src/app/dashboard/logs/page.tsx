"use client";

import {
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  Loader2,
  RefreshCw,
  ScrollText,
} from "lucide-react";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import { useTenant } from "@/context/TenantContext";
import {
  getMessageLogs,
  MessageLog,
} from "@/lib/api";
import {
  btnQuiet,
  emptyState,
  errorBanner,
  inputClass,
  pageHeader,
  pageSubtitle,
  pageTitle,
  surfaceCard,
} from "@/lib/ui";

const PAGE_SIZE = 25;

export default function LogsPage() {
  const { tenantId } = useTenant();
  const [logs, setLogs] = useState<MessageLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  const loadLogs = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      setLogs(await getMessageLogs(tenantId));
    } catch (requestError) {
      console.error(requestError);
      setError(
        "Could not load message logs. Confirm the backend is available.",
      );
    } finally {
      setLoading(false);
    }
  }, [tenantId]);

  useEffect(() => {
    void loadLogs();
  }, [loadLogs]);

  const filteredLogs = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) {
      return logs;
    }

    return logs.filter((log) => {
      const values = [
        log.id,
        log.student_id,
        log.student_name,
        log.channel,
        log.intent,
        log.timestamp,
      ];

      return values.some((value) =>
        String(value ?? "")
          .toLowerCase()
          .includes(query),
      );
    });
  }, [logs, search]);

  useEffect(() => {
    setPage(1);
  }, [search, logs]);

  const totalPages = Math.max(
    1,
    Math.ceil(filteredLogs.length / PAGE_SIZE),
  );

  const currentPage = Math.min(page, totalPages);

  const pageLogs = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE;
    return filteredLogs.slice(start, start + PAGE_SIZE);
  }, [filteredLogs, currentPage]);

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col gap-4 overflow-hidden">
      <div className={`${pageHeader} mb-0 shrink-0`}>
        <div className="min-w-0">
          <div className="flex items-center gap-3">
            <ScrollText className="h-6 w-6 text-blue" />
            <h1 className={pageTitle}>Message Logs</h1>
          </div>
          <p className={pageSubtitle}>
            View historical student and AI message activity.
          </p>
        </div>

        <button
          type="button"
          onClick={() => void loadLogs()}
          disabled={loading}
          className={btnQuiet}
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      <input
        type="search"
        value={search}
        onChange={(event) => setSearch(event.target.value)}
        placeholder="Search by student, channel, intent..."
        className={`${inputClass} shrink-0`}
      />

      {error ? (
        <div className={`${errorBanner} shrink-0`}>
          <AlertTriangle className="h-5 w-5 shrink-0 text-blue" />
          {error}
        </div>
      ) : null}

      {loading ? (
        <div className="flex min-h-48 flex-1 items-center justify-center">
          <Loader2 className="h-7 w-7 animate-spin text-muted" />
        </div>
      ) : filteredLogs.length === 0 ? (
        <div className={emptyState}>No message logs found.</div>
      ) : (
        <>
          <div
            className={`${surfaceCard} min-h-0 flex-1 overflow-auto`}
          >
            <table className="min-w-full text-sm">
              <thead className="sticky top-0 z-10 border-b border-border bg-surface text-left text-muted">
                <tr>
                  <th className="px-4 py-3 font-medium">Time</th>
                  <th className="px-4 py-3 font-medium">Student</th>
                  <th className="px-4 py-3 font-medium">Student ID</th>
                  <th className="px-4 py-3 font-medium">Channel</th>
                  <th className="px-4 py-3 font-medium">Intent</th>
                </tr>
              </thead>
              <tbody>
                {pageLogs.map((log) => (
                  <tr
                    key={log.id}
                    className="border-b border-border last:border-0"
                  >
                    <td className="whitespace-nowrap px-4 py-3 text-muted">
                      {log.timestamp
                        ? new Date(log.timestamp).toLocaleString()
                        : "—"}
                    </td>
                    <td className="px-4 py-3 font-medium text-heading">
                      {log.student_name ?? "Unknown student"}
                    </td>
                    <td className="px-4 py-3 text-muted">{log.student_id}</td>
                    <td className="px-4 py-3 capitalize text-fg">
                      {log.channel || "—"}
                    </td>
                    <td className="px-4 py-3 text-fg">
                      {log.intent ? log.intent.replaceAll("_", " ") : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex shrink-0 flex-wrap items-center justify-between gap-3 text-sm text-muted">
            <p>
              Showing {(currentPage - 1) * PAGE_SIZE + 1}–
              {Math.min(currentPage * PAGE_SIZE, filteredLogs.length)} of{" "}
              {filteredLogs.length}
            </p>
            <div className="flex items-center gap-2">
              <button
                type="button"
                className={btnQuiet}
                disabled={currentPage <= 1}
                onClick={() => setPage((value) => Math.max(1, value - 1))}
              >
                <ChevronLeft className="h-4 w-4" />
                Prev
              </button>
              <span className="tabular text-fg">
                Page {currentPage} / {totalPages}
              </span>
              <button
                type="button"
                className={btnQuiet}
                disabled={currentPage >= totalPages}
                onClick={() =>
                  setPage((value) => Math.min(totalPages, value + 1))
                }
              >
                Next
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
