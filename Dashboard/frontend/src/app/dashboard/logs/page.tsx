"use client";

import {
  AlertTriangle,
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

export default function LogsPage() {
  const { tenantId } = useTenant();
  const [logs, setLogs] = useState<MessageLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

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

  return (
    <div className="space-y-6">
      <div className={pageHeader}>
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
        className={inputClass}
      />

      {error ? (
        <div className={errorBanner}>
          <AlertTriangle className="h-5 w-5 shrink-0 text-blue" />
          {error}
        </div>
      ) : null}

      {loading ? (
        <div className="flex min-h-48 items-center justify-center">
          <Loader2 className="h-7 w-7 animate-spin text-muted" />
        </div>
      ) : filteredLogs.length === 0 ? (
        <div className={emptyState}>No message logs found.</div>
      ) : (
        <div className={`${surfaceCard} overflow-x-auto`}>
          <table className="min-w-full text-sm">
            <thead className="border-b border-border bg-bg/60 text-left text-muted">
              <tr>
                <th className="px-4 py-3 font-medium">Time</th>
                <th className="px-4 py-3 font-medium">Student</th>
                <th className="px-4 py-3 font-medium">Student ID</th>
                <th className="px-4 py-3 font-medium">Channel</th>
                <th className="px-4 py-3 font-medium">Intent</th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.map((log) => (
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
      )}
    </div>
  );
}
