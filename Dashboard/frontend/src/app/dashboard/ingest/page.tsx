"use client";

import { useRouter, useSearchParams } from "next/navigation";
import {
  FormEvent,
  Suspense,
  useCallback,
  useEffect,
  useState,
} from "react";
import {
  AlertTriangle,
  FileUp,
  Loader2,
  Upload,
} from "lucide-react";

import { useToast } from "@/context/ToastContext";
import { useTenant } from "@/context/TenantContext";
import { getClasses, SubjectClass, uploadDocument } from "@/lib/api";

function IngestContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { tenantId } = useTenant();
  const { showToast } = useToast();

  const [classes, setClasses] = useState<SubjectClass[]>([]);
  const [classId, setClassId] = useState(searchParams.get("class_id") ?? "");
  const [title, setTitle] = useState("");
  const [lesson, setLesson] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loadingClasses, setLoadingClasses] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadClasses = useCallback(async () => {
    setLoadingClasses(true);

    try {
      const rows = await getClasses(tenantId);
      setClasses(rows);

      setClassId((current) => current || rows[0]?.id || "");
    } catch (requestError) {
      console.error(requestError);
      setError("Could not load classes for ingest.");
    } finally {
      setLoadingClasses(false);
    }
  }, [tenantId]);

  useEffect(() => {
    void loadClasses();
  }, [loadClasses]);

  useEffect(() => {
    const preselected = searchParams.get("class_id");
    if (preselected) {
      setClassId(preselected);
    }
  }, [searchParams]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!classId || !file) {
      setError("Select a class and a PDF file.");
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const result = await uploadDocument(
        {
          classId,
          file,
          title: title.trim() || undefined,
          lesson: lesson.trim() || undefined,
        },
        tenantId,
      );

      showToast(
        `Uploaded ${result.source_filename ?? "PDF"} — ${result.chunks_upserted} chunks ingested.`,
        "success",
      );

      setFile(null);
      setTitle("");
      setLesson("");
      router.refresh();
    } catch (requestError) {
      console.error(requestError);
      showToast("Document upload failed.", "error");
      setError("Upload failed. Check that the AI backend and Qdrant are configured.");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900 dark:text-white">
          Upload Tutor Notes
        </h1>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
          PDFs are chunked and added to the tenant knowledge base for RAG.
        </p>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-200">
          <AlertTriangle className="h-5 w-5" />
          {error}
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5"
      >
        <label className="block space-y-2">
          <span className="text-sm text-slate-700 dark:text-slate-300">Class</span>
          <select
            value={classId}
            onChange={(event) => setClassId(event.target.value)}
            disabled={loadingClasses}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 px-3 py-2 text-slate-900 dark:text-white outline-none focus:border-gray-500"
          >
            {classes.map((subjectClass) => (
              <option key={subjectClass.id} value={subjectClass.id}>
                {subjectClass.subject} ({subjectClass.id})
              </option>
            ))}
          </select>
        </label>

        <label className="block space-y-2">
          <span className="text-sm text-slate-700 dark:text-slate-300">PDF file</span>
          <input
            type="file"
            accept="application/pdf,.pdf"
            onChange={(event) =>
              setFile(event.target.files?.[0] ?? null)
            }
            className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 px-3 py-2 text-sm text-slate-700 dark:text-slate-300"
          />
        </label>

        <label className="block space-y-2">
          <span className="text-sm text-slate-700 dark:text-slate-300">Title (optional)</span>
          <input
            type="text"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="Lesson 7 Notes"
            className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 px-3 py-2 text-slate-900 dark:text-white outline-none focus:border-gray-500"
          />
        </label>

        <label className="block space-y-2">
          <span className="text-sm text-slate-700 dark:text-slate-300">Lesson label (optional)</span>
          <input
            type="text"
            value={lesson}
            onChange={(event) => setLesson(event.target.value)}
            placeholder="7"
            className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 px-3 py-2 text-slate-900 dark:text-white outline-none focus:border-gray-500"
          />
        </label>

        <button
          type="submit"
          disabled={uploading || !file || !classId}
          className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500 disabled:opacity-50"
        >
          {uploading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Upload className="h-4 w-4" />
          )}
          Upload to knowledge base
        </button>
      </form>

      <div className="flex items-start gap-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-4 text-sm text-slate-600 dark:text-slate-400">
        <FileUp className="mt-0.5 h-5 w-5 shrink-0" />
        <p>
          Maximum file size is 20 MB. Chunks are appended to the existing
          Qdrant collection for this tenant and scoped to the selected class.
        </p>
      </div>
    </div>
  );
}

export default function IngestPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-48 items-center justify-center">
          <Loader2 className="h-7 w-7 animate-spin text-slate-600 dark:text-slate-400" />
        </div>
      }
    >
      <IngestContent />
    </Suspense>
  );
}
