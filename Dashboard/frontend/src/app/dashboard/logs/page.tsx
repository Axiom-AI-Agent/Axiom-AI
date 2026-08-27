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

import {
  getMessageLogs,
  MessageLog,
} from "@/lib/api";

export default function LogsPage() {
  const [logs, setLogs] = useState<MessageLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  const loadLogs = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await getMessageLogs();

      setLogs(data);
    } catch (requestError) {
      console.error(requestError);

      setError(
        "Could not load message logs. Confirm the backend is available.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

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
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <ScrollText className="h-6 w-6 text-blue-500" />

            <h1 className="text-2xl font-semibold text-slate-900 ">
              Message Logs
            </h1>
          </div>

          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            View historical student and AI message activity.
          </p>
        </div>

        <button
          type="button"
          onClick={() => void loadLogs()}
          disabled={loading}
          className="flex items-center gap-2 rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-700 hover:bg-hover disabled:opacity-50 dark:border-slate-700 dark:text-muted dark:hover:bg-slate-800"
        >
          <RefreshCw
            className={`h-4 w-4 ${
              loading ? "animate-spin" : ""
            }`}
          />

          Refresh
        </button>
      </div>

      <div>
        <input
          type="search"
          value={search}
          onChange={(event) =>
            setSearch(event.target.value)
          }
          placeholder="Search by student, channel, intent..."
          className="w-full rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-900 "
        />
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-600 dark:text-red-300">
          <AlertTriangle className="h-5 w-5" />

          {error}
        </div>
      )}

      {loading ? (
        <div className="flex min-h-48 items-center justify-center">
          <Loader2 className="h-7 w-7 animate-spin text-slate-400" />
        </div>
      ) : filteredLogs.length === 0 ? (
        <div className="rounded-xl border border-slate-200 bg-white p-10 text-center text-slate-500 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400">
          No message logs found.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
          <table className="min-w-full text-sm">
            <thead className="border-b border-slate-200 bg-slate-50 text-left text-slate-600 dark:border-slate-800 dark:bg-slate-950 dark:text-muted">
              <tr>
                <th className="px-4 py-3">
                  Time
                </th>

                <th className="px-4 py-3">
                  Student
                </th>

                <th className="px-4 py-3">
                  Student ID
                </th>

                <th className="px-4 py-3">
                  Channel
                </th>

                <th className="px-4 py-3">
                  Intent
                </th>
              </tr>
            </thead>

            <tbody>
              {filteredLogs.map((log) => (
                <tr
                  key={log.id}
                  className="border-b border-slate-100 last:border-0 dark:border-slate-800"
                >
                  <td className="whitespace-nowrap px-4 py-3 text-slate-500 dark:text-slate-400">
                    {log.timestamp
                      ? new Date(
                          log.timestamp,
                        ).toLocaleString()
                      : "—"}
                  </td>

                  <td className="px-4 py-3 font-medium text-slate-900 ">
                    {log.student_name ??
                      "Unknown student"}
                  </td>

                  <td className="px-4 py-3 text-slate-500 dark:text-slate-400">
                    {log.student_id}
                  </td>

                  <td className="px-4 py-3 capitalize text-slate-700 dark:text-muted">
                    {log.channel || "—"}
                  </td>

                  <td className="px-4 py-3 text-slate-700 dark:text-muted">
                    {log.intent
                      ? log.intent.replaceAll(
                          "_",
                          " ",
                        )
                      : "—"}
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