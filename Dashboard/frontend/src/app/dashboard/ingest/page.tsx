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
  Trash2,
  Upload,
} from "lucide-react";

import { useToast } from "@/context/ToastContext";
import { useTenant } from "@/context/TenantContext";
import {
  deleteIngestDocument,
  getClasses,
  INGEST_ACCEPT,
  ingestSizeError,
  KbDocumentRecord,
  listIngestDocuments,
  SubjectClass,
  uploadDocument,
} from "@/lib/api";

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
  const [ingestStatus, setIngestStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [documents, setDocuments] = useState<KbDocumentRecord[]>([]);
  const [loadingDocuments, setLoadingDocuments] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const loadDocuments = useCallback(async () => {
    setLoadingDocuments(true);
    try {
      const result = await listIngestDocuments(tenantId, classId || undefined);
      setDocuments(result.documents);
    } catch (requestError) {
      console.error(requestError);
    } finally {
      setLoadingDocuments(false);
    }
  }, [tenantId, classId]);

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
    void loadDocuments();
  }, [loadDocuments]);

  useEffect(() => {
    const preselected = searchParams.get("class_id");
    if (preselected) {
      setClassId(preselected);
    }
  }, [searchParams]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!classId || !file) {
      setError("Select a class and a document.");
      return;
    }

    const sizeError = ingestSizeError(file);
    if (sizeError) {
      setError(sizeError);
      return;
    }

    setUploading(true);
    setError(null);
    setIngestStatus(null);

    try {
      const result = await uploadDocument(
        {
          classId,
          file,
          title: title.trim() || undefined,
          lesson: lesson.trim() || undefined,
        },
        tenantId,
        (document) => {
          setIngestStatus(document.status);
          void loadDocuments();
        },
      );

      const ocrNote = result.ocr_pages
        ? ` (${result.ocr_pages} scanned page${result.ocr_pages === 1 ? "" : "s"} transcribed)`
        : "";

      const skipped = result.skipped ? " (unchanged — skipped re-ingest)" : "";

      showToast(
        `${result.source_filename ?? "document"} — ${result.chunks_upserted} chunks${ocrNote}${skipped}.`,
        "success",
      );

      setWarnings(result.warnings ?? []);

      setFile(null);
      setTitle("");
      setLesson("");
      setIngestStatus(null);
      void loadDocuments();
      router.refresh();
    } catch (requestError) {
      console.error(requestError);
      const message =
        requestError instanceof Error
          ? requestError.message
          : "Document upload failed.";
      showToast(message, "error");
      setError(message);
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(documentId: string, filename: string) {
    if (!window.confirm(`Remove "${filename}" from the knowledge base?`)) {
      return;
    }
    setDeletingId(documentId);
    try {
      const result = await deleteIngestDocument(documentId, tenantId);
      showToast(`Deleted ${filename} (${result.chunks_deleted} chunks removed).`, "success");
      void loadDocuments();
    } catch (requestError) {
      console.error(requestError);
      showToast("Could not delete document.", "error");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900 dark:text-white">
          Upload Tutor Notes
        </h1>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
          PDF, Word and Markdown files are chunked and added to the tenant
          knowledge base for RAG.
        </p>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-200">
          <AlertTriangle className="h-5 w-5" />
          {error}
        </div>
      )}

      {warnings.length > 0 && (
        <div className="space-y-1 rounded-lg border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-200">
          <div className="flex items-center gap-2 font-medium">
            <AlertTriangle className="h-5 w-5" />
            Ingested with warnings
          </div>
          <ul className="ml-7 list-disc space-y-1">
            {warnings.map((warning) => (
              <li key={warning}>{warning}</li>
            ))}
          </ul>
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
          <span className="text-sm text-slate-700 dark:text-slate-300">Document</span>
          <input
            type="file"
            accept={INGEST_ACCEPT}
            onChange={(event) => {
              setFile(event.target.files?.[0] ?? null);
              setWarnings([]);
              setError(null);
            }}
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
          {uploading && ingestStatus
            ? `Processing (${ingestStatus})…`
            : "Upload to knowledge base"}
        </button>
      </form>

      <div className="flex items-start gap-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-4 text-sm text-slate-600 dark:text-slate-400">
        <FileUp className="mt-0.5 h-5 w-5 shrink-0" />
        <p>
          Accepts PDF (max 50 MB), Word .docx (25 MB) and Markdown (5 MB).
          Re-uploading the same file replaces its chunks rather than duplicating them.
          Scanned PDF pages are transcribed automatically when a vision API key is set.
        </p>
      </div>

      <section className="space-y-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-medium text-slate-900 dark:text-white">
            Ingested documents
          </h2>
          <button
            type="button"
            onClick={() => void loadDocuments()}
            className="text-sm text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
          >
            Refresh
          </button>
        </div>

        {loadingDocuments ? (
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <Loader2 className="h-4 w-4 animate-spin" />
            Loading documents…
          </div>
        ) : documents.length === 0 ? (
          <p className="text-sm text-slate-500">No documents ingested yet for this class.</p>
        ) : (
          <ul className="divide-y divide-slate-200 dark:divide-slate-800">
            {documents.map((doc) => (
              <li
                key={doc.document_id}
                className="flex items-start justify-between gap-4 py-3 first:pt-0 last:pb-0"
              >
                <div className="min-w-0">
                  <p className="truncate font-medium text-slate-900 dark:text-white">
                    {doc.title || doc.filename}
                  </p>
                  <p className="text-xs text-slate-500">
                    {doc.source_type.toUpperCase()} · {doc.chunks_upserted ?? 0} chunks ·{" "}
                    {doc.status}
                    {doc.page_count ? ` · ${doc.page_count} pages` : ""}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => void handleDelete(doc.document_id, doc.filename)}
                  disabled={deletingId === doc.document_id}
                  className="inline-flex shrink-0 items-center gap-1 rounded-md border border-red-500/30 px-2 py-1 text-xs text-red-400 hover:bg-red-500/10 disabled:opacity-50"
                >
                  {deletingId === doc.document_id ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    <Trash2 className="h-3 w-3" />
                  )}
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
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
